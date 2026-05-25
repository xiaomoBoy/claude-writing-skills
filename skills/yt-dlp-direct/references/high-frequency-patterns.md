# yt-dlp High-Frequency Patterns

## 1. 探测但不下载

```bash
yt-dlp --simulate --print "%(title)s" "<url>"
yt-dlp --dump-single-json "<url>"
```

## 2. 看格式

```bash
yt-dlp -F "<url>"
yt-dlp -S "res:1080,ext:mp4:m4a" "<url>"
```

## 3. 下载单视频

```bash
yt-dlp -o "%(title)s [%(id)s].%(ext)s" "<url>"
```

## 4. 提音频

```bash
yt-dlp -x --audio-format mp3 "<url>"
yt-dlp -x --audio-format m4a "<url>"
```

## 5. 下字幕

```bash
yt-dlp --write-subs --write-auto-subs --skip-download "<url>"
yt-dlp --write-subs --sub-langs "en,zh-Hans,zh-Hant" --skip-download "<url>"
```

## 6. 播放列表

```bash
yt-dlp --flat-playlist "<playlist-url>"
yt-dlp -I 1:10 "<playlist-url>"
yt-dlp -o "%(playlist_index)s - %(title)s [%(id)s].%(ext)s" "<playlist-url>"
```

## 7. 搜索

```bash
yt-dlp "ytsearch5:Claude Code skills"
yt-dlp --simulate --print "%(title)s | %(webpage_url)s" "ytsearch5:Claude Code skills"
```

## 8. Cookies / 登录态

```bash
yt-dlp --cookies-from-browser chrome "<url>"
yt-dlp --cookies cookies.txt "<url>"
yt-dlp --impersonate chrome "<url>"
```

## 9. 依赖排查

```bash
yt-dlp --version
yt-dlp -v "<url>"
ffmpeg -version
```

