import json
import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.kemeny_perturbation import KemenyPerturbationEngine

# Publication-quality matplotlib styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
mpl.rcParams["font.family"] = "serif"
mpl.rcParams["font.size"] = 11
mpl.rcParams["axes.labelsize"] = 12
mpl.rcParams["axes.titlesize"] = 13
mpl.rcParams["xtick.labelsize"] = 10
mpl.rcParams["ytick.labelsize"] = 10
mpl.rcParams["legend.fontsize"] = 10
mpl.rcParams["figure.titlesize"] = 14
mpl.rcParams["lines.linewidth"] = 2
mpl.rcParams["lines.markersize"] = 6

os.makedirs("figures", exist_ok=True)

@dataclass
class PhaseTransitionData:
    w_vals: List[float]
    dK_vals: List[float]
    w_crit: float
    w_opt: float
    asymp: float

@dataclass
class BenchmarkData:
    n: int
    mean_all_pairs_sec: float
    std_all_pairs_sec: float
    mean_brute_force_sec: Optional[float]
    std_brute_force_sec: Optional[float]
    speedup: Optional[float]

@dataclass
class RegimeData:
    name: str
    favorable: float
    braess: float
    weight_induced: float

@dataclass
class KarateClubData:
    G: nx.Graph
    dK_matrix: np.ndarray
    top_favorable: List[Tuple[int, int]]
    top_braess: List[Tuple[int, int]]
    kemeny_constant: float


def load_phase_transition_data() -> PhaseTransitionData:
    """Load phase transition data from JSON file."""
    with open("results/phase_transition_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)["canonical_transition"]

    w_vals = [pt["w"] for pt in data["dK_curve"]]
    dK_vals = [pt["delta_K"] for pt in data["dK_curve"]]
    w_crit = data["critical_weight"]
    w_opt = data["optimal_weight"]
    asymp = data["asymptotic_delta_k"]

    return PhaseTransitionData(w_vals, dK_vals, w_crit, w_opt, asymp)


def load_benchmark_data() -> List[BenchmarkData]:
    """Load benchmark data from JSON file."""
    with open("results/benchmark_timings.json", "r", encoding="utf-8") as f:
        benchmarks = json.load(f)

    benchmark_data = []
    for b in benchmarks:
        benchmark_data.append(
            BenchmarkData(
                n=b["n"],
                mean_all_pairs_sec=b["mean_all_pairs_sec"],
                std_all_pairs_sec=b["std_all_pairs_sec"],
                mean_brute_force_sec=b.get("mean_brute_force_sec"),
                std_brute_force_sec=b.get("std_brute_force_sec"),
                speedup=b.get("speedup"),
            )
        )

    return benchmark_data


def load_regime_data() -> List[RegimeData]:
    """Load regime data from JSON file."""
    with open("results/phase_transition_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)["regime_breakdown"]

    regime_data = []
    for name, info in data.items():
        clean_name = name.split("(")[0].strip()
        pcts = info["regime_percentages"]
        regime_data.append(
            RegimeData(
                name=clean_name,
                favorable=pcts.get("Globally Favorable", 0.0),
                braess=pcts.get("Globally Braess", 0.0),
                weight_induced=pcts.get("Weight-Induced Braess", 0.0),
            )
        )

    return regime_data


def load_karate_club_data() -> KarateClubData:
    """Load and analyze Zachary's Karate Club data."""
    G = nx.karate_club_graph()
    A = nx.to_numpy_array(G)
    engine = KemenyPerturbationEngine(A)
    all_pairs = engine.all_pairs_kemeny_analysis(w=1.0)
    dK_matrix = all_pairs["delta_K"]

    non_edges = list(nx.non_edges(G))
    ranked_non_edges = sorted(non_edges, key=lambda pair: dK_matrix[pair[0], pair[1]])

    top_favorable = ranked_non_edges[:5]
    top_braess = ranked_non_edges[-5:]

    return KarateClubData(
        G=G,
        dK_matrix=dK_matrix,
        top_favorable=top_favorable,
        top_braess=top_braess,
        kemeny_constant=engine.kemeny_constant,
    )


def plot_fig1_phase_transition(data: PhaseTransitionData) -> None:
    """Figure 1: Weight-Induced Braess Phase Transition and Critical Threshold."""
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)

    # Plot Delta K curve
    ax.plot(data.w_vals, data.dK_vals, color="#1f77b4", label=r"Exact Perturbation $\Delta K(w)$", lw=2.5)

    # Horizontal zero line
    ax.axhline(0, color="gray", linestyle="--", lw=1.2, alpha=0.7)

    # Critical weight threshold w*
    ax.axvline(data.w_crit, color="#d62728", linestyle=":", lw=2, label=rf"Critical Threshold $w^* = {data.w_crit:.2f}$")
    ax.plot([data.w_crit], [0], marker="o", markersize=8, color="#d62728")

    # Optimal weight w_opt
    min_dK = min(data.dK_vals)
    ax.plot([data.w_opt], [min_dK], marker="s", markersize=8, color="#2ca02c", label=rf"Optimal Weight $w_{{\mathrm{{opt}}}} = {data.w_opt:.2f}$")

    # Asymptotic limit
    ax.axhline(data.asymp, color="#9467bd", linestyle="-\.", lw=1.5, alpha=0.8, label=rf"Asymptotic Limit $w \to \infty$ (${data.asymp:.2f}$)")

    # Color background regions
    ax.axvspan(min(data.w_vals), data.w_crit, color="#2ca02c", alpha=0.08, label=r"Favorable Regime ($\Delta K < 0$)")
    ax.axvspan(data.w_crit, max(data.w_vals), color="#d62728", alpha=0.08, label=r"Braess Paradox Regime ($\Delta K > 0$)")

    ax.set_xscale("log")
    ax.set_xlabel(r"Edge Perturbation Weight $w$ (log scale)")
    ax.set_ylabel(r"Change in Kemeny's Constant $\Delta K(G; u, v, w)$")
    ax.set_title(r"Weight-Induced Braess Phase Transition on $G = (V, E)$")
    ax.legend(loc="lower right", frameon=True, framealpha=0.9)
    plt.tight_layout()

    fig.savefig("figures/fig1_phase_transition_curves.pdf")
    fig.savefig("figures/fig1_phase_transition_curves.png")
    plt.close(fig)
    print("Figure 1 generated: figures/fig1_phase_transition_curves.pdf and .png")


def plot_fig2_all_pairs_scaling(data: List[BenchmarkData]) -> None:
    """Figure 2: Computational scaling comparison between Naive O(n^5) and Exact O(n^3) algorithm."""
    ns = [b.n for b in data]
    all_pairs_times = [b.mean_all_pairs_sec for b in data]
    all_pairs_err = [b.std_all_pairs_sec for b in data]

    bf_ns = [b.n for b in data if b.mean_brute_force_sec is not None]
    bf_times = [b.mean_brute_force_sec for b in data if b.mean_brute_force_sec is not None]
    bf_err = [b.std_brute_force_sec for b in data if b.mean_brute_force_sec is not None]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)

    # Plot 1: Runtime scaling on log-log axes
    ax1.errorbar(bf_ns, bf_times, yerr=bf_err, fmt="o-", color="#d62728", label=r"Brute-Force $\mathcal{O}(n^5)$", lw=2, capsize=4)
    ax1.errorbar(ns, all_pairs_times, yerr=all_pairs_err, fmt="s-", color="#1f77b4", label=r"Exact All-Pairs $\mathcal{O}(n^3)$ [Ours]", lw=2, capsize=4)

    # Reference slope lines
    n_ref = np.array([20, 50, 100])
    ax1.plot(n_ref, 1e-7 * (n_ref**3), "--", color="#1f77b4", alpha=0.5, label=r"$\mathcal{O}(n^3)$ reference slope")
    ax1.plot(bf_ns, 1e-7 * (np.array(bf_ns)**5) * (bf_times[0] / (1e-7 * (bf_ns[0]**5))), "--", color="#d62728", alpha=0.5, label=r"$\mathcal{O}(n^5)$ reference slope")

    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xlabel(r"Number of Graph Vertices $n$")
    ax1.set_ylabel(r"Wall-Clock Execution Time (seconds)")
    ax1.set_title("All-Pairs Kemeny Computation Runtime")
    ax1.legend(loc="upper left", frameon=True)

    # Plot 2: Speedup factor
    speedups = [b.speedup for b in data if b.speedup is not None]
    ax2.plot(bf_ns, speedups, "d-", color="#2ca02c", lw=2.5, markersize=7)
    ax2.set_yscale("log")
    ax2.set_xlabel(r"Number of Graph Vertices $n$")
    ax2.set_ylabel(r"Empirical Speedup Factor ($\\times$)")
    ax2.set_title(r"Speedup: Brute-Force / Exact $\mathcal{O}(n^3)$")
    for x, y in zip(bf_ns, speedups):
        if x in [10, 20, 50]:
            ax2.annotate(f"{y:,.0f}x", (x, y), textcoords="offset points", xytext=(0, 8), ha="center", fontweight="bold")

    plt.tight_layout()
    fig.savefig("figures/fig2_all_pairs_scaling.pdf")
    fig.savefig("figures/fig2_all_pairs_scaling.png")
    plt.close(fig)
    print("Figure 2 generated: figures/fig2_all_pairs_scaling.pdf and .png")


def plot_fig3_regime_distribution(data: List[RegimeData]) -> None:
    """Figure 3: Distribution of edge regimes across diverse network topologies."""
    labels = [d.name for d in data]
    favorable = [d.favorable for d in data]
    braess = [d.braess for d in data]
    weight_induced = [d.weight_induced for d in data]

    x = np.arange(len(labels))
    width = 0.55

    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=300)

    p1 = ax.bar(x, favorable, width, label=r"Globally Favorable ($\Delta K < 0, \\forall w$)", color="#2ca02c")
    p2 = ax.bar(x, weight_induced, width, bottom=favorable, label=r"Weight-Induced Braess ($\Delta K < 0$ for $w < w^*$, $> 0$ for $w > w^*$)", color="#ff7f0e")
    bottom_braess = np.array(favorable) + np.array(weight_induced)
    p3 = ax.bar(x, braess, width, bottom=bottom_braess, label=r"Globally Braess ($\Delta K > 0, \\forall w$)", color="#d62728")

    ax.set_ylabel("Proportion of Non-Edges (%)")
    ax.set_title("Prevalence of Edge Regimes Across Network Topologies")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylim(0, 105)
    ax.legend(loc="upper right", frameon=True, framealpha=0.9)

    plt.tight_layout()
    fig.savefig("figures/fig3_regime_distribution.pdf")
    fig.savefig("figures/fig3_regime_distribution.png")
    plt.close(fig)
    print("Figure 3 generated: figures/fig3_regime_distribution.pdf and .png")


def plot_fig4_karate_club(data: KarateClubData) -> None:
    """Figure 4: Zachary's Karate Club network optimization and Braess edge visualization."""
    pos = nx.spring_layout(data.G, seed=42)

    fig, ax = plt.subplots(figsize=(8, 6.5), dpi=300)

    # Draw existing edges
    nx.draw_networkx_edges(data.G, pos, ax=ax, edge_color="#bdc3c7", width=1.5, alpha=0.7)

    fav_min = data.dK_matrix[data.top_favorable[0][0], data.top_favorable[0][1]]
    fav_max = data.dK_matrix[data.top_favorable[-1][0], data.top_favorable[-1][1]]
    braess_min = data.dK_matrix[data.top_braess[0][0], data.top_braess[0][1]]
    braess_max = data.dK_matrix[data.top_braess[-1][0], data.top_braess[-1][1]]

    # Draw top favorable edges (green solid)
    nx.draw_networkx_edges(
        data.G, pos, edgelist=data.top_favorable, ax=ax,
        edge_color="#2ca02c", width=3.0, alpha=0.9, style="solid",
        label=rf"Top 5 Favorable Edges ($\\Delta K \\in [{fav_min:.2f}, {fav_max:.2f}]$)"
    )

    # Draw top Braess edges (red dashed)
    nx.draw_networkx_edges(
        data.G, pos, edgelist=data.top_braess, ax=ax,
        edge_color="#d62728", width=3.0, alpha=0.9, style="dashed",
        label=rf"Top 5 Braess Edges ($\\Delta K \\in [{braess_min:.2f}, {braess_max:.2f}]$)"
    )

    # Draw nodes
    nx.draw_networkx_nodes(data.G, pos, ax=ax, node_color="#34495e", node_size=280, alpha=0.95)
    nx.draw_networkx_labels(data.G, pos, ax=ax, font_size=8, font_color="white", font_weight="bold")

    ax.set_title(f"Zachary's Karate Club ($n=34, m=78$): Optimal Additions vs Braess Bottlenecks\\nBase Kemeny Constant $K(G) = {data.kemeny_constant:.2f}$")
    ax.legend(loc="upper left", frameon=True, framealpha=0.9)
    ax.axis("off")

    plt.tight_layout()
    fig.savefig("figures/fig4_karate_club_optimization.pdf")
    fig.savefig("figures/fig4_karate_club_optimization.png")
    plt.close(fig)
    print("Figure 4 generated: figures/fig4_karate_club_optimization.pdf and .png")


def main() -> None:
    """Generate all figures."""
    phase_transition_data = load_phase_transition_data()
    benchmark_data = load_benchmark_data()
    regime_data = load_regime_data()
    karate_club_data = load_karate_club_data()

    plot_fig1_phase_transition(phase_transition_data)
    plot_fig2_all_pairs_scaling(benchmark_data)
    plot_fig3_regime_distribution(regime_data)
    plot_fig4_karate_club(karate_club_data)


if __name__ == "__main__":
    main()
