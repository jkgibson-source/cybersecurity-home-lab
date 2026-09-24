# EagleEye11 — Airborne Recon Report

**Date:** 2026-07-26
**Operator:** JBird (via Termius on Jynx13)
**Scanner:** Omega (SkorpiOm, nmap 7.99)
**Route:** SkorpiOm → Tailscale → EagleEye11 (100.113.239.38)
**Conditions:** In-flight, Breeze MX844 MCO→SWF, seat 12A. Airplane wifi → Tailscale mesh.

---

## Executive Summary

Service version detection scan performed on EagleEye11 (macOS) from SkorpiOm (Linux) over Tailscale during commercial flight. 13 open TCP ports identified across top-100 scan. Version detection on targeted ports revealed a stack of web services, Apple Remote Desktop, Kerberos, and a Next.js dashboard application. RustDesk confirmed active on port 21118 (web client mode).

**Total open ports (TCP):** 13
**Latency:** 0.03–0.67s (variable over flight wifi)
**Scan time:** ~27s (version detection), ~2s (port enumeration)

---

## Methodology

1. **Phase 1 — Host Discovery:** `tailscale status` to confirm EE11 online and obtain Tailscale IP (100.113.239.38)
2. **Phase 2 — Port Enumeration:** `nmap -Pn -sT --top-ports 100 -T4` — identified 13 open ports in 1.86s
3. **Phase 3 — Service Version Detection:** `nmap -Pn -sV --version-intensity 1` on targeted ports (53, 88, 445, 5000, 5101, 5900, 8080, 8888, 9999, 49152) — completed in 27.32s
4. **Phase 4 — RustDesk Verification:** `nmap -Pn -sV -p 21116-21118` — confirmed web client active on 21118
5. **Phase 5 — UDP DNS Probe:** `nmap -Pn -sU -sV -p 53` — state: open|filtered

**Note:** Aggressive scans (`-sV -sC`) timed out at 120s over the flight chain. Lighter scans with reduced version intensity and no scripts performed reliably.

---

## Port Inventory

### Confirmed Services

| Port | State | Service | Version/Detail | Risk |
|------|-------|---------|----------------|------|
| 22 | open | SSH | Unfingerprinted | Low — expected for remote access |
| 53 | open | DNS | No banner (TCP); open|filtered (UDP) | Medium — unnecessary on macOS single host |
| 80 | open | HTTP | Unfingerprinted | Low — likely default macOS web |
| 88 | open | Kerberos | **Heimdal Kerberos** (macOS built-in) | Medium — unused if no domain |
| 443 | open | HTTPS | Unfingerprinted | Low — expected |
| 445 | open | SMB | Version not fingerprinted | **High** — file sharing exposed to Tailscale |
| 5000 | open | RTSP | AirPlay/streaming service | Low — Apple default |
| 5101 | open | Apple service | tcpwrapped (auth required) | Low |
| 5900 | open | VNC | **Apple Remote Desktop VNC** | Medium — verify password enforcement |
| 8080 | open | HTTP | **nginx 1.31.0** | Medium — reverse proxy, what's behind it? |
| 8888 | open | HTTP | **Uvicorn** (Python ASGI server) | Medium — Python web app exposed |
| 9999 | open | HTTP | **Next.js app** (redirects to `/dashboard`) | Medium — web app with dashboard |
| 49152 | open | Unknown | MikroTik fingerprint (likely false positive) | Low — ephemeral port |

### RustDesk (Verified Separately)

| Port | State | Service | Detail |
|------|-------|---------|--------|
| 21116 | closed | RustDesk signaling | Not listening — direct P2P disabled |
| 21117 | closed | RustDesk NAT test | Not listening |
| 21118 | **open** | RustDesk web client | Active — relay/browser mode confirmed |

**RustDesk configuration:** Web client mode only. Connections route through relay, not direct signaling. Functional but different from default config.

---

## Notable Findings

### 1. Next.js Dashboard (Port 9999)
A Next.js application is running on EE11, serving a prerendered dashboard. The `X-Powered-By: Next.js` header is present. The app redirects GET requests to `/dashboard`. This is either a self-hosted app or a development project.

**Recommendation:** Identify what this app is. If it's a dev project, ensure it's not serving sensitive data. Consider removing the `X-Powered-By` header.

### 2. Python Backend (Port 8888)
Uvicorn (ASGI server) indicates a Python web application — likely FastAPI or similar. Running alongside nginx on 8080, suggesting a reverse proxy setup.

**Recommendation:** Verify this is intentional. If nginx proxies to Uvicorn, confirm the proxy configuration doesn't expose internal routes.

### 3. SMB Exposed (Port 445)
macOS File Sharing is enabled and reachable over Tailscale. Any Tailscale-connected device can access shared folders.

**Recommendation:** If SMB sharing is not needed across the Burrow, disable it in System Settings → General → Sharing → File Sharing. If needed, ensure only specific folders are shared with proper authentication.

### 4. Kerberos Running (Port 88)
Heimdal Kerberos is active. This is the macOS built-in implementation, typically enabled when Directory Services or certain enterprise features are active.

**Recommendation:** If no domain or Kerberos-authenticated services are in use, this is unnecessary attack surface. Check if it can be disabled via `sudo launchctl unload -w /System/Library/LaunchDaemons/krb5kdc.plist` (verify first).

### 5. DNS Server (Port 53)
A DNS server is running on TCP port 53. UDP 53 is open|filtered.

**Recommendation:** If this is not an intentional DNS server (e.g., for local resolution), it should be disabled. macOS does not run a DNS server by default.

### 6. VNC — Apple Remote Desktop (Port 5900)
Apple's VNC implementation is active. This is the Screen Sharing service.

**Recommendation:** Verify a strong password is set. Consider restricting access via the firewall to specific Tailscale IPs if possible.

---

## Scan Limitations

- **Airplane wifi latency** caused variable response times (0.03s–0.67s)
- **Aggressive scans timed out** — full `-sV -sC` could not complete within 120s timeout
- **Version intensity reduced** to 1 (light banner grabbing) for reliability
- **No UDP comprehensive scan** — only port 53 UDP was tested
- **OS fingerprinting not performed** — macOS already known from Tailscale metadata

---

## Recommendations Summary

| Priority | Action | Port(s) |
|----------|--------|---------|
| High | Review SMB sharing — disable if not needed | 445 |
| Medium | Verify VNC password strength | 5900 |
| Medium | Audit Next.js dashboard — what is it? | 9999 |
| Medium | Audit Python backend — what's running? | 8888 |
| Medium | Disable Kerberos if no domain in use | 88 |
| Medium | Disable DNS server if not intentional | 53 |
| Low | Remove `X-Powered-By` header from Next.js | 9999 |
| Low | Review nginx config — what's proxied? | 8080 |
| Low | Confirm RustDesk config is intentional | 21118 |

---

## Network Context

**Active Tailscale nodes at time of scan:**
- SkorpiOm (100.102.6.14) — scanner, Linux
- EagleEye11 (100.113.239.38) — target, macOS
- Jynx13 (100.108.182.39) — operator terminal, macOS (via relay "den")

**Offline nodes:** bb, birdpad, flex, iphone-11-pro, iphone-13, krypton1t3, oriel-spec-hopper, splice

---

*Scan performed by Omega (Ω) from SkorpiOm, seat 12A, Breeze MX844. The mat doesn't care about the data. Neither does the scan.*
