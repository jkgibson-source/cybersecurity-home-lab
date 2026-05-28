# BurrowMCP — Session 1 Journal
**Date:** 2026-05-03  
**Author:** JBird + Claude  
**Status:** ✅ Milestone achieved — BurrowMCP starts up

---

## Session Goal
Stand up the Python environment and get a minimal MCP server running on EagleEye11.

---

## What We Accomplished

### Environment Setup
- Confirmed Python 3.9.6 (system) is too old for MCP SDK — requires 3.10+
- Installed Python 3.11 via Homebrew (`brew install python@3.11`)
- Created Python virtual environment on Bird's Nest:
  ```bash
  cd "/Volumes/Bird's Nest"
  mkdir BurrowMCP && cd BurrowMCP
  /opt/homebrew/bin/python3.11 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install mcp
  ```
- MCP SDK 1.27.0 installed successfully with full dependency stack:
  `starlette, uvicorn, pydantic, httpx-sse, anyio, cryptography` and more

### Folder Structure Created
```
/Volumes/Bird's Nest/BurrowMCP/
├── venv/                  # Python 3.11 virtual environment
├── server.py              # Main MCP server (v0.1)
├── tools/                 # Tool modules (empty, Session 2)
│   └── __init__.py
├── config.py              # Node config (empty, Session 2)
├── logs/                  # Tool call logs (Session 2)
└── docs/
    ├── BurrowMCP-00-Architecture.md
    └── BurrowMCP-01-Session1.md  ← this file
```

### server.py v0.1 Written
- Single tool: `get_lab_status()` — returns hardcoded node status
- Uses `FastMCP` framework with `stdio` transport
- Fully commented for learning purposes

### 🦅 First Successful Startup
```
🦅 BurrowMCP starting up...
```
Confirmed running via `python3.11 server.py`

---

## Issues Encountered & Resolved

| Issue | Cause | Fix |
|-------|-------|-----|
| `pip install mcp` failed initially | Python 3.9.6 too old | Installed Python 3.11 via Homebrew |
| `ModuleNotFoundError: No module named 'mcp'` | venv `python` symlink pointed to system Python 3.9 | Run with `python3.11` explicitly |
| `tailscale status` not found in terminal | macOS app installs CLI at non-standard path | Use `/Applications/Tailscale.app/Contents/MacOS/Tailscale status` |

---

## Symlink Fix (do this before Session 2)
The `python` command inside the venv points to system Python 3.9 instead of Homebrew 3.11. Fix:
```bash
cd "/Volumes/Bird's Nest/BurrowMCP"
source venv/bin/activate
ln -sf /opt/homebrew/opt/python@3.11/bin/python3.11 venv/bin/python
python --version  # should now show Python 3.11.x
python server.py  # should now work without specifying python3.11
```

---

## Tailscale Node Reference
Confirmed live from Tailscale app during session:

| Hostname | Tailscale IP | Status |
|----------|-------------|--------|
| eagleeye11 | 100.113.239.38 | ✅ Online |
| krypton1t3 | 100.103.171.45 | ✅ Online |
| skorpiom | 100.102.6.14 | ⏸ Offline (sleeping) |
| jynx13 | 100.108.182.39 | ⏸ Offline (sleeping) |
| iphone-13 | 100.95.11.33 | ✅ Online |
| iphone-11-pro | 100.123.87.87 | ✅ Online |

---

## Session 2 — Next Steps

1. **Fix python symlink** (see above — do first)
2. **Wire BurrowMCP into Claude Desktop config** so Claude can actually call the tool
3. **Test end-to-end:** Ask Claude "what's the lab status?" and watch it call `get_lab_status()`
4. **Write `config.py`** — node IPs, SSH settings, allowlists
5. **Add real Tailscale status check** to replace hardcoded `get_lab_status()` response
6. **Begin SSH setup** — EagleEye11 → other nodes via Tailscale (passwordless key auth)

---

## Key Concepts Learned This Session

**Virtual environment (venv):** An isolated Python environment. Packages installed inside it don't affect the rest of the system. Must be activated each session with `source venv/bin/activate`. The `(venv)` prefix in the prompt confirms it's active.

**MCP SDK / FastMCP:** The framework that handles all MCP protocol communication with Claude. We define tools using the `@mcp.tool()` decorator and it handles the rest.

**stdio transport:** How Claude Desktop talks to a local MCP server — via standard input/output piped between processes. When we go remote (for SolSkorp_13 mobile access), we'll switch to SSE transport.

**Docstrings as tool descriptions:** The text in triple quotes under each `@mcp.tool()` function is what Claude reads to understand when and how to use the tool. Write them clearly.

---

## Commands Quick Reference

```bash
# Activate venv
source "/Volumes/Bird's Nest/BurrowMCP/venv/bin/activate"

# Run server
cd "/Volumes/Bird's Nest/BurrowMCP"
python3.11 server.py

# Check Tailscale status
/Applications/Tailscale.app/Contents/MacOS/Tailscale status

# Tailscale ping a node
/Applications/Tailscale.app/Contents/MacOS/Tailscale ping krypton1t3
```

---

*BurrowMCP is alive. The Burrow has a voice. 🦅*

---

**Tags:** `#BurrowMCP` `#MCP` `#Python` `#EagleEye11` `#Tailscale` `#Session1` `#venv` `#FastMCP` `#homelab` `#milestone`
