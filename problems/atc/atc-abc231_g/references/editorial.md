# Editorial Notes

## Sources
- Primary URL: https://atcoder.jp/contests/abc231/editorial/3089
- Collected Entries:
  - Title: Official Editorial
    URL: https://atcoder.jp/contests/abc231/editorial/3089
    Kind: official
  - Title: User Editorial by Kiri8128
    URL: https://atcoder.jp/contests/abc231/editorial/3127
    Kind: user_editorial

## Editorial 1
### Title
- Official Editorial

### Source
- URL: https://atcoder.jp/contests/abc231/editorial/3089

### Core Idea
- Expand `E[prod_i (A_i + X_i)]` by choosing, for each factor, either `A_i` or `X_i`.
- Group the terms by how many `X_i` factors were chosen. For a fixed size `s`, symmetry makes
  `E[prod_{i in T} X_i]` depend only on `s`, not on the specific subset `T`.
- Therefore the answer is the sum of:
  `elementary symmetric sum of degree N - s in A` times `E[prod_{i=1}^s X_i]`.
- Compute the elementary symmetric sums by DP on `prod_i (1 + A_i x)`, then compute
  `E[prod_{i=1}^s X_i] = (K)_s / N^s`, where `(K)_s = K (K - 1) ... (K - s + 1)`.

### Invariants
- If `e[t]` denotes the degree-`t` elementary symmetric sum of `A`, then after processing `A_{i+1}`,
  the transition is `dp[j] = dp[j] + A_{i+1} * dp[j - 1]`.
- For `E[prod_{i=1}^s X_i]`, only assignments of the `s` chosen boxes to pairwise distinct operation
  times contribute. If two different boxes try to use the same operation index, the product is `0`.
- The number of valid ordered time choices is `(K)_s`, and each contributes probability `(1 / N)^s`.

### Complexity
- `O(N^2)` time for the symmetric-sum DP.
- `O(N)` time to build all falling-factorial expectation terms.
- `O(N)` extra memory with a 1D DP implementation.

### Distinctive Point
- This editorial is the most direct combinatorial decomposition: first reduce the product to
  elementary symmetric sums, then reduce the random part to counting injective choices of operations.

## Editorial 2
### Title
- User Editorial by Kiri8128

### Source
- URL: https://atcoder.jp/contests/abc231/editorial/3127

### Core Idea
- Represent a state with counts `c_i` by the monomial `x_1^{c_1} ... x_N^{c_N}`.
- One random operation corresponds to multiplying by `(x_1 + ... + x_N) / N`, so after `K` operations
  the weighted generating function is
  `(prod_i x_i^{A_i}) * (x_1 + ... + x_N)^K / N^K`.
- The score `prod_i B_i` can be extracted by differentiating once with respect to every `x_i` and then
  substituting `x_i = 1`.
- Let `y = x_1 + ... + x_N`. Then each derivative acts like `(A_i / x_i + d/dy)` on this special form,
  so expanding all derivatives has the same coefficient structure as expanding `prod_i (A_i + X)`.

### Invariants
- Choosing the `d/dy` part from exactly `s` factors corresponds to taking the `s`-th derivative of `y^K`,
  which gives the falling factorial `(K)_s`.
- Choosing the `A_i / x_i` part from the other factors corresponds to selecting a product of some `A_i`,
  so the same elementary symmetric sums appear as in the official editorial.
- After substituting `x_i = 1`, the operator expansion collapses to the same final formula as the
  combinatorial solution.

### Complexity
- Naive coefficient expansion gives the same `O(N^2)` time as the official approach.
- The note also points out that the polynomial `prod_i (A_i + X)` can be built with FFT in
  `O(N (log N)^2)` if one wants the bonus faster approach.

### Distinctive Point
- This editorial reframes the entire problem as a generating-function and differential-operator
  computation, which explains why the elementary symmetric polynomial appears naturally.

## Editorial Comparison
- Both notes derive the same final formula: sum over `s` of an elementary symmetric sum in `A`
  multiplied by `(K)_s / N^s`.
- The official editorial is easier to implement from scratch because it directly exposes the DP and the
  injective-time counting argument.
- The user editorial is more structural: it explains the same coefficients via generating functions and
  repeated differentiation, and also highlights the polynomial-product viewpoint behind the bonus FFT idea.

## Points To Compare With My Attempt
- Did I explicitly reduce the answer to elementary symmetric sums of `A`, or did I stay stuck on the
  multinomial distribution of `(X_1, ..., X_N)`?
- Did I notice that `E[prod_{i=1}^s X_i]` only counts pairwise distinct operation times, giving
  a clean falling factorial `(K)_s`?
- If I found the formula, which viewpoint got me there faster: direct combinatorics or generating
  functions?
