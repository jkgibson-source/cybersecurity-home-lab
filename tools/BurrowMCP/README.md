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
| `BurrowMCP-00-Architecture.md` | System design and principles |
| `BurrowMCP-01` through `BurrowMCP-10` | Node onboarding, SSH setup, tool builds, Wazuh/Splunk integration |
| `BurrowMCP-11-Session11.md` | Dashboard build — auth, API layer, mobile HTML, Splunk Free, PWA |

---

## What's Next

- **Write operations** — service restart via the dashboard (one route + one button each)
- **Node detail drawer** — tap a card to expand disk + services inline
- **Splunk saved queries** — dropdown of common searches
- **PWA manifest** — full installable app with offline support

---

*Built by JBird + Shade (Claude / PAI). The Burrow is a real home lab, built from scratch in 10 weeks with old hardware, no prior Linux or Python experience, and a lot of late nights.*
