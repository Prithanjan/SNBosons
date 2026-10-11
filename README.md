# SNBosons: Quantum Song Round Trip & Entangled Harmony Duet

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 13 Passed](https://img.shields.io/badge/tests-13%20passed-brightgreen.svg)](tests/test_pipeline.py)

SNBosons (`qsong`) is an algorithmic music and quantum information pipeline bridging quantum state manipulation with acoustic counterpoint. The system operates across two core stages:

First, it implements an exact 11-qubit quantum memory round-trip. Monophonic melody notes are quantized onto a 16th-note grid, packed into pitch (7 bits) and duration (4 bits), and encoded into computational basis states using single-qubit Pauli-X gates. Projective measurement recovers the original melody with 100% deterministic fidelity ($P=1.0$), establishing lossless quantum state storage.

Second, it generates a two-voice counterpoint duet whose interval movements are governed by physical Bell state measurements. Melodic direction and register dynamically dictate measurement angles ($\alpha_t, \beta_t$). Under specific melodic contours, these angles align with the maximal Tsirelson violation of the CHSH inequality. Measurements on Bell pairs ($|\Phi^+\rangle = (|00\rangle + |11\rangle)/\sqrt{2}$) exhibit non-classical correlations ($S \approx 2.83$, exceeding the classical limit of 2.0). Outcomes dictate upper and lower voice shifts chosen from consonant intervals ({3, 4, 7, 8, 9} semitones in C major), strictly avoiding dissonant tritones.

To test human perceptual discrimination, SNBosons renders quantum duets alongside independent classical controls using additive sine synthesis, backing triads, bass, and calibrated RMS loudness matching (<0.5% error). It includes an automated double-blind testing protocol with isolated answer keys, and supports both local NumPy statevector simulation and cloud execution on IonQ trapped-ion QPUs and Qollab.

**Verification Boundary:** Superposition, entanglement, and CHSH violation ($S=2.83$) are verified. Audible quantum advantage, speed-up, and aesthetic superiority are not verified and remain pending human listening evaluation.

---

## Quickstart

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run automated test suite
```bash
pytest tests/test_pipeline.py -v
```

### 3. Run experiment via CLI
```bash
python -m qsong.cli run --mode quantum --seed 101 --wav output.wav --midi output.mid
```
