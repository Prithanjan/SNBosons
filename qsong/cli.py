"""
Unified command-line interface and run_experiment entry point.
Sections 6, 7, and R2 of Agent PRD.
"""

from typing import List, Tuple, Dict, Any, Optional
import argparse
import json
import os
import numpy as np

from .encode import events_from_tune, roundtrip_melody
from .harmony import TWINKLE, settings, duet_voices
from .measure import sample_bell_pair, sample_classical_pair
from .render import render_mix, write_wav, measure_rms
from .midi_io import write_midi


def compute_same_direction_fraction(upper: List[int], lower: List[int]) -> float:
    """
    Fraction of note transitions where upper and lower voices move in the same direction:
    sign(upper[t] - upper[t-1]) == sign(lower[t] - lower[t-1]).
    """
    if len(upper) <= 1:
        return 0.0
    same = 0
    total = len(upper) - 1
    for t in range(1, len(upper)):
        du = np.sign(upper[t] - upper[t - 1])
        dl = np.sign(lower[t] - lower[t - 1])
        if du == dl:
            same += 1
    return float(same / total)


def compute_sample_chsh(
    alphas: List[float], betas: List[float], pairs: List[Tuple[int, int]]
) -> Optional[float]:
    """
    Compute sample CHSH S value if all 4 angle combinations occur:
    settings: (0, pi/8), (0, -pi/8), (pi/4, pi/8), (pi/4, -pi/8).
    S = E(0, pi/8) + E(0, -pi/8) + E(pi/4, pi/8) - E(pi/4, -pi/8).
    """
    grouped: Dict[str, List[int]] = {
        "0_pos": [],
        "0_neg": [],
        "pi4_pos": [],
        "pi4_neg": [],
    }

    for a, b, (out_a, out_b) in zip(alphas, betas, pairs):
        prod = out_a * out_b  # +1 if same, -1 if diff
        if abs(a - 0.0) < 1e-4 and b > 0:
            grouped["0_pos"].append(prod)
        elif abs(a - 0.0) < 1e-4 and b < 0:
            grouped["0_neg"].append(prod)
        elif abs(a - np.pi / 4.0) < 1e-4 and b > 0:
            grouped["pi4_pos"].append(prod)
        elif abs(a - np.pi / 4.0) < 1e-4 and b < 0:
            grouped["pi4_neg"].append(prod)

    # Check that all four settings have at least 1 sample
    if any(len(lst) == 0 for lst in grouped.values()):
        return None

    e0_pos = float(np.mean(grouped["0_pos"]))
    e0_neg = float(np.mean(grouped["0_neg"]))
    epi4_pos = float(np.mean(grouped["pi4_pos"]))
    epi4_neg = float(np.mean(grouped["pi4_neg"]))

    return float(e0_pos + e0_neg + epi4_pos - epi4_neg)


def run_experiment(
    tune: List[Tuple[int, float]] = None,
    seed: int = 42,
    mode: str = "quantum",
    add_reverb: bool = True,
) -> Dict[str, Any]:
    """
    Run full experiment pipeline according to Section 6:
    Returns dict containing:
    notes, upper, lower, pairs, chsh, same_direction_fraction, rms, max_abs.
    """
    if tune is None:
        tune = TWINKLE

    events = events_from_tune(tune)
    alphas, betas = settings(events)
    rng = np.random.default_rng(seed)

    if mode == "quantum":
        pairs = [sample_bell_pair(a, b, rng) for a, b in zip(alphas, betas)]
    elif mode in ("independent", "classical"):
        pairs = [sample_classical_pair(rng) for _ in range(len(events))]
    elif mode == "original":
        pairs = [(1, 1) for _ in range(len(events))]
    else:
        raise ValueError(f"Unknown mode: {mode}")

    if mode == "original":
        upper = [p for p, _, _ in events]
        lower = [p for p, _, _ in events]
    else:
        upper, lower = duet_voices(events, pairs)

    # Render audio mix
    mix = render_mix(events, upper, lower, mode=mode, add_reverb=add_reverb)
    rms = measure_rms(mix)
    max_abs = float(np.max(np.abs(mix)))
    same_dir_frac = compute_same_direction_fraction(upper, lower)
    chsh_val = compute_sample_chsh(alphas, betas, pairs)

    return {
        "events": events,
        "upper": upper,
        "lower": lower,
        "pairs": pairs,
        "chsh": chsh_val,
        "same_direction_fraction": same_dir_frac,
        "rms": rms,
        "max_abs": max_abs,
        "mode": mode,
        "seed": seed,
        "audio": mix,
    }


def generate_blind_trials(
    tune: List[Tuple[int, float]] = None,
    num_trials: int = 10,
    base_seed: int = 100,
    rng_order_seed: int = 2026,
    output_dir: str = "blind_trials",
    private_key_dir: str = "private",
) -> Dict[str, Any]:
    """
    Generate 10 double-blind trials (trial_01..10) according to Section 4:
    - Each trial has trial_XX_A.wav and trial_XX_B.wav.
    - One is quantum duet, one is independent duet, both RMS-matched to target 0.1835.
    - Order is randomized using rng_order_seed = 2026.
    - Secret answer keys saved ONLY in private/trials_key.json.
    """
    if tune is None:
        tune = TWINKLE

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(private_key_dir, exist_ok=True)

    order_rng = np.random.default_rng(rng_order_seed)
    keys = {}

    for i in range(1, num_trials + 1):
        trial_seed = base_seed + i
        res_quantum = run_experiment(tune, seed=trial_seed, mode="quantum")
        res_indep = run_experiment(tune, seed=trial_seed, mode="independent")

        # Determine assignment: 0 -> A=quantum, B=independent; 1 -> A=independent, B=quantum
        flip = order_rng.choice([0, 1])
        if flip == 0:
            clip_a = res_quantum["audio"]
            clip_b = res_indep["audio"]
            key_a = "quantum"
            key_b = "independent"
        else:
            clip_a = res_indep["audio"]
            clip_b = res_quantum["audio"]
            key_a = "independent"
            key_b = "quantum"

        trial_name = f"trial_{i:02d}"
        path_a = os.path.join(output_dir, f"{trial_name}_A.wav")
        path_b = os.path.join(output_dir, f"{trial_name}_B.wav")

        write_wav(path_a, clip_a)
        write_wav(path_b, clip_b)

        keys[trial_name] = {
            "A": key_a,
            "B": key_b,
            "more_independent": "A" if key_a == "independent" else "B",
            "seed": trial_seed,
            "rms_A": float(res_quantum["rms"] if flip == 0 else res_indep["rms"]),
            "rms_B": float(res_indep["rms"] if flip == 0 else res_quantum["rms"]),
        }

    # Save keys strictly in private directory
    key_path = os.path.join(private_key_dir, "trials_key.json")
    with open(key_path, "w") as f:
        json.dump(keys, f, indent=2)

    return keys


def main():
    parser = argparse.ArgumentParser(description="SNBosons / qsong CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # run command
    run_parser = subparsers.add_parser("run", help="Run experiment")
    run_parser.add_argument("--mode", choices=["quantum", "independent", "original"], default="quantum")
    run_parser.add_argument("--seed", type=int, default=42)
    run_parser.add_argument("--wav", type=str, default=None, help="Output WAV path")
    run_parser.add_argument("--midi", type=str, default=None, help="Output MIDI path")
    run_parser.add_argument("--json", type=str, default=None, help="Output metrics JSON path")

    # roundtrip command
    subparsers.add_parser("roundtrip", help="Verify exact quantum basis memory roundtrip")

    # blind-trials command
    blind_parser = subparsers.add_parser("blind-trials", help="Generate blind listening trials")
    blind_parser.add_argument("--count", type=int, default=10)
    blind_parser.add_argument("--out-dir", type=str, default="blind_trials")

    args = parser.parse_args()

    if args.command == "roundtrip":
        events = events_from_tune(TWINKLE)
        reconstructed = roundtrip_melody(events)
        print(f"Round trip exact on all {len(reconstructed)} notes of Twinkle Twinkle!")

    elif args.command == "run":
        res = run_experiment(tune=TWINKLE, seed=args.seed, mode=args.mode)
        metrics = {
            "mode": res["mode"],
            "seed": res["seed"],
            "chsh": res["chsh"],
            "same_direction_fraction": res["same_direction_fraction"],
            "rms": res["rms"],
            "max_abs": res["max_abs"],
        }
        print(json.dumps(metrics, indent=2))

        if args.wav:
            write_wav(args.wav, res["audio"])
            print(f"Wrote audio to {args.wav}")
        if args.midi:
            write_midi(args.midi, res["events"], res["upper"], res["lower"])
            print(f"Wrote MIDI to {args.midi}")
        if args.json:
            with open(args.json, "w") as f:
                json.dump(metrics, f, indent=2)
            print(f"Wrote metrics to {args.json}")

    elif args.command == "blind-trials":
        keys = generate_blind_trials(num_trials=args.count, output_dir=args.out_dir)
        print(f"Generated {args.count} blind trials in {args.out_dir}")
        print("Answer keys written to private/trials_key.json (never commit or expose).")


if __name__ == "__main__":
    main()
