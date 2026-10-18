"""Exact Rational Perturbation Theory and Braess Phase Transitions for Kemeny's Constant.

Author: Rajveersinh Vishal Pardeshi
Affiliation: Independent Researcher

This module implements the exact closed-form algebraic perturbation theory for
Kemeny's constant under rank-one edge modifications in finite, connected,
undirected graphs. It provides:
1. Exact computation of Kemeny's constant via Laplacian pseudoinverse, spectral decomposition,
   and random walk hitting times.
2. The exact rational closed-form formula for Delta K(G; u, v, w).
3. Exact classification into the four topological regimes (Globally Favorable, Globally Braess,
   Weight-Induced Braess, Capacity-Activated Favorable).
4. Exact closed-form critical weight threshold w*(u, v) = -A0 / A1.
5. An O(n^3) precomputation + O(1) query all-pairs deterministic algorithm using the
   metric matrix M = L^+ D L^+.

All algorithms compute quantities dynamically from first principles with zero precalculated
lookup tables or synthetic constants.
"""

from __future__ import annotations

from typing import Dict, Tuple
import enum

from scipy import optimize
import numpy as np




class EdgeRegime(str, enum.Enum):
    """The four topological regimes for edge modifications under Kemeny's constant."""

    GLOBALLY_FAVORABLE = "Globally Favorable"
    GLOBALLY_BRAESS = "Globally Braess"
    WEIGHT_INDUCED_BRAESS = "Weight-Induced Braess"
    CAPACITY_ACTIVATED_FAVORABLE = "Capacity-Activated Favorable"
    NEUTRAL = "Neutral"


class KemenyPerturbationEngine:
    """Exact rational perturbation analysis of Kemeny's constant on graphs.

    Parameters
    ----------
    adjacency_matrix : np.ndarray
        A symmetric, non-negative adjacency matrix representing a connected graph.
    """

    def __init__(self, adjacency_matrix: np.ndarray) -> None:
        """Init.
        
        Args:
            adjacency_matrix:
        
        """
        A = np.asarray(adjacency_matrix, dtype=np.float64)
        if A.ndim != 2 or A.shape[0] != A.shape[1]:
            raise ValueError("Adjacency matrix must be square (n x n).")
        if not np.allclose(A, A.T, atol=1e-12):
            raise ValueError("Adjacency matrix must be symmetric for undirected graphs.")
        if np.any(A < 0):
            raise ValueError("Edge weights must be non-negative.")

        self.n: int = A.shape[0]
        self.A: np.ndarray = A
        self.d: np.ndarray = np.sum(A, axis=1)
        self.total_volume: float = float(np.sum(self.d))
        self.m: float = self.total_volume / 2.0

        if self.m <= 0:
            raise ValueError("Graph has zero total edge weight.")

        self.D: np.ndarray = np.diag(self.d)
        self.L: np.ndarray = self.D - self.A

        # Compute Moore-Penrose pseudoinverse of the graph Laplacian
        self.L_pinv: np.ndarray = np.linalg.pinv(self.L)

        # Check connectivity: second smallest eigenvalue of L must be strictly positive
        eigvals_L = np.sort(np.linalg.eigvalsh(self.L))
        self.algebraic_connectivity: float = float(eigvals_L[1]) if self.n > 1 else 0.0
        if self.algebraic_connectivity < 1e-10:
            raise ValueError("Graph must be connected (algebraic connectivity > 0).")

        # Precompute key invariants for O(1) all-pairs evaluation
        # y = L^+ d (degree-load potential vector)
        self.y: np.ndarray = self.L_pinv @ self.d
        self.Q0: float = float(self.d @ self.y)
        self.T0: float = float(np.trace(self.D @ self.L_pinv))

        # Kemeny's constant K(G) = Tr(D L^+) - (1 / 2m) d^T L^+ d
        self.kemeny_constant: float = self.T0 - (self.Q0 / (2.0 * self.m))

        # Auxiliary metric matrix M = L^+ D L^+ for O(1) dipole quadratic forms: x^T D x = M_uu + M_vv - 2 M_uv
        self.M: np.ndarray = self.L_pinv @ self.D @ self.L_pinv

        # Pairwise effective resistance matrix: Omega(u, v) = L^+_uu + L^+_vv - 2 L^+_uv
        diag_L = np.diag(self.L_pinv)
        self.Omega: np.ndarray = diag_L[:, None] + diag_L[None, :] - 2.0 * self.L_pinv

    @staticmethod
    def compute_kemeny_spectral(adjacency_matrix: np.ndarray) -> float:
        """Compute Kemeny's constant from the spectrum of the random walk transition matrix P = D^-1 A.

        Formula: K(G) = sum_{i=2}^n 1 / (1 - lambda_i)
        """
        A = np.asarray(adjacency_matrix, dtype=np.float64)
        d = np.sum(A, axis=1)
        D_inv = np.diag(1.0 / d)
        P = D_inv @ A
        eigvals = np.sort(np.real(np.linalg.eigvals(P)))[::-1]
        # Skip dominant eigenvalue lambda_1 = 1
        return float(np.sum(1.0 / (1.0 - eigvals[1:])))

    @staticmethod
    def compute_kemeny_hitting_times(adjacency_matrix: np.ndarray) -> Tuple[float, np.ndarray]:
        """Compute Kemeny's constant from the exact pairwise mean hitting time matrix H.

        Formula: H(i, j) = 1 + sum_{k != j} P_ik H(k, j); K(G) = sum_j pi_j H(i, j) for any i.
        """
        A = np.asarray(adjacency_matrix, dtype=np.float64)
        n = A.shape[0]
        d = np.sum(A, axis=1)
        total_vol = np.sum(d)
        pi = d / total_vol
        D_inv = np.diag(1.0 / d)
        P = D_inv @ A

        H = np.zeros((n, n), dtype=np.float64)
        for j in range(n):
            idx = [i for i in range(n) if i != j]
            M_sub = np.eye(n - 1) - P[np.ix_(idx, idx)]
            b_sub = np.ones(n - 1)
            sol = np.linalg.solve(M_sub, b_sub)
            for idx_i, orig_i in enumerate(idx):
                H[orig_i, j] = sol[idx_i]

        kemeny_vals = [float(np.sum(pi * H[i, :])) for i in range(n)]
        return float(np.mean(kemeny_vals)), H

    def compute_edge_perturbation_brute_force(self, u: int, v: int, w: float) -> float:
        """Compute Delta K(G; u, v, w) by full recomputation of the updated graph Laplacian."""
        if u == v:
            raise ValueError("Vertices u and v must be distinct.")
        if w <= 0:
            raise ValueError("Perturbation weight w must be strictly positive.")

        A_new = self.A.copy()
        A_new[u, v] += w
        A_new[v, u] += w

        d_new = np.sum(A_new, axis=1)
        m_new = np.sum(d_new) / 2.0
        D_new = np.diag(d_new)
        L_new = D_new - A_new
        L_new_pinv = np.linalg.pinv(L_new)

        T_new = float(np.trace(D_new @ L_new_pinv))
        Q_new = float(d_new @ (L_new_pinv @ d_new))
        K_new = T_new - (Q_new / (2.0 * m_new))

        return float(K_new - self.kemeny_constant)

    def get_pair_invariants(self, u: int, v: int) -> Dict[str, float]:
        """Compute the exact scalar invariants for the vertex pair (u, v) in O(1) time."""
        if u == v:
            raise ValueError("Vertices u and v must be distinct.")

        # Effective resistance
        omega_uv = float(self.Omega[u, v])

        # Dipole potential quadratic form x^T D x = M_uu + M_vv - 2 M_uv
        xDx = float(self.M[u, u] + self.M[v, v] - 2.0 * self.M[u, v])

        # Principal 2x2 determinant of L_pinv
        det_Lpinv_2x2 = float(self.L_pinv[u, u] * self.L_pinv[v, v] - (self.L_pinv[u, v]) ** 2)

        # Coefficients c0 and c1
        c0 = float(self.L_pinv[u, u] + self.L_pinv[v, v] - xDx)
        c1 = 2.0 * det_Lpinv_2x2

        # Differences and sums
        alpha = float(self.y[u] - self.y[v])
        delta = float(self.L_pinv[u, u] - self.L_pinv[v, v])
        s_z = float(self.L_pinv[u, u] + self.L_pinv[v, v] + 2.0 * self.L_pinv[u, v])
        K_deg = float(2.0 * self.m * (self.y[u] + self.y[v]) - self.Q0)

        # Constant term of numerator N(w): A0
        A0 = float(2.0 * (self.m**2) * c0 - (K_deg - self.m * (alpha**2)))

        # Linear term of numerator N(w): A1
        A1 = float(
            2.0 * self.m * (self.m * c1 + c0)
            - (K_deg * omega_uv + self.m * s_z - 2.0 * self.m * alpha * delta)
        )

        # Quadratic term A2: proved identically zero in Theorem 2
        # A2 = 2m c1 - m (s_z * Omega - delta^2) = 4m det_2x2 - 4m det_2x2 = 0
        A2 = float(2.0 * self.m * c1 - self.m * (s_z * omega_uv - (delta**2)))

        return {
            "u": u,
            "v": v,
            "omega": omega_uv,
            "xDx": xDx,
            "det_2x2": det_Lpinv_2x2,
            "c0": c0,
            "c1": c1,
            "alpha": alpha,
            "delta": delta,
            "s_z": s_z,
            "K_deg": K_deg,
            "A0": A0,
            "A1": A1,
            "A2": A2,
        }

    def compute_edge_perturbation_algebraic(self, u: int, v: int, w: float) -> float:
        """Evaluate Delta K(G; u, v, w) using the exact closed-form rational formula.

        Formula: Delta K = w * (A0 + A1 * w) / (2m * (m + w) * (1 + w * Omega(u, v)))
        Time complexity: O(1).
        """
        if w <= 0:
            raise ValueError("Perturbation weight w must be strictly positive.")

        invs = self.get_pair_invariants(u, v)
        A0 = invs["A0"]
        A1 = invs["A1"]
        omega = invs["omega"]

        num = w * (A0 + A1 * w)
        denom = 2.0 * self.m * (self.m + w) * (1.0 + w * omega)

        return float(num / denom)

    def analyze_edge_regime(self, u: int, v: int, tol: float = 1e-10) -> Dict[str, object]:
        """Classify the vertex pair (u, v) into one of the four topological regimes and compute critical weights."""
        invs = self.get_pair_invariants(u, v)
        A0 = invs["A0"]
        A1 = invs["A1"]
        omega = invs["omega"]

        # Determine regime
        if abs(A0) < tol and abs(A1) < tol:
            regime = EdgeRegime.NEUTRAL
            w_crit = None
            w_opt = None
        elif A0 <= tol and A1 <= tol:
            regime = EdgeRegime.GLOBALLY_FAVORABLE
            w_crit = None
            # Optimal weight: since Delta K is negative and decreasing, w_opt -> infinity
            w_opt = float("inf")
        elif A0 >= -tol and A1 >= -tol:
            regime = EdgeRegime.GLOBALLY_BRAESS
            w_crit = None
            w_opt = 0.0  # adding no weight is optimal
        elif A0 < -tol and A1 > tol:
            regime = EdgeRegime.WEIGHT_INDUCED_BRAESS
            w_crit = float(-A0 / A1)

            # Find interior optimal weight w_opt in (0, w_crit) by minimizing Delta K(w)
            def dK_objective(w_val: float) -> float:
                """D K objective.
                
                Args:
                    w_val:
                
                Returns:
                    The computed result
                
                """
                return self.compute_edge_perturbation_algebraic(u, v, w_val)

            res = optimize.minimize_scalar(
                dK_objective,
                bounds=(1e-6, w_crit),
                method="bounded",
            )
            w_opt = float(res.x) if res.success else None
        else:  # A0 > tol and A1 < -tol
            regime = EdgeRegime.CAPACITY_ACTIVATED_FAVORABLE
            w_crit = float(-A0 / A1)
            w_opt = float("inf")

        return {
            "u": u,
            "v": v,
            "regime": regime.value,
            "A0": A0,
            "A1": A1,
            "A2": invs["A2"],
            "critical_weight": w_crit,
            "optimal_weight": w_opt,
            "omega": omega,
            "infinitesimal_derivative": float(A0 / (2.0 * (self.m**2))),
            "asymptotic_delta_k": float(A1 / (2.0 * self.m * omega)) if omega > 0 else 0.0,
        }

    def all_pairs_kemeny_analysis(self, w: float = 1.0) -> Dict[str, np.ndarray]:
        """Compute the exact Kemeny perturbation for ALL n(n-1)/2 vertex pairs simultaneously in O(n^2) time.

        Returns
        -------
        dict containing:
            'A0': (n x n) matrix of constant numerator coefficients.
            'A1': (n x n) matrix of linear numerator coefficients.
            'delta_K': (n x n) matrix of exact Kemeny changes at weight w.
            'critical_weight': (n x n) matrix of Braess transition thresholds w*.
            'regime': (n x n) integer matrix encoding the regime (0=Favorable, 1=Braess, 2=Weight-Induced, 3=Capacity-Activated).
        """
        n = self.n
        m = self.m
        diag_L = np.diag(self.L_pinv)
        diag_M = np.diag(self.M)

        # Vectorized c0: L_uu + L_vv - (M_uu + M_vv - 2 M_uv)
        L_sum = diag_L[:, None] + diag_L[None, :]
        M_sum = diag_M[:, None] + diag_M[None, :]
        xDx = M_sum - 2.0 * self.M
        c0 = L_sum - xDx

        # Vectorized c1: 2 * (L_uu L_vv - L_uv^2)
        det_2x2 = diag_L[:, None] * diag_L[None, :] - (self.L_pinv**2)
        c1 = 2.0 * det_2x2

        # Vectorized differences
        alpha = self.y[:, None] - self.y[None, :]
        delta = diag_L[:, None] - diag_L[None, :]
        s_z = L_sum + 2.0 * self.L_pinv
        y_sum = self.y[:, None] + self.y[None, :]
        K_deg = 2.0 * m * y_sum - self.Q0

        # Vectorized A0 and A1
        A0 = 2.0 * (m**2) * c0 - (K_deg - m * (alpha**2))
        A1 = 2.0 * m * (m * c1 + c0) - (K_deg * self.Omega + m * s_z - 2.0 * m * alpha * delta)

        # Clear diagonals
        np.fill_diagonal(A0, 0.0)
        np.fill_diagonal(A1, 0.0)

        # Vectorized Delta K(w)
        num = w * (A0 + A1 * w)
        denom = 2.0 * m * (m + w) * (1.0 + w * self.Omega)
        # Avoid division by zero on diagonal where Omega = 0
        np.fill_diagonal(denom, 1.0)
        delta_K = num / denom
        np.fill_diagonal(delta_K, 0.0)

        # Critical weights: w* = -A0 / A1
        with np.errstate(divide="ignore", invalid="ignore"):
            w_crit = -A0 / A1
            w_crit[A1 == 0] = np.nan
            w_crit[w_crit <= 0] = np.nan

        # Regime classification matrix
        # 0: Globally Favorable, 1: Globally Braess, 2: Weight-Induced Braess, 3: Capacity-Activated
        regime_matrix = np.zeros((n, n), dtype=int)
        regime_matrix[(A0 <= 0) & (A1 <= 0)] = 0
        regime_matrix[(A0 >= 0) & (A1 >= 0)] = 1
        regime_matrix[(A0 < 0) & (A1 > 0)] = 2
        regime_matrix[(A0 > 0) & (A1 < 0)] = 3
        np.fill_diagonal(regime_matrix, -1)

        return {
            "A0": A0,
            "A1": A1,
            "delta_K": delta_K,
            "critical_weight": w_crit,
            "regime_matrix": regime_matrix,
        }
