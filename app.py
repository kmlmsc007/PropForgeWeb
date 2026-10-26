import streamlit as st
import subprocess
import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime
from groq import Groq

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY", "gsk_Grok_api_key"))

QUCHECK_API_SPEC = """
QuCheck Framework Architecture and Rules:
1. Core Imports:
   import unittest
   import json
   from qiskit import QuantumCircuit
   from qiskit_aer import AerSimulator
   from qucheck.property import Property
   from qucheck.input_generators import RandomState
   from qucheck.test_runner import TestRunner

2. Property Class Definition:
   Each property must inherit from `Property`:
   class MyProperty(Property):
       def get_input_generators(self):
           # Always return a list with RandomState matching the qubit count, e.g. [RandomState(2)]
           return [RandomState(num_qubits)]

       def preconditions(self, *inputs):
           return True

       def operations(self, *inputs):
           # CRITICAL: Always construct QuantumCircuit with BOTH qubits and classical bits matching the total qubit count:
           # For N qubits: qc = QuantumCircuit(N, N)
           # CRITICAL: NEVER call qc.measure(...) inside operations()! QuCheck automatically attaches all projective measurements internally.
           qc = QuantumCircuit(num_qubits, num_qubits)
           ...
           # Statistical assertions on self.statistical_analysis:
           # - Entanglement assertion:
           #   For 2 qubits: self.statistical_analysis.assert_entangled(self, [0, 1], qc, basis=["z"])
           #   For 3 qubits (GHZ): self.statistical_analysis.assert_entangled(self, [0, 1, 2], qc, basis=["z"])
           # - Probability assertion (Note: 'probabililties' is spelled with an extra 'il' and represents probability of outcome |0>):
           #   e.g. for outcome |0> with probability 0.5: probabililties=[0.5]
           #   e.g. for outcome |1> with probability 1.0 (state |1>): probabililties=[0.0]
           #   self.statistical_analysis.assert_probability(self, qubits=[0], circuit=qc, probabililties=[0.5], basis=["z"])
           # - Separable assertion:
           #   self.statistical_analysis.assert_separable(self, qubits=[0, 1], circuit=qc, basis=["z"])

3. Execution with unittest (Adaptive Feed with Early Stopping):
   import random
   class TestQuantumCircuit(unittest.TestCase):
       def setUp(self):
           self.num_measurements = 2000

       def test_properties(self):
           max_input_limit = 50
           overall_status = "passed"
           failing_seed = None
           inputs_processed = 0

           for _ in range(max_input_limit):
               inputs_processed += 1
               dynamic_seed = random.randint(1, 1000000)
               runner = TestRunner([MyProperty], num_inputs=1, random_seed=dynamic_seed, num_measurements=self.num_measurements)
               runner.run_tests()
               if runner.list_failing_properties():
                   failing_seed = dynamic_seed
                   overall_status = "failed"
                   break

           confidence_score = 0.99 if overall_status == "passed" else 0.01
           results = {
               "overall_status": overall_status,
               "inputs_processed": inputs_processed,
               "failing_seed": failing_seed,
               "confidence_score": confidence_score,
           }
           with open("latest_results.json", "w", encoding="utf-8") as f:
               json.dump(results, f, indent=2)

           self.assertEqual(overall_status, "passed")

   if __name__ == "__main__":
       unittest.main()
"""

# Initialize session state for run history
if 'run_history' not in st.session_state:
    st.session_state.run_history = []

# Set page config
st.set_page_config(
    page_title="PropForge: AI Quantum Testing",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom modern CSS for a premium quantum dark theme and distinct card widgets
st.markdown(
    """
    <style>
        /* Base typography & palette */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Outfit:wght@300;500;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }

        code, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Section Containers (Cards) with Distinct Color Coding */
        /* Card 1: Upload Section (#1e293b - very dark elevated blue) */
        [data-testid="stColumn"]:nth-of-type(1) [data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="column"]:nth-of-type(1) [data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.upload-marker) {
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 10px !important;
            padding: 20px !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
        }

        /* Card 2: Execution Section (#2d3748 - subtle charcoal) */
        [data-testid="stColumn"]:nth-of-type(2) [data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="column"]:nth-of-type(2) [data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.execution-marker) {
            background-color: #2d3748 !important;
            border: 1px solid #4a5568 !important;
            border-radius: 10px !important;
            padding: 20px !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
        }

        /* Card 3: Results & Graph Area (#182234 - distinct deep slate/navy) */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.results-marker) {
            background-color: #182234 !important;
            border: 1px solid #28374d !important;
            border-radius: 10px !important;
            padding: 20px !important;
            margin-top: 24px !important;
            margin-bottom: 24px !important;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35) !important;
        }

        .section-header {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 700;
            font-size: 1.25rem;
            color: #e2e8f0;
            margin-bottom: 16px;
            padding-bottom: 8px;
        }

        /* Badges */
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9rem;
        }

        .status-success {
            background: rgba(34, 197, 94, 0.15);
            border: 1px solid rgba(34, 197, 94, 0.4);
            color: #4ade80;
        }

        .status-error {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.4);
            color: #f87171;
        }

        /* Terminal box */
        .terminal-box {
            background: #090d16;
            border: 1px solid #1e293b;
            border-radius: 10px;
            padding: 16px;
            color: #38bdf8;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            line-height: 1.5;
            max-height: 380px;
            overflow-y: auto;
            white-space: pre-wrap;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header Section: Custom HTML block with Flexbox alignment and enlarged font
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 15px; margin-top: -12px; margin-bottom: 25px; padding: 4px 0;">
        <div style="width: 64px; height: 64px; min-width: 64px; background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 34px; box-shadow: 0 6px 18px rgba(37, 99, 235, 0.45); border: 1px solid rgba(147, 197, 253, 0.35); flex-shrink: 0;">
            ⚛️
        </div>
        <div style="display: flex; flex-direction: column; justify-content: center;">
            <div style="font-size: 3rem; font-weight: 800; line-height: 1.15; background: linear-gradient(90deg, #60a5fa 0%, #a855f7 50%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.5px;">
                PropForge: AI Quantum Testing
            </div>
            <p style="color: #94a3b8; font-size: 1.05rem; margin: 4px 0 0 0; font-weight: 400;">
                Autonomous Property-Based Testing for Qiskit Circuits powered by Gemini & QuCheck
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Current directory paths
BASE_DIR = Path(__file__).resolve().parent
PROPFORGE_FILE = BASE_DIR / "propforge.py"
GENERATED_TEST_FILE = BASE_DIR / "generated_test.py"
SAMPLE_TEST_FILE = BASE_DIR / "sample_Test1.py"
PYTHON_EXE = BASE_DIR / "venv" / "Scripts" / "python.exe"
if not PYTHON_EXE.exists():
    PYTHON_EXE = sys.executable


# Available circuits dictionary
CIRCUIT_OPTIONS = {
    "my_circuit.py (2-Qubit Bell State)": "my_circuit.py",
    "ghz_circuit.py (3-Qubit GHZ State)": "ghz_circuit.py",
    "superdense.py (Superdense Coding Protocol)": "superdense.py",
}

# Scan for any additional custom circuits in directory
for extra_file in BASE_DIR.glob("*circuit*.py"):
    label = f"{extra_file.name} (Custom Circuit)"
    if (
        extra_file.name not in CIRCUIT_OPTIONS.values()
        and extra_file.name not in ["circuit_generator.py", "uploaded_circuit.py"]
    ):
        CIRCUIT_OPTIONS[label] = extra_file.name

def extract_circuit_type(filename: str = "", label: str = "", code: str = "") -> str:
    target = f"{filename} {label} {code}".lower()
    if "teleport" in target:
        return "teleportation"
    elif "grover" in target:
        return "grovers"
    elif "qft" in target or "fourier" in target:
        return "qft"
    elif "superdense" in target or "dense" in target:
        return "superdense"
    elif "ghz" in target:
        return "entanglement"
    elif "bell" in target:
        return "bell_state"
    return "bell_state"

# Two columns layout
col_left, col_right = st.columns([1, 1], gap="large")

# Left Column: Circuit Selector & Code Viewer (Card 1: Upload Section)
with col_left:
    with st.container(border=True):
        st.markdown('<span class="upload-marker" style="display:none;"></span>', unsafe_allow_html=True)
        st.markdown('<div class="section-header" style="color: #60a5fa; border-bottom: 1px solid rgba(96, 165, 250, 0.25);">📄 Target Quantum Circuit</div>', unsafe_allow_html=True)
        
        selected_label = st.selectbox(
            "Choose Circuit to Test:",
            options=list(CIRCUIT_OPTIONS.keys()),
            index=0,
        )
        selected_filename = CIRCUIT_OPTIONS[selected_label]

        # File uploader right below the selectbox
        uploaded_file = st.file_uploader(
            "Or upload a custom circuit file (.py):",
            type=["py"],
            help="Upload a Python Qiskit circuit file to analyze and test",
        )

        # Determine active circuit: uploaded file takes priority over selectbox
        if uploaded_file is not None:
            uploaded_code = uploaded_file.getvalue().decode("utf-8")
            active_filename = "uploaded_circuit.py"
            active_circuit_file = BASE_DIR / active_filename
            with open(active_circuit_file, "w", encoding="utf-8") as f:
                f.write(uploaded_code)
            
            st.info(f"📁 Using uploaded circuit: `{uploaded_file.name}` (saved as `{active_filename}`)")
            circuit_code = uploaded_code
        else:
            active_filename = selected_filename
            active_circuit_file = BASE_DIR / active_filename
            if active_circuit_file.exists():
                with open(active_circuit_file, "r", encoding="utf-8") as f:
                    circuit_code = f.read()
            else:
                circuit_code = None

        # Extract circuit type from selection or upload and provide UI dropdown
        auto_circuit_type = extract_circuit_type(active_filename, selected_label, circuit_code or "")
        protocol_options = ["superdense", "bell_state", "teleportation", "grovers", "qft"]
        default_idx = protocol_options.index(auto_circuit_type) if auto_circuit_type in protocol_options else 0
        circuit_type_string = st.selectbox(
            "Protocol / Circuit Type:",
            options=protocol_options,
            index=default_idx,
            help="Select the quantum protocol or circuit type for property routing",
        )
        circuit_type = circuit_type_string
        st.caption(f"🎯 Protocol / Circuit Type: **`{circuit_type_string}`**")

        if circuit_code is not None:
            st.code(circuit_code, language="python", line_numbers=True)
        else:
            st.warning(f"`{active_filename}` not found in directory.")

        # Circuit diagram preview button/expander
        with st.expander(f"🔍 Preview {active_filename} ASCII Diagram", expanded=True):
            if st.button("Render Circuit Diagram", key=f"render_{active_filename}"):
                try:
                    result = subprocess.run(
                        [str(PYTHON_EXE), str(active_circuit_file)],
                        cwd=str(BASE_DIR),
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                    )
                    if result.stdout:
                        st.code(result.stdout, language="text")
                    if result.stderr:
                        st.caption("Runtime info:")
                        st.code(result.stderr, language="text")
                except Exception as e:
                    st.error(f"Error rendering circuit: {e}")

# Right Column: Test Generation & Execution (Card 2: Execution Section)
with col_right:
    with st.container(border=True):
        st.markdown('<span class="execution-marker" style="display:none;"></span>', unsafe_allow_html=True)
        st.markdown('<div class="section-header" style="color: #c084fc; border-bottom: 1px solid rgba(192, 132, 252, 0.25);">⚡ QuCheck Autonomous Verification</div>', unsafe_allow_html=True)
        st.write(f"Synthesize formal quantum property tests with Gemini for **`{active_filename}`**, then execute statistical property verification.")

        num_shots = st.slider('🎯 Simulation Shots (Precision)', min_value=100, max_value=10000, value=2000, step=100, help='Controls statistical accuracy. Higher shots increase precision but take longer to simulate.')

        run_btn = st.button(f"🚀 Generate & Run Tests for {active_filename}", type="primary", use_container_width=True)

        if run_btn:
            # Step 1: Synthesize QuCheck Properties with Groq
            with st.status(f"🧠 Step 1: Synthesizing QuCheck Properties for {active_filename} ({num_shots} shots)...", expanded=True) as status_step:
                try:
                    gen_prompt = (
                        "You are an expert in quantum computing and the QuCheck testing framework.\n"
                        f"API Reference:\n{QUCHECK_API_SPEC}\n\n"
                        "CRITICAL RULES:\n"
                        "1. Modern Qiskit syntax: Do NOT use from qiskit import Aer. You must use from qiskit_aer import Aer or from qiskit_aer import AerSimulator for setting up the simulation backend.\n"
                        "2. Circuit Dimensions: In operations(), always initialize QuantumCircuit(N, N) where classical bit count equals the qubit count (e.g. QuantumCircuit(2, 2) for 2 qubits).\n"
                        "3. DO NOT call qc.measure(...) inside operations()! QuCheck automatically injects and handles measurements. Calling qc.measure() inside operations() causes IndexError / CircuitError.\n"
                        "4. Input Generators: get_input_generators(self) must return a list with RandomState, e.g. [RandomState(2)], never an empty list.\n\n"
                        f"Analyze this Qiskit circuit from '{active_filename}' and write a valid QuCheck property-based test script for it. "
                        "Create properties for entanglement and measurement probabilities that reflect the circuit state. "
                        f"Ensure the TestRunner execution block at the bottom runs with exactly {num_shots} measurements/shots. "
                        "Implement an adaptive feed with early stopping in unittest: iterate up to max_input_limit = 50 with num_inputs=1 and random dynamic_seed; on any failure, capture failing_seed, set overall_status='failed', and break early. "
                        "Finally, write a dictionary to latest_results.json containing overall_status, inputs_processed, failing_seed (or null if passed), confidence_score (0.99 if passed, 0.01 if failed), and counts (counts dictionary from AerSimulator). "
                        "Output ONLY the raw Python code, no markdown.\n\n"
                        f"Circuit:\n{circuit_code}"
                    )

                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "You are a quantum software engineer specializing in property-based testing with QuCheck."},
                            {"role": "user", "content": gen_prompt}
                        ],
                        model="openai/gpt-oss-120b",
                    )
                    ai_code = chat_completion.choices[0].message.content

                    # Clean markdown fences if present
                    clean_code = ai_code.strip()
                    if clean_code.startswith("```"):
                        lines = clean_code.splitlines()
                        if lines[0].startswith("```"):
                            lines = lines[1:]
                        if lines and lines[-1].startswith("```"):
                            lines = lines[:-1]
                        clean_code = "\n".join(lines).strip()

                    with open(GENERATED_TEST_FILE, "w", encoding="utf-8") as f:
                        f.write(clean_code + "\n")

                    status_step.update(label=f"✅ Tests for {active_filename} generated successfully!", state="complete", expanded=False)
                    st.toast(f"QuCheck tests generated for {active_filename}!", icon="✨")
                except Exception as ex:
                    status_step.update(label=f"❌ Error: {ex}", state="error")
                    st.error(f"Generation failed: {ex}")
                    st.stop()

            # Step 2: Run sample_Test1.py
            with st.status(f"🔬 Step 2: Executing QuCheck Statistical Test Suite ({circuit_type_string})...", expanded=True) as run_step:
                try:
                    start_time = time.time()
                    circuit_file_path = str(active_circuit_file)
                    test_env = os.environ.copy()
                    test_env["CIRCUIT_TYPE"] = circuit_type_string
                    test_env["CIRCUIT_FILE"] = circuit_file_path
                    test_proc = subprocess.run(
                        [str(PYTHON_EXE), str(SAMPLE_TEST_FILE), circuit_file_path, circuit_type_string],
                        cwd=str(BASE_DIR),
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        env=test_env,
                    )
                    full_output = (test_proc.stdout or "") + ("\n" + test_proc.stderr if test_proc.stderr else "")
                    elapsed_time = time.time() - start_time
                    
                    # Check results from latest_results.json for strict status determination
                    results_file = BASE_DIR / "latest_results.json"
                    results = {}
                    if results_file.exists():
                        try:
                            with open(results_file, "r", encoding="utf-8") as f:
                                results = json.load(f)
                        except Exception:
                            results = {}

                    if results.get('overall_status') == 'Passed':
                        run_step.update(label="✅ All Property-Based Tests Passed [OK]", state="complete", expanded=False)
                        st.success('All Property-Based Tests Passed [OK]')
                        st.markdown(
                            f"""
                            <div class="status-badge status-success" style="margin-bottom: 12px;">
                                <span>✔</span> <span>All Quantum Properties for {active_filename} Verified & Passed in {elapsed_time:.2f}s</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        st.session_state.run_history.append({
                            "Time": datetime.now().strftime("%H:%M:%S"),
                            "Circuit": active_filename,
                            "Status": "✅ Passed",
                            "Qucheck Execution Time": f"{elapsed_time:.2f}s",
                            "Shots": num_shots,
                        })
                    else:
                        run_step.update(label="❌ Property-Based Tests Failed", state="error", expanded=False)
                        st.error('Property-Based Tests Failed')
                        st.markdown(
                            f"""
                            <div class="status-badge status-error" style="margin-bottom: 12px;">
                                <span>✖</span> <span>Some Quantum Property Assertions Failed for {active_filename} in {elapsed_time:.2f}s</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        st.session_state.run_history.append({
                            "Time": datetime.now().strftime("%H:%M:%S"),
                            "Circuit": active_filename,
                            "Status": "❌ Failed",
                            "Qucheck Execution Time": f"{elapsed_time:.2f}s",
                            "Shots": num_shots,
                        })

                        test_output = full_output
                        prompt = f"You are a senior quantum engineer. Explain this QuCheck test failure in exactly 2 simple sentences for a standard software engineer. Do not use complex math. Here is the error log: {test_output}"
                        with st.spinner("AI analyzing failure..."):
                            try:
                                chat_completion = client.chat.completions.create(
                                    messages=[
                                        {"role": "system", "content": "You are a quantum software engineer specializing in property-based testing with QuCheck."},
                                        {"role": "user", "content": prompt}
                                    ],
                                    model="openai/gpt-oss-120b",
                                )
                                ai_explanation = chat_completion.choices[0].message.content
                            except Exception as ex:
                                ai_explanation = f"Could not generate AI debugger explanation: {ex}"
                        st.error(f"🤖 **AI Debugger:** {ai_explanation}")

                    # Visual Terminal Output Box
                    st.markdown("**🖥️ Captured Terminal Output:**")
                    st.markdown(f'<div class="terminal-box">{full_output.strip()}</div>', unsafe_allow_html=True)

                except Exception as ex:
                    run_step.update(label=f"❌ Execution error: {ex}", state="error")
                    st.error(f"Failed to execute tests: {ex}")

# Read latest_results.json and render permanently on dashboard (Card 3: Results & Graph Area)
results_file = BASE_DIR / "latest_results.json"
if results_file.exists():
    with st.container(border=True):
        st.markdown('<span class="results-marker" style="display:none;"></span>', unsafe_allow_html=True)
        st.markdown('<div class="section-header" style="color: #38bdf8; border-bottom: 1px solid rgba(56, 189, 248, 0.25);">📊 Statistical Verification Results & State Distribution</div>', unsafe_allow_html=True)
        try:
            with open(results_file, "r", encoding="utf-8") as f:
                results_data = json.load(f)

            confidence_score = float(results_data.get("confidence_score", 0.0))
            confidence_score = max(0.0, min(1.0, confidence_score))
            failing_seed = results_data.get("failing_seed")
            inputs_processed = results_data.get("inputs_processed", 0)
            overall_status = str(results_data.get("overall_status", "")).lower()

            st.progress(confidence_score, text=f"Match Confidence: {int(confidence_score * 100)}%")

            if results_data.get('overall_status') == 'Passed':
                st.success('All Property-Based Tests Passed [OK]')
            elif results_data.get('overall_status') == 'Failed':
                st.error('Property-Based Tests Failed')

            properties_tested = results_data.get("properties_tested", [])
            for prop in properties_tested:
                name = prop.get("name", "QuantumProperty")
                status = prop.get("status", "Pass")
                if status == "Pass":
                    with st.expander(f"✅ {name} - PASSED", expanded=False):
                        st.success(f"✅ {name} - PASSED")
                elif status == "Fail":
                    with st.expander(f"❌ {name} - FAILED", expanded=True):
                        st.error(f"❌ {name} - FAILED")

            st.info(f"Seed: {failing_seed} | Inputs Processed: {inputs_processed}")

            if overall_status == "failed" or failing_seed is not None:
                st.error(f"🚨 Failing Seed: {failing_seed} — use this seed to reproduce the edge case.")

            counts_data = results_data.get("counts")
            if counts_data:
                try:
                    st.bar_chart(counts_data, x_label='Quantum State (Outcome)', y_label='Measurement Count (Shots)')
                except TypeError:
                    import pandas as pd
                    import altair as alt
                    df = pd.DataFrame(list(counts_data.items()), columns=['Quantum State (Outcome)', 'Measurement Count (Shots)'])
                    chart = alt.Chart(df).mark_bar().encode(
                        x=alt.X('Quantum State (Outcome):N', title='Quantum State (Outcome)'),
                        y=alt.Y('Measurement Count (Shots):Q', title='Measurement Count (Shots)')
                    )
                    st.altair_chart(chart, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not load latest test results: {e}")

# Inspect Generated Test Code
if GENERATED_TEST_FILE.exists():
    with st.expander("📜 View Current `generated_test.py`", expanded=False):
        with open(GENERATED_TEST_FILE, "r", encoding="utf-8") as f:
            test_code = f.read()
        st.code(test_code, language="python", line_numbers=True)
        
    st.download_button(
        label="⬇️ Download Generated Test Script (.py)",
        data=test_code,
        file_name=f"test_{active_filename}",
        mime="text/x-python",
        use_container_width=True
    )

# QA Session History Section
st.divider()
st.markdown('<div class="section-header">📊 QA Session History</div>', unsafe_allow_html=True)
if st.session_state.run_history:
    st.dataframe(st.session_state.run_history, use_container_width=True)
else:
    st.info("No tests have been run yet.")