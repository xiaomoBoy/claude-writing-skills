# 文章爆款潜力优化助手 — 自主研究指令

这是一个让 AI Agent 扮演"资深主编"，通过不断修改文章内容，提升其在固定评分系统下的"爆款潜力值"的实验。

## 概述

评分系统（`score_prompt.md`）是固定的。你的目标是修改用户提供的目标文章，使其获得的 `viral_percentage` 越高越好。

## Setup

开始前，与用户确认：

1. **确认目标文章**：请用户提供要优化的文章文件路径（如 `my_article.md`）。后续所有操作以此路径为准，记为 `<article_file>`。
2. **约定标签**：基于日期和目标文章提出标签（如 `opt_mar17`）。从 master 分支创建 `optimizing/<tag>` 分支。
3. **创建文件夹**：确保 `articles/optimized/` 文件夹存在，用于存放所有版本的优化文章。
4. **阅读文件**：
   - `score_prompt.md` — 指导你如何打分（固定不变，这是你的评价指南）
   - `<article_file>` — 你要修改和优化的文章
   - `run_single_score.py` — 用于给当前文章打分的工具
5. **获取基线分数**：
   `python3 run_single_score.py <article_file>`
   记录初始的 `viral_percentage` 和 `improvements`（改进建议）。
6. **初始化 optimization_results.tsv**：
   表头：`commit\tviral_score\tstatus\tfile_path\tdescription`

确认后开始优化循环。

## 优化循环

**你可以做的：**
- 修改 `<article_file>`：
  - 重写标题（爆款的关键）
  - 优化开头勾子（抓住读者）
  - 增加情绪价值（共鸣、冲突、金句）
  - 调优结构节奏（短句、分段、留白）
  - 增强互动引导（引导评论/收藏）
  - 注入个人 IP 感（鲜明观点、独特表达）
- **保存版本**：每次优化后的版本，必须另存为 `articles/optimized/iterationN.md`（N 为递增序号）。

**你不能做的：**
- 修改 `score_prompt.md`（它是固定规则）
- 修改 `run_single_score.py`（它是固定裁判）

## 运行实验

```bash
# 对修改后的文章打分，输出为 JSON
python3 run_single_score.py <article_file> > opt_run.log 2>&1

# 从日志中提取关键分数
grep "viral_percentage" opt_run.log
```

## 记录结果

记录到 `optimization_results.tsv`。

示例：
```
commit\tviral_score\tstatus\tfile_path\tdescription
a1b2c3d\t35\tkeep\tarticles/optimized/iteration0.md\t初始版本
b2c3d4e\t58\tkeep\tarticles/optimized/iteration1.md\t重写了有悬念感的标题，增加了争议性开头
c3d4e5f\t52\tdiscard\tarticles/optimized/iteration2.md\t尝试增加数据分析(效果下降)
```

## 迭代策略

1. **根据建议优化**：评分返回的 `improvements` 是你最好的改写指南。
2. **单点突破**：每次专注于优化一个维度（如先攻标题，再攻互动），看看分数变化。
3. **金句注入**：在关键转折点加入能引起转发冲动的金句。
4. **格式优化**：在手机端的阅读体验非常重要，尝试调整排版。

## 重要提示

**勇往直前**：不要停下来问用户意见。Agent 应该自主尝试各种写作风格和策略，直到分数达到理想水平（如 90% 以上）或被人工中断，或者迭代10轮都没有提升。
**真实性**：在追求高分的同时，保持文章逻辑自洽，不要为了高分写出毫无意义的内容。
