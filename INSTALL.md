# Installation Guide

End-to-end install for everything `claude-writing-skills` depends on. **You don't need all of them** — install only the ones for the skills you'll use.

**中文版**: [INSTALL.zh-CN.md](INSTALL.zh-CN.md)

---

## TL;DR

| Dependency | Used by | Quickest install |
|---|---|---|
| Claude Code | the skills themselves | https://docs.claude.com/en/docs/claude-code |
| `yt-dlp` | yt-dlp-direct, research-collector | `brew install yt-dlp` / `pip install -U yt-dlp` |
| `ffmpeg` | (optional, for audio extraction in yt-dlp) | `brew install ffmpeg` / `apt install ffmpeg` |
| `nlm` (notebooklm-mcp-cli) | research-collector | `pip install notebooklm-mcp-cli` |
| `codex` (@openai/codex) | article-optimizer, score-optimizer | `npm install -g @openai/codex` |
| `wechatsync` (@wechatsync/cli) | publisher-wechatsync | `npm install -g @wechatsync/cli` + Chrome extension |

Python 3.9+ is required to run the bundled scripts (already present on macOS and most Linux).

---

## 1. Install Claude Code (the host runtime)

These are Claude Code skills — they need Claude Code to run. Skip if you already have it.

- macOS / Linux / Windows: [docs.claude.com/en/docs/claude-code/setup](https://docs.claude.com/en/docs/claude-code/setup)
- Confirm: `claude --version`

After Claude Code is set up, install this skill collection:

```
/plugin marketplace add xiaomoBoy/claude-writing-skills
/plugin install claude-writing-skills@claude-writing-skills
```

Then `/plugin list` should show `claude-writing-skills@claude-writing-skills`.

> **Not using Claude Code?** See [INTEGRATIONS.md](INTEGRATIONS.md) for how to use these skills in Cursor / Aider / Codex CLI / direct API.

---

## 2. yt-dlp

Used by: `yt-dlp-direct`, `research-collector`.

### macOS

```bash
brew install yt-dlp
# Optional but recommended for audio extraction / merging:
brew install ffmpeg
```

### Linux

```bash
# Debian / Ubuntu (apt version often outdated — pip is preferred)
sudo apt install yt-dlp ffmpeg
# OR (recommended, always latest):
pip install -U yt-dlp
sudo apt install ffmpeg

# Arch
sudo pacman -S yt-dlp ffmpeg

# Fedora
sudo dnf install yt-dlp ffmpeg
```

### Windows

```powershell
# Option A: winget
winget install yt-dlp.yt-dlp
winget install Gyan.FFmpeg

# Option B: scoop
scoop install yt-dlp ffmpeg

# Option C: pip (cross-platform)
pip install -U yt-dlp
# Then download ffmpeg separately from https://ffmpeg.org
```

### Verify

```bash
yt-dlp --version       # 2024.xx.xx or newer
ffmpeg -version        # 6.x or newer
```

### Common issues

- **"yt-dlp says it's outdated" on Linux apt** — apt repos lag. Switch to `pip install -U yt-dlp` and put `~/.local/bin` on `PATH`.
- **403 Forbidden / region-locked** — try `--cookies-from-browser chrome` (use a browser logged into the relevant account).
- **JS runtime warnings** — ignore for `--simulate` / `--print` workflows; install Node.js if you need full JS extraction.

---

## 3. notebooklm-mcp-cli (`nlm`)

Used by: `research-collector`. Author: [jacob-bd/notebooklm-mcp-cli](https://github.com/jacob-bd/notebooklm-mcp-cli).

### All OS (pip)

```bash
pip install notebooklm-mcp-cli
# or pipx (recommended — isolated env):
pipx install notebooklm-mcp-cli
```

> The binary name is `nlm` (not `notebooklm-mcp-cli`).

### Authenticate

```bash
nlm login
# Opens a browser flow → log into your Google account → return to terminal
# Session lasts ~20 minutes; re-run `nlm login` when it expires.
```

### Verify

```bash
nlm --version             # 0.5.x or newer
nlm login --check         # returns "logged in" or "session expired"
nlm notebook list         # should show your existing NotebookLM notebooks
```

### Common issues

- **`command not found: nlm` after pip install** — your `pip` install prefix isn't on `PATH`. On macOS the fix is usually `export PATH="$HOME/Library/Python/3.x/bin:$PATH"` (or use `pipx`).
- **`nlm login --check` returns expired** — sessions are short (~20 min). Just re-run `nlm login`.
- **Deep research takes 5+ minutes** — that's expected. Don't kill it. Use `nlm research status <alias> --max-wait 360` to poll.
- **Concurrent research not allowed** — one notebook can only have one in-flight research task. Wait or `--force` reset.

---

## 4. @openai/codex (`codex`)

Used by: `article-optimizer`, `score-optimizer`. Source: [openai/codex](https://github.com/openai/codex).

### All OS (npm)

```bash
npm install -g @openai/codex
# or with sudo if you don't manage global npm prefix:
sudo npm install -g @openai/codex
```

Requires Node.js 20+. If you don't have Node:

```bash
# macOS
brew install node
# Linux Debian/Ubuntu
sudo apt install nodejs npm
# Or use nvm (recommended): https://github.com/nvm-sh/nvm
```

### Authenticate

```bash
codex auth login
# Browser flow, then returns to terminal.
```

You'll need either an OpenAI API key with access to Codex, or a Codex CLI subscription — see [openai/codex README](https://github.com/openai/codex).

### Verify

```bash
codex --version          # 0.13x or newer
codex exec "say hi"      # quick sanity check; should reply
```

### Path override

If `codex` is installed in a non-standard location (nvm-managed Node, custom prefix), the skills auto-resolve `codex` from `PATH`. To override:

```bash
export CODEX_CLI_PATH="/path/to/codex"
```

### Common issues

- **`Error: not authenticated`** — run `codex auth login` again; tokens can rotate.
- **`codex: command not found`** even after install — npm global bin isn't on PATH. Run `npm config get prefix` and add `<prefix>/bin` to PATH.
- **Sandbox errors on macOS** — first time only; allow in System Settings → Privacy.

---

## 5. @wechatsync/cli (`wechatsync`)

Used by: `publisher-wechatsync`. Used for publishing to Chinese platforms (知乎 / 掘金 / CSDN / 公众号 / 小红书 / 头条 etc.). Skip if you don't publish to those.

### All OS (npm)

```bash
npm install -g @wechatsync/cli
# Verify:
wechatsync --version     # 1.x or newer
```

### Install the Chrome extension

Wechatsync needs a Chrome extension to bridge to logged-in platform sessions:

1. Install Chrome (or Edge / any Chromium-based browser)
2. Find the **Wechatsync** extension in the Chrome Web Store
3. Open the extension popup → enable **"同步桥接" / "MCP Connection"**
4. Copy the token shown in the extension

### Set the token

```bash
export WECHATSYNC_TOKEN="<paste-token-from-extension>"
# Make it permanent:
echo 'export WECHATSYNC_TOKEN="..."' >> ~/.zshrc   # or ~/.bashrc
```

Optional: change the bridge port if 9527 is taken:

```bash
export SYNC_WS_PORT=9528
```

### Log in to your target platforms

The extension uses your current Chrome cookies. So you must **first log in (in Chrome) to each platform you want to publish to**:

- 知乎: https://www.zhihu.com — sign in
- 掘金: https://juejin.cn — sign in
- 公众号: https://mp.weixin.qq.com — sign in
- ... etc.

Then check status:

```bash
wechatsync platforms -a
# Should list each platform and whether you're logged in
```

### Verify

```bash
wechatsync --version
echo "$WECHATSYNC_TOKEN" | wc -c    # > 1 (token set)
wechatsync platforms -a              # logged-in status per platform
```

### Common issues

- **"已有实例正在运行但 Chrome Extension 未连接"** — Open the extension, enable MCP Connection, re-export the token.
- **`未登录 zhihu`** — log in via Chrome at zhihu.com, then `wechatsync auth zhihu -r` to refresh.
- **Image upload fails** — your image paths are URL-encoded (Obsidian-style). The publisher-wechatsync skill auto-runs `scripts/normalize_image_paths.py` to fix this; if you're calling wechatsync directly, run that script first.

---

## 6. Optional: Python 3.9+ for bundled scripts

The skills use Python for some helpers (`normalize_image_paths.py`, `run_single_score.py`, `run_scoring.py`, `evaluate.py`).

```bash
# macOS comes with Python 3.9+ by default
python3 --version

# Debian/Ubuntu
sudo apt install python3 python3-pip

# Windows
winget install Python.Python.3.12
# or download from https://python.org
```

No Python packages need to be pre-installed — the scripts only use the standard library.

---

## Full verification (one-shot smoke test)

After installing everything (or just the parts you need), run this to confirm:

```bash
# Core
yt-dlp --version            && echo "✓ yt-dlp"           || echo "✗ yt-dlp missing"
nlm --version               && echo "✓ nlm"              || echo "✗ nlm missing"
codex --version             && echo "✓ codex"            || echo "✗ codex missing"
wechatsync --version        && echo "✓ wechatsync"       || echo "✗ wechatsync missing"
python3 --version           && echo "✓ python3"          || echo "✗ python3 missing"
ffmpeg -version >/dev/null  && echo "✓ ffmpeg"           || echo "✗ ffmpeg missing (optional)"

# Auth state
nlm login --check 2>&1 | grep -q "logged in" && echo "✓ nlm logged in" || echo "✗ nlm needs login"
[ -n "$WECHATSYNC_TOKEN" ]  && echo "✓ wechatsync token set" || echo "✗ WECHATSYNC_TOKEN not set"
```

If every relevant line shows ✓, you're ready. See [docs/USAGE.md](docs/USAGE.md) for the end-to-end walkthrough.

---

## Updating

| Tool | Update command |
|---|---|
| `yt-dlp` | `pip install -U yt-dlp` or `brew upgrade yt-dlp` |
| `nlm` | `pip install -U notebooklm-mcp-cli` |
| `codex` | `npm install -g @openai/codex@latest` |
| `wechatsync` | `npm install -g @wechatsync/cli@latest` |
| Claude Code | follow the official Claude Code update path |
| This skill collection | `/plugin update claude-writing-skills@claude-writing-skills` |

---

## Uninstall

```bash
# Skill collection
/plugin uninstall claude-writing-skills@claude-writing-skills
/plugin marketplace remove claude-writing-skills

# Dependencies (only if you don't use them elsewhere)
pip uninstall yt-dlp notebooklm-mcp-cli
npm uninstall -g @openai/codex @wechatsync/cli
```
