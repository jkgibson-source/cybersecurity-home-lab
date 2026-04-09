# Pi Network Node — Security Analysis Report

**Date:** April 7–8, 2026
**Lab:** The Burrow | Miami, FL
**Analyst:** JBird (`jkgibson-source`)
**Host Machine:** EagleEye11 (Mac mini M1, 8GB unified memory, macOS)
**Subject:** Pi Network Docker node (`testnet2`) — third-party application security review
**Status:** ✅ Decommissioned following analysis

---

## Executive Summary

A Pi Network blockchain node (`testnet2`) was discovered running as a Docker container on EagleEye11, the lab's primary SIEM host running Splunk Enterprise. The node was installed prior to the lab's security-focused build-out and had been running unexamined.

This report documents a structured security analysis conducted before decommissioning — treating the removal as a portfolio-quality investigation rather than a simple uninstall. The analysis uncovered two **High** severity findings and six **Medium** severity findings. The container was generating approximately 5.4GB of cumulative egress, contacting nearly 5,000 unique external IPs within a 5-minute window, and running an unauthenticated management interface — all on a machine whose primary role is security monitoring and log integrity.

**Decision: Decommission.** The risk-to-value ratio was unacceptable for a SIEM host.

---

## Environment

| Component | Detail |
|---|---|
| Host | EagleEye11 — Mac mini M1, macOS, 8GB unified memory |
| Host role | Splunk Enterprise SIEM, Docker runtime, daily driver |
| Container name | `testnet2` |
| Image | `pinetwork/pi-node-docker:community-v1.1-p21.2` |
| Base OS (container) | Ubuntu 20.04 (EOL April 2025) |
| Docker runtime | Docker Desktop for macOS |
| Analysis tools | `docker inspect`, `docker stats`, `tcpdump`, Wireshark, `tshark`, Splunk Enterprise, `whois` |

---

## Key Conceptual Finding — Docker ≠ VM

A foundational assumption going into this analysis was that Docker provided VM-like isolation. This investigation disproved that clearly.

Docker containers share the host kernel — there is no hypervisor boundary. The bridge network provides process-level network namespacing, but **port bindings to `0.0.0.0` expose those ports to the entire LAN**. A compromised or misbehaving container can affect the host in ways a VM cannot.

This distinction is critical on a SIEM machine where log integrity and host stability are the primary concerns.

---

## Phase 1 — Container Inspection

**Command:** `docker inspect testnet2`

### Network Configuration

| Parameter | Value |
|---|---|
| Network mode | Custom bridge (`pi-network_default`) |
| Container IP | `172.18.0.2` |
| Gateway | `172.18.0.1` |
| Host mode | No — internal bridge, but ports forwarded to `0.0.0.0` |

### Port Bindings (all LAN-exposed via `0.0.0.0`)

| Container Port | Host Port | Protocol | Service |
|---|---|---|---|
| 1570/tcp | 31403 | TCP | Stellar peer |
| 31402/tcp | 31402 | TCP | Stellar peer gossip |
| 8000/tcp | 31401 | TCP | HTTP interface |
| 5432/tcp | internal only | TCP | PostgreSQL |

### Findings

**[HIGH] Plaintext credentials in environment variables**

```
POSTGRES_PASSWORD=xxxxxxxxxxxxxxxx.      
NODE_PRIVATE_xxxxxxxxxxxxxxxxxxxxx
```

The `NODE_PRIVATE_KEY` is a Stellar blockchain private key stored in plaintext — visible to anyone with Docker access on the host. Secrets must never be passed as plaintext environment variables. Docker Secrets or a secrets manager (e.g., HashiCorp Vault) should be used instead.

**[MEDIUM] RW bind mounts to host filesystem**

```
~/Library/Application Support/Pi Network/docker_volumes/testnet_2/stellar     → /opt/stellar
~/Library/Application Support/Pi Network/docker_volumes/testnet_2/supervisor_logs → /var/log/supervisor
~/Library/Application Support/Pi Network/docker_volumes/testnet_2/history     → /history
```

Read-write bind mounts from inside the container back to the host home directory create a potential path for container escape or host file manipulation.

**[MEDIUM] No resource limits**

`Memory: 0` and `NanoCpus: 0` — the container had no CPU or memory caps, allowing it to consume all system resources unchecked. On a machine also running Splunk Enterprise and Ollama models on 8GB of unified memory, this is a significant stability risk.

**[MEDIUM] EOL base image**

`pinetwork/pi-node-docker:community-v1.1-p21.2` runs Ubuntu 20.04, which reached end-of-life in April 2025. No further security patches are available for the base image.

---

## Phase 2 — Traffic Capture

### Challenge: Docker Desktop on macOS

On Linux hosts, Docker bridge interfaces (e.g., `br-96ee3834c46e`) are real host interfaces accessible to `tcpdump`. On macOS, Docker Desktop runs inside a hidden Linux VM — the bridge interface does not exist on the macOS host. Running `tcpdump` on the host returns `No such device exists`.

**Solution: Capture from inside the container**

```bash
docker exec -it testnet2 bash
apt-get install -y tcpdump
tcpdump -i eth0 -w /tmp/pi_node_inside.pcap
# ~5 minutes of capture, then Ctrl+C
exit
docker cp testnet2:/tmp/pi_node_inside.pcap ~/pi_node_capture.pcap
```

**Result:** 45,500 packets captured | 8.8MB pcap file

---

## Phase 3 — Traffic Analysis

**Tool:** Wireshark + `tshark`

### DNS Behavior

Filter: `dns` → **0 packets.**

The container uses zero DNS resolution. All peers are contacted by hardcoded IP address. This means the node **bypasses DNS-based network filtering entirely** — a significant security control gap for any network implementing DNS-layer blocking.

### Outbound Traffic Volume

Filter: `ip.dst != 172.18.0.0/16`

- **33,670 of 45,500 packets (73.8%) were outbound to external IPs**
- All targeting port `31402` (Stellar peer gossip)
- Large volume of TCP Retransmissions — node spray-connects to its full hardcoded peer list; most peers unreachable

### Unique Destination IP Extraction

```bash
tshark -r ~/pi_node_capture.pcap -T fields -e ip.dst \
  | sort -u | grep -v "^172\.18\." > ~/pi_node_dest_ips.txt
wc -l ~/pi_node_dest_ips.txt
```

**Result: 4,989 unique destination IPs in approximately 5 minutes.**

---

## Phase 4 — IP Intelligence & Geographic Analysis

### WHOIS Sample (20 IPs)

Heavy Asia-Pacific concentration — consistent with Pi Network's largest user base regions.

| Region | Organizations Identified |
|---|---|
| Vietnam | VNPT, Viettel Group, FPT Telecom |
| Taiwan | Chunghwa Telecom, Data Communication Business Group |
| South Korea | Korea Telecom |
| China / Cloud | Alibaba Cloud LLC |
| Singapore | Aceville Pte. Ltd. |
| US | HostPapa, APNIC-allocated ranges |

### First-Octet Distribution (top ranges from 4,989 IPs)

| Count | Octet | Notes |
|---|---|---|
| 470 | 14.x.x.x | Historically DoD-allocated, now redistributed APAC |
| 438 | 47.x.x.x | Alibaba Cloud |
| 285 | 171.x.x.x | APAC |
| 276 | 113.x.x.x | China / APAC |
| 246 | 43.x.x.x | Japan / APAC |

No IPs flagged malicious in spot-check. Traffic is consistent with legitimate Stellar peer discovery behavior — but the volume and broadcast scope are wholly inappropriate for a SIEM host.

---

## Phase 5 — Splunk Log Analysis

Container logs were forwarded to Splunk via file monitor on `~/pi_node_live.log`. **51 events indexed.**

### Process Activity (from supervisord)

| PID | Process | Role |
|---|---|---|
| 1 | supervisord | Container process manager |
| 78 | postgresql | Full database server |
| 79 | stellar-core | Blockchain consensus engine |

### Critical Finding

```
CRIT Server 'unix_http_server' running without any HTTP authentication checking
```

Supervisord's management interface has **no authentication**. Anyone who can reach it has unrestricted control over the container's process management. This was self-reported as `CRIT` by the application and captured by Splunk — a direct demonstration of SIEM value. This finding would have gone unnoticed without log monitoring.

---

## Phase 6 — Resource Monitoring

**Command:** `docker stats testnet2 --no-stream` (sampled every 30 seconds)

| Metric | Observed Range |
|---|---|
| CPU | 0.4% – 92.6% (spikes during peer sync) |
| Memory | 637 – 644 MiB sustained |
| Network I/O | ~2.1GB received / ~5.4GB sent (cumulative) |
| Active PIDs | 22 – 23 at all times |

A sustained ~640MB memory footprint on an 8GB unified memory machine also running Splunk Enterprise and Ollama models represents a meaningful and unacceptable overhead for a security monitoring host.

---

## Findings Summary

| # | Finding | Severity |
|---|---|---|
| 1 | Plaintext Stellar private key + database password in environment variables | **High** |
| 2 | Unauthenticated supervisord HTTP management interface (self-reported CRIT) | **High** |
| 3 | 4,989 unique outbound IPs in ~5 min / ~5.4GB cumulative egress | **High** |
| 4 | Three ports bound to `0.0.0.0` — exposed to entire LAN | Medium |
| 5 | Zero DNS usage — bypasses DNS-based network controls | Medium |
| 6 | EOL base image (Ubuntu 20.04, EOL April 2025) | Medium |
| 7 | No CPU or memory resource limits configured | Medium |
| 8 | RW bind mounts to host home directory subtree | Medium |

---

## Evidence Files

| File | Size | Contents |
|---|---|---|
| `pi_node_capture.pcap` | 8.8MB | Wireshark packet capture (45,500 packets, ~5 min) |
| `pi_node_dest_ips.txt` | 69KB | 4,989 unique external destination IPs |
| `pi_node_final_logs_20260408.txt` | 5.5KB | Container logs at session end |
| `pi_node_live.log` | 5.5KB | Real-time log stream (Splunk-monitored) |
| `pi_node_stats.log` | 9.5KB | Resource usage over time |

---

## Decommission Procedure

```bash
# Stop and remove the container
docker stop testnet2 && docker rm testnet2

# Remove the compose-managed network
docker network rm pi-network_default

# Remove the Docker image
docker rmi pinetwork/pi-node-docker:community-v1.1-p21.2

# Remove any named Docker volumes
docker volume ls | grep pi
docker volume rm <any_pi_volumes_listed>

# Remove bind mount data from host
rm -rf ~/Library/Application\ Support/Pi\ Network/

# Verify cleanup
docker ps -a
docker network ls
docker stats
```

No account deletion or node deregistration with Pi Network is required. The node simply stops participating in the network when the container is removed. Any Pi coin balance remains accessible through the Pi Network mobile application, entirely separate from the Docker node.

---

## Key Learnings

- **Docker Desktop on macOS** hides the Linux VM layer — `tcpdump` on Docker bridge interfaces fails at the host level; capture must occur from inside the container or at the host NIC level via `en0`
- **`docker inspect`** is a first-order recon tool — reveals network configuration, plaintext credentials, bind mounts, and resource limits in a single command
- **Stellar-core peer sweeps** are aggressive by design — hardcoded IPs, no DNS, high connection volume is expected behavior for blockchain nodes, but wholly inappropriate on sensitive infrastructure
- **Splunk caught the CRIT log** — the unauthenticated supervisord management interface would have gone unnoticed without log monitoring; direct demonstration of SIEM operational value
- **Docker ≠ VM** — containers share the host kernel; isolation is process-level, not hardware-level; port bindings to `0.0.0.0` expose services to the full LAN regardless of bridge networking

---

## Tools Used

`docker inspect` · `docker stats` · `docker exec` · `tcpdump` · Wireshark 4.6.4 · `tshark` · Splunk Enterprise 10.2.1 · `whois` · `sort` · `wc`

---

*The Burrow — Miami, FL | EagleEye11 | Splunk Enterprise 10.2.1 | April 2026*
*Analyst: JBird (`jkgibson-source`)*
