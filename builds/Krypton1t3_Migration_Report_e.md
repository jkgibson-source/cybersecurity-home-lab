# 🦂 Krypton1t3 OS Migration Report

**Machine:** Krypton1t3 (2014 MacBook Pro — Model A1398)  
**Migration:** macOS Big Sur → Fedora Security Lab 43  
**Date:** April 2026  
**Author:** jkgibson-source  

---

## Overview

Krypton1t3 is a 2014 MacBook Pro (A1398) with 16GB RAM and Iris Pro Graphics, repurposed as a secondary defensive and logging node within The Burrow home lab. This document chronicles the complete OS migration from macOS Big Sur to Fedora Security Lab 43.

**Migration rationale:**
- macOS Big Sur reached end-of-support on Apple's official timeline
- Fedora Security Lab provides a purpose-built environment for defensive cybersecurity tooling
- Linux offers better control over system telemetry and log collection

---

## Hardware Profile

| Component | Specification |
|---|---|
| Model | MacBook Pro A1398 (Retina, 2014) |
| CPU | Intel Core i7 (4th Gen) |
| RAM | 16 GB DDR3 |
| Graphics | Intel Iris Pro Graphics (1536 MB) |
| Wireless | Broadcom BCM4360 (rev 03) |
| Storage | Internal SSD |

> **Note:** This hardware has no discrete GPU. All inference runs on CPU.

---

## Pre-Migration State

| Item | Detail |
|---|---|
| Previous OS | macOS Big Sur 11.7.10 |
| Splunk UF | Installed, forwarding to EagleEye11:9997 |
| Wazuh Agent | Installed |
| Ollama | Running `llama3.2:3b` |
| Tailscale | Connected (100.103.171.45) |

---

## Installation Process

### 1. Media Preparation

- Downloaded Fedora Security Lab 43 (x86_64) ISO
- Created bootable USB using Balena Etcher
- Verified ISO checksum before flashing

### 2. Boot & Installation

- Powered down, held **Option** key to access boot picker
- Selected the Fedora USB installer
- Partitioned entire drive (macOS partitions removed)
- Installed with **Fedora Security Lab** spin, included defensive tooling packages

### 3. Initial Setup

```bash
# Update all packages
sudo dnf update -y

# Install development tools (required for DKMS)
sudo dnf groupinstall "Development Tools" -y
sudo dnf install kernel-devel kernel-headers -y
```

---

## Post-Installation Configuration

### WiFi — Broadcom BCM4360

The BCM4360 wireless card required proprietary driver support via RPMFusion.

**Step 1: Enable RPMFusion repositories**

```bash
sudo dnf install https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-43.noarch.rpm -y
sudo dnf install https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-43.noarch.rpm -y
```

**Step 2: Install the broadcom-wl driver**

```bash
sudo dnf install broadcom-wl broadcom-wl-driver-manager -y
```

**Step 3: Resolve kernel header mismatch**

Initial boot ran kernel `6.17.1-300.fc43.x86_64` but available kernel headers did not match.

```bash
# Install matching kernel-devel
sudo dnf install kernel-devel-6.17.1-300.fc43.x86_64 -y

# Rebuild modules with DKMS
sudo akmods --force
sudo dracut -f
```

**Step 4: Load the driver**

```bash
# Verify driver loads
sudo modprobe wl

# Persist across reboots
echo "wl" | sudo tee /etc/modules-load.d/wl.conf
```

**Result:** WiFi connected to Puffin SSID on 2.4GHz and 5GHz bands.

---

### Splunk Universal Forwarder

Splunk UF was reinstalled from scratch.

**Installation:**

```bash
# Download splunkforwarder from splunk.com (requires free account)
# Transfer via USB or direct download on the machine

sudo rpm -i splunkforwarder-*.rpm
sudo /opt/splunkforwarder/bin/splunk start --accept-license
```

**Configuration:**

```bash
# Set hostname so Splunk UF reports correctly
# (Fedora's hostnamectl does not propagate to Splunk automatically)

sudo /opt/splunkforwarder/bin/splunk set servername Krypton1t3
sudo /opt/splunkforwarder/bin/splunk set default-hostname Krypton1t3
```

**inputs.conf — log monitoring:**

```ini
[default]
hostname = Krypton1t3

[monitor:///var/log]
_TCP_ROUTING = *

[monitor:///var/log/secure]
_TCP_ROUTING = *

[monitor:///var/log/messages]
_TCP_ROUTING = *

[monitor:///var/log/dnf5.log]
_TCP_ROUTING = *

[monitor:///var/log/firewalld]
_TCP_ROUTING = *
```

**Deployment client:**

```bash
sudo /opt/splunkforwarder/bin/splunk set deploy-poll 10.0.0.112:8089
sudo /opt/splunkforwarder/bin/splunk restart
```

**Verify connectivity:**

```bash
# Confirm active connection to EagleEye11:9997
sudo /opt/splunkforwarder/bin/splunk list forward-server
```

Expected output:
```
Active forwards:
    10.0.0.112:9997
Configured but inactive forwards:
    None
```

**Validate monitored paths:**

```bash
sudo /opt/splunkforwarder/bin/splunk list monitor
```

**Inject a test event to confirm end-to-end pipeline:**

```bash
logger "Krypton1t3 pipeline test"
```

Then search in Splunk on EagleEye11:
```
index=main host=Krypton1t3
```

---

### Splunk Forwarder — Troubleshooting Reference

Two issues were encountered and resolved during initial setup. Documented here for future reference.

**Issue 1: `/var/log/messages` and `/var/log/secure` missing**

Fedora uses `systemd-journald` by default — traditional syslog files do not exist unless `rsyslog` is installed.

```bash
sudo dnf install rsyslog -y
sudo systemctl enable --now rsyslog

# Confirm files now exist
ls /var/log/messages /var/log/secure
```

**Issue 2: Events arriving in Splunk under `host=fedora` instead of `host=Krypton1t3`**

The Splunk Universal Forwarder does not automatically inherit the system hostname set via `hostnamectl`. The `host` field must be explicitly declared in the forwarder config.

```bash
sudo nano /opt/splunkforwarder/etc/system/local/inputs.conf
```

Add under `[default]`:
```ini
[default]
host = Krypton1t3
```

```bash
sudo /opt/splunkforwarder/bin/splunk restart
```

> ⚠️ This applies to any fresh Fedora installation where the OS default hostname (`fedora`) has not been overridden in the forwarder config. `hostnamectl set-hostname` alone is not sufficient — the forwarder has its own hostname setting that takes precedence.

**Check forwarder logs for connection errors:**

```bash
sudo tail -f /opt/splunkforwarder/var/log/splunk/splunkd.log | grep -i "error\|warn\|connect"
```

**Check for SELinux blocks (Fedora-specific — not present on Ubuntu/Kali):**

```bash
sudo ausearch -m avc -ts recent
```

If denials referencing `splunkforwarder` appear, SELinux is blocking log file access and policies will need adjustment. No SELinux blocks were observed on this install.

---

### Wazuh Agent

**Installation:**

```bash
sudo rpm --import https://packages.wazuh.com/key/GPG-KEY-WAZUH
sudo cat > /etc/yum.repos.d/wazuh.repo <<EOF
[Wazuh]
gpgcheck=1
gpgkey=https://packages.wazuh.com/key/GPG-KEY-WAZUH
enabled=1
name=Wazuh
baseurl=https://packages.wazuh.com/4.x/yum/
protect=1
EOF

sudo dnf install wazuh-agent -y
```

**Configure manager IP in ossec.conf:**

```bash
sudo sed -i 's/MANAGER_IP/10.0.0.112/' /var/ossec/etc/ossec.conf

# Verify
sudo grep -A 3 "<server>" /var/ossec/etc/ossec.conf
```

Expected output:
```xml
<server>
  <address>10.0.0.112</address>
  <port>1514</port>
  <protocol>tcp</protocol>
```

**Enable and start the agent:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable wazuh-agent
sudo systemctl start wazuh-agent
sudo systemctl status wazuh-agent
```

All five processes confirm a healthy agent:
- `wazuh-execd`
- `wazuh-agentd`
- `wazuh-syscheckd`
- `wazuh-logcollector`
- `wazuh-modulesd`

**Docker Manager Enrollment — Important:**

> ⚠️ The Wazuh Manager runs inside Docker on EagleEye11. The `wazuh-control` binary does NOT exist on the EagleEye11 host filesystem. All manager-side commands must be run via `docker exec`.

**Step 1 — Confirm manager version and container name (EagleEye11):**

```bash
docker ps | grep wazuh
# Container name: single-node-wazuh.manager-1

docker exec single-node-wazuh.manager-1 /var/ossec/bin/wazuh-control info
# WAZUH_VERSION="v4.9.0"
```

**Step 2 — Open agent manager inside the container (EagleEye11):**

```bash
docker exec -it single-node-wazuh.manager-1 /var/ossec/bin/manage_agents
```

**Step 3 — List existing agents before adding (L):**

Always list first to avoid duplicate name conflicts. Known agents:
```
ID: 001, Name: Krypton1t3.local, IP: any   ← legacy pentest entry, do not reuse
ID: 002, Name: SkorpiOm, IP: any
ID: 003, Name: Krypton1t3, IP: any          ← current Fedora node
```

**Step 4 — Add new agent (A):**
```
Name: Krypton1t3
IP: 10.0.0.242
Confirm: y
```

> ⚠️ If `WARNING: 9008: Duplicate name` appears, the agent already exists. Use **E** to extract the key for the existing entry instead of creating a new one.

**Step 5 — Extract key (E):**
```
Agent ID: 003
```
Copy the full base64 key string displayed.

**Step 6 — Import key on Krypton1t3:**

```bash
sudo /var/ossec/bin/manage_agents
# Choose: I (Import key)
# Paste the full key string copied from the manager
# Confirm: y
```

**Step 7 — Restart agent and verify:**

```bash
sudo systemctl restart wazuh-agent
```

Verify in Wazuh dashboard at `https://10.0.0.112` — Krypton1t3 should appear as agent 003 with active status and MITRE ATT&CK events populating.

> **Enrollment note:** Due to Wazuh Manager running inside a Docker container on EagleEye11, standard agent enrollment required additional configuration for the correct manager port and Docker network addressing. Agent is currently enrolled and communicating.

---

### Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull llama3.2:3b

# Start service
sudo systemctl enable ollama
sudo systemctl start ollama
```

**Verification:**

```bash
ollama list
# NAME                ID           SIZE      MODIFIED
# llama3.2:3b         146500e46c48  1.9GB     2026-04-22
```

---

### Tailscale

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Authenticate (one-time)
sudo tailscale up --operator jk.gibson

# Verify
tailscale status
```

**Confirmed:** Krypton1t3 reachable at `100.103.171.45` on the Puffin tailnet.

---

### Additional Tooling Installed

```bash
# Virtualization (planned for future use)
sudo dnf install virt-manager libvirtd -y
sudo systemctl enable libvirtd

# Misc security tools (already in Security Lab spin)
# nmap, wireshark, tcpdump, suricata, zeek (already included)
```

---

## Verified Functionality

| Service | Status | Notes |
|---|---|---|
| WiFi (BCM4360) | ✅ Working | broadcom-wl via DKMS |
| Splunk UF | ✅ Forwarding | → EagleEye11:9997, all monitored logs |
| Wazuh Agent | ✅ Enrolled | Communicating with EagleEye11 manager |
| Ollama | ✅ Running | `llama3.2:3b` CPU inference |
| Tailscale | ✅ Connected | 100.103.171.45 |
| Tailscale EulerB | ✅ Active | subnet router for 10.0.0.0/24 |

---

## Known Issues & Resolutions

| Issue | Resolution |
|---|---|
| Kernel headers mismatch after fresh install | Installed `kernel-devel-6.17.1-300.fc43.x86_64` explicitly |
| BCM4360 WiFi not detected | Installed `broadcom-wl` from RPMFusion, ran `akmods --force` |
| Splunk UF hostname mismatch | Manually set in `/opt/splunkforwarder/etc/system/local/inputs.conf` under `[default]` |
| Wazuh enrollment (Docker manager) | Used Docker-aware enrollment settings for manager IP/port |

---

## Current Node Configuration

| Item | Value |
|---|---|
| Hostname | Krypton1t3 |
| LAN IP | 10.0.0.x (DHCP via Talon router) |
| Tailscale IP | 100.103.171.45 |
| OS | Fedora Security Lab 43 |
| Kernel | 6.17.1-300.fc43.x86_64 |
| Primary Role | Defensive / Logging |
| Splunk Forwarding | EagleEye11:9997 |
| Ollama Model | `llama3.2:3b` |

---

## Security & System Hardening

### SELinux (Fedora Default)

Fedora 43 ships with SELinux in **enforcing** mode by default. Unlike Ubuntu/Kali, this is active out of the box and will silently block unauthorized file access. Verify status:

```bash
getenforce
# Expected: Enforcing
```

Do not disable SELinux. If a service is blocked, audit the denial and write a targeted policy exception rather than setting permissive mode:

```bash
# Check recent denials
sudo ausearch -m avc -ts recent

# View SELinux status details
sestatus
```

---

### Firewall (firewalld)

Fedora uses `firewalld` by default. Verify it is active:

```bash
sudo systemctl status firewalld
sudo firewall-cmd --list-all
```

Krypton1t3 should only expose ports required by lab services. Review and restrict as needed:

```bash
# Check open ports
sudo firewall-cmd --list-ports

# Remove unnecessary ports
sudo firewall-cmd --permanent --remove-port=<port>/tcp
sudo firewall-cmd --reload
```

---

### Automatic Security Updates

Enable automatic security patches to keep the node current between active sessions:

```bash
sudo dnf install dnf-automatic -y
sudo systemctl enable --now dnf-automatic-install.timer
```

Verify the timer is active:

```bash
systemctl status dnf-automatic-install.timer
```

---

### SSH Hardening

If SSH is enabled on Krypton1t3, apply baseline hardening:

```bash
sudo nano /etc/ssh/sshd_config
```

Recommended settings:
```
PermitRootLogin no
PasswordAuthentication no
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
```

```bash
sudo systemctl restart sshd
```

> Since Krypton1t3 is accessible via Tailscale, consider restricting SSH to the Tailscale interface only (`ListenAddress 100.103.171.45`).

---

### Kernel Audio Tuning (Low-Latency / Music Production)

Fedora 43 ships with a `PREEMPT_DYNAMIC` kernel, which can be tuned for low-latency audio without a full RT kernel replacement. This is preferable to Ubuntu Studio's separate low-latency kernel build.

**Enable low-latency mode via GRUB:**

```bash
sudo nano /etc/default/grub
```

Add to `GRUB_CMDLINE_LINUX`:
```
preempt=full threadirqs
```

Regenerate GRUB config:
```bash
sudo grub2-mkconfig -o /boot/grub2/grub.cfg
```

Reboot and verify:
```bash
cat /sys/kernel/debug/sched/preempt
# Expected: full
```

**Install rsyslog for traditional audio/JACK logging compatibility:**
Already installed as part of Splunk UF setup.

**Audio group permissions (limits.conf):**

```bash
sudo nano /etc/security/limits.d/audio.conf
```

Add:
```
@audio   -  rtprio     95
@audio   -  memlock    unlimited
```

Add user to audio group:
```bash
sudo usermod -aG audio superskorp_7
```

> Note: Running KVM virtual machines and low-latency audio simultaneously is not recommended. These workloads compete for CPU scheduling priority. Keep them separated in time.

---

## Future Enhancements - all completed!

- ✅ virt-manager + libvirtd — VM hypervisor verification and first guest (Metasploitable 2)
- ✅ Twingate client — alternative VPN mesh / zero-trust access
- ✅ Splunk UF boot start — enable Splunk UF on system boot
- ✅ Full Wazuh agent capability verification (YARA scanning, active response)
- ✅ Additional Ollama models — mistral:7b, phi3:mini, deepseek-coder:6.7b (pulled, testing pending)
- ✅ Jam/music production software — Ardour, JACK, plugins
- ✅ Upgrade to Fedora Security Lab 44 Final via `sudo dnf upgrade --refresh` (target: April 25, 2026)

---

## References

- [Fedora Security Lab](https://fedoraproject.org/security)
- [RPMFusion Broadcom WiFi Guide](https://rpmfusion.org/Howto/Broadcom)
- [Splunk Universal Forwarder Docs](https://docs.splunk.com/Documentation/Forwarder)
- [Wazuh Agent Enrollment](https://documentation.wazuh.com/current/infrastructure-summary/deploying-wazuh-agent.html)
- [Tailscale on Linux](https://tailscale.com/download/linux)

---

*Report generated: April 2026*  
*Source: The Burrow Home Lab — github.com/jkgibson-source/cybersecurity-home-lab*
