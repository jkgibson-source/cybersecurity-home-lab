# Burrow Journal — Session 20
**Date:** 2026-05-12
**Node:** Jynx13 (commander)
**Tags:** #BurrowMCP #Jynx13 #migration #SSH #burrowuser #Krypton1t3 #bugfix #Splunk #ClaudeCode #config

> **Sessions 15–19 note:** These sessions were spent working out BurrowMCP as a connector for SolSkorp_13 (iPhone 13 mobile node). Details documented separately.

---

## Summary

Short but productive session. Primary focus: diagnosing and resolving the Jynx13 BurrowMCP SSH failure for Krypton1t3, and confirming Splunk's license migration to the free tier.

---

## Systems Check

All four core nodes online at session start:

| Node | Status | Uptime |
|---|---|---|
| EagleEye11 | ✅ Online | 4 days, 1h |
| Krypton1t3 | ✅ Online | SSH auth failing via BurrowMCP |
| SkorpiOm | ✅ Online | ~1 day, 21h |
| Jynx13 | ✅ Local | Commander node |

**SkorpiOm** had `networking.service` in failed state — likely cosmetic (NetworkManager conflict on Kali), networking functional.

---

## Splunk License Migration — Confirmed

Queried `_internal` rollover summary via BurrowMCP Splunk tool. Results:

- **May 12** rollover: `licenseGroup=Free`, `productType=splunk` — **free tier active**
- May 11 and prior: still showing Trial/Enterprise entries

Migration landed cleanly. Daily cap is 500MB. Some trial-era days were pushing 500–835MB so ingest volume worth monitoring going forward.

---

## BurrowMCP Jynx13 Migration Bug — Diagnosed and Fixed

### The Problem
BurrowMCP was migrated from EagleEye11 to Jynx13 but carried over several EagleEye11-specific artifacts. The primary failure: SSH connections to Krypton1t3 were being made as `SuperSkorp_7` (the node's `ssh_user` reference value) instead of `burrowuser` (the dedicated BurrowMCP service account).

### Diagnosis Path
1. Confirmed `burrowuser` account exists on Krypton1t3 (uid=956, shell `/bin/bash`)
2. Confirmed `authorized_keys` populated and correct
3. Manual `ssh -vvv` from Jynx13 → Krypton1t3 as `burrowuser` **succeeded cleanly**
4. SELinux ruled out
5. Grep of BurrowMCP source revealed SSH command built with `node["ssh_user"]` instead of hardcoded `"burrowuser"`
6. Secondary artifact: `BURROWMCP_BASE` still pointed to `"/Volumes/Bird's Nest/BurrowMCP"` (EagleEye11 path) — corrected to `"/Users/jbird13/BurrowMCP"`

### Fix
- Handed off to **Claude Code** with a scoped brief (`BurrowMCP-Jynx13-Handoff.md`)
- Claude Code audited codebase and corrected SSH invocation to use `burrowuser` throughout
- Config versioned: **0.1.2 — 2026-05-12**
  - 0.1.1 would have been the initial migration patch (retroactively noted)
  - 0.1.2 is this fix
- Restarted Jynx13 BurrowMCP (via Claude for Mac Login Item)

### Verification
Post-fix, all three remote nodes responding cleanly through Jynx13:

```
Krypton1t3 | 15:11:50 up 1 day, 3:28, 2 users, load average: 0.07, 0.13, 0.11
SkorpiOm   | 15:11:55 up 1 day, 22:45, 2 users, load average: 1.63, 1.10, 0.97
EagleEye11 | 15:11 up 4 days, 3:01, 5 users, load averages: 5.08 4.45 4.11
```

Jynx13 is fully operational as BurrowMCP commander node. ✅

---

## Key Lessons

- **Always version patch increments at migration time.** The initial Jynx13 migration should have been 0.1.1 — by the time we caught it we were already on 0.1.2.
- **`ssh_user` in the NODES dict is reference-only.** All BurrowMCP SSH connections use `burrowuser` + `burrow_ed25519` regardless of node.
- **Restart the app.** Twice today the fix was in but BurrowMCP wasn't reloaded. Old habits.
- **Claude Code is worth the $20.** Scoped brief + clear bug description = fast resolution.

---

## Parked / Next Session

- EagleEye11 load averages elevated (~5.0) — monitor; may want to audit what's running
- SkorpiOm `networking.service` failed state — verify cosmetic or investigate
- Session 12 TODO still parked: Krypton1t3 ↔ Jynx13 SSH key exchange (SuperSkorp_7) + WatchYourLAN BurrowMCP tool
- Telegram integration on Hermes (Krypton1t3) still pending
- Cloudflare tunnel / `theburrow.dev` remote access — mid-June Palm Beach Gardens deadline
