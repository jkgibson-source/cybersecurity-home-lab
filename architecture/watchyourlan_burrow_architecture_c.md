# WatchYourLAN Deployment — The Burrow

## Overview

**WatchYourLAN** is a lightweight network visibility and device awareness service deployed as part of The Burrow's defensive monitoring stack. It was added to complement existing systems — Wazuh, Splunk, Sniffnet, Tailscale, and Reticulum — by filling a specific gap: persistent LAN inventory awareness.

The service is deployed on **Krypton1t3**, the lab's hybrid AI/workstation/infrastructure node running Fedora Linux 44.

---

## Why WatchYourLAN

The Burrow already had strong coverage across endpoint monitoring, log aggregation, packet observation, and mesh networking. What it lacked was a persistent, passive census of what devices are on the LAN at any given moment — and a history of when they appeared or disappeared.

WatchYourLAN provides:
- Continuous ARP/network scanning
- MAC/IP tracking with historical visibility
- Device presence and absence detection
- Lightweight defensive telemetry with no agent required on targets

---

## Architectural Role

### WatchYourLAN vs Sniffnet

These two tools are complementary, not redundant:

| Tool | Best For |
|---|---|
| **Sniffnet** | Live traffic visualization — investigating flows, spotting anomalies, interactive analysis |
| **WatchYourLAN** | Persistent LAN awareness — device inventory, history, unexpected arrivals/departures |

Together they form a lightweight but complete network visibility layer: Sniffnet tells you what's happening in traffic, WatchYourLAN tells you who's on the network.

---

## Why Not EagleEye11

WatchYourLAN was first attempted on EagleEye11 (macOS, Docker Desktop). The container launched and the web UI functioned, but ARP scanning was effectively broken — Docker Desktop on macOS runs containers inside a Linux VM, so the container sees Docker's virtual network (`192.168.65.x`) rather than the real LAN. EagleEye11 was ruled out as the primary deployment target.

---

## Deployment — Krypton1t3

Krypton1t3 was the right choice: Fedora Linux, real Docker host networking, direct LAN access, and a growing role as a persistent infrastructure node (always-on, lid-closed configuration — see below).

### Directory Setup

```bash
mkdir -p ~/docker/watchyourlan/wyl
cd ~/docker/watchyourlan
```

### Network Interface

```bash
ip route | grep default
# default via 10.0.0.1 dev wlp2s0
```

Interface: `wlp2s0`

### Permission Fix

Initial launches failed with `permission denied` on the config file, causing database initialization failures and segfaults. Fix:

```bash
docker stop watchyourlan && docker rm watchyourlan
sudo rm -rf ~/docker/watchyourlan/wyl
mkdir -p ~/docker/watchyourlan/wyl
chmod 777 ~/docker/watchyourlan/wyl
```

### Final Deployment Command

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

Web UI: `http://localhost:8840`

> Note: `docker-compose` was unavailable on this Fedora installation — `docker run` was used directly.

---

## Operational Commands

```bash
# Status
docker ps | grep watchyourlan

# Logs (live)
docker logs -f watchyourlan

# Stop / Start / Remove
docker stop watchyourlan
docker start watchyourlan
docker rm -f watchyourlan
```

---

## Always-On Configuration

Krypton1t3 is configured to remain operational with the lid closed, acting as a headless infrastructure node.

### Prevent Suspend on Lid Close

```bash
sudo nano /etc/systemd/logind.conf
```

```ini
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
```

```bash
sudo systemctl restart systemd-logind
```

### Ensure Docker Starts at Boot

```bash
sudo systemctl enable --now docker
```

---

## Defensive Stack Position

WatchYourLAN slots into The Burrow's monitoring stack as the **asset awareness layer**:

| Layer | Tool |
|---|---|
| Endpoint monitoring | Wazuh |
| Log aggregation | Splunk |
| Traffic observation | Sniffnet |
| LAN asset awareness | **WatchYourLAN** |
| Mesh networking | Tailscale |
| Resilient comms | Reticulum |

---

## Future Considerations

- Grafana integration for historical dashboards
- Webhook alerting on new/unknown device detection
- Correlation with Wazuh events (new device → trigger alert)
- BurrowMCP tool integration for remote LAN census queries
- TRIM_HIST tuning for longer retention windows

---

## Tags

`#watchyourlan` `#docker` `#fedora` `#krypton1t3` `#theburrow` `#network-monitoring` `#asset-awareness` `#homelab` `#blue-team` `#defensive-operations` `#situational-awareness`
