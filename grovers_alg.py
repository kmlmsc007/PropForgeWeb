from qiskit import QuantumCircuit

# 2-Qubit Grover's Algorithm (Searching for state |11>)
qc = QuantumCircuit(2, 2)

# Step 1: Initialization (Create uniform superposition)
qc.h([0, 1])
qc.barrier()

# Step 2: Oracle (Marks the |11> state by flipping its sign)
qc.cz(0, 1) 
qc.barrier()

# Step 3: Diffuser / Amplitude Amplification (Increases probability of the marked state)
qc.h([0, 1])
qc.x([0, 1])
qc.cz(0, 1)
qc.x([0, 1])
qc.h([0, 1])
qc.barrier()

# Step 4: Measurement
qc.measure([0, 1], [0, 1])