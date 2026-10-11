"""
SNBosons — Quantum Bell Counterpoint on Qollab (https://qollab.xyz)
==================================================================
Runs directly inside Qollab's in-browser Python/Qiskit runtime (Python 3.14 + Qiskit 2.x).
Zero API keys needed: Qollab injects the pre-created `backend` global when you select
your QPU/simulator in the "Select QPU" modal.

Single-job IonQ rule compliant: multi-measure circuits are batched into a single backend.run() call.
"""

import math

# Qollab provides `backend` globally when you click "Run" and choose a QPU/simulator.
# Fallback provider if running offline or in local Python:
if "backend" not in globals():
    try:
        from qiskit.providers.basic_provider import BasicProvider
        backend = BasicProvider().get_backend("basic_simulator")
    except Exception:
        try:
            from qiskit import Aer
            backend = Aer.get_backend("aer_simulator")
        except Exception:
            backend = None

from qiskit import QuantumCircuit

# Ode to Joy opening theme (MIDI note numbers)
ODE_TO_JOY = [
    64, 64, 65, 67,  # E4, E4, F4, G4
    67, 65, 64, 62,  # G4, F4, E4, D4
    60, 60, 62, 64,  # C4, C4, D4, E4
    64, 62, 62, 62   # E4, D4, D4, D4
]

PITCH_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def midi_to_note_name(midi_val: int) -> str:
    octave = (midi_val // 12) - 1
    return f"{PITCH_NAMES[midi_val % 12]}{octave}"


def build_bell_counterpoint_circuit(pitch: int, measure_idx: int = 1) -> QuantumCircuit:
    """
    Constructs a 2-qubit Bell pair Phi+ rotated by pitch interval angles.
    q0 = Lead Melody Voice
    q1 = Entangled Counterpoint Voice (Species Harmony)
    """
    # Interval angle relative to C4 (60)
    interval = (pitch - 60) % 12
    alpha = (interval / 12.0) * math.pi
    beta = ((interval + 7) % 12 / 12.0) * math.pi  # Perfect fifth harmonic relation

    qc = QuantumCircuit(2, 2, name=f"M{measure_idx}_{midi_to_note_name(pitch)}")
    # Entangle Bell pair Phi+ = (|00> + |11>) / sqrt(2)
    qc.h(0)
    qc.cx(0, 1)
    # Basis rotations encoding melody & species counterpoint
    qc.ry(-2.0 * alpha, 0)
    qc.ry(-2.0 * beta, 1)
    # Measurement
    qc.measure([0, 1], [0, 1])
    return qc


def decode_counterpoint_note(lead_midi: int, outcome: str) -> int:
    """
    Decodes 2-qubit measurement outcome ('c1 c0') into acoustic counterpoint pitch.
    '00' -> Unison / Octave (+0)
    '11' -> Harmonic Third (+4)
    '01' -> Perfect Fifth (+7)
    '10' -> Perfect Octave (+12)
    """
    offsets = {
        "00": 0,
        "11": 4,
        "01": 7,
        "10": 12,
    }
    # Reverse string if Qiskit returns little-endian c1c0
    return lead_midi + offsets.get(outcome, 7)


def main(shots: int = 1024, transpose: int = 0, full_song: bool = False, verbose: bool = True):
    """
    Qollab main entry point.
    Signature must be on one single line starting at column 0 for Qollab form parser.
    """
    print("=" * 64)
    print("  SNBosons — Quantum Bell Counterpoint Duet")
    print("  Qollab In-Browser Quantum Execution (qollab.xyz)")
    print("=" * 64)

    if backend is None:
        print("[ERROR] No quantum backend found. Please select a QPU in Qollab.")
        return

    backend_name = getattr(backend, "name", lambda: str(backend))()
    print(f"[*] Target QPU / Simulator : {backend_name}")
    print(f"[*] Shot Budget            : {shots}")
    print(f"[*] Transpose (semitones)  : {transpose:+d}")
    print(f"[*] Full Song Mode         : {full_song}")
    print("-" * 64)

    if not full_song:
        # Single representative measure demonstration
        lead_pitch = ODE_TO_JOY[0] + transpose
        print(f"[*] Measure 1 Lead Note: {midi_to_note_name(lead_pitch)} (MIDI {lead_pitch})")
        qc = build_bell_counterpoint_circuit(lead_pitch, measure_idx=1)

        print("\n--- Quantum Counterpoint Circuit ---")
        try:
            print(qc.draw("text"))
        except Exception:
            print(qc)

        print("\n[*] Submitting circuit to backend...")
        job = backend.run(qc, shots=shots)
        result = job.result()
        counts = result.get_counts()
        print(f"[*] Quantum Measurement Counts: {counts}")

        # Compute Bell Correlation and Harmonic Probabilities
        total = sum(counts.values()) if counts else 1
        p00 = counts.get("00", 0) / total
        p01 = counts.get("01", 0) / total
        p10 = counts.get("10", 0) / total
        p11 = counts.get("11", 0) / total

        # Correlation E = (P00 + P11) - (P01 + P10)
        corr_e = (p00 + p11) - (p01 + p10)
        print(f"\n[*] Bell State Quantum Correlation E : {corr_e:+.4f}")
        print(f"[*] Consonance Rate (Same Basis)      : {(p00 + p11) * 100:.1f}%")

        # Pick most frequent outcome
        top_outcome = max(counts, key=counts.get)
        cp_pitch = decode_counterpoint_note(lead_pitch, top_outcome)
        print(f"[*] Dominant Quantum Measurement    : |{top_outcome}>")
        print(f"[*] Synthesized Harmony Note        : {midi_to_note_name(cp_pitch)} (MIDI {cp_pitch})")
        print("=" * 64)

    else:
        # Full 16-measure song execution
        # NOTE: IonQ Qollab backends enforce ONE job per run.
        # We submit ALL 16 measure circuits in a single backend.run([qc1, ...]) call!
        print("[*] Generating all 16 measure circuits for Ode to Joy...")
        circuits = []
        lead_pitches = []
        for i, raw_pitch in enumerate(ODE_TO_JOY):
            p = raw_pitch + transpose
            lead_pitches.append(p)
            circuits.append(build_bell_counterpoint_circuit(p, measure_idx=i + 1))

        print(f"[*] Submitting batch of {len(circuits)} circuits in 1 job (IonQ compliant)...")
        job = backend.run(circuits, shots=shots)
        result = job.result()

        print("\n================ DUET COUNTERPOINT SCORE ================")
        print(f"{'M#':<4} | {'Lead Voice':<12} | {'Quantum CP':<12} | {'Top Basis':<10} | {'Counts'}")
        print("-" * 64)

        for i, (lead_p, qc) in enumerate(zip(lead_pitches, circuits)):
            try:
                cnts = result.get_counts(qc)
            except Exception:
                cnts = result.get_counts()[i] if isinstance(result.get_counts(), list) else result.get_counts()

            top_meas = max(cnts, key=cnts.get)
            cp_pitch = decode_counterpoint_note(lead_p, top_meas)
            m_label = f"M{i+1}"
            lead_label = f"{midi_to_note_name(lead_p)} ({lead_p})"
            cp_label = f"{midi_to_note_name(cp_pitch)} ({cp_pitch})"
            print(f"{m_label:<4} | {lead_label:<12} | {cp_label:<12} | {top_meas:<10} | {cnts}")

        print("=" * 64)
        print("[SUCCESS] Full 16-measure quantum duet synthesized on Qollab!")


if __name__ == "__main__" and "backend" not in globals():
    main()
