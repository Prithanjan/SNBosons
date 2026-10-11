"""
Melody settings extraction and scale-based consonant harmony rules.
Sections 2.1, 2.4, 2.6 of Agent PRD.
"""

from typing import List, Tuple
import numpy as np

# Reference tune: Twinkle Twinkle Little Star (42 notes)
TWINKLE: List[Tuple[int, float]] = [
    # Phrase 1
    (60, 1.0), (60, 1.0), (67, 1.0), (67, 1.0), (69, 1.0), (69, 1.0), (67, 2.0),
    # Phrase 2
    (65, 1.0), (65, 1.0), (64, 1.0), (64, 1.0), (62, 1.0), (62, 1.0), (60, 2.0),
    # Phrase 3
    (67, 1.0), (67, 1.0), (65, 1.0), (65, 1.0), (64, 1.0), (64, 1.0), (62, 2.0),
    # Phrase 4
    (67, 1.0), (67, 1.0), (65, 1.0), (65, 1.0), (64, 1.0), (64, 1.0), (62, 2.0),
    # Phrase 5
    (60, 1.0), (60, 1.0), (67, 1.0), (67, 1.0), (69, 1.0), (69, 1.0), (67, 2.0),
    # Phrase 6
    (65, 1.0), (65, 1.0), (64, 1.0), (64, 1.0), (62, 1.0), (62, 1.0), (60, 2.0),
]

# Secondary reference tune: Beethoven's Ode to Joy (16 notes, 4 bars in C major)
ODE_TO_JOY: List[Tuple[int, float]] = [
    (64, 1.0), (64, 1.0), (65, 1.0), (67, 1.0),
    (67, 1.0), (65, 1.0), (64, 1.0), (62, 1.0),
    (60, 1.0), (60, 1.0), (62, 1.0), (64, 1.0),
    (64, 1.0), (62, 1.0), (62, 1.0), (62, 1.0),
]

C_MAJOR_PITCH_CLASSES = {0, 2, 4, 5, 7, 9, 11}
VALID_CONSONANT_INTERVALS = {3, 4, 7, 8, 9}

PITCH_NAME_TO_INT = {
    "C": 0, "B#": 0, "C#": 1, "DB": 1, "D": 2, "D#": 3, "EB": 3,
    "E": 4, "F": 5, "E#": 5, "F#": 6, "GB": 6, "G": 7, "G#": 8,
    "AB": 8, "A": 9, "A#": 10, "BB": 10, "B": 11, "CB": 11
}

MAJOR_INTERVALS = [0, 2, 4, 5, 7, 9, 11]
NATURAL_MINOR_INTERVALS = [0, 2, 3, 5, 7, 8, 10]
DORIAN_INTERVALS = [0, 2, 3, 5, 7, 9, 10]


def get_scale_pitch_classes(root: str = "C", scale_type: str = "major") -> set:
    """
    Generate pitch class set for any musical key and scale:
    root in {'C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'}
    scale_type in {'major', 'minor', 'dorian'}
    """
    root_int = PITCH_NAME_TO_INT.get(root.upper().strip(), 0)
    st = scale_type.lower().strip()
    if "minor" in st:
        intervals = NATURAL_MINOR_INTERVALS
    elif "dorian" in st:
        intervals = DORIAN_INTERVALS
    else:
        intervals = MAJOR_INTERVALS
    return {(root_int + interval) % 12 for interval in intervals}


def settings(events: List[Tuple[int, int, int]]) -> Tuple[List[float], List[float]]:
    """
    Extract measurement angles (alpha_t, beta_t) derived from melody:
    alpha_t = pi/4 if p_t < p_{t-1} (downward motion), else 0 (up or unchanged).
    For t=0, compare p_0 against p_0 (so alpha_0 = 0).
    beta_t = +pi/8 if p_t >= 65 (F4 or higher), else -pi/8.
    """
    alphas = []
    betas = []
    for t, (p_t, _, _) in enumerate(events):
        p_prev = events[t - 1][0] if t > 0 else events[0][0]
        alpha = np.pi / 4.0 if p_t < p_prev else 0.0
        beta = np.pi / 8.0 if p_t >= 65 else -np.pi / 8.0
        alphas.append(float(alpha))
        betas.append(float(beta))
    return alphas, betas


def pick(pitch: int, options: List[int], scale_pitch_classes: set = None) -> int:
    """
    Pick first (pitch + offset) for offset in options where (pitch + offset) mod 12 is in scale.
    Defaults to C Major if scale_pitch_classes is None.
    """
    if scale_pitch_classes is None:
        scale_pitch_classes = C_MAJOR_PITCH_CLASSES

    for offset in options:
        candidate = pitch + offset
        if candidate % 12 in scale_pitch_classes:
            return candidate
    raise ValueError(f"No valid consonant interval found for pitch {pitch} with options {options} in scale {scale_pitch_classes}")


def duet_voices(
    events: List[Tuple[int, int, int]],
    pairs: List[Tuple[int, int]],
    scale_pitch_classes: set = None,
) -> Tuple[List[int], List[int]]:
    """
    Derive upper and lower harmony voices given note events, measurement pairs (a_t, b_t),
    and target musical scale pitch classes:
    upper_t = pick(p_t, [7, 8, 9]) if a_t = +1 else pick(p_t, [4, 3])
    lower_t = pick(p_t, [-7, -8, -9]) if b_t = +1 else pick(p_t, [-4, -3])
    """
    if len(events) != len(pairs):
        raise ValueError(f"Mismatch in length: events ({len(events)}) vs pairs ({len(pairs)})")

    if scale_pitch_classes is None:
        scale_pitch_classes = C_MAJOR_PITCH_CLASSES

    upper = []
    lower = []
    for (p_t, _, _), (a_t, b_t) in zip(events, pairs):
        u_t = pick(p_t, [7, 8, 9], scale_pitch_classes=scale_pitch_classes) if a_t == +1 else pick(p_t, [4, 3], scale_pitch_classes=scale_pitch_classes)
        l_t = pick(p_t, [-7, -8, -9], scale_pitch_classes=scale_pitch_classes) if b_t == +1 else pick(p_t, [-4, -3], scale_pitch_classes=scale_pitch_classes)

        # Validate intervals
        diff_u = abs(u_t - p_t)
        diff_l = abs(p_t - l_t)
        if diff_u not in VALID_CONSONANT_INTERVALS:
            raise RuntimeError(f"Interval violation in upper harmony: {diff_u} not in {VALID_CONSONANT_INTERVALS}")
        if diff_l not in VALID_CONSONANT_INTERVALS:
            raise RuntimeError(f"Interval violation in lower harmony: {diff_l} not in {VALID_CONSONANT_INTERVALS}")

        upper.append(u_t)
        lower.append(l_t)

    return upper, lower
