# 🦂 Hermes Forge (Krypton1t3) – Local AI Agent Deployment Report

## 🦂 The Burrow | Build Report

**Date:** 2026-04-23  
**System Codename:** Krypton1t3  
**Agent Codename:** Hermes Forge  

---

## 📍 Overview

This report documents the deployment and testing of **Hermes Agent (Hermes Forge)** on a repurposed 2014 MacBook Pro running Fedora Security Lab.

Goal:
- Fully local AI agent
- No external APIs
- Privacy-first lab integration

---

## 🖥️ Environment

- **Host:** Krypton1t3 (2014 MacBook Pro)
- **OS:** Fedora Security Lab
- **LLM Runtime:** Ollama
- **Agent Framework:** Hermes Agent
- **Network:** Local lab (Tailscale-enabled)

---

## 🧠 Models Tested

| Model | Result | Notes |
|------|--------|------|
| deepseek-coder:6.7b | ❌ Failed | Blocked by 64K context requirement |
| phi3:mini | ❌ Failed | No tool support |
| phi4-mini | ⚠️ Partial | Extremely slow (~20 min responses) |
| mistral:7b | ❌ Failed | Blocked by 64K context requirement |
| llama3.2:3b | ✅ Success | Best performance + tool compatibility |

---

## ⚠️ Major Challenges

### 1. 64K Context Gate
- New Hermes versions enforce minimum 64K context
- Blocks many local models
- Config override unreliable

### 2. Tool Compatibility
- Many Ollama models lack tool support
- Hermes still attempts tool calls → HTTP 400 errors

### 3. Model Behavior Instability
Observed:
- Hallucinated outputs
- Incorrect commands
- Inconsistent tool usage

---

## 🔧 Final Working Configuration

```yaml
model:
  provider: custom
  base_url: http://localhost:11434/v1
  default: llama3.2:3b

agent:
  tool_use_enforcement: ["llama"]
```

---

## 🧪 Functional Testing

### ✅ Terminal Tool Execution

Command:
```bash
ls -l ~/.hermes
```

Result:
- Tool invoked successfully
- Real filesystem output returned

---

### ❌ Command Accuracy Issues

Example failure:
```bash
du -dh ~ | tail -n 1
```

Error:
- Invalid syntax
- Incorrect flag usage

---

### ❌ Output Hallucination

Hermes produced:
- Fake filesystem tables
- Negative disk usage values
- Incorrect summaries

---

### ⚠️ Tool Invocation Inconsistency

Behavior observed:
- Sometimes executes tools correctly
- Sometimes explains instead of acting
- Sometimes stalls or outputs nothing

---

## 📊 Capability Assessment

| Capability | Status |
|-----------|--------|
| Local inference | ✅ |
| Tool execution | ✅ |
| Tool decision-making | ⚠️ |
| Command accuracy | ⚠️ |
| Output reliability | ❌ |

---

## 🧠 Operational Model

Hermes Forge currently functions as:

> 🧠 **AI Operator Assistant (Human-in-the-Loop)**

NOT:

> 🤖 Fully autonomous agent

---

## 🔄 Recommended Workflow

1. Ask Hermes for commands
2. Execute or verify manually
3. Feed real output back
4. Request analysis

---

## 🦂 Key Insight

> Local AI agents on constrained hardware are viable, but require guided interaction.

---

## 🔮 Future Work

- Test older Hermes versions (pre-64K enforcement)
- Evaluate mistral:7b under rollback conditions
- Improve prompting strategies
- Integrate with Burrow tooling stack

---

## 🏷️ Repo Placement

/builds/hermes-forge-krypton1t3.md

---

## 🦂 The Burrow

**Local AI. Real Control.**
