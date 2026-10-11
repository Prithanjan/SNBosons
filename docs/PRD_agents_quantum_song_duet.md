# Agent PRD: Quantum Song Round Trip and Entangled Harmony Duet

**Audience:** AI agents implementing, extending, or verifying this project.
**Companion document:** `PRD_quantum_song_roundtrip_duet.md` (product view). This file is the implementation spec.
**Status:** v1 prototype. Verified on one tune. Listening test pending.

---

## 0. Ground rules for agents

1. **Never overstate the quantum claim.** Verified: superposition, entanglement, and a CHSH value of 2.83 (classical limit 2). Not verified: audible quantum advantage, quantum speed-up, or that the music is "better". Every output or report must use these exact terms.
2. **Do not overwrite the blind-test keys.** Keys live in `private/` and must never be copied into the outputs folder. Regenerating blind trials requires the same fixed RNG seed (2026) so the key order stays consistent, or you must write a new key file with a new name and report it.
3. **Do not run the legacy entry points casually.** Several scripts execute other scripts with `exec()` and will rewrite output files. Read section 5 before running anything.
4. **Every result you report must come from a script run in this session**, with its output shown. Do not restate numbers from memory.
5. **Listening is a human task.** Agents cannot judge audio quality. Agents may only report objective audio measurements and must say so.

---

## 1. Goal

Build and verify a pipeline that:

- (a) takes a monophonic melody, encodes it into quantum basis states, decodes it back, and gets the identical melody (**exact round trip**);
- (b) adds two harmony voices whose movement is chosen by entangled quantum measurements, with settings derived from the melody (**entangled duet**);
- (c) renders the result to MIDI and WAV with a basic synth, backing chords, and bass;
- (d) provides a classical control with the same voice rules and independent random coins, and a blind listening protocol to compare them.

---

## 2. Algorithm

### 2.1 Input
- Monophonic note list `TUNE = [(pitch_midi, beats), ...]`.
- v1 constraints: key of C major; durations quantized to 16th notes; pitches 0–127; durations 1–15 sixteenths.
- Reference tune: Twinkle Twinkle Little Star, 42 notes (`TWINKLE` in `tests/test_pipeline.py`).

### 2.2 Event conversion
```python
d16 = round(beats * 4)          # duration in sixteenths, must be 1..15
onset16 = running sum of d16     # onset in sixteenths
events = [(pitch, d16, onset16), ...]
```

### 2.3 Encoding (round trip, stage 1)
- Each note uses **11 qubits**: bits 0–6 hold pitch (7 bits), bits 7–10 hold duration (4 bits).
- `value = pitch | (d16 << 7)`.
- Circuit: start in |0…0⟩, apply an **X gate on every qubit k where bit k of value is 1**. Nothing else.
- Decoding: measure, read the basis index `i`, then `pitch = i & 0x7F`, `d16 = i >> 7`.
- **Exactness condition:** the output probability on the target basis state must equal 1 (tolerance 1e-9). Any other result is a failure.

### 2.4 Settings derived from the melody (stage 2)
For each note index `t` with pitch `p_t` and previous pitch `p_{t-1}` (use `p_0` for the first note):
```python
alpha_t = pi/4   if p_t < p_{t-1}     # melody moves down
alpha_t = 0      otherwise            # up or unchanged
beta_t  = +pi/8  if p_t >= 65         # F4 or higher
beta_t  = -pi/8  otherwise
```
These four combinations (0 or π/4 with +π/8 or −π/8) are what the CHSH test requires. On Twinkle Twinkle, all four occur (counts 9, 16, 6, 11).

### 2.5 Entangled measurement (stage 2, quantum)
- Initial state: Bell pair Φ+ = (|00⟩ + |11⟩)/√2.
- Measurement basis for angle θ: outcome 0 → vector (cos θ, sin θ); outcome 1 → (−sin θ, cos θ).
- Joint probability: `P(x, y) = |(basis_x(alpha_t) ⊗ basis_y(beta_t)) · Φ+|²`.
- Sample one (x, y) pair per note from P. Map outcome 0 → +1, outcome 1 → −1. Result: `(a_t, b_t)`.
- **Expected correlation:** `E = P(same) − P(different) = cos(2(alpha_t − beta_t))`.

### 2.6 Harmony voices (stage 2, rules)
Use scale-based consonant choices, first in key:
```python
pick(p, options) = first (p + o) for o in options where (p + o) mod 12 is in C major

upper_t = pick(p_t, [7, 8, 9])  if a_t = +1    (fifth above)
upper_t = pick(p_t, [4, 3])     if a_t = −1    (third above)
lower_t = pick(p_t, [-7,-8,-9]) if b_t = +1    (fifth below)
lower_t = pick(p_t, [-4,-3])    if b_t = −1    (third below)
```
- **Invariant:** every interval melody→upper and melody→lower is in {3, 4, 7, 8, 9}. Tested for 100 seeds.
- **Do not** use fixed scale-step offsets. They produce tritones (for example, four scale steps below F gives B, a tritone). This bug was found and fixed.

### 2.7 Classical control
Same settings, same voice rules, but `(a_t, b_t)` drawn from **independent fair coins**: `a_t, b_t` each uniform on {+1, −1}. Loudness and the number of notes must match the quantum version.

### 2.8 Backing and rendering (stage 3)
- Chords: C, F, G, C; one chord every 4 beats (16 sixteenths); three notes each in octave 3–4 (MIDI 48–62).
- Bass: chord root one octave below (MIDI root − 12).
- Voice synthesis: additive sine partials; attack 0.01 s; exponential decay `exp(−1.2 t)`.
  - Melody: partials [1, 0.45, 0.15], amplitude 0.35.
  - Upper/lower harmony: partials [1, 0.5, 0.25], amplitude 0.18.
  - Chords: partials [1, 0.3], amplitude 0.12.
  - Bass: partials [1, 0.1], amplitude 0.25.
- Sample rate 44100 Hz. Tempo 100 BPM. 16th = 0.15 s.
- Optional reverb: exponentially decaying Gaussian noise impulse response, 1.5 s long, decay rate 4.0, convolved with melody and harmony; wet mix 0.35.
- **Loudness matching:** scale each mix to the same RMS (target 0.1835) before writing. Then check peak < 1.0 to avoid clipping. Do not normalize by peak alone, because that changes RMS.

### 2.9 MIDI output
- Channel 0: melody. Channel 1: chords. Channel 2: bass. Channel 3: harmony.
- Ticks per beat 480. Note-on at `onset16 * 120` ticks. Note-off at `(onset16 + d16) * 120 − 10` ticks.
- Tempo meta message: 100 BPM.

---

## 3. Verified results (reference values)

| Quantity | Value | Test |
|---|---|---|
| Single-note round trip failures | 0 of 1920 (128 × 15) | `test_pipeline.py` |
| Random melody round trips | 50 of 50 exact | `test_pipeline.py` |
| MIDI round trip, Twinkle | 42 of 42 pitches | `test_pipeline.py` |
| Bell correlation vs theory | matches `cos(2(a−b))` over 9×9 grid | `test_pipeline.py` |
| CHSH S, theoretical settings | 2.828 | `test_pipeline.py` |
| CHSH S, measured from shots (Twinkle) | 2.830 (theory max 2.828; difference is sampling noise) | `duet.py` |
| Harmony consonance | 100 of 100 seeds, all intervals in {3,4,7,8,9} | `test_pipeline.py` |
| Audio pitch check (quantum duet) | 42 of 42 notes within 1 semitone of original melody | `duet_audio.py` |
| Motion, quantum duet | upper and lower voices move the same direction 53% of the time | `duet_audio.py` |
| Motion, independent duet | same direction 84% of the time | `duet_audio.py` |
| RMS match | 0.2038 vs 0.2037 (quantum vs independent) | `duet_audio.py` |

---

## 4. Listening protocol (human task)

- Trials: `blind_trials/trial_01..10` (A/B WAV pairs). Each pair: quantum duet vs independent duet, same melody, RMS matched to 0.00%.
- Seeds: quantum seed = 100 + i, independent seed = 100 + i, for trial i. Order randomized with RNG seed 2026.
- The listener marks which clip has more independent-sounding harmony, with confidence 1–3.
- Pass criterion (PRD): at least 8 of 10 correct. Chance = 5 of 10.
- Agents must not score a listening test without the human's answer sheet and must not reveal the key before answers are recorded.

---

## 5. Code map and target architecture

Logic refactored into modular `qsong/` package:
- `qsong/encode.py`: basis state encoding/decoding.
- `qsong/measure.py`: Bell pair measurement, CHSH correlation, IonQ/Qiskit backend adapter.
- `qsong/harmony.py`: settings extraction and consonant voice selection.
- `qsong/render.py`: additive synthesis, reverb, RMS loudness normalization.
- `qsong/midi_io.py`: MIDI output generation.
- `qsong/cli.py`: Unified command line interface.
- `qsong/ionq_adapter.py`: IonQ hardware and Qollab execution adapter.

---

## 6. Target Interfaces

```python
def events_from_tune(tune: list[tuple[int, float]]) -> list[tuple[int, int, int]]: ...
def encode_note(pitch: int, d16: int) -> np.ndarray: ...          # statevector
def decode_index(i: int) -> tuple[int, int]: ...
def settings(events: list[tuple[int, int, int]]) -> tuple[list[float], list[float]]: ...
def sample_bell_pair(alpha: float, beta: float, rng) -> tuple[int, int]: ...
def duet_voices(events: list[tuple[int, int, int]], pairs: list[tuple[int, int]]) -> tuple[list[int], list[int]]: ...
def render_mix(events: list[tuple[int, int, int]], upper: list[int], lower: list[int], mode: str) -> np.ndarray: ...
def write_midi(path: str, events: list[tuple[int, int, int]], upper: list[int], lower: list[int]) -> None: ...
def run_experiment(tune: list[tuple[int, float]], seed: int, mode: str) -> dict: ...
```

---

## 7. Acceptance Criteria

1. `test_pipeline.py` passes 11 of 11 (or more, if tests are added).
2. The round trip is exact for every note of every test tune.
3. For every harmony choice, every interval is in {3, 4, 7, 8, 9}, checked on rendered audio as well as note list.
4. The quantum and independent renders have RMS matched to within 0.5%, and peak below 1.0.
5. The CHSH value is reported from a fresh run, with number of shots and seed used.
6. No file in the outputs folder contains an answer key.
7. The report states plainly what was not verified.
