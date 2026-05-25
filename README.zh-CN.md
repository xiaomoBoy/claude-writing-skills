# claude-writing-skills

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/xiaomoBoy/claude-writing-skills?style=social)](https://github.com/xiaomoBoy/claude-writing-skills)
[![Last commit](https://img.shields.io/github/last-commit/xiaomoBoy/claude-writing-skills)](https://github.com/xiaomoBoy/claude-writing-skills/commits/main)
[![Issues](https://img.shields.io/github/issues/xiaomoBoy/claude-writing-skills)](https://github.com/xiaomoBoy/claude-writing-skills/issues)
[![Skills](https://img.shields.io/badge/skills-5-green)](skills/)

> 一套面向长文写作的 [Claude Code](https://www.anthropic.com/claude-code) skill 工具箱 —— 调研、打分、改稿、发布，端到端。

5 个从真实写作工作流里抽出来的 skill。边界很死,各管一段,可以组合用。每个只做一件事。

> Skill 描述(frontmatter)写英文是为了能在多语言场景下被正确触发,正文是中文(作者母语)。如果你只看中文,完全够用 —— 描述告诉你做什么,正文就是怎么做。

**English version**: [README.md](README.md)

## 安装

把本仓库加为 Claude Code marketplace,然后装这个 plugin:

```
/plugin marketplace add xiaomoBoy/claude-writing-skills
/plugin install claude-writing-skills@claude-writing-skills
```

完事。5 个 skill 都有了。

每个 skill 还需要它自己的上游 CLI(如 `yt-dlp` / `nlm` / `codex` / `wechatsync`)。完整的跨 OS 安装指南(macOS / Linux / Windows + 验证 + troubleshooting)见 **[INSTALL.zh-CN.md](INSTALL.zh-CN.md)**。

> 不用 Claude Code? 看 **[INTEGRATIONS.zh-CN.md](INTEGRATIONS.zh-CN.md)** —— 怎么在 Cursor / Aider / Codex CLI / 直调 Claude API / 纯脚本里用这些 skill。

## 包含哪些 skill

| Skill | 做什么 | 依赖 |
|---|---|---|
| **research-collector** | 给一个主题批量拉 YouTube 视频 + 网页文章,丢进 NotebookLM,跑 3 个分析查询,结果落地成 markdown。 | [`notebooklm-mcp-cli`](https://github.com/jacob-bd/notebooklm-mcp-cli) (即 `nlm`)、`yt-dlp` |
| **publisher-wechatsync** | 一份写完的 .md 文章一键发到知乎 / 掘金 / CSDN / 公众号等平台草稿箱。带预检、图片路径规整、强制 dry-run。 | `@wechatsync/cli` + Chrome 扩展 |
| **article-optimizer** | 单篇文章按固定爆款评分卡打分,然后按低分维度逐轮改写,把分数往上推。 | `codex` CLI |
| **score-optimizer** | 反过来:用一份你自己标注过的样本集去校准评分卡本身。需要改评分维度/权重/示例时用这个。 | `codex` CLI |
| **yt-dlp-direct** | 把 `yt-dlp` 的常用操作经验封进 skill —— 单视频、播放列表、抽音频、下字幕、cookies-from-browser。不重新发明轮子,只是知道怎么用对。 | `yt-dlp` |

## 为什么做这套

我自己长期写 X 长文 + 同步几个中文平台。用 Claude Code 写了一年下来,手里攒了大概 30 个零散的 prompt 和 shell helper。这 5 个 skill 是收口之后留下来的部分 —— 每周真的会用的那几个。

两条贯穿的设计原则:

1. **一个 skill 只干一件事**。没有"端到端做完整流程"的怪物 skill。调研/打分/改稿/发布之间的边界全是显式的,skill 也会拒绝越界。
2. **优先用真工具,不只是 prompt**。如果一个 CLI(`yt-dlp`、`nlm`、`wechatsync`、`codex`)已经把活干好了,skill 就在它外面包一层操作经验,而不是用纯 prompt 重新造一遍。

如果想要整套写作工作流(选题 → 大纲 → 草稿 → 风格对齐),那部分跟我个人的 Obsidian vault 耦合太深,没放出来。这 5 个是能干净抽出来的部分。

## 各 skill 速览

### research-collector
```
你: 帮我收集 "Claude Code skills" 这个话题的素材,输出到 ./research/claude-skills
Claude: [触发 research-collector] → 创建 notebook,加 ~15 个 YouTube + ~40 个网页源,
        跑 3 个分析查询,生成汇总 markdown
```

### publisher-wechatsync
```
你: 把 path/to/article.md 发到知乎和掘金,先 dry-run
Claude: [触发 publisher-wechatsync] → 检查登录态,规整图片路径,
        跑 dry-run,等你确认,再实跑
```

### article-optimizer / score-optimizer
```
你: 给 path/to/article.md 打分
Claude: [触发 article-optimizer] → 返回 9 维评分 JSON

你: 评分器对 "title_score" 给得太松,帮我校准
Claude: [触发 score-optimizer] → 在标注样本上重跑,对比 MAE / Spearman
```

### yt-dlp-direct
```
你: 把这个 YouTube 播放列表的音频下下来
Claude: [触发 yt-dlp-direct] → 构造对的 yt-dlp 命令,执行
```

## 配置

绝大多数 skill 零配置就能跑。几个有用的环境变量:

| 变量 | 用在哪 | 作用 |
|---|---|---|
| `CODEX_CLI_PATH` | article-optimizer, score-optimizer | 当 `codex` 不在 PATH 上时手动指定 |
| `RESEARCH_OUTPUT_DIR` | research-collector | 默认输出目录(默认 `./research/<topic>/`) |
| `MD_VAULT_ROOT` | publisher-wechatsync 的图片规整脚本 | 解析相对路径时的 fallback 根目录 |
| `WECHATSYNC_TOKEN` | publisher-wechatsync | 必填,从 Wechatsync Chrome 扩展里拿 |

## 环境要求

- Claude Code(支持 skill/plugin)—— 或其他 agent runtime,见 [INTEGRATIONS.zh-CN.md](INTEGRATIONS.zh-CN.md)
- 各 skill 对应的 CLI 依赖(`nlm` / `yt-dlp` / `codex` / `wechatsync`)—— 只装你打算用的
- Python 3.9+(脚本运行需要,只用标准库,不装额外 pip 包)

跨 macOS / Linux / Windows 的完整安装指南见 **[INSTALL.zh-CN.md](INSTALL.zh-CN.md)**。

## 仓库结构

```
.claude-plugin/
  marketplace.json     # marketplace 定义(一个 plugin)
  plugin.json          # plugin manifest
.github/
  ISSUE_TEMPLATE/      # bug + feature 模板
  PULL_REQUEST_TEMPLATE.md
skills/
  research-collector/
  publisher-wechatsync/
  article-optimizer/
  score-optimizer/
  yt-dlp-direct/
docs/
  USAGE.md             # 英文使用文档(端到端走一遍)
  USAGE.zh-CN.md       # 中文使用文档
README.md              # 英文 landing
README.zh-CN.md        # 中文 landing
INSTALL.md             # 依赖安装指南(英文)
INSTALL.zh-CN.md       # 依赖安装指南(中文)
INTEGRATIONS.md        # 在 Claude Code 之外用(英文)
INTEGRATIONS.zh-CN.md  # 在 Claude Code 之外用(中文)
CONTRIBUTING.md        # 贡献指引
CHANGELOG.md           # 版本记录
LICENSE
```

## 文档总索引

| 文档 | 讲什么 |
|---|---|
| [README.md](README.md) / [README.zh-CN.md](README.zh-CN.md) | Landing 页、快速安装、5 个 skill 概览 |
| [INSTALL.md](INSTALL.md) / [INSTALL.zh-CN.md](INSTALL.zh-CN.md) | 每个 CLI 依赖的详细安装,分 OS |
| [INTEGRATIONS.md](INTEGRATIONS.md) / [INTEGRATIONS.zh-CN.md](INTEGRATIONS.zh-CN.md) | 在 Cursor / Aider / Codex CLI / Claude API SDK / 纯脚本里用这些 skill |
| [docs/USAGE.md](docs/USAGE.md) / [docs/USAGE.zh-CN.md](docs/USAGE.zh-CN.md) | 端到端场景走一遍 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献流程 + 设计原则 |
| [CHANGELOG.md](CHANGELOG.md) | 版本记录 |
| 各 skill `skills/<name>/SKILL.md` | skill 实际遵循的 playbook |
| 各 skill `skills/<name>/README.md` | GitHub 浏览友好的 skill 摘要 |

## 贡献

Issue / PR 都欢迎。流程和设计原则见 **[CONTRIBUTING.md](CONTRIBUTING.md)**。

目前最有价值的 PR 方向:

- **SKILL.md 正文英译** —— 描述是英文,触发没问题,但正文(流程、命令、troubleshooting)还是中文
- **其他 agent runtime 的集成 recipe**(LangChain / AutoGen 等)—— 加到 [INTEGRATIONS.zh-CN.md](INTEGRATIONS.zh-CN.md)
- **更多 worked example** —— 尤其 `score-optimizer` 的校准循环,没做过的人很难自己摸出来

如果你基于这些 skill 做了新东西,欢迎反链 —— 我会在 README 里 feature 你。

## License

MIT —— 见 [LICENSE](LICENSE)。

## 作者

[@xiaomoBoy](https://github.com/xiaomoBoy)。写 VPS、self-hosting、AI 工作流。觉得有用的话给个 star,会让我更愿意继续维护。
