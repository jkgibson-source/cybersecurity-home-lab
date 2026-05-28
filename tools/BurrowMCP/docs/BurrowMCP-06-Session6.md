# BurrowMCP — Session 6 Journal
**Date:** 2026-05-05
**Author:** JBird + Claude
**Status:** ✅ Complete — `get_wazuh_alerts()` live, logging pipeline extended

---

## Session Goal
Implement `get_wazuh_alerts()` using `docker exec` into the Wazuh manager container on EagleEye11. Wire into `server.py`, clean up the old stub in `ssh_tools.py`, and confirm live alert data flowing through Claude Desktop.

---

## What We Accomplished

### 1. Docker Desktop Upgraded to v4.71.0 ✅
Upgraded cleanly before the session. All 5 containers survived:

| Container | Image | Status |
|---|---|---|
| single-node-wazuh.manager-1 | wazuh/wazuh-manager:4.9.0 | ✅ Running |
| single-node-wazuh.indexer-1 | wazuh/wazuh-indexer:4.9.0 | ✅ Running |
| single-node-wazuh.dashboard-1 | wazuh/wazuh-dashboard:4.9.0 | ✅ Running |
| the-burrow-connector | twingate/connector:1 | ✅ Running |
| single-node (parent) | — | ✅ Running |

**Note:** Docker Desktop now includes an MCP Toolkit (beta) — flagged for future exploration.

---

### 2. Container Discovery
The Wazuh manager container full name (Docker Compose format):
```
single-node-wazuh.manager-1
```
Alert log confirmed at:
```
/var/ossec/logs/alerts/alerts.json
```
Format: **NDJSON** — one JSON object per line. Also contains a `2026/` subdirectory (rotated logs) and `alerts.log` (plaintext duplicate).

---

### 3. `tools/wazuh_tools.py` — New Module ✅

```python
import subprocess
import json
from tools.logger import log_tool_call

WAZUH_CONTAINER = "single-node-wazuh.manager-1"
WAZUH_ALERT_LOG = "/var/ossec/logs/alerts/alerts.json"

def get_wazuh_alerts(n: int = 20) -> str:
    try:
        result = subprocess.run(
            ["docker", "exec", WAZUH_CONTAINER, "tail", f"-n", str(n), WAZUH_ALERT_LOG],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            error = f"ERROR: docker exec failed — {result.stderr.strip()}"
            log_tool_call("get_wazuh_alerts", "EagleEye11", error)
            return error

        alerts = []
        for line in result.stdout.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                alerts.append(json.loads(line))
            except json.JSONDecodeError:
                continue

        if not alerts:
            msg = "No alerts parsed from log."
            log_tool_call("get_wazuh_alerts", "EagleEye11", msg)
            return msg

        lines = [f"=== {len(alerts)} Wazuh Alerts (last {n} lines) ===\n"]
        for a in alerts:
            ts = a.get("timestamp", "?")
            rule = a.get("rule", {})
            level = rule.get("level", "?")
            desc = rule.get("description", "?")
            agent = a.get("agent", {}).get("name", "?")
            groups = ", ".join(rule.get("groups", []))
            mitre = a.get("rule", {}).get("mitre", {})
            tactic = ", ".join(mitre.get("tactic", [])) if mitre else ""
            lines.append(
                f"[{ts}] Level {level} | Agent: {agent}\n"
                f"  Rule: {desc}\n"
                f"  Groups: {groups}"
                + (f"\n  MITRE: {tactic}" if tactic else "")
                + "\n"
            )

        output = "\n".join(lines)
        log_tool_call("get_wazuh_alerts", "EagleEye11", output)
        return output

    except subprocess.TimeoutExpired:
        error = "ERROR: docker exec timed out"
        log_tool_call("get_wazuh_alerts", "EagleEye11", error)
        return error
    except Exception as e:
        error = f"ERROR: {str(e)}"
        log_tool_call("get_wazuh_alerts", "EagleEye11", error)
        return error
```

---

### 4. `ssh_tools.py` Stub Removed ✅

The old `get_wazuh_alerts()` stub in `ssh_tools.py` was a dead-end implementation — it tried to read `WAZUH_ALERT_LOG` directly from the host filesystem (no `docker exec`), which would never work since the log lives inside the container. Removed cleanly:

- Lines 43–88 deleted (duplicate `import json`, duplicate `import subprocess`, `WAZUH_ALERT_LOG` constant, full broken function)
- Stray orphaned `return "\n".join(output_lines)` at line 43 (post-delete) caught and removed
- `ssh_tools.py` now ends cleanly with `check_failed_services`

---

### 5. `server.py` Updated ✅

Import redirected from `tools.ssh_tools` → `tools.wazuh_tools`. Tool wrapper signature updated to match new function:

```python
from tools.wazuh_tools import get_wazuh_alerts as _get_wazuh_alerts

@mcp.tool()
def get_wazuh_alerts(n: int = 20) -> str:
    """
    Returns the most recent Wazuh alerts from the Wazuh manager container on EagleEye11.
    n controls how many log lines to tail (default 20). Each line is one alert.
    """
    return _get_wazuh_alerts(n)
```

---

### 6. Live Smoke Test ✅

First real `get_wazuh_alerts()` call from Claude Desktop returned 20 alerts, all from Jynx13:

- **14x Level 7** — netstat port change detections, firing every 6–12 min. Routine macOS background activity (mDNS, app listeners). Noisy but normal.
- **6x Level 3** — Screen lock/unlock events for UserID 501. Tagged by Wazuh with MITRE categories (Defense Evasion, Persistence, Privilege Escalation) by default — benign in context.

Nothing from Krypton1t3, SkorpiOm, or EagleEye11 in last 20 lines.

---

## Bug Encountered: Python 3.9 / 3.11 Venv Symlink Mismatch

**Symptom:** Syntax check `python3 -c "import server"` threw `ModuleNotFoundError: No module named 'mcp'` despite `pip show mcp` showing it installed.

**Root cause:** The venv's `python3` symlink points to `/Library/Developer/CommandLineTools/usr/bin/python3` (Python 3.9.6 — Apple Xcode CLI tools). But the venv was created with Python 3.11 and packages are installed at `venv/lib/python3.11/site-packages`. The two Pythons can't see each other's packages.

**Fix for interactive use:** Call `python3.11` explicitly:
```bash
"/Volumes/Bird's Nest/BurrowMCP/venv/bin/python3.11" -c "import server"
```

**Why BurrowMCP still works:** `start_burrowmcp.sh` already hardcodes `python3.11`:
```bash
exec "/Users/EagleEye11/BurrowMCP/venv/bin/python3.11" "/Users/EagleEye11/BurrowMCP/server.py"
```
The broken symlink only affects ad-hoc terminal invocations, not the actual MCP runtime.

**Future fix (optional):** Recreate the venv with an explicit Python 3.11 base to fix the symlink permanently:
```bash
python3.11 -m venv "/Volumes/Bird's Nest/BurrowMCP/venv"
```

---

## Wazuh Agent Status (Discovered This Session)

Wazuh dashboard showed: **1 active, 2 disconnected.**

| Agent | Node | Status |
|---|---|---|
| Jynx13 | macOS Monterey | ✅ Active |
| SkorpiOm | Kali Linux | 🔴 Disconnected |
| Krypton1t3 | Fedora Security Lab 44 | 🔴 Disconnected |
| EagleEye11 | macOS M1 (SIEM hub) | ❌ No agent installed |

EagleEye11 has no Wazuh agent — the SIEM hub isn't monitoring itself.

---

## Current File Structure
```
~/start_burrowmcp.sh                  ← Claude Desktop entry point

/Volumes/Bird's Nest/BurrowMCP/
├── venv/
├── server.py                         # v0.5 — wazuh_tools import, updated wrapper
├── config.py                         # SPLUNK_PASS via os.environ.get()
├── start_burrowmcp.sh
├── tools/
│   ├── __init__.py
│   ├── lab_status.py
│   ├── ssh_tools.py                  # stub removed, clean
│   ├── splunk_tools.py
│   ├── wazuh_tools.py                # ← NEW — docker exec implementation
│   └── logger.py
├── logs/
│   └── burrowmcp.log                 # live telemetry
└── docs/
    ├── BurrowMCP-0[1-5].md
    └── BurrowMCP-06-Session6.md      ← this file
```

---

## Parked for Session 7

1. **Wazuh agent reconnects** — SkorpiOm and Krypton1t3 disconnected; need service restart on both. EagleEye11 needs a fresh macOS agent install.
2. **Twingate/Tailscale coexistence on Krypton1t3** — routing conflict when both run simultaneously. Diagnostic: `ip route show` and `resolvectl status` on Krypton1t3 with both active.
3. **EagleEye11 internal drive cleanup** — at 92%. Safe targets identified: Edge (707M), Skype (275M), DAZ 3D (170M), WebEx (95M). ~1.25G recoverable.
4. **Docker Desktop MCP Toolkit (beta)** — spotted in the new Docker Desktop sidebar. Worth exploring — could open interesting local tool integration paths.
5. **BurrowVoice integration path** — how BurrowVoice hands off to BurrowMCP. Krypton1t3 SSH key loose end still open.

---

*"The Burrow now sees its own alerts. The watchtower has eyes."*
— BurrowMCP Session 6, May 2026

---

**Tags:** `#BurrowMCP` `#Session6` `#Wazuh` `#Docker` `#get_wazuh_alerts` `#wazuh_tools` `#NDJSON` `#docker_exec` `#python311` `#venv` `#symlinkbug` `#EagleEye11` `#Jynx13` `#SkorpiOm` `#Krypton1t3` `#MITREattack` `#homelab` `#FastMCP` `#ClaudeDesktop`
