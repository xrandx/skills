# Skills

Personal Git repository for agent skills installed under `~/.agents`.

## Structure

Skills use the runtime-ready flat layout:

```text
~/.agents/
  skills/
    <skill-name>/
      SKILL.md
```

Keep each skill self-contained: place its `SKILL.md` and any referenced assets,
scripts, or examples inside the same skill directory.

## Skills

| Skill | Notes |
| --- | --- |
| `call-graph` | Plain-text call graphs and call stacks. |
| `guided-learning` | Guided, Socratic learning support. |
| `i-have-adhd` | ADHD-friendly response formatting. |
| `lark-base` | Lark Base operations. |
| `lark-calendar` | Lark Calendar operations. |
| `lark-contact` | Lark contact lookup. |
| `lark-doc` | Lark document operations. |
| `lark-drive` | Lark Drive operations. |
| `lark-im` | Lark instant messaging operations. |
| `lark-mail` | Lark Mail operations. |
| `lark-markdown` | Lark Markdown file operations. |
| `lark-shared` | Shared Lark authentication and setup. |
| `lark-sheets` | Lark spreadsheet operations. |
| `translate` | Faithful translation into a requested language. |
| `translate-to-markdown` | Translation into validated, portable Markdown. |
| `translate-to-pdf` | Translation into a visually verified PDF. |

## Git workflow

Run Git commands from `~/.agents`. New skills placed directly under `skills/`
remain immediately available to compatible agents and can be reviewed before
they are staged or committed.
