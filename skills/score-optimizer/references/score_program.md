# 自媒体文章爆款评分 — 自主迭代研究

这是一个让 AI Agent 自主研究和优化"自媒体文章爆款评分系统"的实验。

## 概述

你将通过不断修改评分 Prompt（`score_prompt.md`），提升对文章爆款潜力的评分准确度。每次实验你修改 Prompt，然后对文章集进行评分，评估准确度，决定保留或回滚。

## Setup

开始前，与用户确认：

1. **约定标签**：基于日期提出标签（如 `mar17`）。分支 `scoring/\<tag\>` 必须不存在。
2. **创建分支**：`git checkout -b scoring/\<tag\>` 从当前 master 分支。
3. **阅读文件**：
   - `score_prompt.md` — 你要修改的评分 Prompt
   - `run_scoring.py` — 评分运行脚本（不要修改）
   - `evaluate.py` — 评估脚本（不要修改）
4. **运行基线**：执行一次完整评分+评估，记录基线分数。
5. **初始化 score_results.tsv**：创建只有表头的文件。

确认后开始实验循环。

## 实验循环

**你可以做的：**
- 修改 `score_prompt.md` — 这是你唯一可以编辑的文件。可以改：
  - 评分维度的定义和描述
  - 各维度的评分标准和示例
  - 总体评分的权重分配
  - Prompt 的措辞和指令风格
  - 增加或删除维度
  - 添加 few-shot 示例
  - 调整输出格式要求

**你不能做的：**
- 修改 `evaluate.py`（固定的评估工具）
- 修改 `run_scoring.py`（固定的评分运行器）
- 安装新的依赖

**目标：让综合评分 (composite_score) 尽可能高。** 综合评分由以下三部分组成：
- 维度准确度（MAE 越低越好），占 40%
- 排名准确度（Spearman 相关系数），占 30%
- 分类准确度（爆款/非爆款分类），占 30%

## 运行实验

```bash
# 1. 运行评分（调用 Gemini CLI 对每篇文章评分）
python3 run_scoring.py > scoring.log 2>&1

# 2. 评估结果
python3 evaluate.py > eval.log 2>&1

# 3. 查看关键指标
grep "^composite_score:\|^mae:\|^spearman:\|^classification:" eval.log
```

## 记录结果

每次实验完成后，记录到 `score_results.tsv`（Tab 分隔，不要用逗号）。

表头和列定义：

```
commit\tcomposite_score\tmae\tspearman\tstatus\tdescription
```

1. git commit hash（短格式，7字符）
2. composite_score（综合评分，0-100）
3. mae（平均绝对误差）
4. spearman（排名相关系数）
5. status：`keep`、`discard` 或 `error`
6. 简短描述本次尝试的内容

示例：

```
commit\tcomposite_score\tmae\tspearman\tstatus\tdescription
a1b2c3d\t65.3\t1.85\t0.9000\tkeep\tbaseline
b2c3d4e\t72.1\t1.42\t0.9500\tkeep\t增加 few-shot 示例
c3d4e5f\t61.0\t2.10\t0.8000\tdiscard\t移除情绪价值维度
```

## 实验循环流程

LOOP FOREVER:

1. 查看 git 状态：当前分支/commit
2. 修改 `score_prompt.md`，尝试新的评分策略
3. `git commit -am "描述你的修改"`
4. 运行评分：`python3 run_scoring.py > scoring.log 2>&1`
5. 运行评估：`python3 evaluate.py > eval.log 2>&1`
6. 读取结果：`grep "^composite_score:\|^mae:\|^spearman:\|^classification:" eval.log`
```
7. 如果 grep 输出为空，评分出错。运行 `tail -n 30 eval.log` 查看错误。
8. 记录到 score_results.tsv（不要 commit 这个文件）
9. 如果 composite_score 提高了 → keep，保留 git commit
10. 如果 composite_score 没有提高 → discard，`git reset --hard HEAD~1`

## 优化思路

以下是一些可以尝试的方向（按潜力从高到低排列）：

1. **添加 few-shot 示例**：在 Prompt 中给出高分和低分文章的评分示例
2. **细化评分标准**：每个分数段（1-3、4-6、7-9、10）给出具体描述
3. **调整维度权重**：某些维度可能比其他维度更能预测爆款
4. **增加校准指令**：提醒 AI 不要全给高分，注意分数分布
5. **优化 Prompt 结构**：尝试 Chain-of-Thought、先分析后打分等策略
6. **合并或拆分维度**：某些维度可能重叠或者太粗糙
7. **增加反面示例**：展示常见评分错误和如何避免
8. **增加平台特定指令**：针对特定平台（小红书/公众号/抖音）优化

## 重要提示

**永远不要停下来**：一旦实验循环开始，不要暂停询问用户是否继续。用户可能在睡觉或离开。你是自主的。如果用完了想法，再想想——重新阅读标注数据、分析评分偏差模式、尝试组合之前的策略。循环一直运行直到被人工中断或者10轮都没有提升。

**简洁性原则**：如果一个修改让 Prompt 大幅增加复杂度但只带来微小提升，不值得保留。反过来，删除内容后效果不变或更好，那就是化简胜利。
