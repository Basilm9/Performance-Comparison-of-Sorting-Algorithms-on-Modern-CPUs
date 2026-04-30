"""
Run valgrind cachegrind + branch simulation for all algo × kind combinations.
Merges d1_miss_rate, lld_miss_rate, branch_miss_rate into existing results CSV
(only for n=10000 rows — valgrind is run at that size only).

Usage: python tests/run_valgrind.py --output data/results-<runner>.csv
"""
import csv, os, platform, re, subprocess, sys

ARCH   = platform.machine()
N      = 10000
ALGOS  = ['bubble_sort', 'merge_sort', 'quick_sort']
KINDS  = ['random', 'sorted', 'reverse', 'mostly_sorted']
RUNNER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'perf_runner.py')

FIELDNAMES = ['algorithm', 'n', 'kind', 'seconds_mean', 'memory_kb', 'arch',
              'd1_miss_rate', 'lld_miss_rate', 'branch_miss_rate']


def run_one(algo, kind, debug=False):
    cmd = [
        'valgrind', '--tool=cachegrind', '--cache-sim=yes', '--branch-sim=yes',
        '--cachegrind-out-file=/dev/null',
        sys.executable, RUNNER, algo, str(N), kind,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
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

    # load existing CSV
    with open(output, newline='') as f:
        rows = list(csv.DictReader(f))

    # build lookup: (algorithm, kind) -> valgrind metrics
    vg = {}
    first = True
    for algo in ALGOS:
        for kind in KINDS:
            print(f'Running valgrind: {algo} n={N} kind={kind} ...', flush=True)
            metrics = run_one(algo, kind, debug=first)
            first = False
            vg[(algo, kind)] = metrics
            print(f"  d1={metrics['d1_miss_rate']}% lld={metrics['lld_miss_rate']}% branch={metrics['branch_miss_rate']}%")

    # patch n=10000 rows with valgrind data
    for row in rows:
        if int(row['n']) == N:
            key = (row['algorithm'], row['kind'])
            if key in vg:
                row.update(vg[key])

    # write back — ensure all fieldnames present
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
