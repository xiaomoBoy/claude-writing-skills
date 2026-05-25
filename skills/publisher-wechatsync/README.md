# publisher-wechatsync

Publish a finished markdown article to multiple Chinese content platforms (知乎 / 掘金 / CSDN / 公众号 / 小红书 / 头条 etc.) as drafts via the `@wechatsync/cli` tool.

## What it does

Wraps `wechatsync` with the operational hygiene you actually need every time:

- Pre-flight checks (CLI installed, token set, target platforms logged in)
- **Image-path normalization** (URL-decode + relative-path rewrite — Obsidian-style `%20` paths silently break image upload otherwise)
- Mandatory dry-run before real sync
- Per-platform success/failure report
- Refuses to actually press "publish" — only fills drafts

## Requirements

- [`@wechatsync/cli`](https://www.npmjs.com/package/@wechatsync/cli) installed globally
- Wechatsync Chrome extension installed and connected (provides the sync token)
- `WECHATSYNC_TOKEN` env var set (from the extension)
- Logged in to each target platform in your Chrome (the extension uses your cookies)

## Quick example

```
You: 把 path/to/article.md 发到知乎和掘金，先 dry-run
Claude: [invokes publisher-wechatsync] →
        runs normalize_image_paths.py →
        runs wechatsync platforms -a →
        runs wechatsync sync ... --dry-run →
        asks for confirmation →
        runs real sync
```

## Bundled script

`scripts/normalize_image_paths.py` — URL-decodes and rewrites image paths in a markdown file so wechatsync (and most other publish tools) can find them. Standalone:

```bash
python3 scripts/normalize_image_paths.py path/to/article.md --dry-run
```

## What this skill explicitly will NOT do

- Rewrite content for platform tone (compliance, length, style)
- Generate per-platform title / summary / cover
- Click the actual "publish" button in any platform admin

That's a separate pipeline. This skill stops at "drafts are filled, go review them."

See [SKILL.md](SKILL.md) for full workflow, hard constraints, and troubleshooting.
