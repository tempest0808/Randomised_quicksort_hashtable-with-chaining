"""
randomized_quicksort.py
-----------------------
"""

import random
import time
import sys

sys.setrecursionlimit(20000)

# Sorting implementations

def randomized_quicksort(arr: list, low: int, high: int) -> None:
    """Randomized quicksort implementation."""

    if low < high:
        pivot_idx = _randomized_partition(arr, low, high)
        randomized_quicksort(arr, low, pivot_idx - 1)
        randomized_quicksort(arr, pivot_idx + 1, high)


def _randomized_partition(arr: list, low: int, high: int) -> int:
    """Choose a random pivot, swap it to the end, then partition."""
    rand_idx = random.randint(low, high)
    arr[rand_idx], arr[high] = arr[high], arr[rand_idx]
    return _partition(arr, low, high)


def deterministic_quicksort(arr: list, low: int, high: int) -> None:
    """
    Sort arr[low..high] in-place using the first element as pivot.
    """
    stack = [(low, high)]
    while stack:
        lo, hi = stack.pop()
        if lo < hi:
            pivot_idx = _deterministic_partition(arr, lo, hi)
            stack.append((lo, pivot_idx - 1))
            stack.append((pivot_idx + 1, hi))


def _deterministic_partition(arr: list, low: int, high: int) -> int:
    """Use the first element as pivot."""
    arr[low], arr[high] = arr[high], arr[low]
    return _partition(arr, low, high)


def _partition(arr: list, low: int, high: int) -> int:
    """
    Lomuto partition scheme.
    Pivot = arr[high]. Returns final pivot index.
    """
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

# Input generators

def make_random(n: int) -> list:
    return [random.randint(0, 10 * n) for _ in range(n)]

def make_sorted(n: int) -> list:
    return list(range(n))

def make_reverse(n: int) -> list:
    return list(range(n, 0, -1))

def make_repeated(n: int) -> list:
    # ~10 distinct values regardless of n
    return [random.randint(0, 9) for _ in range(n)]


DISTRIBUTIONS = {
    "Random":          make_random,
    "Sorted":          make_sorted,
    "Reverse-sorted":  make_reverse,
    "Repeated values": make_repeated,
}


# Timing helper

def time_sort(sort_fn, arr: list) -> float:
    """Return wall-clock seconds to run sort_fn on a copy of arr."""
    data = arr[:]
    start = time.perf_counter()
    sort_fn(data, 0, len(data) - 1)
    return time.perf_counter() - start


# Benchmark

SIZES = [500, 1000, 2000, 4000]
TRIALS = 3


def run_benchmark() -> dict:
    """
    Returns nested dict:
      results[dist_name][size] = {"randomized": avg_sec, "deterministic": avg_sec}
    """
    results = {}

    for dist_name, generator in DISTRIBUTIONS.items():
        results[dist_name] = {}
        for n in SIZES:
            rq_times, dq_times = [], []

            for _ in range(TRIALS):
                arr = generator(n)
                rq_times.append(time_sort(randomized_quicksort, arr))
                dq_times.append(time_sort(deterministic_quicksort, arr))

            results[dist_name][n] = {
                "randomized":    sum(rq_times) / len(rq_times),
                "deterministic": sum(dq_times) / len(dq_times),
            }

    return results


def print_results(results: dict) -> None:
    col = 16
    print("\n" + "=" * 72)
    print("  BENCHMARK RESULTS  (average of {} trials)".format(TRIALS))
    print("  Note: timings are machine-specific; run locally for your results.")
    print("=" * 72)

    for dist_name, size_data in results.items():
        print(f"\n  Distribution: {dist_name}")
        header = f"  {'Size':>6}  {'Randomized QS':>{col}}  {'Deterministic QS':>{col}}"
        print(header)
        print("  " + "-" * (len(header) - 2))
        for n, timings in sorted(size_data.items()):
            rq = f"{timings['randomized']  * 1000:.3f} ms"
            dq = f"{timings['deterministic'] * 1000:.3f} ms"
            print(f"  {n:>6}  {rq:>{col}}  {dq:>{col}}")
    print()

# Quick tests

def _smoke_test() -> None:
    cases = [
        [],
        [1],
        [3, 1, 2],
        [5, 5, 5, 5],
        list(range(10)),
        list(range(9, -1, -1)),
        [random.randint(-100, 100) for _ in range(50)],
    ]
    for arr in cases:
        expected = sorted(arr)

        cp = arr[:]
        if cp:
            randomized_quicksort(cp, 0, len(cp) - 1)
        assert cp == expected, f"RQS failed on {arr}"

        cp = arr[:]
        if cp:
            deterministic_quicksort(cp, 0, len(cp) - 1)
        assert cp == expected, f"DQS failed on {arr}"

    print("  Smoke tests passed for both implementations.\n")


# Entry point

if __name__ == "__main__":
    print("\nRunning correctness smoke tests...")
    _smoke_test()

    print("Running benchmark (this may take a few seconds)...")
    results = run_benchmark()
    print_results(results)
