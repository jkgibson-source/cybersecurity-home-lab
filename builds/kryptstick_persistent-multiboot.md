# 🔐 KryptStick: Encrypted Persistent Multi-Boot Cybersecurity Toolkit

## 📍 Overview
This project documents the design and implementation of a portable, encrypted, multi-boot USB toolkit ("KryptStick") used within a home lab environment, The Burrow.

The KryptStick enables secure, persistent access to multiple operating systems—including Parrot OS (encrypted persistence) and Ubuntu Studio (casper persistence)—while leaving no forensic footprint on host machines.

---

## 🎯 Objectives
- Build a portable cybersecurity workstation
- Implement encrypted persistence using LUKS
- Enable multi-boot capability via Ventoy
- Ensure stateful configuration across reboots
- Maintain operational security (OPSEC) by avoiding host system modification

---

## 🧰 Hardware & Environment
- USB Device: 64GB SanDisk USB 3.0
- Host System: Kali Linux (MacBook Pro A1286 — “SkorpiOm”)
- Target System: MacBook Pro A1398 — “Krypton1t3”
- Lab Environment: The Burrow

---

## 💿 Operating Systems Deployed
- Ubuntu Studio 24.04.4 (casper persistence)
- Parrot OS Security 7.1 (LUKS encrypted persistence)
- SystemRescue 13.00 (non-persistent utility)

---

## 🏗️ Architecture

### Ventoy Multi-Boot Layout
- ISO-based boot structure
- Persistence linked via ventoy.json
- Encrypted backend for Parrot OS

### Persistence Design
| OS              | Type            | Size  | Encryption |
|----------------|----------------|------|-----------|
| Ubuntu Studio  | casper-rw file | 20GB | No        |
| Parrot OS      | LUKS container | 20GB | Yes       |

---

## 🔐 Parrot OS Encrypted Persistence Workflow

### 1. Create Persistence File
sudo dd if=/dev/zero of=/mnt/kryptstick/parrot-persistence bs=1M count=20480 status=progress

### 2. Format as LUKS1 (Required)
sudo cryptsetup luksFormat --type luks1 /mnt/kryptstick/parrot-persistence

### 3. Open Encrypted Container
sudo cryptsetup luksOpen /mnt/kryptstick/parrot-persistence parrot-encrypted

### 4. Create Filesystem
sudo mkfs.ext4 -L persistence /dev/mapper/parrot-encrypted
sudo fsck.ext4 -y /dev/mapper/parrot-encrypted

### 5. Configure Persistence
sudo mount /dev/mapper/parrot-encrypted /mnt/parrot-persistence
echo "/ union" | sudo tee /mnt/parrot-persistence/persistence.conf

---

## ⚙️ Ventoy Configuration

{
  "persistence": [
    {
      "image": "/ubuntustudio-24.04.4-dvd-amd64.iso",
      "backend": "/ubuntu-studio-casper-rw"
    },
    {
      "image": "/Parrot-security-7.1_amd64.iso",
      "backend": "/parrot-persistence",
      "encryption": "luks"
    }
  ]
}

---

## 🧪 Validation & Testing

### Test Cases
- File persistence across reboots (testfile.txt)
- System configuration persistence (time settings)
- Encrypted container unlock prompt on boot
- Network configuration persistence (WiFi profile retention)

### Results
All persistence mechanisms functioned as expected.  
Encrypted Parrot OS environment successfully retained state across multiple reboots.

---

## 🛠️ Issue Encountered: WiFi Connection Failure

### Symptoms
- Connection attempted but failed with:
  connection 'NETGEAR14' deactivated

### Root Cause
- Misconfigured NetworkManager profile
- Missing key management configuration (wpa-psk)

### Resolution
Rebuilt connection manually using nmcli:

sudo nmcli connection add type wifi ifname wlp2s0 con-name NETGEAR14 ssid NETGEAR14
sudo nmcli connection modify NETGEAR14 wifi-sec.key-mgmt wpa-psk wifi-sec.psk "<password>"
sudo nmcli connection up NETGEAR14

### Outcome
- Successful connection established
- Configuration persisted across reboot

---

## 🔍 Key Lessons Learned

- Parrot OS requires LUKS1, not LUKS2, for persistence compatibility
- Filesystem integrity checks (fsck) are critical after mkfs
- Ventoy persistence relies heavily on correct JSON mapping
- NetworkManager profiles may fail silently without explicit configuration
- Live environments on Mac hardware may require manual driver handling

---

## 🛡️ Security Considerations

- Encrypted persistence protects stored data at rest
- No writes occur on host system disks
- Suitable for portable red team / OSINT workflows

---

## 🚀 Future Enhancements

- Add toolchain persistence (Burp Suite, Metasploit configs)
- Integrate OSINT automation workflows
- Implement secure data exfiltration testing scenarios
- Expand to full-disk encrypted install on Krypton1t3

---

## 🦂 Final Thoughts

This project demonstrates the ability to:
- Design and implement secure, portable infrastructure
- Troubleshoot Linux systems at a low level
- Apply encryption and persistence techniques in practical scenarios

This is not just a lab build—it is a field-ready operational platform.
