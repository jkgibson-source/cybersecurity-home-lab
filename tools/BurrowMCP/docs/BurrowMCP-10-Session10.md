# BurrowMCP — Session 10 Journal
**Date:** 2026-05-07
**Author:** JBird + Claude
**Status:** ✅ Complete — Jynx13 joins The Burrow as a fully operational remote node

---

## Session Goal
Deploy BurrowMCP on Jynx13 (MacBook Air 2017, macOS Monterey) so that Claude for Mac on the travel node can interact with The Burrow crew — EagleEye11, Krypton1t3, and SkorpiOm — over the Tailscale mesh, without requiring Claude Pro or a Cloudflare tunnel.

---

## What We Accomplished

### 1. Explored SSE Approach First ✅
Attempted to connect Jynx13's Claude for Mac to EagleEye11's BurrowMCP SSE server (port 8766) over Tailscale. Flipped EagleEye11 back to SSE mode and confirmed listener was live:

```bash
lsof -i -nP | grep 8766
# Result: Python  68400  EagleEye11  TCP *:8766 (LISTEN)
```

However, Claude for Mac (App Store version, v1.6259.1) only supports `command`-based stdio servers — not URL-based SSE. The attempt produced:
```
Some MCP servers could not be loaded: BurrowMCP
```

Pivoted to the correct architecture: run BurrowMCP **locally on Jynx13** in stdio mode, with tools SSHing out over Tailscale to reach the lab.

---

### 2. Installed BurrowMCP on Jynx13 ✅
Jynx13 has Python 3.13 and 3.14 installed (no 3.11). Used 3.13 for stability.

Generated `requirements.txt` from EagleEye11's venv:
```bash
/Users/EagleEye11/BurrowMCP/venv/bin/pip freeze > ~/BurrowMCP/requirements.txt
```

Copied BurrowMCP from EagleEye11 to Jynx13 via SCP over Tailscale:
```bash
scp -r EagleEye11@100.113.239.38:~/BurrowMCP ~/BurrowMCP
```

Rebuilt the venv fresh on Jynx13 with Python 3.13:
```bash
rm -rf ~/BurrowMCP/venv
python3.13 -m venv ~/BurrowMCP/venv
source ~/BurrowMCP/venv/bin/activate
pip install -r ~/BurrowMCP/requirements.txt
```

All 32 packages installed cleanly. `server.py` confirmed in stdio mode.

---

### 3. Created Wrapper Script on Jynx13 ✅
Claude for Mac strips the shell environment, so a wrapper script is required — same pattern as EagleEye11.

**File: `~/start_burrowmcp.sh`**
```bash
#!/bin/zsh
source /Users/jbird13/.zshrc 2>/dev/null
source /Users/jbird13/.zprofile 2>/dev/null
export PATH="/usr/local/bin:/usr/bin:/bin"
exec "/Users/jbird13/BurrowMCP/venv/bin/python3.13" "/Users/jbird13/BurrowMCP/server.py"
```

> **Gotcha:** nano split the `exec` line across two lines on first attempt, causing Python to launch in interactive mode instead of running server.py. Fixed by rewriting as a single line.

```bash
chmod +x ~/start_burrowmcp.sh
# Test:
/bin/zsh ~/start_burrowmcp.sh
# Terminal title bar should show "server.py" — stdio mode, waiting silently
```

---

### 4. Wired Claude for Mac on Jynx13 ✅
Edited `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "BurrowMCP": {
      "command": "/bin/zsh",
      "args": ["/Users/jbird13/start_burrowmcp.sh"]
    }
  },
  "preferences": {
    "legacyQuickEntryEnabled": false,
    "coworkScheduledTasksEnabled": false,
    "ccdScheduledTasksEnabled": false,
    "sidebarMode": "chat",
    "coworkWebSearchEnabled": true,
    "floatingAtollActive": true
  }
}
```

After Cmd+Q and relaunch: **BurrowMCP appeared in the Connectors list, toggled ON.** ✅

---

### 5. First Successful Tool Call from Jynx13 ✅
Asked Claude to run `get_lab_status`. BurrowMCP on Jynx13 reached back through Tailscale to EagleEye11 and returned a live status report:

| Node | Status | Notes |
|---|---|---|
| EagleEye11 | ✅ LOCAL | Hub, responding perfectly |
| Krypton1t3 | ⏸ TIMEOUT | Sleeping — valid |
| SkorpiOm | ⏸ TIMEOUT | SSH auth issue — in progress |
| Jynx13 | ❌ OFFLINE | Self-ping loop via Tailscale — expected |

---

### 6. SkorpiOm SSH Key Distribution ✅ (Resolved end of session)
Diagnosed why SkorpiOm timed out from Jynx13:

- `config.py` had EagleEye11's SSH key path hardcoded: `/Users/EagleEye11/.ssh/burrowmcp_ed25519`
- `ssh_tools.py` was missing `-o BatchMode=yes` — causing silent SSH hangs instead of fast failures
- SkorpiOm's network became unstable mid-session (NetworkManager conflict on Kali — known cosmetic issue). **Reboot fixed it.**

**Fixes applied:**
```bash
# Fix 1: Update SSH key path in config.py
sed -i '' 's|/Users/EagleEye11/.ssh/burrowmcp_ed25519|/Users/jbird13/.ssh/burrow_ed25519|g' ~/BurrowMCP/config.py

# Fix 2: Add BatchMode=yes to ssh_tools.py
sed -i '' 's/"StrictHostKeyChecking=no"/"StrictHostKeyChecking=no", "-o", "BatchMode=yes"/' ~/BurrowMCP/tools/ssh_tools.py

# Fix 3: Generate passwordless key for BurrowMCP
ssh-keygen -t ed25519 -f ~/.ssh/burrow_ed25519 -N ""

# Fix 4: Copy key to SkorpiOm (after reboot restored network)
ssh-copy-id -i ~/.ssh/burrow_ed25519.pub solskorp_11@100.102.6.14
```

**End of session status:** SkorpiOm responding via BurrowMCP from Jynx13. ✅

---

## Architecture — Current State

```
Claude for Mac (Jynx13)
    ↓ stdio
BurrowMCP (running locally on Jynx13, Python 3.13)
    ↓ SSH over Tailscale
EagleEye11 ✅  |  Krypton1t3 (sleeping)  |  SkorpiOm ✅
```

Jynx13 can now reach The Burrow from anywhere there's internet. No Pro required. No tunnel required. Just Tailscale doing its thing.

---

## Key Facts

| Item | Value |
|---|---|
| Jynx13 BurrowMCP path | `~/BurrowMCP/` |
| Jynx13 Python version | 3.13 (venv at `~/BurrowMCP/venv/`) |
| Jynx13 SSH key for BurrowMCP | `~/.ssh/burrow_ed25519` (passwordless) |
| Jynx13 wrapper script | `~/start_burrowmcp.sh` |
| Claude for Mac config | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| BatchMode=yes | Added to `ssh_tools.py` — prevents silent SSH hangs |
| SkorpiOm disk usage | 74% (157G / 225G) — healthy |
| SkorpiOm uptime post-reboot | 34 min, load 0.70 |

---

## Parked for Session 11
1. **Splunk license migration — DEADLINE MAY 17** ⚠️ (CRITICAL)
2. Krypton1t3 SSH key distribution from Jynx13 (same `ssh-copy-id` pattern)
3. EagleEye11 internal drive cleanup (92% full)
4. Named Cloudflare tunnel for permanent remote URL
5. BurrowMCP as launchd service on EagleEye11 (auto-start on boot)
6. APP_NAME_MAP expansion for BurrowVoice
7. Wazuh noise on Krypton1t3 — cause TBD

---

*"Jynx13 spread her wings and flew — and The Burrow flew with her."*
— BurrowMCP Session 10, May 2026

**Tags:** #BurrowMCP #Session10 #Jynx13 #travelNode #stdio #SSHkeys #BatchMode #Tailscale #Python313 #homelab #SOC #remoteAccess #ClaudeForMac #mcpServers #SkorpiOm #NetworkManager
