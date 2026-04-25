# 🦂 The Burrow — Evolution Timeline

_Last Updated: 2026-04-25_

---

## 🧭 Overview

This document captures the evolution of **The Burrow** — a self-built cybersecurity home lab — from a question about a laptop battery to a functioning multi-node offensive/defensive ecosystem.

The lab didn't start with a plan. It started with a refurbished 2010 MacBook Pro and a question: *what can I actually learn on this thing?* The answer turned out to be: quite a lot.

---

## 🧬 Visual Architecture (Current State)

```
                 🦅 EagleEye11
           (SIEM / Control / Ops)
        Mac mini M1 | Kali | 10.0.0.x
                     │
     ┌───────────────┼───────────────┐
     │                               │
🦂 SkorpiOm                    🧠 Krypton1t3
(Offensive / Kali)         (Hybrid / Creative / Hypervisor Host)
MacBook Pro 2010           MacBook Pro 2014 | Fedora Security Lab 44
     │                               │
     └───────────────┬───────────────┘
                     │
                🐾 Jynx13
        (OSINT / Travel Node)
        MacBook Air 2017 | macOS
                     │
                🔥 SuperStick
        (Kali / Parrot / Dragon OS)
      Kingston 128GB | Ventoy 1.0.99
```

---

## 🧭 Phase 0 — Genesis

> *It started with a battery.*

The Burrow began not with a security strategy, but with a hardware refurbishment project. A 2010 MacBook Pro (SkorpiOm) was pulled out of retirement, fitted with a new battery and SSD, and booted into Kali Linux — the first Linux installation for this lab's operator.

From there, the first real challenge was the GPU. The NVIDIA GT 330M conflicted with Kali's nouveau drivers, causing system instability. The fix — disabling GPU acceleration via `LIBGL_ALWAYS_SOFTWARE=1` and `NOUVEAU_NO_ACCEL=1` — was the first lesson in diagnosing Linux hardware conflicts without prior experience.

**Key milestone:** A completely broken machine became a functioning attack platform from scratch, with zero prior Linux experience.

---

## ⚙️ Phase 1 — Visibility Layer

With an attack machine running, the next question was: *how do you know if anything you're doing matters?*

The answer was a SIEM. Splunk Enterprise 10.2.1 was deployed on EagleEye11 (Mac mini M1) on an external Thunderbolt SSD nicknamed "Bird's Nest." A Universal Forwarder was configured on SkorpiOm to ship logs to EagleEye11 over TCP 9997. The first custom dashboard — the **SkorpiOm Security Monitor** — was built to visualize authentication events, network connections, and process activity in real time.

This phase established the lab's core philosophy: every offensive action should be visible somewhere on the defensive side.

---

## 🧪 Phase 2 — Attack Simulation

With visibility in place, it was time to generate something worth seeing.

Metasploitable 2 was deployed in VirtualBox as the first intentionally vulnerable target. Early wins included exploiting **CVE-2011-2523** (vsftpd 2.3.4 backdoor) and **CVE-2010-2075** (UnrealIRCd backdoor) for root shells, followed by harvesting `/etc/shadow`. Nmap was used to enumerate services and validate assumptions about the target's attack surface.

Detection gap analysis came next — cross-referencing what was done offensively against what Splunk actually caught. The gaps were instructive.

**Key insight:** Knowing how to attack something is only half the job. Knowing what the attack *looks like in logs* is what makes you useful in a SOC.

---

## 🧠 Phase 3 — AI Integration

The lab began incorporating local AI inference as a force multiplier.

Ollama was deployed across multiple nodes, running models including `gemma4:e4b`, `deepseek-r1:1.5b`, and SenecaLLM (a cybersecurity-specialized model). **Hermes Agent** — a local AI agent framework by Nous Research — was stood up on EagleEye11 (`Hermes Ops`) and later on Krypton1t3 (`Hermes Forge`), enabling persistent, context-aware AI assistance without sending data to external APIs.

A MetasploitMCP pipeline was also developed: a Python MCP client that communicates with a running `msfrpcd` instance over HTTP, enabling LLM-driven interaction with the Metasploit framework.

**Goal:** Use AI not as a shortcut, but as a reasoning layer — for log analysis, exploit research, and workflow documentation.

---

## 🧬 Phase 4 — Krypton1t3 Hybridization

Krypton1t3 (mid-2014 MacBook Pro A1398) has the most interesting arc of any node in the lab.

It began its life in The Burrow as an **isolated target machine** — segmented onto the `10.0.0.x` subnet at `10.0.0.242`, deliberately excluded from the Tailscale mesh, and used as a passive subject for attack exercises while still running macOS.

Then everything changed. With Fedora Security Lab 44 installed as its permanent OS, Krypton1t3 didn't just join the lab — it became the lab's most connected node. Every other machine now holds SSH keys into it via Tailscale. It went from the one machine that couldn't talk to anyone, to the one machine everyone can reach.

Its current role is fully hybrid:

1. **Hypervisor host** — runs a virtual machine hypervisor with an internal Kali VM, meaning it can now *generate* targets rather than just be one
2. **Creative production node** — Fedora Jam Lab for audio production, Kdenlive for video editing
3. **Hermes Forge** — local AI agent instance for lab automation and inference tasks

The arc from deliberate isolation to full mesh integration — and from target to attacker — mirrors the broader journey of the lab itself.

The hybridization of security and creative tools on a single machine also reflects the operator's background: a 25-year career in professional acrobatics and circus arts, now pivoting into cybersecurity.

---

## 🧳 Phase 5 — Mobility Layer

The lab needed to travel.

**Jynx13** (MacBook Air 2017, macOS) was configured as an OSINT and mobile node, running theHarvester, nmap, whois, and exiftool via Homebrew. SSH access to the lab via Termius over Tailscale was tested and confirmed from Orlando — a live demonstration of the mesh network functioning across geographic distance.

**SuperStick** — a Kingston DataTraveler SE9 G3 128GB USB — was built using Ventoy 1.0.99 as a multi-boot toolkit carrying Kali, Parrot OS, Dragon OS, and a shared Ollama model vault. A successful 32GB practice run validated the approach before the full build.

---

## 🌐 Phase 6 — Network Cohesion

With multiple nodes across multiple locations, network architecture became critical.

A Netgear Nighthawk RS100 router was deployed to restructure the lab network onto a dedicated `10.0.0.x` subnet. **Tailscale** was installed across SkorpiOm, EagleEye11, Jynx13, and mobile nodes to create a persistent encrypted mesh. DNS conflicts on SkorpiOm were resolved by locking `/etc/resolv.conf` to `8.8.8.8` via `chattr +i` and setting `--accept-dns=false` at the Tailscale client level.

**Twingate** handles authenticated remote access to lab resources, with a connector running via Docker on EagleEye11. Remote access to the Splunk dashboard from outside the network was confirmed working.

---

## 🧩 Phase 7 — Operational Refinement

With the lab functional, attention shifted to how it's *used*.

Browser hardening, workflow-based role separation across nodes, and intentional minimalism in tooling became priorities. The principle: don't install something unless you can explain what it does and why it's there. OpenClaw was evaluated and declined due to active CVE exposure. The Axios supply chain attack (versions 1.14.1 / 0.30.4) was investigated and a Splunk detection query was written for the lab environment.

This phase is ongoing. The Burrow is not a finished product — it's a living system.

---

## 🧠 Core Philosophy

> Not perfect isolation — but intentional control.

Every node has a role. Every tool has a reason. Every attack has a corresponding log entry somewhere. The lab exists not to simulate a professional environment, but to *build the instincts* needed to work in one.

---

## 🚀 Forward Trajectory

- **Ncrack credential attack exercise** → Metasploitable 2 SSH → Splunk auth log ingestion → GitHub portfolio write-up
- **MetasploitMCP full pipeline** → LLM-driven recon and exploitation workflow
- **SuperStick Ollama vault** → on-device inference without internet dependency
- **Krypton1t3 permanent OS install** → Fedora Security Lab 44, live pentest target
- **Certifications in progress** → CompTIA Security+, Splunk Core Certified User

---

## 🏁 Summary

The Burrow has evolved from a single refurbished laptop into a **modular, adaptive ecosystem** combining:

- Offensive capability (SkorpiOm, SuperStick)
- Defensive visibility (EagleEye11, Splunk)
- Live target infrastructure (Krypton1t3)
- OSINT and mobility (Jynx13)
- AI-assisted operations (Hermes, Ollama, MetasploitMCP)
- Remote access and mesh networking (Tailscale, Twingate)

Built entirely from refurbished consumer hardware. Documented from day one. Started with a battery replacement and a question about Kali Linux.
