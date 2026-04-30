"""Minimal valgrind target — runs one sort once so valgrind can instrument it."""
import os, random, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sorting.sorts import bubble_sort, merge_sort, quick_sort

_ALGOS = {'bubble_sort': bubble_sort, 'merge_sort': merge_sort, 'quick_sort': quick_sort}

def _gen(n, kind):
    data = random.sample(range(n * 10), n)
    if kind == "sorted":       return sorted(data)
    if kind == "reverse":      return sorted(data, reverse=True)
    if kind == "mostly_sorted":
        data = sorted(data)
        for i in random.sample(range(n - 1), max(1, n // 10)):
            data[i], data[i + 1] = data[i + 1], data[i]
        return data
    return data

if __name__ == "__main__":
    _ALGOS[sys.argv[1]](_gen(int(sys.argv[2]), sys.argv[3]))
