"""
Run valgrind cachegrind + branch simulation for all algo × kind combinations.
Compiles sort_runner.c and uses it as the valgrind target (avoids Python's
billions of interpreter instructions which block cache simulation).
Merges d1_miss_rate, lld_miss_rate, branch_miss_rate into existing results CSV
(only for n=10000 rows).

Usage: python tests/run_valgrind.py --output data/results-<runner>.csv
"""
import csv, os, platform, re, subprocess, sys

ARCH      = platform.machine()
N         = 10000
ALGOS     = ['bubble_sort', 'merge_sort', 'quick_sort']
KINDS     = ['random', 'sorted', 'reverse', 'mostly_sorted']
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
C_SRC     = os.path.join(TESTS_DIR, 'sort_runner.c')
C_BIN     = '/tmp/sort_runner'

FIELDNAMES = ['algorithm', 'n', 'kind', 'seconds_mean', 'memory_kb', 'arch',
              'd1_miss_rate', 'lld_miss_rate', 'branch_miss_rate']


def compile_c():
    result = subprocess.run(
        ['gcc', '-O2', '-o', C_BIN, C_SRC],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print('Compile error:', result.stderr)
        sys.exit(1)
    print(f'Compiled {C_SRC} -> {C_BIN}', flush=True)


def run_one(algo, kind, debug=False):
    tmp = f'/tmp/cg_{algo}_{kind}.out'
    cmd = [
        'valgrind', '--tool=cachegrind', '--cache-sim=yes', '--branch-sim=yes',
        f'--cachegrind-out-file={tmp}',
        C_BIN, algo, str(N), kind,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    try:
        os.remove(tmp)
    except FileNotFoundError:
        pass
    if debug:
        print('=== valgrind stderr (first run) ===')
        print(result.stderr[-3000:])
        print('=== end ===', flush=True)
    return parse(result.stderr)


def parse(text):
    def pct(pattern):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).replace(',', '') if m else ''
    return {
        'd1_miss_rate':     pct(r'D1\s+miss rate:\s+([\d.,]+)%'),
        'lld_miss_rate':    pct(r'LLd\s+miss rate:\s+([\d.,]+)%'),
        'branch_miss_rate': pct(r'Mispred rate:\s+([\d.,]+)%'),
    }


def main():
    output = 'data/results.csv'
    for arg in sys.argv[1:]:
        if arg.startswith('--output'):
            output = arg.split('=')[1] if '=' in arg else sys.argv[sys.argv.index(arg) + 1]

    compile_c()

    with open(output, newline='') as f:
        rows = list(csv.DictReader(f))

    vg = {}
    first = True
    for algo in ALGOS:
        for kind in KINDS:
            print(f'Running valgrind: {algo} n={N} kind={kind} ...', flush=True)
            metrics = run_one(algo, kind, debug=first)
            first = False
            vg[(algo, kind)] = metrics
            print(f"  d1={metrics['d1_miss_rate']}% lld={metrics['lld_miss_rate']}% branch={metrics['branch_miss_rate']}%")

    for row in rows:
        if int(row['n']) == N:
            key = (row['algorithm'], row['kind'])
            if key in vg:
                row.update(vg[key])

    for row in rows:
        for col in ('d1_miss_rate', 'lld_miss_rate', 'branch_miss_rate'):
            row.setdefault(col, '')

    with open(output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)

    print(f'\nMerged valgrind data into: {output}')


if __name__ == '__main__':
    main()
