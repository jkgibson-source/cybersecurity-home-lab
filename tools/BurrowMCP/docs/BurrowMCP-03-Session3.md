# BurrowMCP — Session 3 Journal
**Date:** 2026-05-03  
**Author:** JBird + Claude  
**Status:** ✅ Milestone achieved — Live Tailscale pings working end-to-end in Claude Desktop

---

## Session Goal
Replace hardcoded `get_lab_status()` with real Tailscale ping logic, write `config.py`, and move tool logic into proper modules.

---

## What We Accomplished

### `config.py` — Source of Truth
Wrote the full node registry, SSH config, allowlists, paths, and confirmation tokens. All four nodes defined:

| Hostname | Tailscale IP | OS | SSH User | Role |
|----------|-------------|-----|----------|------|
| EagleEye11 | 100.113.239.38 | macOS (M1) | EagleEye11 | Hub / BurrowMCP host / Splunk / Wazuh Manager |
| Krypton1t3 | 100.103.171.45 | Fedora Security Lab 44 | superskorp_7 | Hypervisor / creative workstation |
| SkorpiOm | 100.102.6.14 | Kali Linux | solskorp_11 | Attack machine |
| Jynx13 | 100.108.182.39 | macOS Monterey | jbird13 | OSINT / general |

`is_local: True` on EagleEye11 skips SSH for local operations. `tailscaled` and `ssh` intentionally excluded from `ALLOWED_SERVICES`.

### `tools/lab_status.py` — Live Pings
Wrote `ping_node()` and `get_lab_status()`. After several debugging rounds, the working implementation:

```python
def ping_node(tailscale_name: str) -> str:
    try:
        env = os.environ.copy()
        env["PATH"] = "/usr/local/bin:/usr/bin:/bin:/Applications/Tailscale.app/Contents/MacOS"
        result = subprocess.run(
            [TAILSCALE_BIN, "ping", tailscale_name],
            capture_output=True,
            text=True,
            timeout=TAILSCALE_PING_TIMEOUT + 2,
            env=env
        )
        output = result.stdout.lower()
        if "pong" in output:
            return "ONLINE"
        else:
            return "OFFLINE"
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR: {e}"
```

Tailscale ping output format confirmed:
```
pong from krypton1t3 (100.103.171.45) via 192.168.1.172:41641 in 7ms
```
(`192.168.1.172:41641` is the Tailscale relay — normal and healthy.)

### `server.py` — Cleaned Up
Replaced the bloated Session 1 scaffold with a clean v0.2:

```python
from mcp.server.fastmcp import FastMCP
from tools.lab_status import get_lab_status as _get_lab_status

mcp = FastMCP("BurrowMCP")

@mcp.tool()
def get_lab_status() -> str:
    """
    Returns the current status of The Burrow home lab nodes.
    Use this when asked about lab status, which machines are
    online, or the health of the home lab.
    """
    return _get_lab_status()

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### `start.sh` — Environment Wrapper
Claude Desktop launches MCP servers with a stripped environment. The Tailscale CLI needs a proper PATH to reach its daemon. Solution: a wrapper shell script that sources the user environment before launching Python.

```bash
#!/bin/zsh
source /Users/EagleEye11/.zshrc 2>/dev/null
source /Users/EagleEye11/.zprofile 2>/dev/null
export PATH="/usr/local/bin:/usr/bin:/bin:/Applications/Tailscale.app/Contents/MacOS:$PATH"
exec "/Users/EagleEye11/BurrowMCP/venv/bin/python3.11" "/Users/EagleEye11/BurrowMCP/server.py"
```

Location: `~/start_burrowmcp.sh` (real file, no spaces in path)

### Claude Desktop Config — Final Working State
```json
"BurrowMCP": {
    "command": "/bin/zsh",
    "args": ["/Users/EagleEye11/start_burrowmcp.sh"]
}
```

### Symlink
```bash
ln -s "/Volumes/Bird's Nest/BurrowMCP" ~/BurrowMCP
```
Used internally by `start.sh` to reference venv and server without spaces in paths.

---

## Bugs Encountered & Fixed

| Bug | Cause | Fix |
|-----|-------|-----|
| `--timeout 3s` rejected | Tailscale CLI doesn't support that flag format | Removed flag entirely; use subprocess `timeout=` |
| `--c 1` rejected | Not a valid Tailscale ping flag | Removed |
| Syntax error line 23 | Missing `]` on subprocess args list — paste artifact | Fixed in nano |
| All nodes OFFLINE despite being up | Claude Desktop strips environment; Tailscale CLI can't find daemon | Added `os.environ.copy()` + explicit PATH in `ping_node()` |
| `print()` crashing server | `print()` to stdout corrupts the MCP stdio protocol pipe | Removed the startup print statement |
| `start.sh` "can't open input file" | Claude Desktop can't execute shell scripts directly | Changed config to use `/bin/zsh` as command, script as arg |
| Symlink failing in Claude Desktop | macOS app sandbox can't follow symlinks to external volumes | Copied `start.sh` to `~/start_burrowmcp.sh` (real file, clean path) |

---

## Final Smoke Test Result
```
🦅 BurrowMCP — Live Lab Status
=============================================
EagleEye11   (100.113.239.38) ✅ LOCAL    — Hub / BurrowMCP host / Splunk / Wazuh Manager
Krypton1t3   (100.103.171.45) ✅ ONLINE   — Hypervisor / creative workstation
SkorpiOm     (100.102.6.14)   ✅ ONLINE   — Attack machine
Jynx13       (100.108.182.39) ✅ ONLINE   — OSINT / general
=============================================
```

All four nodes green. Full mesh confirmed. 🎉

---

## Current File Structure
```
~/BurrowMCP/               ← symlink to /Volumes/Bird's Nest/BurrowMCP/
├── venv/
├── server.py              # v0.2 — clean, imports from tools module
├── config.py              # Node registry, SSH config, allowlists, confirmation tokens
├── tools/
│   ├── __init__.py
│   └── lab_status.py      # ping_node() + get_lab_status() with live Tailscale pings
├── logs/                  # (pending)
└── docs/
    ├── BurrowMCP-00-Architecture.md
    ├── BurrowMCP-01-Session1.md
    ├── BurrowMCP-02-Session2.md
    └── BurrowMCP-03-Session3.md   ← this file

~/start_burrowmcp.sh       ← real file, no spaces, Claude Desktop entry point
```

---

## Session 4 — Next Steps

1. **SSH key setup** — generate `burrowmcp_ed25519` on EagleEye11, distribute public key to Krypton1t3 and SkorpiOm
2. **`get_node_info()` tool** — hostname, OS, uptime via SSH (first real SSH tool call)
3. **`check_disk_space()` tool** — `df -h` via SSH on remote nodes
4. **`check_failed_services()` tool** — `systemctl --failed` on Linux nodes
5. **Logging** — every tool call writes to `logs/` and forwards to Splunk

---

## Key Concepts Reinforced This Session

**stdio is sacred:** Claude Desktop communicates with MCP servers via stdin/stdout. Any `print()` to stdout before or during `mcp.run()` corrupts the protocol and crashes the server silently. Use `sys.stderr` for debug output if needed.

**macOS app sandboxing:** Claude Desktop cannot follow symlinks to external volumes, and launches processes with a stripped environment. Always use real file paths for the entry point script, and always explicitly set PATH inside the script.

**Tailscale CLI flags:** On this version, `--timeout` and `--c` are not valid for `ping`. Use bare `tailscale ping <hostname>` and let Python's subprocess `timeout=` handle the kill.

**Pong format:** `pong from <hostname> (<ip>) via <relay>:<port> in <latency>ms`

---

*"Full mesh, no stragglers. The Burrow is alive."*  
— Claude Desktop on BurrowMCP, May 2026

---

**Tags:** `#BurrowMCP` `#MCP` `#ClaudeDesktop` `#EagleEye11` `#Tailscale` `#Session3` `#milestone` `#get_lab_status` `#config` `#lab_status` `#homelab` `#FastMCP` `#stdio` `#debugging` `#sandboxing`
