#!/usr/bin/env python3
"""
generate_optimize_chart.py — 从 optimization_results.tsv 生成文章优化进度图

用法:
    python3 generate_optimize_chart.py                        # 读取 optimization_results.tsv
    python3 generate_optimize_chart.py my_results.tsv         # 指定 TSV 文件
    python3 generate_optimize_chart.py results.tsv out.png    # 指定输出文件

TSV 格式（Tab 分隔）:
    commit  viral_score  status  file_path  description
"""

import sys
import csv
import matplotlib.pyplot as plt
from pathlib import Path


def load_tsv(filepath):
    rows = []
    with open(filepath, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            rows.append(row)
    return rows


def main():
    tsv_file = sys.argv[1] if len(sys.argv) > 1 else 'optimization_results.tsv'
    out_file = sys.argv[2] if len(sys.argv) > 2 else 'process.png'

    if not Path(tsv_file).exists():
        print(f"Error: {tsv_file} not found")
        print("Please run the optimization loop first and record results to optimization_results.tsv")
        sys.exit(1)

    rows = load_tsv(tsv_file)
    if not rows:
        print("Error: no data rows in TSV")
        sys.exit(1)

    labels, scores, statuses, descriptions = [], [], [], []
    for i, row in enumerate(rows):
        labels.append(f"Iter {i}" if i > 0 else "Baseline")
        scores.append(float(row['viral_score']))
        statuses.append(row['status'])
        descriptions.append(row.get('description', ''))

    keep_x = [labels[i] for i, s in enumerate(statuses) if s == 'keep']
    keep_y = [scores[i] for i, s in enumerate(statuses) if s == 'keep']
    discard_x = [labels[i] for i, s in enumerate(statuses) if s == 'discard']
    discard_y = [scores[i] for i, s in enumerate(statuses) if s == 'discard']

    fig, ax = plt.subplots(figsize=(max(10, len(labels) * 0.9), 6))
    ax.set_facecolor('#f9f9f9')
    ax.grid(True, linestyle='--', alpha=0.5, axis='y')

    # 主折线（全部点）
    ax.plot(labels, scores, linestyle='-', color='#bdc3c7', linewidth=1.5, zorder=1)

    # keep 点（实心）
    if keep_x:
        ax.scatter(keep_x, keep_y, color='#2980b9', s=100, zorder=3, label='keep')

    # discard 点（空心）
    if discard_x:
        ax.scatter(discard_x, discard_y, color='#e74c3c', s=100, zorder=3,
                   facecolors='none', linewidths=2, label='discard')

    # 标注数值
    for i, (label, score) in enumerate(zip(labels, scores)):
        offset = 1.5 if score < max(scores) - 5 else -3.5
        ax.text(label, score + offset, f'{score:.1f}%',
                ha='center', va='bottom', fontsize=9, color='#2c3e50')

    # 参考线
    ax.axhline(y=80, color='#95a5a6', linestyle=':', linewidth=1.5, alpha=0.7, label='80% bar')
    ax.axhline(y=85, color='#e67e22', linestyle='--', linewidth=1.5, alpha=0.7, label='85% target')

    # 最高分标注
    max_score = max(scores)
    max_label = labels[scores.index(max_score)]
    ax.annotate(f'Best: {max_score:.1f}%', xy=(max_label, max_score),
                xytext=(max_label, max_score + 5),
                arrowprops=dict(facecolor='#27ae60', shrink=0.05, width=1, headwidth=7),
                fontsize=10, fontweight='bold', ha='center', color='#27ae60')

    ax.set_title('Article Optimization Progress', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Iteration', fontsize=12)
    ax.set_ylabel('Viral Score (%)', fontsize=12)
    ax.set_ylim(max(0, min(scores) - 10), min(100, max(scores) + 12))
    ax.legend(loc='lower right', fontsize=10)

    plt.xticks(rotation=30 if len(labels) > 8 else 0)
    plt.tight_layout()
    plt.savefig(out_file, dpi=150)
    print(f"Chart saved to {out_file}")


if __name__ == '__main__':
    main()
