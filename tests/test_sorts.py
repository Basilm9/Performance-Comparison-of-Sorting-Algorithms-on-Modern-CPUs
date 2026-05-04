import copy
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sorting.algorithms import bubble_sort, merge_sort, quick_sort
from benchmark import run_benchmarks

INPUT_SIZES = [1_000, 5_000, 10_000, 20_000, 40_000]

ALGORITHMS = [
    ("bubble_sort", bubble_sort),
    ("merge_sort", merge_sort),
    ("quick_sort", quick_sort),
]


def generate_input(n, kind):
    data = random.sample(range(n * 10), n)
    if kind == "random":
        return data
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


KINDS = ["random", "sorted", "reverse", "mostly_sorted"]

DATASETS = {kind: {n: generate_input(n, kind) for n in INPUT_SIZES} for kind in KINDS}


def _assert_sorted(fn, datasets, label):
    for n, data in datasets.items():
        a = copy.copy(data)
        fn(a)
        assert a == sorted(data), f"{fn.__name__} failed on {label} n={n}"


def test_bubble_sort():
    for kind, data in DATASETS.items():
        _assert_sorted(bubble_sort, data, kind)


def test_merge_sort():
    for kind, data in DATASETS.items():
        _assert_sorted(merge_sort, data, kind)


def test_quick_sort():
    for kind, data in DATASETS.items():
        _assert_sorted(quick_sort, data, kind)


if __name__ == "__main__":
    output = "data/results.csv"
    for arg in sys.argv[1:]:
        if arg.startswith("--output"):
            output = arg.split("=")[1] if "=" in arg else sys.argv[sys.argv.index(arg) + 1]

    test_bubble_sort()
    test_merge_sort()
    test_quick_sort()
    print("All tests passed.\n")
    for kind, data in DATASETS.items():
        print(f"--- {kind} ---")
        run_benchmarks(ALGORITHMS, data, kind=kind, output_file=output)
