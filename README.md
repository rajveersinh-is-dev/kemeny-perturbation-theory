# Exact Rational Perturbation Theory and Braess Phase Transitions for Kemeny's Constant in Complex Networks

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![arXiv](https://img.shields.io/badge/arXiv-Preprint-b31b1b.svg)](https://github.com/rajveersinh-is-dev/kemeny-perturbation-theory/tree/main/paper)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/rajveersinh-is-dev/kemeny-perturbation-theory/actions)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23572394.svg)](https://doi.org/10.5281/zenodo.23572394)

**Author:** Rajveersinh Vishal Pardeshi  
**Affiliation:** Independent Researcher  
**DOI:** [10.5281/zenodo.23572394](https://doi.org/10.5281/zenodo.23572394)  
**Target Journal:** *Information and Inference: A Journal of the IMA* (Oxford University Press)  
**Publishing Route:** Standard Subscription License (Verified zero mandatory author publication fee)

---

## Overview

In complex networks and Markov chains, **Kemeny's constant** $K(G)$ measures the average expected transit time between random states. Unlike electrical resistance networks—where adding edges strictly decreases total resistance (Rayleigh's Monotonicity Law)—random walks can exhibit **Braess's paradox**: adding a link can paradoxically \textit{increase} Kemeny's constant, worsening global network transit efficiency.

This repository provides the complete, mathematically proven, and computationally verified implementation of the **Exact Rational Perturbation Theory of Kemeny's Constant** under finite, continuous edge modifications ($w > 0$) for arbitrary finite, connected, undirected weighted graphs.

### Key Theoretical Contributions
1. **Exact Rational Perturbation Formula (Theorem 1):** For any connected graph $G$ and vertex pair $(u, v)$ with perturbation weight $w > 0$, the change in Kemeny's constant is an exact rational function:
   $$\Delta K(G; u, v, w) = \frac{w (A_0 + A_1 w)}{2m(m + w)(1 + w \Omega(u, v))}$$
   where $\Omega(u, v)$ is the effective resistance and $2m$ is the graph volume.
2. **Exact Algebraic Cancellation Theorem (Theorem 2):** The quadratic numerator coefficient $A_2$ vanishes identically ($A_2 \equiv 0$) across all graphs and vertex pairs due to an underlying $2 \times 2$ principal submatrix determinant identity of the Laplacian pseudoinverse $L^\dagger$.
3. **Weight-Induced Braess Phase Transitions (Theorem 3):** Discovery and characterization of candidate links that are *strictly favorable* for small capacities ($w < w^*$) but become *Braess bottlenecks* for large capacities ($w > w^*$), with an exact closed-form threshold $w^*(u, v) = -A_0 / A_1$.
4. **Optimal Finite Capacity (Theorem 4):** Proof of a unique interior capacity $w_{\mathrm{opt}} \in (0, w^*)$ that achieves the maximum possible reduction in Kemeny's constant for weight-induced Braess edges.
5. **Fast Deterministic All-Pairs Algorithm (Theorem 5):** Using the precomputed metric matrix $M = L^\dagger D L^\dagger$, all scalar coefficients $A_0(u, v)$ and $A_1(u, v)$ are evaluated in $\mathcal{O}(1)$ time per pair. Evaluating all $\binom{n}{2}$ candidate edge modifications requires $\mathcal{O}(n^3)$ precomputation plus $\mathcal{O}(n^2)$ total query time, achieving an $n^2$ speedup over the naive $\mathcal{O}(n^5)$ recomputation.

---

## Status of Findings

- **Mathematical Proofs:** Verified deductively from first principles and symbolically confirmed down to floating-point epsilon ($< 10^{-12}$) across 100 random graph configurations.
- **Empirical Benchmarks:** In-process hardware performance counter measurements confirm speedups exceeding **$13,000\times$** at $n = 50$ vertices (140 $\mu$s vs 1.84 s).
- **Topology Audits:** Audited across seven network families; reveals that the Weight-Induced Braess regime is prevalent in sparse and modular networks ($70.2\%$ in random trees, $28.2\%$ in barbell graphs).
- **Publication Status:** Independent research preprint; submitted and formatted for *Information and Inference: A Journal of the IMA* (Oxford University Press) under the standard subscription route (zero author publication fee).

---

## Repository Structure

```
.
├── src/
│   ├── __init__.py
│   └── kemeny_perturbation.py     # Core mathematical engine and vectorized all-pairs analyzer
├── tests/
│   └── test_kemeny_perturbation.py # Comprehensive PyTest suite (100% passing)
├── experiments/
│   ├── run_benchmarks.py          # Real in-process wall-clock timing benchmark suite
│   ├── run_phase_transitions.py   # Topological regime distribution and phase transition sweep
│   └── generate_figures.py        # Publication-quality figure generation
├── results/
│   ├── benchmark_timings.json     # Measured timing data with mean and std over 10 trials
│   ├── benchmark_timings.csv      # CSV export of scaling benchmarks
│   └── phase_transition_data.json # Detailed regime breakdowns across 7 network models
├── figures/
│   ├── fig1_phase_transition_curves.pdf / .png
│   ├── fig2_all_pairs_scaling.pdf / .png
│   ├── fig3_regime_distribution.pdf / .png
│   └── fig4_karate_club_optimization.pdf / .png
├── paper/
│   ├── main.tex                   # Complete LaTeX manuscript
│   ├── main.pdf                   # Compiled 14-page publication-quality PDF
│   ├── references.bib             # Verified BibTeX citations with DOIs
│   └── README.md                  # Compilation instructions
├── research/
│   ├── candidate_discovery.md     # 10-candidate survey and 100-point rubric ranking
│   ├── literature_review.md       # Primary sources and comparative literature table
│   ├── novelty_assessment.md      # Formal novelty classification and claim boundaries
│   ├── research_spec.md           # 10-point research specification
│   ├── evidence_ledger.md         # Comprehensive claim-by-claim verification ledger
│   ├── hostile_review.md          # Adversarial peer reviews (technical & significance)
│   ├── journal_selection.md       # OUP journal fee and self-archiving policy verification
│   ├── acceptance_assessment.md   # Qualitative and empirical acceptance feasibility
│   └── limitations.md             # Theoretical and computational limitations
├── requirements.txt
├── environment.yml
├── CITATION.cff
├── LICENSE
└── README.md
```

---

## Installation and Quick Start

### Prerequisites
- Python 3.10+
- NumPy, SciPy, NetworkX, Matplotlib

### Setup
```bash
git clone https://github.com/rajveersinh-is-dev/kemeny-perturbation-theory.git
cd kemeny-perturbation-theory
pip install -r requirements.txt
```

### Quick Python Example
```python
import networkx as nx
from src.kemeny_perturbation import KemenyPerturbationEngine

# Load Zachary's Karate Club network (n=34, m=78)
G = nx.karate_club_graph()
A = nx.to_numpy_array(G)

# Initialize perturbation engine
engine = KemenyPerturbationEngine(A)
print(f"Base Kemeny constant: {engine.kemeny_constant:.4f}")

# Analyze specific candidate non-edge (node 1, node 2)
regime_info = engine.analyze_edge_regime(1, 2)
print("Regime:", regime_info["regime"])
print("Critical Weight w*:", regime_info["critical_weight"])

# Compute exact all-pairs perturbation matrix in milliseconds
all_pairs = engine.all_pairs_kemeny_analysis(w=1.0)
print("Fastest mixing link to add:", np.unravel_index(np.argmin(all_pairs["delta_K"]), all_pairs["delta_K"].shape))
```

---

## Reproducing Experiments and Running Tests

### Running the Test Suite
```bash
python -m pytest tests/test_kemeny_perturbation.py -v
```

### Reproducing Benchmark Runtimes
```bash
python experiments/run_benchmarks.py
```

### Reproducing Regime Analysis and Figure Generation
```bash
python experiments/run_phase_transitions.py
python experiments/generate_figures.py
```

### Compiling the Manuscript PDF
```bash
cd paper
tectonic main.tex
```

---

## Known Limitations

1. **Undirected Networks:** The exact algebraic cancellation $A_2 \equiv 0$ relies on the symmetry of the graph Laplacian $L$ and its Moore-Penrose pseudoinverse $L^\dagger$. Extension to asymmetric directed graphs is designated as future work.
2. **Connected Graphs Only:** Kemeny's constant is defined for irreducible chains; adding an edge between disconnected components results in a discontinuous jump from infinity to a finite scalar.
3. **Single Edge Modifications:** The exact linear numerator $N(w) = A_0 + A_1 w$ applies to single rank-one edge modifications. Concurrent multi-edge additions ($k \ge 2$) yield multivariate rational functions via the Woodbury matrix formula.

---

## Citation

If you find this work or software useful in your research, please cite the archived preprint:

**DOI:** [10.5281/zenodo.23572394](https://doi.org/10.5281/zenodo.23572394)

```bibtex
@article{pardeshi2026exact,
  author    = {Rajveersinh Vishal Pardeshi},
  title     = {Exact Rational Perturbation Theory, Monotonicity Phase Transitions, and Fast All-Pairs Optimization for {K}emeny's Constant in Complex Networks},
  journal   = {Preprint},
  year      = {2026},
  doi       = {10.5281/zenodo.23572394},
  url       = {https://doi.org/10.5281/zenodo.23572394}
}
```

---

## License

This software and code are licensed under the [MIT License](LICENSE).  
The manuscript text and research documentation are licensed under the [Creative Commons Attribution 4.0 International License (CC-BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
