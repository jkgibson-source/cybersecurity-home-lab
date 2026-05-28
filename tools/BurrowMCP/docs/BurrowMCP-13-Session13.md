# BurrowMCP — Session 13 Journal
**Date:** 2026-05-09
**Author:** JBird + Claude
**Status:** ✅ Complete — Wazuh → Splunk pipeline fully operational

---

## Session Goal
Audit SkorpiOm's Splunk forwarder, assess data volume headroom, create a dedicated `wazuh` index, and wire Wazuh alerts into Splunk.

---

## What We Accomplished

### 1. SkorpiOm `inputs.conf` Audit ✅

Located at `/opt/splunkforwarder/etc/system/local/inputs.conf`. Four stanzas — all scan-result data, not continuous log streaming:

| Stanza | Sourcetype | Status |
|---|---|---|
| `splunk_ingest/openvas/` | `openvas_log` | Active |
| `splunk_ingest/` (whitelist: `nessus_mspl2\.json$`) | `nessus_json` | Active |
| `splunk_ingest/openvas_parsed.json` | `openvas_vulns` | Disabled |
| `splunk_ingest/openvas_events/` | `openvas_vulns` | Active |

All files dated April 15–17, static. Splunk fishbucket tracks position — no re-ingestion. SkorpiOm contributes near-zero volume on idle days. 500 MB/day budget is wide open for Wazuh.

---

### 2. Created `wazuh` Index in Splunk ✅

```bash
"/Volumes/Bird's Nest/Applications/Splunk/bin/splunk" add index wazuh -auth admin:<password>
```

Verified active in Splunk Web (Settings → Indexes). Now showing 17 total indexes.

---

### 3. Located Wazuh Docker Compose File ✅

Found at:
```
/Volumes/Bird's Nest/wazuh-docker/single-node/docker-compose.yml
```

Existing backup from prior session present (`docker-compose.yml.backup-before-restart-policy`).

---

### 4. Diagnosed Log Accessibility Problem ✅

`docker inspect` revealed `wazuh_logs` was a **named Docker volume** (not a bind mount):
```
Source: /var/lib/docker/volumes/single-node-wazuh_logs/_data
Destination: /var/ossec/logs
```

On macOS with Docker Desktop, named volume data lives inside the Docker VM — inaccessible from the host filesystem directly. `alerts.json` confirmed present inside the container at `/var/ossec/logs/alerts/alerts.json` but unreachable from Splunk on the host.

---

### 5. Added Bind Mount to Compose File ✅

Created host directory:
```bash
mkdir -p "/Volumes/Bird's Nest/wazuh-logs"
```

Backed up compose file:
```bash
cp docker-compose.yml docker-compose.yml.backup-before-wazuh-splunk
```

Edited `docker-compose.yml` — two changes in `wazuh.manager` service:

**Before:**
```yaml
volumes:
  - wazuh_logs:/var/ossec/logs
...
volumes:
  wazuh_logs:
```

**After:**
```yaml
volumes:
  - /Volumes/Bird's Nest/wazuh-logs:/var/ossec/logs
...
volumes:
  # wazuh_logs:
```

Restarted manager only (indexer and dashboard left running):
```bash
cd "/Volumes/Bird's Nest/wazuh-docker/single-node/"
docker compose down wazuh.manager
docker compose up -d wazuh.manager
```

Verified bind mount worked:
```bash
ls "/Volumes/Bird's Nest/wazuh-logs/alerts/"
# 2026  alerts.json  alerts.log
```

---

### 6. Wired Splunk Forwarder to Monitor Alerts ✅

Appended to `/Volumes/Bird's Nest/Applications/Splunk/etc/system/local/inputs.conf`:

```ini
[monitor:///Volumes/Bird's Nest/wazuh-logs/alerts/alerts.json]
index = wazuh
sourcetype = wazuh_alerts
disabled = false
```

Restarted Splunk:
```bash
"/Volumes/Bird's Nest/Applications/Splunk/bin/splunk" restart
```

---

### 7. Pipeline Verified in Splunk Web ✅

Search confirmed live data flowing:
```
index=wazuh earliest=-5m
```

**346 events** on initial backfill. Steady-state breakdown (4 rule types):

| Rule | Count |
|---|---|
| Host-based anomaly detection (rootcheck) | 6 |
| Listened ports status (netstat) changed | 2 |
| SCA summary: Unix audit <30% | 1 |
| Screen locked with userID:501 | 1 |

Splunk auto-extracted all Wazuh JSON fields including `agent.name`, `agent.ip`, `rule.level`, `rule.description`, `rule.groups[]`, `rule.gdpr[]`, `rule.hipaa[]`, `rule.nist_800_53[]`, `rule.pci_dss[]`, `rule.tsc[]`.

---

### 8. SCA Audit Score Check ✅

```
index=wazuh rule.description="SCA summary*" | table agent.name agent.ip rule.description
```

| Agent | IP | Finding |
|---|---|---|
| EagleEye11.local | 127.0.0.1 | Unix hardening: **<30%** |
| jynx13 | 100.108.182.39 | CIS macOS Monterey benchmark: **49%** |

Not urgent — EagleEye11 is a lab SIEM hub, Jynx13 is a travel/commander node. Worth revisiting as a hardening exercise.

---

## Key Facts

| Item | Value |
|---|---|
| Wazuh alerts host path | `/Volumes/Bird's Nest/wazuh-logs/alerts/alerts.json` |
| Splunk index | `wazuh` |
| Splunk sourcetype | `wazuh_alerts` |
| Compose file | `/Volumes/Bird's Nest/wazuh-docker/single-node/docker-compose.yml` |
| Compose backup | `docker-compose.yml.backup-before-wazuh-splunk` |
| Splunk binary | `/Volumes/Bird's Nest/Applications/Splunk/bin/splunk` |
| Splunk license deadline | May 17 — migrate to free/community tier |

---

## Parked for Session 14

1. **Splunk license migration — DEADLINE MAY 17** ⚠️ CRITICAL
2. Fix `splunk_tools.py` — strip `-earliest`/`-latest` CLI flags, embed time range in SPL
3. Build Wazuh dashboard panel in Splunk (alert level trends, top agents, top rules)
4. Investigate EagleEye11 SCA hardening score <30% — what's failing?
5. WatchYourLAN — revisit after NY trip; consider ethernet scenario on Krypton1t3
6. WatchYourLAN BurrowMCP tool — build once service is stable
7. BurrowMCP as launchd service on EagleEye11 (auto-start on boot)
8. Named Cloudflare tunnel for permanent remote URL
9. APP_NAME_MAP expansion for BurrowVoice
10. Reticulum setup on J-Parrot environment

---

*"Named volumes: great for Docker, terrible for Splunk. One bind mount and suddenly everything talks."*
— BurrowMCP Session 13, May 2026

**Tags:** #BurrowMCP #Session13 #Splunk #Wazuh #WazuhToSplunk #SplunkIndex #BindMount #Docker #DockerCompose #inputs.conf #wazuh_alerts #SIEM #pipeline #EagleEye11 #homelab #SCA #hardening #fieldextraction
