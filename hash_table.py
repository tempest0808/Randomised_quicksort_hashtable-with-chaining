"""
hash_table.py
-------------
Hash table using chaining for collision resolution.

"""

import random
from typing import Any, Optional

# Universal hash function

_PRIME = (1 << 31) - 1   # Mersenne prime 2^31 − 1


class UniversalHashFunction:
    """Universal hash function used by the hash table."""

    def __init__(self, m: int, p: int = _PRIME) -> None:
        self.m = m          # number of slots
        self.p = p
        self.a = random.randint(1, p - 1)
        self.b = random.randint(0, p - 1)

    def __call__(self, key: int) -> int:
        return ((self.a * key + self.b) % self.p) % self.m

    def resize(self, new_m: int) -> "UniversalHashFunction":
        """Return a new hash function for a different table size."""
        return UniversalHashFunction(new_m, self.p)


# Linked-list node for chaining

class _Node:
    __slots__ = ("key", "value", "next")

    def __init__(self, key: int, value: Any, next_node: Optional["_Node"] = None):
        self.key = key
        self.value = value
        self.next = next_node


# Hash table


class HashTable:
    """Hash table with chaining."""

    def __init__(
        self,
        initial_capacity: int = 8,
        max_load_factor: float = 0.75,
        min_load_factor: float = 0.25,
    ) -> None:
        self._capacity = max(1, initial_capacity)
        self._max_lf = max_load_factor
        self._min_lf = min_load_factor
        self._size = 0
        self._hash_fn = UniversalHashFunction(self._capacity)
        self._buckets: list[Optional[_Node]] = [None] * self._capacity

    # Public interface

    def insert(self, key: int, value: Any) -> None:
        """Insert a key-value pair into the table."""
    
        idx = self._hash_fn(key)
        node = self._buckets[idx]

        # Walk the chain: update if key already present
        while node is not None:
            if node.key == key:
                node.value = value
                return          # update in place, size unchanged
            node = node.next

        # Prepend new node (O(1))
        self._buckets[idx] = _Node(key, value, self._buckets[idx])
        self._size += 1
        self._maybe_grow()

    def search(self, key: int) -> Optional[Any]:
        """
        Return the value for key, or None if absent.
        Expected O(1 + α) where α = load factor.
        """
        idx = self._hash_fn(key)
        node = self._buckets[idx]
        while node is not None:
            if node.key == key:
                return node.value
            node = node.next
        return None

    def delete(self, key: int) -> bool:
        """Remove a key from the hash table."""

        idx = self._hash_fn(key)
        prev, node = None, self._buckets[idx]
        while node is not None:
            if node.key == key:
                if prev is None:
                    self._buckets[idx] = node.next
                else:
                    prev.next = node.next
                self._size -= 1
                self._maybe_shrink()
                return True
            prev, node = node, node.next
        return False

    def __len__(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def load_factor(self) -> float:
        return self._size / self._capacity

    # Dynamic resizing

    def _rehash(self, new_capacity: int) -> None:
        """Rebuild the table with a fresh hash function for new_capacity."""
        old_buckets = self._buckets
        self._capacity = new_capacity
        self._hash_fn = self._hash_fn.resize(new_capacity)
        self._buckets = [None] * new_capacity
        self._size = 0

        for head in old_buckets:
            node = head
            while node is not None:
                # Re-insert without triggering resize checks again
                idx = self._hash_fn(node.key)
                self._buckets[idx] = _Node(node.key, node.value, self._buckets[idx])
                self._size += 1
                node = node.next

    def _maybe_grow(self) -> None:
        if self.load_factor > self._max_lf:
            self._rehash(self._capacity * 2)

    def _maybe_shrink(self) -> None:
        if self._capacity > 8 and self.load_factor < self._min_lf:
            self._rehash(max(8, self._capacity // 2))

    # Diagnostics

    def stats(self) -> dict:
        """Return basic statistics about the current state of the table."""
        chain_lengths = []
        for head in self._buckets:
            length = 0
            node = head
            while node:
                length += 1
                node = node.next
            chain_lengths.append(length)

        occupied = sum(1 for l in chain_lengths if l > 0)
        max_chain = max(chain_lengths) if chain_lengths else 0
        avg_chain = (self._size / occupied) if occupied else 0.0

        return {
            "size":          self._size,
            "capacity":      self._capacity,
            "load_factor":   round(self.load_factor, 4),
            "occupied_slots": occupied,
            "max_chain_len":  max_chain,
            "avg_chain_len":  round(avg_chain, 3),
        }


# Demonstration / smoke tests

def _smoke_test() -> None:
    ht = HashTable(initial_capacity=8)

    # Basic insert + search
    ht.insert(1, "one")
    ht.insert(2, "two")
    ht.insert(3, "three")
    assert ht.search(1) == "one"
    assert ht.search(2) == "two"
    assert ht.search(99) is None, "Missing key should return None"

    # Update existing key
    ht.insert(1, "ONE")
    assert ht.search(1) == "ONE", "Update should overwrite old value"

    # Delete
    assert ht.delete(2) is True
    assert ht.search(2) is None
    assert ht.delete(2) is False, "Deleting absent key should return False"

    # Trigger resizing via bulk inserts
    for k in range(100):
        ht.insert(k, k * 10)
    assert ht.search(50) == 500
    assert len(ht) == 100   # keys 0..99; key 2 was deleted then re-inserted

    # Trigger shrink via bulk deletes
    for k in range(100):
        ht.delete(k)
    assert len(ht) == 0

    print("  All smoke tests passed.\n")


def _demo() -> None:
    print("=" * 55)
    print("  Hash Table with Chaining  –  Demo")
    print("=" * 55)

    ht = HashTable(initial_capacity=4)

    ops = [
        ("insert", 10, "apple"),
        ("insert", 20, "banana"),
        ("insert", 30, "cherry"),
        ("insert", 10, "APPLE"),   # overwrite
        ("search", 20, None),
        ("search", 99, None),
        ("delete", 20, None),
        ("search", 20, None),
    ]

    for op in ops:
        if op[0] == "insert":
            _, k, v = op
            ht.insert(k, v)
            print(f"  INSERT  {k!r:>4} → {v!r:<10}  |  size={len(ht)}, lf={ht.load_factor:.2f}")
        elif op[0] == "search":
            _, k, _ = op
            result = ht.search(k)
            print(f"  SEARCH  {k!r:>4}        → {result!r:<10}")
        elif op[0] == "delete":
            _, k, _ = op
            found = ht.delete(k)
            print(f"  DELETE  {k!r:>4}        → found={found}, size={len(ht)}")

    # Stress: insert 200 items and show stats
    print("\n  --- Stress insert (200 items) ---")
    ht2 = HashTable()
    for i in range(200):
        ht2.insert(i, i ** 2)
    s = ht2.stats()
    for k, v in s.items():
        print(f"    {k:<20}: {v}")


if __name__ == "__main__":
    print("\nRunning smoke tests...")
    _smoke_test()
    _demo()
