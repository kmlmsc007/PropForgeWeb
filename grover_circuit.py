import sys
from qiskit import QuantumCircuit

# Ensure UTF-8 output encoding for circuit characters on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    # 2 Search Qubits (0, 1) + 1 Workspace Ancilla Qubit (2)
    qc = QuantumCircuit(3, 3)

    # 1. Prepare workspace ancilla in |-⟩ = (|0⟩ - |1⟩)/√2
    qc.x(2)
    qc.h(2)

    # 2. Initialize search qubits in uniform superposition
    qc.h(0)
    qc.h(1)

    # 3. Grover Oracle (marking target state |11⟩ via CCX phase kickback)
    qc.ccx(0, 1, 2)

    # 4. Grover Diffusion operator on search qubits
    qc.h(0)
    qc.h(1)
    qc.x(0)
    qc.x(1)
    qc.h(1)
    qc.cx(0, 1)
    qc.h(1)
    qc.x(0)
    qc.x(1)
    qc.h(0)
    qc.h(1)

    # 5. Measure search qubits
    qc.measure([0, 1], [0, 1])

    print("3-Qubit Grover Search Circuit with Workspace Ancilla (Marked: |11>):")
    print(qc.draw(output="text"))

if __name__ == "__main__":
    main()
