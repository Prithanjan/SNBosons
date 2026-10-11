# SNBosons: Quantum Song Round Trip & Entangled Harmony Duet

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

SNBosons (`qsong`) is an algorithmic counterpoint pipeline coupling quantum information theory with strict acoustic calibration.

---

## Verified vs. Unverified Status

- **Verified:** 11-qubit basis state superposition encoding with exact deterministic decoding ($P=1.0 \pm 10^{-9}$), Bell state ($\Phi^+$) entanglement exhibiting CHSH parameter $S \approx 2.83$ (classical limit $2.0$), and consonance intervals restricted to $\{3, 4, 7, 8, 9\}$ semitones (0 tritones).
- **Not Verified:** Audible quantum advantage, quantum speed-up, or aesthetic superiority ("better" music). Human listening tests remain pending.

---

## Key Features

1. **Exact 11-Qubit Basis Round Trip:** Maps pitch ($7$ bits) and 16th-note duration ($4$ bits) into computational basis states and recovers them with zero distortion.
2. **Melody-Modulated Bell Measurement:** Extracts local contour angles ($\alpha_t \in \{0, \pi/4\}$) and register angles ($\beta_t \in \{\pm \pi/8\}$), measuring Bell pair $\Phi^+$ at maximal CHSH violation angles.
3. **Consonant Counterpoint:** Generates upper and lower harmony lines strictly in-key without tritone dissonances.
4. **Classical Control & Double-Blind Protocol:** Produces loudness-matched (RMS error $<0.5\%$) classical controls using independent random fair coins for rigorous blind listening tests.
5. **Hardware & Qollab Ready:** Pure NumPy local statevector simulator + Qiskit / IonQ / OpenQASM compilation bridge.

---

## Directory Layout

```
SNBosons/
├── docs/
│   ├── PRD_quantum_song_roundtrip_duet.md   # Product specification
│   ├── PRD_agents_quantum_song_duet.md      # Implementation specification
│   ├── USER_FLOW.md                         # Pipeline and user flow diagrams
│   └── IONQ_QOLLAB_DEPLOYMENT.md            # Hardware & cloud execution guide
├── qsong/
│   ├── __init__.py                          # Package exports
│   ├── encode.py                            # 11-qubit basis encoder & decoder
│   ├── measure.py                           # Bell state measurement & CHSH calculation
│   ├── harmony.py                           # Melody settings & consonant voice rules
│   ├── render.py                            # Additive synthesis, reverb & RMS matching
│   ├── midi_io.py                           # Multi-channel MIDI generation
│   ├── ionq_adapter.py                      # OpenQASM / Qiskit / IonQ bridge
│   └── cli.py                              # Unified CLI
├── tests/
│   └── test_pipeline.py                     # 11 automated reference checks
├── blind_trials/                            # Blind listening test audio pairs
├── private/                                 # Protected keys (git-ignored)
├── pyproject.toml
└── requirements.txt
```

---

## Installation & Quickstart

```bash
pip install -r requirements.txt
```

### Run automated verification
```bash
pytest tests/test_pipeline.py -v
```

### Run experiment
```bash
python -m qsong.cli run --seed 42 --mode quantum
```
