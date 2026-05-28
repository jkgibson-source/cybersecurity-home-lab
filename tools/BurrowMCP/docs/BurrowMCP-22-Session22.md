# BurrowMCP — Session 22 Journal
**Date:** 2026-05-28  
**Author:** JBird + Claude (Shade)  
**Status:** ✅ Complete — Mobile web dashboard live at theburrow.dev

---

## Session Goal

Build a mobile-responsive web dashboard at `theburrow.dev` that exposes all BurrowMCP tool functions — lab status, disk, services, Wazuh alerts, Splunk search — without requiring Claude, burning AI tokens, or opening a terminal. A single personal access token gates everything. Read-only in v1, architected for write operations to be one-route additions.

---

## What We Accomplished

### 1. Claude Dispatch (MCP over stdio) — wired up first ✅

Before the dashboard, we connected BurrowMCP to Claude for Mac's native Dispatch integration. The server already ran in HTTP mode for the Cloudflare tunnel, but Dispatch uses stdio. The path to `server.py` contained a `'` (Bird's Nest volume), which caused Claude Desktop to split the shell argument.

**Fix:** Created a clean wrapper script at `/Users/EagleEye11/burrowmcp_start.sh` (no special characters in path) and pointed `claude_desktop_config.json` there. BurrowMCP tools now appear natively in Claude for Mac and Claude iOS.

```json
"BurrowMCP": {
  "command": "/bin/zsh",
  "args": ["/Users/EagleEye11/burrowmcp_start.sh"]
}
```

### 2. Tailscale ping fix — TIMEOUT for live nodes ✅

`tailscale ping` without `--c 1` runs indefinitely looking for a direct path. Both Krypton1t3 and SkorpiOm route via DERP relay and never get a direct connection, so the lab status check hung until timeout.

**Fix:** Added `"--c", "1"` to stop after the first pong. Also added `TimeoutExpired.stdout` handling to catch the partial output when ping is killed early.

```python
result = subprocess.run(
    [TAILSCALE_BIN, "ping", "--c", "1", tailscale_name],
    capture_output=True, text=True,
    timeout=TAILSCALE_PING_TIMEOUT + 2, env=env
)
```

### 3. Secrets isolation via config.secrets.py ✅

ApertureOscillation (tactical vs. strategic scope analysis) revealed that the real security risk is git leakage, not process-level token exposure. Hardcoding `DASHBOARD_TOKEN` in `config.py` is fine locally but dangerous if the file is ever shared or pasted. Env vars require per-node `.zshrc` setup.

**Resolution:** `config.secrets.py` (gitignored) loaded via `importlib.util`, imported by `config.py`. All secrets — `DASHBOARD_TOKEN`, `SPLUNK_USER`, `SPLUNK_PASS` — live there. `config.py` remains shareable. The `.gitignore` entry is the security boundary.

```python
# config.py loads secrets without normal import (dotted filename)
_secrets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.secrets.py")
_spec = _importlib_util.spec_from_file_location("config_secrets", _secrets_path)
```

### 4. Dashboard build — auth, API layer, HTML ✅

All new routes live inside the `--http` branch of `server.py`. Zero impact on the MCP OAuth path used by Claude Desktop. Zero new Python dependencies.

**Auth:**
- `GET /login` — renders login form
- `POST /login` — checks token via `secrets.compare_digest`, sets `burrow_session` cookie (`HttpOnly`, `SameSite=lax`)
- All `/api/*` and `/dashboard` routes check the cookie; missing or wrong → 401/302

**API layer** (all return `application/json`):

| Route | Tool |
|-------|------|
| `GET /api/status` | `get_lab_status()` — all 4 nodes |
| `GET /api/node/{name}/disk` | `check_disk_space()` |
| `GET /api/node/{name}/services` | `check_failed_services()` |
| `GET /api/node/{name}/info` | `get_node_info()` |
| `GET /api/wazuh` | `get_wazuh_alerts()` |
| `POST /api/splunk` | `splunk_search()` |

**Dashboard HTML** — single self-contained f-string, no CDN, no external JS:
- Dark theme, mobile-first, 375px primary viewport
- 2-column node grid on mobile → 4 columns on desktop (≥900px)
- Each node card: name, IP, status dot (green/yellow/red), role
- Wazuh alerts section (live fetch on load)
- Splunk search textarea + Run button
- Auto-refresh every 60 seconds; "last updated" timestamp on each cycle

**Root redirect:** `GET /` → 307 → `/dashboard` → 302 → `/login` (unauthenticated). Opening `theburrow.dev` with no path now lands on the login screen instead of a 404.

### 5. Splunk — free license, no credentials ✅

Splunk Free has no authentication requirement on its REST API (`localhost:8089`). Updated `splunk_tools.py` to skip the auth header when credentials are empty:

```python
AUTH = (SPLUNK_USER, SPLUNK_PASS) if (SPLUNK_USER and SPLUNK_PASS) else None
```

`config.secrets.py` leaves `SPLUNK_USER = ""` and `SPLUNK_PASS = ""`. Auth header is never sent. Searches run clean.

### 6. Added to phone home screen ✅

`theburrow.dev` opens, logs in via PAT stored in Bitwarden, and is pinned to the SolSkorp_13 home screen as a PWA-style icon. Looks and feels like a native app. The Burrow is in your pocket.

---

## Architecture After This Session

```
Phone / Browser (theburrow.dev)
    │  HTTPS
    ▼
Cloudflare Tunnel
    │
    ▼
EagleEye11 :8766 (uvicorn / Starlette)
    ├── GET /           → 307 → /dashboard
    ├── GET/POST /login → PAT cookie auth
    ├── GET /dashboard  → single-file HTML (auth-gated)
    ├── GET /api/*      → JSON wrappers around existing tools (auth-gated)
    ├── POST /api/splunk → Splunk REST API → localhost:8089
    │
    ├── [MCP OAuth — untouched]
    │   ├── /.well-known/oauth-authorization-server
    │   ├── /oauth/register, /oauth/authorize, /oauth/token
    │   └── /sse  ← Claude Desktop connects here
    │
    └── [SSH / Tailscale → Krypton1t3, SkorpiOm, Jynx13]
```

---

## Files Changed This Session

| File | Change |
|------|--------|
| `server.py` | Added `/login`, `/dashboard`, `/api/*`, `GET /` routes inside `--http` branch |
| `config.py` | Added `importlib.util` loading of `config.secrets.py`; imports `DASHBOARD_TOKEN`, `SPLUNK_USER`, `SPLUNK_PASS` |
| `config.secrets.py` | **New** (gitignored) — holds `DASHBOARD_TOKEN` (43 chars), `SPLUNK_USER`, `SPLUNK_PASS` |
| `.gitignore` | **New** — `config.secrets.py`, `__pycache__/`, `venv/`, `logs/`, `.DS_Store` |
| `tools/lab_status.py` | Added `--c 1` to Tailscale ping; fixed `TimeoutExpired.stdout` handling |
| `tools/splunk_tools.py` | `AUTH` now `None` when credentials are empty (Splunk Free support) |
| `/Users/EagleEye11/burrowmcp_start.sh` | **New** — clean-path wrapper for Claude Desktop stdio MCP config |

---

## Verification Summary

All 36 ISCs passed. Full evidence in `ISA.md → ## Verification`.

Key checks:
- `GET /api/status` unauthenticated → **401**
- `GET /dashboard` unauthenticated → **302 /login**
- `POST /login` correct token → **302 /dashboard** + `HttpOnly` cookie
- All 4 nodes returned with `name`, `ip`, `status`, `role` keys
- `GET /api/node/NoSuchNode/disk` → **404** (not 500)
- `curl /dashboard | grep -E '<(link|script).*http'` → **zero matches** (no CDN)
- Server startup stdout → **DASHBOARD_TOKEN value absent**
- `POST /oauth/token` without cookie → **400** (dashboard auth never touches OAuth)
- `/api/node/EagleEye11/disk` → runs **locally** (no SSH for `is_local=True` node)

---

## What's Next (v2 ideas)

- **Write operations** — service restart button: one API route (`POST /api/node/{name}/service/{svc}/restart`) + one button per card. The confirmation token pattern already exists in `config.py`.
- **Node detail drawer** — tap a card to expand disk + services inline, without a separate page.
- **Splunk saved queries** — dropdown of common searches (failed logins, Wazuh events by severity).
- **Wazuh severity filter** — show critical/high only by default, expandable.
- **PWA manifest** — `manifest.json` + service worker for true offline-capable install.
