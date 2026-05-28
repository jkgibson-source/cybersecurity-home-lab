# BurrowMCP — Session 2 Journal
**Date:** 2026-05-03  
**Author:** JBird + Claude  
**Status:** ✅ Milestone achieved — BurrowMCP connected to Claude Desktop and responding

---

## Session Goal
Wire BurrowMCP into Claude Desktop and confirm end-to-end tool call works.

---

## What We Accomplished

### Python Symlink Fix
Confirmed symlink was already correct from Session 1:
```
venv/bin/python3.11 -> /opt/homebrew/opt/python@3.11/bin/python3.11
```

### Claude Desktop Config
The config file did not exist yet — created the directory first:
```bash
mkdir -p ~/Library/Application\ Support/Claude
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

The file already contained `mempalace` and `cve-mcp` entries. Added BurrowMCP as a third entry in the `mcpServers` block:

```json
{
  "mcpServers": {
    "mempalace": {
      "command": "python3",
      "args": [
        "-m",
        "mempalace.mcp_server",
        "--palace",
        "/Users/EagleEye11/BirdsNest/mempalace"
      ]
    },
    "cve-mcp": {
      "command": "/Users/EagleEye11/cve-mcp-server/.venv/bin/cve-mcp",
      "args": []
    },
    "BurrowMCP": {
      "command": "/Volumes/Bird's Nest/BurrowMCP/venv/bin/python3.11",
      "args": ["/Volumes/Bird's Nest/BurrowMCP/server.py"]
    }
  },
  "preferences": {
    "coworkScheduledTasksEnabled": false,
    "ccdScheduledTasksEnabled": false,
    "sidebarMode": "chat",
    "coworkWebSearchEnabled": true,
    "floatingAtollActive": true
  }
}
```

### Issues Encountered & Resolved

| Issue | Cause | Fix |
|-------|-------|-----|
| `~/Library/Application Support/Claude` didn't exist | Fresh Claude Desktop install | `mkdir -p` to create it |
| BurrowMCP showed `failed` on first launch | `args` path saved as `./Volumes/...` (relative) instead of `/Volumes/...` (absolute) | Re-edited config to ensure leading `/` on server.py path |
| No 🔨 hammer icon after successful launch | Claude Desktop shows local MCP servers in Connectors menu, not hammer | Expected behavior — BurrowMCP visible and toggled on in Connectors |

### First Successful Tool Call
Asked Claude Desktop: *"What's the lab status?"*

BurrowMCP called `get_lab_status()` and returned:

| Node | Tailscale IP | Status | Role |
|------|-------------|--------|------|
| EagleEye11 | 100.113.239.38 | ✅ ONLINE | Hub / Splunk / Wazuh |
| Krypton1t3 | 100.103.171.45 | ✅ ONLINE | Fedora / Hypervisor |
| SkorpiOm | 100.102.6.14 | ⏸ UNKNOWN | Kali / Attack machine |
| Jynx13 | 100.108.182.39 | ⏸ UNKNOWN | macOS / OSINT |

`UNKNOWN` is expected — current `get_lab_status()` is hardcoded. Real Tailscale pings come in Session 3.

---

## Session 3 — Next Steps

1. **Fix python symlink** (if needed — verify with `python --version` inside venv)
2. **Write `config.py`** — node hostnames, Tailscale IPs, SSH usernames
3. **Replace hardcoded `get_lab_status()`** with real Tailscale ping logic:
   ```python
   # Option A: shell out to Tailscale CLI
   /Applications/Tailscale.app/Contents/MacOS/Tailscale ping <hostname> --timeout 2
   
   # Option B: Tailscale API (requires API token)
   # GET https://api.tailscale.com/api/v2/tailnet/-/devices
   ```
4. **Test live status** — SkorpiOm and Jynx13 should flip from UNKNOWN to ONLINE/OFFLINE
5. **Begin SSH setup** — passwordless key auth from EagleEye11 to other nodes over Tailscale
6. **Begin `tools/lab_status.py`** — move logic out of server.py into proper module

---

## Key Concepts Reinforced This Session

**JSON config strictness:** Trailing commas and relative vs absolute paths both cause silent failures in Claude Desktop. Always `cat` the config after editing to verify.

**Local MCP servers in Claude Desktop:** Don't appear under the hammer icon — they live in the Connectors menu (+ button → Connectors). Toggled blue = active.

**stdio transport:** Claude Desktop pipes stdin/stdout to the server process. The server must stay running while Claude Desktop is open. If it crashes, Claude Desktop shows "Server disconnected" in Settings → Developer.

---

## Commands Quick Reference

```bash
# Activate venv
source "/Volumes/Bird's Nest/BurrowMCP/venv/bin/activate"

# Run server manually (for testing)
cd "/Volumes/Bird's Nest/BurrowMCP"
python3.11 server.py

# Edit Claude Desktop config
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Verify config
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Check Tailscale status
/Applications/Tailscale.app/Contents/MacOS/Tailscale status

# Ping a node via Tailscale
/Applications/Tailscale.app/Contents/MacOS/Tailscale ping krypton1t3
```

---

*The Burrow has a voice. BurrowMCP is live. 🦅*

---

**Tags:** `#BurrowMCP` `#MCP` `#ClaudeDesktop` `#EagleEye11` `#Tailscale` `#Session2` `#milestone` `#get_lab_status` `#homelab` `#FastMCP`
