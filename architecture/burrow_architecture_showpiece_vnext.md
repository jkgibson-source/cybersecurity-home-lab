# 🦂 The Burrow — Lab Architecture vNext

![The Burrow Architecture](../../assets/diagrams/burrow_architecture_showpiece_vnext.svg)

## Core Philosophy

> Separation of roles = clarity of signal.

The Burrow is a multi-node cybersecurity home lab designed around clear operational boundaries: observation, attack, detection, target behavior, and future RF/SIGINT expansion.

## Architecture Roles

| Node | Role | Purpose |
|---|---|---|
| **EagleEye11** | Hermes Ops / SIEM Core | Splunk, Wazuh, Twingate, detection engineering, analysis |
| **Krypton1t3** | Hermes Forge / Target | Experimental host, target system, behavioral validation |
| **SkorpiOm** | Primary Attacker | Kali-based attack platform for controlled engagements |
| **Jynx13** | SuperStick Mobile Node | OSINT, anonymous recon, mobile attacker mode, future RF mode |

## Jynx13 Mode Map

| Mode | Function |
|---|---|
| **macOS** | Clean OSINT, research, documentation |
| **Parrot OS** | Privacy-focused / anonymous OSINT |
| **Kali** | Persistent mobile attacker mode |
| **Dragon OS** | Future RF / SDR / signal-analysis layer |

## Operational Flow

```text
SkorpiOm ──────────────► Krypton1t3 ──────────────► EagleEye11
Primary attacks          Target behavior            Logs / telemetry

Jynx13 Kali ───────────► Krypton1t3
Mobile field attacks

Jynx13 macOS/Parrot ───► SkorpiOm
OSINT enrichment

Jynx13 Dragon OS ──────► EagleEye11
Future RF / SDR evidence path
```

## Evolution Timeline

| Version | Milestone |
|---|---|
| **v0** | Single-machine learning and tooling |
| **v1** | SkorpiOm vs Krypton1t3 attack/target pairing |
| **v2** | EagleEye11 SIEM integration with Splunk/Wazuh |
| **v3** | Jynx13 SuperStick multi-boot platform |
| **vNext** | Dragon OS + RTL-SDR / RF telemetry expansion |

---

*The Burrow — built for deliberate practice, clean signal, and portfolio-ready storytelling.* 🦂
