# BurrowMCP — Session 4 Journal
**Date:** 2026-05-03  
**Author:** JBird + Claude  
**Status:** ✅ Milestone achieved — First live SSH tool calls working end-to-end in Claude Desktop

---

## Session Goal
Stand up SSH key-based authentication from EagleEye11 to remote nodes, then build and test the first live SSH tools: `get_node_info()`, `check_disk_space()`, and `check_failed_services()`.

---

## What We Accomplished

### SSH Key Distribution — `burrowmcp_ed25519`
Generated `burrowmcp_ed25519` on EagleEye11 (already in place from prior session) and distributed the public key to remote nodes.

**SkorpiOm** — `ssh-copy-id` worked cleanly on first attempt. 1 key added.

**Krypton1t3** — Required several debugging rounds:

| Attempt | Result | Cause |
|---------|--------|-------|
| `ssh-copy-id` | Permission denied | Password auth disabled on Krypton1t3 |
| Manual key entry in nano | Still denied | Username case mismatch |
| `SuperSkorp_7` (correct case) | ✅ Accepted | Linux usernames are case-sensitive |

**Root cause:** `config.py` had `ssh_user: "superskorp_7"` (all lowercase). The actual username on Krypton1t3 is `SuperSkorp_7` with two capital letters. SSHD logs confirmed it: `Invalid user superskorp_7`. Fixed in `config.py`.

**Verification — both nodes green:**
```
Krypton1t3   up 12:47,  2 users,  load average: 0.13, 0.21, 0.20
SkorpiOm     up 1 day, 23:34,  2 users,  load average: 0.31, 0.36, 0.35
```

---

### `tools/ssh_tools.py` — New Module

Wrote the SSH execution backbone for all future remote tools:

```python
import subprocess
from config import NODES, SSH_KEY_PATH

def run_ssh_command(node_name: str, command: str) -> str:
    node = NODES.get(node_name)
    if not node:
        return f"ERROR: Unknown node '{node_name}'"
    if node.get("is_local"):
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip() or result.stderr.strip()
    ip = node["tailscale_ip"]
    user = node["ssh_user"]
    result = subprocess.run(
        ["ssh", "-i", SSH_KEY_PATH, "-o", "StrictHostKeyChecking=no",
         f"{user}@{ip}", command],
        capture_output=True, text=True, timeout=15
    )
    return result.stdout.strip() or result.stderr.strip()

def get_node_info(node_name: str) -> str:
    hostname = run_ssh_command(node_name, "hostname")
    uptime = run_ssh_command(node_name, "uptime")
    return f"{hostname} | {uptime}"

def check_disk_space(node_name: str) -> str:
    return run_ssh_command(node_name, "df -h --output=source,size,used,avail,pcent,target | head -20")

def check_failed_services(node_name: str) -> str:
    return run_ssh_command(node_name, "systemctl --failed --no-legend 2>/dev/null || echo 'N/A (not systemd)'")
```

`is_local: True` on EagleEye11 bypasses SSH and runs commands directly. All other nodes go through the key-authenticated SSH path.

---

### `server.py` — Three New Tools Registered

```python
from tools.ssh_tools import (
    get_node_info as _get_node_info,
    check_disk_space as _check_disk_space,
    check_failed_services as _check_failed_services
)

@mcp.tool()
def get_node_info(node_name: str) -> str:
    """
    Returns hostname and uptime for a lab node via SSH.
    node_name must match a key in NODES config (e.g. 'Krypton1t3', 'SkorpiOm', 'Jynx13').
    """
    return _get_node_info(node_name)

@mcp.tool()
def check_disk_space(node_name: str) -> str:
    """
    Returns disk usage for a lab node via SSH.
    node_name must match a key in NODES config (e.g. 'Krypton1t3', 'SkorpiOm', 'Jynx13').
    """
    return _check_disk_space(node_name)

@mcp.tool()
def check_failed_services(node_name: str) -> str:
    """
    Returns any failed systemd services on a lab node via SSH.
    Returns N/A for macOS nodes. node_name must match a key in NODES config.
    """
    return _check_failed_services(node_name)
```

---

## Smoke Test Results

### `get_node_info("Krypton1t3")`
```
Krypton1t3 | 23:04:37 up 12:57, 2 users, load average: 0.13, 0.21, 0.20
```
✅ First live SSH tool call through BurrowMCP. Clean.

### `check_disk_space("SkorpiOm")` + `check_disk_space("Krypton1t3")`
```
SkorpiOm    /dev/sda2   225G   177G used   38G free   83%   ⚠️
Krypton1t3  /dev/sda3   232G    77G used  153G free   34%   ✅
```
SkorpiOm at 83% — worth monitoring. Snap loop devices showing 100% are read-only squashfs mounts, not a real problem. Krypton1t3 has plenty of headroom for KVM guests.

### `check_failed_services("SkorpiOm")` + `check_failed_services("Krypton1t3")`
```
SkorpiOm    networking.service   FAILED   ⚠️ (known — NetworkManager conflict on Kali, cosmetic)
Krypton1t3  twingate.service     FAILED   ⚠️ (known — intentionally stopped)
```

**Twingate note:** Twingate is installed and configured on Krypton1t3 but conflicts with Tailscale — both fight for routing control and disrupt internet connectivity when run simultaneously. Currently parked in favor of Tailscale. Goal: find a coexistence solution before the NY trip in late July/August.

---

## Bugs Encountered & Fixed

| Bug | Cause | Fix |
|-----|-------|-----|
| `ssh-copy-id` denied on Krypton1t3 | Password auth disabled | Manual key entry required |
| Manual key entry still denied | `ssh_user` lowercase in config didn't match actual username | Fixed to `SuperSkorp_7` in `config.py` |

---

## Current File Structure
```
~/BurrowMCP/               ← symlink to /Volumes/Bird's Nest/BurrowMCP/
├── venv/
├── server.py              # v0.3 — get_node_info, check_disk_space, check_failed_services added
├── config.py              # SSH_KEY_PATH defined; SuperSkorp_7 corrected
├── tools/
│   ├── __init__.py
│   ├── lab_status.py      # ping_node() + get_lab_status()
│   └── ssh_tools.py       # run_ssh_command() + all SSH-based tools ← NEW
├── logs/                  # (pending)
└── docs/
    ├── BurrowMCP-00-Architecture.md
    ├── BurrowMCP-01-Session1.md
    ├── BurrowMCP-02-Session2.md
    ├── BurrowMCP-03-Session3.md
    └── BurrowMCP-04-Session4.md   ← this file

~/start_burrowmcp.sh       ← real file, no spaces, Claude Desktop entry point
```

---

## Session 5 — Next Steps

1. **Logging** — every tool call writes a timestamped entry to `logs/` and forwards to Splunk via Universal Forwarder
2. **`get_wazuh_alerts()` tool** — pull recent Wazuh alerts by node and severity from EagleEye11
3. **`splunk_search()` tool** — run a Splunk search query and return results
4. **Twingate/Tailscale coexistence research** — find a routing split or override solution for Krypton1t3
5. **Jynx13 SSH key** — distribute `burrowmcp_ed25519` to Jynx13 and verify

---

## Key Concepts Reinforced This Session

**Linux usernames are case-sensitive:** `superskorp_7` and `SuperSkorp_7` are completely different users. SSHD logs (`journalctl -u sshd`) are the fastest way to diagnose auth failures — "Invalid user" tells you immediately it's a username problem, not a key problem.

**SSHD logs before assumptions:** When SSH fails, read the daemon logs first. Don't guess at permissions or key formatting when the actual error message is one command away.

**`authorized_keys` supports multiple keys:** Having two keys in the file is normal and expected. SSH tries each one in order. Multiple keys are not the cause of auth failures.

**`is_local` pattern:** Running `subprocess` directly on EagleEye11 instead of SSH-ing to localhost avoids unnecessary complexity and keeps the local execution path clean.

---

*"Four tools in 90 minutes. The Burrow now reports for duty."*  
— BurrowMCP Session 4, May 2026

---

**Tags:** `#BurrowMCP` `#MCP` `#ClaudeDesktop` `#EagleEye11` `#Krypton1t3` `#SkorpiOm` `#SSH` `#Session4` `#milestone` `#get_node_info` `#check_disk_space` `#check_failed_services` `#ssh_tools` `#homelab` `#FastMCP` `#Tailscale` `#Twingate` `#debugging` `#SELinux` `#sshd`
