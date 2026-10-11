"""
11-qubit basis state encoding and deterministic decoding.
Section 2.2 and 2.3 of Agent PRD.
"""

from typing import List, Tuple
import numpy as np


def events_from_tune(tune: List[Tuple[int, float]]) -> List[Tuple[int, int, int]]:
    """
    Convert monophonic note list [(pitch, beats), ...] to events [(pitch, d16, onset16), ...].
    Durations are quantized to 16th notes (d16 = round(beats * 4)).
    """
    events = []
    onset16 = 0
    for pitch, beats in tune:
        d16 = int(round(beats * 4))
        if d16 < 1 or d16 > 15:
            raise ValueError(f"Duration {d16} sixteenths out of bounds [1, 15] for beats={beats}")
        if pitch < 0 or pitch > 127:
            raise ValueError(f"Pitch {pitch} out of bounds [0, 127]")
        events.append((pitch, d16, onset16))
        onset16 += d16
    return events


def encode_note(pitch: int, d16: int) -> np.ndarray:
    """
    Encode note into an 11-qubit quantum statevector:
    bits 0-6 hold pitch (7 bits), bits 7-10 hold duration (4 bits).
    value = pitch | (d16 << 7).
    State begins in |0...0>, applying X gate on every qubit k where bit k of value is 1.
    Resulting statevector has length 2**11 = 2048 with amplitude 1.0 at index `value`.
    """
    if pitch < 0 or pitch > 127:
        raise ValueError(f"Invalid pitch: {pitch}")
    if d16 < 1 or d16 > 15:
        raise ValueError(f"Invalid d16 duration: {d16}")

    value = pitch | (d16 << 7)
    state = np.zeros(2048, dtype=complex)
    state[value] = 1.0 + 0.0j
    return state


def decode_index(i: int) -> Tuple[int, int]:
    """
    Decode measurement basis index i into (pitch, d16):
    pitch = i & 0x7F
    d16 = i >> 7
    """
    pitch = i & 0x7F
    d16 = i >> 7
    return pitch, d16


def roundtrip_note(pitch: int, d16: int) -> Tuple[int, int, float]:
    """
    Perform exact quantum basis round trip for a single note.
    Returns (decoded_pitch, decoded_d16, target_probability).
    """
    state = encode_note(pitch, d16)
    target_idx = pitch | (d16 << 7)
    prob = float(np.abs(state[target_idx]) ** 2)

    # Projective measurement outcome in computational basis
    measured_idx = int(np.argmax(np.abs(state) ** 2))
    dec_pitch, dec_d16 = decode_index(measured_idx)
    return dec_pitch, dec_d16, prob


def roundtrip_melody(events: List[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
    """
    Perform exact quantum basis round trip for all notes in melody.
    Fails if target probability < 1 - 1e-9 for any note.
    """
    reconstructed = []
    for pitch, d16, onset in events:
        dec_pitch, dec_d16, prob = roundtrip_note(pitch, d16)
        if abs(prob - 1.0) > 1e-9:
            raise RuntimeError(f"Exactness condition failed: prob={prob} for pitch={pitch}, d16={d16}")
        if dec_pitch != pitch or dec_d16 != d16:
            raise RuntimeError(f"Roundtrip mismatch: expected ({pitch}, {d16}), got ({dec_pitch}, {dec_d16})")
        reconstructed.append((dec_pitch, dec_d16, onset))
    return reconstructed
