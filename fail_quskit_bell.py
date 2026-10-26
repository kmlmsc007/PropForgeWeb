from qiskit import QuantumCircuit

def create_faulty_bell_state():
    """
    Deliberately faulty Bell State for QuCheck UI testing.
    Intended state: (|00> + |11>) / sqrt(2)
    Actual state:   (|00> + |01> + |10> + |11>) / 2
    """
    # Initialize a 2-qubit circuit
    qc = QuantumCircuit(2)
    
    # Step 1: Put qubit 0 into superposition (Correct)
    qc.h(0)
    
    # Step 2: THE BUG
    # Instead of entangling the qubits with a CNOT gate ( qc.cx(0, 1) ),
    # the developer accidentally applies a second Hadamard to qubit 1.
    qc.h(1) 
    
    # Note: No measurements are added here assuming your QuCheck backend 
    # automatically inserts them based on the property being tested, 
    # as defined in your architecture.
    
    return qc

# Export the circuit for the QuCheck backend
circuit = create_faulty_bell_state()