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
**Last Updated:** April 29, 2026  
**Status:** ✅ Validated — Full cellular remote test complete

---

## Overview

The Burrow's remote access stack is a layered, defense-in-depth approach to reaching the full lab from anywhere — whether from a coffee shop, a car, or New York City. Every layer is encrypted, every fallback is tested, and the whole thing runs without exposing a single port to the open internet.

The stack was built in stages across April 2026 and validated on **April 29, 2026** with a live cellular remote session connecting to SkorpiOm, Krypton1t3, and EagleEye11 from SolSkorp_13 and BirdPad while out running errands.

---

## The Stack

| Layer | Tool | Purpose |
|---|---|---|
| Primary mesh | Tailscale | P2P encrypted tunneling, WireGuard-based |
| GUI remote | RustDesk (via Tailscale IP) | Full desktop access, unattended |
| Fallback remote | RustDesk (via ID) | Relay-based, no mesh required |
| Network fallback | Twingate | If Tailscale fails entirely |
| Mobile clients | SolSkorp_13 + BirdPad | iPhone primary, iPad secondary |
| Laptop client | Jynx13 | MacBook Air, OSINT/travel machine |

No inbound ports are forwarded on the home router. All traffic routes through Tailscale's WireGuard mesh or Twingate's zero-trust connector. RustDesk's relay fallback (ID-based) provides a last resort if the mesh goes down entirely.

---

## Machine Inventory

| Machine | OS | Role | Tailscale IP | RustDesk |
|---|---|---|---|---|
| EagleEye11 | macOS (M1) | SIEM / Ollama / primary host | 100.113.239.38 | ✅ 1.4.6 |
| SkorpiOm | Kali Linux (Xfce) | Primary attack machine | 100.102.6.14 | ✅ 1.4.6 |
| Krypton1t3 | Fedora Security Lab 44 | Hypervisor / Hermes Forge | 100.103.171.45 | ✅ 1.4.6 |
| Jynx13 | macOS Monterey | OSINT / travel client | 100.108.182.39 | Client only |
| SolSkorp_13 | iOS (iPhone 13) | Mobile mesh node / client | 100.95.11.33 | Client only |
| SkorpiOm11 | iOS (iPhone 11 Pro) | Mesh node | 100.123.87.87 | — |
| BirdPad | iPadOS (iPad mini 4) | Secondary mobile client | 100.71.16.27 | Client only |
| Parrot node | Parrot OS (SuperStick) | Travel pentest node | 100.95.26.111 | ✅ installed |

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

> ⚠️ Critical for NY trip: remember to select X11 at login every time Jynx13 boots into Parrot mode.

---

## SELinux Compatibility (Krypton1t3)

Fedora Security Lab runs SELinux in enforcing mode. RustDesk coexists without issue — no custom policy needed. Verified by running a live remote connection and checking the audit log:

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

---

## NY Trip Readiness

**Target:** August 2026, Newburgh, NY

The full remote access stack is confirmed operational over cellular. The primary use case is maintaining lab access for training, Splunk monitoring, and Hermes Agent work while traveling for the annual Ritz Kidz Youth Circus workshops.

**Outstanding pre-trip items:**
- [ ] Write permanent SELinux policy for RustDesk on Krypton1t3 using `audit2allow` (precautionary — current setup works without it)
- [ ] Full sustained test from a truly external network (coffee shop / parents' house)

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
