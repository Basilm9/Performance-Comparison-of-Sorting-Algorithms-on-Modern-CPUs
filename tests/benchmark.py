import csv
import os
import platform
import time
import tracemalloc

RUNS = 3

ARCH = platform.machine()


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


def run_benchmarks(algorithms, data_by_size, kind="random", output_file="data/results.csv"):
    rows = []
    for n, data in data_by_size.items():
        for name, fn in algorithms:
            total_time = sum(time_one(fn, data) for _ in range(RUNS))
            peak_mem = memory_one(fn, data)
            mean_time = total_time / RUNS
            rows.append([name, n, kind, f"{mean_time:.6f}", f"{peak_mem / 1024:.1f}", ARCH])
            print(f"{name} n={n} kind={kind} time={mean_time:.6f}s memory={peak_mem / 1024:.1f}KB arch={ARCH}")

    write_header = True
    try:
        with open(output_file, "r") as f:
            write_header = f.read(1) == ""
    except FileNotFoundError:
        pass

    with open(output_file, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["algorithm", "n", "kind", "seconds_mean", "memory_kb", "arch"])
        writer.writerows(rows)
