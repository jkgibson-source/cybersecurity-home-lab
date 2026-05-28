# BurrowMCP — Session 8 Journal
**Date:** 2026-05-06
**Author:** JBird + Claude
**Status:** ✅ Complete — BurrowVoice fully operational across all nodes

---

## Session Goal
Investigate the Twingate zombie hydra on Krypton1t3, confirm SSH key distribution
across all nodes, and fix BurrowVoice app launching for Jynx13 and Krypton1t3.

---

## What We Accomplished

### 1. Twingate Zombie Hydra — Confirmed & Neutralized ✅
Diagnosed the root cause of the Krypton1t3 crash-loop alerts from Session 7.
`systemctl cat twingate.service` revealed:
```
Restart=always
RestartSec=2s
RestartPreventExitStatus=125
```
Twingate was exiting with status 125 (initialization failure — couldn't reach
its auth endpoint because Tailscale had claimed the routing table), and systemd
was reviving it every ~2 seconds. That's the Level 5 alert storm BurrowMCP
caught in real time during Session 7.

`reset-failed` cleared the ghost:
```bash
sudo systemctl reset-failed twingate.service
```
Final state: `inactive (dead)`. Tailscale owns the mesh. Twingate = break-glass
emergency backup, manually started only when needed.

**Bonus discovery:** SolSkorp_13 (iPhone 13) Tailscale IP documented for the
first time: `100.95.11.33` — spotted in Krypton1t3's login history.

---

### 2. SSH Key Distribution — All Nodes Confirmed ✅
| Node | Status | Notes |
|---|---|---|
| Krypton1t3 | ✅ | Done in Session 4 |
| SkorpiOm | ✅ | Already done (pre-existing) |
| Jynx13 | ✅ | Confirmed tonight via passwordless SSH test |
| EagleEye11 | n/a | Hub node |

Jynx13 key copy completed with:
```bash
ssh-copy-id jbird13@100.108.182.39
```
Verified with a live passwordless SSH session. Post-quantum warning noted
(cosmetic only — Jynx13's OpenSSH flagging algorithm preferences).

---

### 3. BurrowVoice — Cross-Platform App Launching Fixed ✅
This was the main event. Three separate problems, three separate fixes.

#### Problem A: All remote nodes using macOS `open -a` syntax
Original code sent `open -a AppName` to every remote target regardless of OS.
Linux nodes have no `open` command — hence the SkorpiOm error popups.

**Fix:** Platform detection via `uname` before launching:
```python
platform_check = _run_remote(ssh_target, "uname")
if "Darwin" in platform_check:
    # macOS branch
else:
    # Linux branch
```

#### Problem B: Jynx13 (macOS) — apps launching in SSH void
`launchctl asuser $(id -u) open -a` requires root to switch GUI sessions.
SSH connection runs as unprivileged user → `Operation not permitted`.

**Fix:** `osascript` — AppleScript respects the logged-in GUI session over SSH,
no sudo required:
```python
f"osascript -e 'tell application \"{resolved}\" to activate'"
```
First voice command to open Terminal on Jynx13: ✅ appeared on screen.

#### Problem C: Krypton1t3 (Fedora) — apps silently ghosting
Required setting both DISPLAY and DBus session address explicitly.
SSH sessions don't inherit desktop environment variables.

Diagnostic findings on Krypton1t3:
- `$DISPLAY` → empty in SSH session
- `who` → desktop session on `:0` (seat0, running since May 4)
- DBus socket → `unix:path=/run/user/1000/bus`
- `xdpyinfo` → X server accepting connections fine (no auth wall)
- Root cause → `brave` binary not in PATH; actual binary is `brave-browser`

**Fix:** Explicit environment + direct binary call:
```python
f"DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus {shlex.quote(resolved)} & disown 2>/dev/null && echo launched"
```

#### Problem D: Binary name mismatches across platforms
`brave` → not found. `firefox` → worked. Confirmed need for name map.

**Fix:** `APP_NAME_MAP` dictionary added to dispatch.py:
```python
APP_NAME_MAP = {
    "terminal":  {"darwin": "Terminal",        "linux": "xfce4-terminal"},
    "brave":     {"darwin": "Brave Browser",   "linux": "brave-browser"},
    "firefox":   {"darwin": "Firefox",         "linux": "firefox"},
    "messages":  {"darwin": "Messages",        "linux": None},
    "calendar":  {"darwin": "Calendar",        "linux": None},
    "files":     {"darwin": "Finder",          "linux": "thunar"},
    "burpsuite": {"darwin": None,              "linux": "burpsuite"},
}
```
Resolution logic inserted between `uname` check and platform branch:
```python
app_key = app.lower()
platform = "darwin" if "Darwin" in platform_check else "linux"
resolved = APP_NAME_MAP.get(app_key, {}).get(platform, app_key)
if resolved is None:
    return f"[error] {app} is not available on {target}"
```

---

## BurrowVoice Final Status
| Node | OS | SSH Auth | App Launch Method | Status |
|---|---|---|---|---|
| EagleEye11 | macOS M1 | local | `open -a` | ✅ |
| Krypton1t3 | Fedora 44 | ✅ key | binary + DISPLAY + DBus | ✅ |
| Jynx13 | macOS Monterey | ✅ key | `osascript` | ✅ |
| SkorpiOm | Kali Linux | ✅ key | binary + DISPLAY + DBus | ✅ |

---

## MACHINES Dict Fix
Krypton1t3 had wrong SSH username. Corrected in dispatch.py:
```python
# Before
"krypton1t3": "krypton@100.103.171.45",
# After
"krypton1t3": "SuperSkorp_7@100.103.171.45",
```

---

## Newly Documented
| Item | Value |
|---|---|
| SolSkorp_13 Tailscale IP | `100.95.11.33` |
| Krypton1t3 Brave binary | `/usr/bin/brave-browser` (also `brave-browser-stable`) |
| Krypton1t3 desktop display | `:0` (seat0) |
| Krypton1t3 DBus socket | `unix:path=/run/user/1000/bus` |

---

## Parked for Session 9
1. Splunk license migration — **deadline May 17, 2026** ⚠️
2. EagleEye11 internal drive cleanup (at 92%)
3. Wazuh noise on Krypton1t3 — still firing, cause TBD
4. APP_NAME_MAP expansion (more apps as needed)
5. SkorpiOm app launch testing (Firefox confirmed ✅, others TBD)
6. Docker Desktop MCP Toolkit exploration
7. BurrowVoice → BurrowMCP integration path
8. Wazuh manager upgrade (deferred to end of year)

---

*"Voice command received. Brave opens on Krypton1t3. The Burrow speaks, and
the machines listen."*
— BurrowMCP Session 8, May 2026

**Tags:** #BurrowMCP #Session8 #BurrowVoice #SSH #keyAuth #appLaunch
#osascript #Jynx13 #Krypton1t3 #SkorpiOm #crossPlatform #DISPLAY #DBus
#AppNameMap #Twingate #zombieHydra #resetFailed #SolSkorp13 #Tailscale
#homelab #SOC #voiceControl
