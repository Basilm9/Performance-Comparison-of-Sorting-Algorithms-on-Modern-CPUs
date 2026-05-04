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

# color per input kind, style/marker per arch
KIND_COLORS = {
    'random':        '#4472C4',
    'sorted':        '#2BAA8A',
    'reverse':       '#D95F00',
    'mostly_sorted': '#9B59B6',
}
ARCH_STYLE  = {'x86_64': '-',  'aarch64': '--'}
ARCH_MARKER = {'x86_64': 'o',  'aarch64': 's'}

def plot_algo_timing(ax, algo, title):
    """2 lines per chart — average across all input kinds, one line per arch."""
    for arch, color in [('x86_64', X86_COLOR), ('aarch64', ARM_COLOR)]:
        vals = [statistics.mean(avg(arch, algo, n, k) for k in KINDS if avg(arch, algo, n, k) > 0)
                for n in NS]
        ax.plot(NS, vals,
                color=color,
                marker=ARCH_MARKER[arch],
                linewidth=2.5, markersize=8,
                linestyle=ARCH_STYLE[arch],
                label=arch, zorder=3)
    ax.set_title(title, fontweight='bold', fontsize=15)
    ax.set_xlabel('Input Size (n)')
    ax.set_ylabel('Time (s)')
    ax.set_xticks(NS)
    ax.set_xticklabels([f'{n//1000}k' for n in NS])
    ax.legend(frameon=True, fontsize=11)

# ─────────────────────────────────────────────────────────────────────────────
# Chart 1: Bubble Sort — all input kinds × both architectures
# ─────────────────────────────────────────────────────────────────────────────
print('--- Chart 1: Bubble Sort Timing ---')
fig, ax = plt.subplots(figsize=(14, 8))
fig.suptitle('Bubble Sort — All Input Types · x86_64 vs aarch64',
             fontsize=16, fontweight='bold')
plot_algo_timing(ax, 'bubble_sort', 'Bubble Sort')
plt.tight_layout()
save(fig, 'time_bubble.png')

# ─────────────────────────────────────────────────────────────────────────────
# Chart 2: Merge Sort — all input kinds × both architectures
# ─────────────────────────────────────────────────────────────────────────────
print('--- Chart 2: Merge Sort Timing ---')
fig, ax = plt.subplots(figsize=(14, 8))
fig.suptitle('Merge Sort — All Input Types · x86_64 vs aarch64',
             fontsize=16, fontweight='bold')
plot_algo_timing(ax, 'merge_sort', 'Merge Sort')
plt.tight_layout()
save(fig, 'time_merge.png')

# ─────────────────────────────────────────────────────────────────────────────
# Chart 3: Quick Sort — all input kinds × both architectures
# ─────────────────────────────────────────────────────────────────────────────
print('--- Chart 3: Quick Sort Timing ---')
fig, ax = plt.subplots(figsize=(14, 8))
fig.suptitle('Quick Sort — All Input Types · x86_64 vs aarch64',
             fontsize=16, fontweight='bold')
plot_algo_timing(ax, 'quick_sort', 'Quick Sort')
plt.tight_layout()
save(fig, 'time_quick.png')

# ─────────────────────────────────────────────────────────────────────────────
# Chart 4: All algorithms — 6 lines (algo×arch) + 2 combined avg lines
# Averaged across all input kinds
# ─────────────────────────────────────────────────────────────────────────────
print('--- Chart 4: All Algorithms Comparison ---')
fig, ax = plt.subplots(figsize=(14, 8))
fig.suptitle('All Algorithms — x86_64 vs aarch64 (averaged across all input kinds)',
             fontsize=15, fontweight='bold')

ARCH_STYLE2  = {'x86_64': '-',  'aarch64': '--'}
ARCH_MARKER2 = {'x86_64': 'o',  'aarch64': 's'}

for algo in ALGOS:
    for arch in ['x86_64', 'aarch64']:
        vals = [statistics.mean(avg(arch, algo, n, k) for k in KINDS if avg(arch, algo, n, k) > 0)
                for n in NS]
        ax.plot(NS, vals,
                color=ALGO_COLORS[algo],
                linestyle=ARCH_STYLE2[arch],
                marker=ARCH_MARKER2[arch],
                linewidth=2, markersize=7,
                label=f'{ALGO_LABELS[algo]} ({arch})', zorder=3)

# 2 combined lines — average of all 3 algorithms per arch
for arch, color in [('x86_64', '#333333'), ('aarch64', '#888888')]:
    combined = []
    for n in NS:
        algo_avgs = [statistics.mean(avg(arch, algo, n, k) for k in KINDS if avg(arch, algo, n, k) > 0)
                     for algo in ALGOS]
        combined.append(statistics.mean(algo_avgs))
    ax.plot(NS, combined,
            color=color, linestyle=ARCH_STYLE2[arch],
            marker=ARCH_MARKER2[arch],
            linewidth=3, markersize=9,
            label=f'Combined avg ({arch})', zorder=4)

ax.set_yscale('log')
ax.set_xlabel('Input Size (n)')
ax.set_ylabel('Time (s, log scale)')
ax.set_xticks(NS)
ax.set_xticklabels([f'{n//1000}k' for n in NS])
ax.legend(frameon=True, fontsize=9, ncol=2)
plt.tight_layout()
save(fig, 'time_all_algorithms.png')

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

# ─────────────────────────────────────────────────────────────────────────────
# Charts 7–9: One chart per valgrind metric (when data present)
# Chart 7: L1 Data Cache Miss Rate (d1_miss_rate)
# Chart 8: L3 Last-Level Cache Miss Rate (lld_miss_rate)
# Chart 9: Branch Misprediction Rate (branch_miss_rate)
# Each chart: 4 subplots (one per input kind), grouped bars per algorithm × arch
# ─────────────────────────────────────────────────────────────────────────────
VG_METRICS = [
    ('d1_miss_rate',     'L1 Data Cache Miss Rate (%)',     'd1_miss_rates.png'),
    ('lld_miss_rate',    'L3 Last-Level Cache Miss Rate (%)', 'lld_miss_rates.png'),
    ('branch_miss_rate', 'Branch Misprediction Rate (%)',   'branch_miss_rates.png'),
]

vg_rows = [r for r in all_rows if any(r.get(m, '') != '' for m, _, _ in VG_METRICS)]

if vg_rows:
    vg_groups = defaultdict(list)
    for r in vg_rows:
        for metric, _, _ in VG_METRICS:
            val = r.get(metric, '')
            if val:
                try:
                    vg_groups[(r['arch'], r['algorithm'], r['kind'], metric)].append(float(val))
                except ValueError:
                    pass

    def avg_vg(arch, algo, kind, metric):
        vals = vg_groups[(arch, algo, kind, metric)]
        return statistics.mean(vals) if vals else 0

    vg_kinds = [k for k in KINDS
                if any(vg_groups.get((arch, algo, k, metric))
                       for arch in ('x86_64', 'aarch64')
                       for algo in ALGOS
                       for metric, _, _ in VG_METRICS)]

    if vg_kinds:
        x     = np.arange(len(ALGOS))
        extra = 0

        def avg_vg_all(arch, algo, metric):
            vals = [avg_vg(arch, algo, k, metric) for k in vg_kinds if avg_vg(arch, algo, k, metric) > 0]
            return statistics.mean(vals) if vals else 0

        for metric, ylabel, filename in VG_METRICS:
            if not any(vg_groups.get((arch, algo, k, metric))
                       for arch in ('x86_64', 'aarch64')
                       for algo in ALGOS for k in vg_kinds):
                continue

            print(f'--- Chart: {ylabel} ---')
            fig, ax = plt.subplots(figsize=(10, 7))
            fig.suptitle(f'{ylabel} — valgrind cachegrind (averaged across input kinds)',
                         fontsize=14, fontweight='bold')

            x86_vals = [avg_vg_all('x86_64',  algo, metric) for algo in ALGOS]
            arm_vals = [avg_vg_all('aarch64', algo, metric) for algo in ALGOS]
            bars1 = ax.bar(x - W/2, x86_vals, W, color=X86_COLOR, label='x86_64',  zorder=3)
            bars2 = ax.bar(x + W/2, arm_vals,  W, color=ARM_COLOR, label='aarch64', zorder=3)
            ax.set_xlabel('Algorithm')
            ax.set_ylabel(ylabel)
            ax.set_xticks(x)
            ax.set_xticklabels([ALGO_LABELS[a] for a in ALGOS])
            ax.legend(frameon=True)
            for bar in list(bars1) + list(bars2):
                h = bar.get_height()
                if h > 0:
                    ax.text(bar.get_x() + bar.get_width() / 2, h * 1.02,
                            f'{h:.2f}%', ha='center', va='bottom', fontsize=9)

            plt.tight_layout()
            save(fig, filename)
            extra += 1
    else:
        extra = 0
else:
    extra = 0

print(f'\nDone! {6 + (extra if vg_rows else 0)} PNGs saved.')
