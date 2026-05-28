# BurrowMCP Session 18 Journal
**Date:** May 10, 2026  
**Node:** EagleEye11  
**Focus:** BurrowMCP Remote Access via Cloudflare Tunnel + Claude Mobile

---

## Session Goal
Get BurrowMCP accessible from SolSkorp_13 (iPhone 13) via the Claude mobile app, using the `theburrow.dev` Cloudflare tunnel with OAuth authentication.

---

## What Was Already Working (Coming In)
- `theburrow.dev` registered at Porkbun, transferred to Cloudflare nameservers
- Cloudflare named tunnel `burrow` connected, 4 Miami edge connections healthy
- Tunnel route: `theburrow.dev → http://localhost:8080` (nginx)
- nginx proxying to uvicorn on port 8766
- BurrowMCP SSE working on `localhost:8766` directly
- OAuth endpoints responding through tunnel
- SSL via Let's Encrypt (Cloudflare flexible mode)

---

## Problems Solved This Session

### 1. Host Header Validation (MCP v1.27.1)
**Problem:** `Invalid Host header` error — MCP's `transport_security.py` was rejecting requests where the Host didn't match allowed hosts.  
**Root cause:** `TransportSecuritySettings` defaults to `enable_dns_rebinding_protection=True`.  
**Fix:** Pass `transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False)` to `FastMCP()` at init.  
**Rationale:** DNS rebinding protection is a localhost-exposure defense. With Cloudflare + OAuth in front, it's not needed and actively blocks legitimate tunnel traffic.

```python
from mcp.server.transport_security import TransportSecuritySettings
mcp = FastMCP("BurrowMCP", transport_security=TransportSecuritySettings(
    enable_dns_rebinding_protection=False
))
```

---

### 2. OAuth Metadata Using HTTP Instead of HTTPS
**Problem:** `oauth_metadata` was building URLs from `request.base_url`, which returned `http://` (the internal nginx→uvicorn hop). The Claude app saw `http://` OAuth endpoints and refused to launch the browser flow.  
**Fix:** Hardcode `base = "https://theburrow.dev"` in `oauth_metadata` and `oauth_protected_resource`.

```python
async def oauth_metadata(request):
    base = "https://theburrow.dev"
    return JSONResponse({
        "issuer": base,
        "authorization_endpoint": f"{base}/oauth/authorize",
        ...
    })
```

---

### 3. Missing `/.well-known/oauth-protected-resource` Route
**Problem:** Claude app was hitting `/.well-known/oauth-protected-resource` and `/.well-known/oauth-protected-resource/sse` and getting 404. Without these, the OAuth discovery loop aborted.  
**Fix:** Added `oauth_protected_resource` handler and registered both routes.

```python
async def oauth_protected_resource(request):
    base = "https://theburrow.dev"
    return JSONResponse({
        "resource": base,
        "authorization_servers": [base],
        "bearer_methods_supported": ["header"],
        "scopes_supported": []
    })
```

Routes added:
```python
Route("/.well-known/oauth-protected-resource", oauth_protected_resource),
Route("/.well-known/oauth-protected-resource/sse", oauth_protected_resource),
```

---

### 4. `oauth_register` Not Echoing `redirect_uris`
**Problem:** Claude app sent `redirect_uris: ["https://claude.ai/api/mcp/auth_callback"]` during dynamic client registration, but the server returned `redirect_uris: []`. The app had no valid redirect URI and aborted the OAuth flow.  
**Fix:** Read and echo back the redirect URIs from the request body.

```python
async def oauth_register(request):
    body = await request.json()
    redirect_uris = body.get("redirect_uris", [])
    return JSONResponse({
        "client_id": "burrow-client",
        "client_secret": "<value>",
        "redirect_uris": redirect_uris,
        "grant_types": ["authorization_code"],
        "response_types": ["code"]
    })
```

---

### 5. `oauth_token` Code Validation Bug (Indentation)
**Problem:** `del auth_codes[code]` and the success `return JSONResponse(...)` were at the wrong indentation level — outside the function body — causing `SyntaxError: 'return' outside function`.  
**Fix:** Used Python line-level rewrite script (nano kept mangling indentation).

```python
async def oauth_token(request):
    body = await request.form()
    code = body.get("code")

    if not code or code not in auth_codes:
        return JSONResponse(
            {"error": "invalid_grant"},
            status_code=400
        )

    del auth_codes[code]  # single use

    return JSONResponse({
        "access_token": secrets.token_urlsafe(32),
        "token_type": "Bearer",
        "expires_in": 86400,
        "scope": ""
    })
```

---

### 6. nginx Not Forwarding Authorization Header
**Problem:** nginx was not passing `Authorization: Bearer <token>` to uvicorn. Added to all location blocks.  
**Fix:**
```nginx
proxy_set_header Authorization $http_authorization;
```

---

### 7. Streamable HTTP Transport — Dead End
**Attempted:** Switched from `mcp.sse_app()` to `mcp.streamable_http_app()` per MCP spec 2025-03-26 which deprecates standalone SSE in favor of Streamable HTTP.  
**Result:** `RuntimeError: Task group is not initialized. Make sure to use run().`  
**Root cause:** `streamable_http_app()` requires MCP's own event loop management via `mcp.run()` and cannot be mounted inside an external Starlette app.  
**Decision:** Reverted to SSE transport (`mcp.sse_app()`). SSE is deprecated in the spec but fully functional.

**Key finding from investigation:**
- `streamable_http_path` is a FastMCP init parameter (default: `/mcp`)
- `streamable_http_app()` takes no parameters — path set at `FastMCP()` init
- The app internally mounts at `/mcp`, Starlette strips the prefix, causing 404s

---

## Current State of `server.py` OAuth Flow

Full OAuth sequence now working (confirmed in logs):
```
POST /sse                                    → 405 (correct, probe)
GET  /.well-known/oauth-protected-resource  → 200 ✅
GET  /.well-known/oauth-authorization-server → 200 ✅
POST /oauth/register                         → 200 ✅
GET  /oauth/authorize                        → 307 ✅ (redirect to claude.ai callback)
POST /oauth/token                            → 200 ✅
```

**Remaining blocker:** After `POST /oauth/token 200`, the Claude mobile app does not follow through with `GET /sse`. The token is issued and valid, nginx forwards the Authorization header, and the SSE endpoint returns 200 with a bearer token when tested manually. The app is silently dropping the connection attempt after receiving the token.

---

## Current nginx Config (`/opt/homebrew/etc/nginx/nginx.conf`)

```nginx
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    server {
        listen 8080;
        server_name _;

        location /mcp/ {
            proxy_pass http://127.0.0.1:8766/mcp/;
            proxy_http_version 1.1;
            proxy_set_header Host localhost;
            proxy_set_header Authorization $http_authorization;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection '';
            proxy_buffering off;
            proxy_cache off;
        }

        location / {
            proxy_pass http://127.0.0.1:8766;
            proxy_http_version 1.1;
            proxy_set_header Host localhost;
            proxy_set_header Authorization $http_authorization;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection '';
            proxy_buffering off;
            proxy_cache off;
            chunked_transfer_encoding on;
        }
    }
}
```

---

## Startup Sequence
```bash
# Terminal 1
~/start_burrowmcp.sh

# nginx already running as brew service
# brew services start nginx  (if not running)

# Terminal 2
cloudflared tunnel --config ~/.cloudflared/config.yml run --token <token>
```

---

## Next Session — Investigation Targets

### Priority 1: Why doesn't the app connect after token exchange?
The SSE endpoint returns a relative URL in the session data:
```
event: endpoint
data: /messages/?session_id=<id>
```
The Claude app may be constructing `https://theburrow.dev/messages/?session_id=...` and that POST may be failing or timing out. Test:
```bash
curl -v -X POST "https://theburrow.dev/messages/?session_id=<real_id>" \
  -H "Authorization: Bearer <real_token>" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"ping","id":1}'
```

### Priority 2: Force absolute URL in SSE session data
Check if MCP SSE can be configured to return an absolute URL:
```bash
grep -n "base_url\|messages\|endpoint\|data:" \
  "/Volumes/Bird's Nest/BurrowMCP/venv/lib/python3.11/site-packages/mcp/server/sse.py"
```
Look for where `data: /messages/...` is constructed and whether it respects `X-Forwarded-Proto` or a configurable base URL.

### Priority 3: WWW-Authenticate on unauthenticated /sse
Some sources indicate the Claude app expects a `401` with `WWW-Authenticate: Bearer` header on unauthenticated SSE requests, not a 200 or 405. Currently the SSE endpoint serves anyone without checking the token. Adding token validation + 401 response might be the missing signal.

### Priority 4: Check for known iOS app bug
Found open GitHub issue: Claude iOS app loops on unauthenticated GET requests and never follows WWW-Authenticate to complete OAuth discovery. May need to watch for Anthropic fix or workaround.

---

## Key Files
| File | Path |
|------|------|
| BurrowMCP server | `/Volumes/Bird's Nest/BurrowMCP/server.py` |
| Backup | `/Volumes/Bird's Nest/BurrowMCP/server.py.bak` |
| nginx config | `/opt/homebrew/etc/nginx/nginx.conf` |
| Cloudflare tunnel config | `~/.cloudflared/config.yml` |
| Start script | `~/start_burrowmcp.sh` |
| Debug log | `/tmp/burrowmcp_debug.log` |

---

## Tags
`#burrowmcp` `#remote-access` `#cloudflare-tunnel` `#oauth` `#mcp` `#eagleeye11` `#theburrow-dev` `#sse` `#nginx` `#session-18`
