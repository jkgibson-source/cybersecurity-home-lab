<!-- ================================================================ -->
<!-- 🦅🦂 THE BURROW LAB // REMOTE ACCESS ARCHITECTURE REPORT -->
<!-- Blue • Gold • Black // Secure Remote Operations // No Open Ports -->
<!-- ================================================================ -->

<div align="center">

# 🦅🦂 THE BURROW LAB

**Remote Access Architecture Report**  
*Secure mesh access • zero exposed inbound ports • mobile-ready lab operations*

</div>

---

# Remote Access Architecture — The Burrow
**Last Updated:** May 8, 2026  
**Status:** ✅ Validated — Full cellular remote test complete + Reticulum/RNX + Remmina/VNC layers added

---

## Overview

The Burrow's remote access stack is a layered, defense-in-depth approach to reaching the full lab from anywhere — whether from a coffee shop, a car, or New York City. Every layer is encrypted, every fallback is tested, and the whole thing runs without exposing a single port to the open internet.

The stack was built in stages across April–May 2026. Initial validation on **April 29, 2026** confirmed full cellular remote access to SkorpiOm, Krypton1t3, and EagleEye11 from SolSkorp_13 and BirdPad. Subsequent sessions added Reticulum/RNX as an authenticated command layer (May 5–6), Remmina+VNC as a live desktop layer (May 7), and J-Parrot as a second independent RNX command node with its own cryptographic identity (May 7).

---

## The Stack

| Layer | Tool | Purpose |
|---|---|---|
| Primary mesh | Tailscale | P2P encrypted tunneling, WireGuard-based |
| GUI remote — full desktop | RustDesk (via Tailscale IP) | Full desktop access, unattended; available on mobile |
| GUI remote — live mirror | Remmina + x0vncserver (TigerVNC) | Live desktop mirroring, multi-protocol; Jynx13/J-Parrot only |
| Authenticated command layer | Reticulum / rnx | Encrypted, identity-authenticated remote shell over Tailscale TCP |
| Fallback remote | RustDesk (via ID) | Relay-based, no mesh required |
| Network fallback | Twingate | If Tailscale fails entirely |
| Mobile clients | SolSkorp_13 + BirdPad | iPhone primary, iPad secondary |
| Laptop client | Jynx13 | MacBook Air, OSINT/travel machine |

No inbound ports are forwarded on the home router. All traffic routes through Tailscale's WireGuard mesh or Twingate's zero-trust connector. RustDesk's relay fallback (ID-based) provides a last resort if the mesh goes down entirely.

---

## Machine Inventory

| Machine | OS | Role | Tailscale IP | RustDesk | VNC (x0vncserver) | RNX Listener |
|---|---|---|---|---|---|---|
| EagleEye11 | macOS Tahoe 26.4.1 (M1) | SIEM / Ollama / primary host | 100.113.239.38 | ✅ 1.4.6 | ✅ macOS Screen Sharing | ✅ |
| SkorpiOm | Kali Linux (Xfce) | Primary attack machine | 100.102.6.14 | ✅ 1.4.6 | ✅ x0vncserver (systemd) | ✅ |
| Krypton1t3 | Fedora Security Lab 44 | Hypervisor / AI node | 100.103.171.45 | ✅ 1.4.6 | ✅ x0vncserver (systemd) | ✅ |
| Jynx13 | macOS Monterey | OSINT / travel client | 100.108.182.39 | Client only | Remmina cockpit (J-Parrot) | RNX command node |
| SolSkorp_13 | iOS (iPhone 13) | Mobile mesh node / client | 100.95.11.33 | Client only | — | — |
| SkorpiOm11 | iOS (iPhone 11 Pro) | Mesh node | 100.123.87.87 | — | — | — |
| BirdPad | iPadOS (iPad mini 4) | Secondary mobile client | 100.71.16.27 | Client only | — | — |
| Parrot node | Parrot OS 7.2 (SuperStick) | Travel pentest node / RNX commander | 100.95.26.111 | ✅ installed | Remmina client | RNX command node (separate identity) |

---

## RustDesk Deployment Notes

### Version
All machines running **RustDesk 1.4.6** as of April 28, 2026.

### Installation by Platform

**Kali Linux (SkorpiOm) — .deb:**
```bash
curl -LO https://github.com/rustdesk/rustdesk/releases/download/1.4.6/rustdesk-1.4.6-x86_64.deb
sudo dpkg -i rustdesk-1.4.6-x86_64.deb
sudo apt --fix-broken install -y
sudo systemctl enable rustdesk
sudo systemctl start rustdesk
```

**Fedora (Krypton1t3) — RPM (not Flatpak):**
```bash
curl -LO https://github.com/rustdesk/rustdesk/releases/download/1.4.6/rustdesk-1.4.6-0.x86_64.rpm
sudo dnf install libxdo -y
sudo rpm -i rustdesk-1.4.6-0.x86_64.rpm
sudo systemctl enable rustdesk
sudo systemctl start rustdesk
```

> ⚠️ **Do not use Flatpak on Fedora.** Flatpak sandboxing prevents RustDesk from binding to its required ports. Always install via RPM.

**Fedora firewall rules (required after install):**
```bash
sudo firewall-cmd --permanent --add-port=21115-21119/tcp
sudo firewall-cmd --permanent --add-port=21116/udp
sudo firewall-cmd --reload
```

**macOS (EagleEye11):** Standard .dmg install from rustdesk.com.

### Connecting via Tailscale IP
In RustDesk Settings → Security → **Enable direct IP access** (not enabled by default).

Connect with:
```
<tailscale-ip>:21118
```
Example: `100.103.x.x:21118`

### Permanent Password
Set in **Settings → Security → Password** on each target machine. Required for unattended access — without it, a one-time password must be read from the screen by someone physically present. When a permanent password is set, the one-time password field shows `-`. This is expected behavior, not a bug.

---

## Remmina + TigerVNC (x0vncserver) — Live Desktop Layer

Remmina is pre-installed on Parrot OS (SuperStick / J-Parrot) and serves as a full remote desktop cockpit for Jynx13. It supports RDP, VNC, SSH, SPICE, and X2Go — broader protocol coverage than RustDesk. It is not available on mobile (SolSkorp_13).

The VNC method used across the Burrow is **x0vncserver** (TigerVNC), which mirrors the *live* display at `:0` rather than creating a parallel virtual session. This is the correct choice for lab monitoring — you see exactly what's on screen.

### Burrow VNC Map

| Node | VNC Address | Method | Status |
|---|---|---|---|
| Krypton1t3 | `100.103.171.45:5900` | x0vncserver (systemd) | ✅ Persistent |
| SkorpiOm | `100.102.6.14:5900` | x0vncserver (systemd) | ✅ Persistent |
| EagleEye11 | `100.113.239.38:5900` | macOS Screen Sharing (built-in) | ✅ Always on |
| Jynx13 | — | Remmina client (cockpit) | ✅ J-Parrot |

### Server Setup — Krypton1t3 (Fedora)

```bash
sudo dnf install tigervnc-server
vncpasswd
x0vncserver -display :0 -passwordfile ~/.vnc/passwd
```

**Systemd service** (`/etc/systemd/system/x0vncserver.service`):
```ini
[Unit]
Description=TigerVNC x0vncserver - Live Desktop Share
After=graphical.target

[Service]
Type=simple
User=SuperSkorp_7
ExecStart=/usr/bin/x0vncserver -display :0 -passwordfile /home/SuperSkorp_7/.vnc/passwd
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical.target
```

### Server Setup — SkorpiOm (Kali Linux)

Kali requires a different package than Fedora, and has a non-standard passwd file location:

```bash
# x0vncserver lives in the scraping server package, NOT standalone-server
sudo apt install tigervnc-scraping-server

# Passwd file is NOT at ~/.vnc/passwd on this version
# Actual location:
~/.config/tigervnc/passwd

# Find it with:
find / -name "passwd" -path "*vnc*" 2>/dev/null

# Must specify -localhost no or it binds to 127.0.0.1 only
x0vncserver -display :0 -passwordfile ~/.config/tigervnc/passwd -localhost no

# Verify it's listening on the network (not just loopback):
ss -tlnp | grep 5900   # must show 0.0.0.0:5900

# Open UFW:
sudo ufw allow 5900/tcp
```

**Systemd service** (`/etc/systemd/system/x0vncserver.service`):
```ini
[Unit]
Description=TigerVNC x0vncserver - Live Desktop Share
After=graphical.target

[Service]
Type=simple
User=solskorp_11
ExecStart=/usr/bin/x0vncserver -display :0 -passwordfile /home/solskorp_11/.config/tigervnc/passwd -localhost no
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical.target
```

### EagleEye11 (macOS)

No additional setup required. Screen Sharing was already enabled in System Settings → General → Sharing. Remmina connects via VNC to `100.113.239.38:5900` using the macOS system login password (no separate VNC password).

### VNC Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Parallel desktop instead of live screen | `vncserver :1` creates new session | Use `x0vncserver -display :0` instead |
| Authentication failure loops | passwd file not found / wrong path | `find / -name "passwd" -path "*vnc*"` |
| "Too many security failures" lockout | Too many failed attempts | `pkill x0vncserver` and restart |
| Binds to 127.0.0.1 only | Default Kali TigerVNC behavior | Add `-localhost no` flag |
| "VNC server already running" on systemd start | Manual instance still running | `pkill x0vncserver` before `systemctl start` |

---

## Reticulum / RNX — Authenticated Command Layer

Reticulum/rnx provides an encrypted, identity-authenticated remote shell channel carried over Tailscale TCP. Each home listener only accepts commands from explicitly allow-listed cryptographic identities — no other node can send commands even if it reaches port 4242.

There are now **two independent RNX command nodes**: Jynx13 macOS and J-Parrot (Parrot OS on SuperStick). Each has its own separate identity. All three home listener start scripts have been permanently updated to allow both identities via multiple `-a` flags, e.g.:

```bash
rnx -l -a <jynx13-macos-identity> -a <jynx13-parrot-identity>
```

This layer is documented in full in the companion reports:
- **`the_burrow_reticulum_rnx_report_2026-05-06_PUBLIC.md`** — initial setup, home listener config, destination hashes, management scripts
- **`the_burrow_jynx13_parrot_reticulum_rnx_commander_install_report_2026-05-07.md`** — J-Parrot install, identity generation, listener script updates

> ⚠️ Both Jynx13 identity hashes (macOS and Parrot) are intentionally omitted from all public reports. The home node destination hashes are safe to publish — they cannot be used without a Jynx13 identity being allow-listed on each listener.

### Quick Reference

All home nodes listen on TCP port `4242`. Both Jynx13 commanders connect as TCP clients to all three.

| Node | OS | RNX Role | Version | Helper Script |
|---|---|---|---|---|
| SkorpiOm | Kali Linux | Listener | 1.2.3 | `~/reticulum-scripts/skorpiom-rnx.sh "<cmd>"` |
| EagleEye11 | macOS Tahoe | Listener | 1.2.3 | `~/reticulum-scripts/eagleeye-rnx.sh "<cmd>"` |
| Krypton1t3 | Fedora 44 | Listener | 1.2.3 | `~/reticulum-scripts/krypton-rnx.sh "<cmd>"` |
| Jynx13 macOS | macOS Monterey | Commander | 1.2.3 | — |
| J-Parrot | Parrot OS 7.2 | Commander | 1.2.4 | same scripts, separate identity |

> **Version note:** J-Parrot installed rnx 1.2.4 (latest available at time of install, May 7). Home listeners remain on 1.2.3. No compatibility issues observed.

### Listener Health Check

A healthy listener node status must show all three of these:

```
Shared Instance: Up
Serving: 1 program       ← critical — "0 programs" means rnx -l isn't properly attached
TCPServerInterface: Up
```

If `Serving: 0 programs` despite an `rnx -l` process appearing in `ps`, do a full stack restart:

```bash
pkill -f "rnx -l" 2>/dev/null || true
pkill -f "rnsd" 2>/dev/null || true
nohup rnsd -vv > ~/reticulum-logs/rnsd-<node>.log 2>&1 &
sleep 4
# then re-run the node's start listener script
~/reticulum-scripts/start-<node>-rnx-listener.sh
```

---

## Tailscale Notes

### Krypton1t3 (Fedora) — Required Flags
Must specify non-default flags each time:
```bash
sudo tailscale up --accept-dns=false --accept-routes=false --operator=SuperSkorp_7
```

### Twingate + Tailscale Conflict on Krypton1t3
Both cannot run simultaneously — they conflict over the network stack. Use these aliases in `~/.bashrc`:
```bash
alias ts-up='sudo systemctl stop twingate && sudo tailscale up --accept-dns=false --accept-routes=false --operator=SuperSkorp_7'
alias ts-down='sudo tailscale down && sudo systemctl start twingate'
```

### SkorpiOm DNS Lock
Tailscale's MagicDNS overwrites `/etc/resolv.conf` on SkorpiOm. Locked to 8.8.8.8:
```bash
sudo chattr +i /etc/resolv.conf
# and in tailscale up:
sudo tailscale up --accept-dns=false
```

---

## Parrot OS / SuperStick Notes

RustDesk requires an **X11 session** — Wayland support is experimental and unattended access will not work reliably. At the Parrot OS login screen, select the **X11/Xfce session** before logging in.

> ⚠️ Critical for NY trip: remember to select X11 at login every time Jynx13 boots into Parrot mode. Remmina is available in any session; RustDesk unattended access requires X11.

### J-Parrot RNX Persistence Verification

Because J-Parrot runs from an encrypted live boot persistence volume, verify these still exist after every reboot before assuming the RNX layer is ready:

```bash
ls -la ~/rns-env
ls -la ~/.reticulum
ls -la ~/reticulum-scripts
```

Then activate and test:

```bash
source ~/rns-env/bin/activate
rnstatus | head -120
~/reticulum-scripts/skorpiom-rnx.sh "/bin/bash -lc 'hostname; date; uptime'"
~/reticulum-scripts/eagleeye-rnx.sh "/bin/zsh -lc 'hostname; date; uptime; sw_vers'"
~/reticulum-scripts/krypton-rnx.sh "/bin/bash -lc 'hostname; date; uptime; cat /etc/os-release | head -5'"
```

---

## SELinux Compatibility (Krypton1t3)

Fedora Security Lab runs SELinux in enforcing mode. RustDesk and x0vncserver both coexist without issue — no custom policy needed for either. Verified by running live remote connections and checking the audit log:

```bash
sudo ausearch -c 'rustdesk' --raw | audit2allow -M rustdesk-policy
# Result: "Nothing to do" — no denials, no policy needed
```

Enforcing mode remains intact. If a future Fedora or RustDesk update causes denials, generate a policy with:
```bash
sudo setenforce 0
# trigger a RustDesk connection from remote
sudo ausearch -c 'rustdesk' --raw | audit2allow -M rustdesk-policy
sudo semodule -i rustdesk-policy.pp
sudo setenforce 1
```
`semodule -i` makes the policy survive reboots automatically.

---

## Validation Log

| Date | Test | Method | Result |
|---|---|---|---|
| April 28, 2026 | Jynx13 → Krypton1t3 | RustDesk ID | ✅ Pass |
| April 28, 2026 | Jynx13 → Krypton1t3 | Tailscale IP + port 21118 | ✅ Pass |
| April 28, 2026 | SolSkorp_13 → Jynx13 | RustDesk ID | ✅ Pass |
| April 28, 2026 | Full mesh (all machines) | Inside + outside Puffin | ✅ Pass |
| April 29, 2026 | SolSkorp_13 → SkorpiOm | RustDesk / cellular | ✅ Pass |
| April 29, 2026 | SolSkorp_13 → Krypton1t3 | RustDesk / cellular | ✅ Pass |
| April 29, 2026 | BirdPad → EagleEye11 (Splunk) | Hotspot via SolSkorp_13 | ✅ Pass |
| April 29, 2026 | Krypton1t3 → Splunk ingest | Log forwarding confirmed | ✅ 13 events |
| May 5–6, 2026 | Jynx13 macOS → SkorpiOm / EagleEye11 / Krypton1t3 | Reticulum / rnx | ✅ All three nodes |
| May 7, 2026 | J-Parrot → Krypton1t3 | Remmina / VNC (x0vncserver) | ✅ Pass |
| May 7, 2026 | J-Parrot → SkorpiOm | Remmina / VNC (x0vncserver) | ✅ Pass |
| May 7, 2026 | J-Parrot → EagleEye11 | Remmina / VNC (Screen Sharing) | ✅ Pass |
| May 7, 2026 | J-Parrot → SkorpiOm / EagleEye11 / Krypton1t3 | Reticulum / rnx (new Parrot identity) | ✅ All three nodes |

---

## NY Trip Readiness

**Target:** August 2026, Newburgh, NY

The full remote access stack is confirmed operational over cellular. The primary use case is maintaining lab access for training, Splunk monitoring, and Hermes Agent work while traveling for the annual Ritz Kidz Youth Circus workshops.

**Outstanding pre-trip items:**
- [ ] Write permanent SELinux policy for RustDesk on Krypton1t3 using `audit2allow` (precautionary — current setup works without it)
- [ ] Full sustained test from a truly external network (coffee shop / parents' house)
- [ ] Run Reticulum pre-travel readiness checklist (see companion RNX report)
- [ ] Verify EagleEye11 macOS firewall still allows Homebrew Python for RNX listener (see companion RNX report)
- [ ] Verify J-Parrot RNX persistence after reboot (rns-env, .reticulum, reticulum-scripts all intact; test all three command paths from both commanders if practical)
- [ ] Reboot each home listener and confirm listener scripts restart clean with `Serving: 1 program`

---

*Architecture documented by JBird (jkgibson-source) with Claude (Anthropic) — The Burrow Lab*

---

<div align="center">

**THE BURROW LAB**  
*Blue • Gold • Black // EagleEye11 • SkorpiOm • Krypton1t3 • Jynx13*  
**Secure the nest. Watch the mesh. Keep the lab alive.**

</div>

<!-- ================================================================ -->
<!-- END THE BURROW LAB REPORT -->
<!-- ================================================================ -->
