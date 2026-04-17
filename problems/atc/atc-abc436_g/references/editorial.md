# Editorial Notes

## Source
- URL: https://atcoder.jp/contests/abc436/editorial/14748?lang=en

## Core Idea
- Let `f(A, M)` be the number of non-negative integer vectors `X` with `A · X <= M`.
- Choose an integer base `d >= 2` and write every coordinate as `X = dQ + R` with `0 <= R_i < d`.
- For a fixed remainder vector `R`, the inequality becomes `d(A · Q) + A · R <= M`, so
  `f(A, M) = sum_{s in S} f(A, floor((M - s) / d))`,
  where `S` is the multiset of all values `A · R` over `R_i in [0, d - 1]`.
- Instead of evaluating a single state directly, maintain a finite linear combination
  `sum_i c_i f(A, i)`. One reduction step rewrites the coefficients as
  `c'_i = sum_{j = 0}^{d - 1} sum_{s in S} c_{id + j + s}`.
- Start from `c_M = 1` and repeatedly apply the reduction until every nonzero index is `<= 0`.
  Then only `c_0` survives because `f(A, i) = 0` for `i < 0` and `f(A, 0) = 1`.

## Invariants
- After one reduction, the maximum live index shrinks by about a factor of `d`.
- Let `L0` be the span of indices with nonzero coefficients and `L1 = max(S) = (d - 1) * sum(A)`.
  The editorial proves `L0 <= L1 * d / (d - 1)` throughout the process, so the active range stays
  `O(sum(A))`, independent of `M`.
- The heavy work per round is updating the coefficient window using the multiset `S`, which can be
  handled with convolutions / FFT-like polynomial multiplication.

## Complexity
- Number of reduction rounds: `O(log_d M)`.
- Per round cost: `O((L0 + L1) log(L0 + L1))`, with `L0 + L1 = O(sum(A))`.
- The sample implementation also spends extra preprocessing time to build `S`; with the stated
  implementation this is still fast enough for `N <= 100`, `A_i <= 100`.

## Points To Compare With My Attempt
- Did I notice that the direct `<= M` count can be reduced digit-by-digit by decomposing each `x_i` in base `d`?
- Did I keep the state space compressed to a short coefficient interval instead of DP over `M`?
- If I used convolutions, did I separate the one-time construction of `S` from the repeated coefficient updates?
