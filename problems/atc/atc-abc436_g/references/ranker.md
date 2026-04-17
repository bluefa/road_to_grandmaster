# Ranker Notes

## Source
- URL: https://kmjp.hatenablog.jp/entry/2025/12/14/0930

## Implementation Angle
- kmjp uses a more algebraic route than the official editorial.
- Append one extra weight `1` to `A`. Then counting solutions to `A · X <= M` becomes counting
  exact solutions to `A' · X' = M`, because the added variable absorbs the leftover slack.
- The answer is therefore the coefficient of `x^M` in
  `P(x) = product_i 1 / (1 - x^{A_i})`.
- Since `M` is up to `10^18`, the coefficient is extracted with Bostan-Mori instead of DP on `M`.

## Data Representation
- Let `Q(x) = product_i (1 - x^{A_i})`. Then `P(x) = 1 / Q(x)`, so the task is coefficient extraction
  from a rational generating function.
- Because `sum(A_i) <= 10000` after appending `1`, `Q` has manageable degree and can be stored densely.
- Polynomial products inside Bostan-Mori are implemented with NTT under modulus `998244353`.
- A practical build path is:
  1. Count how many times each weight appears.
  2. Build `Q(x)` from repeated multiplication by `(1 - x^w)`.
  3. Run Bostan-Mori on numerator `1` and denominator `Q(x)` to obtain `[x^M] 1 / Q(x)`.

## Complexity
- Degree scale is `S = sum(A) + 1`.
- Building the denominator is about `O(S^2)` if done naively or faster with grouped products.
- Bostan-Mori then costs roughly `O(S log S log M)` with NTT-based multiplication.

## Points To Compare With My Attempt
- Did I convert the inequality into an equality by adding a synthetic weight `1`?
- Did I recognize the count as a generating-function coefficient instead of a combinatorial DP?
- If I know Bostan-Mori, could I reuse a standard rational-series coefficient template here almost unchanged?
