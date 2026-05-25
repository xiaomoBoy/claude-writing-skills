# Sample Articles (you provide these)

This directory is where you put your own labeled sample articles to calibrate the scoring rubric. **None are shipped with this skill** — that's intentional: the samples that matter are the ones from your own domain / your own platform.

## What to put here

- 10–30 `.md` articles you have **manually rated**
- A mix of clearly-viral / mediocre / weak pieces, so the rubric has range
- Real articles you have rights to use (your own writing, or public-domain text)
- Suggested naming: `01_high_topic.md`, `02_mid_topic.md`, `03_low_topic.md` — a numeric prefix helps with sorting; the prefix label is just for your own reference

## Labels schema

Each sample article needs a corresponding entry in `../labels.example.json` (rename to `labels.json` once you've added your own). The schema:

```json
{
  "articles": [
    {
      "file": "01_my_article.md",
      "human_scores": {
        "title_score": 8,
        "opening_score": 7,
        "emotion_score": 6,
        "info_score": 8,
        "interaction_score": 5,
        "structure_score": 7,
        "trending_score": 6,
        "ip_score": 7,
        "ai_flavor_score": 4.0
      },
      "human_total": 58.0,
      "viral_level": "high",
      "notes": "Why you rated this the way you did — useful when re-reading later."
    }
  ]
}
```

- All `*_score` fields go 0–10, where higher = better, **except** `ai_flavor_score` which is 0–10 where higher = more AI-like (a penalty signal)
- `viral_level` is `high` / `mid` / `low` — a coarse bucket for stratified evaluation
- `notes` is free-text; helps you remember why you scored a given dimension a given way

## Why labels matter

The whole point of `score-optimizer` is comparing **model scores** against **your scores** to find rubric drift. Without your labels, there is no ground truth to calibrate against.

If you don't have time to label by hand, you can also use this directory purely for ad-hoc `article-optimizer` style scoring (no calibration). But you won't get the calibration benefit without labels.
