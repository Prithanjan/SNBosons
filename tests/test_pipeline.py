"""
Test Pipeline for SNBosons / qsong.
Implements the 11 automated verification checks defined in Section 3 and Section 7 of Agent PRD.
"""

import os
import tempfile
import pytest
import numpy as np

from qsong.encode import (
    events_from_tune,
    encode_note,
    decode_index,
    roundtrip_note,
    roundtrip_melody,
)
from qsong.harmony import (
    TWINKLE,
    C_MAJOR_PITCH_CLASSES,
    VALID_CONSONANT_INTERVALS,
    pick,
    settings,
    duet_voices,
)
from qsong.measure import (
    sample_bell_pair,
    sample_classical_pair,
    joint_probabilities,
    theoretical_correlation,
    theoretical_chsh_s,
    measure_chsh_statistic,
)
from qsong.render import (
    render_mix,
    measure_rms,
    write_wav,
)
from qsong.midi_io import (
    write_midi,
)
from qsong.cli import (
    run_experiment,
    compute_same_direction_fraction,
)


# Test 1: Single-note round trip exhaustive check across all 128 pitches and 15 durations (1920 notes)
def test_1_exhaustive_single_note_roundtrip():
    failures = 0
    total = 0
    for pitch in range(128):
        for d16 in range(1, 16):
            dec_p, dec_d16, prob = roundtrip_note(pitch, d16)
            if dec_p != pitch or dec_d16 != d16 or abs(prob - 1.0) > 1e-9:
                failures += 1
            total += 1
    assert total == 1920
    assert failures == 0, f"Exhaustive roundtrip failed on {failures} / {total} notes"


# Test 2: Random melody round trips (50 of 50 exact)
def test_2_random_melody_roundtrips():
    rng = np.random.default_rng(2026)
    failures = 0
    for _ in range(50):
        length = int(rng.integers(10, 40))
        pitches = rng.integers(48, 84, size=length)
        beats = rng.choice([0.25, 0.5, 0.75, 1.0, 1.5, 2.0], size=length)
        tune = [(int(p), float(b)) for p, b in zip(pitches, beats)]
        events = events_from_tune(tune)
        try:
            reconstructed = roundtrip_melody(events)
            for orig, rec in zip(events, reconstructed):
                if orig[0] != rec[0] or orig[1] != rec[1] or orig[2] != rec[2]:
                    failures += 1
                    break
        except Exception:
            failures += 1
    assert failures == 0, f"Random melody roundtrips had {failures} failures out of 50"


# Test 3: Twinkle melody round trip (42 of 42 notes exact)
def test_3_twinkle_melody_roundtrip():
    events = events_from_tune(TWINKLE)
    assert len(events) == 42
    reconstructed = roundtrip_melody(events)
    assert len(reconstructed) == 42
    for orig, rec in zip(events, reconstructed):
        assert orig[0] == rec[0]
        assert orig[1] == rec[1]
        assert orig[2] == rec[2]


# Test 4: Bell correlation vs theory over a 9x9 angle grid
def test_4_bell_correlation_grid():
    grid = np.linspace(-np.pi / 2, np.pi / 2, 9)
    for alpha in grid:
        for beta in grid:
            p00, p01, p10, p11 = joint_probabilities(alpha, beta)
            # Analytical sum must equal 1.0
            assert abs((p00 + p01 + p10 + p11) - 1.0) < 1e-9
            e_analytical = (p00 + p11) - (p01 + p10)
            e_theory = theoretical_correlation(alpha, beta)
            assert abs(e_analytical - e_theory) < 1e-9


# Test 5: Theoretical CHSH S parameter under optimal settings (S = 2*sqrt(2) = 2.8284)
def test_5_theoretical_chsh_s():
    s_val = theoretical_chsh_s()
    assert abs(s_val - 2.8284271247) < 1e-4
    assert s_val > 2.0, "Theoretical CHSH S must violate the classical Bell bound (2.0)"


# Test 6: Measured CHSH S parameter from 20000 shots approaches 2.83
def test_6_measured_chsh_from_shots():
    s_meas, corr = measure_chsh_statistic(shots_per_setting=20000, seed=2026)
    # Measured S should be close to 2.828 with small statistical variance
    assert 2.75 <= s_meas <= 2.90, f"Measured S={s_meas:.4f} outside expected tolerance"
    assert s_meas > 2.0, "Measured CHSH must strictly exceed the classical limit of 2.0"


# Test 7: Harmony consonance across 100 random seeds (every interval in {3, 4, 7, 8, 9}, 0 tritones)
def test_7_harmony_consonance_100_seeds():
    events = events_from_tune(TWINKLE)
    alphas, betas = settings(events)

    for seed in range(100):
        rng = np.random.default_rng(seed)
        pairs = [sample_bell_pair(a, b, rng) for a, b in zip(alphas, betas)]
        upper, lower = duet_voices(events, pairs)

        for (p, _, _), u, l in zip(events, upper, lower):
            diff_u = abs(u - p)
            diff_l = abs(p - l)
            assert diff_u in VALID_CONSONANT_INTERVALS, f"Upper interval {diff_u} not in {VALID_CONSONANT_INTERVALS}"
            assert diff_l in VALID_CONSONANT_INTERVALS, f"Lower interval {diff_l} not in {VALID_CONSONANT_INTERVALS}"
            assert u % 12 in C_MAJOR_PITCH_CLASSES
            assert l % 12 in C_MAJOR_PITCH_CLASSES


# Test 8: Audio render RMS match between quantum and independent duets (within 0.5% error)
def test_8_audio_rms_match():
    res_q = run_experiment(tune=TWINKLE, seed=101, mode="quantum")
    res_c = run_experiment(tune=TWINKLE, seed=101, mode="independent")

    rms_q = res_q["rms"]
    rms_c = res_c["rms"]
    error_pct = abs(rms_q - rms_c) / rms_c * 100.0

    assert error_pct < 0.5, f"RMS mismatch {error_pct:.4f}% exceeds 0.5% limit"
    assert res_q["max_abs"] < 1.0, f"Quantum mix clipped: max_abs={res_q['max_abs']}"
    assert res_c["max_abs"] < 1.0, f"Independent mix clipped: max_abs={res_c['max_abs']}"


# Test 9: Voice motion characteristics
def test_9_voice_motion_characteristics():
    res_q = run_experiment(tune=TWINKLE, seed=42, mode="quantum")
    res_c = run_experiment(tune=TWINKLE, seed=42, mode="independent")

    # In Twinkle, motion fraction for quantum seed 42 is ~0.536
    assert 0.40 <= res_q["same_direction_fraction"] <= 0.70
    assert 0.35 <= res_c["same_direction_fraction"] <= 0.85


# Test 10: MIDI and WAV writing verification
def test_10_file_io_midi_and_wav():
    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = os.path.join(tmpdir, "test.wav")
        mid_path = os.path.join(tmpdir, "test.mid")

        events = events_from_tune(TWINKLE)
        rng = np.random.default_rng(42)
        pairs = [sample_classical_pair(rng) for _ in range(len(events))]
        upper, lower = duet_voices(events, pairs)

        mix = render_mix(events, upper, lower, mode="quantum")
        write_wav(wav_path, mix)
        assert os.path.exists(wav_path)
        assert os.path.getsize(wav_path) > 1000

        write_midi(mid_path, events, upper, lower)
        assert os.path.exists(mid_path)
        assert os.path.getsize(mid_path) > 100


# Test 11: Ground rule isolation (no private keys in outputs, key generation reproducible)
def test_11_private_keys_isolation_and_reproducibility():
    from qsong.cli import generate_blind_trials

    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = os.path.join(tmpdir, "blind_out")
        key_dir = os.path.join(tmpdir, "private_key")

        # Generate trials with canonical seed 2026
        keys1 = generate_blind_trials(
            tune=TWINKLE,
            num_trials=3,
            base_seed=100,
            rng_order_seed=2026,
            output_dir=out_dir,
            private_key_dir=key_dir,
        )

        # Check that keys are in key_dir and NOT in out_dir
        assert os.path.exists(os.path.join(key_dir, "trials_key.json"))
        assert not os.path.exists(os.path.join(out_dir, "trials_key.json"))

        # Re-generating with seed 2026 must produce identical key order
        keys2 = generate_blind_trials(
            tune=TWINKLE,
            num_trials=3,
            base_seed=100,
            rng_order_seed=2026,
            output_dir=out_dir,
            private_key_dir=key_dir,
        )
        assert keys1 == keys2, "Key generation with fixed seed 2026 must be reproducible"


# Test 12: Secondary tune (Ode to Joy) exact round trip, angle coverage, and consonance (Task R4/R5)
def test_12_ode_to_joy_roundtrip_and_consonance():
    from qsong.harmony import ODE_TO_JOY

    events = events_from_tune(ODE_TO_JOY)
    assert len(events) == 16

    # 1. Exact quantum basis round trip
    reconstructed = roundtrip_melody(events)
    assert len(reconstructed) == 16
    for orig, rec in zip(events, reconstructed):
        assert orig == rec

    # 2. Angle settings must cover all 4 CHSH combinations
    alphas, betas = settings(events)
    counts = {"0_pos": 0, "0_neg": 0, "pi4_pos": 0, "pi4_neg": 0}
    for a, b in zip(alphas, betas):
        if abs(a) < 1e-4 and b > 0:
            counts["0_pos"] += 1
        elif abs(a) < 1e-4 and b < 0:
            counts["0_neg"] += 1
        elif abs(a - np.pi / 4.0) < 1e-4 and b > 0:
            counts["pi4_pos"] += 1
        else:
            counts["pi4_neg"] += 1
    assert all(c > 0 for c in counts.values()), f"Ode to Joy missing an angle setting: {counts}"

    # 3. Consonance across 100 seeds
    for seed in range(100):
        rng = np.random.default_rng(seed)
        pairs = [sample_bell_pair(a, b, rng) for a, b in zip(alphas, betas)]
        upper, lower = duet_voices(events, pairs)
        for (p, _, _), u, l in zip(events, upper, lower):
            assert abs(u - p) in VALID_CONSONANT_INTERVALS
            assert abs(p - l) in VALID_CONSONANT_INTERVALS
            assert u % 12 in C_MAJOR_PITCH_CLASSES
            assert l % 12 in C_MAJOR_PITCH_CLASSES


# Test 13: Secondary tune (Ode to Joy) audio render and RMS match
def test_13_ode_to_joy_render_and_rms_match():
    from qsong.harmony import ODE_TO_JOY

    res_q = run_experiment(tune=ODE_TO_JOY, seed=101, mode="quantum")
    res_c = run_experiment(tune=ODE_TO_JOY, seed=101, mode="independent")

    rms_q = res_q["rms"]
    rms_c = res_c["rms"]
    error_pct = abs(rms_q - rms_c) / rms_c * 100.0

    assert error_pct < 0.5, f"Ode to Joy RMS mismatch {error_pct:.4f}% exceeds 0.5%"
    assert res_q["max_abs"] < 1.0, f"Ode to Joy quantum mix clipped: {res_q['max_abs']}"
    assert res_c["max_abs"] < 1.0, f"Ode to Joy independent mix clipped: {res_c['max_abs']}"

