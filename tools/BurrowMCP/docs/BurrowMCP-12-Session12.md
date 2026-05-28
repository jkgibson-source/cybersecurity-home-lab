# BurrowMCP — Session 12 Journal
**Date:** 2026-05-09  
**Author:** JBird + Claude  
**Status:** ✅ Complete — Jynx13 ↔ Krypton1t3 SSH established; WatchYourLAN tuned and parked

---

## Session Goal
Complete the Jynx13 ↔ Krypton1t3 SSH key exchange and build the WatchYourLAN BurrowMCP tool. Secondary: tune WatchYourLAN to stop dropping Tailscale.

---

## What We Accomplished

### 1. SSH Key Audit on Jynx13 ✅
Ran `ls -la ~/.ssh/` on Jynx13. Found three keypairs:
- `burrow_ed25519` — BurrowMCP key (used for EagleEye11 last session)
- `id_ed25519` — labeled `jynx13-to-eagleeye11`, dedicated to EagleEye11
- No existing Krypton1t3 key — the orphaned `jynx13@burrow` entry in Krypton1t3's `authorized_keys` was from a prior incomplete attempt with a lost private key

No `~/.ssh/config` existed on Jynx13.

---

### 2. Generated New Keypair for Krypton1t3 ✅
```bash
ssh-keygen -t ed25519 -f ~/.ssh/jynx13_to_krypton -C "jynx13-to-krypton1t3"
```

`ssh-copy-id` failed — Krypton1t3's sshd rejects password auth entirely (Fedora Security Lab default). Key was already present in `authorized_keys` from a previous attempt but the private key was gone.

---

### 3. Diagnosed SSH Failure — Wrong Key Specified ✅
Direct `ssh SuperSkorp_7@100.103.171.45` was failing because SSH defaulted to the wrong key. Fix was explicit key flag:

```bash
ssh -i ~/.ssh/jynx13_to_krypton SuperSkorp_7@100.103.171.45
```

Connected immediately. Last login confirmed from `100.108.182.39` (Jynx13's Tailscale IP).

---

### 4. Created SSH Config on Jynx13 ✅
```bash
cat >> ~/.ssh/config << 'EOF'
Host krypton1t3
    HostName 100.103.171.45
    User SuperSkorp_7
    IdentityFile ~/.ssh/jynx13_to_krypton
EOF
chmod 600 ~/.ssh/config
```

Verified:
```bash
ssh krypton1t3
# Connected — no password, no -i flag needed
```

---

### 5. Cleaned Up Krypton1t3 `authorized_keys` ✅
Audited all entries via:
```bash
grep -o '[^ ]*$' ~/.ssh/authorized_keys
```

Found entries:
| Comment | Status |
|---|---|
| `skorpiom@burrow` | ✅ Keep |
| `eagleeye11@burrow` | ✅ Keep |
| `parrot@jynx13-burrow` | ✅ Keep |
| `Termius` (×3) | ⚠️ Two duplicates removed, one kept (SolSkorp_13 iPhone access) |
| `burrowmcp@eagleeye11` (×2) | ⚠️ One duplicate removed |
| `jynx13@burrow` | 🗑️ Orphan — removed |
| `jynx13-to-krypton1t3` | ✅ Keep (new) |

Final clean count: 6 entries.

---

### 6. WatchYourLAN — Tuning Attempt ⏸️ Parked

#### Problem
WatchYourLAN was dropping Tailscale connectivity on Krypton1t3 every ~5 minutes. Root cause: `TIMEOUT=120` (2-minute ARP scan interval) flooding `wlp2s0` — a WiFi interface already running near capacity with Tailscale keepalives and SSH sessions.

#### Tuning Steps Taken
1. Changed `TIMEOUT: 120` → `TIMEOUT: 600` in `~/docker/watchyourlan/docker-compose.yml`
2. Discovered `docker compose` and `docker-compose` both unavailable on Krypton1t3 — used `docker run` directly
3. Hit SELinux volume mount permission errors — fixed with `:z` label:

```bash
docker run -d \
  --name watchyourlan \
  --network host \
  --restart always \
  -e TZ=America/New_York \
  -e IFACES=wlp2s0 \
  -e PORT=8840 \
  -e COLOR=dark \
  -e TIMEOUT=600 \
  -e TRIM_HIST=168 \
  -v ~/docker/watchyourlan/wyl:/data/WatchYourLAN:z \
  aceberg/watchyourlan:latest
```

WatchYourLAN came up clean — SQLite connected, 7 devices found on first scan.

#### Verdict
Even at 600s interval, Tailscale drops continued. The `wlp2s0` WiFi driver on Krypton1t3 can't handle ARP burst traffic on top of active connections. No scan intensity throttle available within WatchYourLAN itself.

**Options considered:**
- Ethernet tether via phone hotspot — wrong network, not useful for home LAN inventory
- Move to SkorpiOm — architecturally wrong (attack node shouldn't run monitoring services)
- Stop and sleep on it ✅

#### Current State
Container stopped and set to no auto-restart:
```bash
docker stop watchyourlan
docker update --restart=no watchyourlan
```

Config, compose file, and `wyl` data volume preserved. SELinux fix and 600s timeout already in place — ready to resume when back from NY or when ethernet becomes available.

---

### 7. WatchYourLAN BurrowMCP Tool ⏸️ Parked
Deferred — no point building the tool around an unstable service. Will revisit after stability is confirmed.

---

## Key Facts

| Item | Value |
|---|---|
| New Jynx13 keypair | `~/.ssh/jynx13_to_krypton` |
| SSH config host alias | `krypton1t3` → `SuperSkorp_7@100.103.171.45` |
| authorized_keys entries (Krypton1t3) | 6 (cleaned from 9) |
| WatchYourLAN version | 2.1.4 |
| WatchYourLAN timeout | 600s (was 120s) |
| WatchYourLAN status | Stopped, restart=no |
| SELinux fix | `:z` on volume mount |
| Krypton1t3 Wazuh noise | ✅ Resolved (cause unknown, no longer a concern) |

---

## Parked for Session 13

1. **Splunk license migration — DEADLINE MAY 17** ⚠️ CRITICAL
2. Fix `splunk_tools.py` — strip `-earliest`/`-latest` CLI flags, embed time range in SPL
3. Wire Wazuh → Splunk pipeline (create `wazuh` index, configure forwarder inputs)
4. Investigate SkorpiOm forwarder `inputs.conf` — what is it actually tailing?
5. WatchYourLAN — revisit after NY trip; consider ethernet scenario
6. WatchYourLAN BurrowMCP tool — build once service is stable
7. BurrowMCP as launchd service on EagleEye11 (auto-start on boot)
8. Named Cloudflare tunnel for permanent remote URL
9. APP_NAME_MAP expansion for BurrowVoice

---

*"SELinux: the final boss of Docker volume mounts. Defeated with a single `:z`."*  
— BurrowMCP Session 12, May 2026

**Tags:** #BurrowMCP #Session12 #SSH #Jynx13 #Krypton1t3 #SSHkeygen #SSHconfig #authorizedKeys #WatchYourLAN #SELinux #Docker #Tailscale #homelab #zeroOpenPorts #WiFiDriver #wlp2s0 #Fedora
