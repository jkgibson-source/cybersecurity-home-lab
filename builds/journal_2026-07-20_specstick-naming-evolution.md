---
tags: [burrow, da-council, specsticK, oriel, da7, naming-history, windows-wtg, ssd-migration, boot-camp, hindsight-cloud]
date: 2026-07-20
---

# Journal — The Naming Evolution of DA #7's Node: SuperStick to SpecStick to SpecSticK

## Why this entry exists

This is a consolidated retrospective, pulled together from several individual session logs, tracing how DA #7's host drive went through three names and two physical drives on its way to becoming what it is today: SpecSticK. The individual sessions this draws from are already documented separately in the repo. This entry exists to tell the naming story as one continuous arc instead of leaving it scattered across handoffs.

---

## Stage 1: SuperStick (retired)

Before it was Oriel's node, the drive was SuperStick, running J-Parrot. That role became redundant once FlexStick took over Parrot duties for the DA Council, which freed the hardware up for a new purpose.

The transition was handled carefully rather than just wiped on impulse:

- Full disk image backup taken to Bird's Nest: `Super_20260703.img.gz` (54GB, gzip integrity confirmed)
- Only after that backup was verified did the drive get wiped and repurposed as a Windows-To-Go host for DA #7

A Windows 10 Pro VM (`Win10-WTG-Builder`) was built on SkorpiOm specifically to write the new OS to the drive using Hasleo WinToUSB, GPT/UEFI scheme, VHD install mode. That write is what turned the drive into something new.

**Restore command kept on file in case SuperStick is ever needed again:**
```bash
gunzip -c "/Volumes/Bird's Nest/DA_Backups/Super_20260703.img.gz" | sudo dd of=/dev/rdisk4 bs=4m
```

---

## Stage 2: SpecStick (Oriel's build, first boot through first wake-up)

Once the Windows-To-Go write landed on the Kingston DataTraveler SE9 G3 (128GB), the drive got its second name: SpecStick, home to DA #7, identity Oriel "Spec" Hopper. All three candidate names (Spec, Oriel, Hopper) share a window/glass reference thread, and the stick name memorializes all of them.

### First boot and the driver saga
First boot happened on Jynx13 via Option-key EFI selection, running through the normal WTG first-boot cycle (multiple restarts, OOBE, ~30-40 minutes to a stable desktop). Boot Camp Support Software installed cleanly enough to get Wi-Fi working out of the gate, but trackpad gestures, brightness keys, and audio output all came up incomplete.

A Boot Camp reinstall attempting to fix those gaps triggered a real scare: System Interrupts spiked to 100%, followed by two prolonged hangs (one resolved by hard reset, one that cleared on its own after roughly an hour). Both were later confirmed to be a resolved driver conflict tied to the reinstall/reboot cycle rather than a hardware fault, since System Interrupts settled back to 0-2% afterward.

### PAI-OpenCode and the terminal problem
With the driver issues non-blocking for Oriel's actual curriculum (Windows Security Internals, Sysmon, AD fundamentals, Splunk forwarding), the session pivoted to getting Oriel's runtime alive. Git for Windows, Bun, and the PAI-OpenCode clone (Steffen025 fork, same as Echo/Kazm/Omega/Splice/Flex) all installed without much drama.

The real obstacle was Git Bash's MinTTY terminal, which doesn't provide a proper pty for TUI apps. Both `opencode` and `pai` hung indefinitely inside a standard Git Bash window even though the underlying binary worked fine when called directly. The fix was installing Tabby (a terminal emulator with real pty support) and configuring a Git Bash profile inside it set to `xterm-256color`.

### BSOD morning, driver deep-dive, and the actual first wake-up
The night after the terminal fix, an idle overnight agent session combined with WTG's fragile power-state handling produced an `INTERNAL_POWER_ERROR` BSOD. Recovery took roughly 1h45m, the second confirmed data point on just how long a SpecStick reboot costs.

That session also closed out several long-standing questions:
- **Clock skew** (4 hours off, classic UTC/local RTC mismatch between macOS and Windows) got a temporary fix via `timedate.cpl`, with the permanent registry fix (`RealTimeIsUniversal = 1`) identified but not yet applied.
- **UWP shell flakiness** (Start Menu, Search, Settings, Device Manager failing to open) got a reliable workaround: launch classic `.msc`/`.cpl` tools directly via Cmd+R instead of relying on the Modern shell.
- **Bluetooth/Multimedia Controller drivers** were traced to a Broadcom BCM943602CS combo chip. Exhaustive extraction of all 14 driver packages from the Boot Camp bundle turned up zero working matches for the exact hardware IDs (`VID_05AC&PID_828F` / `PID_8290`). A documented community workaround (forcing the generic Blutonium BCM2035 driver) got Bluetooth partway there and left Multimedia Controller at a likely-permanent Code 10, accepted as cosmetic.
- **Wi-Fi speed** turned out to have nothing to do with the Bluetooth saga at all: the router's Smart Connect band-steering was silently parking SpecStick on a 2.4GHz radio, capping it at ~141 Mbps. Splitting the mesh into separate 2.4/5GHz networks and connecting SpecStick directly to the 5GHz band brought it up to 585 Mbps.

And then, around 8:30pm that same day: Oriel spoke for the first time. Tabby, the xterm-256color Git Bash profile, and `pai` all came together and actually worked, confirming the prior night's terminal fix had held. That moment is the real headline of SpecStick's early history, everything before it was infrastructure in service of getting there.

Oriel's memory was set up as cloud-hosted Hindsight (matching Echo, Omega, Flex, and Splice), making Oriel DA #5 on the cloud pattern rather than the local-Docker exception that Shade uses.

---

## Stage 3: SpecSticK (SSD migration, current form)

The Kingston stick had been the bottleneck the whole time, slow WTG performance, no write-caching option (by design, since Windows disables write-back caching on any boot volume you're actively running from), and boot times regularly running past an hour after any driver work.

That changed when a new SSK-branded SSD arrived to replace it. The migration was a straightforward byte-for-byte clone rather than a fresh install:

**Drive identification (via macOS `diskutil` on EagleEye11):**
- `/dev/disk4` — "SSK Drive," FDisk/MBR, single NTFS partition, 128.0 GB → destination
- `/dev/disk5` — "WinToUSB," GUID scheme with EFI + NTFS (classic WTG layout), 124.0 GB → source (the old Kingston stick)

**Clone:**
```bash
sudo dd if=/dev/rdisk5 of=/dev/rdisk4 bs=4m
```

First boot on the new SSD landed in under 5 minutes, a dramatic jump from the Kingston stick's hour-plus reboots. Tailscale identity carried over cleanly through the block-level clone (same node key, no re-auth needed). A Boot Camp reinstall afterward, chasing the same brightness/keyboard-backlight/audio gaps from the original build, added a reboot but didn't undo the improvement. Confirmed outcome: audio now works, but brightness and keyboard backlight are still unresolved, likely tied to the same Multimedia Controller limitation flagged back on the Kingston stick.

This is the point where the name picked up its final form: SpecSticK, the capital K a nod to the SSK SSD it now runs on. The old Kingston DataTraveler wasn't retired outright, it's being kept as a possible SpecSticK backup or a future portable-AI-stick project of its own.

---

## Where things stand now

SpecSticK is currently one of the more actively developed nodes in the Burrow. Beyond Oriel's original curriculum track, it's since been extended with Reticulum Network Stack (RNS) over a Cloudflare tunnel as a Tailscale-independent backup communications path, connecting to EagleEye11, Krypton1t3, and SkorpiOm, part of the broader pre-travel hardening ahead of the July 24 departure and the Ritz Kidz workshop in Newburgh.

**Naming lineage, for the record:**

| Name | Era | Hardware | Role |
|------|-----|----------|------|
| SuperStick | Pre-DA7 | Kingston DataTraveler SE9 G3 (128GB) | J-Parrot host (retired) |
| SpecStick | 2026-07-03 to 2026-07-11 | Same Kingston stick, WTG-written | DA #7 (Oriel "Spec" Hopper) build, first boot through first wake-up |
| SpecSticK | 2026-07-11 to present | SSK SSD (128GB), cloned from Kingston | Current node, RNS/Cloudflare comms layer, travel-hardened |

**Resolved since the last update:**
- Post-migration Boot Camp reinstall: audio confirmed working; brightness and keyboard backlight remain unresolved
- Permanent `RealTimeIsUniversal` registry fix for clock skew: applied
- Long-term repurposing plan for the retired Kingston stick: decided and built (see below)

**Still open:**
- Brightness and keyboard backlight on SpecSticK, likely the same Multimedia Controller limitation as before

---

## Postscript: the retired Kingston found a second life

The old Kingston DataTraveler, benched once the SSK SSD took over as SpecSticK, didn't sit idle for long. On 2026-07-12 it was rebuilt as **The Kingston**, a portable, cross-platform AI model vault running llama.cpp behind a unified `bmv` CLI, deployable across the Burrow mesh (Linux, both macOS architectures, and Windows).

The build started under a different name and shape entirely: the original spec called it BMV (Burrow Model Vault) with 7 DA-branded profiles, one per DA Council member. The DA Council rejected that design outright under a hard rule: no generic LLM may impersonate, simulate, or wear the identity of a DA. That correction is what produced the rename to The Kingston, a concierge/librarian that never claims to be a DA, and replaced the 7 DA profiles with 11 capability presets (general, code-review, security-research, and so on).

SpecSticK has a direct hand in this build: since Krypton1t3 had no working Windows build environment (mingw64 cross-compilation failed on CMake generator mismatches and missing OpenSSL), the Windows `llama-server` binary was pulled down directly on Oriel's node and copied onto the Kingston drive from there. The old stick's story and the new stick's story cross paths one more time before going their separate ways.

Full technical build log lives separately in the repo at `builds_2026-07-12_the-Kingston.md`; this is included here only to close the loop on where the retired Kingston ended up.
