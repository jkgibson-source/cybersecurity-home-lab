# 🦂 The Burrow – Lab Note
## Krypton1t3 Connectivity & Enumeration Sanity Check

**Lab:** Cybersecurity Home Lab (The Burrow)  
**Date:** 2026-04-15  
**Systems:** SkorpiOm (Kali Linux) → Krypton1t3 (macOS)  

---

## 🎯 Purpose
This exercise was conducted to validate network visibility and tool behavior between the attack host and target system **prior to a full penetration test**.

### Goals:
- Confirm host reachability under realistic conditions  
- Observe firewall behavior (ICMP vs TCP)  
- Validate Nmap scan strategies and performance  
- Identify potential early attack surface  

> This is a **pre-engagement validation**, not a full assessment.

---

## 🧪 Scenario

Initial attempt:
```bash
ping <target_ip>
```

### Result:
- ❌ No response from Krypton1t3  
- ✅ Reverse ping (target → attacker) successful  

### Interpretation:
- Host is alive  
- ICMP echo replies are being blocked  

---

## 🔍 Root Cause

Krypton1t3’s firewall is configured to:
- Block ICMP (ping)
- Allow selective TCP traffic

---

## ⚡ Adaptation Strategy

Pivot from ICMP-based discovery to TCP-based enumeration:

```bash
sudo nmap -sS -Pn <target_ip>
```

### Key Adjustment:
- `-Pn` → Treat host as up (bypass ICMP dependency)

---

## 🚀 Scan Optimization

Initial full-port scan proved slow due to dropped packets:

```bash
sudo nmap -sS -p- <target_ip>
```

### Optimized approach:
```bash
sudo nmap -sS -Pn -T4 --top-ports 1000 -v <target_ip>
```

### Outcome:
- Significantly faster results
- Accurate service discovery despite filtering

---

## 🔓 Key Findings

### Open Ports Identified
- 88 (Kerberos)
- 3283 (Apple Remote Desktop)
- 3689 (Bonjour)
- 5900 (VNC)
- 9090 (Unknown/custom service)
- 9503 (Unknown HTTP-like service)
- 49152 (Apple ODS HTTP)

---

## 🧠 Service Insights

### 🔥 High-Interest Services
- **5900 (VNC):** Remote desktop access enabled  
- **9090:** Custom service responding with “WELCOME”  
- **9503:** HTTP-like behavior, possibly misconfigured  

### ⚙️ System Services
- Apple-related services confirm macOS environment
- Some require authentication (lower immediate risk)

---

## 🧬 Notable Behavior

- Firewall **drops packets instead of rejecting them**
- This causes:
  - Increased scan times  
  - Need for timing adjustments (`-T4`, reduced retries)

---

## 🧠 Key Takeaways

- ICMP blocking does not prevent host discovery  
- TCP enumeration remains effective under filtering  
- Scan performance must be tuned to environment  
- Unknown services represent potential attack surface  

---

## 🚀 Next Steps (Planned)

- Manual service probing (`curl`, `nc`)
- Browser interaction with exposed ports
- Integration with:
  - Splunk (logging)
  - Wazuh (detection)
- Transition into structured pentest phases

---

## 🦂 Burrow Insight

> A host that appears invisible to basic discovery techniques may still expose a meaningful attack surface when approached with adaptive enumeration strategies.

