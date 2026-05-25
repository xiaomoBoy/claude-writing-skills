#!/usr/bin/env python3
"""
generate_score_chart.py — 从 score_results.tsv 生成评分系统优化进度图

用法:
    python3 generate_score_chart.py                       # 读取 score_results.tsv
    python3 generate_score_chart.py my_results.tsv        # 指定 TSV 文件
    python3 generate_score_chart.py results.tsv out.png   # 指定输出文件

TSV 格式（Tab 分隔）:
    commit  composite_score  mae  spearman  status  description
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
    tsv_file = sys.argv[1] if len(sys.argv) > 1 else 'score_results.tsv'
    out_file = sys.argv[2] if len(sys.argv) > 2 else 'score_progress.png'

    if not Path(tsv_file).exists():
        print(f"Error: {tsv_file} not found")
        print("Please run the scoring loop first and record results to score_results.tsv")
        sys.exit(1)

    rows = load_tsv(tsv_file)
    if not rows:
        print("Error: no data rows in TSV")
        sys.exit(1)

    labels, composites, maes, spearmans, statuses = [], [], [], [], []
    for i, row in enumerate(rows):
        labels.append(f"Iter {i}" if i > 0 else "Baseline")
        composites.append(float(row['composite_score']))
        maes.append(float(row['mae']))
        spearmans.append(float(row['spearman']))
        statuses.append(row['status'])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(max(10, len(labels) * 0.9), 9), sharex=True)
    fig.suptitle('Score System Optimization Progress', fontsize=16, fontweight='bold')

    for ax in (ax1, ax2):
        ax.set_facecolor('#f9f9f9')
        ax.grid(True, linestyle='--', alpha=0.5, axis='y')

    # — 上图：综合评分 —
    ax1.plot(labels, composites, linestyle='-', color='#bdc3c7', linewidth=1.5, zorder=1)

    keep_idx = [i for i, s in enumerate(statuses) if s == 'keep']
    discard_idx = [i for i, s in enumerate(statuses) if s == 'discard']

    if keep_idx:
        ax1.scatter([labels[i] for i in keep_idx], [composites[i] for i in keep_idx],
                    color='#2980b9', s=100, zorder=3, label='keep')
    if discard_idx:
        ax1.scatter([labels[i] for i in discard_idx], [composites[i] for i in discard_idx],
                    color='#e74c3c', s=100, zorder=3, facecolors='none', linewidths=2, label='discard')

    for label, score in zip(labels, composites):
        ax1.text(label, score + 1, f'{score:.1f}', ha='center', va='bottom', fontsize=9, color='#2c3e50')

    max_c = max(composites)
    max_label = labels[composites.index(max_c)]
    ax1.annotate(f'Best: {max_c:.1f}', xy=(max_label, max_c),
                 xytext=(max_label, max_c + 4),
                 arrowprops=dict(facecolor='#27ae60', shrink=0.05, width=1, headwidth=7),
                 fontsize=10, fontweight='bold', ha='center', color='#27ae60')

    ax1.set_ylabel('Composite Score (0-100)', fontsize=11)
    ax1.set_ylim(max(0, min(composites) - 10), min(105, max(composites) + 12))
    ax1.legend(loc='lower right', fontsize=10)

    # — 下图：MAE 和 Spearman —
    color_mae = '#e67e22'
    color_sp = '#8e44ad'

    ax2.plot(labels, maes, marker='o', linestyle='-', color=color_mae,
             linewidth=2, markersize=7, label='MAE (lower=better)')
    ax2b = ax2.twinx()
    ax2b.plot(labels, spearmans, marker='s', linestyle='--', color=color_sp,
              linewidth=2, markersize=7, label='Spearman (higher=better)')

    ax2.set_ylabel('MAE', fontsize=11, color=color_mae)
    ax2b.set_ylabel('Spearman', fontsize=11, color=color_sp)
    ax2.tick_params(axis='y', labelcolor=color_mae)
    ax2b.tick_params(axis='y', labelcolor=color_sp)
    ax2b.set_ylim(-0.1, 1.1)

    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2b.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='lower right', fontsize=10)
    ax2.set_xlabel('Iteration', fontsize=11)

    plt.xticks(rotation=30 if len(labels) > 8 else 0)
    plt.tight_layout()
    plt.savefig(out_file, dpi=150)
    print(f"Chart saved to {out_file}")


if __name__ == '__main__':
    main()
