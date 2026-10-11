# IonQ & Qollab Deployment Guide for SNBosons

This document details how the SNBosons quantum circuits execute in local simulated environments, Jupyter-based collaborative platforms (e.g. Qollab), and physical IonQ trapped-ion QPUs (such as IonQ Aria and Forte).

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
     - For Alice (upper voice): $R_y(-2\alpha)$ on $q_0$.
     - For Bob (lower voice): $R_y(-2\beta)$ on $q_1$.
  3. Measure in computational basis $Z \otimes Z$.
- **Native IonQ Gates:**
  - Trapped-ion native 2-qubit gate is the Mølmer-Sørensen (MS) gate: $XX(\theta)$.
  - A CNOT maps directly to $R_y$, $XX(\pi/2)$, and single-qubit rotations.

---

## 2. Qollab & Jupyter Notebook Integration

In the Qollab environment, researchers can import the `qsong` package and choose between local fast NumPy simulation or remote execution:

```python
from qsong.ionq_adapter import create_bell_chsh_circuit, export_to_qasm, run_on_ionq
from qsong.harmony import TWINKLE, events_from_tune, settings

# 1. Convert melody into events and angles
events = events_from_tune(TWINKLE)
alphas, betas = settings(events)

# 2. Inspect the Bell CHSH circuit for the first note
qc = create_bell_chsh_circuit(alphas[0], betas[0])
print(qc)

# 3. Export to OpenQASM 2.0 / 3.0 for arbitrary quantum backends
qasm_str = export_to_qasm(qc)
print(qasm_str)
```

---

## 3. Physical IonQ Hardware Execution via Qiskit

To submit circuits to physical IonQ QPUs (Aria, Forte):

```python
import os
from qiskit_ionq import IonQProvider

# API key from environment variable
api_key = os.environ.get("IONQ_API_KEY")
if api_key:
    provider = IonQProvider(token=api_key)
    # Available backends: ionq_simulator, ionq_qpu.aria-1, ionq_qpu.forte-1
    backend = provider.get_backend("ionq_qpu.aria-1")
    
    # Run batch of melody note circuits
    # ...
```

---

## 4. Fallback & Noise-Robust Hybrid Mode

Because queue times and shot costs on real hardware can be high, `qsong` provides a dual-mode engine:
1. **Local Deterministic Simulator (`backend="local"`):** Pure NumPy linear algebra. Zero external cloud dependencies, instant execution, perfect fidelity check.
2. **Hardware/Noise Simulator (`backend="ionq"`):** Compiles to Qiskit QuantumCircuit or OpenQASM, supporting shot-based measurement and hardware execution.
