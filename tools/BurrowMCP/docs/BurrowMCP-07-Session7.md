# BurrowMCP — Session 7 Journal
**Date:** 2026-05-05
**Author:** JBird + Claude
**Status:** ✅ Complete — All 4 Wazuh agents active, Twingate/Tailscale conflict resolved

## Session Goal
Reconnect disconnected Wazuh agents on Krypton1t3 and SkorpiOm, install a
fresh Wazuh agent on EagleEye11 (the manager's own host), and resolve the
Twingate/Tailscale routing conflict on Krypton1t3.

---

## What We Accomplished

### 1. Wazuh Agent Version Mismatch Diagnosed ✅
Krypton1t3 had auto-updated to Wazuh agent v4.14.5, but the manager container
is pinned at v4.9.0. Wazuh enforces: agent version must be ≤ manager version.
Decision: downgrade agents to 4.9.0. Manager upgrade deferred to end of year.

### 2. Root Cause #2: Manager IP Was LAN, Not Tailscale ✅
ossec.conf still pointed to 10.0.0.112, but EagleEye11 had been on Tailscale
for several days and the LAN route wasn't resolving. All agents now point to
Tailscale IP 100.113.239.38 (except EagleEye11 itself → 127.0.0.1).

### 3. Krypton1t3 — Agent Downgraded to 4.9.0 ✅
```bash
sudo systemctl stop wazuh-agent
sudo rpm -e wazuh-agent
curl -O https://packages.wazuh.com/4.x/yum/wazuh-agent-4.9.0-1.x86_64.rpm
sudo WAZUH_MANAGER="100.113.239.38" rpm -ivh wazuh-agent-4.9.0-1.x86_64.rpm
sudo systemctl enable wazuh-agent && sudo systemctl start wazuh-agent
```

### 4. SkorpiOm — Already v4.9.0, Needed IP Fix + Zombie Kill ✅
Version check: sudo /var/ossec/bin/wazuh-control info → WAZUH_VERSION="v4.9.0"
No reinstall. Updated ossec.conf, then killed zombie processes before restart:
```bash
sudo pkill -f wazuh && sleep 3 && sudo systemctl start wazuh-agent
```

### 5. EagleEye11 — Fresh macOS Agent Install ✅
```bash
curl -O https://packages.wazuh.com/4.x/macos/wazuh-agent-4.9.0-1.arm64.pkg
sudo WAZUH_MANAGER="127.0.0.1" installer -pkg wazuh-agent-4.9.0-1.arm64.pkg -target /
# WAZUH_MANAGER env var didn't write to config — manual fix required:
sudo nano /Library/Ossec/etc/ossec.conf  # set <address>127.0.0.1</address>
sudo /Library/Ossec/bin/wazuh-control restart
```
macOS paths: /Library/Ossec/etc/, /Library/Ossec/logs/, /Library/Ossec/bin/

### 6. Final State: Active (4) — Disconnected (0) ✅
| Agent      | OS                    | Status    |
|------------|-----------------------|-----------|
| EagleEye11 | macOS M1              | ✅ Active |
| Krypton1t3 | Fedora Security Lab 44| ✅ Active |
| SkorpiOm   | Kali Linux            | ✅ Active |
| Jynx13     | macOS Monterey        | ✅ Active |

### 7. Twingate/Tailscale Conflict Resolved on Krypton1t3 ✅
BurrowMCP's get_wazuh_alerts() caught a crash-loop in real time — Level 5
systemd failure alerts every ~6 seconds. Root cause: Twingate auto-restarting
and fighting Tailscale's routing table.
```bash
sudo systemctl disable twingate && sudo systemctl stop twingate
# Emergency re-enable: sudo systemctl start twingate
```
Philosophy: Tailscale owns the mesh. Twingate = break-glass emergency backup.

---

## Splunk License Note
Expires May 17, 2026. Migration to free tier planned, not urgent yet.

---

## Parked for Session 8
1. Splunk license migration (May 17 deadline)
2. EagleEye11 internal drive cleanup — at 92%, ~1.25GB recoverable
3. Docker Desktop MCP Toolkit (beta) — explore
4. BurrowVoice → BurrowMCP integration path
5. Wazuh manager upgrade — deferred to end of year / post-NY trip

---

## Wazuh Agent Quick Reference
| Node       | Manager Address  | Path Prefix      | Start Command              |
|------------|-----------------|------------------|----------------------------|
| EagleEye11 | 127.0.0.1       | /Library/Ossec/  | wazuh-control restart      |
| Krypton1t3 | 100.113.239.38  | /var/ossec/      | systemctl restart wazuh-agent |
| SkorpiOm   | 100.113.239.38  | /var/ossec/      | systemctl restart wazuh-agent |
| Jynx13     | 100.113.239.38  | /var/ossec/      | wazuh-control restart      |

---
*"Active four. Disconnected zero. The Burrow has eyes on everything."*
— BurrowMCP Session 7, May 2026

**Tags:** #BurrowMCP #Session7 #Wazuh #WazuhAgent #v4.9.0 #versionMismatch
#Krypton1t3 #SkorpiOm #EagleEye11 #Jynx13 #Tailscale #Twingate
#routingConflict #zombieProcess #macOSagent #RPMdowngrade #homelab #SOC #SIEM