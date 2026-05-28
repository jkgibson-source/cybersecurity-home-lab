# BurrowMCP — Session 5 Journal
**Date:** 2026-05-04  
**Author:** JBird + Claude  
**Status:** ✅ Milestone achieved — Logging pipeline live, Splunk monitor active, all four nodes reporting disk data cleanly

---

## Session Goal
Build the logging pipeline (tool call → `logs/burrowmcp.log` → Splunk), add `get_wazuh_alerts()` and `splunk_search()` tools, distribute SSH key to Jynx13, and fix the `df --output` macOS incompatibility.

---

## What We Accomplished

### 1. `tools/logger.py` — New Logging Module

Every tool call now writes a timestamped, structured entry to `logs/burrowmcp.log`:

```python
import os
import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "burrowmcp.log")

def log_tool_call(tool_name: str, node_name: str, result: str):
    status = "ERROR" if result.startswith("ERROR") else "SUCCESS"
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    result_snippet = result.replace("\n", " | ")[:200]
    entry = f"{timestamp} | {tool_name} | {node_name} | {status} | {result_snippet}\n"
    with open(LOG_FILE, "a") as f:
        f.write(entry)
```

Log format:
```
2026-05-04T23:08:26 | check_disk_space | Krypton1t3 | SUCCESS | Filesystem  Size  Used Avail Use% ...
```

**Bug encountered:** `from tools.logger import log_tool_call` was placed at the bottom of `ssh_tools.py` instead of the top. Logger was never imported, so no entries were written. Fix: move import to top of file.

---

### 2. Splunk Monitor Stanza

Added to `/Volumes/Bird's Nest/Applications/Splunk/etc/system/local/inputs.conf`:

```ini
[monitor:///Volumes/Bird's Nest/BurrowMCP/logs/burrowmcp.log]
index = main
sourcetype = burrowmcp
host = EagleEye11
```

Splunk binary location (learned this session):
```
/Volumes/Bird's Nest/Applications/Splunk/bin/splunk
```
Not `/Volumes/Bird's Nest/splunk/bin/splunk` — the folder is `Applications/Splunk`, not `splunk`.

Restart command:
```bash
"/Volumes/Bird's Nest/Applications/Splunk/bin/splunk" restart
```

---

### 3. `tools/splunk_tools.py` — New Module

Hits the Splunk REST API on localhost:8089, submits a search job, polls until done, returns formatted results.

```python
import requests, time
from config import SPLUNK_HOST, SPLUNK_PORT, SPLUNK_USER, SPLUNK_PASS
from tools.logger import log_tool_call

SPLUNK_BASE = f"https://{SPLUNK_HOST}:{SPLUNK_PORT}"
AUTH = (SPLUNK_USER, SPLUNK_PASS)

def splunk_search(query: str, earliest: str = "-24h", latest: str = "now", max_results: int = 20) -> str:
    # Submit → poll → fetch results
    ...
```

Added to `config.py`:
```python
SPLUNK_HOST = "localhost"
SPLUNK_PORT = 8089
SPLUNK_USER = "admin"
SPLUNK_PASS = "sp@rkle69!"
```

`requests` and `urllib3` installed in venv:
```bash
source ~/BurrowMCP/venv/bin/activate
pip install requests urllib3
```

**Note:** `SPLUNK_PASS` is currently in `config.py` in plaintext. Move to env var before any public repo push. The `start_burrowmcp.sh` already exports `SPLUNK_PASS` — config.py should use `os.environ.get("SPLUNK_PASS")` instead.

---

### 4. Jynx13 SSH Key Distribution ✅

```bash
ssh-copy-id -i ~/.ssh/burrowmcp_ed25519.pub jbird13@100.108.182.39
ssh -i ~/.ssh/burrowmcp_ed25519 jbird13@100.108.182.39 "hostname && uptime"
# Output: jynx13 / 20:06  up 3 days, 20:50, 2 users, load averages: 4.39 5.08 3.94
```

Post-quantum SSH warnings on Jynx13 are cosmetic — OpenSSH flagging key exchange algorithm, not a real issue for a home lab.

---

### 5. `df` macOS Compatibility Fix

`df --output=source,size,used,avail,pcent,target` is GNU coreutils (Linux only). macOS `df` doesn't support `--output`. Fixed with a node-aware branch in `check_disk_space`:

```python
def check_disk_space(node_name: str) -> str:
    macos_nodes = {"EagleEye11", "Jynx13"}
    if node_name in macos_nodes:
        command = "df -h"
    else:
        command = "df -h --output=source,size,used,avail,pcent,target | head -20"
    result = run_ssh_command(node_name, command)
    log_tool_call("check_disk_space", node_name, result)
    return result
```

---

### 6. start_burrowmcp.sh Path Drama

**Root cause:** Session 5 introduced `start_burrowmcp.sh` as a new name (previously `start.sh`). The file was created at `/Volumes/Bird's Nest/BurrowMCP/start_burrowmcp.sh` but the Claude Desktop config was pointing to `/Users/EagleEye11/start_burrowmcp.sh` (non-existent). 

**Secondary issue:** The apostrophe in `Bird's Nest` caused zsh to fail when Claude Desktop passed the path as an argument (`/bin/zsh: can't open input file`). 

**Fix:** Copy script to home directory (no apostrophe in path), update config to `/Users/EagleEye11/start_burrowmcp.sh`.

```bash
cp "/Volumes/Bird's Nest/BurrowMCP/start_burrowmcp.sh" ~/start_burrowmcp.sh
```

`claude_desktop_config.json` BurrowMCP entry:
```json
"BurrowMCP": {
    "command": "/bin/zsh",
    "args": ["/Users/EagleEye11/start_burrowmcp.sh"]
}
```

**Lesson:** Avoid spaces and apostrophes in paths used by Claude Desktop MCP config. The Bird's Nest drive name will keep causing friction — consider symlinking critical scripts to `~/` as standard practice.

---

## Smoke Test Results

### Disk Space — All Nodes Clean ✅
| Node | Drive | Used | Total | % |
|------|-------|------|-------|---|
| EagleEye11 | Internal (Data) | 182G | 228G | **92% 🔴** |
| EagleEye11 | Bird's Nest | 298G | 699G | 43% ✅ |
| EagleEye11 | BrdBckp (TM) | 190G | 233G | 82% 🟡 |
| Krypton1t3 | /dev/sda3 | 78G | 232G | 34% ✅ |
| SkorpiOm | /dev/sda2 | 156G | 225G | **74% 🟡** |
| Jynx13 | Data | 51G | 113G | 54% ✅ |

⚠️ **EagleEye11 internal at 92%** — worth investigating. Heavy stuff (Splunk, models) lives on Bird's Nest which is healthy, but the internal drive needs a cleanup pass.

### Logging Pipeline ✅
`burrowmcp.log` confirmed writing on first post-fix tool call. Splunk monitor stanza in place — `sourcetype=burrowmcp` searchable in Splunk UI.

---

## Bugs Encountered & Fixed

| Bug | Cause | Fix |
|-----|-------|-----|
| BurrowMCP not connecting | Script path pointed to non-existent `~/start_burrowmcp.sh` | Copy script to `~/`, update config |
| zsh `can't open input file` | Apostrophe in `Bird's Nest` mangled by zsh | Script moved to apostrophe-free `~/` path |
| `ImportError: SPLUNK_HOST` | Splunk vars never added to `config.py` | Added all four SPLUNK_* vars |
| Logger not writing | `log_tool_call` import at bottom of file, never executed | Moved import to top of `ssh_tools.py` |
| `df` error on EagleEye11/Jynx13 | `--output` flag is Linux-only | macOS-aware branch using plain `df -h` |

---

## Parked for Session 6

1. **`get_wazuh_alerts()`** — Wazuh runs in Docker on Bird's Nest. Alert log is inside the container, not at `/var/ossec/logs/alerts/alerts.json` on the host. Need to identify container name and use `docker exec` to read it. Also need to generate some actual alerts first.
2. **Twingate/Tailscale coexistence** on Krypton1t3 — routing conflict when both run simultaneously. Research deferred to Session 6.
3. **EagleEye11 internal drive cleanup** — at 92%, worth a sweep before it becomes a problem.
4. **`SPLUNK_PASS` in config.py** — move to env var only, remove from config.py.

---

## Current File Structure
```
~/start_burrowmcp.sh           ← Claude Desktop entry point (apostrophe-free path)

/Volumes/Bird's Nest/BurrowMCP/
├── venv/
├── server.py                  # v0.4 — splunk_search + get_wazuh_alerts registered
├── config.py                  # SPLUNK_* vars added
├── start_burrowmcp.sh         # Copy also lives at ~/start_burrowmcp.sh
├── tools/
│   ├── __init__.py
│   ├── lab_status.py
│   ├── ssh_tools.py           # log_tool_call added to all tools; macOS df fix
│   ├── splunk_tools.py        # ← NEW
│   └── logger.py              # ← NEW
├── logs/
│   └── burrowmcp.log          # ← LIVE — writing telemetry ✅
└── docs/
    ├── BurrowMCP-00-Architecture.md
    ├── BurrowMCP-01-Session1.md
    ├── BurrowMCP-02-Session2.md
    ├── BurrowMCP-03-Session3.md
    ├── BurrowMCP-04-Session4.md
    └── BurrowMCP-05-Session5.md   ← this file
```

---

## Key Concepts Reinforced This Session

**Import order matters:** Python executes imports at parse time in order. An import buried at the bottom of a file after function definitions is legal Python, but if those functions reference the imported name, they'll fail at call time with `NameError`. Always put imports at the top.

**Apostrophes in shell paths are a trap:** When a path is passed as an argument through multiple layers (JSON config → Claude Desktop → zsh), special characters get mangled. The fix isn't clever escaping — it's eliminating the apostrophe from the execution path entirely.

**`df --output` is GNU only:** macOS ships BSD coreutils. Any tool targeting mixed Linux/macOS nodes needs OS-aware command branches for `df`, `stat`, `ls`, and others that differ between GNU and BSD implementations.

**Splunk binary location:** On a non-standard install (external drive), always `find` before assuming. `/Volumes/Bird's Nest/Applications/Splunk/bin/splunk` — not `splunk/bin/splunk`.

---

*"Four nodes. Live telemetry. The Burrow reports for duty — and now it keeps receipts."*  
— BurrowMCP Session 5, May 2026

---

**Tags:** `#BurrowMCP` `#MCP` `#ClaudeDesktop` `#EagleEye11` `#Krypton1t3` `#SkorpiOm` `#Jynx13` `#SSH` `#Session5` `#logging` `#telemetry` `#Splunk` `#splunk_search` `#splunk_tools` `#logger` `#check_disk_space` `#macOS` `#df` `#GNU` `#BSD` `#apostrophe` `#pathbug` `#homelab` `#FastMCP` `#Tailscale` `#Wazuh` `#Docker` `#debugging`
