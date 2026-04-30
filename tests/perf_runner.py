"""
Minimal driver for `perf stat` — runs one sorting algorithm N times.
perf stat wraps this process and captures hardware counters.

Usage: python perf_runner.py <algo> <n> <kind> [runs]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sorting.sorts import bubble_sort, merge_sort, quick_sort

_ALGOS = {
    'bubble_sort': bubble_sort,
    'merge_sort':  merge_sort,
    'quick_sort':  quick_sort,
}


def _gen(n, kind):
    data = random.sample(range(n * 10), n)
    if kind == "sorted":
        return sorted(data)
    if kind == "reverse":
        return sorted(data, reverse=True)
    if kind == "mostly_sorted":
        data = sorted(data)
        indices = random.sample(range(n - 1), max(1, n // 10))
        for i in indices:
            data[i], data[i + 1] = data[i + 1], data[i]
        return data
    return data


if __name__ == "__main__":
    algo_name = sys.argv[1]
    n         = int(sys.argv[2])
    kind      = sys.argv[3]
    runs      = int(sys.argv[4]) if len(sys.argv) > 4 else 3

    fn = _ALGOS[algo_name]
    for _ in range(runs):
        fn(_gen(n, kind))
