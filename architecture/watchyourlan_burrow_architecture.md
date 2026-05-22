# WatchYourLAN Deployment for The Burrow

## Overview

This document describes the deployment, configuration, operational role, and architectural significance of **WatchYourLAN** within **The Burrow** home lab environment.

WatchYourLAN was added as a lightweight network visibility and device awareness layer to complement existing defensive and monitoring systems including:

- Wazuh
- Splunk
- Sniffnet
- Tailscale
- Reticulum
- Dockerized infrastructure services

The service was ultimately deployed on **Krypton1t3**, the lab’s hybrid AI / workstation / infrastructure node running Fedora Linux.

---

# Why WatchYourLAN Was Added

The Burrow already had:
- endpoint visibility
- log aggregation
- packet observation
- remote management
- mesh networking

What it lacked was:
- persistent LAN inventory awareness
- device appearance/disappearance tracking
- passive asset awareness
- lightweight network census functionality

WatchYourLAN fills that gap.

It provides:
- continuous ARP/network scanning
- LAN device discovery
- MAC/IP tracking
- historical visibility
- device presence awareness
- lightweight defensive telemetry

---

# Architectural Role

## WatchYourLAN vs Sniffnet

The deployment clarified an important distinction:

| Tool | Purpose |
|---|---|
| Sniffnet | Live traffic visualization and analysis |
| WatchYourLAN | Persistent LAN device awareness |

### Sniffnet
Best for:
- investigating traffic
- observing flows
- spotting anomalies
- interactive analysis

### WatchYourLAN
Best for:
- identifying devices on the LAN
- tracking device history
- detecting unexpected arrivals/disappearances
- maintaining persistent situational awareness

Together they form a complementary lightweight network visibility stack.

---

# Initial Deployment Attempt

## EagleEye11 (macOS)

WatchYourLAN was first attempted inside Docker on:
- EagleEye11
- macOS host
- Docker Desktop

### Result

Partial success:
- container launched
- web UI functioned
- scanning functionality was limited

### Root Cause

Docker Desktop on macOS uses a Linux VM abstraction layer.

As a result:
- host networking is not truly exposed
- ARP scanning is limited
- the container sees Docker virtual networking rather than the real LAN

Example observed network:
- 192.168.65.x

### Conclusion

EagleEye11 was deemed unsuitable for primary WatchYourLAN deployment.

---

# Final Deployment Target

## Krypton1t3

### Why Krypton1t3 Was Chosen

Krypton1t3 already functioned as:
- AI experimentation node
- Docker host
- hybrid workstation
- infrastructure support node

Advantages:
- Fedora Linux
- real Docker host networking
- direct LAN access
- existing Docker installation
- suitable long-running role during NY trip operations

---

# Deployment Procedure

## Directory Structure

```bash
mkdir -p ~/docker/watchyourlan/wyl
cd ~/docker/watchyourlan
```

---

# Network Interface Discovery

The active network interface was identified using:

```bash
ip route | grep default
```

Example result:

```text
default via 10.0.0.1 dev wlp2s0
```

Interface used:
- `wlp2s0`

---

# Docker Deployment

Compose was unavailable on the Fedora installation, so the deployment used a direct `docker run` workflow.

---

# Permission Issue Encountered

Initial container launches failed with:

```text
permission denied
open /data/WatchYourLAN/config_v2.yaml
```

This caused:
- database initialization failures
- segmentation faults
- container crashes

---

# Resolution

The data directory was recreated with permissive write access:

```bash
docker stop watchyourlan
docker rm watchyourlan

cd ~/docker/watchyourlan

sudo rm -rf wyl
mkdir -p wyl
chmod 777 wyl
```

---

# Final Working Deployment Command

```bash
docker run -d \
  --name watchyourlan \
  --network host \
  --restart always \
  -e TZ=America/New_York \
  -e IFACES=wlp2s0 \
  -e PORT=8840 \
  -e COLOR=dark \
  -e TIMEOUT=120 \
  -e TRIM_HIST=168 \
  -v "$HOME/docker/watchyourlan/wyl:/data/WatchYourLAN" \
  aceberg/watchyourlan:latest
```

---

# Accessing the Web UI

```text
http://localhost:8840
```

The service successfully:
- scanned the LAN
- identified devices
- populated the database
- persisted configuration data

---

# Operational Commands

## View Running Container

```bash
docker ps | grep watchyourlan
```

---

## View Logs

```bash
docker logs -f watchyourlan
```

---

## Stop Service

```bash
docker stop watchyourlan
```

---

## Start Existing Container

```bash
docker start watchyourlan
```

---

## Remove Container

```bash
docker rm -f watchyourlan
```

---

# Persistence Behavior

The container was configured with:

```text
--restart always
```

This ensures:
- automatic restart after reboot
- automatic restart after Docker daemon restart
- crash recovery

Docker itself should be enabled at boot:

```bash
sudo systemctl enable --now docker
```

---

# Lid-Closed / Always-On Configuration

Krypton1t3 was evaluated as a potential “always-on” operational node during extended remote operations.

Recommended configuration:

## Prevent Suspend on Lid Close

Edit:

```bash
sudo nano /etc/systemd/logind.conf
```

Add or modify:

```ini
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
```

Apply:

```bash
sudo systemctl restart systemd-logind
```

---

# Operational Role During NY Trip

During travel operations, Krypton1t3 is expected to function as:

- WatchYourLAN host
- AI experimentation node
- Docker infrastructure node
- remotely accessible utility system
- lightweight defensive monitoring node

The system will remain:
- powered
- network-connected
- lid closed
- display off
- operational

---

# Strategic Significance

WatchYourLAN adds an important defensive layer to The Burrow because it enables:

- persistent network awareness
- passive device discovery
- historical LAN visibility
- unexpected device detection
- infrastructure awareness during remote operations

This capability complements:
- Wazuh (endpoint monitoring)
- Splunk (log aggregation)
- Sniffnet (traffic observation)
- Tailscale (mesh networking)
- Reticulum (resilient communications)

Rather than replacing those systems, WatchYourLAN acts as:
> a lightweight situational-awareness and asset-visibility layer.

---

# Future Considerations

Potential future enhancements:

- Grafana integration
- webhook alerting
- VLAN-aware segmentation
- correlation with Wazuh events
- integration into BurrowMCP tooling
- remote monitoring dashboards
- persistent historical retention tuning

---

# Tags

`#watchyourlan`
`#docker`
`#fedora`
`#krypton1t3`
`#theburrow`
`#network-monitoring`
`#asset-awareness`
`#homelab`
`#blue-team`
`#defensive-operations`
`#docker-networking`
`#situational-awareness`
