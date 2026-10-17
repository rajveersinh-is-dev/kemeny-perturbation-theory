"""Investigate the distribution of the four topological regimes and weight-induced Braess transitions.

Author: Rajveersinh Vishal Pardeshi
Affiliation: Independent Researcher
"""

from __future__ import annotations

import json
import os
import sys
from typing import Dict, List

import networkx as nx
import numpy as np

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.kemeny_perturbation import EdgeRegime, KemenyPerturbationEngine


def analyze_regime_distribution() -> Dict[str, object]:
    """Examine the prevalence of each regime across graph topologies and real networks."""
    topologies: Dict[str, nx.Graph] = {}

    # 1. Random Tree (n=30)
    T = nx.random_labeled_tree(30, seed=42)
    topologies["Random Tree (n=30)"] = T

    # 2. Barbell Graph (5, 4)
    BB = nx.barbell_graph(6, 4)
    topologies["Barbell Network (n=16)"] = BB

    # 3. Erdős–Rényi Random Graph (n=30, p=0.15)
    ER = nx.erdos_renyi_graph(30, 0.15, seed=42)
    while not nx.is_connected(ER):
        ER = nx.erdos_renyi_graph(30, 0.15)
    topologies["Erdős–Rényi (n=30, p=0.15)"] = ER

    # 4. Barabási–Albert Scale-Free (n=30, m=2)
    BA = nx.barabasi_albert_graph(30, 2, seed=42)
    topologies["Scale-Free Barabási–Albert (n=30)"] = BA

    # 5. Watts–Strogatz Small-World (n=30, k=4, p=0.2)
    WS = nx.watts_strogatz_graph(30, 4, 0.2, seed=42)
    topologies["Small-World Watts–Strogatz (n=30)"] = WS

    # 6. Real Network: Zachary's Karate Club (n=34)
    topologies["Zachary Karate Club (n=34)"] = nx.karate_club_graph()

    # 7. Real Network: Florentine Families (n=15)
    FF = nx.florentine_families_graph()
    largest_cc = max(nx.connected_components(FF), key=len)
    topologies["Florentine Families (n=15)"] = nx.convert_node_labels_to_integers(FF.subgraph(largest_cc))

    regime_results = {}

    for name, G in topologies.items():
        n = G.number_of_nodes()
        A = nx.to_numpy_array(G, nodelist=range(n))
        engine = KemenyPerturbationEngine(A)

        non_edges = list(nx.non_edges(G))
        total_non_edges = len(non_edges)

        regime_counts = {
            EdgeRegime.GLOBALLY_FAVORABLE.value: 0,
            EdgeRegime.GLOBALLY_BRAESS.value: 0,
            EdgeRegime.WEIGHT_INDUCED_BRAESS.value: 0,
            EdgeRegime.CAPACITY_ACTIVATED_FAVORABLE.value: 0,
            EdgeRegime.NEUTRAL.value: 0,
        }

        critical_weights: List[float] = []

        for u, v in non_edges:
            res = engine.analyze_edge_regime(u, v)
            regime_counts[res["regime"]] += 1
            if res["critical_weight"] is not None:
                critical_weights.append(res["critical_weight"])

        regime_results[name] = {
            "n": n,
            "edges": G.number_of_edges(),
            "total_non_edges": total_non_edges,
            "kemeny_constant": engine.kemeny_constant,
            "regime_counts": regime_counts,
            "regime_percentages": {
                k: (v / total_non_edges * 100.0) if total_non_edges > 0 else 0.0
                for k, v in regime_counts.items()
            },
            "mean_critical_weight": float(np.mean(critical_weights)) if critical_weights else None,
            "min_critical_weight": float(np.min(critical_weights)) if critical_weights else None,
            "max_critical_weight": float(np.max(critical_weights)) if critical_weights else None,
        }

    # Specifically study the Weight-Induced Braess curve on the 5-node canonical example
    G_canon = nx.erdos_renyi_graph(5, 0.4, seed=1)
    A_canon = nx.to_numpy_array(G_canon, nodelist=range(5))
    engine_canon = KemenyPerturbationEngine(A_canon)
    u_c, v_c = 1, 2
    res_canon = engine_canon.analyze_edge_regime(u_c, v_c)

    # Sweep weights from 1e-2 to 1e2 across 100 log-spaced points
    w_values = np.logspace(-2, 2, 100)
    dK_curve: List[Dict[str, float]] = []
    for w in w_values:
        dK_val = engine_canon.compute_edge_perturbation_algebraic(u_c, v_c, float(w))
        dK_curve.append({"w": float(w), "delta_K": float(dK_val)})

    output_data = {
        "regime_breakdown": regime_results,
        "canonical_transition": {
            "edges": list(G_canon.edges()),
            "pair": [u_c, v_c],
            "A0": res_canon["A0"],
            "A1": res_canon["A1"],
            "critical_weight": res_canon["critical_weight"],
            "optimal_weight": res_canon["optimal_weight"],
            "infinitesimal_derivative": res_canon["infinitesimal_derivative"],
            "asymptotic_delta_k": res_canon["asymptotic_delta_k"],
            "dK_curve": dK_curve,
        },
    }

    os.makedirs("results", exist_ok=True)
    with open("results/phase_transition_data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print("Regime breakdown and phase transition data saved to results/phase_transition_data.json")
    return output_data


if __name__ == "__main__":
    analyze_regime_distribution()
