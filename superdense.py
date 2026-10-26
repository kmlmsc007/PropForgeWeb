import sys
from qiskit import QuantumCircuit

# Ensure UTF-8 output encoding for circuit characters on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    # Superdense Coding Protocol (Encoding the message '11')
    qc = QuantumCircuit(2, 2)
    
    # 1. Create Entanglement (Shared Bell pair)
    qc.h(0)
    qc.cx(0, 1)
    
    # 2. Encode message '11' by applying Z and X gates to Qubit 0
    qc.z(0)
    qc.x(0)
    
    # 3. Decode the message
    qc.cx(0, 1)
    qc.h(0)
    
    # 4. Measure
    qc.measure([0, 1], [0, 1])
    
    print("Superdense Coding Circuit (Target: 11):")
    print(qc.draw(output="text"))

if __name__ == "__main__":
    main()