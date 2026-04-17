# C - And Reachability

## Source
- URL: https://codeforces.com/problemset/problem/1168/C
- Time Limit: 3 seconds
- Memory Limit: 256 megabytes

## Summary
- Given an array `a_1, ..., a_n` of non-negative integers, define `y` as reachable from `x` (with `x < y`) if there exists an increasing index sequence `x = p_1 < p_2 < ... < p_k = y` such that `a_{p_i} & a_{p_{i+1}} > 0` for every consecutive pair.
- Answer `q` queries, each asking whether `y_i` is reachable from `x_i`.

## Constraints
- `2 <= n <= 300000`
- `1 <= q <= 300000`
- `0 <= a_i <= 300000`
- `1 <= x_i < y_i <= n`

## Input / Output Notes
- Input line 1: `n q`.
- Input line 2: `n` integers `a_1 ... a_n`.
- Next `q` lines: two integers `x_i y_i` per line.
- Output: `q` lines, each either `Shi` (reachable) or `Fou` (not reachable).

## Edge Cases
- `a_i = 0` can never participate in any reachability edge (AND with anything is 0).
- Values are bounded by `300000`, so at most 19 bits are relevant for the bitmask DP.
