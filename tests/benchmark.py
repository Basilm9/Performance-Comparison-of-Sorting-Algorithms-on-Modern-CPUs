import csv
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import tracemalloc

RUNS = 3
PERF_RUNS = 2  # fewer runs for perf — subprocess overhead is high

ARCH = platform.machine()

_PERF_EVENTS = (
    'branch-misses,branch-instructions,'
    'cache-misses,cache-references,'
    'stalled-cycles-frontend,stalled-cycles-backend,'
    'instructions,cycles'
)
_PERF_RUNNER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'perf_runner.py')
PERF_AVAILABLE = sys.platform == 'linux' and bool(shutil.which('perf'))


def time_one(fn, data):
    work = data.copy()
    t0 = time.perf_counter()
    fn(work)
    return time.perf_counter() - t0


def memory_one(fn, data):
    work = data.copy()
    tracemalloc.start()
    fn(work)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


def _parse_perf(text):
    out = {}
    for key, pat in [
        ('branch_misses',           r'([\d,]+)\s+branch-misses'),
        ('branch_instructions',     r'([\d,]+)\s+branch-instructions'),
        ('cache_misses',            r'([\d,]+)\s+cache-misses'),
        ('cache_references',        r'([\d,]+)\s+cache-references'),
        ('stalled_cycles_frontend', r'([\d,]+)\s+stalled-cycles-frontend'),
        ('stalled_cycles_backend',  r'([\d,]+)\s+stalled-cycles-backend'),
        ('instructions',            r'([\d,]+)\s+instructions'),
        ('cycles',                  r'([\d,]+)\s+cycles'),
    ]:
        m = re.search(pat, text)
        out[key] = int(m.group(1).replace(',', '')) if m else ''
    return out


def perf_one(algo_name, n, kind):
    empty = {
        'branch_misses': '', 'branch_instructions': '',
        'cache_misses': '', 'cache_references': '',
        'stalled_cycles_frontend': '', 'stalled_cycles_backend': '',
        'instructions': '', 'cycles': '',
    }
    if not PERF_AVAILABLE:
        return empty
    cmd = [
        'perf', 'stat', '-e', _PERF_EVENTS,
        sys.executable, _PERF_RUNNER, algo_name, str(n), kind, str(PERF_RUNS),
    ]
    env = {**os.environ, 'LC_ALL': 'C'}
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=env)
        return _parse_perf(result.stderr)
    except Exception:
        return empty


def run_benchmarks(algorithms, data_by_size, kind="random", output_file="data/results.csv"):
    rows = []
    for n, data in data_by_size.items():
        for name, fn in algorithms:
            total_time = sum(time_one(fn, data) for _ in range(RUNS))
            peak_mem = memory_one(fn, data)
            mean_time = total_time / RUNS
            perf = perf_one(name, n, kind)
            rows.append([
                name, n, kind,
                f"{mean_time:.6f}", f"{peak_mem / 1024:.1f}", ARCH,
                perf['branch_misses'],           perf['branch_instructions'],
                perf['cache_misses'],            perf['cache_references'],
                perf['stalled_cycles_frontend'], perf['stalled_cycles_backend'],
                perf['instructions'],            perf['cycles'],
            ])
            print(
                f"{name} n={n} kind={kind} time={mean_time:.6f}s "
                f"memory={peak_mem / 1024:.1f}KB arch={ARCH} "
                f"branch_misses={perf['branch_misses']} "
                f"cache_misses={perf['cache_misses']} "
                f"stalled_frontend={perf['stalled_cycles_frontend']} "
                f"stalled_backend={perf['stalled_cycles_backend']}"
            )

    write_header = True
    try:
        with open(output_file, "r") as f:
            write_header = f.read(1) == ""
    except FileNotFoundError:
        pass

    with open(output_file, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                "algorithm", "n", "kind", "seconds_mean", "memory_kb", "arch",
                "branch_misses", "branch_instructions",
                "cache_misses", "cache_references",
                "stalled_cycles_frontend", "stalled_cycles_backend",
                "instructions", "cycles",
            ])
        writer.writerows(rows)
