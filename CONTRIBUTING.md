# Contributing

Issues and PRs welcome. This is a small, opinionated project — keep changes focused.

## Where to file issues

- Bug reports: [open an issue](https://github.com/xiaomoBoy/claude-writing-skills/issues/new?template=bug_report.md) with reproduction steps
- Feature requests: [open an issue](https://github.com/xiaomoBoy/claude-writing-skills/issues/new?template=feature_request.md) — describe the use case, not just the feature
- Questions: GitHub Discussions, or open an issue tagged `question`

## PR workflow

1. Fork the repo
2. Make your changes on a feature branch
3. Test locally (install your fork as a Claude Code marketplace and verify the affected skill still triggers and works)
4. Open a PR with a clear description: what changed, why, what was tested

Small PRs land fast. Large PRs (rewrites, new skills) — please open a discussion issue first so we agree on direction.

## Design principles

These run through the whole project. Please read before proposing changes:

1. **One skill, one job.** No "do the whole workflow" skills. Boundaries between skills are explicit and enforced inside SKILL.md (the `## Working Scope` and `## Hard Constraints` sections). If a contribution blurs a boundary, it'll be asked to either split or stay out of scope.
2. **Real tools first.** Where a CLI already does the job (`yt-dlp`, `nlm`, `wechatsync`, `codex`), wrap it. Don't reinvent in pure prompt. Skills add the operational knowledge layer, not the underlying capability.
3. **Hard gates over polite suggestions.** "Always dry-run first" is enforced as a refusal pattern, not just a tip. Same for "don't auto-publish", "don't fabricate user experiences", etc.
4. **Plain markdown + standalone scripts.** Avoid binary dependencies, complex build steps, or Claude-Code-only features that can't be replicated in other agents. See [INTEGRATIONS.md](INTEGRATIONS.md) for the portability targets.

## What kinds of PRs are most welcome

- **English translations of SKILL.md bodies.** Descriptions are English; bodies are Chinese. Translations widen the audience significantly.
- **Integration recipes** for other agent runtimes (Aider, Cursor, LangChain, etc.) — add to `INTEGRATIONS.md`.
- **OS-specific install notes** — especially Windows, where some deps are flakier.
- **Real worked examples** — short scenarios in `docs/` showing one skill solving one real problem.
- **Bug fixes** for the bundled scripts, with a reproducer.

## What kinds of PRs need more discussion

- **New skills.** Each new skill adds maintenance surface. Please open a discussion issue first describing: what job it does, why it's separate from existing skills, what tools it wraps.
- **Renaming or restructuring directories.** These break user setups that pinned `.claude-plugin/marketplace.json` entries.
- **Changing the rubric in `score_prompt.md`.** The rubric is opinionated and calibrated. Tweaks are fine; rewrites need a justification (and ideally before/after on a sample set).

## Adding a new skill (file layout)

If you've discussed and the new skill is approved, follow this layout:

```
skills/<your-skill-name>/
├── SKILL.md                # frontmatter + workflow (see existing skills as templates)
├── README.md               # 1-page English summary for GitHub browsing
├── scripts/                # optional: standalone scripts
│   └── *.py
├── references/             # optional: rubrics, command tables, query templates
│   └── *.md
└── assets/                 # optional: bundled non-code files
```

SKILL.md must have:

- YAML frontmatter with `name:` and `description:` (English; this is what triggers it)
- A `## Working Scope` section listing what it does and doesn't do
- A `## Workflow` section with concrete steps
- A `## Hard Constraints` section with what the skill refuses to do
- A `## Troubleshooting` section

The skill should also be added to `.claude-plugin/marketplace.json` — but if you're adding it via PR, leave that for the maintainer to handle so version bumps are consistent.

## Translation contributions

- Bilingual files: pair as `<name>.md` (English) + `<name>.zh-CN.md` (Chinese). Both should link to each other at the top.
- For SKILL.md bodies (currently Chinese), please keep the frontmatter `description:` field in English — that's what Claude Code uses for triggering and it needs to be English for cross-language users.
- Use Simplified Chinese for `.zh-CN.md`. Traditional Chinese contributions are welcome as `.zh-TW.md`.

## Code style (Python scripts)

- Python 3.9+
- Standard library only (no pip deps)
- Type hints encouraged
- Keep scripts under ~200 lines; if it grows, split into modules

## License

By contributing, you agree your contribution is licensed under the [MIT License](LICENSE), same as the rest of the project.

## Recognition

Contributors are listed in [CHANGELOG.md](CHANGELOG.md) per release.
