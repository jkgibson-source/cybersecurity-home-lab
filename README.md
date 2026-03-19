# 🔐 Cybersecurity Home Lab

A self-built cybersecurity home lab documenting my journey from hardware 
refurbishment to penetration testing, digital forensics, network analysis, 
and SIEM monitoring. Built and maintained by a self-taught security 
enthusiast transitioning into the cybersecurity field.

---

## 🖥️ Lab Infrastructure

| Component | Details |
|-----------|---------|
| **Attack Machine** | Apple MacBook Pro A1286 Mid-2010 |
| **OS** | Kali Linux (Xfce desktop) |
| **Storage** | Fikwot FX815 SSD (self-installed) |
| **Virtualization** | VirtualBox |
| **Target Machine** | Metasploitable 2 (VM) |
| **SIEM** | Splunk Enterprise 10.2.1 |
| **SIEM Hardware** | Apple Mac mini M1 (2020) |
| **VPN** | ProtonVPN |
| **Mobile Forensics** | libimobiledevice |

---

## 🛠️ Skills Demonstrated

### Offensive Security
- Vulnerability scanning with Nmap
- Exploitation with Metasploit Framework
- Identified and exploited CVE-2010-2075 (UnrealIRCd backdoor)
- Post-exploitation enumeration (privilege escalation, credential harvesting)

### Network Analysis
- Packet capture and analysis with Wireshark
- TCP/IP protocol analysis (SYN, ACK, PSH, RST flags)
- TCP three-way handshake analysis
- DNS traffic analysis
- Unencrypted shell traffic capture and reconstruction via TCP stream follow

### SIEM & Detection
- Deployed Splunk Enterprise on Apple Silicon (M1)
- Configured Universal Forwarder on Kali Linux
- Built cross-machine log pipeline (Kali → Splunk)
- Installed and configured Splunk Add-on for Unix and Linux
- Built real-time security monitoring dashboard
- Detected active exploitation in real time via netstat and process monitoring

### Digital Forensics
- iOS device forensics using libimobiledevice
- Artifact extraction from Apple iPhone 7
- Timeline analysis of mobile device data

### System Administration
- Hardware refurbishment (battery replacement, HDD → SSD upgrade)
- Kali Linux installation and configuration from scratch
- NVIDIA GPU driver troubleshooting (nouveau driver stabilization)
- UFW firewall configuration
- SSH configuration and management
- systemd service configuration and troubleshooting
- Cross-platform file transfer via SCP

---

## 📁 Projects

### 1. Home Lab Build
**Status:** ✅ Complete

Refurbished a 2010 MacBook Pro with a new battery and SSD, installed 
Kali Linux, and configured it as a dedicated penetration testing machine. 
Resolved system instability caused by NVIDIA nouveau driver by disabling 
GPU acceleration.

**Tools:** Kali Linux, Xfce, VirtualBox, ProtonVPN

---

### 2. Metasploitable 2 — Penetration Test
**Status:** ✅ Complete

Set up Metasploitable 2 as a vulnerable target VM and conducted a 
penetration test using Metasploit Framework. Successfully exploited 
CVE-2010-2075 (UnrealIRCd 3.2.8.1 backdoor) to gain a root shell.

**Attack Chain:**
1. Network reconnaissance with Nmap (-sV service version detection)
2. Identified 23 open ports and vulnerable services
3. Exploited UnrealIRCd backdoor via Metasploit
4. Gained root shell on target
5. Post-exploitation: enumerated users, processes, and harvested /etc/shadow

**Tools:** Nmap, Metasploit Framework, Netcat

---

### 3. Network Traffic Analysis
**Status:** ✅ Complete

Captured and analyzed live network traffic during a penetration test 
using Wireshark. Observed the complete attack chain at the packet level 
including TCP handshakes, exploit delivery, and shell session traffic.

**Key Findings:**
- Captured SYN/ACK handshakes during Nmap port scanning
- Identified exploit traffic on port 6667 (IRC)
- Reconstructed unencrypted shell session via TCP stream follow
- Demonstrated why encrypted channels (SSH) are critical for secure communications

**Tools:** Wireshark, Nmap, Metasploit Framework

---

### 4. Splunk SIEM Deployment
**Status:** ✅ Complete

Designed and deployed a functional SIEM pipeline across two machines. 
Configured real-time log collection, forwarding, and monitoring. Built 
a custom security dashboard and successfully detected an active 
exploitation attempt in real time.

**Architecture:**
```
Kali Linux (SkorpiOm)
    ↓ Splunk Universal Forwarder
    ↓ TCP port 9997
Splunk Enterprise (Mac mini M1)
    ↓ index=main
SkorpiOm Security Monitor Dashboard
```

**Dashboard Panels:**
- Active Network Connections (netstat)
- Open Ports Monitor (openPorts)
- Running Processes (ps)
- Command History (bash_history)

**Tools:** Splunk Enterprise 10.2.1, Splunk Universal Forwarder, 
Splunk Add-on for Unix and Linux

---

### 5. iOS Digital Forensics
**Status:** ✅ Complete

Conducted forensic analysis of an Apple iPhone 7 using libimobiledevice. 
Extracted and analyzed device artifacts including messages, call logs, 
and application data.

**Tools:** libimobiledevice, Kali Linux

---

## 📚 Learning Platforms
- [TryHackMe](https://tryhackme.com)
- [LabEx](https://labex.io)
- [OverTheWire Wargames](https://overthewire.org)

---

## 🎯 Certifications

### Completed
- ✅ **ISC2 Certified in Cybersecurity (CC)**
- ✅ **Google Cybersecurity Professional Certificate** *(Coursera)*

### In Progress
- 📚 CompTIA Security+ *(planned)*
- 📚 Splunk Core Certified User *(planned)*
  
---

## 📊 Tools & Technologies

![Kali Linux](https://img.shields.io/badge/Kali_Linux-557C94?style=flat&logo=kali-linux&logoColor=white)
![Splunk](https://img.shields.io/badge/Splunk-000000?style=flat&logo=splunk&logoColor=white)
![Wireshark](https://img.shields.io/badge/Wireshark-1679A7?style=flat&logo=wireshark&logoColor=white)
![Metasploit](https://img.shields.io/badge/Metasploit-E34F26?style=flat&logo=metasploit&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat&logo=linux&logoColor=black)
![VirtualBox](https://img.shields.io/badge/VirtualBox-183A61?style=flat&logo=virtualbox&logoColor=white)

---

*This lab is for educational purposes only. All testing is performed 
on intentionally vulnerable systems in an isolated environment.*
