# PropForge: Autonomous AI Quantum QA Dashboard

## Overview

**QuCheck** is a specialized property-based testing framework designed for quantum software, allowing engineers to validate quantum circuits against underlying mathematical rules (like entanglement and superposition) rather than relying solely on classical unit tests.

**PropForge** acts as the interactive, visual tool that supercharges this framework. PropForge is an autonomous AI agent designed to bridge the mathematical bottleneck in quantum computing. It takes standard Qiskit circuits and utilizes the Gemini 1.5 API to automatically synthesize and execute complex, property-based statistical tests using the QuCheck framework. By wrapping QuCheck in a powerful Streamlit dashboard, PropForge transforms raw terminal outputs into a comprehensive, user-friendly QA environment.

## Key Features

* **Automated Property Synthesis:** Generates advanced tests for states like Superposition and Entanglement without manual mathematical calculations.


* **Agentic Self-Correction:** The AI engine dynamically reads local framework documentation to ensure perfectly accurate test generation.


* **Interactive Data Visualizations:** A web UI to visualize the target circuit, trigger AI generation, and display deterministic execution results, including statistical bar graphs mapping the probability distribution of final quantum measurement outcomes.


* **Dynamic Protocol Routing:** Ensures uploaded circuits (like Bell State or Grover's) are evaluated exclusively against their mathematically appropriate property tests.
* **Precision Simulation Control:** Allows engineers to dictate the statistical weight of the simulation by injecting custom shot counts via the UI.
* **Automated QA Audit Logging:** Maintains a session history tracker recording timestamps, target file names, execution times, pass/fail status, and custom shot counts for every run.

## Prerequisites

* Python 3.8+
* Git
* Valid API Keys (Gemini/Groq, depending on your local environment configuration)

## How to Run Locally

1. **Clone the repository:**
```bash
git clone https://github.com/kmlmsc007/PropForge.git
cd PropForge

```


2. **Create and activate a virtual environment (Recommended):**
* Windows:
```bash
python -m venv venv
.\venv\Scripts\activate

```


* macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate

```




3. **Install the required dependencies:**
```bash
pip install -r requirements.txt

```


(Note: This command installs all necessary libraries, including Streamlit, Qiskit, and QuCheck dependencies).


4. **Configure Environment Variables:**
Ensure your API keys are set in your local environment or an `.env` file before launching the dashboard.
5. **Launch the Dashboard:**
```bash
streamlit run propforge.py

```



## How to Use PropForge

1. **Upload a Circuit:** Once the Streamlit dashboard opens in your browser, upload any standard Qiskit `.py` file (e.g., `my_circuit.py` for a Bell state or `grover_circuit.py`).
2. **Verify Architecture:** Review the auto-generated ASCII circuit diagram rendered directly from your code to visually confirm your gate layout.
3. **Configure the Test:** Use the dropdown menu to select the specific test protocol (e.g., `bell_state`) and adjust the precision slider to set your desired simulation shots.
4. **Execute & Analyze:** Run the test to trigger the QuCheck backend. The dashboard will output a statistical bar graph of the quantum state distribution and append the exact execution metrics to your session audit log.
