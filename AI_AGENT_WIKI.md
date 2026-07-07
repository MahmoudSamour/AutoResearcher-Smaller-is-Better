# AI Agent Architecture & Learning Wiki

This wiki serves as a consolidated repository of all the learnings, architectural decisions, and best practices discovered while building fully autonomous AI agents across various projects (Trading Bot, AutoResearcher, etc.).

## 1. Token-Free IPC & Background Architecture
One of the biggest lessons learned is how to manage background tasks and queues without burning through AI quota or API tokens.

### The Problem with Python Schedulers
Initially, we used Python loops (like `schedule.every(5).minutes`) inside the AI agent itself to poll for messages or run tasks. This kept the agent "active" and consumed massive amounts of tokens just by waiting.

### The "Zero-Token" Bash Watcher Solution
We transitioned to a pure Bash-based architecture for IPC (Inter-Process Communication):
1. **Producer:** A lightweight Python script (e.g., `live_telegram_agent.py`) listens to Telegram webhooks. When a message arrives, it writes the text to a file (`telegram_request.txt`).
2. **Consumer (Watcher):** A simple `while` loop in Bash (`while [ ! -f telegram_request.txt ]; do sleep 2; done`) waits for the file to appear. This costs 0 AI tokens and uses ~0 CPU.
3. **Execution:** Once the file appears, the Bash script `cat`s the content and pipes it into the actual AI agent. The agent wakes up, does its job, and goes back to sleep.
4. **Queue Clearing:** The AI agent must explicitly `rm telegram_request.txt` to clear the queue and prevent infinite loops.

## 2. The "Hyper-Evolution" Loop
For self-improving agents (like the Trading Bot or AutoResearcher), we implemented a "Hyper-Evolution" loop.

### Mechanics
- **State File:** A simple `hyper_iteration.txt` tracks the current loop count.
- **Crontab vs. Background Bash:** We learned that chaining tasks using `for i in {1..10}; do sleep 3600; bash evolve.sh; done` in the background is often more reliable than `cron` for sequential, stateful multi-hour tasks, because `cron` doesn't inherently care if the previous task finished, whereas a `for` loop guarantees sequential execution.
- **Ghost Processes:** *Critical Lesson:* When IDEs or servers restart, detached Bash processes survive. This can lead to multiple overlapping "ghost" loops triggering evolution simultaneously. Always include a `pkill -f` or a PID lock-file check before starting a multi-hour background sequence.

## 3. Autonomous Self-Repair & Memory
Agents must be able to read their own error logs and fix themselves.

### Database Log Bridges
Instead of relying solely on standard out, we bridge raw `stderr` and `stdout` into a PostgreSQL database (e.g., `system_errors` table). 
- A `self_repair.sh` agent wakes up periodically, queries the `system_errors` table, reads the stack traces, and aggressively patches the source code to fix the errors.
- **Transitory vs Fatal:** We learned to classify errors. Network timeouts or exchange minimum-volume rejections are "transitory" and shouldn't trigger a full system halt. The agent is trained to ignore transitory terms (e.g., `ErrVolumeTooLow`) when evaluating its health status, but it uses them during Hyper-Evolution to adjust trade sizes.

### Agent Memory (AGENT_MEMORY.md)
The AI agent is stateless between invocations. To maintain continuity across weeks of evolution, we use a rolling `AGENT_MEMORY.md` file. 
- Every time the agent deploys a code change, it appends a "Cycle X" entry to the memory file detailing the *Observation*, the *Enhancement*, and the *Reasoning*.
- On the next wake-up, the agent reads this file first to avoid repeating past mistakes.

## 4. Multi-Agent Review Systems (Trinity Framework)
For complex tasks (like generating Alpha in trading or generating Research hypotheses), a single LLM pass is prone to hallucination or logical gaps.
We implemented the **Trinity Expert Feedback** pattern:
1. **The Generator:** Creates the initial strategy or code.
2. **The Reviewers:** The RAG context is fed to simulated expert personas (e.g., [FULLSTACK REVIEWER], [CRYPTO MASTER REVIEWER], [FINTECH MONETIZATION EXPERT]).
3. **The Synthesizer:** The original agent reads the feedback from all three experts and aggressively patches the generated output before finalizing it.

## 5. Startup & Resilience
Agents are useless if they die when the laptop goes to sleep.
- **Desktop Entry (`.desktop`):** We added an autostart script (`~/.config/autostart/vscode-trading.desktop`) that ensures the VS Code IDE and the background watchers boot up the moment the Linux OS starts.
- **Decoupled Deployment:** The agent pushes its changes to GitHub (`deploy.sh`), which automatically triggers a cloud redeployment (e.g., Koyeb, Vercel). The local machine only acts as the "Brain" (the thinker and queue watcher), while the actual execution of the code happens on the cloud. This ensures the trading engine runs 24/7 even if the local brain is asleep.
