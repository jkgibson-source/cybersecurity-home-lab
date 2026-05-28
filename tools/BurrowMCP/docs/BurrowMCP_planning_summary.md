# The Burrow MCP Planning Summary

**Project:** Burrow Ops MCP for Remote Home Lab Maintenance  
**Primary Control Host:** EagleEye11  
**Target Assistant:** Claude Desktop via MCP  
**Context:** Planning for a month away from the home lab while Jynx13 travels with the user.

---

## 1. Core Idea

The goal is to create a custom MCP server on **EagleEye11** that allows Claude Desktop to act as a bounded, request-only assistant for The Burrow while the user is out of state.

This is **not** intended to be an autonomous AI administrator with broad root access. The desired design is closer to a guarded remote control panel:

```text
Claude Desktop on EagleEye11
        ↓
Local Burrow MCP Server
        ↓
Whitelisted tools only
        ↓
Specific maintenance tasks on SkorpiOm, Krypton1t3, and EagleEye11
```

The assistant should only perform specific actions when explicitly requested by the user.

---

## 2. Design Philosophy

The MCP should be built around safety, clarity, and operational usefulness.

### Guiding Principles

- No unrestricted shell access.
- No vague autonomy.
- Read-only checks should be available by default.
- Change-making tools should require explicit confirmation.
- Tools should be host-specific where practical.
- Every meaningful action should write a log.
- Remote access services should be protected from accidental shutdown.
- Risky actions should have a recovery path documented before use.
- The MCP should behave like a **Burrow Ops console**, not a general-purpose root shell.

A good description of the intended system:

> A bounded Burrow Ops MCP with request-only maintenance tools, host-specific permissions, and full logging.

---

## 3. Machines Discussed

### EagleEye11

**Role:** Control-plane / Hermes Ops / MCP host.

EagleEye11 is a strong candidate for hosting the MCP because it already fits the command-center role in The Burrow.

Potential responsibilities:

- Host the MCP server for Claude Desktop.
- Check remote connectivity.
- Monitor Tailscale/Twingate status.
- Monitor Syncthing and BurrowSync.
- Confirm Bird’s Nest external drive is mounted.
- Write maintenance logs.
- Act as the safe operations anchor while the user is away.

### Krypton1t3

**Role:** Fedora-based creative workstation / Security Lab / Hermes Forge / experimentation machine.

Potential MCP tasks:

- Check `dnf` updates.
- Preview Fedora upgrades.
- Apply confirmed `dnf` upgrades.
- Check Ollama or Hermes Forge services.
- Check Syncthing status.
- Check disk space and failed services.
- Restart selected non-critical services when requested.

### SkorpiOm

**Role:** Dedicated Kali / pentest / red-purple team box.

Potential MCP tasks:

- Run `apt update` checks.
- Preview available upgrades.
- Apply confirmed `apt` upgrades.
- Check whether reboot is required.
- Check disk space and failed services.
- Check Syncthing or remote access status if applicable.

### Jynx13

**Role:** Travel machine accompanying the user.

Since Jynx13 is coming with the user and is macOS-based, she is not the main focus of remote maintenance MCP tools.

Potential role while away:

- Field terminal.
- Remote SSH/Tailscale access point.
- Report review station.
- Screenshot triage workstation.
- BurrowSync client.
- Travel notes and documentation machine.

---

## 4. Useful MCP Tool Categories

### A. OS Update Tools

For **SkorpiOm**:

```text
skorpiom_apt_check()
skorpiom_apt_upgrade_preview()
skorpiom_apt_upgrade_apply(confirm)
skorpiom_apt_autoremove(confirm)
```

Possible underlying commands:

```bash
sudo apt update
apt list --upgradable
sudo apt upgrade
sudo apt autoremove
```

For **Krypton1t3**:

```text
krypton_dnf_check()
krypton_dnf_upgrade_preview()
krypton_dnf_upgrade_apply(confirm)
krypton_dnf_autoremove(confirm)
krypton_dnf_history()
```

Possible underlying commands:

```bash
sudo dnf check-update
sudo dnf upgrade
sudo dnf autoremove
sudo dnf history
```

Important note: checking updates should be treated differently from applying updates. Checks are low-risk; upgrades are change-making operations and should require confirmation.

---

### B. Health Check Tools

Useful MCP tools:

```text
get_host_status(host)
check_disk_space(host)
check_memory_pressure(host)
check_failed_services(host)
check_recent_errors(host)
check_temperature(host)
check_reboot_needed(host)
```

Possible underlying commands:

```bash
uptime
df -h
free -h
systemctl --failed
journalctl -p 3 -xb
sensors
```

These tools would allow the user to ask things like:

> Check on Krypton1t3 and SkorpiOm. Anything weird?

The assistant could then summarize the current health of each system.

---

### C. Service Management Tools

Useful MCP tools:

```text
get_service_status(host, service)
restart_named_service(host, service, confirm)
start_named_service(host, service, confirm)
stop_named_service(host, service, confirm)
```

Potential services to monitor:

```text
tailscaled
syncthing
ssh
wazuh-agent
splunk
docker
ollama
hermes-agent
twingate
```

Important safety point: services related to remote access, such as `tailscaled`, `ssh`, and `twingate`, should be protected from casual restart or shutdown.

---

### D. Tailscale / Remote Access Tools

Useful MCP tools:

```text
check_tailscale_status(host)
list_tailscale_peers()
test_peer_connectivity(source_host, target_host)
check_ssh_reachability(host)
check_twingate_status(host)
ping_host(host)
test_port(host, port)
```

These would be valuable while away because remote access is the lifeline back into The Burrow.

Example user request:

> Can Krypton1t3 still see EagleEye11 over Tailscale?

---

### E. Syncthing / BurrowSync Tools

Useful MCP tools:

```text
check_syncthing_all()
check_syncthing_status(host)
check_syncthing_devices()
check_syncthing_folders()
check_burrowsync_status()
list_recent_burrowsync_changes()
check_sync_conflicts()
pause_syncthing_device(device, confirm)
resume_syncthing_device(device, confirm)
```

Important use case:

- Detecting sync conflicts before they pile up.
- Confirming BurrowSync is still healthy.
- Confirming EagleEye11’s external drive path is still available.

---

### F. External Drive / Mount Tools

Especially relevant to EagleEye11 and the Bird’s Nest drive.

Useful MCP tools:

```text
check_external_drives(host)
check_mount_exists(host, path)
check_drive_free_space(host, path)
check_drive_smart_status(host, disk)
```

Important path:

```text
/Volumes/Bird's Nest/BurrowSync
```

Useful check:

```text
check_mount_exists("EagleEye11", "/Volumes/Bird's Nest")
```

This matters because if the external drive disappears or remounts incorrectly, Syncthing or other workflows could behave unexpectedly.

---

### G. Security Monitoring Tools

Potential tools for Wazuh, Splunk, or local log review:

```text
get_wazuh_agent_status()
get_recent_wazuh_alerts(severity_min, hours)
get_splunk_index_status()
search_splunk(query, time_range)
get_failed_login_attempts(host, hours)
get_recent_sudo_events(host, hours)
```

Example requests:

> Show me high-severity Wazuh alerts from the last 24 hours.

> Check for failed SSH logins across the lab.

> Anything weird in sudo logs since yesterday?

---

### H. Backup / Snapshot Tools

Before making system changes, the assistant should be able to verify that backups exist or trigger a known backup job.

Useful MCP tools:

```text
run_backup_job(host, job_name, confirm)
check_backup_status(host)
list_recent_backups(host)
verify_backup_integrity(host, backup_id)
create_snapshot(host, target, confirm)
```

Potential workflow before upgrades:

```text
1. Check disk space.
2. Check recent backup status.
3. Preview updates.
4. Ask for confirmation.
5. Apply updates.
6. Check for reboot requirement.
7. Write maintenance log.
```

---

### I. Reboot Management Tools

Useful MCP tools:

```text
check_reboot_required(host)
schedule_reboot(host, time, confirm)
reboot_host(host, confirm)
cancel_scheduled_reboot(host)
wait_for_host(host)
verify_core_services(host)
reboot_and_verify(host, confirm)
```

A `reboot_and_verify` tool would be very valuable, but should be treated as higher risk.

Post-reboot checks should include:

```text
Tailscale is back.
SSH is reachable.
Syncthing is running.
External mounts are present.
No critical failed services are present.
Wazuh agent is running, if applicable.
```

---

### J. Screenshot Classification Tools

The user also mentioned a possible workflow for sorting and categorizing pentest screenshots using an AI agent with vision capability.

Potential MCP tools:

```text
list_screenshot_files(path)
classify_screenshot(file)
extract_visible_text(file)
move_file_to_category(file, category, confirm)
generate_screenshot_index(path)
```

Potential screenshot categories:

```text
recon
scan-results
web-findings
auth-findings
vulnerability-evidence
exploitation-attempts
credentials-redacted
false-positive
needs-review
report-worthy
```

Potential outputs:

```text
screenshots/index.md
screenshots/findings-map.csv
screenshots/report-worthy/
screenshots/needs-review/
```

This could be one of the strongest future use cases because screenshot triage is tedious, visual, and bounded.

---

## 5. Tools to Avoid or Heavily Restrict

The MCP should not expose broad dangerous commands directly.

Avoid exposing unrestricted versions of:

```bash
sudo bash
rm -rf
dd
mkfs
fdisk
passwd
useradd
chmod -R
chown -R
iptables
ufw reset
dnf remove
apt purge
```

Instead of a general tool like:

```text
run_shell_command(command)
```

Prefer a constrained pattern like:

```text
run_allowed_command(host, command_id, args)
```

Where `command_id` maps to a known safe operation such as:

```text
check_disk
check_updates
restart_syncthing
check_logs
```

---

## 6. Confirmation Pattern

Change-making tools should require explicit confirmation arguments.

Example:

```json
{
  "host": "Krypton1t3",
  "action": "dnf_upgrade_apply",
  "confirm": "CONFIRM_DNF_UPGRADE_KRYPTON1T3"
}
```

This prevents casual or accidental tool use. The assistant should not be able to perform upgrades, reboots, service stops, or destructive actions without a matching confirmation string.

Suggested confirmation categories:

```text
CONFIRM_APT_UPGRADE_SKORPIOM
CONFIRM_DNF_UPGRADE_KRYPTON1T3
CONFIRM_REBOOT_EAGLEEYE11
CONFIRM_REBOOT_KRYPTON1T3
CONFIRM_REBOOT_SKORPIOM
CONFIRM_RESTART_REMOTE_ACCESS_SERVICE
```

---

## 7. Logging Pattern

Every significant MCP action should write a maintenance log.

Useful tool:

```text
write_maintenance_log(host, action, result)
```

Potential log location:

```text
BurrowSync/logs/maintenance/
```

Example log names:

```text
2026-05-03-krypton1t3-dnf-upgrade.md
2026-05-03-skorpiom-apt-upgrade.md
2026-05-03-eagleeye11-burrowsync-check.md
```

Each log should include:

```text
Date/time
Host
Requested action
Commands or tool IDs used
Pre-check results
Action result
Post-check results
Errors or warnings
Next recommended action
```

This keeps the system compatible with future MemPalace mining and repo documentation.

---

## 8. Suggested First Toolset

A practical first version of the Burrow MCP could include:

```text
list_lab_hosts()
get_host_status(host)
check_disk_space(host)
check_failed_services(host)
check_recent_errors(host)
check_tailscale_status(host)
check_syncthing_status(host)
check_burrowsync_status()
check_external_mounts(host)

skorpiom_apt_check()
skorpiom_apt_upgrade_preview()
skorpiom_apt_upgrade_apply(confirm)

krypton_dnf_check()
krypton_dnf_upgrade_preview()
krypton_dnf_upgrade_apply(confirm)

get_service_status(host, service)
restart_named_service(host, service, confirm)

check_reboot_required(host)
reboot_and_verify(host, confirm)

get_recent_security_alerts(hours)
get_failed_logins(host, hours)
get_recent_sudo_events(host, hours)

test_lab_connectivity()
write_maintenance_log(host, action, result)
```

---

## 9. Suggested Implementation Phases

### Phase 1: Read-Only Visibility

Start with tools that only observe and report.

```text
status
disk
services
logs
tailscale
syncthing
updates available
mount checks
```

This phase is low-risk and immediately useful.

### Phase 2: Confirmed Maintenance

Add request-only, confirmation-gated change tools.

```text
restart selected services
apply apt upgrades
apply dnf upgrades
write maintenance logs
```

### Phase 3: Higher-Risk Operations

Add tools that can disrupt access or system state, but only with strong confirmation and post-action verification.

```text
reboot and verify
backup/snapshot integration
remote access service handling
security alert summaries
```

### Phase 4: Agentic Documentation and Triage

Add workflows that are bounded but more advanced.

```text
screenshot classification
pentest evidence indexing
repo-ready maintenance reports
MemPalace mining notes
```

---

## 10. Suggested Tool Matrix Template

Before coding, create a planning matrix like this:

```text
Tool name | Host | Read/Write | Underlying command(s) | Requires confirmation | Log location | Risk level | Notes
```

Example rows:

```text
krypton_dnf_check | Krypton1t3 | Read | dnf check-update | No | maintenance logs | Low | Preview only
krypton_dnf_upgrade_apply | Krypton1t3 | Write | sudo dnf upgrade | Yes | maintenance logs | Medium | Run post-checks
skorpiom_apt_check | SkorpiOm | Read | sudo apt update && apt list --upgradable | No | maintenance logs | Low | Preview only
skorpiom_apt_upgrade_apply | SkorpiOm | Write | sudo apt upgrade | Yes | maintenance logs | Medium | Check reboot required after
check_burrowsync_status | EagleEye11 | Read | Syncthing status + mount check | No | maintenance logs | Low | Important for external drive workflows
reboot_and_verify | Any host | Write | reboot + connectivity checks | Yes | maintenance logs | High | Use carefully while remote
```

---

## 11. Best Framing for the Project

This MCP should be framed as:

```text
Burrow Ops MCP
A request-only MCP server for Claude Desktop on EagleEye11 that exposes safe, whitelisted maintenance tools for The Burrow while the user is away from the lab.
```

Possible subtitle:

```text
Remote maintenance without unrestricted shell access.
```

---

## 12. Key Takeaway

The most valuable version of this MCP is not the most powerful one. It is the one that is:

- Specific.
- Bounded.
- Logged.
- Request-only.
- Host-aware.
- Recovery-minded.
- Useful during real remote maintenance.

For The Burrow, the right first milestone is a safe MCP that can answer:

> What is healthy, what needs attention, what updates are available, and what can I safely ask you to do next?

---

## Tags

#TheBurrow #BurrowOps #MCP #ClaudeDesktop #EagleEye11 #Krypton1t3 #SkorpiOm #Jynx13 #HermesOps #HermesForge #HomeLab #RemoteMaintenance #Tailscale #Syncthing #BurrowSync #Fedora #KaliLinux #APT #DNF #Wazuh #Splunk #MemPalace #CybersecurityHomeLab #OpsRunbook
