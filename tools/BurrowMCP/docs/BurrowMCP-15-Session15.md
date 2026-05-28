# BurrowMCP — Session 15 Journal
**Date:** 2026-05-10
**Author:** JBird + Claude
**Status:** ✅ Complete — `run_burrow_command()` fully operational on Jynx13 → SkorpiOm + Krypton1t3

---

## Session Goal
Build and deploy the `run_burrow_command()` tool designed in the Session 15 planning pre-session: a whitelisted, safety-gated remote command execution pipeline for BurrowMCP on Jynx13.

---

## What We Accomplished

### 1. SSH Keypair Situation Resolved ✅
A keypair (`burrow_ed25519`) had already been generated two sessions ago and was referenced in `config.py` as `SSH_KEY_PATH`. Today we mistakenly generated a duplicate (`burrowmcp_id_ed25519`). Deleted the duplicate and used the existing key throughout — cleaner and consistent with config.

```bash
rm ~/.ssh/burrowmcp_id_ed25519
rm ~/.ssh/burrowmcp_id_ed25519.pub
```

---

### 2. `burrowuser` Created on SkorpiOm ✅
Dedicated SSH service account with no password, keypair-only auth, and a limited sudoers entry.

```bash
sudo useradd -r -s /bin/bash burrowuser
sudo mkdir -p /home/burrowuser/.ssh
sudo chmod 700 /home/burrowuser/.ssh
# Pasted burrow_ed25519.pub into authorized_keys (hand-typed — different machine)
sudo chmod 600 /home/burrowuser/.ssh/authorized_keys
sudo chown -R burrowuser:burrowuser /home/burrowuser/.ssh
```

**Sudoers** (`/etc/sudoers.d/burrowuser` on SkorpiOm — Kali/Debian accepts comma-separated):
```
burrowuser ALL=(ALL) NOPASSWD: /usr/bin/apt, /sbin/reboot, /bin/systemctl
```

**Note:** Initially created with `/usr/sbin/nologin` shell — SSH connected but blocked command execution. Fixed by switching to `/bin/bash`. Security comes from keypair + sudoers, not the shell.

```bash
sudo usermod -s /bin/bash burrowuser
```

---

### 3. SSH Test — Jynx13 → SkorpiOm ✅
```bash
ssh -i ~/.ssh/burrow_ed25519 burrowuser@100.102.6.14 "apt list --upgradable 2>/dev/null"
# Result: Listing...   (no packages — SkorpiOm fully up to date)
```

No password prompt. Clean output. Pipeline validated.

---

### 4. `burrow_command_tools.py` Written and Deployed ✅
New tool module at `~/BurrowMCP/tools/burrow_command_tools.py`.

**Architecture:**
```
Claude → run_burrow_command() → 4 gates → _ssh_burrowuser() → burrowuser@node → sudoers → command
```

**Four security gates:**
1. `command_id` must exist in `COMMAND_REGISTRY`
2. `node_name` must be in that command's allowed node list
3. `reboot` is suggest-only — returns a confirmation prompt, never executes
4. Write operations require a valid `confirm_token` matching `CONFIRM_TOKENS` in `config.py`
5. `service_name` validated against `ALLOWED_SERVICES` before touching the shell

**Command whitelist (v1):**

| command_id | Node(s) | Type |
|---|---|---|
| `apt_check_updates` | SkorpiOm | Read |
| `apt_upgrade` | SkorpiOm | Write |
| `dnf_check_updates` | Krypton1t3 | Read |
| `dnf_upgrade` | Krypton1t3 | Write |
| `disk_usage` | SkorpiOm, Krypton1t3 | Read |
| `service_status` | SkorpiOm, Krypton1t3 | Read |
| `service_restart` | SkorpiOm, Krypton1t3 | Write |
| `reboot` | SkorpiOm, Krypton1t3 | Suggest-only |

`confirm_token_key` values align exactly with `CONFIRM_TOKENS` keys in `config.py`.

---

### 5. `server.py` Updated ✅
Appended `run_burrow_command` tool registration above `if __name__ == "__main__":` using heredoc:

```bash
cat >> ~/BurrowMCP/server.py << 'EOF'
from tools.burrow_command_tools import run_burrow_command as _run_burrow_command

@mcp.tool()
def run_burrow_command(...) -> str:
    ...
EOF
```

BurrowMCP restarted via `pkill -f start_burrowmcp.sh && /bin/zsh ~/start_burrowmcp.sh`.

---

### 6. `burrowuser` Created on Krypton1t3 ✅
Same pattern as SkorpiOm, but key was piped remotely over the existing `jynx13_to_krypton` key — no hand-typing required.

```bash
# Step 1: pipe key to tmp (pipe + sudo = terminal conflict workaround)
ssh -i ~/.ssh/jynx13_to_krypton SuperSkorp_7@100.103.171.45 "cat > /tmp/burrow_key" < ~/.ssh/burrow_ed25519.pub

# Step 2: move into place with sudo
ssh -t -i ~/.ssh/jynx13_to_krypton SuperSkorp_7@100.103.171.45 \
  "sudo cp /tmp/burrow_key /home/burrowuser/.ssh/authorized_keys && sudo rm /tmp/burrow_key"

# Step 3: permissions
ssh -t -i ~/.ssh/jynx13_to_krypton SuperSkorp_7@100.103.171.45 \
  "sudo chmod 600 /home/burrowuser/.ssh/authorized_keys && sudo chown -R burrowuser:burrowuser /home/burrowuser/.ssh"
```

**Sudoers on Krypton1t3** — Fedora's visudo rejects comma-separated commands, requires separate lines:
```
burrowuser ALL=(ALL) NOPASSWD: /usr/bin/dnf
burrowuser ALL=(ALL) NOPASSWD: /sbin/reboot
burrowuser ALL=(ALL) NOPASSWD: /bin/systemctl
```

**Home directory permissions** also needed fixing — dnf writes cache/state dirs:
```bash
sudo chown -R burrowuser:burrowuser /home/burrowuser
```

**GPG key import** — one-time prompt on first `dnf check-update` run for the Brave Browser repo. Accepted. Won't recur.

---

### 7. Live End-to-End Tests ✅

**SkorpiOm disk usage** — returned full `df -h` output, Claude analyzed snap cruft and suggested cleanup. Real data, real analysis.

**Krypton1t3 update check** — returned `brave-browser 1.90.121-1` as the only pending upgrade.

**Krypton1t3 dnf upgrade (write operation)** — confirm token gate fired correctly:
- Claude blocked and requested explicit confirmation
- JBird typed "confirmed" in chat
- Tool approval dialog appeared (Claude for Mac)
- Token passed through, upgrade executed
- Brave Browser upgraded 1.89.145 → 1.90.121 (429MB)
- Krypton1t3 fully up to date ✅

---

## Key Facts

| Item | Value |
|---|---|
| BurrowMCP path (Jynx13) | `~/BurrowMCP/` |
| New tool file | `~/BurrowMCP/tools/burrow_command_tools.py` |
| SSH key used | `~/.ssh/burrow_ed25519` |
| burrowuser shell | `/bin/bash` (nologin blocks remote commands) |
| SkorpiOm sudoers format | Comma-separated (Kali/Debian — accepted) |
| Krypton1t3 sudoers format | One command per line (Fedora — required) |
| Krypton1t3 key delivery method | Two-step ssh pipe via `jynx13_to_krypton` |
| Brave Browser on Krypton1t3 | Upgraded 1.89.145 → 1.90.121 |

---

## Parked (Not This Session)

- Krypton1t3 ↔ Jynx13 SSH key exchange for `SuperSkorp_7` — already done prior to this session
- WatchYourLAN BurrowMCP tool — paused (was causing wifi issues on Krypton1t3)
- BurrowMCP Cloudflare tunnel + Claude Pro → SolSkorp_13 remote access
- Wazuh → Splunk pipeline wiring
- Splunk license migration (deadline ~May 17) ⚠️
- Splunk CLI `-earliest`/`-latest` flag fix in `splunk_tools.py`
- Wazuh dashboard drilldown links on rule.id
- Rule 19007 investigation
- EagleEye11 SCA score <30% investigation
- APP_NAME_MAP expansion for BurrowVoice

---

*"Least privilege isn't paranoia — it's architecture. And now it runs Brave Browser updates from across the room."*
— BurrowMCP Session 15, May 2026

**Tags:** #BurrowMCP #Session15 #runBurrowCommand #burrowuser #ServiceAccount #SSH #sudoers #Jynx13 #SkorpiOm #Krypton1t3 #LeastPrivilege #Tailscale #ConfirmToken #WriteGate #dnf #apt #homelab #SOC #Python #MCP
