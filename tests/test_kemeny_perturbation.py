"""Comprehensive unit tests and mathematical verification suite for Kemeny perturbation theory.

Author: Rajveersinh Vishal Pardeshi
Affiliation: Independent Researcher
"""

import math
import networkx as nx
import numpy as np
import pytest

from src.kemeny_perturbation import EdgeRegime, KemenyPerturbationEngine


def test_three_kemeny_formulations_equivalence():
    """Verify that Laplacian pseudoinverse, spectral, and hitting time formulas yield identical Kemeny constants."""
    # Test on a path graph of 5 nodes
    G = nx.path_graph(5)
    A = nx.to_numpy_array(G)

    engine = KemenyPerturbationEngine(A)
    K_pinv = engine.kemeny_constant
    K_spec = KemenyPerturbationEngine.compute_kemeny_spectral(A)
    K_hit, H = KemenyPerturbationEngine.compute_kemeny_hitting_times(A)

    assert math.isclose(K_pinv, K_spec, rel_tol=1e-12, abs_tol=1e-12)
    assert math.isclose(K_pinv, K_hit, rel_tol=1e-12, abs_tol=1e-12)

    # Test on a barbell graph
    G_barbell = nx.barbell_graph(4, 2)
    A_bb = nx.to_numpy_array(G_barbell)
    engine_bb = KemenyPerturbationEngine(A_bb)
    assert math.isclose(
        engine_bb.kemeny_constant,
        KemenyPerturbationEngine.compute_kemeny_spectral(A_bb),
        rel_tol=1e-12,
    )
    K_hit_bb, _ = KemenyPerturbationEngine.compute_kemeny_hitting_times(A_bb)
    assert math.isclose(engine_bb.kemeny_constant, K_hit_bb, rel_tol=1e-12)


def test_exact_algebraic_formula_vs_brute_force():
    """Verify Theorem 1: algebraic rational formula matches brute force recomputation down to machine precision."""
    # Generate 15 random connected graphs of varying densities and sizes
    for seed in range(15):
        n = 5 + (seed % 6)
        p = 0.35 + 0.05 * (seed % 5)
        G = nx.erdos_renyi_graph(n, p, seed=seed)
        if not nx.is_connected(G):
            # Add minimal edges to connect
            components = list(nx.connected_components(G))
            for i in range(len(components) - 1):
                u = list(components[i])[0]
                v = list(components[i + 1])[0]
                G.add_edge(u, v)

        A = nx.to_numpy_array(G)
        engine = KemenyPerturbationEngine(A)
        non_edges = list(nx.non_edges(G))
        if not non_edges:
            continue

        for u, v in non_edges[:3]:
            for w in [0.001, 0.1, 1.0, 5.0, 25.0]:
                dK_bf = engine.compute_edge_perturbation_brute_force(u, v, w)
                dK_alg = engine.compute_edge_perturbation_algebraic(u, v, w)
                diff = abs(dK_bf - dK_alg)
                assert diff < 1e-11, f"Seed {seed}, pair ({u}, {v}), w={w}: diff={diff} exceeds 1e-11"


def test_quadratic_coefficient_cancellation():
    """Verify Theorem 2: quadratic numerator term A2 is identically zero for all graphs and vertex pairs."""
    for seed in range(10):
        n = 6
        G = nx.erdos_renyi_graph(n, 0.45, seed=seed)
        if not nx.is_connected(G):
            continue
        A = nx.to_numpy_array(G)
        engine = KemenyPerturbationEngine(A)
        for u in range(n):
            for v in range(u + 1, n):
                invs = engine.get_pair_invariants(u, v)
                assert abs(invs["A2"]) < 1e-12, f"A2 non-zero: {invs['A2']}"


def test_weight_induced_braess_phase_transition():
    """Verify Theorem 3: existence of weight-induced Braess phase transition and exact critical threshold w*."""
    # A known graph exhibiting weight-induced Braess: 5-node graph with edges (0,1), (0,4), (2,4), (3,4)
    # Non-edge (1, 2)
    G = nx.erdos_renyi_graph(5, 0.4, seed=1)
    A = nx.to_numpy_array(G, nodelist=range(5))
    engine = KemenyPerturbationEngine(A)
    u, v = 1, 2

    res = engine.analyze_edge_regime(u, v)
    assert res["regime"] == EdgeRegime.WEIGHT_INDUCED_BRAESS.value
    assert res["A0"] < 0
    assert res["A1"] > 0
    w_crit = res["critical_weight"]
    assert w_crit is not None
    assert w_crit > 0

    # Test Delta K at critical weight: must be zero
    dK_at_crit = engine.compute_edge_perturbation_algebraic(u, v, w_crit)
    assert abs(dK_at_crit) < 1e-12, f"Delta K at w* is not zero: {dK_at_crit}"

    # Test strictly below critical weight: must be negative (favorable)
    dK_below = engine.compute_edge_perturbation_algebraic(u, v, 0.5 * w_crit)
    assert dK_below < 0, f"Expected dK < 0 below w*, got {dK_below}"

    # Test strictly above critical weight: must be positive (Braess)
    dK_above = engine.compute_edge_perturbation_algebraic(u, v, 1.5 * w_crit)
    assert dK_above > 0, f"Expected dK > 0 above w*, got {dK_above}"

    # Verify optimal weight w_opt exists strictly between 0 and w_crit
    w_opt = res["optimal_weight"]
    assert w_opt is not None
    assert 0 < w_opt < w_crit
    dK_opt = engine.compute_edge_perturbation_algebraic(u, v, w_opt)
    assert dK_opt < dK_below
    assert dK_opt < 0


def test_vectorized_all_pairs_equivalence():
    """Verify Theorem 5: vectorized all-pairs matrix matches individual O(1) evaluations."""
    G = nx.erdos_renyi_graph(8, 0.5, seed=123)
    A = nx.to_numpy_array(G)
    engine = KemenyPerturbationEngine(A)

    w = 1.75
    all_pairs = engine.all_pairs_kemeny_analysis(w=w)

    for u in range(engine.n):
        for v in range(u + 1, engine.n):
            single_dK = engine.compute_edge_perturbation_algebraic(u, v, w)
            vec_dK = all_pairs["delta_K"][u, v]
            assert math.isclose(single_dK, vec_dK, rel_tol=1e-12, abs_tol=1e-12)

            single_invs = engine.get_pair_invariants(u, v)
            assert math.isclose(single_invs["A0"], all_pairs["A0"][u, v], rel_tol=1e-12)
            assert math.isclose(single_invs["A1"], all_pairs["A1"][u, v], rel_tol=1e-12)


def test_100_random_graphs_property_test():
    """Exhaustive randomized test across 100 graphs verifying zero algebraic discrepancy."""
    max_discrepancy = 0.0
    for seed in range(100):
        n = 5 + (seed % 8)
        p = 0.25 + 0.05 * (seed % 6)
        G = nx.erdos_renyi_graph(n, p, seed=seed)
        if not nx.is_connected(G):
            components = list(nx.connected_components(G))
            for i in range(len(components) - 1):
                u = list(components[i])[0]
                v = list(components[i + 1])[0]
                G.add_edge(u, v)

        A = nx.to_numpy_array(G, nodelist=range(n))
        engine = KemenyPerturbationEngine(A)
        non_edges = list(nx.non_edges(G))
        if not non_edges:
            continue

        u, v = non_edges[seed % len(non_edges)]
        w = 0.1 + (seed * 0.15)

        dK_bf = engine.compute_edge_perturbation_brute_force(u, v, w)
        dK_alg = engine.compute_edge_perturbation_algebraic(u, v, w)
        err = abs(dK_bf - dK_alg)
        if err > max_discrepancy:
            max_discrepancy = err
        assert err < 1e-11

    assert max_discrepancy < 1e-11


def test_real_world_networks():
    """Verify perturbation engine on canonical real-world benchmark networks."""
    # 1. Zachary's Karate Club (n=34)
    G_karate = nx.karate_club_graph()
    A_karate = nx.to_numpy_array(G_karate)
    engine_karate = KemenyPerturbationEngine(A_karate)

    assert engine_karate.n == 34
    assert engine_karate.kemeny_constant > 0

    # Pick non-edges and verify formula
    non_edges_karate = list(nx.non_edges(G_karate))
    for u, v in non_edges_karate[:5]:
        dK_bf = engine_karate.compute_edge_perturbation_brute_force(u, v, 1.0)
        dK_alg = engine_karate.compute_edge_perturbation_algebraic(u, v, 1.0)
        assert abs(dK_bf - dK_alg) < 1e-11

    # 2. Florentine Families Graph (n=15)
    G_florentine = nx.florentine_families_graph()
    largest_cc = max(nx.connected_components(G_florentine), key=len)
    G_flor_sub = nx.convert_node_labels_to_integers(G_florentine.subgraph(largest_cc))
    A_flor = nx.to_numpy_array(G_flor_sub)
    engine_flor = KemenyPerturbationEngine(A_flor)
    assert engine_flor.kemeny_constant > 0
    non_edges_flor = list(nx.non_edges(G_flor_sub))
    for u, v in non_edges_flor[:5]:
        dK_bf = engine_flor.compute_edge_perturbation_brute_force(u, v, 1.0)
        dK_alg = engine_flor.compute_edge_perturbation_algebraic(u, v, 1.0)
        assert abs(dK_bf - dK_alg) < 1e-11


def test_input_validation_and_edge_cases():
    """Verify robust error handling on degenerate or invalid inputs."""
    # Disconnected graph must raise ValueError
    A_disc = np.zeros((4, 4))
    A_disc[0, 1] = A_disc[1, 0] = 1.0
    A_disc[2, 3] = A_disc[3, 2] = 1.0
    with pytest.raises(ValueError, match="connected"):
        KemenyPerturbationEngine(A_disc)

    # Non-symmetric matrix
    A_asym = np.array([[0, 1], [0, 0]], dtype=float)
    with pytest.raises(ValueError, match="symmetric"):
        KemenyPerturbationEngine(A_asym)

    # Identical nodes u == v
    G = nx.complete_graph(3)
    engine = KemenyPerturbationEngine(nx.to_numpy_array(G))
    with pytest.raises(ValueError, match="distinct"):
        engine.get_pair_invariants(0, 0)

    # Non-positive weight
    with pytest.raises(ValueError, match="strictly positive"):
        engine.compute_edge_perturbation_algebraic(0, 1, -1.0)
