# BurrowMCP Session 17 Journal
**Date:** Sunday, May 10, 2026
**Node:** Jynx13 (commander) + EagleEye11
**Operator:** JBird

---

## Session Overview

Two-track session: finished Krypton1t3's unattended-boot hardening (carried over from Session 16), then made a serious push toward the long-awaited goal of connecting BurrowMCP remotely via SolSkorp_13. Got further than ever before — named Cloudflare tunnel running, OAuth layer built, SSE confirmed working locally — stopped at the domain wall. Session 18 will finish the job.

---

## 1. Krypton1t3 — Auto-Login (LightDM)

**Problem:** Krypton1t3 would sit at a login screen after an unattended reboot, blocking all remote desktop access.

**Discovery:** `systemctl status display-manager` revealed Krypton1t3 uses **LightDM**, not GDM as initially assumed. A `/etc/gdm/custom.conf` was created by mistake and subsequently removed.

**Fix:** Edited `/etc/lightdm/lightdm.conf`:
```ini
[Seat:*]
autologin-user=SuperSkorp_7
autologin-user-timeout=0
```

**Result:** Krypton1t3 now boots directly to desktop as `SuperSkorp_7`. ✅

---

## 2. Krypton1t3 — GNOME Keyring Fix

**Problem:** After auto-login, apps that use the GNOME keyring (Brave browser, Claude Desktop) prompted for keyring password on launch — a blocker for unattended operation.

**Root cause:** The keyring is normally unlocked during the login screen password entry. Auto-login bypasses this, so the keyring stays locked.

**Fix:** Removed the existing login keyring so it gets recreated with no password:
```bash
rm ~/.local/share/keyrings/login.keyring
```

On next launch, apps recreate the keyring with no password and never prompt again.

**Security note:** Credentials stored in the keyring sit unencrypted on disk. Acceptable tradeoff given physical security model (home lab) and the layered network security already in place (Tailscale, SSH keys, Wazuh).

**Result:** Claude Desktop and Brave launch cleanly after unattended reboot. ✅

---

## 3. Krypton1t3 — Remote Access Summary (Post-Session)

| Tool | Status | Notes |
|------|--------|-------|
| RustDesk | ✅ Auto-starts on boot | Primary remote desktop — arm when leaving the house |
| SSH | ✅ Always available | Full shell access anytime |
| x0vncserver | ⚠️ Manual start only | Not worth further troubleshooting |

Krypton1t3 is now fully hardened for unattended operation. ✅

---

## 4. BurrowMCP SSE — Remote Access Push

### Goal
Connect SolSkorp_13 (iPhone 13) to BurrowMCP via claude.ai custom connector, using a Cloudflare tunnel as the public endpoint. This has been the endgame since Session 9.

### What Changed Since Session 9
The `__main__` block in `server.py` had been reverted to `stdio` transport for daily local use. Now that Claude Pro is active, it was time to flip back to SSE and go for it.

### Steps Completed

**4a. server.py — Switched back to SSE**

Updated `/Volumes/Bird's Nest/BurrowMCP/server.py` `__main__` block:
```python
if __name__ == "__main__":
    import uvicorn
    app = mcp.sse_app()
    uvicorn.run(app, host="0.0.0.0", port=8766)
```

**4b. start_burrowmcp.sh — Pointed to Bird's Nest**

Updated script to use the correct path:
```bash
exec "/Volumes/Bird's Nest/BurrowMCP/venv/bin/python3.11" "/Volumes/Bird's Nest/BurrowMCP/server.py"
```

**4c. Claude Desktop config — Removed stdio BurrowMCP entry**

Claude Desktop's local MCP config was still launching BurrowMCP via stdio, causing port 8766 conflicts every time Claude Desktop started. Removed the BurrowMCP entry from `claude_desktop_config.json` entirely. Also fixed a trailing comma JSON parse error left over from the edit.

**4d. OAuth layer added to server.py**

Claude.ai requires OAuth for custom connectors. Added a minimal OAuth implementation to the Starlette app wrapping the SSE server:

```python
if __name__ == "__main__":
    import uvicorn
    import secrets
    from starlette.applications import Starlette
    from starlette.routing import Route, Mount
    from starlette.responses import JSONResponse, RedirectResponse

    auth_codes = {}

    async def oauth_metadata(request):
        base = str(request.base_url).rstrip("/")
        return JSONResponse({
            "issuer": base,
            "authorization_endpoint": f"{base}/oauth/authorize",
            "token_endpoint": f"{base}/oauth/token",
            "registration_endpoint": f"{base}/oauth/register",
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code"],
            "code_challenge_methods_supported": ["S256"]
        })

    async def oauth_register(request):
        return JSONResponse({
            "client_id": "burrow-client",
            "client_secret": "burrow-secret",
            "redirect_uris": [],
            "grant_types": ["authorization_code"],
            "response_types": ["code"]
        })

    async def oauth_authorize(request):
        redirect_uri = request.query_params.get("redirect_uri")
        state = request.query_params.get("state", "")
        code = secrets.token_urlsafe(16)
        auth_codes[code] = True
        return RedirectResponse(f"{redirect_uri}?code={code}&state={state}")

    async def oauth_token(request):
        return JSONResponse({
            "access_token": "burrow-token",
            "token_type": "bearer",
            "expires_in": 86400
        })

    mcp_app = mcp.sse_app()
    app = Starlette(routes=[
        Route("/.well-known/oauth-authorization-server", oauth_metadata),
        Route("/oauth/register", oauth_register, methods=["POST"]),
        Route("/oauth/authorize", oauth_authorize),
        Route("/oauth/token", oauth_token, methods=["POST"]),
        Mount("/", app=mcp_app),
    ])
    uvicorn.run(app, host="0.0.0.0", port=8766, proxy_headers=True, forwarded_allow_ips="*")
```

**4e. Cloudflare named tunnel created**

- Created free Cloudflare account (jk.gibson@gmail.com)
- Created named tunnel `burrow` via dashboard GUI
- Tunnel ID: `5f70128f-e634-4c54-9749-9ee2af6a94e3`
- Connected successfully: 1 active replica, 4 edge connections via Miami (mia02, mia08, mia09)
- Run command: `cloudflared tunnel run --token <token>`

**4f. The wall: domain required for public routing**

Named tunnels require a domain in your Cloudflare account to add a public route. Without a domain, the tunnel connects but has no public URL to expose.

Quick tunnels (`trycloudflare.com`) work but reject SSE connections with "Invalid Host header" — a known Cloudflare limitation.

**Confirmed working:**
- ✅ BurrowMCP SSE server on localhost:8766
- ✅ OAuth endpoints responding correctly
- ✅ Named tunnel connecting to Cloudflare edge
- ✅ `/oauth/register` returning correct JSON through tunnel

**Blocked on:**
- ❌ No domain → no public route → claude.ai can't reach the tunnel

---

## 5. The Fix (Session 18)

Get a domain. That's it. One purchase unlocks everything.

**Recommended:** `burrow.dev` via Porkbun (~$10/yr)

**Session 18 steps (5 minutes once domain exists):**
1. Add domain to Cloudflare account
2. Add public route to `burrow` tunnel → `burrow.dev`
3. Update connector URL in claude.ai to `https://burrow.dev/sse`
4. Connect on SolSkorp_13

---

## Cloudflare Account Details
| Item | Value |
|------|-------|
| Account | jk.gibson@gmail.com |
| Account ID | 5451bf22ef37e5500240ed3b3f9dfdcd |
| Tunnel name | burrow |
| Tunnel ID | 5f70128f-e634-4c54-9749-9ee2af6a94e3 |
| Token name | BurrowMCP-tunnel |
| cloudflared version | 2026.3.0 |

---

## Pending / Next Session
- [ ] **Session 18 priority:** Buy `burrow.dev` (or similar) on Porkbun → add to Cloudflare → route tunnel → connect SolSkorp_13
- [ ] Splunk free license migration (due ~May 17) ⚠️
- [ ] WatchYourLAN BurrowMCP tool (SSH into Krypton1t3 → curl localhost)
- [ ] Wire Telegram into Hermes on Krypton1t3

---

## Tags
`#burrowmcp` `#session17` `#krypton1t3` `#autologin` `#lightdm` `#keyring` `#sse` `#cloudflare` `#oauth` `#remote-access` `#solskorp13` `#eagleeye11` `#domain` `#porkbun` `#mempalace`
