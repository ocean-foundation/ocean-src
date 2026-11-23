# sort

Stable O(n log n) merge sorts of dynamic arrays in place, and binary search.

- `Ints(&items)`, `Floats(&items)`, `Strings(&items)` sort in increasing order
  (strings by unsigned byte value; NaN positions are unspecified).
- `Slice<T>(&items, less)` sorts any element type by `less(a, b)`. Generic
  calls need explicit type arguments.
- `IsSorted<T>(items, less)`, `Reverse<T>(&items)`.
- `Search(n, found)` returns the first index in `[0, n)` where `found` is true
  (or `n`), assuming false-then-true. `SearchInts` and `SearchStrings` return
  the index of a value in sorted data, or its insertion point.

Sorting allocates one temporary copy of the array. Run `ocean test sort`.
