"""
Benchmark Chart Generator
Produces 7 PNGs: 2 headline + 3 time + 2 memory.
Reads from the two CSV files in the same folder as this script.
"""

import csv, os, statistics
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))

def load_csv(filename):
    with open(os.path.join(BASE, filename), newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

all_rows = (
    load_csv('results-ubuntu-latest.csv') +
    load_csv('results-ubuntu-24.04-arm.csv')
)

# ── time + memory groups ───────────────────────────────────────────────────────
groups     = defaultdict(list)
mem_groups = defaultdict(list)
for r in all_rows:
    key = (r['arch'], r['algorithm'], int(r['n']), r['kind'])
    groups[key].append(float(r['seconds_mean']))
    mem_groups[(r['arch'], r['algorithm'], int(r['n']))].append(float(r['memory_kb']))

def avg(arch, algo, n, kind):
    vals = groups[(arch, algo, n, kind)]
    return statistics.mean(vals) if vals else 0

def avg_mem(arch, algo, n):
    vals = mem_groups[(arch, algo, n)]
    return statistics.mean(vals) if vals else 0

# ── constants ──────────────────────────────────────────────────────────────────
NS    = [1000, 5000, 10000, 20000, 40000]
ALGOS = ['bubble_sort', 'merge_sort', 'quick_sort']

ALL_KINDS   = ['random', 'sorted', 'reverse', 'mostly_sorted']
KIND_LABELS = {
    'random':        'Random',
    'sorted':        'Sorted',
    'reverse':       'Reverse',
    'mostly_sorted': 'Mostly Sorted (90%)',
}
ALGO_LABELS  = {'bubble_sort': 'Bubble Sort', 'merge_sort': 'Merge Sort', 'quick_sort': 'Quick Sort'}
ALGO_COLORS  = {'bubble_sort': '#4472C4', 'merge_sort': '#2BAA8A', 'quick_sort': '#D95F00'}

X86_COLOR = '#4472C4'
ARM_COLOR = '#C0504D'
W = 0.35

# only render kinds that actually have data
KINDS = [k for k in ALL_KINDS
         if any(groups.get((arch, algo, n, k))
                for arch in ('x86_64', 'aarch64')
                for algo in ALGOS
                for n in NS)]

plt.rcParams.update({
    'font.family':       'DejaVu Sans',
    'axes.spines.top':   False,
    'axes.spines.right': False,
    'axes.grid':         True,
    'grid.color':        '#e0e0e0',
    'grid.linewidth':    0.8,
    'axes.labelsize':    12,
    'axes.titlesize':    13,
    'xtick.labelsize':   11,
    'ytick.labelsize':   11,
    'legend.fontsize':   10,
    'figure.facecolor':  'white',
    'axes.facecolor':    'white',
})

def save(fig, name):
    path = os.path.join(BASE, name)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved: {path}')

def fmt_time(v):
    if v == 0:   return '0'
    if v < 0.001: return f'{v*1000:.2f}ms'
    if v < 1:    return f'{v:.4f}s'
    return f'{v:.2f}s'

nk = len(KINDS)

# ─────────────────────────────────────────────────────────────────────────────
# Chart 1: Algorithm Comparison — all 3 on same axes, random input
# 1×2 subplots: x86_64 | aarch64
# The headline chart: shows O(n²) bubble explosion vs O(n log n) merge/quick
# ─────────────────────────────────────────────────────────────────────────────
print('--- Chart 1: Algorithm Comparison (random input) ---')
fig, axes = plt.subplots(1, 2, figsize=(18, 7))
fig.suptitle('Sorting Algorithm Comparison — Random Input',
             fontsize=18, fontweight='bold')

for col, (arch, arch_label) in enumerate([('x86_64', 'x86_64'), ('aarch64', 'aarch64')]):
    ax = axes[col]
    for algo in ALGOS:
        vals = [avg(arch, algo, n, 'random') for n in NS]
        ax.plot(NS, vals, color=ALGO_COLORS[algo], marker='o',
                linewidth=2.5, markersize=8, label=ALGO_LABELS[algo], zorder=3)
    ax.set_title(arch_label, fontweight='bold', fontsize=15)
    ax.set_xlabel('Input Size (n)')
    ax.set_ylabel('Time (s)')
    ax.set_xticks(NS)
    ax.set_xticklabels([f'{n//1000}k' for n in NS])
    ax.legend(frameon=True)

plt.tight_layout()
save(fig, 'algorithm_comparison.png')

# ─────────────────────────────────────────────────────────────────────────────
# Chart 2: Theoretical Complexity Fit
# Log-log plot: actual data + O(n²) and O(n log n) reference curves
# Slope on log-log: O(n²)→2, O(n log n)→~1. Connects theory to measured data.
# ─────────────────────────────────────────────────────────────────────────────
print('--- Chart 2: Theoretical Complexity Fit ---')
fig, axes = plt.subplots(1, 2, figsize=(18, 7))
fig.suptitle('Actual Performance vs Theoretical Complexity — Random Input (log-log)',
             fontsize=16, fontweight='bold')

ns_fine = np.linspace(NS[0], NS[-1], 300)

for col, arch in enumerate(['x86_64', 'aarch64']):
    ax = axes[col]

    # plot actual data
    for algo in ALGOS:
        vals = [avg(arch, algo, n, 'random') for n in NS]
        ax.loglog(NS, vals, color=ALGO_COLORS[algo], marker='o',
                  linewidth=2.5, markersize=8, label=f'{ALGO_LABELS[algo]} (actual)', zorder=3)

    # anchor theoretical curves to bubble_sort at n=1000 and merge_sort at n=1000
    bubble_base = avg(arch, 'bubble_sort', NS[0], 'random')
    merge_base  = avg(arch, 'merge_sort',  NS[0], 'random')

    if bubble_base > 0:
        c2 = bubble_base / (NS[0] ** 2)
        ax.loglog(ns_fine, c2 * ns_fine ** 2,
                  color=ALGO_COLORS['bubble_sort'], linewidth=1.5,
                  linestyle=':', label='O(n²) theoretical', zorder=2)

    if merge_base > 0:
        c_nlogn = merge_base / (NS[0] * np.log2(NS[0]))
        ax.loglog(ns_fine, c_nlogn * ns_fine * np.log2(ns_fine),
                  color=ALGO_COLORS['merge_sort'], linewidth=1.5,
                  linestyle=':', label='O(n log n) theoretical', zorder=2)

    ax.set_title(arch, fontweight='bold', fontsize=15)
    ax.set_xlabel('Input Size (n, log scale)')
    ax.set_ylabel('Time (s, log scale)')
    ax.set_xticks(NS)
    ax.set_xticklabels([f'{n//1000}k' for n in NS])
    ax.legend(frameon=True, fontsize=9)

plt.tight_layout()
save(fig, 'complexity_fit.png')

# ─────────────────────────────────────────────────────────────────────────────
# Chart 3: Scaling Overview — per algo per kind, both archs
# Rows = input kind, Cols = algorithm
# Each subplot: 2 lines (x86_64 solid, aarch64 dashed)
# ─────────────────────────────────────────────────────────────────────────────
print('--- Chart 1: Scaling Overview ---')
fig, axes = plt.subplots(nk, 3, figsize=(21, 6 * nk))
fig.suptitle('Sorting Algorithm Scaling — x86_64 vs aarch64',
             fontsize=20, fontweight='bold', y=1.01)
if nk == 1:
    axes = [axes]

for row, kind in enumerate(KINDS):
    for col, algo in enumerate(ALGOS):
        ax = axes[row][col]
        color = ALGO_COLORS[algo]
        x86_vals = [avg('x86_64',  algo, n, kind) for n in NS]
        arm_vals = [avg('aarch64', algo, n, kind) for n in NS]
        ax.plot(NS, x86_vals, color=color, marker='o', linewidth=2.5, markersize=8,
                linestyle='-', label='x86_64', zorder=3)
        ax.plot(NS, arm_vals, color=color, marker='s', linewidth=2.5, markersize=8,
                linestyle='--', label='aarch64', alpha=0.8, zorder=3)
        ax.set_title(f'{ALGO_LABELS[algo]}\n{KIND_LABELS[kind]}', fontweight='bold')
        ax.set_xlabel('Input Size (n)')
        ax.set_ylabel('Time (s)')
        ax.set_xticks(NS)
        ax.set_xticklabels([f'{n//1000}k' for n in NS])
        ax.legend(frameon=True, loc='upper left')

plt.tight_layout()
save(fig, 'scaling_overview.png')

# ─────────────────────────────────────────────────────────────────────────────
# Chart 2: Architecture Comparison at n=40,000
# 1×nk subplots (one per kind), grouped bars, log y-axis
# ─────────────────────────────────────────────────────────────────────────────
print('--- Chart 2: Architecture Comparison at n=40,000 ---')
fig, axes = plt.subplots(1, nk, figsize=(7 * nk, 7))
fig.suptitle('x86_64 vs aarch64 at n=40,000 (log scale)',
             fontsize=16, fontweight='bold')
if nk == 1:
    axes = [axes]

x = np.arange(len(ALGOS))

for col, kind in enumerate(KINDS):
    ax = axes[col]
    x86_vals = [avg('x86_64',  algo, 40000, kind) for algo in ALGOS]
    arm_vals = [avg('aarch64', algo, 40000, kind) for algo in ALGOS]
    bars1 = ax.bar(x - W/2, x86_vals, W, color=X86_COLOR, label='x86_64',  zorder=3)
    bars2 = ax.bar(x + W/2, arm_vals,  W, color=ARM_COLOR, label='aarch64', zorder=3)
    ax.set_yscale('log')
    ax.set_title(KIND_LABELS[kind], fontweight='bold', fontsize=14)
    ax.set_xlabel('Algorithm')
    ax.set_ylabel('Time (s, log scale)')
    ax.set_xticks(x)
    ax.set_xticklabels([ALGO_LABELS[a] for a in ALGOS])
    ax.legend(frameon=True)
    for bar in list(bars1) + list(bars2):
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h * 1.4,
                    fmt_time(h), ha='center', va='bottom', fontsize=9, rotation=45)

plt.tight_layout()
save(fig, 'arch_comparison.png')

# ─────────────────────────────────────────────────────────────────────────────
# Chart 3: Input Type Sensitivity at n=40,000
# 1×3 subplots (one per algorithm), grouped bars by kind
# ─────────────────────────────────────────────────────────────────────────────
print('--- Chart 3: Input Type Sensitivity at n=40,000 ---')
fig, axes = plt.subplots(1, 3, figsize=(7 * 3, 7))
fig.suptitle('Input Type Sensitivity at n=40,000 — x86_64 vs aarch64',
             fontsize=16, fontweight='bold')

x = np.arange(nk)

for col, algo in enumerate(ALGOS):
    ax = axes[col]
    x86_vals = [avg('x86_64',  algo, 40000, kind) for kind in KINDS]
    arm_vals = [avg('aarch64', algo, 40000, kind) for kind in KINDS]
    bars1 = ax.bar(x - W/2, x86_vals, W, color=X86_COLOR, label='x86_64',  zorder=3)
    bars2 = ax.bar(x + W/2, arm_vals,  W, color=ARM_COLOR, label='aarch64', zorder=3)

    all_vals = [v for v in x86_vals + arm_vals if v > 0]
    if all_vals and max(all_vals) / min(all_vals) > 100:
        ax.set_yscale('log')
        ax.set_ylabel('Time (s, log scale)')
    else:
        ax.set_ylabel('Time (s)')

    ax.set_title(ALGO_LABELS[algo], fontweight='bold', fontsize=14)
    ax.set_xlabel('Input Type')
    ax.set_xticks(x)
    ax.set_xticklabels([KIND_LABELS[k] for k in KINDS], rotation=15, ha='right')
    ax.legend(frameon=True)
    for bar in list(bars1) + list(bars2):
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    h * (1.4 if ax.get_yscale() == 'log' else 1.02),
                    fmt_time(h), ha='center', va='bottom', fontsize=9, rotation=45)

plt.tight_layout()
save(fig, 'input_sensitivity.png')

# ─────────────────────────────────────────────────────────────────────────────
# Chart 4: Memory Scaling
# Single plot: memory vs n for all algos × archs (log scale)
# Annotated with space complexity class
# ─────────────────────────────────────────────────────────────────────────────
print('--- Chart 4: Memory Scaling ---')
fig, ax = plt.subplots(figsize=(12, 7))

for algo in ALGOS:
    color = ALGO_COLORS[algo]
    x86_vals = [avg_mem('x86_64',  algo, n) for n in NS]
    arm_vals = [avg_mem('aarch64', algo, n) for n in NS]
    ax.plot(NS, x86_vals, color=color, marker='o', linewidth=2.5, markersize=8,
            linestyle='-', label=f'{ALGO_LABELS[algo]} (x86_64)', zorder=3)
    ax.plot(NS, arm_vals, color=color, marker='s', linewidth=2.5, markersize=8,
            linestyle='--', label=f'{ALGO_LABELS[algo]} (aarch64)', alpha=0.8, zorder=3)

ax.set_yscale('log')
ax.set_title('Memory Usage Scaling — x86_64 vs aarch64', fontweight='bold', fontsize=16)
ax.set_xlabel('Input Size (n)')
ax.set_ylabel('Memory (KB, log scale)')
ax.set_xticks(NS)
ax.set_xticklabels([f'{n//1000}k' for n in NS])
ax.legend(frameon=True, ncol=2)

ax.annotate('O(n) — Merge Sort',   xy=(40000, avg_mem('x86_64', 'merge_sort',  40000)),
            xytext=(-80,  10), textcoords='offset points', fontsize=10,
            color=ALGO_COLORS['merge_sort'],  fontweight='bold')
ax.annotate('O(log n) — Quick Sort', xy=(40000, avg_mem('x86_64', 'quick_sort', 40000)),
            xytext=(-120, 10), textcoords='offset points', fontsize=10,
            color=ALGO_COLORS['quick_sort'], fontweight='bold')
ax.annotate('O(1) — Bubble Sort',  xy=(40000, avg_mem('x86_64', 'bubble_sort', 40000)),
            xytext=(-110,-20), textcoords='offset points', fontsize=10,
            color=ALGO_COLORS['bubble_sort'], fontweight='bold')

plt.tight_layout()
save(fig, 'memory_scaling.png')

# ─────────────────────────────────────────────────────────────────────────────
# Chart 5: Time vs Memory Tradeoff at n=40,000
# Log-log scatter: x=memory_kb, y=seconds (random input)
# ─────────────────────────────────────────────────────────────────────────────
print('--- Chart 5: Memory vs Time Tradeoff at n=40,000 ---')
fig, ax = plt.subplots(figsize=(12, 7))

markers = {'x86_64': 'o', 'aarch64': 's'}
for arch in ['x86_64', 'aarch64']:
    for algo in ALGOS:
        mem  = avg_mem(arch, algo, 40000)
        time = avg(arch, algo, 40000, 'random')
        color = ALGO_COLORS[algo]
        ax.scatter(mem, time, color=color, marker=markers[arch],
                   s=180, zorder=4, edgecolors='white', linewidths=1.5,
                   label=f'{ALGO_LABELS[algo]} ({arch})')
        ax.annotate(f'{ALGO_LABELS[algo]}\n({arch})',
                    xy=(mem, time), xytext=(8, 4), textcoords='offset points',
                    fontsize=9, color=color)

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_title('Time vs Memory Tradeoff at n=40,000 — Random Input\n(lower-left = better)',
             fontweight='bold', fontsize=15)
ax.set_xlabel('Memory Usage (KB, log scale)')
ax.set_ylabel('Time (s, log scale)')
ax.legend(frameon=True, ncol=2, fontsize=9)

plt.tight_layout()
save(fig, 'memory_vs_time_tradeoff.png')

print('\nDone! 7 PNGs saved.')
