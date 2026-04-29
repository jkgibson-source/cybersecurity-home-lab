# 🦾 THE BURROW
## Mercury Agent + Ollama Integration Test
### Krypton1t3 Experimental Report

> **Hermes Forge Experimental Track**  
> **System:** Krypton1t3 (Fedora Security Lab)  
> **Role:** Agent Testing & AI Integration

---

## 🎯 Objective

Evaluate whether Mercury Agent can be integrated with a local Ollama stack as a potential execution layer for Hermes Forge within The Burrow architecture.

---

## 🧰 Environment

- **Host:** Krypton1t3 (2014 MacBook Pro, Fedora Security Lab)
- **LLM Runtime:** Ollama (local)
- **Agent Framework:** Mercury Agent v1.1.4
- **Models available:** llama3.2:3b, gemma4:e2b, qwen2.5:7b, mistral:7b, deepseek-coder:6.7b, phi3:mini

---

## ⚙️ Installation

```bash
# Mercury Agent
npm install -g @cosmicstack/mercury-agent

# Ollama
ollama serve
ollama list
```

**Configuration (`.env`):**
```env
DEFAULT_PROVIDER=ollamaLocal
OLLAMA_LOCAL_BASE_URL=http://127.0.0.1:11434/api
OLLAMA_LOCAL_MODEL=llama3.2
```

---

## 🧪 Test Procedure

1. Installed Mercury Agent globally via npm
2. Resolved PATH and npm prefix issues
3. Verified Mercury CLI functionality
4. Configured Ollama Local provider
5. Attempted system analysis prompt

---

## ❌ Observed Behavior

Mercury failed to execute any LLM-based task. Every attempt produced the same error:

```text
Unsupported model version v1 for provider "ollama.chat"
AI SDK 5 only supports models that implement specification version "v2"
```

Fallback attempts to other configured providers returned:

```text
All LLM providers failed.
```

---

## 🔍 Root Cause

A direct query to the Ollama API confirmed the issue:

```bash
curl http://127.0.0.1:11434/api/tags
```

All models returned `"format": "gguf"` — indicating they expose a v1 interface. Mercury Agent runs on AI SDK v5, which requires models implementing the v2 specification. There is currently no compatibility bridge between the two.

---

## 🧠 Findings

Mercury Agent is incompatible with standard Ollama local model deployments as of this test. The failure isn't a configuration problem — it's a spec mismatch at the SDK level. The existing Hermes + Ollama stack remains the primary local agent solution in The Burrow until either Mercury updates its Ollama provider or Ollama introduces v2-compatible interfaces.

This experiment is paused, not abandoned. Worth revisiting when either side of the stack moves.

---

## 🔄 Next Steps

- Monitor Mercury Agent releases for updated Ollama provider support
- Monitor Ollama for v2-compatible model interfaces
- Evaluate alternative local agent frameworks in the interim

---

## ⚠️ Status

⏸️ **Paused — pending upstream updates**

---

**Green • Black | Experimental Node: Krypton1t3**
