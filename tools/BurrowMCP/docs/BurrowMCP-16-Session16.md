# BurrowMCP Session 16 Journal
**Date:** Sunday, May 10, 2026
**Node:** Jynx13 (commander)
**Operator:** JBird

---

## Session Overview

First session operating BurrowMCP exclusively from Jynx13 as a commander node. Focus was on validating Jynx13's BurrowMCP instance, fixing Splunk query issues, investigating Wazuh alerts, and hardening SkorpiOm's remote access capabilities for unattended operation.

---

## 1. Jynx13 BurrowMCP — Self-Reporting Fix

**Problem:** Jynx13 was showing as `❌ OFFLINE` in her own lab status checks.

**Cause:** `config.py` had `"is_local": False` for the Jynx13 node entry. Since Jynx13 runs her own BurrowMCP instance and is the one performing the pings, she can't ping herself — she needs to self-report as LOCAL.

**Fix:** Edited `config.py` on Jynx13:
```python
"Jynx13": {
    "tailscale_ip": "100.108.182.39",
    "tailscale_name": "jynx13",
    "os": "macOS Monterey",
    "ssh_user": "jbird13",
    "role": "OSINT / general",
    "is_local": True,   # Changed from False
},
```

**Result:** Jynx13 now correctly shows as `✅ LOCAL` in her own status checks. EagleEye11 shows as `✅ ONLINE` (not LOCAL) from Jynx13's perspective — expected behavior.

---

## 2. Splunk Tool Fix — `splunk_tools.py`

**Problem:** All Splunk queries from Jynx13 were returning:
```
ERROR: FATAL: Error in 'head' command: Invalid argument: 'earliest=-24h'
```

**Cause:** The `earliest` and `latest` time parameters were being interpolated **inside** the quoted query string in the Splunk CLI command f-string:
```python
f'"{SPLUNK_BIN}" search "{query} earliest={earliest} latest={latest}"'
```
Splunk CLI treats them as part of the search text, not as CLI flags.

**Fix:** Moved time parameters **outside** the quoted query:
```python
splunk_cmd = (
    f'"{SPLUNK_BIN}" search "{query}" '
    f'earliest={earliest} latest={latest} '
    f'-maxout {max_results} '
    f'-auth {SPLUNK_USER}:{SPLUNK_PASS}'
)
```

**Additional fix:** Increased `subprocess.run()` timeout from `60` to `120` seconds to accommodate SSH round-trip latency for heavier queries.

**Result:** Splunk queries now working from Jynx13. Keep time windows to `-1h` or shorter for best performance over Tailscale SSH.

---

## 3. Wazuh Alerts Investigation

**Wazuh index confirmed healthy:** 3,345 events in the last hour, all flowing from `Bird's Nest/wazuh-logs/alerts/alerts.json` on EagleEye11.

### Alert breakdown (last 1 hour):
| Level | Count | Meaning |
|-------|-------|---------|
| 7 | 3,176 | Notable / informational |
| 3 | 159 | Low |
| 5 | 9 | Moderate |
| 9 | 3 | High — investigated |

### Top alert types:
- **Integrity checksum changed** — 2,624 (FIM, normal for active lab)
- **Listened ports changed** — 474 (BurrowMCP/SSH activity)
- **Successful sudo to ROOT** — 33
- **Screen locked/unlocked** — 23 each

### Level 9 Alerts (from yesterday, May 9):
1. **EagleEye11 (x2):** SCA Unix audit score below 30% — expected for unhardened lab machine
2. **Jynx13:** CIS macOS 12 Monterey Benchmark — "Ensure Appropriate Permissions Are Enabled for System Wide Applications" changed from **passed → failed**

### Root cause of Jynx13 Level 9:
Port storm at 17:45 EDT coincided exactly with initial BurrowMCP startup on Jynx13. Three app bundles had world-writable (`777`) permissions:
- `Bing Wallpaper.app`
- `Firefox.app`
- `Microsoft Bing for Safari.app`

**Fix:**
```bash
sudo chmod 755 /Applications/Bing\ Wallpaper.app
sudo chmod 755 /Applications/Firefox.app
sudo chmod 755 /Applications/"Microsoft Bing for Safari.app"
```

`/Applications` itself shows `drwxrwxr-x` (775) — macOS SIP blocks `chmod 755` on this directory even with sudo. This is intentional Apple behavior; the admin group write access is by design. Noted as known exception — not a real security concern in lab context.

---

## 4. BurrowMCP — `x0vncserver` Added to ALLOWED_SERVICES

Added `"x0vncserver"` to `ALLOWED_SERVICES` in `config.py` on Jynx13 so BurrowMCP can check and restart the TigerVNC service remotely:

```python
ALLOWED_SERVICES = [
    "wazuh-agent",
    "splunk",
    "ollama",
    "syncthing",
    "docker",
    "hermes-agent",
    "x0vncserver",   # Added Session 16
]
```

---

## 5. SkorpiOm — Auto-Login & Remote Access Hardening

### Problem
If SkorpiOm reboots while JBird is away, the machine sits at a login screen. No desktop = no remote desktop tools. Only SSH would work.

### Auto-Login Fix (LightDM)
Edited `/etc/lightdm/lightdm.conf`, uncommented and set in `[Seat:*]` section:
```ini
[Seat:*]
autologin-user=solskorp_11
autologin-user-timeout=0
```
**Result:** SkorpiOm now boots directly to desktop as `solskorp_11`. ✅

### x0vncserver (TigerVNC) — Auto-Start Attempts
Extensive troubleshooting to get x0vncserver to survive reboots:

1. Added `DISPLAY` and `XAUTHORITY` env vars to system service — helped manually but not on boot
2. Converted to user systemd service (`~/.config/systemd/user/x0vncserver.service`)
3. Added `-forever` flag to `ExecStart`
4. Enabled lingering: `sudo loginctl enable-linger solskorp_11`
5. Service file location: `/home/solskorp_11/.config/systemd/user/x0vncserver.service`

**Final service file:**
```ini
[Unit]
Description=TigerVNC x0vncserver - Live Desktop Share
After=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/bin/x0vncserver -display :0 -passwordfile /home/solskorp_11/.config/tigervnc/passwd -localhost no -forever
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical-session.target
```

**Outcome:** x0vncserver still not surviving reboots reliably. Decision made to **leave it** — can be started manually via SSH if needed. Not worth additional troubleshooting time.

**Note:** Old system service (`/etc/systemd/system/x0vncserver.service`) is now `disabled` and `inactive (dead)` — correct state.

### Remote Access Summary for SkorpiOm (post-reboot):
| Tool | Status | Notes |
|------|--------|-------|
| RustDesk | ✅ Auto-starts on boot | Primary remote desktop |
| SSH | ✅ Always available | Can start VNC manually if needed |
| x0vncserver | ⚠️ Manual start only | `systemctl --user start x0vncserver` |
| Remmina | ℹ️ J-Parrot only | Client-side, needs VNC running on target |

---

## 6. Krypton1t3 — Pending

Auto-login on Fedora (GDM) not yet configured — carry over to Session 17.

---

## Pending / Next Session
- [ ] Configure auto-login on Krypton1t3 (Fedora/GDM)
- [ ] Splunk free license migration (due ~May 17)
- [ ] WatchYourLAN BurrowMCP tool (SSH into Krypton1t3 → curl localhost)

---

## Tags
`#burrowmcp` `#jynx13` `#skorpiom` `#splunk` `#wazuh` `#tigervnc` `#autologin` `#lightdm` `#remote-access` `#rustdesk` `#config` `#session16` `#mempalace`
