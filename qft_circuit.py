import math
import sys
from qiskit import QuantumCircuit

# Ensure UTF-8 output encoding for circuit characters on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    # 2-Qubit Quantum Fourier Transform (QFT)
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cp(math.pi / 2, 1, 0)
    qc.h(1)
    qc.swap(0, 1)
    qc.measure([0, 1], [0, 1])

    print("2-Qubit QFT Circuit:")
    print(qc.draw(output="text"))

if __name__ == "__main__":
    main()
