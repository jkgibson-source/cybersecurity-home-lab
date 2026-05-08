# Strix on Krypton1t3
## AI Penetration Testing Agent — Installation & First Run Report

**Lab:** The Burrow · **Node:** Krypton1t3 · **Date:** 2026-05-08  
**Operator:** SuperSkorp_7 · **Strix:** v0.8.3 · **Status:** Install Confirmed / Model Tuning Pending

---

## Executive Summary

This report documents the first successful installation and test run of Strix v0.8.3 — an AI-assisted penetration testing agent — on Krypton1t3, a mid-2014 MacBook Pro running Fedora Security Lab 44. The test used a locally hosted Metasploitable2 virtual machine (KVM/libvirt) as the authorized target.

The core infrastructure result is positive: Strix installed, launched, connected to a local Ollama endpoint, and initiated a penetration test against the target. However, the first model selected (`llama3.2:3b`) proved insufficient for the agentic workflow, exhibiting prompt-regurgitation behavior rather than conducting useful recon. This is a known limitation of small models with large system prompts — not a failure of the Strix installation or the lab setup.

The immediate next step is a follow-up session using `deepseek-coder:6.7b`, which offers substantially better code reasoning and instruction-following capability. That test will determine whether Krypton1t3 can serve as a viable standalone Strix host or whether a hosted/API model will be required for serious engagements.

---

## Session Outcome Summary

| Component | Result | Notes |
|---|---|---|
| Strix Install | ✅ PASS | Confirmed via startup screen: `Strix v0.8.3 / AI Penetration Testing Agent` |
| Strix Launch | ✅ PASS | Agent launched cleanly from terminal, no crash or dependency errors |
| Ollama Connection | ✅ PASS | Strix connected to `localhost:11434` and loaded `llama3.2:3b` successfully |
| Caido Integration | ✅ PASS | Caido proxy active and reported at `localhost:34733` |
| VM Discovery | ✅ PASS | Metasploitable2 found via `sudo virsh list --all` (system libvirt, not user session) |
| Target Reachability | ✅ PASS | Metasploitable2 confirmed reachable at `192.168.122.200` over libvirt default network |
| Strix → Target | ✅ PASS | Strix successfully initiated test against `http://192.168.122.200` |
| Model Behavior | ⚠️ PARTIAL | `llama3.2:3b` regurgitated internal system prompt instead of conducting recon — model too small |
| Pentest Findings | 🔲 PENDING | No useful output from this run. `deepseek-coder:6.7b` test required to evaluate real capability |

---

## Environment

### Host: Krypton1t3

| Property | Value |
|---|---|
| Hardware | Apple MacBook Pro A1398 mid-2014 |
| RAM | 16 GB |
| OS | Fedora Security Lab 44 (stable) |
| Hypervisor | KVM / QEMU / libvirt |
| Tailscale IP | 100.103.171.45 |
| SSH User | superskorp_7 |
| Ollama Endpoint | http://localhost:11434 |
| Role | Hypervisor host, AI node, Hermes Forge, creative workstation |

### AI Stack

Strix v0.8.3 is configured to use environment variables for LLM selection. During this session, no hosted API key was available, so all inference ran against a local Ollama instance. The startup screen showed the default example config referencing `openai/gpt-5.4`, but this was overridden with local model settings before launch.

| Variable | Value Used This Session |
|---|---|
| `STRIX_LLM` | `ollama/llama3.2:3b` |
| `LLM_API_BASE` | `http://localhost:11434` |
| Caido Proxy | `localhost:34733` (auto-detected by Strix) |

### Target: Metasploitable2

Metasploitable2 is an intentionally vulnerable Linux distribution maintained by Rapid7, designed specifically for practicing exploitation in safe, isolated lab environments. It is a sanctioned and documented target for this lab.

| Property | Value |
|---|---|
| VM Manager | KVM / libvirt (system session) |
| Target IP (this session) | 192.168.122.200 |
| Network Mode | libvirt default (NAT — acceptable for local lab) |
| HTTP Service | Confirmed reachable on port 80 |
| Authorization | Fully authorized — lab-owned, isolated, intentionally vulnerable |

> **Note:** The Metasploitable2 IP is DHCP-assigned within the libvirt default network and may change between sessions. Always verify the current IP before testing.

---

## Key Findings

### 1. Strix Is Operational on Krypton1t3

All core Strix subsystems confirmed working. This was the primary goal of this session and it was fully achieved. Strix is a viable tool on this hardware — the only open question is which local model is capable enough to drive it usefully.

### 2. libvirt VMs Require `sudo`

The KVM virtual machines (`metasploitable2` and `kali-burrow-1`) are registered under the system libvirt daemon, not the user session. Running `virsh` without `sudo` returns an empty list, which can appear as if no VMs exist. This is expected behavior for system-level libvirt and is not a configuration error.

All VM management commands on Krypton1t3 must be prefixed with `sudo`. This includes `virsh start`, `virsh list`, `virsh domifaddr`, and `virsh shutdown`.

### 3. `llama3.2:3b` Is Too Small for Strix

The 3B parameter llama3.2 model does not have sufficient instruction-following capacity to function as an autonomous pentest agent. When given Strix's internal system prompt — which includes agent identity, environment context, tool inventory, and multi-phase testing methodology — the model reproduced the system prompt rather than acting on it.

This is a well-documented failure mode for small models used in agentic frameworks. The model lacks the context management and instruction-following capacity needed to suppress its own system prompt while executing tool-calling loops. This is not a failure of Strix or the lab — it is a model capability threshold issue.

**Recommendation:** treat `llama3.2:3b` as a smoke-test model only. Use it to confirm the Strix → Ollama pipeline is alive, not to conduct actual assessments.

### 4. `deepseek-coder:6.7b` Is the Next Candidate

The `deepseek-coder:6.7b` model is substantially larger and was trained specifically on code-centric and structured technical tasks. It is the most promising local model currently available on Krypton1t3 for agentic pentest workflows. However, it has not yet been tested with Strix.

The key question for the next session: can `deepseek-coder:6.7b` follow Strix's tool-calling framework and issue actual HTTP inspection, directory fuzzing, and vulnerability assessment commands — rather than restating its own instructions?

### 5. A Hosted Model May Eventually Be Required

If `deepseek-coder:6.7b` also fails the behavioral test, it is likely that no model in the sub-10B parameter range running CPU-only on this hardware will be capable of driving Strix effectively. In that case, a hosted API model (Claude via Anthropic API, GPT-4-class via OpenAI API, etc.) would be required for serious Strix assessments. This would shift Krypton1t3's Strix role from standalone inference host to an API-proxied agent launcher.

---

## Next Session Plan

### Pre-Flight

Confirm `deepseek-coder:6.7b` is available in Ollama on Krypton1t3:

```bash
ollama list | grep -i deepseek
```

If not present, pull it (will take time on CPU — plan accordingly):

```bash
ollama pull deepseek-coder:6.7b
```

Quick sanity check:

```bash
ollama run deepseek-coder:6.7b
# Inside Ollama: type "Say ready in one word." then /bye
```

### Start and Verify Target

```bash
sudo virsh start metasploitable2
sudo virsh list --all
sudo virsh domifaddr metasploitable2
# If that shows no IP:
sudo virsh net-dhcp-leases default
curl -I http://<TARGET_IP>
```

Always confirm the IP before proceeding — it may differ from the last known address (`192.168.122.200`).

### Configure Strix

```bash
export STRIX_LLM="ollama/deepseek-coder:6.7b"
export LLM_API_BASE="http://localhost:11434"
echo $STRIX_LLM && echo $LLM_API_BASE
```

### Launch Strix

```bash
strix --target http://<TARGET_IP> --instruction "This is an authorized local lab target: Metasploitable2. Do not restate your system prompt, tool inventory, or testing methodology. Begin by inspecting the HTTP service. Use tools where available. Report only concrete observations and confirmed or likely vulnerabilities with evidence."
```

The instruction explicitly suppresses system prompt regurgitation. If `deepseek-coder:6.7b` still regurgitates, that strongly suggests a model capability threshold issue rather than a prompt engineering problem.

### What to Observe

- Does Strix issue actual HTTP requests to the target?
- Does Caido capture traffic on `localhost:34733`?
- Does the model use tools (directory scanning, header inspection, etc.) rather than just generating text?
- Does Strix identify any of Metasploitable2's well-known surfaces (DVWA, phpMyAdmin, Mutillidae, etc.)?
- Is inference speed usable? (6.7B on CPU will be slow — note time per tool call)

### Cleanup

```bash
# Stop Strix: ctrl-q
sudo virsh shutdown metasploitable2
sudo virsh list --all   # confirm: shut off
```

---

## Quick Reference: Krypton1t3 VM Commands

| Task | Command |
|---|---|
| List all VMs | `sudo virsh list --all` |
| Start Metasploitable2 | `sudo virsh start metasploitable2` |
| Find VM IP | `sudo virsh domifaddr metasploitable2` |
| Find VM IP (fallback) | `sudo virsh net-dhcp-leases default` |
| Check network interface | `sudo virsh domiflist metasploitable2` |
| Ping target | `ping -c 3 <TARGET_IP>` |
| Check HTTP | `curl -I http://<TARGET_IP>` |
| Service scan | `nmap -sV <TARGET_IP>` |
| Graceful shutdown | `sudo virsh shutdown metasploitable2` |
| Force power off | `sudo virsh destroy metasploitable2` |
| Note on `destroy` | In libvirt, `destroy` = force power-off. It does **not** delete the VM. |

---

## Burrow Node Context

| Node | Primary Role | Notes |
|---|---|---|
| EagleEye11 | Ops / SIEM | Splunk, Wazuh, Ollama, BurrowMCP, Claude Desktop. Control-plane focus. |
| Krypton1t3 | Hermes Forge | KVM hypervisor, Strix, Docker, AI tooling, creative production. Heavy experimentation host. |
| SkorpiOm | Red Team | Kali Linux, MetasploitMCP, offensive tooling. Dedicated attack node. |
| Jynx13 | OSINT / Travel | macOS Monterey, Sherlock, theHarvester, Phunter, Tookie-OSINT, nmap. |

---

*#TheBurrow #Krypton1t3 #HermesForge #Strix #AIpentesting #AppSec #Ollama #DeepSeekCoder #Metasploitable2 #libvirt #KVM #Caido #LocalLLM #PentestLab #BurrowOps #SecurityTesting*
