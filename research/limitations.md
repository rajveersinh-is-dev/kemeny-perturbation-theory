# Research Limitations and Scope Delimitation

This document provides a candid disclosure of the theoretical, algorithmic, and empirical limitations of this research.

---

## 1. Mathematical and Theoretical Limitations

1. **Undirected Graphs Only:**
   The theorems and algebraic cancellations established in this work rely fundamentally on the symmetry of the graph Laplacian $L = D - W$ and its Moore-Penrose pseudoinverse $L^\dagger$. For directed graphs, the transition matrix $P$ and directed Laplacian $L_{\text{dir}}$ are asymmetric. While the group inverse $(I - P)^\#$ can still be updated via general Sherman-Morrison formulas, the left and right eigenvectors diverge, and the compact cancellation $A_2 \equiv 0$ derived from symmetric $2 \times 2$ submatrix determinants cannot be directly assumed without substantial generalization.

2. **Connected Graphs Only:**
   Kemeny's constant is defined for irreducible Markov chains. If a graph is disconnected, random walk transit times between disconnected components are infinite ($K(G) = \infty$). When adding an edge between two previously disconnected components, Kemeny's constant transitions from infinity to a finite scalar; this discontinuous topological transition cannot be modeled as a continuous rational function on $\mathbb{R}_{>0}$.

3. **Single Rank-One Perturbation (Single Edge Modification):**
   Our closed-form rational formula applies to rank-one updates corresponding to single edge additions or weight adjustments between node pairs $(u, v)$. Simultaneously adding or modifying $k \ge 2$ independent edges constitutes a rank-$k$ update. By the Woodbury matrix identity, this yields a multivariate rational function with multilinear numerator and denominator polynomials of degree $k$, which cannot be reduced to the univariate linear numerator $A_0 + A_1 w$.

---

## 2. Algorithmic and Computational Limitations

1. **Dense Matrix Multiplication in Precomputation:**
   The all-pairs algorithm achieves $\mathcal{O}(n^3)$ precomputation time by constructing the auxiliary matrix $M = L^\dagger D L^\dagger$. For dense graphs or moderate graph sizes ($n \le 5,000$), this precomputation is virtually instantaneous on modern multi-core CPUs/GPUs. However, for massive web-scale networks ($n \ge 10^6$), materializing dense $n \times n$ matrices $L^\dagger$ and $M$ in RAM requires terabytes of memory.
2. **Extensions to Approximate Sketching:**
   For ultra-large graphs, fast Laplacian solvers (Spielman-Teng, Koutis-Miller-Peng) approximate effective resistances $\Omega(u, v)$ in $\tilde{\mathcal{O}}(m \epsilon^{-2})$ time via Johnson-Lindenstrauss random projections. Adapting our exact formula to sketched approximations introduces bounded approximation errors $\epsilon$ into $A_0$ and $A_1$, which may shift the estimated critical threshold $w^*$.

---

## 3. Empirical Limitations

1. **Topology Sensitivity:**
   Our empirical findings show that the prevalence of the Weight-Induced Braess regime is highly topology-dependent: it dominates in trees ($70.2\%$) and modular barbell networks ($28.2\%$), but is rare in dense scale-free networks ($0.5\%$). Practitioners cannot assume a uniform prevalence across arbitrary domain graphs without executing the all-pairs diagnostic.
2. **Static Network Assumption:**
   The analysis assumes static network topology and fixed transition rates. In dynamic, time-varying networks where node degrees fluctuate continuously, the optimal weight $w_{\text{opt}}$ may drift over time.
