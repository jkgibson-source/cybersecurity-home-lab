# BurrowMCP — Session 9 Journal
**Date:** 2026-05-06
**Author:** JBird + Claude
**Status:** ✅ Complete — BurrowMCP SSE server live, Cloudflare tunnel established, remote endgame architecture ready

---

## Session Goal
Migrate BurrowMCP to SSE transport so it can be exposed as a remote MCP connector
accessible from SolSkorp_13 (iPhone 13) and anywhere else Claude runs.

---

## What We Accomplished

### 1. Diagnosed BurrowMCP's Current State ✅
Commands run on EagleEye11:
```bash
lsof -i -nP | grep python | grep LISTEN
cat ~/start_burrowmcp.sh
grep -r "sse|stdio|port|transport" ~/start_burrowmcp.sh
```

Findings:
- Port: `127.0.0.1:8065` (loopback only — not externally reachable)
- Transport: `stdio` (default MCP local mode, used by Claude Desktop)
- MCP SDK version: `1.27.0`
- Dependencies already included: `sse-starlette`, `uvicorn` — SSE ready with zero new installs

---

### 2. Port Conflict Discovery ✅
Port 8065 is occupied by **Splunk Web**. BurrowMCP was silently crashing on restart
due to `[Errno 48] address already in use`. Moved BurrowMCP to port **8766**.

---

### 3. Switched BurrowMCP to SSE Transport ✅
**File edited:** `/Users/EagleEye11/BurrowMCP/server.py`

```python
# Before
if __name__ == "__main__":
    mcp.run(transport="stdio")

# After
if __name__ == "__main__":
    import uvicorn
    app = mcp.sse_app()
    uvicorn.run(app, host="0.0.0.0", port=8766)
```

**Note:** `FastMCP.run()` in mcp 1.27.0 does not accept `host` or `port` kwargs directly.
Must use `mcp.sse_app()` + `uvicorn.run()` pattern.

Verified with:
```bash
lsof -i -nP | grep 8766
# Result: Python  22930  EagleEye11  TCP *:8766 (LISTEN)
```

SSE endpoint confirmed live:
```bash
curl -N http://localhost:8766/sse
# Result:
# event: endpoint
# data: /messages/?session_id=80c3a555d23c4f378a823d179b63b66b
# : ping — 2026-05-06 21:59:42.721626+00:00
```

---

### 4. Cloudflare Tunnel Established ✅
```bash
brew install cloudflared   # version 2026.3.0
cloudflared tunnel --url http://localhost:8766
```

Public URL generated:
```
https://choose-creating-environmental-stones.trycloudflare.com
```

Tunnel registered via Miami (mia08), protocol: QUIC.

**Note:** Quick tunnels (no account) are temporary — URL changes on each run.
For a permanent URL, a named tunnel with a Cloudflare account is needed (free tier available).

---

### 5. Remote Connector Wall — Strategic Decision ✅
Custom remote MCP connectors (pasting a URL into Claude's connector settings)
require **Claude Pro**. The free plan connector directory only shows
Anthropic-approved third-party apps.

**Decision:** Hold the $25 gift card. Activate Claude Pro immediately before
the NY trip (late July/August) when remote lab access will be most valuable.
BurrowMCP SSE + Cloudflare tunnel sits ready — connecting SolSkorp_13 will
take ~5 minutes once Pro is active.

---

### 6. Claude Desktop Config Updated ✅
Even though Claude for Mac (v1.6259.1) rejected the URL format, the config
was updated for when Claude Desktop (developer version) is installed:

```json
"BurrowMCP": {
  "url": "http://localhost:8766/sse"
}
```

---

## Architecture — Remote Endgame (Ready to Activate)

```
SolSkorp_13 (iPhone)
    ↓ HTTPS
Claude cloud (Anthropic)
    ↓ MCP/SSE
Cloudflare tunnel
    ↓
EagleEye11 :8766 — BurrowMCP SSE server
    ↓ SSH / Tailscale
Krypton1t3 · SkorpiOm · Jynx13
```

When Pro activates: go to claude.ai → + → Connectors → Add connector →
paste the tunnel URL + `/sse`. Done.

---

## Key Facts Documented
| Item | Value |
|---|---|
| BurrowMCP port | `8766` (moved from 8065 — Splunk conflict) |
| BurrowMCP transport | SSE via uvicorn |
| BurrowMCP bind | `0.0.0.0` (all interfaces) |
| SSE endpoint | `http://localhost:8766/sse` |
| Splunk Web port | `8065` (do not use) |
| cloudflared version | `2026.3.0` |
| Tunnel URL (session) | `https://choose-creating-environmental-stones.trycloudflare.com` |
| Claude for Mac version | `1.6259.1 (5095e7)` |
| MCP SDK | `1.27.0` |

---

## start_burrowmcp.sh — Still Valid
The wrapper script still works for starting BurrowMCP. It now launches
the SSE server instead of stdio. No changes needed to the script itself.

```bash
~/start_burrowmcp.sh &
# Starts uvicorn on 0.0.0.0:8766
# Keep the terminal tab open — uvicorn runs in foreground
```

---

## Parked for Session 10
1. **Splunk license migration — DEADLINE MAY 17** ⚠️ (critical)
2. Named Cloudflare tunnel (persistent URL, no account or free account)
3. Claude Desktop (developer app) install — separate from Claude for Mac
4. EagleEye11 internal drive cleanup (92% full)
5. Wazuh noise on Krypton1t3 — cause TBD
6. BurrowMCP as a launchd service on EagleEye11 (auto-start on boot)
7. APP_NAME_MAP expansion for BurrowVoice

## Before NY Trip (Aspirational)
- **Claude Pro** — activate with $25 gift card immediately before trip for remote lab access
- **Custom domain + named Cloudflare tunnel** — `burrow.yourdomain.com/sse` as permanent
  connector URL. Cloudflare account is free. Domain ~$10-15/yr via Cloudflare Registrar
  (at-cost, no markup) or Porkbun. Named tunnel setup:
  ```bash
  cloudflared tunnel login
  cloudflared tunnel create burrow
  cloudflared tunnel route dns burrow burrow.yourdomain.com
  cloudflared tunnel run --url http://localhost:8766 burrow
  ```
  Once Pro + domain are in place, SolSkorp_13 remote access is ~5 minutes of setup.

---

## Notes
- BurrowMCP SSE server must be running before Cloudflare tunnel is started
- Quick tunnel URL is temporary — regenerates each session until named tunnel is set up
- Pro activation timing: immediately before NY trip for maximum value

---

*"The tunnel is dug. The Burrow reaches the surface.
It just needs the door to open."*
— BurrowMCP Session 9, May 2026

**Tags:** #BurrowMCP #Session9 #SSE #uvicorn #cloudflared #CloudflareTunnel
#remoteAccess #SolSkorp13 #endgame #port8766 #splunkConflict #ClaudeForMac
#ClaudePro #homelab #SOC #transport #FastMCP
