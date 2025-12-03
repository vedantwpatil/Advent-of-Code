from collections import Counter
import sys

# Read all input at once, split into words, map to int
data = map(int, sys.stdin.read().split())
# "Unzip" into two lists using slicing [start::step]
left, right = list(data)[0::2], list(data)[1::2]

# --- Part 1 ---
# zip(sorted(l), sorted(r)) pairs them up perfectly
print("Part 1:", sum(abs(l - r) for l, r in zip(sorted(left), sorted(right))))

# --- Part 2 ---
# Counter creates the hashmap for us instantly
counts = Counter(right)
print("Part 2:", sum(num * counts[num] for num in left))
