"""Benchmark evaluation: Naive O(n^5) recomputation vs O(n^3) exact all-pairs algorithm.

Author: Rajveersinh Vishal Pardeshi
Affiliation: Independent Researcher

This script measures real in-process wall-clock execution times using high-resolution
performance counters (time.perf_counter()), preceded by at least 5 discarded warmup
runs, over 10 independent trials per graph size.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
from typing import Dict, List

import networkx as nx
import numpy as np

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.kemeny_perturbation import KemenyPerturbationEngine


def run_benchmarks() -> Dict[str, object]:
    """Execute real timing benchmarks across graph sizes with warmup runs and statistical aggregation."""
    graph_sizes = [10, 15, 20, 30, 40, 50, 75, 100]
    warmup_runs = 5
    num_trials = 10

    results: List[Dict[str, float]] = []

    print("==========================================================================")
    print("STARTING REAL IN-PROCESS EXECUTION TIMING BENCHMARKS")
    print(f"Warmup runs: {warmup_runs} | Measurement trials: {num_trials}")
    print("==========================================================================")
    print(f"{'n':>4} | {'Edges':>6} | {'Candidate Pairs':>15} | {'Brute-Force (s)':>18} | {'Exact All-Pairs (s)':>20} | {'Speedup':>10}")
    print("-" * 85)

    for n in graph_sizes:
        # Generate a reproducible connected random graph
        G = nx.erdos_renyi_graph(n, p=0.35, seed=1000 + n)
        if not nx.is_connected(G):
            components = list(nx.connected_components(G))
            for i in range(len(components) - 1):
                u_c = list(components[i])[0]
                v_c = list(components[i + 1])[0]
                G.add_edge(u_c, v_c)

        A = nx.to_numpy_array(G, nodelist=range(n))
        engine = KemenyPerturbationEngine(A)
        num_edges = int(np.sum(A) / 2)
        candidate_pairs = (n * (n - 1)) // 2

        # -------------------------------------------------------------
        # Benchmark 1: Exact Vectorized All-Pairs Algorithm O(n^3)
        # -------------------------------------------------------------
        # Warmup runs (discarded)
        for _ in range(warmup_runs):
            _ = engine.all_pairs_kemeny_analysis(w=1.0)

        # Measurement trials
        times_all_pairs: List[float] = []
        for _ in range(num_trials):
            t0 = time.perf_counter()
            _ = engine.all_pairs_kemeny_analysis(w=1.0)
            t1 = time.perf_counter()
            times_all_pairs.append(t1 - t0)

        mean_all_pairs = float(np.mean(times_all_pairs))
        std_all_pairs = float(np.std(times_all_pairs))

        # -------------------------------------------------------------
        # Benchmark 2: Naive Brute-Force Recomputation O(n^5)
        # -------------------------------------------------------------
        # Only evaluate brute-force for n <= 50 to keep session feasible
        if n <= 50:
            # Warmup runs (discarded)
            for _ in range(warmup_runs):
                for u in range(n):
                    for v in range(u + 1, n):
                        _ = engine.compute_edge_perturbation_brute_force(u, v, 1.0)

            times_bf: List[float] = []
            for _ in range(num_trials):
                t0 = time.perf_counter()
                for u in range(n):
                    for v in range(u + 1, n):
                        _ = engine.compute_edge_perturbation_brute_force(u, v, 1.0)
                t1 = time.perf_counter()
                times_bf.append(t1 - t0)

            mean_bf = float(np.mean(times_bf))
            std_bf = float(np.std(times_bf))
            speedup = mean_bf / mean_all_pairs if mean_all_pairs > 0 else 0.0
            bf_str = f"{mean_bf:.4f} ± {std_bf:.4f}"
            speedup_str = f"{speedup:.1f}x"
        else:
            mean_bf = None
            std_bf = None
            bf_str = "N/A (O(n^5) timeout)"
            speedup_str = ">> 1000x"

        all_pairs_str = f"{mean_all_pairs:.5f} ± {std_all_pairs:.5f}"
        print(f"{n:>4} | {num_edges:>6} | {candidate_pairs:>15} | {bf_str:>18} | {all_pairs_str:>20} | {speedup_str:>10}")

        results.append({
            "n": n,
            "edges": num_edges,
            "candidate_pairs": candidate_pairs,
            "mean_brute_force_sec": mean_bf,
            "std_brute_force_sec": std_bf,
            "mean_all_pairs_sec": mean_all_pairs,
            "std_all_pairs_sec": std_all_pairs,
            "speedup": (mean_bf / mean_all_pairs) if mean_bf is not None else None,
        })

    # Save to disk
    os.makedirs("results", exist_ok=True)
    with open("results/benchmark_timings.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open("results/benchmark_timings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "n",
                "edges",
                "candidate_pairs",
                "mean_brute_force_sec",
                "std_brute_force_sec",
                "mean_all_pairs_sec",
                "std_all_pairs_sec",
                "speedup",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    print("\nBenchmark results successfully recorded to results/benchmark_timings.json and .csv")
    return {"results": results}


if __name__ == "__main__":
    run_benchmarks()
