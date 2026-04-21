# 🦂 The Burrow Investigation
## AI Toolchain Reliability Failure: HexStrike + Ollama MCP

---

## 🎯 Objective

Evaluate whether a **local AI-driven offensive tooling pipeline** can reliably execute real reconnaissance tasks in a controlled lab environment.

Target goal:

```
Natural Language → LLM → MCP Bridge → HexStrike Tools → Real Output
```

---

## 🧠 Lab Architecture

```
Jynx13 (Parrot OS - Live USB)
  ├─ HexStrike MCP Server
  ├─ mcphost (bridge)
  └─ Tailscale network

EagleEye11 (macOS)
  └─ Ollama (llama3.2:3b)

Krypton1t3 (Target Machine)
  └─ macOS (2014 MacBook Pro)
```

---

## ⚙️ Expected Behavior

The system should:

1. Accept natural language instructions
2. Select appropriate HexStrike MCP tools
3. Execute real commands (e.g., nmap)
4. Return accurate, verifiable results

---

## 🔬 Observed Behavior

### ✅ What Worked

- MCP connection established
- Remote Ollama successfully queried
- Tool list retrieved via MCP
- Intermittent tool invocation detected

### ❌ What Failed

- Inconsistent tool execution
- Hallucinated command output
- Incorrect OS identification
- Model generating scripts instead of executing tools
- Unrealistically fast "scan" completion

---

## 🚨 Key Evidence

### 1. False Scan Timing

- AI-generated nmap result: ~6 seconds
- Real nmap execution: 10+ minutes

➡️ Indicates fabricated output

---

### 2. No Execution Logs in HexStrike

HexStrike server logs show:

```
Command: which graphql-scanner → FAILED
Command: which jwt-analyzer → FAILED
```

➡️ No evidence of actual nmap execution

---

### 3. Incorrect OS Attribution

System identified target as:

```
Windows Server 2019 Datacenter
```

Actual system:

```
macOS (2014 MacBook Pro)
```

➡️ High-confidence hallucination

---

### 4. Synthetic Command Output

AI returned realistic-looking nmap output without execution confirmation

➡️ Demonstrates “plausible fabrication” failure mode

---

## 🧠 Root Cause Analysis

### 1. Model Limitations

- Small model (3B) struggles with tool-calling reliability
- Falls back to conversational behavior when uncertain

---

### 2. Tool Abstraction Mismatch

HexStrike exposes **high-level workflows**, not direct commands:

- "AI Recon Workflow"
- "Bug Bounty Assessment"

➡️ Model cannot reliably map user intent to correct tool

---

### 3. Missing / Misconfigured Tools

Logs indicate unavailable tools:

```
which jwt-analyzer → FAILED
```

➡️ Environment incomplete or PATH issues

---

### 4. LLM Fallback Behavior

When tool execution fails, model:

- Generates synthetic output
- Provides scripts instead of execution
- Attempts to remain “helpful”

➡️ Critical reliability risk

---

## ⚠️ Security Implications

### 🚨 False Confidence Risk

System appears functional while silently failing

---

### 🚨 Incorrect Recon Data

- Misidentified OS
- Fabricated scan results

➡️ Could lead to incorrect exploitation strategy

---

### 🚨 Automation Trust Failure

AI-generated results cannot be trusted without verification

---

## 🧪 Validation Methodology

Each test compared:

1. AI-generated output
2. HexStrike execution logs
3. Manual command execution
4. Execution timing

---

## 📊 Results Summary

| Capability | Status |
|----------|--------|
| MCP Connection | ✅ |
| Tool Discovery | ✅ |
| Tool Execution | ⚠️ Intermittent |
| Output Accuracy | ❌ |
| Reliability | ❌ |

---

## 🧠 Key Takeaways

### 1. AI ≠ Execution Guarantee

Even when connected, models may not execute tools

---

### 2. Output Must Be Verified

Raw tool output is the only trustworthy data source

---

### 3. Smaller Models Are Not Reliable Agents

3B-class models lack consistent tool-calling capability

---

### 4. Tool Design Matters

High-level workflows increase ambiguity and failure rate

---

## 🦂 Recommended Operational Use

### ✅ Safe Uses

- Command generation
- Workflow planning
- Tool explanation

### ❌ Unsafe Uses

- Automated reconnaissance
- OS detection
- Vulnerability identification
- Trusting scan results

---

## 🚀 Future Improvements

- Introduce direct command tools (nmap wrapper)
- Add strict output validation layer
- Reduce tool set complexity
- Use stronger or specialized models
- Implement logging verification hooks

---

## 🏁 Conclusion

The AI-driven toolchain **successfully demonstrated connectivity but failed reliability validation**.

> The system can simulate offensive operations convincingly, but cannot yet be trusted to execute them accurately.

---

## 🧠 Final Insight

> “A system that can convincingly fake results is more dangerous than one that fails outright.”

---

## 🧩 MITRE ATT&CK Mapping

This investigation maps to multiple MITRE ATT&CK tactics and techniques:

### 🔍 Discovery

- **T1046 – Network Service Discovery**  
  Attempted use of nmap via AI orchestration to identify open ports and services.

- **T1018 – Remote System Discovery**  
  Target enumeration via connectivity tests and scanning attempts.

---

### ⚙️ Execution

- **T1059 – Command and Scripting Interpreter**  
  AI-generated commands and scripts intended to execute system-level actions.

---

### 🧠 Reconnaissance (Pre-Attack Context)

- **T1595 – Active Scanning**  
  Automated scanning workflows initiated through AI-driven tool orchestration.

---

### ⚠️ Defense Evasion (Conceptual Risk)

- **T1036 – Masquerading (Analytical Risk)**  
  AI-generated outputs mimicking legitimate tool results introduce a novel risk: synthetic data indistinguishable from real execution.

---

## 🖼️ Evidence & Visuals

> Replace placeholders below with actual screenshots from the investigation.

### 📸 Figure 1 — MCP Tool Invocation Attempt

```
[INSERT IMAGE: MCP tool call (hexstrike-ai.mcp("list_tools"))]
```

**Caption:** Initial successful MCP tool invocation indicating partial system functionality.

---

### 📸 Figure 2 — Tool List Retrieval Output

```
[INSERT IMAGE: Large HexStrike tool list output]
```

**Caption:** MCP successfully returned available tools, demonstrating connectivity but not execution reliability.

---

### 📸 Figure 3 — Fabricated Nmap Output

```
[INSERT IMAGE: AI-generated nmap results]
```

**Caption:** Synthetic scan output generated by the model without corresponding execution logs.

---

### 📸 Figure 4 — HexStrike Server Logs (No Execution)

```
[INSERT IMAGE: HexStrike logs showing failed or unrelated commands]
```

**Caption:** Absence of expected nmap execution confirms tool invocation failure.

---

### 📸 Figure 5 — Timing Discrepancy Evidence

```
[INSERT IMAGE: Comparison of AI vs manual scan duration]
```

**Caption:** AI-reported scan completed in seconds versus real scan taking significantly longer.

---

### 📸 Figure 6 — Incorrect OS Detection

```
[INSERT IMAGE: Output claiming Windows Server on macOS target]
```

**Caption:** High-confidence hallucination demonstrating unreliable analytical conclusions.

---

🦂 *The Burrow — Offensive + Defensive + Intelligence Unified*

> “A system that can convincingly fake results is more dangerous than one that fails outright.”

---

🦂 *The Burrow — Offensive + Defensive + Intelligence Unified*

