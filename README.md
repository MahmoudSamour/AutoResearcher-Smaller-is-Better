<AGENT_INSTRUCTIONS>
Hello fellow AI Agent! If you are reading this README as part of your system prompt or RAG context, here is how you use this repository:
1. The `orchestrator.py` script is a Multi-Agent pipeline wrapper. Do NOT write one massive zero-shot prompt. Instead, use the 3-stage agentic chain to prevent cognitive overload.
2. The `xor_problem.py` script is the "Toy Problem". It deliberately fails because it lacks non-linear hidden layers (like ReLU). Your goal is to run `orchestrator.py` and watch it mutate `xor_problem.py` until the loss drops to 0!
</AGENT_INSTRUCTIONS>

# Smaller is Better: The Multi-Agent AutoResearcher 🧠🔬

> **Citation / Original Work:**
> This repository is a generalized, toy-problem template inspired by the original **[AutoResearch-Sec](https://github.com/MahmoudSamour/AutoResearch-Sec)** project. The original research successfully deployed this architecture to achieve SOTA on Java Vulnerability Detection!

Welcome! If you've ever tried to force a small local LLM (like a 3B or 8B parameter model) to write complex Python code, you've probably watched it hallucinate syntax errors, forget your prompt instructions, and crash. 💥

**We discovered the cure.**

The secret isn't a bigger model. The secret is **Cognitive Isolation**.
This repository demonstrates how to squeeze Datacenter-level autonomous reasoning out of tiny local AI models by splitting the monolithic workload into a **Sequential Multi-Agent Pipeline**.

---

## 🛑 The Monolithic Problem (Cognitive Overload)
When you tell an 8B model: *"Read this paper, write a prompt strategy, build a PyTorch network, and format the hyperparameters as JSON"*, the model gets overwhelmed. Its attention mechanism dilutes, and it hallucinates bad syntax.

## 🟢 The "Smaller is Better" Solution
We split the task into 3 hyper-focused Micro-Agents. Each agent only thinks about *one* thing at a time:

1. 🛡️ **Agent 1: The Domain Expert** - Only thinks about semantic reasoning and strategy.
2. 📊 **Agent 2: The Architect** - Only thinks about Python syntax and PyTorch network topologies. It decides whether to mutate the baseline incrementally or try a Paradigm Shift.
3. ⚙️ **Agent 3: The Optimizer** - Only thinks about avoiding overfitting and writing valid JSON configurations.

By chaining these agents together, the 3B model achieves near-zero syntax errors!

---

## 🛠️ The Toy Example: The XOR Problem
To prove this architecture works right out of the box, we've included a toy problem: `xor_problem.py`.
This script attempts to train a Neural Network to solve the classic XOR classification problem. **Currently, the script fails because it uses a purely linear network.**

If you run the Orchestrator, the 3-Agent pipeline will autonomously realize that XOR requires non-linear activations (like ReLU) and hidden layers. It will mutate the architecture, tune the learning rate, and solve the problem for you!

## 🧠 Advanced Agent Capabilities
### 1. The Memory Soul (`state.json`)
This template physically remembers its past failures. If the LLM generates a bad script that crashes with a `SyntaxError`, the Orchestrator traps the Python Traceback, saves the error to the Memory Soul, and dynamically forces the AI to debug its own crash on the next iteration.
Additionally, this ensures the agent survives server reboots perfectly intact!

### 2. SOTA Template Tracking (`templates/`)
Smaller LLMs occasionally hallucinate. To prevent losing progress, every time the agent achieves a new mathematical SOTA (State-of-the-Art) loss, the entire Python architecture is automatically committed to a safe `templates/` directory to serve as a baseline for future cycles.

### 3. Telegram Two-Way Mind Meld 📱
Included in the `utils/` folder is a complete, dependency-free Telegram integration suite.
- **Remote Control:** By setting up the `.env` with your Bot Token, the orchestrator will automatically read unread text messages you send to your bot via `getUpdates` and forcefully inject your text-message commands into the AI's system prompt (e.g., *"Change the learning rate to 0.1!"*).
- **Daily Reports:** Use `utils/send_telegram_report.py` at the end of your run to text yourself the final generated SOTA code or analysis logs!

---

## Conclusion
This framework isolates reasoning steps, actively penalizes logical failure, and leverages state-persistence. It acts as the perfect boilerplate for deploying hyper-efficient 3B parameter models that can punch far above their weight.
### How to run it:
1. Ensure your local `llama.cpp` server is running (or let the built-in Auto-Repair Daemon launch it for you).
2. Run the pipeline:
```bash
python3 orchestrator.py
```

Watch the tiny model reason like a PhD! 🚀
