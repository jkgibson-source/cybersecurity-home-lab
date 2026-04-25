# 🦂 The Burrow — Architecture Diagram

_Last Updated: 2026-04-25_

> **A modular cybersecurity, creative, and AI-assisted lab ecosystem built around intentional role separation, controlled flexibility, and iterative growth.**

---

## 🧬 Current System Architecture

```mermaid
flowchart TD
    EE11["🦅 EagleEye11<br/>SIEM / Control / Ops<br/>Splunk • Wazuh • Twingate • Hermes Ops"]
    SKORP["🦂 SkorpiOm<br/>Dedicated Offensive Node<br/>Kali Linux"]
    KRYPT["🧠 Krypton1t3<br/>Hybrid Workstation<br/>Fedora Security Lab • Jam Lab • Kdenlive • Hermes Forge"]
    JYNX["🐾 Jynx13<br/>Mobile OSINT Node<br/>2017 MacBook Air<br/>theHarvester • Sherlock • exiftool • nmap"]
    STICK["🔥 SuperStick<br/>Portable Multi-Boot Toolkit<br/>Kali • Parrot • DragonOS<br/>Encrypted Persistence"]

    EE11 <--> SKORP
    EE11 <--> KRYPT
    EE11 <--> JYNX

    SKORP --> KRYPT
    JYNX --> STICK
    STICK --> JYNX

    KRYPT -. creative + lab crossover .-> EE11
```

---

## 🧭 Node Roles

| Node | Primary Role | Secondary Role | Identity |
|---|---|---|---|
| 🦅 EagleEye11 | Monitoring / SIEM / Control | Ops coordination | Visibility layer |
| 🦂 SkorpiOm | Offensive testing | Dedicated Kali box | Attack platform |
| 🧠 Krypton1t3 | Hybrid Fedora workstation | Creative production + lab work | Execution + creation |
| 🐾 Jynx13 | OSINT / mobile recon | Travel system | Portable intelligence node |
| 🔥 SuperStick | Multi-boot field toolkit | Encrypted persistence | Adaptive deployment layer |

---

## 🧠 Functional Layers

```mermaid
flowchart LR
    A["Recon / OSINT<br/>Jynx13 + SuperStick"] --> B["Offensive Testing<br/>SkorpiOm"]
    B --> C["Target / Hybrid Execution<br/>Krypton1t3"]
    C --> D["Detection + Logging<br/>EagleEye11"]
    D --> E["Analysis + Reporting<br/>Hermes Ops / Hermes Forge"]
    E --> A
```

---

## 🧩 Design Philosophy

The Burrow is not designed around perfect isolation.  
It is designed around **intentional control**.

Core principles:

- Separate roles where separation matters.
- Allow hybrid use where flexibility adds value.
- Keep dedicated offensive capability isolated.
- Maintain visibility through SIEM and logging.
- Use AI as an augmentation layer, not a replacement for judgment.
- Document the system as it evolves.

---

## 🧬 System Identity

> **The Burrow is a living lab ecosystem: part cybersecurity range, part creative workstation environment, part AI-assisted research platform.**

---

## 🔗 Related Documents

- Burrow Evolution Timeline (see /architecture/burrow_evolution_timeline_c.md)
