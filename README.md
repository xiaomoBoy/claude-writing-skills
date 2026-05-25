# claude-writing-skills

> A toolkit of [Claude Code](https://www.anthropic.com/claude-code) skills for long-form content creators — research, score, rewrite, and publish, end to end.

**中文版**: [README.zh-CN.md](README.zh-CN.md)

5 skills extracted from a real working writing setup. They are opinionated, narrow in scope, and meant to compose. Each one does one thing.

> Skill descriptions (frontmatter) are English so they trigger correctly. Skill bodies are written in Chinese — that's the author's working language. If you don't read Chinese, the script files and command examples are still usable, and the descriptions tell you what each skill does. PRs translating bodies welcome.

## Install

Add this repo as a Claude Code marketplace, then install:

```
/plugin marketplace add xiaomoBoy/claude-writing-skills
/plugin install claude-writing-skills@claude-writing-skills
```

That's it — you now have all 5 skills available.

## What's inside

| Skill | What it does | Depends on |
|---|---|---|
| **research-collector** | Collect YouTube videos + web articles for a topic, push into a NotebookLM notebook, run analysis queries, save results as markdown. | [`notebooklm-mcp-cli`](https://github.com/jacob-bd/notebooklm-mcp-cli) (`nlm`), `yt-dlp` |
| **publisher-wechatsync** | Publish a finished markdown article to 知乎 / 掘金 / CSDN / 公众号 etc. as drafts via the wechatsync CLI. Handles pre-flight checks, dry-run, and image-path normalization. | `@wechatsync/cli` + Chrome extension |
| **article-optimizer** | Score a single article against a fixed viral-content rubric, then iterate rewrites round by round to raise the score. | `codex` CLI |
| **score-optimizer** | Calibrate / improve the scoring rubric itself by batch-scoring a labeled sample set. The companion to article-optimizer when you want to tune the evaluator. | `codex` CLI |
| **yt-dlp-direct** | A pragmatic command-reference skill for the installed `yt-dlp` CLI — single videos, playlists, audio extraction, subtitles, cookies-from-browser. No reinvention, just operational knowledge. | `yt-dlp` |

## Why I built these

I write long-form articles on my own publication and cross-post to several Chinese platforms. After a year of doing it with Claude Code, I had accumulated maybe 30 ad-hoc prompts and shell helpers. These 5 skills are the parts that survived the consolidation — the ones I actually use every week.

Two design principles run through all of them:

1. **One skill, one job.** No "do the whole workflow" skills. The boundaries between research / scoring / rewriting / publishing are explicit and the skills refuse to cross them.
2. **Real tools, not LLM-only.** Where a CLI already does the job well (`yt-dlp`, `nlm`, `wechatsync`, `codex`), the skill wraps operational knowledge around it rather than reinventing in pure prompt.

If you want the writing workflow as a whole (idea → outline → draft → style alignment), it's deeply coupled to my personal vault and not part of this release. These 5 are the parts I could cleanly extract.

## Per-skill quick start

### research-collector
```
You: 帮我收集 "Claude Code skills" 这个话题的素材，输出到 ./research/claude-skills
Claude: [invokes research-collector] → creates notebook, adds ~15 YouTube + ~40 web sources,
        runs 3 analysis queries, saves summary markdown
```

### publisher-wechatsync
```
You: 把 path/to/article.md 发到知乎和掘金（先 dry-run）
Claude: [invokes publisher-wechatsync] → checks auth, normalizes image paths,
        runs dry-run, asks confirmation, then syncs
```

### article-optimizer / score-optimizer
```
You: 给 path/to/article.md 跑一遍评分
Claude: [invokes article-optimizer] → returns 9-dimension score JSON

You: 评分器对 "title_score" 给得太松，帮我校准
Claude: [invokes score-optimizer] → re-runs prompt on labeled samples, compares
```

### yt-dlp-direct
```
You: 把这个 YouTube 播放列表的音频下下来
Claude: [invokes yt-dlp-direct] → constructs the exact yt-dlp invocation, runs it
```

## Configuration

Most skills work with zero config. A few env vars are useful:

| Variable | Used by | Purpose |
|---|---|---|
| `CODEX_CLI_PATH` | article-optimizer, score-optimizer | Override `codex` binary path if not on `PATH` |
| `RESEARCH_OUTPUT_DIR` | research-collector | Default output directory (default: `./research/<topic>/`) |
| `MD_VAULT_ROOT` | publisher-wechatsync (image normalizer) | Fallback root for resolving relative image paths |
| `WECHATSYNC_TOKEN` | publisher-wechatsync | Required, from the Wechatsync Chrome extension |

## Requirements

- Claude Code (with skill / plugin support)
- For individual skills, see the per-skill `SKILL.md` for tool dependencies (`nlm`, `yt-dlp`, `codex`, `wechatsync`, etc.)
- Python 3.9+ for the bundled scripts

## Repository layout

```
.claude-plugin/
  marketplace.json     # marketplace definition (one plugin)
  plugin.json          # plugin manifest
skills/
  research-collector/
  publisher-wechatsync/
  article-optimizer/
  score-optimizer/
  yt-dlp-direct/
docs/
  USAGE.md             # end-to-end walkthrough (EN)
  USAGE.zh-CN.md       # end-to-end walkthrough (ZH)
LICENSE
README.md              # this file
README.zh-CN.md        # Chinese landing
```

## Detailed usage guide

- English: [docs/USAGE.md](docs/USAGE.md)
- 中文: [docs/USAGE.zh-CN.md](docs/USAGE.zh-CN.md)

Walks through one complete end-to-end scenario (research → write → score → publish).

## Contributing

Issues and PRs welcome. Two areas where help would matter most:

- **English translation of SKILL.md bodies** — the descriptions trigger fine in English, but the body content (workflows, troubleshooting) is currently Chinese.
- **More worked examples in per-skill READMEs** — especially for `score-optimizer` (the calibration loop is non-obvious if you haven't tried it).

If you build something on top of these or extract a new skill, link back — happy to feature it in the README.

## License

MIT — see [LICENSE](LICENSE).

## Author

Built by [@xiaomoBoy](https://github.com/xiaomoBoy). I write about VPS, self-hosting, and AI workflows. If this is useful to you, a star helps me find time to keep maintaining it.
