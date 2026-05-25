# research-collector

Collect YouTube videos + web articles for a topic, push them into a NotebookLM notebook, run analysis queries, and save results as markdown.

## What it does

A fixed pipeline so you don't redesign research workflow every time:

1. Create a NotebookLM notebook for the topic
2. Search YouTube with `yt-dlp ytsearch` from 2-3 angles, filter to top 15
3. Add them as sources to the notebook
4. Run NotebookLM `deep` research to auto-discover ~40 web articles
5. Run 3 analysis queries (top-N list, target-audience filter, getting-started + pitfalls)
6. Extract `answer` fields into a single summary markdown

## Requirements

- [`notebooklm-mcp-cli`](https://github.com/jacob-bd/notebooklm-mcp-cli) installed (`pip install notebooklm-mcp-cli`) and logged in (`nlm login --check`)
- `yt-dlp` on `PATH`

## Quick example

```
You: 帮我收集 "AI agent frameworks 2026" 这个话题的素材
Claude: [invokes research-collector] → asks you about angle and naming →
        creates notebook → adds sources → runs research → saves output
```

Output lands in `./research/<topic>/` by default. Configurable via `RESEARCH_OUTPUT_DIR` or by telling Claude where to put it.

## Notes

- A NotebookLM `deep` research run takes ~5 min and adds ~40 sources
- Only one research task can run per notebook at a time
- The skill won't run audio / video / slides generation by default (those cost quota)

See [SKILL.md](SKILL.md) for the full workflow, phase breakdown, query templates, and troubleshooting.
