# Supported Sites Notes

`yt-dlp` 官方支持站点很多，覆盖 YouTube、Bilibili、X、TikTok、Instagram、SoundCloud、Vimeo 等大量平台。

但有 3 条要记住：

1. 列在支持清单里，不等于此刻一定可用
2. 很多站点的部分内容依赖 cookies 或登录态
3. 最可靠的判断方法不是背列表，而是先试 `--simulate`

推荐判断顺序：

```bash
yt-dlp --simulate "<url>"
yt-dlp -F "<url>"
yt-dlp -v "<url>"
```

如果用户只是问“这个站点支不支持”，优先这样回答：

- 官方支持面非常广
- 真正是否可用，要看当前 extractor 是否正常、内容是否需要登录、是否有区域限制
- 最稳妥的方式是直接用 `--simulate` 试一次

如果需要 extractor 级别确认，再看官方 `supportedsites.md`。

