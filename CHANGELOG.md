# Changelog

All notable changes to this project will be documented here. Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-05-24

Initial public release.

### Added

- **5 skills** extracted from a real long-form writing workflow:
  - `yt-dlp-direct` — pragmatic `yt-dlp` CLI wrapper for video / audio / subtitle / format inspection
  - `research-collector` — NotebookLM-backed research pipeline (YouTube search + deep web research + analysis queries)
  - `article-optimizer` — single-article scoring + rewrite loop against a fixed viral rubric
  - `score-optimizer` — calibrate the scoring rubric itself against your labeled samples
  - `publisher-wechatsync` — multi-platform Chinese-platform publishing via `@wechatsync/cli`, with mandatory dry-run and image-path normalization
- **Marketplace manifest** (`.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json`) so the whole collection can be installed via `/plugin marketplace add xiaomoBoy/claude-writing-skills`
- **Documentation** (English + 简体中文):
  - `README.md` / `README.zh-CN.md` — landing pages with quick install + skill overview
  - `INSTALL.md` / `INSTALL.zh-CN.md` — comprehensive dependency install guide (macOS / Linux / Windows)
  - `INTEGRATIONS.md` / `INTEGRATIONS.zh-CN.md` — how to use these skills outside Claude Code (Cursor / Aider / Codex CLI / Claude API SDK / standalone)
  - `docs/USAGE.md` / `docs/USAGE.zh-CN.md` — end-to-end workflow walkthrough
  - `CONTRIBUTING.md` — contribution workflow + design principles
- **Per-skill READMEs** for GitHub browsing
- **GitHub issue + PR templates** in `.github/`
- **MIT License**

### Notes

- The skill bodies (`SKILL.md`) are written in Simplified Chinese (the author's working language). Frontmatter `description:` fields are English so they trigger correctly in any locale. English translations of bodies welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
- The `score-optimizer` skill ships with no sample articles — calibration requires samples from your own domain. See [skills/score-optimizer/assets/articles/samples/README.md](skills/score-optimizer/assets/articles/samples/README.md) for the schema.

[Unreleased]: https://github.com/xiaomoBoy/claude-writing-skills/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/xiaomoBoy/claude-writing-skills/releases/tag/v0.1.0
