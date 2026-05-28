# Session 18 Handoff — BurrowMCP Remote Access
**Date:** May 10, 2026

## What's Working
- `theburrow.dev` domain registered (Porkbun), transferred to Cloudflare nameservers ✅
- Cloudflare named tunnel `burrow` connected, healthy, 4 Miami edge connections ✅
- Tunnel route: `theburrow.dev → http://localhost:8080` (nginx) ✅
- CNAME record: `@` → `5f70128f-e634-4c54-9749-9ee2af6a94e3.cfargotunnel.com` (proxied) ✅
- SSL: Flexible mode ✅
- OAuth endpoints responding correctly through tunnel ✅
- BurrowMCP SSE works on `localhost:8766` directly ✅
- nginx running on 8080, proxying to 8766, Host header set to `localhost` ✅

## The Remaining Problem
MCP library v1.27.1 has strict host header validation in `sse.py` — it rejects any request where the host doesn't match its internal expectation, even when nginx rewrites the Host header to `localhost`. Error: `Invalid Host header`.

## What to Try Next Session
1. **Pin MCP to an older version** that doesn't have strict host validation:
   ```bash
   "/Volumes/Bird's Nest/BurrowMCP/venv/bin/pip3.11" install mcp==1.2.0
   ```
2. **Patch the MCP SSE source directly** — find and comment out the host validation in:
   `/Volumes/Bird's Nest/BurrowMCP/venv/lib/python3.11/site-packages/mcp/server/sse.py`
   Look for `Invalid Host header` string and neutralize the check.
3. **Switch to streamable HTTP transport** (`mcp.streamable_http_app()`) — fix the `Task group not initialized` error by using `anyio.from_thread` properly.

## Current server.py State
- Located at: `/Volumes/Bird's Nest/BurrowMCP/server.py`
- Backup at: `/Volumes/Bird's Nest/BurrowMCP/server.py.bak`
- `__main__` block uses `mcp.sse_app()` wrapped in Starlette with OAuth layer
- nginx config: `/opt/homebrew/etc/nginx/nginx.conf`
- Tunnel token in Cloudflare dashboard (BurrowMCP-tunnel)
- Tunnel ID: `5f70128f-e634-4c54-9749-9ee2af6a94e3`

## Startup Sequence (once fixed)
```bash
~/start_burrowmcp.sh          # Terminal 1
brew services start nginx      # (already running as service)
cloudflared tunnel --config ~/.cloudflared/config.yml run --token <token>  # Terminal 2
```
