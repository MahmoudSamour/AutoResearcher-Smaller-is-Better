import os
import json
import logging
import subprocess
import requests
import time
import glob
import re

logging.basicConfig(level=logging.INFO, format='%(message)s')

LLM_API_URL = "http://127.0.0.1:8081/v1/chat/completions"

def ensure_llm_server_running():
    try:
        requests.get(LLM_API_URL.replace('/chat/completions', '/models'), timeout=2)
        logging.info("LLM Server is already running!")
        return
    except requests.exceptions.ConnectionError:
        logging.warning("LLM Server is DOWN. Attempting Auto-Repair...")
        
    cmd = [
        "llama-server",
        "-m", "/home/mm/AI-Workspace/models/Qwen2.5-Coder-3B-Q4_K_M.gguf",
        "--port", "8081",
        "--host", "127.0.0.1",
        "-ngl", "99",
        "-c", "16384"
    ]
    
    with open("llama_auto_repair.log", "w") as f:
        subprocess.Popen(cmd, stdout=f, stderr=f)
        
    logging.info("Waiting 15 seconds for LLM Server to boot...")
    for _ in range(15):
        try:
            requests.get(LLM_API_URL.replace('/chat/completions', '/models'), timeout=2)
            logging.info("Auto-Repair Successful! LLM Server is online.")
            return
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            
    logging.error("Auto-Repair Failed. Check your llama.cpp installation.")

class MultiAgentOrchestrator:
    def __init__(self):
        logging.info("Initializing Smaller-is-Better Multi-Agent Orchestrator...")
        ensure_llm_server_running()
        
        self.state_file = "state.json"
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            self.memory_soul = state.get("memory_soul", [])
            self.best_loss = state.get("best_loss", float('inf'))
        else:
            self.memory_soul = []
            self.best_loss = float('inf')
            
    def save_state(self, new_loss=None):
        if new_loss is not None:
            self.best_loss = new_loss
        with open(self.state_file, 'w') as f:
            json.dump({
                "best_loss": self.best_loss,
                "memory_soul": self.memory_soul
            }, f, indent=4)
            
    def get_working_templates(self):
        templates_str = ""
        for path in sorted(glob.glob("templates/*.py"), reverse=True)[:3]:
            with open(path, "r") as f:
                templates_str += f"\n--- TEMPLATE: {os.path.basename(path)} ---\n"
                templates_str += f.read() + "\n"
        if templates_str:
            return f"\n[WORKING TEMPLATES LIBRARY]\nHere is code that compiled and achieved SOTA previously. You MUST use these as structural references:\n{templates_str}\n"
        return ""

    def call_llm(self, system_prompt, role_title="AI Agent", temperature=0.7):
        import uuid
        job_id = str(uuid.uuid4())[:8]
        prompt_file = f"/tmp/ag_prompt_{job_id}.txt"
        resp_file = f"/tmp/ag_resp_{job_id}.txt"

        with open(prompt_file, 'w') as f:
            f.write(system_prompt)

        if os.path.exists(resp_file):
            os.remove(resp_file)

        agent_prompt = f"""[Antigravity AutoResearch Bridge]
You are acting as a {role_title}.
1. Please read the full task prompt located at: {prompt_file}
2. Execute the task perfectly.
3. Write your final, raw text response directly to the file: {resp_file}
DO NOT ask for permission, just use your write_to_file tool immediately to create {resp_file}.
"""
        logging.info(f"Spawning IDE Agent for {role_title}...")
        subprocess.run(["antigravity", "chat", "-m", "agent", agent_prompt])

        logging.info("Waiting for Antigravity Agent to complete task...")
        import time
        while True:
            if os.path.exists(resp_file):
                size = os.path.getsize(resp_file)
                if size > 0:
                    time.sleep(2) # Give agent time to flush the write
                    break
            time.sleep(1)

        with open(resp_file, 'r') as f:
            content = f.read()

        # Clean up
        try:
            os.remove(prompt_file)
            os.remove(resp_file)
        except Exception:
            pass

        return content

    def execute_multi_agent_pipeline(self):
        # Fetch Telegram Feedback
        try:
            subprocess.run(["python3", "utils/fetch_telegram_feedback.py"])
        except Exception as e:
            logging.error(f"Failed to fetch Telegram feedback: {e}")
            
        telegram_feedback = ""
        if os.path.exists("USER_FEEDBACK.txt"):
            with open("USER_FEEDBACK.txt", "r") as f:
                telegram_feedback = f"[USER TELEGRAM FEEDBACK]\nThe user sent you the following direct command:\n{f.read()}\nYOU MUST STRICTLY OBEY THIS COMMAND!\n"

        memory_str = "\n".join(self.memory_soul[-5:]) if self.memory_soul else "No past memory yet."
        working_templates = self.get_working_templates()
        
        # Read the current XOR baseline
        with open('xor_problem.py', 'r') as f:
            baseline_code = f.read()

        logging.info("Agent 1: Domain Expert (Diagnosing the problem)...")
        expert_prompt = f"""[MEMORY SOUL: PAST EXPERIENCES]
{memory_str}
{telegram_feedback}
[PREVIOUS SCORE]
The previous baseline achieved a loss of: {self.best_loss:.4f}. (Lower is better, goal is 0.0)
[TASK]
You are the Domain Expert. The XOR dataset is completely non-linear. The current network is likely just a linear layer, which physically cannot solve XOR.
Outline the optimal strategy to solve it.
Output exactly in this format:
<STRATEGY>
Your raw strategy string here
</STRATEGY>
"""
        strategy_output = self.call_llm(expert_prompt, role_title="Domain Expert")

        logging.info("Agent 2: Architect (Designing PyTorch Architecture)...")
        arch_prompt = f"""[MEMORY SOUL: PAST EXPERIENCES]
{memory_str}
{working_templates}
[PREVIOUS SCORE]
The previous baseline achieved a loss of: {self.best_loss:.4f}. 
[STRATEGY FROM DOMAIN EXPERT]
{strategy_output}
[TASK]
You are the Code Architect. You must rewrite the `XORModel` class inside `xor_problem.py` to add non-linear hidden layers (like `nn.ReLU()`) so it can solve the XOR problem!
Here is the previous architecture script:
<ARCHITECTURE>
{baseline_code}
</ARCHITECTURE>
Output your exact Python code in this format. You must output the entire updated script!
<ARCHITECTURE>
Your complete python script here
</ARCHITECTURE>
"""
        arch_output = self.call_llm(arch_prompt, role_title="Software Architect")
        arch_match = re.search(r'<ARCHITECTURE>\n?(.*?)\n?</ARCHITECTURE>', arch_output, re.DOTALL)
        new_arch = arch_match.group(1).strip() if arch_match else baseline_code

        logging.info("Agent 3: Optimizer (Tuning Hyperparameters)...")
        hyper_prompt = f"""[MEMORY SOUL: PAST EXPERIENCES]
{memory_str}
[ARCHITECTURE TO TUNE FOR]
{new_arch}
[TASK]
You are the Optimization Expert. TWEAK the hyperparameters to match the new architecture. Maybe increase the learning rate to 0.1?
Output exactly in this format:
<HYPERPARAMETERS>
{{"learning_rate": 0.1, "epochs": 2000}}
</HYPERPARAMETERS>
"""
        hyper_output = self.call_llm(hyper_prompt, role_title="Optimization Expert", temperature=0.5)
        hyper_match = re.search(r'<HYPERPARAMETERS>\n?(.*?)\n?</HYPERPARAMETERS>', hyper_output, re.DOTALL)
        new_hyper = hyper_match.group(1).strip() if hyper_match else '{"learning_rate": 0.05, "epochs": 1000}'

        # Write to files
        with open('xor_problem.py', 'w') as f:
            f.write(new_arch)
        with open('hyperparameters.json', 'w') as f:
            f.write(new_hyper)

    def run(self):
        os.makedirs("templates", exist_ok=True)
        logging.info("Starting Smaller-is-Better Optimization Loop...")
        for i in range(1, 20):
            logging.info(f"\\n--- Iteration {i} ---")
            self.execute_multi_agent_pipeline()
            
            logging.info("Executing the updated script...")
            result = subprocess.run(["python3", "xor_problem.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                # Parse Loss
                try:
                    loss_match = re.search(r'Final Loss: ([\d\.]+)', result.stdout)
                    loss = float(loss_match.group(1))
                    logging.info(f"Experiment Succeeded! Final Loss: {loss:.4f}")
                    
                    if loss < self.best_loss:
                        logging.info("New SOTA Achieved! Saving to templates.")
                        self.save_state(loss)
                        with open(f"templates/working_arch_loss_{loss:.4f}.py", "w") as f:
                            with open('xor_problem.py', 'r') as src:
                                f.write(src.read())
                    else:
                        logging.info("Model Degraded.")
                        
                    if loss < 0.05:
                        logging.info("🎉 XOR Problem Solved! The Multi-Agent Pipeline works!")
                        break
                        
                except Exception as e:
                    logging.error("Failed to parse loss from output.")
            else:
                logging.error(f"⚠️ Script Crashed! Trapping traceback into Memory Soul...")
                traceback_snippet = result.stderr.strip()[-500:] # Capture more of the traceback
                self.memory_soul.append(f"CRASH REPORT - You generated code that caused this Python Traceback:\n{traceback_snippet}\nYou MUST fix this error in the next iteration!")
                self.save_state()

if __name__ == "__main__":
    orchestrator = MultiAgentOrchestrator()
    orchestrator.run()
