import copy
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sorting.sorts import bubble_sort, merge_sort, quick_sort
from benchmark import run_benchmarks

INPUT_SIZES = [1_000, 5_000, 10_000, 50_000, 100_000]

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


RANDOM_DATA = {n: generate_input(n, "random") for n in INPUT_SIZES}
SORTED_DATA = {n: generate_input(n, "sorted") for n in INPUT_SIZES}
REVERSE_DATA = {n: generate_input(n, "reverse") for n in INPUT_SIZES}


def test_bubble_sort():
    for n in INPUT_SIZES:
        a = copy.copy(RANDOM_DATA[n])
        bubble_sort(a)
        assert a == sorted(RANDOM_DATA[n]), f"bubble_sort failed on random n={n}"

        a = copy.copy(SORTED_DATA[n])
        bubble_sort(a)
        assert a == sorted(SORTED_DATA[n]), f"bubble_sort failed on sorted n={n}"

        a = copy.copy(REVERSE_DATA[n])
        bubble_sort(a)
        assert a == sorted(REVERSE_DATA[n]), f"bubble_sort failed on reverse n={n}"


def test_merge_sort():
    for n in INPUT_SIZES:
        a = copy.copy(RANDOM_DATA[n])
        merge_sort(a)
        assert a == sorted(RANDOM_DATA[n]), f"merge_sort failed on random n={n}"

        a = copy.copy(SORTED_DATA[n])
        merge_sort(a)
        assert a == sorted(SORTED_DATA[n]), f"merge_sort failed on sorted n={n}"

        a = copy.copy(REVERSE_DATA[n])
        merge_sort(a)
        assert a == sorted(REVERSE_DATA[n]), f"merge_sort failed on reverse n={n}"


def test_quick_sort():
    for n in INPUT_SIZES:
        a = copy.copy(RANDOM_DATA[n])
        quick_sort(a)
        assert a == sorted(RANDOM_DATA[n]), f"quick_sort failed on random n={n}"

        a = copy.copy(SORTED_DATA[n])
        quick_sort(a)
        assert a == sorted(SORTED_DATA[n]), f"quick_sort failed on sorted n={n}"

        a = copy.copy(REVERSE_DATA[n])
        quick_sort(a)
        assert a == sorted(REVERSE_DATA[n]), f"quick_sort failed on reverse n={n}"


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
    run_benchmarks(ALGORITHMS, RANDOM_DATA, kind="random", output_file=output)
    print("--- sorted ---")
    run_benchmarks(ALGORITHMS, SORTED_DATA, kind="sorted", output_file=output)
    print("--- reverse ---")
    run_benchmarks(ALGORITHMS, REVERSE_DATA, kind="reverse", output_file=output)
