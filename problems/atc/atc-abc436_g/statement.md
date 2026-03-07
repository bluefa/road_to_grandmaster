# G - Linear Inequation

## Source
- URL: https://atcoder.jp/contests/abc436/tasks/abc436_g

## Summary
- Given a positive integer sequence `A` of length `N` and a positive integer `M`, count how many non-negative integer sequences `x` satisfy `sum(A_i * x_i) <= M`.
- Output the count modulo `998244353`.

## Constraints
- `1 <= N <= 100`
- `1 <= A_i <= 100`
- `1 <= M <= 10^18`

## Input / Output Notes
- Input: `N M` on the first line, then `A_1 ... A_N` on the second line.
- Output: one integer, the number of valid sequences modulo `998244353`.

## Edge Cases
- `M` is very large, so naive DP over `M` is not viable.
- Each `x_i` can be zero.
- The raw count can be extremely large before taking modulo.
