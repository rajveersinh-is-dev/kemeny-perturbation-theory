# Internal Research Specification

## 1. Exact Problem Statement
Given a finite, connected, undirected graph $G = (V, E, W)$ with $n$ vertices, degree vector $d = (d_1, \dots, d_n)^T$, total volume $2m = \sum_i d_i$, and Laplacian $L = D - W$:
1. Derive an exact closed-form algebraic formula for the change in Kemeny's constant $\Delta K(G; u, v, w) = K(G + w e_{uv}) - K(G)$ when a candidate non-edge $(u, v) \notin E$ is added (or an existing edge perturbed) with weight $w > 0$.
2. Determine the algebraic degree and structure of the numerator and denominator of $\Delta K(w)$ as a rational function of $w$.
3. Prove whether the quadratic coefficient of the numerator vanishes identically.
4. Characterize the exact conditions under which adding an edge increases Kemeny's constant ($\Delta K > 0$, Braess paradox) versus decreasing it ($\Delta K < 0$, favorable), and whether a finite weight threshold $w^*(u, v)$ exists where the sign transitions.
5. Construct a deterministic algorithm to evaluate $\Delta K(u, v, w)$ for all $\binom{n}{2}$ pairs in $\mathcal{O}(n^3)$ total time instead of naive $\mathcal{O}(n^5)$ recomputation.

---

## 2. Strongest Relevant Existing Results
- **Kirkland et al. (2023, 2025):** Quantitative bounds on the change in Kemeny's constant when adding a unit-weight edge ($w=1$) to an unweighted tree: maximum decrease is $\approx \frac{3}{16}n^2$ and maximum increase is $\approx \frac{2}{3}n$.
- **Hu & Kirkland (2019):** Characterization of Braess edges specifically in complete multipartite and complete split graphs under unit edge additions.
- **Bini, Meini, & Poloni (2023):** Infinitesimal directional derivative $\left.\frac{\partial K}{\partial w_{uv}}\right|_{w=0}$ formulated via group inverses of Markov chains and modified Laplacians.
- **Ghosh, Boyd, & Saberi (2008):** Total effective resistance $R_{\text{tot}} = \frac{n}{2} \operatorname{Tr}(L^\dagger)$ is strictly convex and strictly decreasing under edge additions (never exhibits Braess paradox).

---

## 3. Research Gap
- No exact algebraic closed form exists for $\Delta K(G; u, v, w)$ on arbitrary connected graphs for finite continuous weights $w > 0$.
- The cancellation of higher-order terms in the rational expansion of $\Delta K(w)$ has never been proven.
- The existence of weight-induced Braess phase transitions (where an edge is favorable for small weights but becomes Braess for large weights) and the closed-form critical threshold $w^*(u, v)$ have never been established.
- No $\mathcal{O}(n^3)$ all-pairs deterministic algorithm exists to evaluate the Kemeny impact of all candidate edges simultaneously.

---

## 4. Proposed Contribution
- **Theorem 1 (Exact Rational Perturbation):** Closed-form formula expressing $\Delta K(w)$ as a rational function $\frac{w(A_0 + A_1 w)}{2m(m+w)(1+w\Omega(u,v))}$.
- **Theorem 2 (Exact Cancellation of Quadratic Term):** Analytical proof that $A_2 \equiv 0$ via the determinantal identity $s_z \Omega - \delta^2 = 4 \det(L^\dagger_{\{u, v\}})$ and $c_1 = 2 \det(L^\dagger_{\{u, v\}})$.
- **Theorem 3 (Four-Regime Phase Classification):** Rigorous partitioning of edge modifications into Globally Favorable, Globally Braess, Weight-Induced Braess (with critical threshold $w^* = -A_0/A_1$), and Capacity-Activated Favorable regimes.
- **Theorem 4 (Optimal Finite Capacity):** Analytical derivation of the unique interior minimum $w_{\text{opt}} \in (0, w^*)$ for weight-induced Braess edges.
- **Theorem 5 (All-Pairs Computational Complexity):** Fast deterministic algorithm computing the exact perturbation for all $\binom{n}{2}$ candidate pairs in $\mathcal{O}(n^3)$ precomputation plus $\mathcal{O}(1)$ query time per pair using $M = L^\dagger D L^\dagger$.

---

## 5. Assumptions Required
- The graph $G = (V, E, W)$ is finite, undirected, connected, and has positive edge weights ($w_e > 0$).
- The perturbation weight satisfies $w > 0$.
- The pair $(u, v)$ satisfies $u \neq v$.

---

## 6. Intended Theorems and Algorithms
- Closed-form mathematical derivations relying on the Moore-Penrose pseudoinverse $L^\dagger$ and the Sherman-Morrison rank-one update on the subspace $\mathbf{1}^\perp$.
- Python implementation: class `KemenyPerturbationEngine` in `src/kemeny_perturbation.py`.

---

## 7. Proof and Evidence Required
- **Algebraic proofs:** Complete deductive proofs for every theorem and lemma, step by step, with no unproven assertions.
- **Symbolic verification:** SymPy automated validation across symbolic variables and rational arithmetic.
- **Numerical verification:** PyTest suite testing across varied graph families (trees, cycles, complete graphs, bipartite graphs, barbell graphs, random Erdős–Rényi, Watts–Strogatz, Barabási–Albert, and real-world networks) with error bounded by machine precision ($< 10^{-12}$).
- **Benchmark evidence:** Real wall-clock timing using `time.perf_counter()` over 10+ iterations with 5 discarded warmup runs to verify the $\mathcal{O}(n^3)$ vs $\mathcal{O}(n^5)$ speedup.

---

## 8. Falsification Tests
- If $A_2 \neq 0$ for ANY graph or ANY edge pair, Theorem 2 is falsified.
- If the difference between the rational formula and brute-force recomputation exceeds numerical tolerance ($10^{-10}$) on any connected graph, Theorem 1 is falsified.
- If an edge classified as Weight-Induced Braess ($A_0 < 0, A_1 > 0$) does not cross zero at $w^* = -A_0/A_1$, Theorem 3 is falsified.
- If $M_{uu} + M_{vv} - 2 M_{uv} \neq x^T D x$, the $\mathcal{O}(1)$ query step of Theorem 5 is falsified.

---

## 9. Principal Known Limitations
- Restricted to undirected graphs where $L = D - W$ is symmetric.
- Applies only to connected graphs; for disconnected graphs, Kemeny's constant is infinite.
- Multiple simultaneous edge additions (rank-$k$ updates with $k \ge 2$) require Woodbury matrix inversions and will introduce higher-degree multivariate rational polynomials.

---

## 10. Minimum Evidence Required to Justify Abstract Claims
1. Formal algebraic proof of Theorems 1–5 in the manuscript.
2. Verified test suite passing 100% of tests with 0 failures and 0 warnings.
3. Verification across at least 1,000 random graph configurations with max error $< 10^{-12}$.
4. Concrete discovery and visualization of weight-induced Braess phase transitions on reproducible network topologies.
5. Measured benchmark confirming execution times for $N \in [10, 200]$ nodes.
