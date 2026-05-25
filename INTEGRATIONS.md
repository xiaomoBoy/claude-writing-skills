# Using These Skills Outside Claude Code

These skills were authored for [Claude Code](https://www.anthropic.com/claude-code) and ship as a Claude Code plugin. But **the content of each skill is just markdown + standalone scripts** — so they can be used (with some manual wiring) inside Cursor, Aider, the OpenAI Codex CLI, the Claude API directly, or any LLM agent framework. They can also be run as pure CLI tools with no AI at all.

**中文版**: [INTEGRATIONS.zh-CN.md](INTEGRATIONS.zh-CN.md)

---

## What's portable vs. what's Claude Code-specific

| Component | What it is | Portable? |
|---|---|---|
| `SKILL.md` body | The workflow / instructions / hard constraints / troubleshooting for an agent to follow | ✅ Yes — load it into any LLM context |
| `references/*.md` | Reference material (rubrics, command tables, query templates) | ✅ Yes — same as SKILL.md |
| `scripts/*.py` | Standalone CLIs with no Claude dependency | ✅ Yes — run from any shell |
| `scripts/*.sh` (none currently, but pattern) | Same as above | ✅ Yes |
| `.claude-plugin/marketplace.json` | Plugin manifest for Claude Code's marketplace | ❌ No — CC-specific |
| `SKILL.md` frontmatter `description:` triggering | How Claude Code auto-invokes the right skill | ❌ No — CC-specific; in other agents you invoke manually |
| `agents/openai.yaml` (in yt-dlp-direct) | Codex agent interface metadata | ⚠️ Codex-specific — but small, see [Codex section](#openai-codex-cli) |

The **scripts** are the most portable piece. The **SKILL.md content** is portable as agent context. The **triggering glue** is the only Claude Code-specific piece.

---

## Integration patterns (pick one)

### Pattern 1 — Load SKILL.md as agent context

For: any LLM-based agent (Claude API, Cursor, Aider, Gemini, custom).

The agent reads `SKILL.md` once at the start of a session (or per task), follows the workflow inside it, and calls bundled scripts when the workflow says to. You — the human — explicitly invoke "use the publisher-wechatsync workflow for this article" instead of relying on auto-triggering.

### Pattern 2 — Use the scripts standalone

For: shell pipelines, cron jobs, no AI needed.

The scripts are plain CLIs. Examples:

```bash
# Score a single article
python3 skills/article-optimizer/scripts/run_single_score.py path/to/article.md

# Normalize markdown image paths (no AI)
python3 skills/publisher-wechatsync/scripts/normalize_image_paths.py path/to/article.md

# Batch score a sample set (after you've put samples + labels in)
cd skills/score-optimizer && python3 scripts/run_scoring.py
```

You lose the agent's coordination, but the scripts themselves work fine.

### Pattern 3 — Wrap as an MCP server / Smithery skill

For: agent runtimes that consume MCP (Model Context Protocol).

Not done out of the box, but feasible. You'd expose each script as an MCP tool and ship the SKILL.md as the tool's description. Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Per-runtime guides

### Claude API (direct, Python)

```python
from anthropic import Anthropic
from pathlib import Path

client = Anthropic()

# Load the skill's playbook as system prompt
skill_md = Path("skills/publisher-wechatsync/SKILL.md").read_text()

system_prompt = f"""You are an agent that helps the user publish articles.
Follow this playbook strictly:

{skill_md}

When the playbook says to run a script, use the tool_use API to call it.
Stop and ask for confirmation at every gate the playbook defines."""

# Then run normally
resp = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=4096,
    system=system_prompt,
    messages=[{"role": "user", "content": "Publish ./my-article.md to zhihu, dry-run first"}],
    tools=[ ... ],  # define tools that call the bundled scripts
)
```

Use [prompt caching](https://docs.claude.com/en/docs/build-with-claude/prompt-caching) on the system block since SKILL.md doesn't change between calls.

### Claude API (TypeScript / Node)

```typescript
import Anthropic from "@anthropic-ai/sdk";
import { readFileSync } from "fs";

const client = new Anthropic();
const skillMd = readFileSync("skills/publisher-wechatsync/SKILL.md", "utf-8");

const resp = await client.messages.create({
  model: "claude-opus-4-7",
  max_tokens: 4096,
  system: [{
    type: "text",
    text: `You are an agent that follows this playbook strictly:\n\n${skillMd}`,
    cache_control: { type: "ephemeral" },  // cache the playbook
  }],
  messages: [{ role: "user", content: "Publish my-article.md to zhihu, dry-run first" }],
});
```

### Cursor

Cursor reads `.cursorrules` (or `.cursor/rules/*.mdc` in newer versions) as context for the agent. To use one of these skills:

```bash
# Project-wide: copy the skill body into Cursor rules
mkdir -p .cursor/rules
cp ~/path/to/claude-writing-skills/skills/publisher-wechatsync/SKILL.md \
   .cursor/rules/publisher-wechatsync.mdc
```

Or merge all 5 into one rules file:

```bash
cat ~/path/to/claude-writing-skills/skills/*/SKILL.md \
  > .cursor/rules/writing-skills.mdc
```

The triggering language in SKILL.md frontmatter (`Use when ...`) becomes ordinary natural-language hints — Cursor's agent will pick up the right one based on your message.

Then run the scripts as needed (Cursor can execute shell commands via the agent).

### OpenAI Codex CLI

The Codex CLI looks for an `agents/openai.yaml` inside each skill — this is the wiring file. The `yt-dlp-direct` skill ships one as a worked example:

```yaml
# skills/yt-dlp-direct/agents/openai.yaml
interface:
  display_name: "yt-dlp Direct"
  short_description: "Inspect, download, or extract media via the installed yt-dlp CLI"
  default_prompt: "Use $yt-dlp-direct to inspect, download, or extract media."
policy:
  allow_implicit_invocation: true
```

For the other 4 skills, copy and adapt:

```bash
# In each skill dir
mkdir -p skills/research-collector/agents
cat > skills/research-collector/agents/openai.yaml <<'EOF'
interface:
  display_name: "Research Collector"
  short_description: "Collect YouTube + web research into a NotebookLM notebook"
  default_prompt: "Use $research-collector to gather material on a topic."
policy:
  allow_implicit_invocation: true
EOF
```

Then point Codex at the skills directory:

```bash
codex --skills-dir ~/path/to/claude-writing-skills/skills exec "..."
```

(Adjust to current Codex CLI flags — see `codex --help`.)

### Aider

Aider doesn't have a native skill concept, but it accepts message files. Use the skill as a contextual instruction:

```bash
# Load the publisher playbook as context, then ask
aider --message-file <(cat <<EOF
Follow this playbook strictly when I ask you to publish anything:

$(cat ~/path/to/claude-writing-skills/skills/publisher-wechatsync/SKILL.md)

---

User request: publish ./my-article.md to zhihu, dry-run first.
EOF
)
```

For repeated use, save the prefix to a file and `cat prefix.md request.md | aider --message-file /dev/stdin`.

### Gemini CLI / other agents

Gemini CLI and most other agent frameworks accept a system prompt or "context file". The pattern is identical:

1. Load the relevant `SKILL.md` as the agent's system / context
2. User issues a natural-language request that matches the skill
3. Agent follows the playbook, calls the bundled scripts
4. You confirm at each gate the playbook defines

Most agent frameworks support tool / function calling — expose the bundled scripts as tools and the agent will call them at the right moment.

### Smithery (MCP)

[Smithery](https://smithery.ai) hosts MCP servers. None of these skills currently ship as MCP, but conversion is straightforward:

1. Wrap each script as an MCP tool (input schema + handler)
2. Ship the SKILL.md content as the tool's `description`
3. Register the MCP server with Smithery

If you do this, please open a PR linking your MCP package — happy to feature it.

### Standalone (no AI)

All scripts work without any AI involvement:

```bash
# yt-dlp-direct — just use yt-dlp directly, the skill body is human reference
yt-dlp -F "https://www.youtube.com/watch?v=..."

# article-optimizer — score a file
python3 skills/article-optimizer/scripts/run_single_score.py article.md

# score-optimizer — batch score samples
cd skills/score-optimizer
python3 scripts/run_scoring.py
python3 scripts/evaluate.py

# publisher-wechatsync — preflight + image normalization, then call wechatsync
python3 skills/publisher-wechatsync/scripts/normalize_image_paths.py article.md
wechatsync sync article.md -p zhihu,juejin --dry-run
```

Some skills wrap multiple tools and gates — the value of the SKILL.md is encoding that orchestration. If you go standalone, you reproduce the orchestration manually.

---

## What you give up without Claude Code

If you use these via Pattern 1/2 instead of inside Claude Code, you lose:

- **Auto-triggering**: in Claude Code, the skill's `description:` frontmatter routes user requests automatically. Elsewhere you say "use the X workflow" explicitly.
- **Native gate prompts**: Claude Code's interactive prompts are CC-specific. Other agents fake this with normal LLM "ask the user before proceeding" instructions.
- **`/plugin` install flow**: outside Claude Code you `git clone` the repo and reference paths directly.

What you keep:

- The actual operational knowledge (the bulk of the value)
- All the scripts
- The hard-constraint discipline (no auto-publish, mandatory dry-run, etc.) — as long as your prompt to the agent enforces it

---

## Help wanted

If you wire these up to a runtime that's not listed here (LangChain, AutoGen, OpenAgents, etc.), please open a PR adding your integration recipe to this file. The pattern is always "load SKILL.md + expose scripts" — but every framework has its own way of doing both.
