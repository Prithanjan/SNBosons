# Running SNBosons on Qollab (qollab.xyz)

[Qollab](https://qollab.xyz) is an in-browser quantum playground running **Python 3.14 with Qiskit 2.x** via Pyodide.

Unlike Google Colab or local scripts, **Qollab requires ZERO API keys or pip installs**. You select your quantum hardware or simulator directly in Qollab's **Select QPU** dialog, and Qollab injects a pre-created `backend` object directly into `main.py`.

---

## 🚀 Quickstart (30 Seconds)

1. Open **[qollab.xyz](https://qollab.xyz)** in your browser.
2. Click **+ New Project** and select **Python / Qiskit** (or **Upload your own files** and upload `main.py`).
3. In the **Code** tab, paste the code from [`main.py`](main.py).
4. Click **Run** at the top right.
5. In the **Select QPU** dialog:
   - Under **Run settings**, adjust parameters if desired:
     - **Shots**: Default `1024`
     - **Transpose**: Transposition in semitones (e.g. `0` for C major)
     - **Full Song**: `False` for quick 1-measure Bell test; `True` for full 16-measure duet
   - Choose your runner:
     - **BasicSimulator** (instant, built-in, free)
     - **IonQ Simulators** (free remote simulator)
     - **IonQ Aria / Forte** (trapped-ion hardware)
6. Click **Run** inside the dialog.
7. Watch the quantum counterpoint synthesis and duet score print directly to the console!

---

## ⚛️ How the Code Works

### 1. Pre-Created Backend (`backend`)
```python
# In Qollab, `backend` is pre-injected into the global scope.
# No IonQProvider, no tokens, no os.environ["IONQ_API_KEY"].
job = backend.run(qc, shots=1024)
counts = job.result().get_counts()
```

### 2. Single-Job Rule for IonQ Hardware
IonQ backends on Qollab enforce **one job per run**. When `full_song=True`, `main.py` constructs all 16 measure circuits and submits them in a **single batched call**:
```python
job = backend.run(circuits, shots=shots)  # All 16 measures in 1 job
```

### 3. Interactive UI Form via `main()`
Qollab parses the signature of `main()` to render input fields in the "Select QPU" modal:
```python
def main(shots: int = 1024, transpose: int = 0, full_song: bool = False, verbose: bool = True):
    ...
```
*(The `def main(` line must be at column 0 on a single line with `int`, `float`, `str`, or `bool` type annotations).*

---

## 🎼 Quantum Counterpoint Mapping
- **Qubit 0 (Melody):** Rotated by angle $\alpha = \frac{\text{interval}}{12} \pi$.
- **Qubit 1 (Counterpoint):** Entangled via Bell pair $|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$, rotated by harmonic interval $\beta = \frac{\text{interval} + 7}{12} \pi$.
- **Measurement:** Decoded into strictly consonant counterpoint intervals (unisons, thirds, fifths, octaves).
