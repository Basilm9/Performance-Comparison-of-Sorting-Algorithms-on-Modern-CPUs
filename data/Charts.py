"""
Benchmark Chart Generator
One PNG per chart — large and readable.
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

groups = defaultdict(list)
for r in all_rows:
    groups[(r['arch'], r['algorithm'], int(r['n']), r['kind'])].append(float(r['seconds_mean']))

def avg(arch, algo, n, kind):
    vals = groups[(arch, algo, n, kind)]
    return statistics.mean(vals) if vals else 0

NS    = [1000, 5000, 10000, 20000, 40000]
KINDS = ['random', 'sorted', 'reverse']
KIND_TITLES = {'random': 'Random Input', 'sorted': 'Sorted Input', 'reverse': 'Reverse Input'}

BLUE   = '#4472C4'
RED    = '#C0504D'
TEAL   = '#2BAA8A'
ORANGE = '#D95F00'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.color': '#e0e0e0',
    'grid.linewidth': 0.8,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 13,
    'ytick.labelsize': 13,
    'legend.fontsize': 12,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
})

def save(fig, name):
    path = os.path.join(BASE, name)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved: {path}')

# ── Scaling: Bubble Sort — one PNG per kind ────────────────────────────────────
print('--- Scaling: Bubble Sort ---')
for kind in KINDS:
    fig, ax = plt.subplots(figsize=(10, 6))
    x86_vals = [avg('x86_64',  'bubble_sort', n, kind) for n in NS]
    arm_vals = [avg('aarch64', 'bubble_sort', n, kind) for n in NS]
    ax.plot(NS, x86_vals, color=BLUE, marker='o', linewidth=2.5, markersize=8, linestyle='-',  label='Bubble Sort (x86_64)')
    ax.plot(NS, arm_vals, color=BLUE, marker='s', linewidth=2.5, markersize=8, linestyle='--', label='Bubble Sort (aarch64)')
    ax.set_title(f'Bubble Sort Scaling — {KIND_TITLES[kind]}', fontweight='bold')
    ax.set_xlabel('Input Size (n)')
    ax.set_ylabel('Time (seconds)')
    ax.set_xticks(NS)
    ax.set_xticklabels([f'{n:,}' for n in NS])
    ax.legend(frameon=True)
    save(fig, f'scaling_bubble_{kind}.png')

# ── Scaling: Merge & Quick — one PNG per kind ─────────────────────────────────
print('--- Scaling: Merge & Quick Sort ---')
for kind in KINDS:
    fig, ax = plt.subplots(figsize=(10, 6))
    for algo, color, label_base in [
        ('merge_sort', TEAL,   'Merge Sort'),
        ('quick_sort', ORANGE, 'Quick Sort'),
    ]:
        x86_vals = [avg('x86_64',  algo, n, kind) for n in NS]
        arm_vals = [avg('aarch64', algo, n, kind) for n in NS]
        ax.plot(NS, x86_vals, color=color, marker='o', linewidth=2.5, markersize=8, linestyle='-',  label=f'{label_base} (x86_64)')
        ax.plot(NS, arm_vals, color=color, marker='s', linewidth=2.5, markersize=8, linestyle='--', label=f'{label_base} (aarch64)')
    ax.set_title(f'Merge & Quick Sort Scaling — {KIND_TITLES[kind]}', fontweight='bold')
    ax.set_xlabel('Input Size (n)')
    ax.set_ylabel('Time (seconds)')
    ax.set_xticks(NS)
    ax.set_xticklabels([f'{n:,}' for n in NS])
    ax.legend(frameon=True)
    save(fig, f'scaling_merge_quick_{kind}.png')

# ── Arch Compare: Bubble Sort — one PNG per n + kind ──────────────────────────
print('--- Arch Compare: Bubble Sort ---')
for n in NS:
    for kind in KINDS:
        fig, ax = plt.subplots(figsize=(7, 6))
        x86_val = avg('x86_64',  'bubble_sort', n, kind)
        arm_val = avg('aarch64', 'bubble_sort', n, kind)
        ax.bar([0], [x86_val], 0.4, color=BLUE, label='x86_64')
        ax.bar([0.45], [arm_val], 0.4, color=RED, label='aarch64')
        ax.set_xticks([0.225])
        ax.set_xticklabels(['Bubble Sort'])
        ax.set_xlabel('Algorithm')
        ax.set_ylabel('Time (seconds)')
        ax.set_title(f'Bubble Sort — n={n:,} — {kind}', fontweight='bold')
        ax.legend(frameon=True)
        ax.ticklabel_format(style='sci', axis='y', scilimits=(-3, 3))
        save(fig, f'archcompare_bubble_n{n}_{kind}.png')

# ── Arch Compare: Merge & Quick — one PNG per n + kind ────────────────────────
print('--- Arch Compare: Merge & Quick Sort ---')
x = np.array([0, 1])
W = 0.35
for n in NS:
    for kind in KINDS:
        fig, ax = plt.subplots(figsize=(9, 6))
        merge_x86 = avg('x86_64',  'merge_sort', n, kind)
        merge_arm = avg('aarch64', 'merge_sort', n, kind)
        quick_x86 = avg('x86_64',  'quick_sort', n, kind)
        quick_arm = avg('aarch64', 'quick_sort', n, kind)
        ax.bar(x - W/2, [merge_x86, quick_x86], W, color=BLUE, label='x86_64')
        ax.bar(x + W/2, [merge_arm, quick_arm],  W, color=RED,  label='aarch64')
        ax.set_xticks(x)
        ax.set_xticklabels(['Merge Sort', 'Quick Sort'])
        ax.set_xlabel('Algorithm')
        ax.set_ylabel('Time (seconds)')
        ax.set_title(f'Merge & Quick Sort — n={n:,} — {kind}', fontweight='bold')
        ax.legend(frameon=True)
        ax.ticklabel_format(style='sci', axis='y', scilimits=(-3, 3))
        save(fig, f'archcompare_merge_quick_n{n}_{kind}.png')

print('\nDone! All PNGs saved to your project folder.')