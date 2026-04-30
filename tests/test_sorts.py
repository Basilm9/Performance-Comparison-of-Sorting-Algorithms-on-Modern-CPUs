import copy
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sorting.sorts import bubble_sort, merge_sort, quick_sort
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


RANDOM_DATA       = {n: generate_input(n, "random")       for n in INPUT_SIZES}
SORTED_DATA       = {n: generate_input(n, "sorted")       for n in INPUT_SIZES}
REVERSE_DATA      = {n: generate_input(n, "reverse")      for n in INPUT_SIZES}
MOSTLY_SORTED_DATA = {n: generate_input(n, "mostly_sorted") for n in INPUT_SIZES}


def _assert_sorted(fn, datasets, label):
    for n, data in datasets.items():
        a = copy.copy(data)
        fn(a)
        assert a == sorted(data), f"{fn.__name__} failed on {label} n={n}"


def test_bubble_sort():
    _assert_sorted(bubble_sort, RANDOM_DATA,        "random")
    _assert_sorted(bubble_sort, SORTED_DATA,        "sorted")
    _assert_sorted(bubble_sort, REVERSE_DATA,       "reverse")
    _assert_sorted(bubble_sort, MOSTLY_SORTED_DATA, "mostly_sorted")


def test_merge_sort():
    _assert_sorted(merge_sort, RANDOM_DATA,        "random")
    _assert_sorted(merge_sort, SORTED_DATA,        "sorted")
    _assert_sorted(merge_sort, REVERSE_DATA,       "reverse")
    _assert_sorted(merge_sort, MOSTLY_SORTED_DATA, "mostly_sorted")


def test_quick_sort():
    _assert_sorted(quick_sort, RANDOM_DATA,        "random")
    _assert_sorted(quick_sort, SORTED_DATA,        "sorted")
    _assert_sorted(quick_sort, REVERSE_DATA,       "reverse")
    _assert_sorted(quick_sort, MOSTLY_SORTED_DATA, "mostly_sorted")


if __name__ == "__main__":
    output = "data/results.csv"
    for arg in sys.argv[1:]:
        if arg.startswith("--output"):
            output = arg.split("=")[1] if "=" in arg else sys.argv[sys.argv.index(arg) + 1]

    test_bubble_sort()
    test_merge_sort()
    test_quick_sort()
    print("All tests passed.")
    print()
    print("--- random ---")
    run_benchmarks(ALGORITHMS, RANDOM_DATA,        kind="random",        output_file=output)
    print("--- sorted ---")
    run_benchmarks(ALGORITHMS, SORTED_DATA,        kind="sorted",        output_file=output)
    print("--- reverse ---")
    run_benchmarks(ALGORITHMS, REVERSE_DATA,       kind="reverse",       output_file=output)
    print("--- mostly_sorted ---")
    run_benchmarks(ALGORITHMS, MOSTLY_SORTED_DATA, kind="mostly_sorted", output_file=output)
