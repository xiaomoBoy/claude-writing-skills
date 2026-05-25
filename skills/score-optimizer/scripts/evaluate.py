#!/usr/bin/env python3
"""
evaluate.py — 评估评分结果的准确度

将 AI 评分结果 (scores.json) 与人工标注 (labels.json) 对比，
计算多个准确度指标，输出评估报告。

此文件是固定的评估工具，Agent 不应修改。
"""

import json
import sys
import os
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ASSETS_DIR = SKILL_DIR / "assets"


def load_json(filepath):
    """加载 JSON 文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_metrics(human_scores, ai_scores):
    """计算单篇文章的评分偏差"""
    dimensions = [
        'title_score', 'opening_score', 'emotion_score', 'info_score',
        'interaction_score', 'structure_score', 'trending_score', 'ip_score',
        'ai_flavor_score'
    ]

    errors = {}
    total_abs_error = 0
    count = 0

    for dim in dimensions:
        human_val = human_scores.get(dim, 0)
        ai_val = ai_scores.get(dim, 0)
        error = ai_val - human_val
        abs_error = abs(error)
        errors[dim] = {'human': human_val, 'ai': ai_val, 'error': error, 'abs_error': abs_error}
        total_abs_error += abs_error
        count += 1

    mae = total_abs_error / count if count > 0 else float('inf')
    return errors, mae


def calculate_rank_accuracy(labels_data, scores_data):
    """计算排名准确度（爆款排序是否正确）"""
    # 按人工标注的total排序
    human_ranking = sorted(
        [(a['file'], a['human_total']) for a in labels_data['articles']],
        key=lambda x: x[1], reverse=True
    )

    # 按AI评分的total排序
    ai_totals = {}
    for result in scores_data['results']:
        filename = result['file']
        scores = result.get('scores', {})
        total = scores.get('total_score', 0)
        ai_totals[filename] = total

    ai_ranking = sorted(ai_totals.items(), key=lambda x: x[1], reverse=True)

    # 计算排名相关性（简化版 Spearman）
    human_ranks = {item[0]: i for i, item in enumerate(human_ranking)}
    ai_ranks = {item[0]: i for i, item in enumerate(ai_ranking)}

    n = len(human_ranks)
    if n == 0:
        return 0.0, [], []

    # Spearman rank correlation
    d_squared_sum = 0
    common_files = set(human_ranks.keys()) & set(ai_ranks.keys())

    for f in common_files:
        d = human_ranks[f] - ai_ranks[f]
        d_squared_sum += d * d

    n_common = len(common_files)
    if n_common <= 1:
        spearman = 1.0
    else:
        spearman = 1 - (6 * d_squared_sum) / (n_common * (n_common ** 2 - 1))

    return spearman, human_ranking, ai_ranking


def calculate_viral_classification(labels_data, scores_data):
    """计算爆款分类准确度（high/low 分类是否正确）"""
    correct = 0
    total = 0

    results_by_file = {}
    for result in scores_data['results']:
        results_by_file[result['file']] = result.get('scores', {})

    details = []
    for article in labels_data['articles']:
        filename = article['file']
        human_level = article['viral_level']
        ai_scores = results_by_file.get(filename, {})
        ai_total = ai_scores.get('total_score', 0)

        # 阈值：总分 >= 56 认为是爆款 (62.5% of 90)
        ai_level = 'high' if ai_total >= 56 else 'low'

        is_correct = (human_level == ai_level)
        if is_correct:
            correct += 1
        total += 1

        details.append({
            'file': filename,
            'human_level': human_level,
            'ai_level': ai_level,
            'ai_total': ai_total,
            'correct': is_correct
        })

    accuracy = correct / total if total > 0 else 0
    return accuracy, details


def main():
    scores_file = sys.argv[1] if len(sys.argv) > 1 else 'scores.json'
    labels_file = sys.argv[2] if len(sys.argv) > 2 else str(ASSETS_DIR / 'articles' / 'labels.json')

    # 检查文件存在
    if not os.path.exists(scores_file):
        print(f"错误: 未找到评分结果文件 {scores_file}")
        print("请先运行: ./run_scoring.sh")
        sys.exit(1)

    if not os.path.exists(labels_file):
        print(f"错误: 未找到标注文件 {labels_file}")
        sys.exit(1)

    # 加载数据
    scores_data = load_json(scores_file)
    labels_data = load_json(labels_file)

    # 构建评分查找表
    scores_by_file = {}
    for result in scores_data['results']:
        scores_by_file[result['file']] = result.get('scores', {})

    print("=" * 60)
    print("📊 自媒体文章爆款评分 — 评估报告")
    print("=" * 60)

    # 1. 逐篇文章的维度偏差
    total_mae = 0
    article_count = 0

    print("\n## 各文章维度评分对比\n")

    for article in labels_data['articles']:
        filename = article['file']
        human_scores = article['human_scores']
        ai_scores = scores_by_file.get(filename, {})

        if not ai_scores or 'error' in ai_scores:
            print(f"⚠️  {filename}: 评分失败，跳过")
            continue

        errors, mae = calculate_metrics(human_scores, ai_scores)
        total_mae += mae
        article_count += 1

        human_total = article['human_total']
        ai_total = ai_scores.get('total_score', 0)

        print(f"### {filename}")
        print(f"  人工总分: {human_total} | AI总分: {ai_total} | 偏差: {ai_total - human_total:+.1f}")
        print(f"  MAE (平均绝对误差): {mae:.2f}")
        for dim, val in errors.items():
            arrow = "✅" if val['abs_error'] <= 1 else ("⚠️" if val['abs_error'] <= 2 else "❌")
            print(f"    {arrow} {dim}: 人工={val['human']} AI={val['ai']} (偏差={val['error']:+.1f})")
        print()

    # 2. 排名准确度
    spearman, human_ranking, ai_ranking = calculate_rank_accuracy(labels_data, scores_data)

    print("\n## 排名准确度\n")
    print(f"  Spearman 排名相关系数: {spearman:.4f}")
    print(f"  (1.0=完全一致, 0=无关, -1=完全反向)")
    print()
    print("  人工排名:")
    for i, (f, score) in enumerate(human_ranking):
        print(f"    {i+1}. {f} (总分={score})")
    print()
    print("  AI排名:")
    for i, (f, score) in enumerate(ai_ranking):
        print(f"    {i+1}. {f} (总分={score})")

    # 3. 爆款分类准确度
    classification_accuracy, details = calculate_viral_classification(labels_data, scores_data)

    print(f"\n## 爆款分类准确度\n")
    print(f"  分类准确率: {classification_accuracy:.1%}")
    print(f"  (阈值: 总分>=50 判定为爆款)")
    print()
    for d in details:
        icon = "✅" if d['correct'] else "❌"
        print(f"    {icon} {d['file']}: 人工={d['human_level']} AI={d['ai_level']} (AI总分={d['ai_total']})")

    # 4. 综合指标
    avg_mae = total_mae / article_count if article_count > 0 else float('inf')

    print(f"\n## 综合指标\n")
    print(f"  整体 MAE (平均绝对误差): {avg_mae:.2f}")
    print(f"  排名相关系数 (Spearman): {spearman:.4f}")
    print(f"  分类准确率: {classification_accuracy:.1%}")

    # 综合评分 (0-100)
    # MAE 满分标准: MAE<=1 得满分40, MAE>=5 得0分
    mae_score = max(0, min(40, 40 * (1 - (avg_mae - 1) / 4)))
    # Spearman 满分标准: 1.0 得满分30
    spearman_score = max(0, spearman * 30)
    # 分类准确率满分标准: 100% 得满分30
    class_score = classification_accuracy * 30

    composite = mae_score + spearman_score + class_score

    print(f"\n  📈 综合评分: {composite:.1f} / 100")
    print(f"     - 9维度准确度 ({mae_score:.1f}/40)")
    print(f"     - 排名平稳度 ({spearman_score:.1f}/30)")
    print(f"     - 爆款命中率 ({class_score:.1f}/30)")

    # 输出机器可读的关键指标
    print(f"\n---")
    print(f"composite_score: {composite:.1f}")
    print(f"mae: {avg_mae:.4f}")
    print(f"spearman: {spearman:.4f}")
    print(f"classification: {classification_accuracy:.4f}")


if __name__ == '__main__':
    main()
