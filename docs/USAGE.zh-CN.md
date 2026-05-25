# 使用文档

5 个 skill 端到端怎么用。各 skill 互相独立,挑你需要的组合。

**English version**: [USAGE.md](USAGE.md)

---

## 工具箱预设的工作流

```
   research-collector       (你写)         article-optimizer       publisher-wechatsync
        │                     │                  │                       │
        ▼                     ▼                  ▼                       ▼
  YouTube + 网页        你在编辑器里        按爆款评分卡              发草稿到
  → NotebookLM          写正经初稿          逐轮改稿打分              中文平台
  → 汇总 md             (用你的工具)        直到分数平台期            (强制 dry-run)


                              [副本]
                              score-optimizer
                              用你标注过的样本校准评分卡本身


                              [辅助]
                              yt-dlp-direct
                              要下视频音频的时候随手叫
```

Skill 之间不直接通信,中间产物全是普通 markdown 文件。**你是集成层** —— 该叫下一个 skill 的时候由你决定。

---

## 端到端走一遍

目标:写一篇 "2026 年的 self-hosted AI agents" 长文。

### Step 1 — 拉素材 (research-collector)

```
你: 帮我收集 "self-hosted AI agents 2026" 这个话题的素材,输出到 ./research/self-hosted-ai/

Claude(触发 research-collector):
  → 先问你: 主题 / 角度 / notebook 命名 / 量级 确认
  → 创建 NotebookLM notebook "self-hosted AI agents 2026 素材"
  → yt-dlp 跑 2-3 个角度的搜索,取 top 15 视频
  → 逐条加为 source(每条 sleep 2 秒防限流)
  → 跑 `nlm research start --mode deep`(~5 分钟,自动发现 ~40 个网页源)
  → import research 结果到 notebook
  → 跑 3 个分析查询:
      Q1: 被最多来源推荐的 top 10 工具
      Q2: 按目标读者画像筛选
      Q3: 入门方式 + 常见坑
  → 写到 ./research/self-hosted-ai/research-summary.md
```

10 分钟能看完的素材汇总,加一个可以继续 chat 追问的 notebook。

### Step 2 — 可选:深挖某个视频 (yt-dlp-direct)

如果某个 YouTube 视频特别对口,想拿字幕和音频:

```
你: 把 https://www.youtube.com/watch?v=XXX 的字幕和音频都拉下来,存到 ./research/self-hosted-ai/

Claude(触发 yt-dlp-direct):
  → 构造命令:
      yt-dlp --write-subs --sub-lang en --write-auto-subs --skip-download URL
      yt-dlp -x --audio-format mp3 -o './research/self-hosted-ai/%(title)s.%(ext)s' URL
  → 跑,回报文件路径
```

### Step 3 — 写初稿

这一步**不在工具箱里**。用你的编辑器、你常用的 AI、你自己的写作 skill,写出真正的初稿。存成 `path/to/article.md`。

下面的 skill 假设你有一份带 frontmatter(`title` / `date` 等)的 markdown 文件。

### Step 4 — 给初稿打分 (article-optimizer)

```
你: 给 path/to/article.md 跑一遍评分

Claude(触发 article-optimizer):
  → 调用 scripts/run_single_score.py path/to/article.md
  → 返回 JSON:
    {
      "title_score": 7,
      "opening_score": 5,
      "emotion_score": 6,
      "info_score": 9,
      "interaction_score": 4,
      "structure_score": 8,
      "trending_score": 6,
      "ip_score": 7,
      "ai_flavor_score": 6,
      "total_score": 58,
      "viral_percentage": 64.4
    }
```

看最低分的几维。这个例子里 `interaction_score: 4`(没 CTA / 没钩子)和 `opening_score: 5`(开头太平)。

### Step 5 — 针对性改 + 重打分

```
你: opening 太弱,帮我改前 3 段,再打分

Claude:
  → 改开头(只改这一处,不重写全文)
  → 重打分
  → 回报: opening_score 5 → 8, total 58 → 64, viral_percentage 64.4 → 71.1
```

迭代到每轮提升小于你能接受的阈值就停。

### Step 6 — 发布 (publisher-wechatsync) —— 只针对中文平台

> 注意:这个 skill 专门面向中文平台(知乎 / 掘金 / CSDN / 公众号 / 小红书 等),底层是 [`@wechatsync/cli`](https://www.npmjs.com/package/@wechatsync/cli)。不发中文平台就跳过这步。

一次性准备:
- `npm install -g @wechatsync/cli`
- 装 Wechatsync Chrome 扩展
- 从扩展里拿 token,`export WECHATSYNC_TOKEN=…`
- 在 Chrome 里登录目标平台

```
你: 把 path/to/article.md 发到知乎和掘金,先 dry-run

Claude(触发 publisher-wechatsync):
  → which wechatsync             → ok
  → echo $WECHATSYNC_TOKEN | wc  → ok
  → 跑 python3 scripts/normalize_image_paths.py path/to/article.md --dry-run
  → 规整 URL 编码的图片路径(Obsidian 默认的 %20 等)
  → wechatsync platforms -a       → 显示各平台登录状态
  → wechatsync sync ... --dry-run → 显示将发到哪
  → 等你确认
  → wechatsync sync ...           → 真发,只填草稿
  → 按平台逐个回报成功/失败 + 草稿 ID
```

Skill **不会替你点"发布"按钮**,只填草稿。你去各平台后台预览 → 配封面 → 手动点发布。

---

## 副本:校准评分卡 (score-optimizer)

打过 20+ 篇后,你大概率会发现评分卡有偏(比如标题打太松、结构打太紧)。校准方式:

1. 把 10-30 篇你**自己标注过分数的** `.md` 放进 `skills/score-optimizer/assets/articles/samples/`
2. `cp skills/score-optimizer/assets/articles/labels.example.json skills/score-optimizer/assets/articles/labels.json`
3. 在 `labels.json` 里给每篇样本填上你的评分
4. 跑基线:
   ```bash
   cd skills/score-optimizer
   python3 scripts/run_scoring.py
   python3 scripts/evaluate.py
   ```
5. 看每维度的 MAE / Spearman。如果 `title_score` 的 MAE 高,去改 `references/score_prompt.md`(标题维度的描述或 few-shot 例子),重跑
6. 一直迭代到评分卡跟你的判断对得上

Skill **不带任何样本** —— 没有你自己领域的样本,校准没意义。schema 见 [skills/score-optimizer/assets/articles/samples/README.md](../skills/score-optimizer/assets/articles/samples/README.md)。

---

## 一些常用习惯

### 改稿前后都打一遍分
任何改动之前先打一次基线分,改完再打。没有基线就不知道改得有没有用。

### 不自动串 skill
每个 skill 都需要你点头才走 —— 这是故意的。`research-collector` 不会自动调 `article-optimizer`。"调研够了" 和 "可以打分了" 之间的边界是判断题,你来判。

### 留 dry-run 输出
`publisher-wechatsync` 强制 dry-run。把 dry-run 输出存到文件,后面同一篇要发别的平台时可以 diff 对比。

---

## 通用 troubleshooting

| 现象 | 大概率原因 | 解法 |
|---|---|---|
| `codex: command not found`(article-optimizer / score-optimizer) | `codex` 不在 `PATH` 上 | 装 [openai/codex](https://github.com/openai/codex),或 `export CODEX_CLI_PATH=/path/to/codex` |
| `nlm login` 失败(research-collector) | session 过期(~20 分钟) | 重跑 `nlm login` |
| `wechatsync` 报 "Chrome Extension not connected" | 扩展没开,或 token 不一致 | 打开扩展 → 启用 MCP Connection → 重导 token → 重 `export` |
| `yt-dlp` 报 403 / 区域限制 | yt-dlp 版本太老,或被 geo-block | 先 `pip install -U yt-dlp`;geo 问题可试 `--cookies-from-browser chrome` |
| 知乎/掘金图片上传失败 | 图片路径未规整 | 确认 `normalize_image_paths.py` 跑过了(publisher-wechatsync 自动会跑) |

---

## 往下读

每个 skill 都有更细的文档:

- [skills/research-collector/SKILL.md](../skills/research-collector/SKILL.md) —— 完整的 phase 拆分 + query 模板
- [skills/publisher-wechatsync/SKILL.md](../skills/publisher-wechatsync/SKILL.md) —— 预检规则 / 硬约束 / troubleshooting
- [skills/article-optimizer/SKILL.md](../skills/article-optimizer/SKILL.md) —— 迭代循环细节
- [skills/score-optimizer/SKILL.md](../skills/score-optimizer/SKILL.md) —— 校准工作流 + 实验约束
- [skills/yt-dlp-direct/SKILL.md](../skills/yt-dlp-direct/SKILL.md) —— 命令大全

---

## 这套工具箱明确**不做**的事

- 不替你写正稿。写作里"声音"那部分太私人,没法泛化成 skill。你是作者,这些 skill 是操作支撑
- 不自动发布(只填草稿,你来点发布)
- 不绕开平台 DRM / 合规 / 限流
- 不把 5 个揉成一个端到端大 skill。边界故意做死
