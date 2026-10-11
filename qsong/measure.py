"""
Bell state measurement, CHSH correlation, and sampling.
Section 2.5 of Agent PRD.
"""

from typing import Tuple, List, Dict
import numpy as np


def joint_probabilities(alpha: float, beta: float) -> Tuple[float, float, float, float]:
    """
    Compute analytical joint probabilities P(x, y) for Bell state Phi+ = (|00> + |11>) / sqrt(2)
    measured in basis angles alpha and beta:
    x in {0, 1}, y in {0, 1}.
    Returns (P(0,0), P(0,1), P(1,0), P(1,1)).
    """
    diff = alpha - beta
    p_same_half = 0.5 * (np.cos(diff) ** 2)
    p_diff_half = 0.5 * (np.sin(diff) ** 2)
    p00 = float(p_same_half)
    p11 = float(p_same_half)
    p01 = float(p_diff_half)
    p10 = float(p_diff_half)
    return p00, p01, p10, p11


def sample_bell_pair(alpha: float, beta: float, rng: np.random.Generator = None) -> Tuple[int, int]:
    """
    Sample one (x, y) pair from the entangled joint distribution P(x, y).
    Maps outcome 0 -> +1, outcome 1 -> -1.
    Returns (a, b) where a, b in {+1, -1}.
    """
    if rng is None:
        rng = np.random.default_rng()

    probs = list(joint_probabilities(alpha, beta))
    # Outcomes: 0 -> (0,0), 1 -> (0,1), 2 -> (1,0), 3 -> (1,1)
    choice = rng.choice(4, p=probs)
    if choice == 0:
        return +1, +1
    elif choice == 1:
        return +1, -1
    elif choice == 2:
        return -1, +1
    else:
        return -1, -1


def sample_classical_pair(rng: np.random.Generator = None) -> Tuple[int, int]:
    """
    Sample one independent fair coin pair (a, b) where each is uniform on {+1, -1}.
    Used as classical control baseline.
    """
    if rng is None:
        rng = np.random.default_rng()
    a = int(rng.choice([+1, -1]))
    b = int(rng.choice([+1, -1]))
    return a, b


def theoretical_correlation(alpha: float, beta: float) -> float:
    """
    Theoretical correlation E(alpha, beta) = cos(2(alpha - beta)).
    """
    return float(np.cos(2.0 * (alpha - beta)))


def theoretical_chsh_s() -> float:
    """
    Theoretical maximum CHSH S parameter under optimal settings:
    alpha in {0, pi/4}, beta in {pi/8, -pi/8}.
    S = E(0, pi/8) + E(0, -pi/8) + E(pi/4, pi/8) - E(pi/4, -pi/8) = 2*sqrt(2) = 2.828427...
    """
    e00 = theoretical_correlation(0.0, np.pi / 8.0)
    e01 = theoretical_correlation(0.0, -np.pi / 8.0)
    e10 = theoretical_correlation(np.pi / 4.0, np.pi / 8.0)
    e11 = theoretical_correlation(np.pi / 4.0, -np.pi / 8.0)
    return float(e00 + e01 + e10 - e11)


def measure_chsh_statistic(shots_per_setting: int = 10000, seed: int = 42) -> Tuple[float, Dict[str, float]]:
    """
    Measure empirical CHSH S parameter by simulating shots from the Bell state.
    Returns (S_measured, correlations_dict).
    """
    rng = np.random.default_rng(seed)
    settings_list = [
        ("0_pos", 0.0, np.pi / 8.0),
        ("0_neg", 0.0, -np.pi / 8.0),
        ("pi4_pos", np.pi / 4.0, np.pi / 8.0),
        ("pi4_neg", np.pi / 4.0, -np.pi / 8.0),
    ]

    correlations = {}
    for name, alpha, beta in settings_list:
        same_count = 0
        diff_count = 0
        for _ in range(shots_per_setting):
            a, b = sample_bell_pair(alpha, beta, rng)
            if a == b:
                same_count += 1
            else:
                diff_count += 1
        e = (same_count - diff_count) / shots_per_setting
        correlations[name] = e

    s_val = correlations["0_pos"] + correlations["0_neg"] + correlations["pi4_pos"] - correlations["pi4_neg"]
    return float(s_val), correlations
