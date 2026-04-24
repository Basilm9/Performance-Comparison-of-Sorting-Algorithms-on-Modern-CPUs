"""
Timing harness: random integers, sizes from the proposal, averaged runs using time.perf_counter.

Run from repository root:
    python -m sorting.benchmark              # full sizes (Bubble Sort on large n is very slow)
    python -m sorting.benchmark --quick    # small n for a fast smoke test
"""

from __future__ import annotations

import argparse
import csv
import random
import sys
import time
from collections.abc import Callable, MutableSequence

from .sorts import bubble_sort, merge_sort, quick_sort

FULL_SIZES = [1_000, 5_000, 10_000, 50_000, 100_000]
QUICK_SIZES = [500, 1_000, 2_000]
RUNS_FULL = 5
RUNS_QUICK = 3
SEED = 42

Sorter = Callable[[MutableSequence[int]], None]


def _time_one(sorter: Sorter, data: list[int]) -> float:
    work = data.copy()
    t0 = time.perf_counter()
    sorter(work)
    return time.perf_counter() - t0


def run_table(
    stream=sys.stdout,
    *,
    sizes: list[int] | None = None,
    runs_per_size: int = RUNS_FULL,
    log: Callable[[str], None] | None = None,
) -> None:
    sizes = sizes if sizes is not None else list(FULL_SIZES)
    log = log or (lambda _msg: None)

    rng = random.Random(SEED)
    algorithms: list[tuple[str, Sorter]] = [
        ("bubble_sort", bubble_sort),
        ("merge_sort", merge_sort),
        ("quick_sort", quick_sort),
    ]

    writer = csv.writer(stream)
    writer.writerow(["algorithm", "n", "seconds_mean", "runs"])

    for n in sizes:
        log(f"benchmark: generating n={n} …")
        base = [rng.randint(-(2**31), 2**31 - 1) for _ in range(n)]
        for name, sorter in algorithms:
            log(f"benchmark: timing {name} n={n} ({runs_per_size} runs) …")
            total = 0.0
            for _ in range(runs_per_size):
                total += _time_one(sorter, base)
            mean = total / runs_per_size
            writer.writerow([name, n, f"{mean:.6f}", runs_per_size])


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Sort timing CSV (see module docstring).")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Use small n and fewer runs for a fast sanity check.",
    )
    args = parser.parse_args(argv)

    sizes = list(QUICK_SIZES) if args.quick else list(FULL_SIZES)
    runs = RUNS_QUICK if args.quick else RUNS_FULL
    run_table(sizes=sizes, runs_per_size=runs, log=lambda m: print(m, file=sys.stderr))


if __name__ == "__main__":
    main()
