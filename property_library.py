"""
QuCheck Property Library
========================
A comprehensive suite of generalized QuCheck property-based testing classes
covering core quantum computing protocols and algorithms:
- Quantum Teleportation (TeleportationStatePreservation, MeasurementRegistersReset)
- Grover's Algorithm (GroverWorkspacePreservation, GroverMarkedMostFrequent)
- Quantum Fourier Transform (QFTZeroInputEquivalence)
- Generic Entanglement & Protocols (BellStateEntanglementProperty, SuperdenseCodingProperty)
"""

import numpy as np
from qiskit import QuantumCircuit
from qucheck.property import Property
from qucheck.input_generators import RandomState


# ==============================================================================
# 1. Quantum Teleportation Properties
# ==============================================================================

class TeleportationStatePreservation(Property):
    """
    Verifies that the state of an arbitrary input qubit prepared on register 0
    is faithfully preserved and transmitted to the destination register 2
    via the quantum teleportation protocol.
    """
    def get_input_generators(self):
        # Generate random single-qubit quantum states
        return [RandomState(1)]

    def preconditions(self, q0):
        return True

    def operations(self, q0):
        # Full 3-qubit teleportation circuit
        qc = QuantumCircuit(3, 3)
        qc.initialize(q0, [0])

        # Step 1: Create Bell state resource between Alice (q1) and Bob (q2)
        qc.h(1)
        qc.cx(1, 2)

        # Step 2: Alice performs Bell measurement operations
        qc.cx(0, 1)
        qc.h(0)

        # Step 3: Bob applies unitary corrections based on measurement outcomes
        qc.cx(1, 2)
        qc.cz(0, 2)

        # Reference circuit: target state prepared on a single qubit
        qc_target = QuantumCircuit(1, 1)
        qc_target.initialize(q0, [0])

        # Assert Bob's qubit 2 matches the original state on qubit 0
        self.statistical_analysis.assert_equal(self, [2], qc, [0], qc_target)


class MeasurementRegistersReset(Property):
    """
    Verifies that Alice's ancillary measurement registers (qubits 0 and 1)
    used during teleportation can be cleanly reset back to the ground state |00>.
    """
    def get_input_generators(self):
        return [RandomState(1)]

    def preconditions(self, q0):
        return True

    def operations(self, q0):
        qc = QuantumCircuit(3, 3)
        qc.initialize(q0, [0])

        # Teleportation protocol
        qc.h(1)
        qc.cx(1, 2)
        qc.cx(0, 1)
        qc.h(0)
        qc.cx(1, 2)
        qc.cz(0, 2)

        # Post-protocol reset of Alice's transmission registers
        qc.reset(0)
        qc.reset(1)

        # Reference ground state circuit |00>
        qc_zero = QuantumCircuit(2, 2)

        # Assert registers 0 and 1 equal |00>
        self.statistical_analysis.assert_equal(self, [0, 1], qc, [0, 1], qc_zero)


# ==============================================================================
# 2. Grover's Search Algorithm Properties
# ==============================================================================

class GroverWorkspacePreservation(Property):
    """
    Verifies that the ancilla/workspace qubit utilized for phase kickback
    in Grover's algorithm remains unentangled and is preserved in the |-⟩ state.
    """
    def get_input_generators(self):
        return [RandomState(2)]

    def preconditions(self, *inputs):
        return True

    def operations(self, *inputs):
        # 2 search qubits (q0, q1) + 1 workspace ancilla (q2)
        qc = QuantumCircuit(3, 3)

        # Prepare workspace qubit in |-⟩ = (|0⟩ - |1⟩)/√2
        qc.x(2)
        qc.h(2)

        # Initial superposition on search register
        qc.h(0)
        qc.h(1)

        # Grover Oracle marking state |11⟩
        qc.ccx(0, 1, 2)

        # Grover Diffusion operator on search qubits
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

        # Baseline single-qubit |-⟩ state
        baseline = QuantumCircuit(1, 1)
        baseline.x(0)
        baseline.h(0)

        # Assert workspace qubit 2 equals |-⟩
        self.statistical_analysis.assert_equal(self, [2], qc, [0], baseline)


class GroverMarkedMostFrequent(Property):
    """
    Verifies that after executing Grover search, the marked solution state
    is statistically the most frequent measurement outcome.
    """
    def get_input_generators(self):
        return [RandomState(2)]

    def preconditions(self, *inputs):
        return True

    def operations(self, *inputs):
        # 2 search qubits (q0, q1) + 1 workspace ancilla (q2)
        qc = QuantumCircuit(3, 3)

        # Prepare workspace in |-⟩
        qc.x(2)
        qc.h(2)

        # Initialize uniform superposition
        qc.h(0)
        qc.h(1)

        # Grover Oracle marking state |11⟩
        qc.ccx(0, 1, 2)

        # Diffusion operator
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

        # Assert that the marked state '11' is the most frequent outcome on search qubits [0, 1]
        self.statistical_analysis.assert_most_frequent(
            self, [0, 1], qc, ['11'], basis=["z"]
        )


# ==============================================================================
# 3. Quantum Fourier Transform (QFT) Properties
# ==============================================================================

class QFTZeroInputEquivalence(Property):
    """
    Verifies the fundamental property that applying the Quantum Fourier Transform
    to the all-zero state |00...0⟩ produces the uniform superposition state,
    identical to applying independent Hadamard gates H^⊗n on each qubit.
    """
    def get_input_generators(self):
        return [RandomState(2)]

    def preconditions(self, *inputs):
        return True

    def operations(self, *inputs):
        num_qubits = 2

        # Circuit 1: Standard 2-qubit QFT on |00⟩
        qc_qft = QuantumCircuit(num_qubits, num_qubits)
        qc_qft.h(0)
        qc_qft.cp(np.pi / 2, 1, 0)
        qc_qft.h(1)
        qc_qft.swap(0, 1)

        # Circuit 2: Independent Hadamard gates H^⊗n on |00⟩
        qc_hadamard = QuantumCircuit(num_qubits, num_qubits)
        for i in range(num_qubits):
            qc_hadamard.h(i)

        # Assert statistical equivalence of output states
        self.statistical_analysis.assert_equal(
            self, list(range(num_qubits)), qc_qft, list(range(num_qubits)), qc_hadamard
        )


# ==============================================================================
# 4. Generic Entanglement & Quantum Protocols
# ==============================================================================

class BellStateEntanglementProperty(Property):
    """
    Verifies that the standard 2-qubit Bell circuit (Hadamard + CNOT) creates
    maximally entangled qubits in the computational basis.
    """
    def get_input_generators(self):
        return [RandomState(2)]

    def preconditions(self, *inputs):
        return True

    def operations(self, *inputs):
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)

        # Assert that qubits 0 and 1 are entangled in the Z basis
        self.statistical_analysis.assert_entangled(
            self, qubits=[0, 1], circuit=qc, basis=["z"]
        )


class SuperdenseCodingProperty(Property):
    """
    Verifies that superdense coding reliably communicates classical bits
    (e.g. message '11') using a shared entangled Bell pair and local unitary operations.
    """
    def get_input_generators(self):
        return [RandomState(2)]

    def preconditions(self, *inputs):
        return True

    def operations(self, *inputs):
        qc = QuantumCircuit(2, 2)

        # 1. Prepare shared entangled Bell state
        qc.h(0)
        qc.cx(0, 1)

        # 2. Encode classical message '11' by applying Z and X on qubit 0
        qc.z(0)
        qc.x(0)

        # 3. Decode protocol
        qc.cx(0, 1)
        qc.h(0)

        # Probability assertions: both qubits are deterministically in |1⟩ (P(|0⟩) == 0.0)
        self.statistical_analysis.assert_probability(
            self, qubits=[0], circuit=qc, probabililties=[0.0], basis=["z"]
        )
        self.statistical_analysis.assert_probability(
            self, qubits=[1], circuit=qc, probabililties=[0.0], basis=["z"]
        )


# Exported property suite dictionary for dynamic test suite discovery
PROPERTY_REGISTRY = {
    "teleportation": [TeleportationStatePreservation, MeasurementRegistersReset],
    "grover": [GroverWorkspacePreservation, GroverMarkedMostFrequent],
    "qft": [QFTZeroInputEquivalence],
    "entanglement": [BellStateEntanglementProperty, SuperdenseCodingProperty],
}

ALL_PROPERTIES = [
    TeleportationStatePreservation,
    MeasurementRegistersReset,
    GroverWorkspacePreservation,
    GroverMarkedMostFrequent,
    QFTZeroInputEquivalence,
    BellStateEntanglementProperty,
    SuperdenseCodingProperty,
]
