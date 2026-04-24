"""
In-place sorting implementations for benchmarking (Basil Mohad — implementation lead).

All three functions mutate the list passed in. Callers should pass a copy if the
original data must be preserved.
"""

from __future__ import annotations

import random
from collections.abc import MutableSequence


def bubble_sort(arr: MutableSequence[int]) -> None:
    """O(n^2) average/worst; stable; in-place. Early exit when a pass makes no swaps."""
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break


def merge_sort(arr: MutableSequence[int]) -> None:
    """O(n log n) worst case; stable; O(n) auxiliary space."""
    n = len(arr)
    if n < 2:
        return
    aux = [0] * n

    def merge(lo: int, mid: int, hi: int) -> None:
        i, j = lo, mid + 1
        for k in range(lo, hi + 1):
            aux[k] = arr[k]
        k = lo
        while i <= mid and j <= hi:
            if aux[i] <= aux[j]:
                arr[k] = aux[i]
                i += 1
            else:
                arr[k] = aux[j]
                j += 1
            k += 1
        while i <= mid:
            arr[k] = aux[i]
            i += 1
            k += 1
        while j <= hi:
            arr[k] = aux[j]
            j += 1
            k += 1

    def sort_range(lo: int, hi: int) -> None:
        if lo >= hi:
            return
        mid = (lo + hi) // 2
        sort_range(lo, mid)
        sort_range(mid + 1, hi)
        merge(lo, mid, hi)

    sort_range(0, n - 1)


def quick_sort(arr: MutableSequence[int]) -> None:
    """O(n log n) typical; O(n^2) worst case; not stable; in-place; iterative to avoid recursion depth."""
    n = len(arr)
    if n < 2:
        return

    def partition(lo: int, hi: int) -> int:
        pivot_idx = random.randint(lo, hi)
        arr[pivot_idx], arr[hi] = arr[hi], arr[pivot_idx]
        pivot = arr[hi]
        i = lo
        for j in range(lo, hi):
            if arr[j] <= pivot:
                arr[i], arr[j] = arr[j], arr[i]
                i += 1
        arr[i], arr[hi] = arr[hi], arr[i]
        return i

    stack: list[tuple[int, int]] = [(0, n - 1)]
    while stack:
        lo, hi = stack.pop()
        if lo >= hi:
            continue
        p = partition(lo, hi)
        stack.append((lo, p - 1))
        stack.append((p + 1, hi))
