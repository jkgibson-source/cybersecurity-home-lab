# 🦂 The Burrow — Reticulum / RNX Remote-Ops Layer
### Installation & Validation Report · 2026-05-05 → 2026-05-06

---

## Overview

Reticulum / `rnx` is now installed and validated across all four core Burrow nodes. It operates as an encrypted, low-overhead, mesh-capable remote command layer carried over the existing Tailscale network — and is designed to grow alongside the lab without needing to be rebuilt.

For the immediate use case — the summer trip to New York — it gives Jynx13 a reliable fallback channel to check the health of every home node without depending on SSH, VPN tunnels, or any centralized service.

```
Jynx13 (travel)  ──►  SkorpiOm    (Kali Linux / attack box)
                  ──►  EagleEye11  (macOS M1 / SIEM node)
                  ──►  Krypton1t3  (Fedora 44 / AI & lab node)
```

All three paths are confirmed working and restart-validated.

---

## What Is Reticulum?

[Reticulum](https://reticulum.network/) is a cryptographic networking stack designed for resilience. It works over nearly any transport (TCP, UDP, serial, LoRa, packet radio) and requires no central infrastructure. The `rnx` tool — part of the RNS suite — provides authenticated remote shell command execution over any Reticulum-connected path.

For The Burrow, the transport is TCP over Tailscale. This means every `rnx` command travels through an already-encrypted Tailscale tunnel and is additionally authenticated at the Reticulum layer by a per-node identity hash — so only Jynx13's known identity can execute commands on any listener node.

---

## Network Map

### Tailscale IPs

| Node | Role | OS | Tailscale IP |
|---|---|---|---|
| Jynx13 | Travel command node | macOS Monterey | 100.108.182.39 |
| SkorpiOm | Home listener | Kali Linux | 100.102.6.14 |
| EagleEye11 | Home listener | macOS Tahoe (26.4.1) | 100.113.239.38 |
| Krypton1t3 | Home listener | Fedora Linux 44 | 100.103.171.45 |

### RNX Identity & Destination Reference

| Node | RNX Identity / Destination | Notes |
|---|---|---|
| Jynx13 | `<jynx13-identity-hash>` | Allow-listed on all home listeners |
| SkorpiOm | `d99f53f8f3d6ae950dc795c233643318` | Send commands here from Jynx13 |
| EagleEye11 | `afbed294c0cef2fd26e882b5838fdcfc` | Send commands here from Jynx13 |
| Krypton1t3 | `9160c8c249df0a3ce8911b9a61bf97fd` | Send commands here from Jynx13 |

> ⚠️ **The Jynx13 identity is critical.** Every home listener's `rnx -l` is started with `-a <jynx13-identity-hash>`. If this value is wrong, the listener will reject all commands with `Identity not allowed, tearing down link`. Copy it exactly.

---

## Software Versions

All nodes are running identical Reticulum/RNX versions:

```
rnsd 1.2.3
rnx  1.2.3
```

Each node uses a Python virtual environment at `~/rns-env`. Installation command (inside the venv):

```bash
pip install rns
```

> **EagleEye11 caveat:** The system Python (3.9.6, Apple/CLT) is too old for Reticulum. EagleEye11 requires Homebrew Python 3.14+. The venv must be built with the Homebrew Python binary, not the system one.

---

## Reticulum Configuration

All home listener nodes use the same config pattern. The key element is a `TCPServerInterface` on port `4242`.

**Home node `~/.reticulum/config` (all three listeners):**

```ini
[reticulum]

enable_transport = False
share_instance = Yes
shared_instance_port = 37428
instance_control_port = 37429
panic_on_interface_error = No

[logging]

loglevel = 6

[interfaces]

  [[TCP Server Interface]]
  type = TCPServerInterface
  enabled = yes
  listen_ip = 0.0.0.0
  listen_port = 4242
```

**Jynx13 `~/.reticulum/config` — TCP clients pointing at all three home nodes:**

```ini
[interfaces]

  [[TCP Client to SkorpiOm]]
  type = TCPClientInterface
  enabled = yes
  target_host = 100.102.6.14
  target_port = 4242

  [[TCP Client to EagleEye11]]
  type = TCPClientInterface
  enabled = yes
  target_host = 100.113.239.38
  target_port = 4242

  [[TCP Client to Krypton1t3]]
  type = TCPClientInterface
  enabled = yes
  target_host = 100.103.171.45
  target_port = 4242
```

> If a home node is offline, Jynx13 will print a `Connection refused` warning for that node's TCP client. This does **not** affect connections to the other nodes. The warnings are informational.

---

## Management Scripts

Each home node has three scripts in `~/reticulum-scripts/`. All were validated with a stop → start → status → remote command cycle.

### SkorpiOm (Kali Linux / `bash`)

```bash
# Start
~/reticulum-scripts/start-skorpiom-rnx-listener.sh

# Stop
~/reticulum-scripts/stop-skorpiom-rnx-listener.sh

# Status
~/reticulum-scripts/status-skorpiom-rnx-listener.sh
```

### EagleEye11 (macOS / `zsh`)

```zsh
# Start
~/reticulum-scripts/start-eagleeye-rnx-listener.sh

# Stop
~/reticulum-scripts/stop-eagleeye-rnx-listener.sh

# Status
~/reticulum-scripts/status-eagleeye-rnx-listener.sh
```

### Krypton1t3 (Fedora Linux / `bash`)

```bash
# Start
~/reticulum-scripts/start-krypton-rnx-listener.sh

# Stop
~/reticulum-scripts/stop-krypton-rnx-listener.sh

# Status
~/reticulum-scripts/status-krypton-rnx-listener.sh
```

**Successful status markers (any node):**

```
Shared Instance[...]
Status : Up
```

```
TCPServerInterface[TCP Server Interface/0.0.0.0:4242]
Status : Up
```

---

## Jynx13 Helper Scripts

These live on Jynx13 in `~/reticulum-scripts/` and wrap the destination hash so you don't have to remember it.

### Command SkorpiOm

```zsh
~/reticulum-scripts/skorpiom-rnx.sh "/bin/bash -lc 'hostname; date; uptime; df -h /; systemctl --failed --no-pager'"
```

### Command EagleEye11

```zsh
~/reticulum-scripts/eagleeye-rnx.sh "/bin/zsh -lc 'hostname; date; uptime; sw_vers'"
```

### Command Krypton1t3

```zsh
~/reticulum-scripts/krypton-rnx.sh "/bin/bash -lc 'hostname; date; uptime; cat /etc/os-release | head -5'"
```

> **Shell wrapping is required for compound commands.** `rnx` does not automatically invoke a shell. Always wrap multi-command calls in `"/bin/bash -lc 'cmd1; cmd2'"` (Linux) or `"/bin/zsh -lc 'cmd1; cmd2'"` (macOS).

---

## Validated Command Output

### Jynx13 → SkorpiOm

```
SkorpiOm
Wed May  6 03:05:16 PM EDT 2026
15:05:16 up 4 days, 15:34, 1 user, load average: 0.54, 1.00, 0.89
```

### Jynx13 → EagleEye11

```
EagleEye11.local
Wed May  6 21:05:41 EDT 2026
21:05 up 24 days, 20:47, 2 users, load averages: 8.01 8.39 8.29
ProductName:        macOS
ProductVersion:     26.4.1
BuildVersion:       25E253
```

### Jynx13 → Krypton1t3

```
Krypton1t3
Wed May  6 10:59:22 PM EDT 2026
22:59:22 up 11:58, 1 user, load average: 0.72, 0.58, 0.62
NAME="Fedora Linux"
VERSION="44 (Forty Four)"
```

---

## Emergency Restart Pattern

If a node's listener goes stale, the full recovery is:

**On the home node:**

```bash
~/reticulum-scripts/stop-<node>-rnx-listener.sh
~/reticulum-scripts/start-<node>-rnx-listener.sh
~/reticulum-scripts/status-<node>-rnx-listener.sh
```

**Then from Jynx13:**

```zsh
~/reticulum-scripts/<node>-rnx.sh "/bin/bash -lc 'hostname; date; uptime'"
```

---

## Known Quirks — Don't Chase These

| Symptom | Root Cause | Action |
|---|---|---|
| `AutoInterface Peers : 0 reachable` on SkorpiOm | Local multicast discovery, unrelated to TCP/rnx path | Ignore |
| `AutoInterface utun5: No buffer space` on Jynx13 | macOS Tailscale VPN interface behavior | Ignore |
| `Connection refused` for an offline node in Jynx13's log | That node's listener is simply not running | Ignore if other nodes work |
| Status script appears in its own process list | Script filename contains `rnx` | Harmless |
| `Could not get RNS status` immediately after starting rnsd | Shared instance hasn't initialized yet | Wait a few seconds and re-run `rnstatus` |

---

## EagleEye11: macOS Firewall Note

EagleEye11's `rnx` listener requires macOS firewall approval for the Homebrew Python executable. This was granted during setup. The approval is tied to the **specific executable path:**

```
/opt/homebrew/Cellar/python@3.14/3.14.4_1/Frameworks/Python.framework/
  Versions/3.14/Resources/Python.app/Contents/MacOS/Python
```

If Homebrew upgrades Python or the venv is rebuilt, macOS may treat the new binary as a new app and prompt again. **Do not upgrade Homebrew Python or rebuild the venv shortly before travel** unless physically present to approve the prompt.

Pre-travel firewall check on EagleEye11:

```zsh
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps | grep -A1 -B1 "python@3.14"
```

Expected result: `Allow incoming connections`

If the prompt needs to be re-triggered while physically present, remove and re-approve:

```zsh
~/reticulum-scripts/stop-eagleeye-rnx-listener.sh
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --remove \
  "/opt/homebrew/Cellar/python@3.14/3.14.4_1/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python"
~/reticulum-scripts/start-eagleeye-rnx-listener.sh
```

Then trigger a command from Jynx13 to force the prompt.

> **Fallback:** RustDesk remains available for GUI-level recovery if the firewall prompt appears while remote.

---

## Pre-Travel Readiness Checklist

Run this **3–7 days before departure**:

- [ ] Start listener scripts on SkorpiOm, EagleEye11, and Krypton1t3
- [ ] Confirm Tailscale is active and connected on all four nodes
- [ ] Confirm `rnstatus` shows TCP server interface Up on each listener
- [ ] Confirm EagleEye11 firewall entry still shows `Allow incoming connections`
- [ ] Confirm Jynx13 helper scripts reach all three nodes successfully
- [ ] Reboot each listener node once and restart listener scripts
- [ ] Confirm Jynx13 can still command each node after reboot
- [ ] **Freeze:** No `brew upgrade`, Python upgrades, venv rebuilds, or `pip reinstall rns` after this window unless physically present

---

## Session History

### 2026-05-05 — Proof of Concept (SkorpiOm ↔ Jynx13, bidirectional)

The initial session proved the Reticulum/rnx path was viable. The first working direction was `SkorpiOm → Jynx13`, then flipped to confirm bidirectional capability. Key discovery: compound commands require explicit shell wrapping (`/bin/zsh -lc '...'`). The `AutoInterface Peers : 0` warning was identified as noise and decoupled from TCP path health.

### 2026-05-06 (AM) — SkorpiOm as Home Listener

Direction flipped to the intended travel-use-case architecture: `Jynx13 → SkorpiOm`. SkorpiOm's old TCP client block (pointing at Jynx13) was disabled to stop `Connection refused` log spam. Three management scripts were created and validated on SkorpiOm. Jynx13's `skorpiom-rnx.sh` helper script was written and confirmed working. A typo in the Jynx13 identity allow-list (one character transposed at the start) caused an auth failure that was caught and corrected.

### 2026-05-06 (PM) — EagleEye11 Added

EagleEye11 started with no Reticulum setup. The system Python 3.9.6 produced a syntax error during `pip install rns`; Homebrew Python 3.14.4 resolved it. EagleEye11 was configured as a TCP server listener. macOS firewall approval was required and granted for the Homebrew Python executable. Scripts created, validated. `Jynx13 → EagleEye11` confirmed working.

### 2026-05-06 (Evening) — Krypton1t3 Added (Cleanest Install)

Krypton1t3 (Fedora 44) was the smoothest setup of the three. Python 3.14.4 and Tailscale were already in place. `pip install rns` succeeded immediately. No firewall prompts (Linux). Scripts created, validated, and restart-tested. `Jynx13 → Krypton1t3` confirmed working. The full Burrow RNX remote-ops backbone was declared complete.

---

## Completed Milestone Summary

```
✅ Jynx13 → SkorpiOm     confirmed and scripted
✅ Jynx13 → EagleEye11   confirmed and scripted
✅ Jynx13 → Krypton1t3   confirmed and scripted
✅ All nodes: rnsd 1.2.3 / rnx 1.2.3
✅ All home nodes: TCP server interface Up on 0.0.0.0:4242
✅ All scripts: start / stop / status validated
✅ All paths: restart-tested (stop → start → status → remote command)
✅ EagleEye11 macOS firewall: approved and documented
✅ Jynx13 Reticulum config: all three TCP client blocks present
```

---

## Future Work

| Priority | Item |
|---|---|
| Optional | Convert SkorpiOm and Krypton1t3 listeners into `systemd --user` services for auto-start |
| Optional | Convert EagleEye11 listener into a `launchd` agent for auto-start |
| Optional | Standardize a common Jynx13 "Burrow health sweep" script that pings all three nodes in sequence |
| Future | Extend Reticulum to LoRa/Meshtastic hardware for a fully off-grid backup path |

---

## Tags

`#TheBurrow` `#Reticulum` `#RNS` `#RNX` `#Tailscale` `#Jynx13` `#SkorpiOm` `#EagleEye11` `#Krypton1t3` `#RemoteOps` `#HomeLab` `#SummerTravelSetup` `#FallbackCommandChannel` `#TravelReadiness` `#BurrowComms` `#LocalFirstOps`
