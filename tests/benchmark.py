import time
import tracemalloc

RUNS = 5


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


def run_benchmarks(algorithms, data_by_size):
    for n, data in data_by_size.items():
        for name, fn in algorithms:
            total_time = sum(time_one(fn, data) for _ in range(RUNS))
            peak_mem = memory_one(fn, data)
            print(f"{name} n={n} time={total_time / RUNS:.6f}s memory={peak_mem / 1024:.1f}KB")
