# article-optimizer

Score a single article against a fixed viral-content rubric, then iterate rewrites round by round to raise the score.

## What it does

The scoring rubric is **fixed**. The article is what changes. Each round:

1. Score the current article version (9 dimensions, JSON output)
2. Use the lowest-scoring dimensions to drive a targeted rewrite
3. Re-score the new version
4. Compare and keep the best

This is the right tool when you have a piece you believe in and want to push its score up. If instead you want to *change the scoring rubric*, use the companion [`score-optimizer`](../score-optimizer) skill.

## Requirements

- [`codex` CLI](https://github.com/openai/codex) on `PATH` (or set `CODEX_CLI_PATH`)
- Python 3.9+

## Quick example

```
You: 给 path/to/article.md 跑一遍评分
Claude: [invokes article-optimizer] → calls scripts/run_single_score.py →
        returns JSON: { title_score: 7, opening_score: 6, ..., total_score: 64,
                        viral_percentage: 71.1 }

You: opening 太弱，改一下开头再打分
Claude: → rewrites opening → re-scores → reports delta
```

## Scoring dimensions

| Dimension | Weight |
|---|---|
| title_score | 10 |
| opening_score | 10 |
| emotion_score | 10 |
| info_score | 10 |
| interaction_score | 10 |
| structure_score | 10 |
| trending_score | 10 |
| ip_score | 10 |
| ai_flavor_score | 10 (penalty-style: high = more AI-like) |

Total out of 90. Rubric definition lives in `references/score_prompt.md`.

## Files

- `scripts/run_single_score.py` — score one article, print JSON
- `references/score_prompt.md` — the rubric

See [SKILL.md](SKILL.md) for the full iteration workflow.
