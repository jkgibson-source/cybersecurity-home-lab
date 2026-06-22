# BurrowDash Uplevel — Build Report
**Date:** 2026-05-31  
**Session type:** Feature build (Algorithm, E3)  
**Files changed:** `BurrowMCP/tools/ssh_tools.py`, `BurrowMCP/server.py`  
**Status:** 73/74 ISCs verified. ISC-68 (mobile visual) deferred — manual phone check required.

---

## What We Built

BurrowDash's node cards used to be read-only status chips. Green dot, IP, role. That was it. You couldn't click them, and getting any real detail about a node — CPU load, RAM, temperature — still required either opening a terminal and SSH-ing in, or burning Claude tokens on a lab status check.

This session changes that. Every node card is now clickable. Click one, and a detail drawer slides in from the right (or up from the bottom on your phone) showing:

- Uptime and load averages
- RAM usage
- CPU temperature (Linux nodes) or N/A (macOS — no reliable CLI thermal)
- Network interfaces and IPs
- Running service count (Linux) or N/A (macOS — no systemd)
- Disk usage (from the existing `/disk` endpoint)
- Failed services (from the existing `/services` endpoint)

No tokens. No terminal. Just tap and read.

---

## The Architecture (and Why It Works This Way)

### The Data Layer: One SSH Connection Per Node

The first design decision was how to gather five stats from a remote node. The obvious approach is five separate SSH calls — one for uptime, one for RAM, one for temperature, and so on. Run them in parallel and you get all five in roughly the time of one.

That's wrong for this setup, and it's worth understanding why.

Each SSH connection carries overhead: TCP handshake, key exchange, authentication. On a LAN node over Tailscale, that's typically 500ms to 2 seconds per connection. Five parallel connections means five concurrent SSH handshakes, plus the complexity of `asyncio.run_in_executor` to avoid blocking Starlette's event loop, plus five separate error conditions to handle.

The better approach is a **single compound shell command** — all five stat commands joined with `&&`, separated by echo delimiters, sent as one SSH call:

```bash
echo '---UPTIME---' && uptime && \
echo '---MEM---' && free -h && \
echo '---TEMP---' && (cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo N/A) && \
echo '---NET---' && (ip -brief addr show 2>/dev/null || ifconfig | grep 'inet ') && \
echo '---SVCCOUNT---' && (systemctl list-units --state=active --no-legend 2>/dev/null | wc -l || echo N/A)
```

One SSH handshake. All five results. The server parses the `---SECTION---` delimiters into a Python dict. Total latency is the same as the fastest parallel approach — but with no concurrency complexity and no event loop issues.

Each section uses `|| echo N/A` so a missing binary or permission error on one stat doesn't kill the others.

### OS Awareness

The Burrow has two macOS nodes (EagleEye11, Jynx13) and two Linux nodes (Krypton1t3 on Fedora, SkorpiOm on Kali). The compound command is OS-aware — macOS nodes use `vm_stat` for memory and `ifconfig` for network; Linux nodes use `free -h` and `ip -brief addr show`. CPU temperature is Linux-only (`/sys/class/thermal/thermal_zone0/temp`); macOS returns N/A because there's no reliable CLI thermal read on Apple Silicon. Service count is Linux-only (systemd); macOS also returns N/A.

EagleEye11 is `is_local=True` in the config, so it never opens an SSH subprocess at all — it runs the command directly via `subprocess.run`. Same function, same output format, no SSH overhead.

### The API Layer: One New Route

The new endpoint is `GET /api/node/{name}/stats`. It follows the exact same pattern as the existing `/disk`, `/services`, and `/info` routes:

- Auth-gated by `burrow_session` cookie
- Returns 401 if no valid session
- Returns 404 if `name` isn't in the NODES registry
- Returns the `get_node_stats()` dict as JSON on success

One important detail about **route registration order**: Starlette matches routes top-to-bottom. If a more general pattern (like `/api/node/{name}/disk`) were registered before `/api/node/{name}/stats`, Starlette might resolve `/stats` incorrectly. The new `/stats` route is registered first, before `/disk`, `/services`, and `/info`. This is a silent failure mode — no error at startup, just wrong handler called at runtime.

### The Dashboard: Clickable Cards and a Detail Drawer

The dashboard HTML lives as a single string inside `server.py`. That's a deliberate architectural choice from the original build (see its ISA for the reasoning), and we didn't change it here.

What we added:

**CSS:**
- `cursor: pointer` and `border-color` hover transition on `.card`
- A fixed-position detail drawer (`#drawer`) that slides in from the right on desktop and up from the bottom on mobile (<480px). Both transitions are pure CSS — no JS required for the animation.
- A backdrop overlay (`#drawer-overlay`) that closes the drawer on click-outside.
- Stable `id` attributes on every stat section inside the drawer (`id="drawer-uptime"`, `id="drawer-ram"`, etc.). More on why this matters below.

**JavaScript:**
- `openDrawer(node)` — called on card click. Immediately populates the static fields (status, role, IP) from the already-loaded node data, sets all stat fields to `…`, opens the drawer, then fires the three fetches.
- Three parallel fetches: `/api/node/{name}/stats`, `/api/node/{name}/disk`, `/api/node/{name}/services`. These are independent and run concurrently via a `Promise.all`-based settled wrapper.
- `closeDrawer()` — triggered by the close button, clicking the overlay, or pressing `Escape`.

### The Promise.all Resilience Fix

The initial implementation used a standard `Promise.all` with a single `.catch`. This is the "fails closed" pattern: if any one of the three fetches fails (say, the SSH call to SkorpiOm times out while fetching stats), the entire `.catch` fires and all drawer fields show "error: ...". You lose disk and services data even though those fetches might have succeeded.

After the Advisor review, this was replaced with a per-promise settled wrapper:

```javascript
function settled(promise) {
  return promise.then(
    function(v) { return {ok: true, value: v}; },
    function(e) { return {ok: false, error: e}; }
  );
}
```

Each fetch is wrapped individually. The outer `Promise.all` always resolves (never rejects). Each section checks its own `ok` flag and shows its data or its own error independently. A node that's SSH-unreachable will show "fetch error" for stats/disk/services but still show the name, IP, role, and status from the initial load. Partial data beats a blank panel.

This is the correct default for any dashboard that aggregates independent data sources.

---

## Phase 3: What's Already In Place

Phase 3 is service start/stop/restart control from the dashboard. It's not implemented yet, but the infrastructure for it was already in `config.py` from a prior design session:

```python
ALLOWED_SERVICES = [
    "wazuh-agent", "splunk", "ollama", "syncthing", "docker", "hermes-agent",
]

CONFIRM_TOKENS = {
    "restart_service": "CONFIRM_RESTART_SERVICE",
    # ...
}
```

Phase 3 will add `POST /api/node/{name}/service/{svc}/start` and `/stop` routes. The service name must be in `ALLOWED_SERVICES` (Tailscale and SSH are intentionally excluded — you never restart your lifeline remotely). The request body will require the matching `CONFIRM_TOKENS` value to prevent accidental execution.

On the dashboard side, the `id="drawer-services"` container currently shows a number. Phase 3 swaps that content for a list of named services with action buttons — no surrounding HTML changes required. That's why the stable drawer IDs matter: they make Phase 3 a zero-refactor additive layer.

---

## What Didn't Happen (and Why)

**Forge (GPT-5.4 via codex CLI)** was selected as the code-writing agent for this build (E3 coding tasks auto-include Forge per Algorithm doctrine). Forge's startup check found that the `codex` CLI binary is not installed on EagleEye11. Forge correctly refused to silently fall back to another model — the whole point of a cross-vendor agent is provenance integrity — and reported the blocker honestly with three options. We took option C (execute inline) since the spec was fully defined and the implementation was deterministic. Forge's spec was used verbatim.

**ISC-68 (mobile visual verification)** requires a browser screenshot at 375px viewport. The Interceptor CLI (the correct tool for this) isn't installed on EagleEye11, and the Claude-in-Chrome MCP extension wasn't connected during the session. ISC-68 is marked `[DEFERRED-VERIFY]`. To clear it: open theburrow.dev on your phone, click any node card, and confirm the drawer slides up from the bottom without horizontal overflow.

---

## Things Worth Knowing for Next Time

**Single compound SSH command is almost always right for multi-stat collection.** The temptation is to make "clean" separate calls. The physics says no: one SSH handshake amortizes across all commands, and the added complexity of async parallelism isn't worth it when a semicolon does the same job.

**Starlette route order is silent global state.** There's no startup error when a new route is shadowed by an existing pattern. Always register specific routes before general ones, and curl-verify both paths after registering a new route.

**For dashboards: always use settled wrappers, not Promise.all.** `Promise.all` is correct when you need all results or none (a transaction). A dashboard aggregating independent sources should always show what it has, not go blank because one source failed.

**Stable IDs on extensible UI sections cost nothing at build time.** Adding `id="drawer-services"` to the service count container in Phase 2 means Phase 3 doesn't touch the surrounding HTML — it just replaces the content of that div. The ApertureOscillation analysis surfaced this: the tactical view (any div works) and the strategic view (Phase 3 needs an in-place swap target) diverge on this one detail, and it's free to resolve at Phase 2.

**The Advisor's `--auto-state` flag reads `MEMORY/STATE/work.json`**, which pointed to a completed task ISA instead of the BurrowMCP project ISA. For project ISAs (files that live in the project repo itself rather than `MEMORY/WORK/`), the auto-state lookup currently fails silently. The workaround is to pass the ISA path explicitly in the advisor prompt.

---

## Files Changed

```
BurrowMCP/tools/ssh_tools.py
  + _parse_node_stats(raw: str, is_macos: bool) -> dict
  + get_node_stats(node_name: str) -> dict

BurrowMCP/server.py
  + @mcp.tool() get_node_stats  [top-level MCP registration]
  + async def api_node_stats(request)  [inside --http block]
  + Route("/api/node/{name}/stats", ...)  [registered before /disk]
  ~ DASHBOARD_HTML  [cursor:pointer, drawer CSS, drawer HTML, openDrawer JS, settled fetch pattern]
```

No new Python dependencies. No changes to OAuth/MCP endpoints. `requirements.txt` unchanged.

---

## ISC Coverage

| Group | ISCs | Status |
|-------|------|--------|
| ssh_tools.py — get_node_stats | ISC-37 to ISC-45 | 9/9 ✓ |
| server.py — MCP tool | ISC-46 to ISC-47 | 2/2 ✓ |
| server.py — API endpoint | ISC-48 to ISC-51 | 4/4 ✓ |
| Dashboard — clickable cards | ISC-52 to ISC-69 | 17/18 (ISC-68 deferred) |
| Anti-criteria | ISC-70 to ISC-72 | 3/3 ✓ |
| Phase 3 scaffolding confirmed | ISC-73 to ISC-74 | 2/2 ✓ |
| **Total** | **74 ISCs** | **73/74** |

---

*Built with The PAI Algorithm v6.3.0 — E3 effort, 4 thinking capabilities (ApertureOscillation, FeedbackMemoryConsult, FirstPrinciples, SystemsThinking), Forge auto-included (blocked, executed inline).*

---

# Addendum — `get_node_stats` Ported to Jynx13
**Date:** 2026-06-01
**Session type:** Targeted port / capability parity
**Files changed:** `BurrowMCP/tools/ssh_tools.py`, `BurrowMCP/server.py` (Jynx13 copy)
**Status:** Applied and verified live. MCP server restart pending to expose the tool.

## Why This Happened

The original build above landed `get_node_stats` on **EagleEye11** (the stationary Mac Mini "Command Central" / BurrowMCP host / BurrowDash backend). **Jynx13** — the 2017 MacBook Air "Mobile Command" machine — never received it. With an extended NY trip ahead, Jynx13 is the machine that travels, and the request was to have the same per-node stats available *from* Jynx13 while away, not just via BurrowDash on the phone.

A diff of the two copies confirmed the divergence is deliberate and runs both ways:

- **EagleEye11** has `get_node_stats` + the full BurrowDash web layer; it does **not** register `run_burrow_command`.
- **Jynx13** has `run_burrow_command` (mobile service start/stop control) but **lacked** `get_node_stats`, and is a stdio-only MCP server with no dashboard/HTTP layer at all.

The fork is intentional — tool sets are tailored to machine role. So this was a one-way, surgical port, not a "sync."

## What Was Changed

Scope was explicitly constrained to **MCP tool only** — no dashboard, no Starlette routes, no HTTP layer. Jynx13's phone access already goes through EagleEye11's BurrowDash, so porting the web layer would have been redundant.

```
BurrowMCP/tools/ssh_tools.py   (Jynx13)
  + _parse_node_stats(raw: str, is_macos: bool) -> dict
  + get_node_stats(node_name: str) -> dict

BurrowMCP/server.py            (Jynx13)
  + from tools.ssh_tools import get_node_stats as _get_node_stats
  + @mcp.tool() get_node_stats   [stdio JSON variant, placed before get_wazuh_alerts]
```

Both functions were ported **verbatim** from EagleEye11 — same compound single-SSH-command pattern (one handshake, all five stats), same `---SECTION---` delimiter parsing, same OS-aware branch (macOS `vm_stat`/`ifconfig` vs Linux `free -h`/`ip`), same temp/service-count handling. The server-side registration matches EagleEye11's docstring and ordering exactly.

## Why the Port Was Clean

The two new functions depend only on `run_ssh_command`, `NODES`, and `log_tool_call` — all already present in Jynx13's files. Critically, they call Jynx13's **existing** `run_ssh_command`, so they inherit Jynx13's own connection behavior (connects as `burrowuser`, includes `BatchMode=yes`) rather than EagleEye11's. No edit to `run_ssh_command` was needed or made. This is why a verbatim copy of two leaf functions "just worked" across two copies whose lower-level SSH helpers differ slightly.

## Verification

- `py_compile` on both changed files — clean.
- `get_node_stats('Jynx13')` — executed **locally** (`is_local=True`), returned valid uptime / RAM (`vm_stat`) / network; `temp` and `service_count` correctly `N/A`/`null` for macOS.
- `get_node_stats('EagleEye11')` — executed **over SSH**, returned valid data including all four of EagleEye11's interfaces.

## Footprint

~3 KB of source added. **No new Python dependencies** — `requirements.txt` unchanged. Net disk impact is five orders of magnitude under the 1 GB ceiling set for the change.

## One Open Item

The running Jynx13 MCP server loaded `server.py` at startup, so the live MCP connection still advertises the prior tool set. **Restart the Jynx13 BurrowMCP server** (`start_burrowmcp.sh`, or reconnect the MCP client) to expose `get_node_stats`. No data migration, no config change required.

---

*Addendum by Claude (Opus 4.8) — surgical port, E-low effort, verified against live nodes. Node-role divergence preserved intentionally.*
