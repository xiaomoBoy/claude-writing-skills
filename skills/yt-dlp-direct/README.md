# yt-dlp-direct

A pragmatic command-reference skill for the [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) CLI. When you want to download or inspect online audio/video, Claude reaches for `yt-dlp` directly instead of writing scripts around it.

## What it does

Wraps operational knowledge for the common (and not-so-common) `yt-dlp` patterns:

- Single video / playlist download
- Audio-only extraction (`-x --audio-format mp3`)
- Subtitle download (auto vs manual, language selection)
- Format inspection (`-F`) and selector strings
- Output templates (`%(title)s.%(ext)s` and friends)
- Cookies-from-browser flows for logged-in content
- Practical troubleshooting (geo-blocks, rate limits, missing ffmpeg, region-restricted videos)

It doesn't try to replace `yt-dlp` with a wrapper — it knows the right invocation for the situation and runs it.

## Requirements

- `yt-dlp` installed and on `PATH` (`pip install yt-dlp` or `brew install yt-dlp`)
- `ffmpeg` for audio extraction / merging
- Optionally a browser with logged-in cookies for `--cookies-from-browser`

## Quick examples

```
You: 把这个 YouTube 播放列表的音频下下来，存到 ./music/
You: 这个视频的英文字幕拉一下
You: 看下这个视频有哪些可选格式
You: 这个频道的最新 5 个视频下到当前目录
```

In each case, Claude constructs the exact `yt-dlp` command and runs it, instead of spending tokens reinventing the helper.

## What it won't do

- Write commentary on copyright / DRM policy
- Attempt to bypass platform DRM
- Suggest browser screen recording as an alternative
- Re-install `yt-dlp` if your install is broken (it'll tell you to update)

See [SKILL.md](SKILL.md) for the full command reference and troubleshooting.
