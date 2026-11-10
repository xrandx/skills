"""Inspect, prepare, and apply a bounded legacy Codex sidebar recovery."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ACCOUNT = 'electron-account-renderer-state-v1'
ATOMS = 'electron-persisted-atom-state'
SECTIONS = 'sidebar-custom-sections-v3'
MAP = 'app-server-project-id-by-legacy-project-id-by-host'
ORDER = 'unified-sidebar-project-order-v1'

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()

def save(path, value):
    with open(path, 'x', encoding='utf-8') as f:
        os.chmod(path, 0o600)
        json.dump(value, f, ensure_ascii=False, indent=2)

def section_state(atoms):
    states = atoms.get(SECTIONS, {})
    if len(states) != 1:
        raise ValueError('Expected one sidebar namespace; inspect schema manually')
    state = next(iter(states.values()))
    assert isinstance(state['sections'], list)
    return state

def summary(globals_, atoms):
    return {
        'projects': [p['name'] for p in globals_.get('local-projects', {}).values()],
        'sections': [{'name': s['name'], 'members': len(s.get('itemKeys', []))}
                     for state in atoms.get(SECTIONS, {}).values()
                     for s in state.get('sections', [])],
    }

def merge(original, source):
    d = copy.deepcopy(original)
    old = d[ACCOUNT]['inactive'][source]
    g = old['globals']
    projects = g['local-projects']
    assert projects, 'Source has no projects'
    for pid, p in projects.items():
        assert p['id'] == pid and isinstance(p['rootPaths'], list)
        assert all(Path(root).is_absolute() for root in p['rootPaths'])
        if pid in d.get('local-projects', {}):
            assert d['local-projects'][pid] == p, 'Project ID collision'
    for key in ['local-projects', 'project-appearances', 'thread-project-assignments',
                'thread-project-membership-host-ids', 'sidebar-project-thread-orders']:
        d[key] = {**copy.deepcopy(g.get(key, {})), **d.get(key, {})}
    for host, mapping in g.get(MAP, {}).items():
        current = d.setdefault(MAP, {}).setdefault(host, {})
        for legacy_id, server_id in mapping.items():
            assert legacy_id not in current or current[legacy_id] == server_id, 'Mapping conflict'
            current[legacy_id] = server_id
    d['project-order'] = list(dict.fromkeys(g.get('project-order', []) + d.get('project-order', [])))
    a = d[ATOMS]
    def local_item(item):
        if item.startswith('codex:project:'):
            return item[len('codex:project:'):] in d['local-projects']
        return item.startswith('codex:thread:local:')
    a[ORDER] = list(dict.fromkeys([v for v in old['atoms'].get(ORDER, [])
                                if v.startswith('codex:project:') and local_item(v)] + a.get(ORDER, [])))
    dst = section_state(a)
    for src in section_state(old['atoms'])['sections']:
        items = [v for v in src.get('itemKeys', []) if local_item(v)]
        if not items:
            continue
        matches = [s for s in dst['sections'] if s['name'] == src['name']]
        assert len(matches) <= 1, 'Ambiguous section names'
        if matches:
            target = matches[0]
        else:
            assert all(s['id'] != src['id'] for s in dst['sections']), 'Section ID collision'
            target = {k: copy.deepcopy(src[k]) for k in ['id', 'name', 'appearance'] if k in src}
            target['hostSectionIds'] = {k: v for k, v in src.get('hostSectionIds', {}).items() if k == 'local'}
            target['itemKeys'] = []
            dst['sections'].append(target)
            dst.setdefault('sectionOrder', []).append('custom:' + target['id'])
        target['itemKeys'] = list(dict.fromkeys(items + target['itemKeys']))
    return d

def assert_stopped(executable):
    assert sys.platform == 'darwin', 'apply currently supports macOS only'
    assert Path(executable).is_absolute() and Path(executable).is_file(), 'Invalid app executable'
    # Anchor and escape the executable path; do not match this Python command itself.
    import re
    result = subprocess.run(['pgrep', '-f', '^' + re.escape(executable) + r'(\s|$)'], capture_output=True)
    assert result.returncode == 1, 'Application running or process check failed'

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['inspect', 'prepare', 'apply'])
    p.add_argument('--state', type=Path, required=True)
    p.add_argument('--source')
    p.add_argument('--out', type=Path)
    p.add_argument('--app-executable')
    args = p.parse_args()
    assert not args.state.is_symlink(), 'State must not be a symlink'
    raw = args.state.read_bytes()
    d = json.loads(raw)
    if args.action == 'inspect':
        print(json.dumps({'current': {'owner': d[ACCOUNT]['owner'], **summary(d, d[ATOMS])},
                          'inactive': {k: summary(v['globals'], v['atoms'])
                                       for k, v in d[ACCOUNT]['inactive'].items()}}, ensure_ascii=False, indent=2))
        return
    assert args.out is not None
    if args.action == 'prepare':
        assert args.source and args.source != d[ACCOUNT]['owner']
        candidate = merge(d, args.source)
        args.out.mkdir(mode=0o700, parents=True, exist_ok=False)
        plan = {'owner': d[ACCOUNT]['owner'], 'source': args.source,
                'sourceDigest': digest(d[ACCOUNT]['inactive'][args.source]),
                'statePath': str(args.state.resolve())}
        save(args.out / 'plan.json', plan)
        save(args.out / 'before-prepare.json', d)
        save(args.out / 'candidate.json', candidate)
        save(args.out / 'status.json', {'status': 'prepared'})
        print(json.dumps({'changedKeys': [k for k in candidate if d.get(k) != candidate[k]],
                          **summary(candidate, candidate[ATOMS])}, ensure_ascii=False, indent=2))
        return
    assert args.app_executable, 'apply needs --app-executable'
    assert_stopped(args.app_executable)
    plan = json.loads((args.out / 'plan.json').read_text())
    assert plan['statePath'] == str(args.state.resolve()), 'State path changed'
    assert plan['owner'] == d[ACCOUNT]['owner'], 'Active account changed'
    assert plan['sourceDigest'] == digest(d[ACCOUNT]['inactive'][plan['source']]), 'Source changed'
    candidate = merge(d, plan['source'])
    save(args.out / 'before-apply.json', d)
    fd, temp = tempfile.mkstemp(prefix='.sidebar-recovery-', dir=args.state.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(candidate, f, ensure_ascii=False, separators=(',', ':'))
            f.flush()
            os.fsync(f.fileno())
        assert_stopped(args.app_executable)
        assert args.state.read_bytes() == raw, 'Concurrent state modification'
        os.replace(temp, args.state)
        assert json.loads(args.state.read_bytes()) == candidate
        (args.out / 'status.json').write_text(json.dumps({'status': 'restored', 'projects': len(candidate['local-projects'])}))
        print('RESTORED; reopen app and verify through application tools and UI')
    finally:
        if os.path.exists(temp):
            os.unlink(temp)

if __name__ == '__main__':
    main()
