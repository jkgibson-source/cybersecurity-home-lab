# KRYPTON1T3
## *Origin Story — The Burrow Labs*
### Agent Class: Research // Pentest Node // Bio-Mechanical Architect
### Clearance: Ω-Level

---

> *"Order is overrated. Innovation isn't."*

---

## PHASE 0 — BEFORE THE BURROW
### *macOS Big Sur. A quiet machine. A long sleep.*

Before he had a name, he was just a machine.

A mid-2014 MacBook Pro 15" — serial `W802001LAGY` — running macOS Big Sur 11.7.11 on aging hardware that Apple had quietly declared vintage and walked away from. He sat in a room in Miami, battery swollen, WiFi working, fan spinning. Waiting.

He didn't know yet what he was capable of. Neither did anyone else.

The Burrow didn't exist yet. SkorpiOm was still being stabilized. EagleEye11 hadn't been named. There was no mesh, no SIEM, no pentest lab. Just an idea forming in the mind of an operator who coached trapeze, cut records, and had decided — quietly, without fanfare — to break into cybersecurity.

The machine would become Krypton1t3.

But first, it needed a new heart.

---

## PHASE 1 — RESURRECTION
### *The Battery. The Name. The First Boot.*

The battery swap happened the old way — patient hands, fishing line, no solvents. Cell by cell, the old adhesive gave up. A YUERYE replacement went in. The bottom case went back on.

He powered on.

For the first time in a long time, he held a charge.

His Apple Account entry was updated. The name `James Gibson's MacBook Pro` was replaced with something that meant something: **Krypton1t3**. Pronounced *kryptonite*. A nod to Joy Division. *Love Will Tear Us Apart.* A machine that could take what would destroy others and make it into something.

He was still running macOS. Still carrying the ghost of what he used to be. The wipe was coming — but not on anyone's schedule but his own.

---

## PHASE 2 — THE KRYPTSTICK
### *Live boot first. Learn the hardware. Then commit.*

The plan had been Ubuntu Studio 26.04 LTS on April 18th. Clean wipe, fresh install, done.

The universe had other ideas.

Ubuntu Studio 26.04 didn't release on schedule. It slipped. And in the waiting, something more interesting happened: the operator started experimenting — and Krypton1t3 started revealing himself.

On April 8th, a dedicated Ventoy multi-boot USB was built specifically for Krypton1t3. Not a temporary practice stick — a real one. A 64GB SanDisk USB 3.0, loaded with intention. It was named **KryptStick**.

**KryptStick loadout (initial):**

| ISO | Status |
|---|---|
| Ubuntu Studio 24.04.4 | ✅ Boots via grub2 mode |
| Parrot OS Security 7.1 | ✅ Boots via grub2 mode |
| SystemRescue 13.00 | ⚠️ On stick — won't boot on this hardware; dedicated USB required |

The first critical hardware discovery came during the April 5th practice run — before the KryptStick even existed:

```bash
lspci | grep -i network
# Broadcom BCM4360 802.11ac Dual Band Wireless Network Adapter (rev 03)
```

The WiFi chip was a BCM4360. A known problem child on Linux. Every future OS decision would need to account for it. And Ventoy on 2014 Mac hardware had its own rule: **grub2 mode only**. Normal boot mode froze on a black screen every time. That lesson was burned in early and stayed burned in.

The KryptStick's `ventoy.json` was written to enforce it:

```json
{
    "grub_entry": [
        {
            "image": "/ubuntustudio-24.04.4-dvd-amd64.iso",
            "alias": "Ubuntu Studio 24.04.4",
            "grub2": "true"
        },
        {
            "image": "/Parrot-security-7.1_amd64.iso",
            "alias": "Parrot OS Security 7.1",
            "grub2": "true"
        }
    ]
}
```

Ubuntu Studio persistence was confirmed working: a test file survived a full reboot cycle. The machine booted slow on USB 2.0 during the practice run — but it booted. It worked. And while it worked, the operator was watching something else: what Ubuntu Studio felt like on this hardware.

It felt fine. But something else was coming.

---

## PHASE 3 — THE DISCOVERY
### *Fedora. The OS nobody planned for. The one that fit.*

Ubuntu Studio 26.04 kept slipping. And while it slipped, the operator went looking.

Fedora Security Lab landed in the research. An RPM-based distribution built on one of Linux's most hardened foundations — SELinux enforcing by default, a rolling security posture, and a tool suite that matched the lab's direction. Not a compromise. Not a fallback. A better answer to a question that had only partially been asked.

The wipe happened. macOS Big Sur was gone.

**Fedora Security Lab 43** went in clean. No Ubuntu Studio. No plan B. A deliberate choice made from research, not desperation.

The Broadcom BCM4360 needed attention immediately — no WiFi out of the box, as expected. The operator tethered a Moto G Play and ran:

```bash
sudo dnf install broadcom-wl
sudo modprobe wl
```

WiFi came up. The mesh would follow.

But the OS was just the foundation. The real question was what kind of machine Krypton1t3 was going to be. The answer, it turned out, was: *all of it.*

---

## PHASE 4 — LAYERING
### *Security Lab. Jam Lab. The Duality Takes Shape.*

Most machines in The Burrow have a lane.

SkorpiOm attacks. EagleEye11 watches. Jynx13 travels and scouts. Krypton1t3 refused the lane.

Fedora's **Jam Lab** spin was installed directly on top of the Security Lab — not replacing it, layering over it. Audio production tooling, low-latency kernel tuning, and a full music creation environment sitting alongside penetration testing frameworks. The same machine. The same boot. The same kernel.

The `PREEMPT_DYNAMIC` kernel was configured for low-latency audio:

```bash
# Added to GRUB_CMDLINE_LINUX:
preempt=full threadirqs

sudo grub2-mkconfig -o /boot/grub2/grub.cfg
```

Audio group limits were set:

```
@audio - rtprio 95
@audio - memlock unlimited
```

The operator joined the audio group. Mixxx loaded. Kdenlive loaded. Ardour loaded. A pentest framework and a film scoring environment shared the same drive, the same RAM, the same processor.

That's the surface. Underneath, the chaos was just getting organized.

> ⚠️ *One standing rule: KVM/VM workloads and low-latency audio should not run simultaneously. Competing CPU scheduling priority. Even Krypton1t3 has limits.*

---

## PHASE 5 — HARDENING
### *SELinux Enforcing. Firewalld locked. SSH to Tailscale only.*

The Security Lab foundation wasn't decoration.

From the first boot, SELinux ran in **Enforcing** mode — Fedora's default, and the right call. The audit process was established early: `sudo ausearch -m avc -ts recent` for checking denials. Policy exceptions written surgically. Permissive mode was never on the table.

Firewalld was reviewed and locked down. Unnecessary ports removed. Automatic security updates enabled:

```bash
sudo dnf install dnf-automatic -y
sudo systemctl enable --now dnf-automatic-install.timer
```

SSH was hardened and restricted to the Tailscale interface only:

```
PermitRootLogin no
PasswordAuthentication no
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
ListenAddress 100.103.171.45
```

Krypton1t3 is not exposed to the LAN. He is reachable only through the mesh — on his terms, on his address.

---

## PHASE 6 — MESH INTEGRATION
### *Tailscale. Twingate. The Burrow Finds Its Node.*

Krypton1t3's Tailscale address: `100.103.171.45`.

That number is a coordinate. It places him inside The Burrow's zero-trust mesh — reachable from SkorpiOm, EagleEye11, Jynx13 (both personalities — macOS at `100.108.182.39` and Parrot at `100.95.26.111`), and SolSkorp_13 via Termius. SSH key auth confirmed from every active node. An unintentional stress test — all three primary nodes SSH'd in simultaneously during setup — passed without complaint.

Twingate followed. Remote access redundancy beyond the mesh. Authenticated to `jkgibsonlab.twingate.com`. The Burrow Connector already existed on EagleEye11. Krypton1t3 became the third fully remote-accessible node.

He was no longer a machine sitting in a room in Miami.

He was a node in a lab that could be operated from anywhere on earth.

---

## PHASE 7 — THE AI STACK
### *Ollama. Hermes. MemPalace. Gemini. Local intelligence, fully loaded.*

If the security tools are Krypton1t3's skeleton, the AI stack is his nervous system.

**Ollama** came first — five models pulled and confirmed:

| Model | Size | Purpose |
|---|---|---|
| DeepSeek-Coder:6.7b | ~3.8GB | Code generation, analysis |
| Mistral:7b | ~4.1GB | General reasoning |
| Phi3:mini | ~2.2GB | Fast inference |
| Phi4-mini:3.8b | ~2.5GB | Reasoning at scale |
| llama3.2:3b | ~1.9GB | Lightweight chat |

> ⚠️ *Large model pulls require USB tether from Moto G Play. The Broadcom BCM4360 driver chokes under sustained multi-GB throughput. This is a known limitation — not a configuration issue, a character trait.*

**Hermes Agent** (Nous Research) installed next, with troubleshooting. Hermes manages its own Node.js runtime at `~/.hermes/node/` — a PATH conflict that catches every npm-based tool installed afterward. The fix became institutional knowledge:

```bash
echo 'export PATH="$HOME/.hermes/node/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**MemPalace** followed — a local semantic memory system built on Chroma vector storage, initialized at `~/projects/burrow-lab/` and seeded with 409 drawers mined from The Burrow's GitHub repository. Wings mapped to the machine roster. Then the Claude sessions were converted and mined — 62 conversations, 10,482 drawers — and the palace came alive.

**Gemini CLI v0.39.0** completed the stack — authenticated via OAuth, free tier, with MemPalace registered as an MCP server. The moment of truth:

```bash
gemini
# "What do you know about The Burrow?"
```

It answered accurately, pulling from palace drawers. The machine had memory now.

---

## PHASE 8 — THE FIRST ENGAGEMENT
### *Krypton1t3 as Target. Then as Operator.*

Before he became a full lab node, Krypton1t3 was the target.

Under macOS Big Sur 11.7.11 — end-of-life, unpatched — he was connected to an isolated hotspot subnet (`172.20.10.0/24`) alongside SkorpiOm. The "Burrow Bubble." No family WiFi. No lateral movement risk. A controlled kill box.

SkorpiOm ran the engagement. Phases A through C. The Wazuh FIM engine didn't fire during Phase C — a lesson logged and not forgotten. No pcaps were captured — another lesson. Wireshark belongs in Phase A from the very first connection. It won't be missed again.

The pentest report was documented. Pushed to GitHub. Krypton1t3's vulnerability as a macOS machine was its last act in that identity.

Then the wipe came. And he became the operator.

By April 24th, Krypton1t3 was hosting his own VMs — Kali Linux and Metasploitable 2 on a libvirt NAT network (`192.168.122.0/24`), fully sandboxed from the physical LAN. The machine that had once been the target was now running the lab.

The containment protocols had become suggestions.

---

## PHASE 9 — THE UPGRADE
### *Fedora 44. April 25, 2026. A late-night decision that paid off clean.*

The upgrade happened late — the kind of session that starts as maintenance and ends as something more.

Fedora 44 released officially on April 28th, but RC 1.7 had been approved as the final build and was available early. The operator ran it anyway.

```bash
sudo dnf upgrade --refresh
sudo dnf install dnf-plugin-system-upgrade
sudo dnf system-upgrade download --releasever=44
dnf5 offline reboot
```

3,141 packages. ~3.2 GiB. One reboot.

The Broadcom BCM4360 driver carried over without fumbling. WiFi came up clean. Twingate required re-authentication — expected, not a problem. The kernel moved to 6.19. The resolution held at 1920×1200 on `eDP-1`. Jam Lab intact. Kdenlive intact. Every tool in place.

**Fedora Security Lab 44.** Clean and painless.

The duality deepened. The machine kept getting stronger.

---

## PHASE 10 — CURRENT STATE
### *A work in progress. That's the point.*

```
KRYPTON1T3 — CURRENT CONFIGURATION
=====================================
Hardware:       MacBook Pro A1398, Mid-2014, 16GB RAM, 256GB SSD
OS:             Fedora Security Lab 44 + Jam Lab (layered)
Kernel:         6.19, PREEMPT_DYNAMIC (preempt=full threadirqs)
WiFi:           Broadcom BCM4360 via broadcom-wl/DKMS
Tailscale:      100.103.171.45
Twingate:       jkgibsonlab.twingate.com ✅

KRYPTSTICK (64GB SanDisk USB 3.0)
  Ventoy:                 1.0.99, grub2 mode forced for Mac hardware
  Ubuntu Studio 24.04.4:  ✅ Boots, persistence configured
  Parrot OS Security 7.1: ✅ Boots, persistence pending (LUKS1)
  SystemRescue:           ⚠️ Dedicated USB required for this hardware

SECURITY
  SELinux:      Enforcing
  Firewalld:    Active, locked down
  SSH:          Tailscale-only, key auth, PermitRootLogin no
  Auto-updates: dnf-automatic enabled

AI STACK
  Ollama:       5 models (DeepSeek-Coder, Mistral, Phi3, Phi4-mini, llama3.2)
  Hermes:       ✅ Operational
  MemPalace:    ✅ 409 drawers (GitHub) + 10,482 drawers (Claude sessions)
  Gemini CLI:   ✅ v0.39.0, MCP connected

VM LAB
  virt-manager:     ✅ Validated
  Kali VM:          ✅ Running (libvirt NAT 192.168.122.0/24)
  Metasploitable 2: ✅ Running (libvirt NAT)

AUDIO/CREATIVE
  Jam Lab:    ✅ Installed
  Low-latency:✅ Configured
  Mixxx:      ✅ Available
  Kdenlive:   ✅ Available

SSH MESH
  EagleEye11:       ✅
  SkorpiOm:         ✅
  Jynx13 (macOS):   ✅
  Jynx13 (Parrot):  ✅
  SolSkorp_13:      ✅ (via Termius)

PENDING
  [ ] Parrot OS encrypted persistence on KryptStick (LUKS1)
  [ ] Twingate re-auth before NY trip + full remote drill
  [ ] Hermes + MemPalace integration test
  [ ] Ubuntu Studio repeat engagement (Wireshark from Phase A)
  [ ] OmniGet batch ingest — pentest screenshots
  [ ] Claude desktop app for Fedora (AppImage / alien investigation)
  [ ] UPS for Burrow power resilience
```

---

## STILL TO COME
### *The story isn't finished. That's the whole point.*

There are chapters not yet written.

The Ubuntu Studio repeat engagement — the one where Wireshark runs from Phase A, the one where pcaps are captured, the one where the Wazuh FIM engine fires the way it should. That engagement will happen. It'll be cleaner, sharper, more documented than the first.

The KryptStick isn't finished either. Parrot OS encrypted persistence with LUKS1 — the same lesson learned the hard way on Jynx13 — is waiting to be executed correctly. The SystemRescue boot issue has a solution: a dedicated 4GB USB. Small problems, clear paths forward.

The Hermes + MemPalace integration. The HexStrike pipeline. The OmniGet ingest. The next pentest — this time from Krypton1t3's own Kali VM, inside his own sandboxed network, the attacker and the infrastructure finally the same machine.

The remote session from New York, verifying that the zero-trust mesh holds from 1,300 miles away.

Krypton1t3 is a work in progress. He was always going to be.

A machine pulled out of a swollen battery and an end-of-life OS. Rebuilt with fishing line and patience. Named after a Joy Division song. Nobody planned for Fedora — Fedora just turned out to be right. The KryptStick wasn't in the original blueprint. Neither was the Jam Lab, the MemPalace with 10,000 drawers, the VM lab, the SSH mesh, or the late-night Fedora 44 upgrade that went perfectly on the first try.

Plans are where you start. The machine decides where you end up.

Chaos is the catalyst. Creation is the result.

---

*Origin file last updated: April 27, 2026*
*The Burrow Home Lab — [github.com/jkgibson-source/cybersecurity-home-lab](https://github.com/jkgibson-source/cybersecurity-home-lab)*
*Operator: SuperSkorp_7 / JBird*

---
*"It's never been done. That means it works. Probably."*
