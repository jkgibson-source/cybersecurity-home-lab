# 🦂 HexStrike + Ollama MCP Runbook
### Jynx13 (Parrot OS Live w/ Persistence)

---

## 🎯 Objective

Establish a fully local AI-driven offensive tooling pipeline:

```
Ollama (LLM) ←→ mcphost (bridge) ←→ HexStrike MCP Server (tools)
```

This enables natural language → real tool execution (nmap, nuclei, OSINT tools, etc.) inside your lab.

---

## 🧠 System Context (The Burrow)

- **Jynx13** → OSINT / AI orchestration node
- **SkorpiOm** → Attack box (Kali)
- **Krypton1t3** → Target
- **EagleEye11** → Logging / SIEM (Splunk + Wazuh)

---

## ✅ Step 1 — Verify HexStrike Location

```bash
cd /usr/share/hexstrike-ai
ls -la
```

Confirm presence of:

- `hexstrike_server.py`
- `hexstrike_mcp.py`

---

## ✅ Step 2 — Ensure Ollama is Running

```bash
curl http://127.0.0.1:11434/api/tags
```

If not running:

```bash
ollama serve &
```

Verify models:

```bash
ollama list
```

---

## ✅ Step 3 — Start HexStrike Server

⚠️ Parrot OS version does **NOT** support `--server` flag

```bash
cd /usr/share/hexstrike-ai
python3 hexstrike_server.py
```

Expected output:

```
[INFO] Server starting on 127.0.0.1:8888
```

---

## ✅ Step 4 — Verify Server Health

Open new terminal:

```bash
curl http://127.0.0.1:8888/health
```

Expected:

- `"status": "healthy"`
- tools listed (nmap, nuclei, etc.)

---

## ✅ Step 5 — Install mcphost (Bridge)

```bash
sudo apt install golang
```

```bash
go install github.com/mark3labs/mcphost@latest
export PATH=$PATH:$HOME/go/bin
```

Persist path:

```bash
echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.bashrc
source ~/.bashrc
```

---

## ✅ Step 6 — Create MCP Config

```bash
nano ~/hexstrike-ai-mcp.json
```

Paste:

```json
{
  "mcpServers": {
    "hexstrike-ai": {
      "command": "/usr/bin/python3",
      "args": [
        "/usr/share/hexstrike-ai/hexstrike_mcp.py",
        "--server",
        "http://127.0.0.1:8888"
      ]
    }
  }
}
```

---

## ✅ Step 7 — Launch MCP Bridge

⚠️ Correct syntax (IMPORTANT):

```bash
mcphost -m ollama:llama3.2:1b --config ~/hexstrike-ai-mcp.json
```

NOT:

```bash
ollama/llama3.2:1b  ❌
```

---

## ✅ Step 8 — Confirm Connection

Expected output:

```
Connected to MCP server: hexstrike-ai
Loaded X tools from MCP servers
```

---

## 🧪 Step 9 — Testing Commands

### Basic tool listing

```
List available hexstrike-ai tools.
```

### Controlled nmap scan

```
I am authorized to test my own lab machine at <TARGET-IP>.
Use hexstrike-ai to run a basic nmap service scan.
```

### Direct tool instruction (more reliable)

```
Use hexstrike-ai nmap tool to run: nmap -sV <TARGET-IP>
```

---

## ⚠️ Model Limitations

`llama3.2:1b`:

- Weak tool-calling
- May stall on "Thinking..."

### Recommended alternatives

```bash
mcphost -m ollama:gemma3:1b --config ~/hexstrike-ai-mcp.json
```

Or create a tool-aware model.

---

## 🔥 Troubleshooting

### ❌ Cannot connect to 8888

```bash
ss -tulpn | grep 8888
```

Restart server.

---

### ❌ Unsupported provider error

Fix model syntax:

```bash
ollama:MODEL_NAME
```

---

### ❌ No tool execution

- Use more explicit prompts
- Switch to stronger model

---

## 🦂 Operational Notes (Burrow)

Jynx13 now functions as:

- AI-driven recon engine
- OSINT automation node
- Tool orchestration system
- Remote observer (via Tailscale)

This integrates directly into your pentest phases:

- Phase 0 → OSINT automation
- Phase A/B → Recon + validation
- Phase C → Evasion + comparison

---

## 🏁 Status

✅ HexStrike Server Running  
✅ MCP Bridge Connected  
✅ Ollama Integrated  

🚀 **System Ready for AI-assisted offensive operations**

---

## 📌 Next Enhancements

- Custom tool-aware Ollama model
- Logging HexStrike output to Splunk
- Automating OSINT workflows
- Burrow-wide orchestration scripts

---

🦂 *The Burrow — Offensive + Defensive + Intelligence Unified*

