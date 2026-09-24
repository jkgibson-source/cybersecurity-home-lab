# 🔐 Cybersecurity Home Lab

**The Burrow** is a multi-node purple-team home lab where I run end-to-end
offensive, defensive, and forensic operations on refurbished hardware and
infrastructure I built from scratch: penetration testing, detection
engineering, SIEM and EDR pipelines, digital forensics, OSINT, and
AI-assisted security tooling.

Every node has a defined role. Every action is logged and analyzed. Every
finding gets documented.

> **Where the lab stands now:** what began as a single Kali laptop and a Splunk
> box has grown into a segmented mesh of four core machines, a fleet of
> portable boot drives (USB sticks and SSDs) each carrying its own operating
> system, a Tailscale overlay with a Reticulum backup path, and a council of
> node-bound AI assistants. This README reflects that current state.

---

## 🦂 The Burrow — Architecture

![The Burrow Architecture](./assets/diagrams/burrow_architecture_vnext.svg)

A segmented multi-node environment built to simulate real-world attack,
detection, and analysis workflows, with clear separation of roles and clean
telemetry across every operation.

### Core Machines
- 🦂 **SkorpiOm** (Kali Linux) - Offensive Operations, primary attacker
- 🦅 **EagleEye11** (macOS + Fedora Asahi Remix, dual-boot) - SIEM, detection, and lab hub
- 🎏 **Jynx13** (macOS Monterey) - OSINT, reconnaissance, and travel/field node
- 🧪 **Krypton1t3** (Fedora 45 Beta) - R&D, virtualization, and AI experimentation

### Portable Nodes
A fleet of bootable USB sticks and SSDs, each running its own OS and hosting a
specialized workflow. See [Lab Infrastructure](#️-lab-infrastructure) for the
full roster.

### Operational Flow
`Reconnaissance → Execution → Observation → Evolution`

### Deep Dives
- 🧬 [Burrow Field Guide](./docs/burrow_field_guide.md)
- 🧠 [Agent Directory - the machines and their Digital Assistants](./nodes/README.md)
- 🖥️ [Command Center - physical lab, node roles, and how the architecture maps to real hardware](./architecture/README.md)
- 📜 [Evolution Timeline](./architecture/burrow_evolution_timeline_c.md)
- 🌐 [Network Diagram](./assets/diagrams/the_burrow_network_diagram_april2026.svg)

### Development Workflow
All lab work follows a structured Git workflow for clean version history and
reproducibility. See the [Burrow Git Workflow Standard](./docs/workflows/burrow_git_workflow_standard.md).

---

## 📝 Recent Lab Reports

- **2026-09-23:** [SSK Portable SSD Failure Investigation](./investigations/dfir/report_2026-09-23_SSK-SSD-consolidated.md) - Cross-platform failure evidence and incomplete sanitization assessment
- **2026-09-15–16:** [EagleEye11 - Fedora Asahi Remix Dual-Boot](./builds/journal_2026-09-15_Fedora-Asahi-Remix.md) - Backup recovery, APFS resizing, and Linux on Apple Silicon
- **2026-09-11:** [SpecSticK Windows 11 Restore](./builds/journal_2026-09-11_specstick-win11-restore.md) - Oriel, PAI-OpenCode, Hindsight, and application restoration
- **2026-09-01:** [InterGenOS on Kingston - Birth of Gauge](./builds/report_2026-09-01_Birth-of-Gauge_InterGenOS-installation.md) - Encrypted portable Linux From Scratch with Apple boot chain and Broadcom Wi-Fi troubleshooting
- **2026-07-26:** [EagleEye11 Airborne Recon](./investigations/network-analysis/report_2026-07-26_fly-scan.md) - Remote service enumeration over Tailscale from in-flight Wi-Fi

---

## 📋 Table of Contents

- [Lab Infrastructure](#️-lab-infrastructure)
- [The Council of Digital Assistants](#-the-council-of-digital-assistants)
- [Skills Demonstrated](#️-skills-demonstrated)
- [ATT&CK Coverage](#-attck-coverage)
- [Investigations](#️-investigations)
- [Featured Builds](#-featured-builds)
- [Lab Tooling](#-lab-tooling)
- [Projects](#-projects)
- [Learning Platforms & Coursework](#-learning-platforms--coursework)
- [Certifications](#-certifications)
- [Tools & Technologies](#-tools--technologies)

---

## 🖥️ Lab Infrastructure

### Core Machines

| Machine | Hardware | OS / Role |
| --- | --- | --- |
| **SkorpiOm** | Apple MacBook Pro A1286 (Mid-2010) | Kali Linux (Xfce) - primary offensive / pentesting platform |
| **EagleEye11** | Apple Mac mini M1 (2020) | macOS 27.0 + Fedora Asahi Remix 44 (dual-boot) - lab hub, Wazuh manager, Ollama, Docker, BurrowMCP |
| **Jynx13** | Apple MacBook Air 13" (2017, Intel) | macOS Monterey 12.7.6 - OSINT, travel/field recon, BurrowMCP commander |
| **Krypton1t3** | Apple MacBook Pro A1398 (Mid-2014) | Fedora 45 Beta (Security + Jam Labs) - hybrid AI/R&D workstation, KVM/libvirt |
| **Target VM** | Metasploitable 2 | libvirt/VirtualBox - intentionally vulnerable target |

### Portable Nodes (USB Sticks & SSDs)

Each portable node is a self-contained, bootable environment that runs on the
core Mac hardware. Most boot on both Krypton1t3 and Jynx13.

| Node | Media | OS | Role |
| --- | --- | --- | --- |
| **SpliceStick** | USB (Ventoy) | Ubuntu Studio 26.04 | Creative production and media forensics workstation |
| **FlexStick** | USB (Ventoy) | Parrot OS 7.3 Security Edition | Field ops, recon, and OSINT toolkit |
| **SpecSticK** | SSK portable SSD | Windows 11 Pro (Hasleo WinToUSB) | Windows security internals, Sysmon, AD fundamentals |
| **PQS** | SSK portable SSD | Deepin 25 + EndeavourOS Titan Nova (dual-boot) | AI-forward Linux workstation pair |
| **VAPOR** | USB | Tails OS 7.13 | Privacy, anonymity, and amnesic sessions |
| **burrowforge** | Kingston 128GB USB | InterGenOS (custom Linux From Scratch) | From-scratch build node, encrypted portable Linux |
| **BMV** | PNY 32GB USB | Cross-platform (llama.cpp) | Portable AI model vault, plugs into any node on demand |

> **Naming note:** the retired **SuperStick** and **KryptStick** names have been
> superseded. KryptStick was split into **SpliceStick** and **FlexStick** on
> 2026-06-28; the SuperStick / Kingston lineage produced **SpecSticK** and was
> later rebuilt into the **burrowforge** InterGenOS node.

### Network & Remote Access

| Technology | Purpose | Scope |
| --- | --- | --- |
| **Tailscale** | Primary mesh VPN, encrypted overlay | All core nodes, portable nodes, and mobile fleet |
| **Reticulum (RNS)** | Tailscale-independent backup comms over Cloudflare tunnels | Core nodes |
| **RustDesk** | GUI remote desktop | All nodes (systemd-enabled) |

### Virtualization & Storage

| Component | Details |
| --- | --- |
| **Virtualization** | KVM/libvirt (Krypton1t3), VirtualBox |
| **Bird's Nest** | External SSD on EagleEye11 - Ollama models, Docker, Wazuh data, and the bulk pentest-evidence store |
| **Phoenix** | SkorpiOm's original 500GB HDD, re-housed in the Bird's Nest enclosure |

---

## 🧠 The Council of Digital Assistants

The Burrow's nodes are not treated as interchangeable computers. Each one has a
role, a history, and an operating style. The **Digital Assistants** grow out of
that foundation: node-bound AI companions shaped by the hardware, operating
system, and mission profile of their host. The node is the body; the DA is the
memory, voice, and presence layered on top.

The Council is human-led. It does not make final decisions. It supports memory,
continuity, documentation, and execution across the lab, and it doubles as the
teaching cast for [**The Net**](https://thenet.miami), my free youth
cybersecurity and digital literacy program, where each DA owns a "block" in a
digital neighborhood the students explore.

The roster spans twelve DAs, but the hardware sets the ceiling: the Council runs
on four physical host machines, so at most four DAs are ever active at once, and
any two DAs that share one body (a dual-boot machine or a dual-boot drive) can
never be awake at the same time.

**The full roster and each DA's role lives in the [Agent Directory](./nodes/README.md).**

---

## 🛠️ Skills Demonstrated

### 🏆 Headline Wins

- 🦂 **macOS endpoint-monitoring architectural finding** - Documented how TCC and SIP defeat endpoint monitoring agents at the OS boundary; multi-phase purple-team writeup
- 🌐 **Real-time exploitation detection** - Built a cross-machine SIEM pipeline (Kali → Splunk via TCP 9997) and detected active exploitation in real time through a custom monitoring dashboard
- 🔥 **Full kill chain captured end-to-end** - Chained UnrealIRCd (CVE-2010-2075) and vsftpd (CVE-2011-2523) to root on Metasploitable, captured the entire attack at the packet level via Wireshark, and reconstructed the unencrypted shell session via TCP stream follow
- 🤖 **AI-assisted red team plumbing** - Integrated Metasploit with local LLMs via MCP (MetasploitMCP in HTTP/SSE + Ollama) to build the rails for agentic offensive operations
- 🛡️ **Custom lab infrastructure from scratch** - Built BurrowMCP (SSH-based remote tooling across every node), a Wazuh SIEM/EDR deployment, and a self-compiled Linux From Scratch node (InterGenOS)
- 👊 **Active incident response** - Multiple same-day CVE engagements documented (Dirty Frag chained CVEs, Copy.Fail, and others)

### Offensive Security

* Identified and exploited CVE-2010-2075 (UnrealIRCd backdoor)
* Identified and exploited vsftpd 2.3.4 backdoor (CVE-2011-2523)
* Post-exploitation enumeration (privilege escalation, credential harvesting)
* Password hash extraction from `/etc/shadow` and offline cracking
* Vulnerability scanning with Nmap, Nessus, and OpenVAS/Greenbone
* Exploitation with Metasploit Framework

### OSINT

* Email and domain reconnaissance with theHarvester
* Network scanning with Nmap
* Username enumeration across platforms with Sherlock
* Image metadata analysis with ExifTool

### Network Analysis

* Unencrypted shell traffic capture and reconstruction via TCP stream follow
* Packet capture and analysis with Wireshark
* TCP/IP protocol analysis (SYN, ACK, PSH, RST flags)
* TCP three-way handshake analysis
* DNS traffic analysis

### SIEM, Detection & EDR

* Deployed Wazuh manager (EagleEye11) with agents across all core nodes for detection and file-integrity monitoring
* Detected active exploitation in real time via netstat and process monitoring
* Built cross-machine log pipeline (Kali → Splunk via TCP 9997) and a real-time security dashboard
* Deployed Splunk Enterprise on Apple Silicon (M1) and configured Universal Forwarders
* Installed and configured the Splunk Add-on for Unix and Linux

### Digital Forensics

* iOS device forensics using libimobiledevice
* Full device backup and artifact extraction from Apple iPhone 5 and iPhone 7
* Timeline analysis of mobile device data
* Safari browsing history extraction via SHA1-hashed plist analysis
* SQLite database analysis with sqlitebrowser
* Application behavior analysis (network traffic, process monitoring, behavioral baselining)

### AI & Automation

* Built **BurrowMCP**, a custom MCP server giving Claude real-time SSH access to every Burrow node over Tailscale
* Integrated Metasploit Framework with MCP via the MetasploitMCP server (HTTP/SSE mode)
* Deployed local LLM inference with Ollama across multiple machines
* Compiled a portable, cross-platform AI model vault (llama.cpp) that runs on Linux, macOS ARM64/x86_64, and Windows
* Ran a node-bound AI assistant framework (PAI-OpenCode + Hindsight memory) across the mesh

### System Administration

* Hardware refurbishment (battery replacement, HDD → SSD upgrades)
* Kali Linux, Fedora, Ubuntu Studio, Parrot, Deepin, EndeavourOS, and Tails deployment from scratch
* Self-compiled a Linux From Scratch distribution (InterGenOS) with a custom kernel, LUKS2 full-disk encryption, and MOK-signed UEFI boot on Apple hardware
* Dual-boot of Fedora Asahi Remix alongside macOS on Apple Silicon (APFS resize, Recovery-mode partitioning)
* Portable Windows installs (Hasleo WinToUSB) bootable across multiple Macs
* NVIDIA GPU driver troubleshooting (nouveau stabilization); Broadcom BCM4360 Wi-Fi driver debugging across Linux distros
* UFW firewall, SSH hardening, systemd service configuration
* Tailscale mesh deployment and DNS conflict resolution

### Programming & Tooling

* **Python** - Built [Burrow OmniGet](./tools/burrow-omniget/README.md), a modular evidence ingestion pipeline (SQLite backend, JSON sidecars, separate ingest/search/utils modules). Strengthening fundamentals via Harvard CS50P.
* **Bash / PowerShell** - Operational scripting for log triage, forwarder configuration, systemd management, Windows-To-Go maintenance, and shell-based wargames (OverTheWire Bandit).
* **AI-augmented development** - Pair-program with Claude to design, scaffold, and iterate on lab tooling, and integrate LLMs into security workflows via MCP. Working toward fuller independent authorship through structured study and self-directed practice.

---

## 🎯 ATT&CK Coverage

Techniques exercised across pentests, network analysis, and detection work in The Burrow:

- **T1190** - Exploit Public-Facing Application *(UnrealIRCd, vsftpd backdoors)*
- **T1059.004** - Command and Scripting Interpreter: Unix Shell *(post-exploitation sessions)*
- **T1003.008** - OS Credential Dumping: /etc/passwd and /etc/shadow *(Metasploitable root → shadow extraction)*
- **T1110.002** - Brute Force: Password Cracking *(offline hash cracking)*
- **T1040** - Network Sniffing *(Wireshark TCP stream reconstruction)*
- **T1057** - Process Discovery *(post-exploit enumeration; SIEM detection panel)*
- **T1049** - System Network Connections Discovery *(netstat-based monitoring + detection)*

---

## 🕵️‍♂️ Investigations

Explore hands-on cybersecurity investigations conducted in **The Burrow**:

📂 [View All Investigations](./investigations/README.md)

### 🔥 Highlighted Work

- 👊 [Dirty Frag - CVE-2026-43284 & CVE-2026-43500 Incident Response](./investigations/incident-response/CVE-2026-43284_CVE-2026-43500_dirty.frag/README.md) - Active incident response engagement on chained CVEs
- 🦂 [Krypton1t3 macOS Detection Engineering Pentest](./investigations/pentests/krypton1t3-big-sur/README.md) - Multi-phase purple team engagement documenting how macOS TCC and SIP defeat endpoint monitoring agents at the architecture level
- 🤖 [Strix AI Pentest Agent on Krypton1t3](./investigations/ai-research/strix_krypton1t3_report_2026-05-08.md) - Evaluation of an agentic AI pentest tool against a hardened lab target
- 🔍 [Windows 7 Offline Data Recovery (DFIR)](./investigations/dfir/windows7_offline_data_recovery.md) - Offline forensic recovery of user data from a locked legacy system
- 🌐 [Splunk Forwarder Network Incident](./investigations/network-analysis/splunk-forwarder-network-incident/splunk_forwarder_network_segmentation_case_study.md) - Investigation of log forwarding issues and network visibility gaps
- 🛠️ [OpenVAS vs Nessus Scanner Comparison](./investigations/vulnerability-research/scanner_comparison_openvas_vs_nessus.md) - Comparative analysis of vulnerability scanning tools in a lab environment

---

## 🔧 Featured Builds

📂 [View All Builds](./builds/README.md)

- [InterGenOS on Kingston - Birth of Gauge](./builds/report_2026-09-01_Birth-of-Gauge_InterGenOS-installation.md)
- [EagleEye11 Fedora Asahi Remix Dual-Boot](./builds/journal_2026-09-15_Fedora-Asahi-Remix.md)
- [SpecSticK Windows 11 Restore](./builds/journal_2026-09-11_specstick-win11-restore.md)
- [The Kingston - Portable AI Model Vault](./builds/builds_2026-07-12_the-Kingston.md)
- [KryptStick Split - Birth of Flex](./builds/FieldJournal_2026-06-28_KryptStickSplit_BirthOfFlex.md)
- [Claude Desktop for Linux + Metasploit MCP Pipeline](./builds/claude_desktop_metasploit_b.md)
- [Hermes Forge Local AI Deployment](./builds/hermes_forge_krypton1t3.md)
- [Wazuh Deployment Case Study](./builds/wazuh_portfolio_case_study.md)
- [Krypton1t3 OS Migration Report](./builds/Krypton1t3_Migration_Report_e.md)

---

## 🧰 Lab Tooling

Custom tools built to support lab operations.

- [Burrow OmniGet](./tools/burrow-omniget/README.md) - local evidence ingestion pipeline for screenshots, artifacts, and analyst notes; SQLite-backed with JSON sidecars, designed to feed a future search + correlation + LLM analyst layer
- [BurrowMCP](./tools/BurrowMCP/README.md) - custom MCP server and mobile-first web dashboard for remote lab management; gives Claude real-time SSH access to all core nodes over Tailscale

---

## 📁 Projects

### 1. Home Lab Build

**Status:** ✅ Complete

Refurbished a 2010 MacBook Pro with a new battery and SSD, installed Kali
Linux, and configured it as a dedicated penetration testing machine. Resolved
system instability caused by the NVIDIA nouveau driver by disabling GPU
acceleration. That first machine became the seed the rest of the lab grew from.

**Tools:** Kali Linux, Xfce, VirtualBox

---

### 2. Metasploitable 2 — Penetration Test

**Status:** ✅ Complete

Set up Metasploitable 2 as a vulnerable target VM and conducted a full
penetration test using Metasploit Framework. Successfully exploited two
separate vulnerabilities to gain root access.

**Attack Chain:**

1. Network reconnaissance with Nmap (-sV service version detection)
2. Identified 23 open ports and multiple vulnerable services
3. Exploited UnrealIRCd backdoor (CVE-2010-2075) via Metasploit → root shell
4. Exploited vsftpd 2.3.4 backdoor (CVE-2011-2523) via Metasploit → root shell
5. Post-exploitation: enumerated users, processes, and harvested `/etc/shadow`
6. Extracted and cracked password hashes offline

**Tools:** Nmap, Metasploit Framework, Netcat

---

### 3. Network Traffic Analysis

**Status:** ✅ Complete

Captured and analyzed live network traffic during a penetration test using
Wireshark. Observed the complete attack chain at the packet level including TCP
handshakes, exploit delivery, and shell session traffic.

**Key Findings:**

* Captured SYN/ACK handshakes during Nmap port scanning
* Identified exploit traffic on port 6667 (IRC)
* Reconstructed unencrypted shell session via TCP stream follow
* Demonstrated why encrypted channels (SSH) are critical for secure communications

**Tools:** Wireshark, Nmap, Metasploit Framework

---

### 4. Splunk SIEM Deployment

**Status:** ✅ Complete

Designed and deployed a functional SIEM pipeline across two machines.
Configured real-time log collection, forwarding, and monitoring. Built a custom
security dashboard and successfully detected an active exploitation attempt in
real time. (The lab has since moved to Wazuh as its primary detection layer;
this deployment remains documented as foundational SIEM work.)

**Architecture:**

```
Kali Linux (Attack Machine)
    ↓ Splunk Universal Forwarder
    ↓ TCP port 9997
Splunk Enterprise (Mac mini M1)
    ↓ index=main
Security Monitor Dashboard
```

**Tools:** Splunk Enterprise, Splunk Universal Forwarder, Splunk Add-on for Unix and Linux

---

### 5. iOS Digital Forensics

**Status:** ✅ Complete

Conducted forensic analysis of two Apple iOS devices using libimobiledevice.
Performed full device backups and extracted artifacts for timeline analysis.
Extracted and analyzed Safari browsing history from SHA1-hashed plist files,
queried SQLite databases directly, and reconstructed user activity timelines.

**Devices:** Apple iPhone 5, Apple iPhone 7

**Tools:** libimobiledevice, plistutil, sqlitebrowser, Kali Linux

---

### 6. Application Behavioral Analysis — Pi Network Node

**Status:** ✅ Complete

Prior to decommissioning a Pi Network Node installation on the lab hub,
conducted a detailed behavioral examination of the application. Monitored
network connections, active processes, and system resource usage to document
and understand the software's runtime behavior before removal.

**Tools:** Splunk, netstat, ps, Kali Linux

---

### 7. AI-Assisted Red Team Pipeline

**Status:** 🔄 In Progress

Building an autonomous AI-assisted red team pipeline integrating a local LLM
(via Ollama), Metasploit Framework (via MetasploitMCP), and detection tooling
for kill-chain monitoring. MetasploitMCP is deployed on the attack machine in
HTTP/SSE mode, enabling AI-driven tool invocation against lab targets.

**Architecture (target state):**

```
Ollama (local LLM)
    ↓ MCP client
MetasploitMCP (HTTP/SSE)
    ↓ Metasploit Framework
Metasploitable 2 (target)
    ↓ logs
Detection layer (Wazuh / Splunk)
```

**Tools:** Ollama, MetasploitMCP, Metasploit Framework, Python

---

### 8. BurrowMCP — Custom MCP Server & Lab Dashboard

**Status:** ✅ Live

A custom MCP server and mobile-first web dashboard built from scratch for
remote lab management. Gives Claude real-time SSH access to the Burrow's core
nodes over Tailscale. Two modes: an MCP server for Claude Desktop/iOS, and a
standalone web dashboard for phone-based control with no AI session required.

→ **[Full documentation and build log](tools/BurrowMCP/README.md)**

**Tools:** Python, Starlette, Tailscale, Cloudflare Tunnel, Wazuh, SSH

---

## 📚 Learning Platforms & Coursework

* [Harvard CS50P](https://cs50.harvard.edu/python) - Python (in progress)
* [OverTheWire Wargames](https://overthewire.org) - Bandit (in progress)
* [LabEx](https://labex.io) - Linux fundamentals
* [TryHackMe](https://tryhackme.com)

---

## 🎯 Certifications

### Completed

* ✅ **ISC2 Certified in Cybersecurity (CC)**
* ✅ **Google Cybersecurity Professional Certificate** *(Coursera)*

### Planned

* 📚 CompTIA Security+
* 📚 Splunk Core Certified User

---

## 📊 Tools & Technologies

[![Kali Linux](https://img.shields.io/badge/Kali_Linux-557C94?style=flat&logo=kali-linux&logoColor=white)](https://www.kali.org)
[![Wazuh](https://img.shields.io/badge/Wazuh-3EBFED?style=flat&logoColor=white)](https://wazuh.com)
[![Splunk](https://img.shields.io/badge/Splunk-000000?style=flat&logo=splunk&logoColor=white)](https://www.splunk.com)
[![Wireshark](https://img.shields.io/badge/Wireshark-1679A7?style=flat&logo=wireshark&logoColor=white)](https://www.wireshark.org)
[![Metasploit](https://img.shields.io/badge/Metasploit-E34F26?style=flat&logo=metasploit&logoColor=white)](https://www.metasploit.com)
[![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat&logo=linux&logoColor=black)](https://www.kernel.org)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Ollama](https://img.shields.io/badge/Ollama-000000?style=flat&logoColor=white)](https://ollama.com)

---

### About this repository

*This lab is for educational purposes only. All testing is performed on intentionally vulnerable systems in an isolated environment.*

*Reports and documentation are drafted with AI writing assistance (Claude). All technical work, findings, and analysis reflect my own lab environment and hands-on research.*

---

# 🦾 THE BURROW
