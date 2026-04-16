# 🦂 The Burrow -- Krypton1t3 Pentest Runbook (v3 -- Portfolio Edition)

**Author:** JBird (James Gibson)  
**Lab:** The Burrow Cybersecurity Lab  
**Engagement Type:** Multi-Phase Adversary Simulation  
**Target:** Krypton1t3 (macOS)  
**Date:** April 2026  

---

## 🎯 Executive Summary

This engagement simulates a real-world adversary targeting a macOS system using OSINT-driven reconnaissance, structured exploitation attempts, and adaptive evasion techniques.

The objective is to evaluate:
- Detection capability across **Splunk (SIEM)** and **Netgear Armor**
- Differences between **baseline and protected environments**
- The impact of **attacker behavior on detection visibility**

---

## 🧭 Lab Architecture

| Role | System | Function |
|------|--------|----------|
| Attacker | SkorpiOm (Kali Linux) | Offensive operations |
| Target | Krypton1t3 (macOS) | Attack surface |
| SIEM | EagleEye11 (Splunk) | Log aggregation |
| SOC | Jynx13 (Parrot OS) | Remote observation |
| Defense | Netgear Armor | Endpoint/network protection |

---

# 🗓️ Phase 0 — OSINT & Hypothesis Building

## 🔎 Tools Used
- Sherlock
- theHarvester
- whois / nslookup
- exiftool

## 🧠 Objective
Transform raw OSINT into actionable attack hypotheses.

## 📝 Key Output
- Username reuse patterns  
- Email formats  
- Potential exposed services  

## 🎯 Result
Defined initial attack vectors:
- VNC (5900)
- CUPS (631)

---

# 🗓️ Phase A — Baseline Attack (No Defense)

## 🔍 Reconnaissance
```bash
nmap -sS -p- -T4 <target_ip>
```

## 🔎 Enumeration
```bash
nmap -sV -p 5900,631 <target_ip>
```

## ⚔️ Exploitation
- Controlled authentication attempts (VNC)
- Service vulnerability analysis (CUPS)

## 📡 Detection Observations

| Action | Splunk | Armor |
|--------|--------|--------|
| Scan | Detected | None |
| Enumeration | Detected | None |
| Exploitation | Detected | N/A |

---

# 🛡️ Phase B — Defensive Validation (Armor Enabled)

## 🔁 Methodology
Repeat identical attack sequence.

## 📊 Observations

| Action | Splunk | Armor |
|--------|--------|--------|
| Scan | Detected | Partial |
| VNC Probe | Detected | Alert |
| Exploitation | Detected | Blocked |

---

# 🧪 Phase C — Evasion Testing (Enhanced)

## ⚙️ Techniques

### Slow Scan
```bash
nmap -sS -T2 -p- <target_ip>
```

### Targeted Scan
```bash
nmap -p 5900 <target_ip>
```

### Behavioral Adjustments
- Reduced scan scope  
- Increased delay  
- Credential-based access simulation  

---

### 🥷 Tor-Based Traffic Obfuscation (AnonSurf Test)

> Controlled evaluation of Tor-routed traffic as an evasion variable.

#### ⚙️ Execution
```bash
sudo anonsurf start
curl ifconfig.me
```

#### 🧪 Test Actions
```bash
nmap -p 5900 <target_ip>
nmap -sS -T2 -p- <target_ip>
nmap -sV -p 5900,631 <target_ip>
```

#### 🛑 Clean Shutdown
```bash
sudo anonsurf stop
sudo systemctl restart NetworkManager
sudo dhclient -v wlan0
```

---

## 📉 Evasion Results

| Technique | Splunk Detection | Armor Detection | Reliability | Key Insight |
|----------|-----------------|-----------------|------------|------------|
| Slow Scan | Reduced | Reduced | High | Threshold detection |
| Targeted Scan | Minimal | Minimal | High | Low-noise effective |
| Credential Use | Low | Low | High | Realistic behavior |
| Tor (AnonSurf) Scan | TBD | TBD | Variable | Compare Tor visibility |
| Tor + Slow Scan | TBD | TBD | Variable | Combined evasion effects |

---

## 🧪 Tor vs Behavioral Evasion Analysis

### Key Questions
- Does Tor increase detection?
- Are exit nodes flagged?
- Does anonymity reduce effectiveness?

### Hypothesis
- Behavioral evasion is more effective
- Tor may increase detectability

---

# 🧠 Detection Analysis

## Key Findings
- Detection is partially threshold-based
- Reduced noise lowers alerting
- Behavior impacts visibility more than tools

---

# 🧬 MITRE ATT&CK Mapping

| Phase | Technique |
|------|----------|
| Recon | T1595 Active Scanning |
| Enumeration | T1046 Network Service Discovery |
| Exploitation | T1078 Valid Accounts |
| Evasion | T1027 Obfuscated/Reduced Signals |
| C2 / Obfuscation | T1090 Proxy / Tor Routing |

---

# 📊 Final Assessment

- Splunk = High visibility, no prevention  
- Armor = Partial prevention  
- Combined = Best coverage  
- Evasion significantly reduces detection fidelity  

---

# 🦂 Conclusion

This engagement demonstrates:

> Detection systems are influenced directly by attacker behavior.

Behavioral evasion proved more reliable than heavy anonymization, while Tor-based routing introduced both variability and potential detectability.

---

## 🧠 Operator Takeaways

- OSINT drives effective attacks  
- Detection ≠ prevention  
- Behavior > tools  
- Multi-layer monitoring is essential  
- Anonymity can increase detection if misused  

---

🦂 The Burrow — Where Offense Meets Defense
