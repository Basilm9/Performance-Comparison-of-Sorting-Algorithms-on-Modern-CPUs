import copy
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sorting.sorts import bubble_sort, merge_sort, quick_sort
from benchmark import run_benchmarks

INPUT_SIZES = [1_000, 5_000, 10_000]

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


DATA = {n: generate_input(n, "random") for n in INPUT_SIZES}


def test_bubble_sort():
    for n in INPUT_SIZES:
        a = copy.copy(DATA[n])
        bubble_sort(a)
        expected = sorted(DATA[n])
        assert a == expected, f"bubble_sort failed on n={n}"


def test_merge_sort():
    for n in INPUT_SIZES:
        a = copy.copy(DATA[n])
        merge_sort(a)
        expected = sorted(DATA[n])
        assert a == expected, f"merge_sort failed on n={n}"


def test_quick_sort():
    for n in INPUT_SIZES:
        a = copy.copy(DATA[n])
        quick_sort(a)
        expected = sorted(DATA[n])
        assert a == expected, f"quick_sort failed on n={n}"


if __name__ == "__main__":
    test_bubble_sort()
    test_merge_sort()
    test_quick_sort()
    print("All tests passed.")
    print()
    run_benchmarks(ALGORITHMS, DATA)
