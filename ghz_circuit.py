import sys
from qiskit import QuantumCircuit

# Ensure UTF-8 output encoding for circuit characters on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    # Create a Quantum Circuit with 3 qubits
    qc = QuantumCircuit(3, 3)
    
    # Put qubit 0 into superposition
    qc.h(0)
    
    # Entangle qubit 0 with 1, and 1 with 2 (GHZ state)
    qc.cx(0, 1)
    qc.cx(1, 2)
    
    # Measure all 3 qubits
    qc.measure([0, 1, 2], [0, 1, 2])
    
    # Display the circuit diagram
    print("3-Qubit GHZ State Circuit:")
    print(qc.draw(output="text"))

if __name__ == "__main__":
    main()