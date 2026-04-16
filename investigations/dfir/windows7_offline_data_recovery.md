# 🦂 The Burrow  
## 🕵️‍♂️ Digital Forensics Case Study  
### Legacy System Data Recovery (Windows 7 Offline Access)

![DFIR](https://img.shields.io/badge/Domain-DFIR-blue)
![Platform](https://img.shields.io/badge/Platform-Windows_7-lightgrey)
![Method](https://img.shields.io/badge/Method-Offline_Recovery-orange)
![Status](https://img.shields.io/badge/Status-Completed-success)

---

## 📌 Overview

This case study documents a real-world **data recovery operation on a legacy Windows 7 system** with restricted access. The objective was to recover user-generated content (photos and videos) without relying on system login credentials, using **offline forensic techniques**.

> ⚖️ **Ethical Note:**  
> All identifying details have been removed to protect privacy. This case study focuses strictly on technical methodology and safe data handling practices.

---

## 🎯 Objectives

- Bypass OS-level authentication **without altering system integrity**
- Locate and extract **user data (images, videos, documents)**
- Preserve original file structure during recovery
- Avoid unnecessary writes to the source disk

---

## 🧰 Tools & Environment

| Tool | Purpose |
|------|--------|
| SystemRescue (Linux) | Live boot environment for offline access |
| Kali Linux (SkorpiOm) | Used to prepare bootable media |
| dd | USB imaging |
| lsblk | Disk identification |
| mount | Filesystem access |
| cp | Data extraction |
| chntpw (optional) | Offline Windows password reset |

---

## 🧪 Methodology

### 1. Create Bootable Recovery Media

```bash
sudo dd if=systemrescue.iso of=/dev/sdX bs=4M status=progress
sudo sync
```

---

### 2. Boot Target System into Live Environment

- Access BIOS boot menu (F12 on Dell systems)
- Boot into SystemRescue (Linux live environment)
- Avoid booting into native OS to prevent disk writes

---

### 3. Identify and Mount Windows Partition

```bash
lsblk
sudo mkdir /mnt/windows
sudo mount /dev/sda2 /mnt/windows
```

---

### 4. Locate User Data

Typical directories:

```bash
/mnt/windows/Users/<username>/Pictures
/mnt/windows/Users/<username>/Videos
/mnt/windows/Users/<username>/Desktop
/mnt/windows/Users/<username>/Documents
```

---

### 5. Extract Data to External Storage

```bash
sudo mkdir /mnt/backup
sudo mount /dev/sdY1 /mnt/backup
cp -r /mnt/windows/Users/<username>/Pictures /mnt/backup/
```

---

## 🔐 Optional: Credential Recovery

```bash
cd /mnt/windows/Windows/System32/config
chntpw -u "<username>" SAM
```

---

## 🧠 Key Takeaways

### 🔍 Forensics Insight
- Physical access can bypass logical controls
- Offline environments are critical for safe recovery

### 🛡️ Security Implication
- Lack of disk encryption exposes data
- Passwords alone do not protect data at rest

### ⚙️ Best Practices
- Minimize writes to source disk
- Verify mount points
- Use external storage for extraction

---

## 🧱 MITRE ATT&CK Mapping

| Technique | Description |
|----------|------------|
| T1003 | OS Credential Access |
| T1078 | Valid Accounts |
| T1083 | File Discovery |
| T1005 | Data from Local System |

---

## 🦂 Burrow Reflection

> **Access control at the OS level is not sufficient without disk-level protection.**

Defensive takeaways:
- Use full disk encryption (BitLocker, FileVault)
- Secure boot configuration
- Control physical access

Offensive perspective:
- Demonstrates post-access data exposure
- Highlights real-world exfiltration paths

---

## 📁 Suggested Repo Placement

```
/investigations/dfir/windows7_offline_data_recovery.md
```

---

## 🏁 Final Thoughts

This case demonstrates ethical and controlled forensic recovery techniques on legacy systems, emphasizing both security gaps and defensive improvements.
