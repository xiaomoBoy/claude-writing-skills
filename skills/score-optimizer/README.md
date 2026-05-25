# score-optimizer

Calibrate / improve the **scoring rubric itself** by batch-scoring a labeled sample set and comparing against ground truth.

## What it does

The companion to [`article-optimizer`](../article-optimizer). Where article-optimizer holds the rubric fixed and changes the article, score-optimizer does the opposite: it holds an article sample set fixed and changes the rubric to make the scores match your labels.

Workflow:

1. Curate a small labeled sample set in `assets/articles/samples/` (10-30 articles you've manually rated as good/medium/bad)
2. Run `scripts/run_scoring.py` to batch-score all of them with the current rubric
3. Compare against your labels via `scripts/evaluate.py`
4. Edit the rubric in `references/score_prompt.md` (criteria, few-shot examples, weights)
5. Re-run, see if accuracy improved
6. Repeat

This is **research mode** — you're tuning a prompt against ground truth, not optimizing a single article.

## Requirements

- [`codex` CLI](https://github.com/openai/codex) on `PATH` (or set `CODEX_CLI_PATH`)
- Python 3.9+
- Your own labeled sample articles (see `assets/articles/samples/` for format)

## Quick example

```
You: 跑一轮基线评分
Claude: → runs scripts/run_scoring.py → all samples scored, saves scores.json

You: 跑评估，看跟我的标注差多少
Claude: → runs scripts/evaluate.py → reports per-dimension accuracy

You: title_score 总是偏高 1-2 分，帮我紧一下
Claude: → edits references/score_prompt.md title rubric → asks to re-run
```

## Files

- `scripts/run_scoring.py` — batch score all samples → `scores.json`
- `scripts/evaluate.py` — compare `scores.json` against labels
- `references/score_prompt.md` — the rubric you're tuning
- `assets/articles/samples/` — **you provide your own samples here** (see [samples/README.md](assets/articles/samples/README.md) for the schema)
- `assets/articles/labels.example.json` — example label format; rename to `labels.json` once you've added your own samples

## Setup before first use

```bash
# 1. Put your own .md sample articles into assets/articles/samples/
# 2. Copy the example labels and fill in your scores:
cp assets/articles/labels.example.json assets/articles/labels.json
# 3. Edit assets/articles/labels.json — one entry per sample file
# 4. Run baseline scoring
python3 scripts/run_scoring.py
# 5. Evaluate against your labels
python3 scripts/evaluate.py
```

The skill ships **no sample articles** — calibration is meaningless without samples from your own domain.

See [SKILL.md](SKILL.md) for the full calibration loop.
