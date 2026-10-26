
import unittest
from pathlib import Path

from qiskit import QuantumCircuit
from qucheck.coordinator import Coordinator
from qucheck.input_generators import RandomState
from qucheck.property import Property


class BellStateEntanglementProperty(Property):
    """Check that H followed by CNOT produces an entangled Bell state."""

    def get_input_generators(self):
        return [RandomState(2)]

    def preconditions(self, state):
        return True

    def operations(self, state):
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)

        self.statistical_analysis.assert_entangled(
            self,
            [0, 1],
            qc,
            basis=["z"],
        )


class BellStateProbabilityProperty(Property):
    """Check the 50/50 computational-basis marginal probabilities."""

    def get_input_generators(self):
        return [RandomState(2)]

    def preconditions(self, state):
        return True

    def operations(self, state):
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)

        self.statistical_analysis.assert_probability(
            self,
            [0, 1],
            qc,
            [0.5, 0.5],
            basis=["z"],
        )


class BellStateCircuitTest(unittest.TestCase):
    """Run the QuCheck property suite with a fixed random seed."""

    def test_bell_state_properties(self):
        properties_dir = Path(__file__).resolve().parent

        coordinator = Coordinator(
            num_inputs=10,
            random_seed=1234,
        )

        results = coordinator.test(
            str(properties_dir),
            measurements=1000,
            run_optimization=True,
        )

        passing = [
            prop.__name__
            for prop in coordinator.test_runner.list_passing_properties()
        ]

        failing = [
            prop.__name__
            for prop in coordinator.test_runner.list_failing_properties()
        ]

        print(f"\nCircuits executed: {results.number_circuits_executed}")
        print(f"Passing properties: {passing}")
        print(f"Failing properties: {failing}")

        self.assertGreater(
            results.number_circuits_executed,
            0,
            "QuCheck did not execute any circuits.",
        )

        self.assertEqual(
            failing,
            [],
            f"Bell-state properties failed: {failing}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
