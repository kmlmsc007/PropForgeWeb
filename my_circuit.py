import sys
from qiskit import QuantumCircuit

# Ensure UTF-8 output encoding for circuit characters on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    # Create a Quantum Circuit with 2 qubits and 2 classical bits
    qc = QuantumCircuit(2, 2)

    # Put qubit 0 into superposition
    qc.h(0)

    # Entangle qubit 0 and qubit 1 to create Bell state (|00> + |11>)/sqrt(2)
    qc.cx(0, 1)

    # Measure qubits into classical bits
    qc.measure([0, 1], [0, 1])

    # Display the circuit diagram
    print("2-Qubit Bell State Circuit:")
    print(qc.draw(output="text"))

if __name__ == "__main__":
    main()
