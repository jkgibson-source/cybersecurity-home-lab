# BurrowMCP — Architecture Document
**Version:** 0.1  
**Created:** 2026-05-03  
**Author:** JBird + Claude  

---

## What Is BurrowMCP?

BurrowMCP is a custom MCP (Model Context Protocol) server that exposes The Burrow home lab as a set of tools Claude can call. It allows Claude — running on Claude Desktop (EagleEye11) or Claude Mobile (SolSkorp_13) — to query lab status, read security alerts, and execute safe maintenance tasks on lab nodes remotely.

---

## Design Philosophy

- **EagleEye11 is the trusted broker.** All tool execution happens on or through EagleEye11. No node is ever touched directly by Claude or the outside world.
- **Tailscale is the secure backbone.** All inter-node communication uses Tailscale IPs. No port forwarding. No public exposure.
- **Read before write.** Tier 1 tools (read-only) are built and tested before Tier 2 tools (write/execute) are added.
- **Every action is logged.** All tool calls are logged locally and forwarded to Splunk on EagleEye11.
- **Allowlists only.** No arbitrary command execution. Every SSH command BurrowMCP can run is explicitly defined in the server code.

---

## Network Topology

```
Claude Mobile (SolSkorp_13 / iphone-13)
    │
    │  Tailscale mesh
    ▼
Claude Desktop (EagleEye11 — 100.113.239.38)  ← BurrowMCP runs here
    │
    ├── SSH → Krypton1t3  (100.103.171.45)   Fedora Security Lab
    ├── SSH → SkorpiOm    (100.102.6.14)     Kali Linux
    └── SSH → Jynx13      (100.108.182.39)   macOS Monterey
```

---

## Tool Tiers

### Tier 1 — Read Only (Build First)
| Tool | Description |
|------|-------------|
| `get_lab_status` | Returns online/offline status of all nodes via Tailscale |
| `get_wazuh_alerts` | Pulls recent Wazuh alerts by node and severity |
| `splunk_search` | Runs a Splunk search query and returns results |
| `get_node_info` | Returns hostname, OS, uptime for a given node |

### Tier 2 — Safe Write Operations (Build Second)
| Tool | Description |
|------|-------------|
| `apt_update` | Runs `apt update && apt upgrade -y` on SkorpiOm |
| `dnf_update` | Runs `dnf update -y` on Krypton1t3 |
| `restart_service` | Restarts an allowlisted service on a specified node |

### Tier 3 — Stretch Goals
| Tool | Description |
|------|-------------|
| `reboot_node` | Reboots a node (requires confirmation token) |
| `ollama_pull` | Pulls a model update on a specified node |
| `ping_sweep` | Runs nmap ping sweep on local subnet |

---

## File Structure

```
/Volumes/Bird's Nest/BurrowMCP/
├── venv/                  # Python virtual environment (Python 3.11)
├── server.py              # Main MCP server entry point
├── tools/
│   ├── __init__.py
│   ├── lab_status.py      # Tier 1: node status tools
│   ├── wazuh.py           # Tier 1: Wazuh alert tools
│   ├── splunk.py          # Tier 1: Splunk search tools
│   └── maintenance.py     # Tier 2: apt/dnf update tools
├── config.py              # Node IPs, SSH config, allowlists
├── logs/                  # Local tool call logs
└── docs/
    ├── BurrowMCP-00-Architecture.md   ← this file
    ├── BurrowMCP-01-Session1.md
    └── ...
```

---

## Node Reference

| Hostname | Tailscale IP | OS | Role |
|----------|-------------|-----|------|
| EagleEye11 | 100.113.239.38 | macOS (M1) | Hub / BurrowMCP host / Splunk / Wazuh Manager |
| Krypton1t3 | 100.103.171.45 | Fedora Security Lab 43 | Hypervisor / pentest node |
| SkorpiOm | 100.102.6.14 | Kali Linux | Attack machine |
| Jynx13 | 100.108.182.39 | macOS Monterey | OSINT / general |

---

## SSH Strategy

BurrowMCP uses `paramiko` (Python SSH library) to connect from EagleEye11 to other nodes over Tailscale. SSH keys will be configured so EagleEye11 can connect without passwords.

Each tool that requires SSH will:
1. Connect to the target node's Tailscale IP
2. Execute only pre-approved, hardcoded commands
3. Return stdout/stderr to Claude
4. Log the action with timestamp

---

## Splunk Integration

All BurrowMCP tool calls will generate a log entry forwarded to Splunk via the Universal Forwarder. This means every Claude-initiated action in the lab becomes a searchable Splunk event — which is both good security hygiene and great portfolio documentation.

---

## Session Log Index

| Doc | Date | Summary |
|-----|------|---------|
| BurrowMCP-00-Architecture.md | 2026-05-03 | Initial architecture design |
| BurrowMCP-01-Session1.md | 2026-05-03 | Environment setup, MCP SDK install, first server |

---

*"The backbone is already in place. We're just adding layers of MCP goodness."*  
— JBird, May 2026
