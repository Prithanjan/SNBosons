# 🎵 SNBosons — How to Play & User Guide

Welcome to **SNBosons**, the world's first interactive quantum synthesizer that uses quantum physics and entanglement to compose multi-voice Renaissance counterpoint in real time.

Live Web App: **[https://snbosons.vercel.app](https://snbosons.vercel.app)**

---

## 🏛️ The Core Concept: The 3 Musical Voices

Instead of using an AI language model that "guesses" harmony notes, SNBosons links your melody to two entangled quantum particles.

| Voice | Color | Instrument | Controlled By | Description |
|---|---|---|---|---|
| **Voice 1: Cantus Firmus** | 🟠 **Orange** | Bell / Lead | **You (Piano Roll)** | The lead melody. You compose this in the grid or pick a preset. |
| **Voice 2: Discantus** | 🟣 **Purple** | Flute / Soprano | **Qubit $q_0$ (Wire 0)** | The upper harmony voice singing above your melody. |
| **Voice 3: Bassus** | 🟡 **Amber** | Cello / Bass | **Qubit $q_1$ (Wire 1)** | The lower bass harmony anchoring the chord below. |

---

## 🎛️ Tab 1: Studio & Live Roll

### 1. Transport & Audio Playback
- **▶ Play Audio:** Starts the playback loop, synthesizes acoustic partials, and activates the live oscilloscope.
- **⏹ Stop:** Halts synthesis and resets the playhead.
- **Engine Switcher:**
  - `⚡ WebAudio`: Instant, zero-latency in-browser synthesizer.
  - `🐍 Qiskit API`: Simulates quantum states through the Vercel serverless Qiskit backend (`/api/simulate`).
  - `⚛️ IonQ QPU`: Simulates or dispatches measurements to an IonQ Aria-1 trapped-ion quantum computer (`/api/ionq`).

### 2. Presets & 12-Key Diatonic Signatures
- **Presets:** Quick-load classical tunes:
  - *Ode to Joy* (Beethoven)
  - *Twinkle Twinkle Little Star* (Mozart)
  - *Bach Minuet in G*
  - *Custom Melody*
- **Key Selector Popover:** Change key signature on the fly (e.g. C Major, G Major, D Minor, A Minor, F Major). All quantum harmony choices automatically transpose and clamp to consonant scale tones—**tritones are physically forbidden**.

### 3. Voice Isolation & Solo Controls
Click any button in the Voice Architecture bar to isolate individual voices:
- **All Three Voices:** Listen to the complete 3-part quantum duet.
- **Solo Melody (Cantus):** Hear only your lead melody.
- **Solo Voice 2 ($q_0$):** Hear only the upper quantum flute line.
- **Solo Voice 3 ($q_1$):** Hear only the lower quantum cello bass.

### 4. Interactive Piano Roll Grid
- **Add Notes:** Click on any empty cell in the grid to place a note.
- **Erase Notes:** Click on an existing orange note to remove it.
- **Automatic Harmony Update:** When you edit the lead melody, both quantum voices recalculate their harmonic interval angles $\alpha$ and $\beta$ in real time.

---

## ⚛️ Tab 2: Quantum Gate Inspector

This is where you physically wire the quantum circuit that writes the rules of harmony.

```
q[0] (Upper Flute): --[ H ]--*--[ Ry(alpha) ]--[ M ]--
                             |
q[1] (Lower Cello): ---------+--[ Ry(beta)  ]--[ M ]--
```

### 1. What the Quantum Gates Do
- **H (Hadamard):** Creates quantum superposition. Turns a fixed state into a 50/50 quantum coin toss.
- **CNOT (+):** The **Entanglement Bridge**. Entangles wire $q_0$ and wire $q_1$ together.
- **X (Pauli-X):** Bit-flip / NOT gate. Flips $0 \leftrightarrow 1$.
- **Z (Pauli-Z):** Phase-flip gate. Flips quantum phase without altering probability magnitudes.
- **Ry (Rotation-Y):** Rotates the measurement angle, allowing smooth variation between close 3rds and open 5ths.

### 2. How Quantum Measurement Collapses Into Music
When the quantum circuit measures the two particles at each beat, it produces one of 4 possible 2-bit states:

| Measured State | Upper Voice ($q_0$) | Lower Voice ($q_1$) | Chord Character |
|---|---|---|---|
| **$\|00\rangle$** | 3rd above | 3rd below | **Closed 3rds:** Sweet, intimate, consonant |
| **$\|01\rangle$** | 3rd above | Octave / 5th below | **Upper 3rd / Bass 8ve:** Balanced open chord |
| **$\|10\rangle$** | 5th above | 3rd below | **Upper 5th / Bass 3rd:** Bright, resonant harmony |
| **$\|11\rangle$** | 5th above | Octave / 5th below | **Wide Open 5th/8ve:** Expansive, majestic cathedral sound |

### 3. Quick-Load Quantum Templates
- **EPR Bell Pair ($\Phi^+$):** Maximum parallel entanglement. Forces the circuit into only $\|00\rangle$ (50%) and $\|11\rangle$ (50%). The voices always move together. Violates classical Bell inequality ($S \approx 2.828 > 2.0$).
- **Contrary Bell Pair ($\Psi^+$):** Maximum contrary motion. Forces the circuit into only $\|01\rangle$ and $\|10\rangle$. When the top voice opens wide, the bass tightens.
- **Unentangled ($H + H$):** Two independent quantum coin flips. All 4 states occur with 25% equal probability.
- **Ground ($\|00\rangle$):** Forces both voices into pure parallel 3rds with 100% certainty.
- **Bit Flip $q_0$ / $q_1$:** Locks one voice open while allowing the other to vary.

### 4. Circuit Toolbar Actions
- **Audition Circuit Harmony:** Instantly plays 4 test chords (C, E, G, C) to audition your quantum gate distribution without playing the whole song.
- **Copy Circuit to Song / Tab 1:** Binds your custom quantum circuit to the active playback engine in Tab 1.
- **Copy OpenQASM 2.0:** Copies the exact quantum circuit code to your clipboard for execution in Qiskit, IBM Quantum, or IonQ.

---

## 🔬 Tab 3: Quantum Counterpoint & Hardware Specs

### 1. What is Closed-Loop Counterpoint?
In classical music, *Species Counterpoint* forbids parallel fifths and harsh dissonances (tritones). Traditional computer music must use rigid classical if-else rules. 

In SNBosons, **quantum non-locality replaces the rulebook**. By entangling particles and tuning measurement angles based on melodic motion:
- Descending melody steps rotate the measurement basis by $\alpha = \pi/4$.
- High registers rotate the measurement basis by $\beta = \pi/8$.
- The quantum measurement physically prevents the voices from choosing dissonant combinations across space without any hardcoded if-statements.

### 2. Running on IonQ Hardware & Qollab
- **Run on IonQ Aria-1 (Simulated/QPU):** Submits the Bell state counterpoint circuit directly to IonQ's API or runs a high-fidelity 32-qubit Aria-1 emulator.
- **Download Qollab Notebook (.ipynb):** Downloads a pre-configured Jupyter notebook ready to upload to Qollab or Google Colab with `qiskit` and `qiskit-ionq`.
- **Test Serverless Qiskit API:** Verifies the Vercel serverless Python simulator (`/api/simulate`) in real time.

### 3. Exporting MIDI
- Click **"Export MIDI File (.mid)"** in Tab 1 to download a Type 1 Standard Multi-Track MIDI file with individual tracks:
  - Track 1: Conductor (Tempo & Time Signature)
  - Track 2: Cantus Firmus (Channel 0)
  - Track 3: Upper Voice $q_0$ (Channel 1)
  - Track 4: Lower Voice $q_1$ (Channel 2)
- Drag and drop this MIDI file directly into Ableton Live, FL Studio, Logic Pro, or Reaper.

---

## ⚡ Quickstart Cheat Sheet

1. Open **[snbosons.vercel.app](https://snbosons.vercel.app)**.
2. Click **▶ Play Audio** to hear Ode to Joy with entangled quantum harmony.
3. Switch to **Tab 2 (Quantum Gate Inspector)**.
4. Click **Contrary Bell Pair ($\Psi^+$)** template $\to$ Click **Audition Circuit Harmony**.
5. Click **Copy Circuit to Song / Tab 1** $\to$ Return to Tab 1 and hit Play to hear the new quantum flavor!
