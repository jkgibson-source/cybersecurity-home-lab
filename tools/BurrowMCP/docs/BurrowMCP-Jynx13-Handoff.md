# BurrowMCP — Jynx13 Migration Handoff
**Date:** 2026-05-12
**Version:** 0.1.2
**Prepared for:** Claude Code
**Tags:** #BurrowMCP #Jynx13 #migration #SSH #burrowuser #config #bugfix

---

## Context

BurrowMCP was originally built and running on EagleEye11 (macOS M1, Bird's Nest external drive). It was migrated to Jynx13 (macOS Monterey) to serve as the commander/travel node. The migration introduced several EagleEye11-specific artifacts that need to be resolved.

---

## Known Bug — SSH connecting as wrong user

**Root cause:** The SSH connection logic uses `node["ssh_user"]` from the NODES dict to build the SSH command. This is wrong. The `ssh_user` field is for reference/display only. All BurrowMCP SSH connections to remote nodes must use the dedicated `burrowuser` service account.

**Evidence from session grep:**
```
docs/BurrowMCP-04-Session4.md:54:    user = node["ssh_user"]
docs/BurrowMCP-04-Session4.md:56:    ["ssh", "-i", SSH_KEY_PATH, "-o", "StrictHostKeyChecking=no",
```

**The fix:** Find wherever `user = node["ssh_user"]` (or equivalent) appears in the source and replace with `user = "burrowuser"`. The SSH keypair is `burrow_ed25519` / `burrow_ed25519.pub`, already correctly set in config as `SSH_KEY_PATH = "/Users/jbird13/.ssh/burrow_ed25519"`.

---

## Additional Migration Artifacts to Audit

- `BURROWMCP_BASE` — was pointing to `"/Volumes/Bird's Nest/BurrowMCP"` (EagleEye11 path). Should be `"/Users/jbird13/BurrowMCP"`. **Verify this is correct in current config.**
- `LOG_DIR` — derived from `BURROWMCP_BASE`, should resolve correctly once base path is fixed.
- Any other hardcoded `/Volumes/Bird's Nest/` paths lurking in the codebase.
- SSH comment block still referenced EagleEye11 — updated in 0.1.2 but worth a full audit.

---

## Environment — Jynx13

| Property | Value |
|---|---|
| Hostname | Jynx13 |
| OS | macOS Monterey |
| User | jbird13 |
| BurrowMCP path | `/Users/jbird13/BurrowMCP/` |
| SSH key | `/Users/jbird13/.ssh/burrow_ed25519` |
| Tailscale IP | 100.108.182.39 |

---

## NODES Dict — Remote Targets

| Node | Tailscale IP | ssh_user (reference only) | OS |
|---|---|---|---|
| EagleEye11 | 100.113.239.38 | EagleEye11 | macOS M1 |
| Krypton1t3 | 100.103.171.45 | SuperSkorp_7 | Fedora Security Lab 44 |
| SkorpiOm | 100.102.6.14 | solskorp_11 | Kali Linux |
| Jynx13 | 100.108.182.39 | jbird13 | macOS Monterey (is_local: True) |

**All SSH connections use `burrowuser` + `burrow_ed25519` regardless of `ssh_user` value.**

---

## Verification Test

After fixes, confirm from Jynx13:
```bash
ssh -i ~/.ssh/burrow_ed25519 burrowuser@100.103.171.45 "echo ok"
```
Then confirm BurrowMCP `get_node_info` for Krypton1t3 returns uptime cleanly via Claude chat.

---

## Session Notes

- `burrowuser` exists on Krypton1t3 (uid=956), shell is `/bin/bash`, authorized_keys is populated and correct.
- Manual SSH from Jynx13 → Krypton1t3 as `burrowuser` **succeeds** (verified via `-vvv` output).
- The failure is purely in BurrowMCP's SSH invocation using the wrong username.
- SELinux on Krypton1t3 was considered and ruled out.
- Splunk migrated to free tier confirmed active as of 2026-05-12.
