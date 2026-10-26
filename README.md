# PropForge QuCheck
# PropForge: Autonomous AI Quantum QA

## Overview
PropForge is an autonomous AI agent designed to bridge the mathematical bottleneck in quantum computing. It takes standard Qiskit circuits and utilizes the Gemini 1.5 API to automatically synthesize and execute complex, property-based statistical tests using the QuCheck framework. 

## Features
* **Automated Property Synthesis:** Generates advanced tests for states like Superposition and Entanglement without manual mathematical calculations.
* **Agentic Self-Correction:** The AI engine dynamically reads local framework documentation to ensure perfectly accurate test generation.
* **Streamlit Dashboard:** A web UI to visualize the target circuit, trigger AI generation, and display deterministic execution results.

## How to Run Locally
1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt