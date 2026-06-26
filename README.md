# Skills

Personal backup repository for agent skills.

## Structure

Skills live under `skills/<category>/<skill-name>/`.

Current layout:

```text
skills/
  learning/
    guided-learning/
      SKILL.md
```

Suggested categories for future additions:

- `learning/` for tutoring, study, and explanation skills
- `productivity/` for planning, summaries, and workflow helpers
- `coding/` for development and review skills
- `misc/` for skills that do not yet fit a stable category

Keep each skill self-contained: place its `SKILL.md` and any referenced assets, scripts, or examples inside the same skill directory.

## Restore

To restore a skill locally, copy its directory into `~/.agents/skills/`:

```sh
cp -R skills/learning/guided-learning ~/.agents/skills/
```
