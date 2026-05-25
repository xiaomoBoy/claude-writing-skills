# 在 Claude Code 之外使用这些 skill

这套 skill 是给 [Claude Code](https://www.anthropic.com/claude-code) 写的、按 Claude Code plugin 形式发布。但**每个 skill 的内容本质上就是 markdown + 独立脚本** —— 所以可以(稍加手工接线)在 Cursor / Aider / OpenAI Codex CLI / 直调 Claude API / 任何 LLM agent 框架里用。也可以完全不用 AI,把脚本当纯 CLI 工具跑。

**English version**: [INTEGRATIONS.md](INTEGRATIONS.md)

---

## 哪些能搬走、哪些是 Claude Code 专属

| 组件 | 是什么 | 能搬走吗 |
|---|---|---|
| `SKILL.md` 正文 | 给 agent 看的工作流 / 指令 / 硬约束 / troubleshooting | ✅ 能 —— 灌进任何 LLM context |
| `references/*.md` | 参考资料(评分卡、命令表、查询模板) | ✅ 能 —— 跟 SKILL.md 一样 |
| `scripts/*.py` | 独立 CLI,不依赖 Claude | ✅ 能 —— 任何 shell 跑 |
| `scripts/*.sh`(目前没有,但模式一样) | 同上 | ✅ 能 |
| `.claude-plugin/marketplace.json` | Claude Code marketplace 的 plugin 清单 | ❌ 不能 —— CC 专属 |
| `SKILL.md` frontmatter `description:` 自动触发 | Claude Code 怎么挑出正确的 skill | ❌ 不能 —— CC 专属;其他 agent 里你手动指定 |
| `agents/openai.yaml`(只 yt-dlp-direct 带了) | Codex agent 接口元数据 | ⚠️ Codex 专属 —— 但很短,见 [Codex 章节](#openai-codex-cli) |

**最能搬走的是脚本**。**SKILL.md 内容**作为 agent context 可搬。**触发胶水**才是唯一 CC 专属的部分。

---

## 集成模式(挑一个)

### 模式 1 —— 把 SKILL.md 当 agent context 灌进去

适合: 任何基于 LLM 的 agent(Claude API、Cursor、Aider、Gemini、自研)。

Agent 在会话开始(或每个任务开始)读一遍 `SKILL.md`,按里面写的工作流走,该调脚本就调。**你**(人)显式说"按 publisher-wechatsync 流程发这篇",不再依赖自动触发。

### 模式 2 —— 脚本独立用

适合: shell pipeline、cron 任务、完全不要 AI。

脚本就是普通 CLI。例子:

```bash
# 单篇打分
python3 skills/article-optimizer/scripts/run_single_score.py path/to/article.md

# 规整 markdown 图片路径(纯脚本,不要 AI)
python3 skills/publisher-wechatsync/scripts/normalize_image_paths.py path/to/article.md

# 批量给样本打分(先把样本和 labels 放好)
cd skills/score-optimizer && python3 scripts/run_scoring.py
```

少了 agent 的编排,但脚本本身没问题。

### 模式 3 —— 包成 MCP server / Smithery skill

适合: 用 MCP(Model Context Protocol)的 agent runtime。

开箱没做,但可行。要做的话: 每个脚本包成一个 MCP tool、把 SKILL.md 当 tool 的 description 发布。欢迎 PR —— 见 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 按 runtime 分的接线指南

### Claude API(直调,Python)

```python
from anthropic import Anthropic
from pathlib import Path

client = Anthropic()

# 把 skill 的 playbook 当 system prompt 灌进去
skill_md = Path("skills/publisher-wechatsync/SKILL.md").read_text()

system_prompt = f"""You are an agent that helps the user publish articles.
Follow this playbook strictly:

{skill_md}

When the playbook says to run a script, use the tool_use API to call it.
Stop and ask for confirmation at every gate the playbook defines."""

# 然后正常跑
resp = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=4096,
    system=system_prompt,
    messages=[{"role": "user", "content": "Publish ./my-article.md to zhihu, dry-run first"}],
    tools=[ ... ],  # 定义对应 bundled 脚本的 tool
)
```

System block 用 [prompt caching](https://docs.claude.com/en/docs/build-with-claude/prompt-caching) —— SKILL.md 不变,缓存最划算。

### Claude API(TypeScript / Node)

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
    cache_control: { type: "ephemeral" },  // 缓存这个 playbook
  }],
  messages: [{ role: "user", content: "Publish my-article.md to zhihu, dry-run first" }],
});
```

### Cursor

Cursor 读 `.cursorrules`(或新版的 `.cursor/rules/*.mdc`)作为 agent context。用法:

```bash
# 项目级: 把 skill 正文复制成 Cursor rule
mkdir -p .cursor/rules
cp ~/path/to/claude-writing-skills/skills/publisher-wechatsync/SKILL.md \
   .cursor/rules/publisher-wechatsync.mdc
```

或者 5 个合成一个:

```bash
cat ~/path/to/claude-writing-skills/skills/*/SKILL.md \
  > .cursor/rules/writing-skills.mdc
```

SKILL.md frontmatter 里的 `Use when ...` 就当普通的自然语言提示 —— Cursor 的 agent 会按你的输入自动挑对应的部分。

脚本就让 Cursor agent 自己跑(它能执行 shell)。

### OpenAI Codex CLI

Codex CLI 找每个 skill 下的 `agents/openai.yaml` 当接线文件。`yt-dlp-direct` 已经带了一份做参考:

```yaml
# skills/yt-dlp-direct/agents/openai.yaml
interface:
  display_name: "yt-dlp Direct"
  short_description: "Inspect, download, or extract media via the installed yt-dlp CLI"
  default_prompt: "Use $yt-dlp-direct to inspect, download, or extract media."
policy:
  allow_implicit_invocation: true
```

其他 4 个 skill 照着复制改:

```bash
# 在每个 skill 目录下
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

然后让 Codex 指向 skills 目录:

```bash
codex --skills-dir ~/path/to/claude-writing-skills/skills exec "..."
```

(按当前 Codex CLI 的 flag 调,看 `codex --help`)

### Aider

Aider 没有原生 skill 概念,但接受 message file。把 skill 当上下文塞进去:

```bash
# 把 publisher playbook 当上下文,然后问
aider --message-file <(cat <<EOF
Follow this playbook strictly when I ask you to publish anything:

$(cat ~/path/to/claude-writing-skills/skills/publisher-wechatsync/SKILL.md)

---

User request: publish ./my-article.md to zhihu, dry-run first.
EOF
)
```

如果反复用,把 prefix 存到文件,`cat prefix.md request.md | aider --message-file /dev/stdin`。

### Gemini CLI / 其他 agent

Gemini CLI 和绝大多数 agent 框架都接受 system prompt 或 context 文件。模式一样:

1. 把对应的 `SKILL.md` 当 agent 的 system / context 灌进去
2. 用户用自然语言提对口的请求
3. Agent 按 playbook 走,调 bundled 脚本
4. 你在 playbook 定义的每个 gate 确认

绝大多数 agent 框架支持 tool / function calling —— 把 bundled 脚本暴露成 tool,agent 会在对的时机调。

### Smithery(MCP)

[Smithery](https://smithery.ai) 是 MCP server 的注册中心。本仓的 skill 还没打成 MCP,但可以做:

1. 每个脚本包成 MCP tool(input schema + handler)
2. SKILL.md 内容当 tool `description` 发布
3. 在 Smithery 注册 MCP server

如果你做了,欢迎 PR 反链 —— 我会在 README 里 feature。

### 纯脚本(无 AI)

所有脚本都能脱 AI 跑:

```bash
# yt-dlp-direct —— 直接用 yt-dlp,skill 正文是人看的参考
yt-dlp -F "https://www.youtube.com/watch?v=..."

# article-optimizer —— 给文件打分
python3 skills/article-optimizer/scripts/run_single_score.py article.md

# score-optimizer —— 批量给样本打分
cd skills/score-optimizer
python3 scripts/run_scoring.py
python3 scripts/evaluate.py

# publisher-wechatsync —— 预检 + 图片规整,然后调 wechatsync
python3 skills/publisher-wechatsync/scripts/normalize_image_paths.py article.md
wechatsync sync article.md -p zhihu,juejin --dry-run
```

有些 skill 是把好几个工具和 gate 串起来用 —— SKILL.md 的价值就在于编码这套编排。脱 AI 用,得自己手工复现编排。

---

## 不用 Claude Code 会失去什么

如果按模式 1/2 用,跟在 Claude Code 里用相比,会失去:

- **自动触发**: Claude Code 里 skill 的 `description:` frontmatter 自动路由用户请求。其他环境你得明确说"用 X 工作流"
- **原生 gate 提示**: Claude Code 的交互式提示是 CC 专属。其他 agent 用普通 LLM "动手前问用户" 指令模拟
- **`/plugin` 安装流**: 不在 Claude Code 里,就 `git clone` 仓库直接用路径引用

仍然保留:

- 真正的操作经验(大头价值在这)
- 全部脚本
- 硬约束纪律(不自动发布、强制 dry-run 等)—— 只要你给 agent 的 prompt 把约束写明就守得住

---

## 求 PR

如果你把这套接进了上面没列的 runtime(LangChain、AutoGen、OpenAgents 等),欢迎 PR 加到本文件。模式永远是"灌 SKILL.md + 暴露脚本",但每个框架都有自己的做法。
