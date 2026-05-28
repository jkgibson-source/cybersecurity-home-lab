# BurrowMCP — Session 14 Journal
**Date:** 2026-05-09
**Author:** JBird + Claude
**Status:** ✅ Complete — Auto-boot, splunk_tools.py fix, Wazuh dashboard live

---

## ⚠️ CRITICAL DEADLINE — READ FIRST
**Splunk free license migration is due MAY 15, 2026.** Don't mention it again!

---

## Session Goals
1. Fix `splunk_tools.py` on EagleEye11 and Jynx13
2. BurrowMCP auto-start on EagleEye11 boot (launchd)
3. Set EagleEye11 to auto-login so launchd fires on reboot
4. Build Wazuh dashboard in Splunk

All four completed. ✅

---

## What We Accomplished

### 1. EagleEye11 Auto-Login ✅

FileVault was enabled on EagleEye11, blocking auto-login. Disabled via:

**System Settings → Privacy & Security → FileVault → Turn Off FileVault**

Decryption completed almost instantly (internal drive was lightly used). Auto-login then became available in:

**System Settings → Users & Groups → Automatically log in as → James Gibson**

---

### 2. BurrowMCP as launchd Service on EagleEye11 ✅

Created LaunchAgent plist at `~/Library/LaunchAgents/com.burrow.burrowmcp.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.burrow.burrowmcp</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>/Users/EagleEye11/start_burrowmcp.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Volumes/Bird's Nest/BurrowMCP/logs/burrowmcp.stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/Volumes/Bird's Nest/BurrowMCP/logs/burrowmcp.stderr.log</string>
</dict>
</plist>
```

```bash
mkdir -p "/Volumes/Bird's Nest/BurrowMCP/logs"
launchctl load ~/Library/LaunchAgents/com.burrow.burrowmcp.plist
launchctl list | grep burrow
# 32436   0   com.burrow.burrowmcp  ← PID confirmed, exit 0
```

BurrowMCP now starts automatically on every boot without manual intervention.

**Note:** stderr log (`burrowmcp.stderr.log`) not created = no errors on startup. Clean launch.

---

### 3. splunk_tools.py Fix — Jynx13 Only ✅

**The bug:** Jynx13's `splunk_tools.py` used the Splunk CLI over SSH and passed time range as `-earliest`/`-latest` flags, which Splunk CLI doesn't accept.

**The fix** — embed time range directly in the SPL query string:

```python
# Before (broken)
splunk_cmd = (
    f'"{SPLUNK_BIN}" search "{query}" '
    f'-earliest "{earliest}" -latest "{latest}" '
    f'-maxout {max_results} '
    f'-auth {SPLUNK_USER}:{SPLUNK_PASS}'
)

# After (fixed)
splunk_cmd = (
    f'"{SPLUNK_BIN}" search "{query} earliest={earliest} latest={latest}" '
    f'-maxout {max_results} '
    f'-auth {SPLUNK_USER}:{SPLUNK_PASS}'
)
```

**EagleEye11's version is a completely different implementation** — it uses the Splunk REST API (`requests.post` to `/services/search/jobs`) and passes time range as JSON body parameters (`earliest_time`, `latest_time`). No bug there, no fix needed.

| Machine | Implementation | Bug Present | Fixed |
|---|---|---|---|
| Jynx13 | SSH + Splunk CLI | ✅ Yes | ✅ Yes |
| EagleEye11 | REST API (requests) | ❌ No | N/A |

---

### 4. Wazuh Dashboard in Splunk ✅

Built a full 6-row Splunk dashboard ("Wazuh — Burrow Security Overview") from live `index=wazuh` data. Installed via Dashboard Source XML editor.

**Dashboard panels:**

| Row | Panels |
|---|---|
| 1 | Total Alerts, High Severity (≥7), Active Agents, Unique Rule Types |
| 2 | Alert Volume Over Time (stacked column), Alerts by Agent (pie) |
| 3 | Alerts by Severity Level (bar), Top 10 Rules Fired (table + heatmap) |
| 4 | Privilege Escalation Events (sudo), Screen Lock / Session Events |
| 5 | SCA Compliance Scores, Rootcheck Anomalies |
| 6 | Recent Alerts Feed (live, top 50) |

**Interactive filters:** Time Range picker + Agent dropdown (All / EagleEye11 / Jynx13 / SkorpiOm / wazuh.manager)

**Live stats at session close:**
- 394 total alerts
- 325 high severity (level ≥ 7)
- 4 active agents
- 19 unique rule types

**Fix applied during session:** `Active Agents` and `Unique Rule Types` KPI panels initially threw "Unknown search command 'dc'" — fixed by wrapping `dc()` properly in a `stats` command:
```
index=wazuh | stats dc(agent.name) as active_agents
index=wazuh | stats dc(rule.id) as unique_rules
```

**Notable findings visible in dashboard:**
- Top rule: Listened ports status (netstat) changed — 290 events, all level 7
- EagleEye11 SCA score: <30% (Unix hardening)
- Jynx13 SCA score: 49% (CIS macOS Monterey benchmark)
- Rule 19007 appearing: "SSH Hardening: Empty passwords should not be allowed" — worth investigating

---

## Key Facts

| Item | Value |
|---|---|
| LaunchAgent plist | `~/Library/LaunchAgents/com.burrow.burrowmcp.plist` |
| BurrowMCP logs dir | `/Volumes/Bird's Nest/BurrowMCP/logs/` |
| Jynx13 splunk_tools.py | Fixed — time range now embedded in SPL |
| EagleEye11 splunk_tools.py | REST API implementation, no fix needed |
| Wazuh dashboard | "Wazuh — Burrow Security Overview" in Splunk Web |
| Splunk index | `wazuh` |
| **License deadline** | **MAY 15, 2026 — migrate to free/community tier** |

---

## Parked for Session 15

1. **⚠️ Splunk license migration — DEADLINE MAY 15** — do this first, no exceptions
2. Investigate Rule 19007 — SSH empty password hardening on which agents?
3. Investigate EagleEye11 SCA score <30% — what checks are failing?
4. WatchYourLAN BurrowMCP tool (SSH into Krypton1t3 → curl localhost)
5. BurrowMCP Cloudflare tunnel + Claude Pro → SolSkorp_13 remote access
6. Reticulum setup on J-Parrot environment
7. APP_NAME_MAP expansion for BurrowVoice
8. Wazuh dashboard: add drilldown links on rule.id column

---

*"391 alerts, 4 agents, one dashboard, zero excuses. The Burrow sees everything now."*
— BurrowMCP Session 14, May 2026

**Tags:** #BurrowMCP #Session14 #Splunk #WazuhDashboard #launchd #AutoLogin #FileVault #splunk_tools #EagleEye11 #Jynx13 #SIEM #Wazuh #dashboard #SCA #hardening #LicenseDeadline #May15
