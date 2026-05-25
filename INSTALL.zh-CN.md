# 安装文档

`claude-writing-skills` 依赖的全部 CLI 工具的端到端安装指南。**不需要全装** —— 只装你打算用的 skill 对应的依赖。

**English version**: [INSTALL.md](INSTALL.md)

---

## TL;DR

| 依赖 | 哪个 skill 用 | 最快安装命令 |
|---|---|---|
| Claude Code | 所有 skill 的运行宿主 | https://docs.claude.com/en/docs/claude-code |
| `yt-dlp` | yt-dlp-direct, research-collector | `brew install yt-dlp` / `pip install -U yt-dlp` |
| `ffmpeg` | (可选,yt-dlp 抽音频用) | `brew install ffmpeg` / `apt install ffmpeg` |
| `nlm` (notebooklm-mcp-cli) | research-collector | `pip install notebooklm-mcp-cli` |
| `codex` (@openai/codex) | article-optimizer, score-optimizer | `npm install -g @openai/codex` |
| `wechatsync` (@wechatsync/cli) | publisher-wechatsync | `npm install -g @wechatsync/cli` + Chrome 扩展 |

Python 3.9+ 是运行脚本必需的(macOS 自带、绝大多数 Linux 也自带)。

---

## 1. 装 Claude Code(宿主运行时)

这是一套 Claude Code skill,得先有 Claude Code。已经装了就跳过。

- macOS / Linux / Windows: [docs.claude.com/en/docs/claude-code/setup](https://docs.claude.com/en/docs/claude-code/setup)
- 验证: `claude --version`

Claude Code 装好后,装本 skill 集:

```
/plugin marketplace add xiaomoBoy/claude-writing-skills
/plugin install claude-writing-skills@claude-writing-skills
```

然后 `/plugin list` 应该能看到 `claude-writing-skills@claude-writing-skills`。

> **不用 Claude Code?** 看 [INTEGRATIONS.zh-CN.md](INTEGRATIONS.zh-CN.md),里面写了怎么在 Cursor / Aider / Codex CLI / 直调 Claude API 里用这些 skill。

---

## 2. yt-dlp

被 `yt-dlp-direct`、`research-collector` 用到。

### macOS

```bash
brew install yt-dlp
# 可选但建议(抽音频 / 合流需要):
brew install ffmpeg
```

### Linux

```bash
# Debian / Ubuntu(apt 版本经常过时,推荐用 pip)
sudo apt install yt-dlp ffmpeg
# 或(推荐,永远最新):
pip install -U yt-dlp
sudo apt install ffmpeg

# Arch
sudo pacman -S yt-dlp ffmpeg

# Fedora
sudo dnf install yt-dlp ffmpeg
```

### Windows

```powershell
# 选项 A: winget
winget install yt-dlp.yt-dlp
winget install Gyan.FFmpeg

# 选项 B: scoop
scoop install yt-dlp ffmpeg

# 选项 C: pip(跨平台)
pip install -U yt-dlp
# ffmpeg 单独从 https://ffmpeg.org 下载
```

### 验证

```bash
yt-dlp --version       # 2024.xx.xx 或更新
ffmpeg -version        # 6.x 或更新
```

### 常见问题

- **Linux apt 安装的 yt-dlp 报版本太老** —— apt 源更新慢。改用 `pip install -U yt-dlp`,把 `~/.local/bin` 加进 `PATH`
- **403 Forbidden / 区域限制** —— 试 `--cookies-from-browser chrome`(浏览器要登过相关账号)
- **JS runtime 警告** —— `--simulate` / `--print` 模式下可以忽略,需要完整 JS 提取就装 Node.js

---

## 3. notebooklm-mcp-cli(`nlm`)

被 `research-collector` 用到。作者: [jacob-bd/notebooklm-mcp-cli](https://github.com/jacob-bd/notebooklm-mcp-cli)。

### 所有 OS(pip)

```bash
pip install notebooklm-mcp-cli
# 或用 pipx(推荐,环境隔离):
pipx install notebooklm-mcp-cli
```

> 命令名叫 `nlm`(不是 `notebooklm-mcp-cli`)。

### 登录

```bash
nlm login
# 会打开浏览器走 Google 登录流程,登完回 terminal
# Session ~20 分钟,过期重跑 nlm login
```

### 验证

```bash
nlm --version             # 0.5.x 或更新
nlm login --check         # 返回 "logged in" 或 "session expired"
nlm notebook list         # 应该能列出你已有的 NotebookLM notebook
```

### 常见问题

- **pip 装完报 `command not found: nlm`** —— pip 的 install prefix 没在 `PATH` 上。macOS 一般加 `export PATH="$HOME/Library/Python/3.x/bin:$PATH"`(或用 `pipx`)
- **`nlm login --check` 显示过期** —— session 很短(~20 分钟),重跑 `nlm login` 即可
- **Deep research 跑 5 分钟以上** —— 正常,别 kill。用 `nlm research status <alias> --max-wait 360` 轮询
- **同一个 notebook 不能并发 research** —— 等上一个跑完,或用 `--force` 重置

---

## 4. @openai/codex(`codex`)

被 `article-optimizer`、`score-optimizer` 用到。来源: [openai/codex](https://github.com/openai/codex)。

### 所有 OS(npm)

```bash
npm install -g @openai/codex
# 如果没管 global npm prefix,需要 sudo:
sudo npm install -g @openai/codex
```

要求 Node.js 20+。没装 Node:

```bash
# macOS
brew install node
# Linux Debian/Ubuntu
sudo apt install nodejs npm
# 或推荐用 nvm: https://github.com/nvm-sh/nvm
```

### 登录

```bash
codex auth login
# 浏览器流程,登完回 terminal
```

需要一个能用 Codex 的 OpenAI API key,或 Codex CLI 订阅 —— 详见 [openai/codex README](https://github.com/openai/codex)。

### 验证

```bash
codex --version          # 0.13x 或更新
codex exec "say hi"      # 简单 sanity check,应该会回复
```

### 路径覆盖

如果 `codex` 装在非标准位置(nvm 管的 Node、自定义 prefix),skill 默认从 `PATH` 找。手动覆盖:

```bash
export CODEX_CLI_PATH="/path/to/codex"
```

### 常见问题

- **`Error: not authenticated`** —— 重跑 `codex auth login`,token 可能轮换了
- **装完还报 `codex: command not found`** —— npm global bin 不在 PATH 上。`npm config get prefix` 看 prefix,把 `<prefix>/bin` 加进 PATH
- **macOS 沙箱报错** —— 首次会,系统设置 → 隐私 里允许

---

## 5. @wechatsync/cli(`wechatsync`)

被 `publisher-wechatsync` 用到。专门发中文平台(知乎 / 掘金 / CSDN / 公众号 / 小红书 / 头条 等)。不发中文平台就跳过。

### 所有 OS(npm)

```bash
npm install -g @wechatsync/cli
# 验证:
wechatsync --version     # 1.x 或更新
```

### 装 Chrome 扩展

Wechatsync 需要一个 Chrome 扩展把命令行跟你登录的平台账号桥起来:

1. 装 Chrome(或 Edge / 任意 Chromium 内核浏览器)
2. Chrome Web Store 搜 **Wechatsync** 装上
3. 打开扩展弹窗 → 启用 **"同步桥接" / "MCP Connection"**
4. 复制扩展里显示的 token

### 设置 token

```bash
export WECHATSYNC_TOKEN="<从扩展复制过来的 token>"
# 持久化:
echo 'export WECHATSYNC_TOKEN="..."' >> ~/.zshrc   # 或 ~/.bashrc
```

可选: 如果 9527 端口被占,换:

```bash
export SYNC_WS_PORT=9528
```

### 登录目标平台

扩展用的是你当前 Chrome 的 cookie。所以你必须**先在 Chrome 里登录每一个要发的平台**:

- 知乎: https://www.zhihu.com —— 登录
- 掘金: https://juejin.cn —— 登录
- 公众号: https://mp.weixin.qq.com —— 登录
- ... 等等

然后查状态:

```bash
wechatsync platforms -a
# 应该列出每个平台和登录状态
```

### 验证

```bash
wechatsync --version
echo "$WECHATSYNC_TOKEN" | wc -c    # > 1 表示 token 已设
wechatsync platforms -a              # 各平台登录状态
```

### 常见问题

- **"已有实例正在运行但 Chrome Extension 未连接"** —— 打开扩展、启用 MCP Connection、重新 export token
- **`未登录 zhihu`** —— Chrome 去 zhihu.com 登录,再跑 `wechatsync auth zhihu -r` 刷新
- **图片上传失败** —— 图片路径是 URL 编码的(Obsidian 风格)。publisher-wechatsync skill 会自动跑 `scripts/normalize_image_paths.py` 修;如果直接调 wechatsync,先手跑这个脚本

---

## 6. 可选: Python 3.9+(脚本运行用)

Skill 里几个 helper 脚本用 Python(`normalize_image_paths.py`、`run_single_score.py`、`run_scoring.py`、`evaluate.py`)。

```bash
# macOS 自带 Python 3.9+
python3 --version

# Debian/Ubuntu
sudo apt install python3 python3-pip

# Windows
winget install Python.Python.3.12
# 或从 https://python.org 下载
```

脚本只用标准库,不需要额外 pip install。

---

## 一键 smoke test

把上面装好的(或装完你要用的部分)之后,跑这个确认:

```bash
# 核心
yt-dlp --version            && echo "✓ yt-dlp"           || echo "✗ yt-dlp 没装"
nlm --version               && echo "✓ nlm"              || echo "✗ nlm 没装"
codex --version             && echo "✓ codex"            || echo "✗ codex 没装"
wechatsync --version        && echo "✓ wechatsync"       || echo "✗ wechatsync 没装"
python3 --version           && echo "✓ python3"          || echo "✗ python3 没装"
ffmpeg -version >/dev/null  && echo "✓ ffmpeg"           || echo "✗ ffmpeg 没装(可选)"

# 登录状态
nlm login --check 2>&1 | grep -q "logged in" && echo "✓ nlm 已登录" || echo "✗ nlm 需要登录"
[ -n "$WECHATSYNC_TOKEN" ]  && echo "✓ wechatsync token 已设" || echo "✗ WECHATSYNC_TOKEN 未设"
```

每条相关的都 ✓ 了就齐了。端到端走一遍见 [docs/USAGE.zh-CN.md](docs/USAGE.zh-CN.md)。

---

## 升级

| 工具 | 升级命令 |
|---|---|
| `yt-dlp` | `pip install -U yt-dlp` 或 `brew upgrade yt-dlp` |
| `nlm` | `pip install -U notebooklm-mcp-cli` |
| `codex` | `npm install -g @openai/codex@latest` |
| `wechatsync` | `npm install -g @wechatsync/cli@latest` |
| Claude Code | 走 Claude Code 官方升级路径 |
| 本 skill 集 | `/plugin update claude-writing-skills@claude-writing-skills` |

---

## 卸载

```bash
# Skill 集
/plugin uninstall claude-writing-skills@claude-writing-skills
/plugin marketplace remove claude-writing-skills

# 依赖(只在你不在其他地方用的情况下)
pip uninstall yt-dlp notebooklm-mcp-cli
npm uninstall -g @openai/codex @wechatsync/cli
```
