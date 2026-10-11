# Product PRD: Quantum Song Round Trip and Entangled Harmony Duet

**Product Name:** SNBosons / qsong
**Version:** v1.0.0
**Target Audience:** Quantum computing researchers, algorithmic music composers, interactive installation artists, and listening study evaluators.

---

## 1. Executive Summary

SNBosons explores the intersection of quantum information theory and algorithmic musical counterpoint. Rather than generating arbitrary pitch sequences via unconstrained random walks, the system introduces two rigorous mechanisms:

1. **Deterministic Quantum Melody Memory (Round Trip):** An 11-qubit quantum state encoding scheme that maps pitch and duration into orthogonal computational basis states with $100\%$ fidelity.
2. **Entangled Counterpoint Harmony (Entangled Duet):** A two-voice harmony generation system whose musical motion is coupled via physical Bell state ($\Phi^+$) measurements. Under specific melodic contour triggers, the measurement angles align with the maximal Tsirelson violation of the CHSH inequality ($S \approx 2.828$), creating musical correlations that cannot be produced by independent classical random variables without shared communication.

The system is paired with a strict classical control baseline and double-blind listening protocol to test whether humans can detect quantum-entangled voice motion versus independent classical randomness.

---

## 2. Core Value Propositions

- **Mathematical Rigor Over Hype:** No claims of "quantum superiority" or "audible advantage." Every claim is grounded in verifiable mathematical bounds (exact basis state reconstruction, CHSH $S > 2.0$, and interval consonance in $\{3, 4, 7, 8, 9\}$ semitones).
- **Dual Runtime Support:** Runs offline using an exact statevector simulation engine (via standard NumPy) or in cloud quantum environments (IonQ hardware via Qiskit and Qollab).
- **Acoustic Integrity:** Equalized RMS loudness calibration ensuring that perceptual tests cannot be confounded by volume or spectral density disparities.

---

## 3. Product Architecture & User Journey

### 3.1 Input
- Monophonic melody provided as `[(pitch_midi, beats), ...]`.
- Supports standard quantization (16th notes) in C Major.

### 3.2 Processing Pipeline
1. **Event Parsing:** Conversion of beats to 16th note durations and running onsets.
2. **Quantum Round Trip:** Encoding pitch (7 bits) and duration (4 bits) into 11 qubits. State decoding verified with probability $1.0$.
3. **Melody Feature Extraction:** Dynamic extraction of measurement angles $\alpha_t \in \{0, \pi/4\}$ based on melodic pitch direction, and $\beta_t \in \{\pm \pi/8\}$ based on pitch register.
4. **Quantum / Classical Measurement:**
   - **Quantum Mode:** Sampling from entangled Bell pair $\Phi^+$ yielding correlated bits $(a_t, b_t) \in \{-1, +1\}^2$.
   - **Classical Mode:** Sampling from independent fair coins.
5. **Consonant Counterpoint Voice Generation:** Deriving upper voice (third/fifth above) and lower voice (third/fifth below) while strictly filtering out dissonant tritones.
6. **Multi-Track Synthesis & Rendering:** Additive sine wave synthesizer with ADSR envelopes, backing triad chords, and bass line. Rendered to 44.1 kHz WAV and standard Type 1 MIDI.
7. **Loudness Normalization:** RMS matching to within $0.5\%$ of target $0.1835$.

### 3.3 Blind Listening Study
- Automated generation of 10 A/B trials with randomized assignment and cryptographic separation of answer keys into `private/`.
- Participant evaluation form for confidence-scored perceptual discrimination.

---

## 4. Key Performance Indicators (KPIs)

| Metric | Target | Verification Method |
|---|---|---|
| Single-note round trip fidelity | $100\%$ ($1920/1920$) | Automated unit tests |
| Random melody round trip fidelity | $100\%$ ($50/50$) | Automated integration test |
| CHSH Parameter $S$ | $2.828 \pm 0.05$ | Shot measurement statistics |
| Dissonant tritone occurrences | $0$ across 100 seeds | Consonance validator |
| Audio RMS match error | $< 0.5\%$ | Dual WAV RMS analysis |
| IonQ/Qollab Circuit Validity | Valid OpenQASM / Qiskit Circuit | Static circuit analyzer |
