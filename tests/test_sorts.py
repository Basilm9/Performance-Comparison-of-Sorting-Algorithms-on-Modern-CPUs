import copy
import random
import unittest

from sorting.sorts import bubble_sort, merge_sort, quick_sort


def run_sort(fn, arr):
    a = copy.copy(arr)
    fn(a)
    return a


class TestSorts(unittest.TestCase):
    def assert_sorted_like_builtin(self, arr):
        expected = sorted(arr)
        for name, fn in (
            ("bubble_sort", bubble_sort),
            ("merge_sort", merge_sort),
            ("quick_sort", quick_sort),
        ):
            with self.subTest(algorithm=name, input=arr[:20]):
                got = run_sort(fn, arr)
                self.assertEqual(got, expected, msg=name)

    def test_empty_and_singleton(self):
        self.assert_sorted_like_builtin([])
        self.assert_sorted_like_builtin([1])

    def test_sorted_reverse_duplicates(self):
        self.assert_sorted_like_builtin(list(range(50)))
        self.assert_sorted_like_builtin(list(range(50, -1, -1)))
        self.assert_sorted_like_builtin([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5])

    def test_random_stress(self):
        rng = random.Random(0)
        for n in (0, 1, 2, 3, 10, 31, 100):
            arr = [rng.randint(-1000, 1000) for _ in range(n)]
            self.assert_sorted_like_builtin(arr)


if __name__ == "__main__":
    unittest.main()
