# IonQ & Qollab Deployment Guide for SNBosons

This document details how the SNBosons quantum circuits execute in local simulated environments, the **Qollab** in-browser quantum playground ([qollab.xyz](https://qollab.xyz)), and physical **IonQ trapped-ion QPUs** (IonQ Aria and Forte).

---

## 1. Circuit Architectures

### 1.1 Exact Memory Circuit (11 Qubits)
- **Qubits:** 11 qubits ($q_0 \dots q_{10}$).
- **Gates:** Single-qubit Pauli-X gates applied based on the binary decomposition of $\text{value} = \text{pitch} \mid (d_{16} \ll 7)$.
- **Depth:** 1 (fully parallel single-qubit gates).
- **Physical Trapped-Ion Mapping:**
  - IonQ natively supports all-to-all connectivity. Since the memory circuit contains only parallel single-qubit $X$ gates, native 1-qubit gate fidelity on IonQ is typically $> 99.9\%$.
  - State readouts measure computational basis directly.

### 1.2 Bell-Pair & Rotated Basis Measurement Circuit (2 Qubits)
- **Qubits:** 2 qubits ($q_0, q_1$).
- **Gates:**
  1. Prepare $|\Phi^+\rangle$: Hadamard $H(q_0)$, followed by CNOT $(q_0 \to q_1)$.
  2. Rotate measurement bases:
     - For Alice (upper melody voice): $R_y(-2\alpha)$ on $q_0$.
     - For Bob (lower counterpoint voice): $R_y(-2\beta)$ on $q_1$.
  3. Measure in computational basis $Z \otimes Z$.
- **Native IonQ Gates:**
  - Trapped-ion native 2-qubit gate is the Mølmer-Sørensen (MS) gate: $XX(\theta)$.
  - A CNOT maps directly to $R_y$, $XX(\pi/2)$, and single-qubit rotations.
  - Generates Bell violation $S = 2\sqrt{2} \approx 2.8284 > 2.0$.

---

## 2. In-Browser Quantum Execution on Qollab (qollab.xyz)

[Qollab](https://qollab.xyz) is an in-browser quantum development environment running **Python 3.14 with Qiskit 2.x** via Pyodide.

### 2.1 The Zero-Key Execution Model
Unlike typical cloud services, **Qollab does NOT require API keys, credentials, or manual provider instantiations**. 

1. **Pre-Created `backend` Variable:**
   When you press **Run** in Qollab, the **Select QPU** dialog opens. You select the target runner:
   - Built-in **BasicSimulator** (instant, local)
   - **IBM Noise Models**
   - **IonQ Simulators** (remote trapped-ion simulator, free)
   - **IonQ Hardware** (Aria / Forte)
   
   Qollab automatically authenticates and injects the selected backend into the global scope as **`backend`**.
   ```python
   # On Qollab: Do NOT write provider = IonQProvider(token=...)
   # `backend` is already pre-created and ready to use!
   job = backend.run(circuit, shots=1024)
   counts = job.result().get_counts()
   ```

2. **One Job Per Run on IonQ:**
   IonQ hardware and remote simulator backends on Qollab enforce a strict **one job per run** rule to prevent credit exhaustion. Multiple calls to `backend.run()` in a single execution will throw an error. 
   
   To synthesize all 16 measures of a melody (e.g. *Ode to Joy*), **pass the full list of circuits into a single `backend.run()` call**:
   ```python
   # Batch all measure circuits in 1 job
   circuits = [build_bell_counterpoint_circuit(p) for p in melody]
   job = backend.run(circuits, shots=shots)
   ```

3. **Interactive UI Form via `def main(...)`:**
   Qollab parses the signature of `main()` in `main.py` and renders interactive input fields under **Run settings** in the "Select QPU" modal:
   ```python
   def main(shots: int = 1024, transpose: int = 0, full_song: bool = False, verbose: bool = True):
       ...
   ```
   *(Note: The signature must start at column 0 on a single line, with typed parameters: `int`, `float`, `str`, or `bool`).*

### 2.2 How to Run SNBosons on Qollab
1. Download or copy [`qollab/main.py`](../qollab/main.py) (also accessible via `/api/qollab?format=py` on the live web app).
2. Go to **[qollab.xyz](https://qollab.xyz)** $\to$ Click **+ New Project** $\to$ **Python / Qiskit**.
3. Paste into `main.py` $\to$ Click **Run**.
4. Select your QPU in the dialog and view the synthesized duet in the console!

---

## 3. Standalone Python / Colab Hardware Execution via Qiskit-IonQ

For researchers running outside Qollab (e.g. in local terminal scripts, HPC clusters, or Google Colab) who manage their own IonQ API keys:

```python
import os
from qiskit_ionq import IonQProvider

api_key = os.environ.get("IONQ_API_KEY", "YOUR_API_KEY")
provider = IonQProvider(token=api_key)
backend = provider.get_backend("ionq_qpu.aria-1")

from qollab.main import build_bell_counterpoint_circuit

qc = build_bell_counterpoint_circuit(pitch=64, measure_idx=1)
job = backend.run(qc, shots=1000)
print("Job ID:", job.job_id())
print("Counts:", job.result().get_counts())
```

---

## 4. Fallback & Noise-Robust Hybrid Mode

Because queue times and shot costs on real hardware can be high, `SNBosons` provides a three-tier architecture:
1. **In-Browser Web Audio & NumPy Simulator:** Zero-latency offline client simulation with Tone.js polyphonic audio.
2. **Qollab Zero-Key Playground:** Browser-native Qiskit 2.x execution on IonQ simulators/QPUs without credentials.
3. **Vercel Serverless Qiskit API (`/api/simulate`, `/api/ionq`):** Emulated Bell statevector sampling and OpenQASM 2.0 generation with $S \ge 2.0$ CHSH violation guarantees.
