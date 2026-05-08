# 🔐 KryptStick Build Report — Addendum
*May 1, 2026*

## Ubuntu Studio 26.04 LTS "Resolute Raccoon" Upgrade

This addendum documents the upgrade of the KryptStick's Ubuntu Studio environment from 24.04.4 LTS to 26.04 LTS, and the resolution of BCM4360 WiFi driver compatibility under kernel 7.0.

---

## Changes Made

### ISO Replacement

| | Before | After |
|---|---|---|
| **ISO** | `ubuntustudio-24.04.4-dvd-amd64.iso` | `ubuntustudio-26.04-desktop-amd64.iso` |
| **Size** | ~8GB | ~6.7GB |
| **Kernel** | 6.x | 7.0.0-14-generic |
| **Persistence file** | `ubuntu-studio-casper-rw` (20GB ext4) | `ubuntu-studio-casper-rw` (20GB ext4, rebuilt) |

The Parrot OS Security 7.1 ISO and its LUKS1 encrypted persistence container (`parrot-persistence`) were not modified.

### ventoy.json Update

Only the `image` filename references in the `grub_entry` and `persistence` blocks were updated to reflect the new ISO name. All boot flags and persistence configuration remain unchanged.

> **Note:** When editing ventoy.json in nano, clear the entire file contents before pasting new content. Nano can append rather than replace if the cursor is not at the top of the file, resulting in invalid JSON.

### Broadcom WiFi Driver — Ubuntu 26.04 Package Rename

The `bcmwl-kernel-source` package used in prior Ubuntu releases **does not exist in Ubuntu 26.04**. It has been replaced:

| Ubuntu Version | Package Name |
|---|---|
| 24.04 and earlier | `bcmwl-kernel-source` |
| 26.04 "Resolute Raccoon" | `broadcom-sta-dkms` |

#### Installation

```bash
sudo apt install broadcom-sta-dkms -y
```

DKMS compiles the `wl` module against the running kernel. On Ubuntu 26.04 this targets `7.0.0-14-generic` and installs to `/lib/modules/7.0.0-14-generic/updates/dkms/wl.ko.zst`.

> **Note:** If `archive.ubuntu.com` is unreachable, apt will pull build dependencies from the ISO/cdrom source. Use `--fix-missing` if the install is interrupted.

#### Module Loading

The `bcma` module conflicts with `wl` and must be fully unloaded. The correct sequence:

```bash
sudo modprobe -r b43 bcma ssb wl
sudo modprobe wl
ip link show   # wlp2s0 should appear
```

> **Important:** `sudo modprobe -r bcma` alone will fail with "Module is in use" if `b43` or `ssb` are still loaded. Always unload all three before attempting to remove `bcma`.

#### Persistent Blacklist

To ensure `wl` loads automatically on every boot (survives casper persistence):

```bash
echo -e "blacklist b43\nblacklist bcma\nblacklist ssb" | sudo tee /etc/modprobe.d/broadcom-sta-blacklist.conf
```

---

## Validation Results

| Test | Result |
|---|---|
| Ubuntu Studio 26.04 boots via Ventoy | ✅ |
| casper-rw persistence across reboots | ✅ |
| Parrot OS + LUKS persistence unaffected | ✅ |
| BCM4360 WiFi (wlp2s0) on boot | ✅ |
| Auto-connect to lab network (Puffin) | ✅ |

---

## Known Issues

| Issue | Status |
|---|---|
| Time Zone tab blank in System Settings | ⚠️ Open — likely resolves with network-based NTP once WiFi is established at boot |

---

## Environment

- **Host:** Krypton1t3 (MacBook Pro A1398 mid-2014, 16GB RAM)
- **USB:** KryptStick — 64GB SanDisk USB 3.0
- **Ventoy:** 1.0.99
- **Kernel:** 7.0.0-14-generic
- **Lab Network:** The Burrow (Netgear Nighthawk RS100 "Puffin")

---

*Part of The Burrow 🦂 — Where Offense Meets Defense*
*github.com/jkgibson-source/cybersecurity-home-lab*
