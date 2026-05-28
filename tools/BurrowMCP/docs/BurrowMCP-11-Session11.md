# BurrowMCP — Session 11 Journal
**Date:** 2026-05-09
**Author:** JBird + Claude
**Status:** ✅ Complete — Splunk accessible from Jynx13 via SSH tunnel; pipeline gaps identified

---

## Session Goal
Get Splunk accessible through BurrowMCP on Jynx13 without opening any ports — maintaining the Burrow's zero-open-ports philosophy throughout.

---

## What We Accomplished

### 1. Confirmed Zero-Port Philosophy ✅
The existing BurrowMCP `splunk_search` tool was hitting `localhost:8089` (Splunk REST API) — broken from Jynx13 since Splunk lives on EagleEye11. Rather than opening port 8089, we pivoted to SSH-exec of the Splunk CLI, consistent with every other BurrowMCP tool.

**Architecture:**
```
Jynx13 BurrowMCP → SSH (Tailscale) → EagleEye11 → Splunk CLI → results
```

---

### 2. Located the Splunk Binary ✅
Splunk binary was not in the expected location. Found via `find`:

```
/Volumes/Bird's Nest/Applications/Splunk/bin/splunk
```

Confirmed working:
```bash
"/Volumes/Bird's Nest/Applications/Splunk/bin/splunk" version
# Splunk 10.2.1 (build c892b66d163d)
```

CLI search confirmed returning live data from `index=main`.

---

### 3. Rewrote `splunk_tools.py` ✅
Replaced the REST API implementation with SSH-exec of the Splunk CLI.

**Key changes:**
- Dropped `requests` library entirely
- Added `subprocess.run()` SSH call into EagleEye11
- Used `NODES["EagleEye11"]` from `config.py` for host/user
- Added stderr noise filter for known harmless Splunk CLI warnings (SSL cert, Bird's Nest path error in `openPortsEnhanced.sh`)
- Added `SPLUNK_USER` and `SPLUNK_PASS` to `config.py` on Jynx13

**File:** `/Users/jbird13/BurrowMCP/tools/splunk_tools.py`

---

### 4. Resolved SSH Auth to EagleEye11 ✅
Jynx13's BurrowMCP key (`~/.ssh/burrow_ed25519`) was not yet in EagleEye11's `authorized_keys`. Fixed:

```bash
ssh-copy-id -i ~/.ssh/burrow_ed25519.pub EagleEye11@100.113.239.38
```

---

### 5. Fixed Shell Quoting Bug ✅
The apostrophe in `Bird's Nest` conflicted with single-quoted shell args. Fixed by switching to double quotes throughout the `splunk_cmd` f-string in `splunk_tools.py`.

---

### 6. First Live Splunk Query from Jynx13 ✅
```
index=main | head 5
```
Returned live macOS system log events from EagleEye11. Zero ports opened.

---

### 7. Pipeline Audit via Splunk ✅
Queried available indexes:
```
| eventcount summarize=false index=* | table index
```

**Result:** Only three indexes exist — `history`, `main`, `summary`. **No `wazuh` index.**

- SkorpiOm forwarder data is landing in `index=main` as raw bash command history, not structured syslog or Wazuh JSON
- Wazuh alerts are **not** flowing into Splunk at all — pipeline was never wired up
- This is a significant gap for the SOC portfolio

---

### 8. EagleEye11 Drive Cleanup Confirmed ✅
JBird cleared ~20GB during the session. Live check via BurrowMCP:

| Volume | Used | Capacity |
|---|---|---|
| /dev/disk1s1 (Data) | 68Gi | 71% |
| /dev/disk1s5s1 (System) | 14Gi | 35% |

Down from 92% — healthy headroom restored.

---

## Known Issues / Partial Fixes

### `-earliest` / `-latest` Flags Invalid for CLI
The Splunk CLI `search` command does **not** accept `-earliest` or `-latest` flags — those are REST API parameters only. Time ranges must be embedded directly in the SPL:

```
index=main earliest=-24h | head 10   ✅
```

`splunk_tools.py` currently passes these as CLI flags — needs a fix in Session 12 to strip them from the `ssh_cmd` and embed them in the query string instead.

---

## Key Facts

| Item | Value |
|---|---|
| Splunk binary | `/Volumes/Bird's Nest/Applications/Splunk/bin/splunk` |
| Splunk version | 10.2.1 (build c892b66d163d) |
| EagleEye11 authorized key added | `~/.ssh/burrow_ed25519.pub` from Jynx13 |
| Splunk indexes found | `history`, `main`, `summary` |
| Wazuh → Splunk pipeline | ❌ Not wired up |
| EagleEye11 data volume | 71% (was 92%) |
| SkorpiOm | Asleep/unreachable at session end |

---

## Parked for Session 12

1. **Splunk license migration — DEADLINE MAY 17** ⚠️ CRITICAL
2. Fix `splunk_tools.py` — strip `-earliest`/`-latest` CLI flags, embed time range in SPL
3. Wire Wazuh → Splunk pipeline (create `wazuh` index, configure forwarder inputs)
4. Investigate SkorpiOm forwarder — what is it actually tailing? (`inputs.conf`)
5. **Krypton1t3 ↔ Jynx13 SSH key exchange** (username: `SuperSkorp_7`, Tailscale `100.103.171.45`)
6. **WatchYourLAN BurrowMCP tool** — do this immediately after #5. WatchYourLAN runs in a Docker container on Krypton1t3. Tool should SSH into Krypton1t3 as `SuperSkorp_7` and curl the WatchYourLAN API on localhost. No ports opened — pure SSH tunnel, same pattern as Splunk.
7. BurrowMCP as launchd service on EagleEye11 (auto-start on boot)
8. Named Cloudflare tunnel for permanent remote URL
9. APP_NAME_MAP expansion for BurrowVoice
10. Wazuh noise on Krypton1t3 — cause TBD

---

*"No ports. No mercy. Just SSH and a Splunk binary hiding in Bird's Nest."*
— BurrowMCP Session 11, May 2026

**Tags:** #BurrowMCP #Session11 #Splunk #SSHtunnel #splunk_tools #SplunkCLI #BirdsNest #Jynx13 #EagleEye11 #Tailscale #zeroOpenPorts #Wazuh #pipeline #homelab #SOC #midnightRun #Python313
