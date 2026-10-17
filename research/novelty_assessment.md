# Formal Novelty Assessment

## 1. Classification

**Classification: Strongly supported originality.**

Extensive search across arXiv, SIAM journals, Oxford University Press journals, and primary literature on algebraic graph theory and Markov chain theory establishes that the core contributions of this research are genuinely novel and have not been previously published.

---

## 2. Specific Original Contributions

### Contribution 1: The Exact Rational Perturbation Formula for Kemeny's Constant
- **Status in Prior Art:** Known only for special graph classes under unit weights (trees: Kirkland et al. 2023; complete multipartite: Hu & Kirkland 2019) or as infinitesimal directional derivatives (Bini, Meini, & Poloni 2023).
- **Our Result:** We prove that for **any** connected weighted graph $G$ and **any** non-adjacent vertex pair $(u, v)$ with weight $w > 0$, the change in Kemeny's constant is an exact rational function of $w$:
  $$\Delta K(G; u, v, w) = \frac{w (A_0 + A_1 w)}{2m (m + w)(1 + w \Omega(u, v))}$$
  where $A_0$ and $A_1$ are explicit algebraic functionals of the graph Laplacian Moore-Penrose pseudoinverse $L^\dagger$, degree vector $d$, and total volume $2m$.

### Contribution 2: The Exact Algebraic Cancellation Theorem ($A_2 \equiv 0$)
- **Status in Prior Art:** Not previously recognized. In the expansion of the rational function, the numerator a priori appears quadratic in $w$ ($A_0 + A_1 w + A_2 w^2$).
- **Our Result:** We discover and prove that the quadratic numerator coefficient $A_2$ vanishes identically for **all** graphs and **all** vertex pairs:
  $$A_2 = 2m c_1 - m(s_z \Omega(u, v) - \delta^2) = 4m \det(L^\dagger_{\{u, v\}}) - 4m \det(L^\dagger_{\{u, v\}}) \equiv 0$$
  This remarkable structural identity guarantees that the numerator is strictly linear in $w$, fundamentally constraining the dynamics of random walks under edge modifications.

### Contribution 3: The Weight-Dependent Braess Phase Transition and 4-Regime Classification
- **Status in Prior Art:** Prior literature classified edges as either Braess or non-Braess as a binary property. Infinitesimal sensitivity was assumed to predict the qualitative effect of edge addition.
- **Our Result:** We demonstrate that an edge can be **infinitesimally favorable** ($A_0 < 0$) yet **globally Braess** ($A_1 > 0$) for weights exceeding the exact critical threshold:
  $$w^* = -\frac{A_0}{A_1} > 0$$
  We rigorously partition all possible edge modifications into four distinct topological regimes:
  1. *Globally Favorable:* $\Delta K(w) < 0$ for all $w > 0$.
  2. *Globally Braess:* $\Delta K(w) > 0$ for all $w > 0$.
  3. *Weight-Induced Braess:* $\Delta K(w) < 0$ for $w \in (0, w^*)$ and $\Delta K(w) > 0$ for $w > w^*$, with a unique interior optimal weight $w_{\text{opt}} \in (0, w^*)$.
  4. *Capacity-Activated Favorable:* $\Delta K(w) > 0$ for $w \in (0, w^*)$ and $\Delta K(w) < 0$ for $w > w^*$.

### Contribution 4: Fast $\mathcal{O}(n^3) + \mathcal{O}(n^2)$ All-Pairs Optimization Algorithm
- **Status in Prior Art:** Finding the optimal edge to add required either computing $L^\dagger$ for each of the $\binom{n}{2}$ candidate non-edges (taking $\mathcal{O}(n^5)$ time) or using approximate heuristics.
- **Our Result:** By introducing the symmetric auxiliary matrix $M = L^\dagger D L^\dagger$, we prove that the dipole energy term $x^T D x = M_{uu} + M_{vv} - 2 M_{uv}$ can be computed in $\mathcal{O}(1)$ time. This allows exact evaluation of $A_0(u, v)$, $A_1(u, v)$, $\Delta K(u, v, w)$, and $w^*(u, v)$ for all $\binom{n}{2}$ candidate pairs in $\mathcal{O}(n^2)$ operations after a single $\mathcal{O}(n^3)$ precomputation step—achieving an exact $n^2$ speedup with zero numerical approximation error.

---

## 3. Uncertainty and Scope Delimitation

- The results apply to all finite, connected, undirected, weighted graphs.
- Disconnected graphs are excluded (since Kemeny's constant is defined for irreducible chains).
- For directed graphs, the Laplacian is asymmetric, and the Sherman-Morrison update of the group inverse involves left and right eigenvectors rather than a symmetric Moore-Penrose pseudoinverse; extensions to directed networks are designated as open directions for future research.
