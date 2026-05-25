# Usage Guide

End-to-end walkthrough of how the 5 skills compose. Pick the parts that match your workflow — they're independent.

**中文版**: [USAGE.zh-CN.md](USAGE.zh-CN.md)

---

## The workflow this toolkit assumes

```
   research-collector       (you)         article-optimizer       publisher-wechatsync
        │                     │                  │                       │
        ▼                     ▼                  ▼                       ▼
  YouTube + web         You write the      Score + iterate            Send drafts
  → NotebookLM          actual draft       against viral rubric       to ZH platforms
  → summary md          in your editor     until score plateaus       (dry-run first)


                              [side quest]
                              score-optimizer
                              calibrate the rubric itself
                              against your labeled samples


                              [helper]
                              yt-dlp-direct
                              grab any video/audio when you need to
```

The skills don't talk to each other. They produce / consume plain markdown files. You're the integration layer — invoking the next skill when you're ready.

---

## End-to-end scenario

Goal: write a long-form article about "Self-hosted AI agents in 2026."

### Step 1 — Gather raw material (research-collector)

```
You: 帮我收集 "self-hosted AI agents 2026" 这个话题的素材，输出到 ./research/self-hosted-ai/

Claude (invokes research-collector):
  → asks: confirm topic / angle / notebook name / how many sources?
  → creates NotebookLM notebook "self-hosted AI agents 2026 素材"
  → yt-dlp searches 2-3 angles, takes top 15 videos
  → adds them as sources (one every 2 seconds to avoid rate limit)
  → runs `nlm research start --mode deep` (~5 min, ~40 web sources discovered)
  → imports research results into notebook
  → runs 3 analysis queries:
      Q1: top 10 most-cited tools
      Q2: filter for target reader profile
      Q3: getting started + common pitfalls
  → writes ./research/self-hosted-ai/research-summary.md
```

You now have a summary you can read in 10 minutes, plus a notebook you can chat with for follow-up questions.

### Step 2 — Optional: deeper dive into one video (yt-dlp-direct)

If one of the YouTube results looks especially relevant and you want a transcript / audio:

```
You: 把 https://www.youtube.com/watch?v=XXX 的字幕和音频都拉下来，存到 ./research/self-hosted-ai/

Claude (invokes yt-dlp-direct):
  → constructs:
      yt-dlp --write-subs --sub-lang en --write-auto-subs --skip-download URL
      yt-dlp -x --audio-format mp3 -o './research/self-hosted-ai/%(title)s.%(ext)s' URL
  → runs them, reports file paths
```

### Step 3 — Write your draft

This part is **outside the toolkit**. Use your editor, your AI of choice, your own writing skill — whatever you actually use. Write a real draft. Save it as `path/to/article.md`.

The skills below assume you have a markdown file with normal frontmatter (`title`, `date`, etc).

### Step 4 — Score the draft (article-optimizer)

```
You: 给 path/to/article.md 跑一遍评分

Claude (invokes article-optimizer):
  → calls scripts/run_single_score.py path/to/article.md
  → returns JSON:
    {
      "title_score": 7,
      "opening_score": 5,
      "emotion_score": 6,
      "info_score": 9,
      "interaction_score": 4,
      "structure_score": 8,
      "trending_score": 6,
      "ip_score": 7,
      "ai_flavor_score": 6,
      "total_score": 58,
      "viral_percentage": 64.4
    }
```

Look at the lowest dimensions. In this example: `interaction_score: 4` (no CTAs / reader hooks) and `opening_score: 5` (boring lead).

### Step 5 — Targeted rewrite + re-score

```
You: opening 太弱，帮我改前 3 段，再打分

Claude:
  → rewrites the opening (one targeted change, not whole-article rewrite)
  → re-scores
  → reports: opening_score 5 → 8, total 58 → 64, viral_percentage 64.4 → 71.1
```

Iterate until the gain per round drops below a threshold you care about. Then stop.

### Step 6 — Publish (publisher-wechatsync) — Chinese platforms only

> Note: this skill targets Chinese platforms (知乎 / 掘金 / CSDN / 公众号 / 小红书 / etc.) via [`@wechatsync/cli`](https://www.npmjs.com/package/@wechatsync/cli). If you don't publish to those, skip this step.

Prerequisites (one-time):
- `npm install -g @wechatsync/cli`
- Install the Wechatsync Chrome extension
- Set `WECHATSYNC_TOKEN` from the extension
- Log in to each target platform in Chrome

```
You: 把 path/to/article.md 发到知乎和掘金，先 dry-run

Claude (invokes publisher-wechatsync):
  → which wechatsync             → ok
  → echo $WECHATSYNC_TOKEN | wc  → ok
  → runs python3 scripts/normalize_image_paths.py path/to/article.md --dry-run
  → fixes URL-encoded image paths (Obsidian style %20 etc) in place
  → wechatsync platforms -a       → shows login status
  → wechatsync sync ... --dry-run → shows what will go where
  → asks you to confirm
  → wechatsync sync ...           → fills drafts
  → reports per-platform success / fail with draft IDs
```

The skill **never presses "publish"**. It only fills drafts. You go to each platform admin to review → set cover image → click publish manually.

---

## Side quest: calibrating the rubric (score-optimizer)

After scoring 20+ articles you'll probably notice the rubric drifts in some direction (e.g. it overrates titles, underrates structure). To calibrate:

1. Put 10-30 of your own labeled `.md` articles into `skills/score-optimizer/assets/articles/samples/`
2. `cp skills/score-optimizer/assets/articles/labels.example.json skills/score-optimizer/assets/articles/labels.json`
3. Fill in your scores for each sample article in `labels.json`
4. Run baseline:
   ```bash
   cd skills/score-optimizer
   python3 scripts/run_scoring.py
   python3 scripts/evaluate.py
   ```
5. Look at per-dimension MAE / Spearman. If `title_score` MAE is high, edit `references/score_prompt.md` (the title rubric or its few-shot examples) and re-run.
6. Keep iterating until the rubric matches your taste.

The skill ships **no sample articles** — calibration is meaningless without samples from your own domain. See [skills/score-optimizer/assets/articles/samples/README.md](../skills/score-optimizer/assets/articles/samples/README.md) for the labels schema.

---

## Common patterns

### Score before AND after rewrites
Always score once before any rewrite, then after each round. Without the baseline, you can't tell whether changes helped.

### Don't chain skills automatically
Each skill is gated by your approval — that's intentional. `research-collector` won't auto-trigger `article-optimizer`. You stay in the loop because the boundary between "research is done" and "let's score the draft" is a judgment call.

### Save dry-run output
`publisher-wechatsync` requires dry-run first. Save the dry-run output to a file you can diff against — useful when the same article goes to multiple platforms over time.

---

## Troubleshooting (general)

| Symptom | Likely cause | Fix |
|---|---|---|
| `codex: command not found` (article-optimizer / score-optimizer) | `codex` not on `PATH` | Either install [openai/codex](https://github.com/openai/codex) globally, or set `CODEX_CLI_PATH=/path/to/codex` |
| `nlm login` fails (research-collector) | Session expired (~20min) | Re-run `nlm login` |
| `wechatsync` says "Chrome Extension not connected" | Extension not running, or token mismatch | Open extension → enable MCP Connection → re-export token → `export WECHATSYNC_TOKEN=…` |
| `yt-dlp` returns 403 / region error | yt-dlp too old, or geo-block | `pip install -U yt-dlp` first; for geo issues consider `--cookies-from-browser chrome` |
| Image upload fails on knowzhihu/掘金/etc | Image paths not normalized | Make sure `normalize_image_paths.py` ran (publisher-wechatsync does this automatically) |

---

## Where to go next

Each skill has its own deeper doc:

- [skills/research-collector/SKILL.md](../skills/research-collector/SKILL.md) — full phase breakdown + query templates
- [skills/publisher-wechatsync/SKILL.md](../skills/publisher-wechatsync/SKILL.md) — pre-flight checks, hard constraints, troubleshooting
- [skills/article-optimizer/SKILL.md](../skills/article-optimizer/SKILL.md) — iteration loop details
- [skills/score-optimizer/SKILL.md](../skills/score-optimizer/SKILL.md) — calibration workflow + experimental constraints
- [skills/yt-dlp-direct/SKILL.md](../skills/yt-dlp-direct/SKILL.md) — full command reference

---

## What this toolkit deliberately doesn't do

- It doesn't write your draft for you. The "voice" part of writing is too personal to be generalized into a skill. You're the writer; these skills are operational support.
- It doesn't auto-publish (it fills drafts, you press publish).
- It doesn't bypass platform DRM, compliance, or rate limits.
- It doesn't integrate end-to-end into one mega-skill. Boundaries are explicit on purpose.
