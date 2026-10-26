import unittest
import json
import random
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qucheck.property import Property
from qucheck.input_generators import RandomState
from qucheck.test_runner import TestRunner

class FaultyBellProperty(Property):
    def get_input_generators(self):
        # Two qubits for the faulty Bell state
        return [RandomState(2)]

    def preconditions(self, *inputs):
        return True

    def operations(self, *inputs):
        # Construct circuit with matching quantum and classical registers
        qc = QuantumCircuit(2, 2)
        # Intended faulty Bell state preparation
        qc.h(0)
        qc.h(1)
        # Assertions reflecting the actual state (uniform, separable)
        self.statistical_analysis.assert_separable(self, qubits=[0, 1], circuit=qc, basis=["z"])
        self.statistical_analysis.assert_probability(self, qubits=[0], circuit=qc, probabililties=[0.5], basis=["z"])
        self.statistical_analysis.assert_probability(self, qubits=[1], circuit=qc, probabililties=[0.5], basis=["z"])
        # No explicit measurement; QuCheck handles it automatically

class TestQuantumCircuit(unittest.TestCase):
    def setUp(self):
        self.num_measurements = 10000

    def test_properties(self):
        max_input_limit = 50
        overall_status = "passed"
        failing_seed = None
        inputs_processed = 0
        final_counts = {}

        for _ in range(max_input_limit):
            inputs_processed += 1
            dynamic_seed = random.randint(1, 1_000_000)
            runner = TestRunner(
                [FaultyBellProperty],
                num_inputs=1,
                random_seed=dynamic_seed,
                num_measurements=self.num_measurements,
            )
            runner.run_tests()
            if runner.list_failing_properties():
                failing_seed = dynamic_seed
                overall_status = "failed"
                break

            # Simulate the circuit to capture measurement counts
            sim_circ = QuantumCircuit(2, 2)
            sim_circ.h(0)
            sim_circ.h(1)
            sim_circ.measure([0, 1], [0, 1])
            backend = AerSimulator()
            result = backend.run(sim_circ, shots=self.num_measurements).result()
            final_counts = result.get_counts()

        confidence_score = 0.99 if overall_status == "passed" else 0.01
        results = {
            "overall_status": overall_status,
            "inputs_processed": inputs_processed,
            "failing_seed": failing_seed,
            "confidence_score": confidence_score,
            "counts": final_counts,
        }
        with open("latest_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        self.assertEqual(overall_status, "passed")

if __name__ == "__main__":
    unittest.main()
