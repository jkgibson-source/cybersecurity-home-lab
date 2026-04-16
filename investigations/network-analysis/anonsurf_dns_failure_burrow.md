# 🦂 The Burrow | Network Investigation  
## 🌐 AnonSurf-Induced DNS Failure in Parrot OS (Live + Persistence)

---

### 🧾 Overview

This investigation documents a network connectivity failure encountered on **Jynx13**, a 2017 MacBook Air running **Parrot OS Live with encrypted persistence**, after attempting to use **AnonSurf** for traffic anonymization.

The system retained partial network functionality (LAN access), but lost the ability to resolve or reach external hosts.

---

### 🎯 Objective

- Identify the root cause of lost internet connectivity  
- Restore full network functionality  
- Analyze the impact of anonymization tooling on system networking  
- Document findings for future operational awareness  

---

### 🖥️ Environment

| Component        | Details |
|----------------|--------|
| Host System     | Jynx13 (MacBook Air 2017) |
| OS             | Parrot OS Live (Encrypted Persistence) |
| Network Type   | Wi-Fi (Broadcom driver manually installed) |
| Router         | 10.0.0.1 |
| Tools Involved | AnonSurf (Tor-based traffic redirection) |

---

### ⚠️ Initial Symptoms

- ✅ Connected to Wi-Fi network  
- ✅ Able to ping external IPs (e.g., `8.8.8.8`)  
- ❌ Unable to resolve domain names (`ping google.com` failed)  
- ❌ Browser unable to reach websites  
- ❌ `sudo apt update` failed  

---

### 🔍 Diagnostic Process

#### 1. Confirm Network Reachability

```bash
ping 8.8.8.8
```

✔ Result: Success  

---

#### 2. Test DNS Resolution

```bash
ping google.com
```

❌ Result: Failure  

---

#### 3. Reset AnonSurf State

```bash
sudo anonsurf stop
sudo systemctl restart NetworkManager
```

---

#### 4. Check Firewall / NAT Rules

```bash
sudo iptables -t nat -L
```

✔ No lingering REDIRECT rules  

---

#### 5. Inspect DNS Configuration

```bash
cat /etc/resolv.conf
```

❌ Misconfigured resolver detected  

---

### 🛠️ Remediation

```bash
sudo nano /etc/resolv.conf
```

```
nameserver 8.8.8.8
nameserver 1.1.1.1
```

---

### ✅ Verification

```bash
ping google.com
sudo apt update
```

✔ Full connectivity restored  

---

### 🧠 Root Cause Analysis

**Residual DNS misconfiguration following AnonSurf usage**

- DNS routing modified for anonymity
- Resolver not restored after shutdown
- Result: External routing intact, DNS broken

---

### 🧬 MITRE ATT&CK Mapping

This scenario aligns with behaviors seen in adversarial tradecraft:

| Tactic | Technique | ID | Relevance |
|------|----------|----|----------|
| Command and Control | Application Layer Protocol | T1071 | Use of Tor for obfuscated communication |
| Command and Control | Proxy | T1090 | Traffic redirection through anonymization layers |
| Defense Evasion | Impair Defenses | T1562 | Disruption of normal DNS resolution |
| Discovery | Network Service Discovery | T1046 | Diagnostic ping/DNS testing mirrors recon behavior |

---

### 🔐 Security Insight

- Misconfigured anonymization can break infrastructure  
- DNS failures are a key detection signal  
- Split functionality (IP works, DNS fails) is a known anomaly pattern  

---

### 🧪 Key Takeaways

- Validate IP connectivity before DNS assumptions  
- Anonymization tools can leave persistent artifacts  
- Live OS environments increase misconfiguration risk  
- Manual DNS override is a reliable recovery method  

---

### 🦂 Burrow Relevance

Demonstrates:

- Real-world troubleshooting methodology  
- Understanding of layered networking  
- Practical interaction with red-team tooling side effects  
- Portfolio-grade documentation discipline  

---

### 🚀 Future Enhancements

- Automate DNS reset post-AnonSurf  
- Capture packet traces during failure  
- Compare Tor vs VPN behavior  
- Integrate into pentest scenario as failure simulation  

---

### 🏁 Conclusion

A DNS misconfiguration introduced during anonymized routing caused selective network failure.  

Restoring resolver configuration resolved the issue and reinforced the importance of layered diagnostics.

---

🦂 *The Burrow — Where Offense Meets Defense*
