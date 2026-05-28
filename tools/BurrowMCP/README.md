# BurrowMCP 🦅🦂

**A custom MCP server + mobile web dashboard for The Burrow home lab.**  
Built from scratch. Runs on a Mac Mini. Accessible from anywhere.

---

## What It Is

BurrowMCP has two modes:

**MCP Server** — exposes The Burrow's tools to Claude (Desktop + iOS). Ask Claude "are all nodes up?" or "what's Krypton1t3's disk usage?" and it calls the real lab, no hallucination.

**Web Dashboard** — a mobile-responsive control panel at `theburrow.dev`. Node health, Wazuh alerts, and Splunk search — no AI session, no token burn, just your lab on your phone.

---

## The Lab

| Node | OS | Role |
|------|----|------|
| EagleEye11 | macOS M1 | Hub — BurrowMCP host, Splunk, Wazuh Manager |
| Krypton1t3 | Fedora Security Lab 44 | Hypervisor / creative workstation |
| SkorpiOm | Kali Linux | Attack machine |
| Jynx13 | macOS Monterey | OSINT / general |

All inter-node communication runs over Tailscale. No port forwarding. No public exposure beyond the Cloudflare tunnel to EagleEye11.

---

## Dashboard Features

- **Node cards** — live status (ONLINE / LOCAL / TIMEOUT / OFFLINE), IP, role for all four nodes
- **Wazuh** — recent security alerts pulled on page load
- **Splunk search** — type any SPL query, get results inline
- **Auto-refresh** — node status updates every 60 seconds
- **Mobile-first** — designed for 375px, works great on desktop too
- **No CDN, no external JS** — single self-contained HTML file, works behind strict firewalls
- **PWA-ready** — add to phone home screen, looks and feels like a native app

---

## Architecture

```
Phone / Browser (theburrow.dev)
    │  HTTPS
    ▼
Cloudflare Tunnel
    │
    ▼
EagleEye11 :8766 (uvicorn / Starlette)
    ├── GET /           → redirect to /dashboard
    ├── GET/POST /login → PAT cookie auth
    ├── GET /dashboard  → single-file HTML
    ├── GET /api/*      → JSON wrappers around tool functions
    ├── POST /api/splunk → Splunk REST API (localhost:8089)
    │
    ├── [MCP OAuth — untouched, used by Claude Desktop]
    │   └── /sse  ← Claude Desktop / Claude iOS connect here
    │
    └── [SSH over Tailscale → Krypton1t3, SkorpiOm, Jynx13]
```

Single `server.py` — one process, two personalities. The `--http` flag enables the dashboard and API layer. Without it, the server runs in stdio MCP mode for Claude Desktop.

---

## API Reference

All `/api/*` routes require a valid `burrow_session` cookie. Returns `application/json`.

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/status` | All nodes — name, IP, status, role |
| GET | `/api/node/{name}/disk` | Disk usage via `df -h` |
| GET | `/api/node/{name}/services` | Failed systemd services |
| GET | `/api/node/{name}/info` | Hostname + uptime |
| GET | `/api/wazuh` | Recent Wazuh alerts |
| POST | `/api/splunk` | Run a SPL query — body: `{"query": "..."}` |

---

## Setup

### Prerequisites

- Python 3.11
- Starlette, uvicorn, httpx, requests (see `requirements.txt`)
- Tailscale on all nodes
- SSH key at `~/.ssh/burrowmcp_ed25519` (EagleEye11 → other nodes)
- Cloudflare tunnel pointed at `localhost:8766`
- Splunk running locally (free license — no credentials needed)
- Wazuh Manager running locally

### Secrets

Create `config.secrets.py` in the project root (gitignored):

```python
DASHBOARD_TOKEN = "your-token-here-at-least-32-chars"
SPLUNK_USER = ""   # leave empty for Splunk Free license
SPLUNK_PASS = ""
```

Generate a token: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`

### Running

**HTTP mode** (dashboard + MCP over SSE):
```bash
python server.py --http
```

**stdio mode** (MCP for Claude Desktop — no dashboard):
```bash
python server.py
```

### Claude Desktop config

```json
"BurrowMCP": {
  "command": "/bin/zsh",
  "args": ["/path/to/burrowmcp_start.sh"]
}
```

Use a wrapper script if your project path contains special characters (apostrophes, spaces).

---

## Security Model

- **Auth:** single personal access token stored in `config.secrets.py` (gitignored), never logged, never rendered in HTML
- **Cookie flags:** `HttpOnly`, `SameSite=lax`
- **OAuth separation:** dashboard auth (`burrow_session` cookie) and MCP OAuth (`/sse`) share zero code and have no interaction
- **No write operations in v1** — all API routes are read-only; write ops are architecturally planned but not shipped
- **Allowlists only** — SSH commands are explicitly defined; no arbitrary execution
- **Tailscale-only inter-node traffic** — nodes are never directly internet-exposed

---

## MCP Tools

| Tool | What it does |
|------|-------------|
| `get_lab_status` | Ping all nodes via Tailscale, return status |
| `get_node_info` | Hostname + uptime via SSH |
| `check_disk_space` | `df -h` output via SSH |
| `check_failed_services` | `systemctl --failed` via SSH |
| `get_wazuh_alerts` | Recent alerts from local Wazuh Manager |
| `splunk_search` | Run SPL query against local Splunk REST API |

---

## Session Journals

The `docs/` folder has a full build log — every session, every decision, every mistake and fix, from zero to live.

| Doc | What happened |
|-----|---------------|
| [BurrowMCP-00-Architecture.md](docs/BurrowMCP-00-Architecture.md) | Defined the system architecture, tool tiers, node topology, and security philosophy before writing a single line of code. |
| [BurrowMCP-01-Session1.md](docs/BurrowMCP-01-Session1.md) | Set up the Python 3.11 environment, installed the MCP SDK, and got a minimal BurrowMCP server starting cleanly on EagleEye11. |
| [BurrowMCP-02-Session2.md](docs/BurrowMCP-02-Session2.md) | Wired BurrowMCP into Claude Desktop and confirmed the first end-to-end tool call from Claude to the lab. |
| [BurrowMCP-03-Session3.md](docs/BurrowMCP-03-Session3.md) | Replaced hardcoded stubs with live Tailscale ping logic, wrote `config.py`, and moved tool logic into proper modules. |
| [BurrowMCP-04-Session4.md](docs/BurrowMCP-04-Session4.md) | Distributed SSH keys to all remote nodes and built the first live SSH tools: `get_node_info()`, `check_disk_space()`, and `check_failed_services()`. |
| [BurrowMCP-05-Session5.md](docs/BurrowMCP-05-Session5.md) | Built the structured logging pipeline, added `splunk_search()`, distributed the SSH key to Jynx13, and fixed the `df` macOS incompatibility. |
| [BurrowMCP-06-Session6.md](docs/BurrowMCP-06-Session6.md) | Implemented `get_wazuh_alerts()` via `docker exec` into the Wazuh manager container and confirmed live alert data flowing through Claude Desktop. |
| [BurrowMCP-07-Session7.md](docs/BurrowMCP-07-Session7.md) | Reconnected all four Wazuh agents (version mismatch + Tailscale IP fix) and resolved the Twingate/Tailscale routing conflict on Krypton1t3. |
| [BurrowMCP-08-Session8.md](docs/BurrowMCP-08-Session8.md) | Diagnosed and neutralized the Twingate zombie restart loop on Krypton1t3, completed SSH key distribution, and got BurrowVoice launching apps across all nodes. |
| [BurrowMCP-09-Session9.md](docs/BurrowMCP-09-Session9.md) | Migrated BurrowMCP to SSE transport and established a Cloudflare tunnel, laying the groundwork for remote mobile access. |
| [BurrowMCP-10-Session10.md](docs/BurrowMCP-10-Session10.md) | Deployed BurrowMCP on Jynx13 as a fully operational travel/commander node using stdio mode over the Tailscale mesh. |
| [BurrowMCP-11-Session11.md](docs/BurrowMCP-11-Session11.md) | Got Splunk accessible from Jynx13 via SSH tunnel to EagleEye11, maintaining the zero-open-ports security model. |
| [BurrowMCP-12-Session12.md](docs/BurrowMCP-12-Session12.md) | Established Jynx13 ↔ Krypton1t3 SSH connectivity and tuned WatchYourLAN to stop dropping Tailscale nodes. |
| [BurrowMCP-13-Session13.md](docs/BurrowMCP-13-Session13.md) | Audited SkorpiOm's Splunk forwarder, created a dedicated `wazuh` index, and wired Wazuh alerts into Splunk. |
| [BurrowMCP-14-Session14.md](docs/BurrowMCP-14-Session14.md) | Fixed `splunk_tools.py` on both nodes, configured BurrowMCP to auto-start via launchd, and built the Wazuh dashboard in Splunk. |
| [BurrowMCP-15-Session15.md](docs/BurrowMCP-15-Session15.md) | Built and deployed `run_burrow_command()` — a whitelisted, safety-gated remote command execution pipeline — on Jynx13. |
| [BurrowMCP-16-Session16.md](docs/BurrowMCP-16-Session16.md) | First full session commanding the lab from Jynx13; fixed the self-reporting status bug and hardened SkorpiOm's unattended remote access. |
| [BurrowMCP-17-Session17.md](docs/BurrowMCP-17-Session17.md) | Completed Krypton1t3 auto-login via LightDM and built the OAuth + SSE stack for Claude Mobile, stopping at the domain routing wall. |
| [BurrowMCP-18-Session18.md](docs/BurrowMCP-18-Session18.md) | Handoff doc capturing the full Cloudflare tunnel / OAuth / SSE state and the specific MCP host-header validation blocker to solve next. |
| [BurrowMCP-19-Session19.md](docs/BurrowMCP-19-Session19.md) | Solved the MCP host-header validation blocker and got OAuth + SSE working end-to-end through the Cloudflare tunnel for Claude Mobile. |
| [BurrowMCP-20-Session20.md](docs/BurrowMCP-20-Session20.md) | Fixed Jynx13's Krypton1t3 SSH failure (wrong service account), confirmed Splunk's migration to the free tier, and resolved SkorpiOm's cosmetic networking failure. |
| [BurrowMCP-21-Session21.md](docs/BurrowMCP-21-Session21.md) | Fixed `splunk_tools.py` after the REST API hit the Splunk Free license wall, resolved a license violation from over-ingestion, and brought Krypton1t3's forwarder under full remote control. |
| [BurrowMCP-22-Session22.md](docs/BurrowMCP-22-Session22.md) | Built and shipped the mobile web dashboard at `theburrow.dev` — node status, Wazuh alerts, and Splunk search — and wired BurrowMCP into Claude for Mac/iOS via Dispatch. |
| [BurrowMCP-Jynx13-Handoff.md](docs/BurrowMCP-Jynx13-Handoff.md) | Migration handoff document cataloging known EagleEye11-specific artifacts and the SSH service-account bug to resolve when deploying BurrowMCP on Jynx13. |
| [BurrowMCP-Tool_List.md](docs/BurrowMCP-Tool_List.md) | Quick-reference card of all BurrowMCP tools and the natural-language prompts to invoke them through Claude Desktop. |
| [BurrowMCP_planning_summary.md](docs/BurrowMCP_planning_summary.md) | Original pre-project planning document defining the core concept, guiding principles, and tiered tool architecture before any code was written. |

---

## What's Next

- **Write operations** — service restart via the dashboard (one route + one button each)
- **Node detail drawer** — tap a card to expand disk + services inline
- **Splunk saved queries** — dropdown of common searches
- **PWA manifest** — full installable app with offline support

---

*Built by JBird + Shade (Claude / PAI). The Burrow is a real home lab, built from scratch in 10 weeks with old hardware, no prior Linux or Python experience, and a lot of late nights.*
