# Algorithm Efficiency and Scalability

This repository contains my implementation and analysis of two classic algorithms: Randomized Quicksort and a Hash Table with Chaining. The goal was to explore how algorithm design decisions, specifically around randomization, affect real-world performance across different input types.

## What's in here

```
.
├── randomized_quicksort.py   # Randomized + Deterministic Quicksort with benchmarking
├── hash_table.py             # Hash Table with chaining, dynamic resizing, and diagnostics
├── report.docx               # Full write-up: theory, benchmarks, and analysis
└── README.md                 # You're reading it
```

## Requirements

Just Python 3.8 or newer. No external packages needed, everything uses the standard library (`random`, `time`, `sys`).

## How to run

### Quicksort

```bash
python randomized_quicksort.py
```

This runs a quick correctness check first (empty arrays, duplicates, sorted/reverse-sorted, random), then benchmarks both Randomized and Deterministic Quicksort across four input distributions and four sizes. The whole thing takes a few seconds.

One thing to note: Deterministic Quicksort is implemented iteratively here instead of recursively. This was intentional, on sorted or reverse-sorted input, a recursive implementation hits Python's recursion limit around n=2000, which would make it impossible to get complete benchmark data. The iterative version sidesteps that without changing the algorithm's behavior or time complexity.

### Hash Table

```bash
python hash_table.py
```

Runs correctness tests (insert, search, update, delete, bulk operations that trigger resizing), then prints a demo showing individual operations with load factor tracking and a stats summary after a stress insert of 200 elements.

## Key findings

**Quicksort:** The randomized version is essentially immune to the sorted/reverse-sorted worst case that cripples the deterministic version. At n=4000 on reverse-sorted input, randomized QS finished in ~6 ms while deterministic QS took over 560 ms, about 90x slower. On random input the gap nearly disappears, with deterministic QS actually edging ahead slightly since it skips the random pivot selection overhead.

The one case where both struggle equally is arrays with very few distinct values. With only 10 unique values across 4000 elements, both implementations slow down significantly due to heavily imbalanced partitions. A three-way partition scheme would fix this, but that's a separate implementation.

**Hash Table:** The universal hash function family keeps collision rates low regardless of input, and dynamic resizing keeps the load factor bounded between 0.25 and 0.75. In practice, after inserting 200 elements the average chain length was 1.19 with a maximum of 2, essentially O(1) per operation as the theory predicts.

## Notes

Benchmark timings will vary depending on your machine. The patterns (which algorithm is faster and by how much) should be consistent, but the absolute millisecond numbers won't match exactly.
