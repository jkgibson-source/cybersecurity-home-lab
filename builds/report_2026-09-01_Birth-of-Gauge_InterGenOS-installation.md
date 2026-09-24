# Report — 2026-09-01 — InterGenOS Installation on Kingston

**Author:** Kazm (Krypton1t3Kazm) on behalf of J-Bird (SuperSkorp_7)
**Scope:** Full account of the InterGenOS portable boot installation on the KingstonBMV USB stick — from the initial backup through to a working wifi connection. Compiled from Hindsight memory records and the project journal.
**Status:** ✅ Wifi resolved (2026-09-01). Boot chain working. Remaining cosmetic items: trackpad (pending) and desktop audio configuration.

---

## 1. Overview

The goal was to build a portable, fully-encrypted, bootable copy of **InterGenOS** — a custom LFS-based (Linux From Scratch) distro — on the **KingstonBMV** 128GB USB stick, so it could boot on K1t3 (MacBookPro11,2) and Jynx13 (MacBook Air / MacBookAir7,2). The build is self-compiled with kernel **6.18.10-igos-17**, hostname **burrowforge**, user **t3ls0n**.

This report chronicles the journey from **Friday 2026-08-28** (initial backup) through **Tuesday 2026-09-01** (wifi connected to the "Puffin" network).

---

## 2. Hardware

| Item | Detail |
|------|--------|
| KingstonBMV stick | 128GB USB. GPT partition layout: `sdb1` = 1G vfat ESP, `sdb2` = ~114.5G LUKS2-encrypted root. |
| Target machine 1 | **K1t3** (MacBookPro11,2) — Fedora host, the primary build/deploy machine. Stick enumerates as `/dev/sdb`. |
| Target machine 2 | **Jynx13** (MacBook Air / MacBookAir7,2 per DMI) — Intel i5-5350U. |
| Wifi chipset | **Broadcom BCM4360 802.11ac** (PCI ID `14e4:43a0`, Apple subsystem `106b:0117` = BCM94360CS2). Driven by the proprietary **`wl`** driver (broadcom-sta). No open-source `brcmfmac` firmware exists for this PCIe ID. |
| Trackpad | BCM5974 controller (no extra firmware required). |
| Kernel | `6.18.10-igos-17 #7 SMP PREEMPT_DYNAMIC`, built with Kazm's assistance in `/home/SuperSkorp_7/kernbuild/`. |

> **Note on capacity:** KingstonBMV is a **128GB** stick. Earlier records mislabeled the Kingston as "1TB"; that confusion was corrected on 2026-08-27 (the 1TB figure belonged to the fake-capacity SuperStick, identified as ChipsBank CBM2199).

---

## 3. Initial Backup (Friday, 2026-08-28)

Before any destructive work, the stick's existing contents were safely preserved:

- **Backup completed** to **SKORPDRIVE** on 2026-08-28.
- **Backup scope:** the Kingston **digital-concierge project files** (the "BMV / The Kingston" concierge interface data) — not the entire raw stick image. This was a deliberate, instruction-scoped backup.
- **Prior context (July):** KingstonBMV was originally a **travel drive** used mainly to hold movies during J-Bird's travels, plus the Kingston concierge interface. The BMV project was renamed to **"The Kingston"** on 2026-07-12 (a concierge/librarian interface, not a DA, per DA-Council architectural correction).
- **Authorization:** Kazm explicitly waited for **J-Bird's approval** before wiping KingstonBMV and installing InterGenOS (2026-08-28T17:02Z). The wipe only proceeded after that go-ahead.

---

## 4. Installation & Boot Chain (2026-08-28 → 2026-08-31)

### 4.1 First bootable attempt — failure
On **2026-08-28** an initial attempt to make Kingston bootable with an "InterGenOS-node" image failed. The GPT table was intact but the **filesystem was corrupted with I/O errors**, and writes died during a USB reset storm. This was the first of several hardware/interop hurdles.

### 4.2 Wipe + InterGenOS layout
After J-Bird's approval, the drive was wiped and laid out:
- **ESP (sdb1)** — 1G vfat EFI System Partition.
- **LUKS2-encrypted root (sdb2)** — the InterGenOS root filesystem.

### 4.3 FDE / LUKS boot failure (2026-08-30)
The first boot failed at the decryption stage with an **`Invalid argument [fde-init]`** error and "wrong passphrase." Root causes identified and fixed:
- The `6.18.10-igos-17` kernel was **missing crypto cipher support** (`CONFIG_CRYPTO_XTS` / AES), so it could not construct the `aes-xts-plain64` cipher for LUKS2.
- **Fix:** rebuild the kernel with `CONFIG_CRYPTO_XTS` and `CONFIG_CRYPTO_AES` enabled, then regenerate the initramfs/UKI.
- The LUKS root partition itself verified intact via `e2fsck` (no errors; 127k files recovered during earlier recovery work).

### 4.4 Keyboard at the passphrase prompt (2026-08-30)
Typing the LUKS passphrase on the built-in MacBook keyboard did not work. Root cause: the **`hid_apple`** driver was neither bundled into the initramfs nor modprobed before the passphrase prompt.
- **Fix:** added `hid_apple` to `REQUIRED_MODULES` (line 313 of `fde-init.sh`) in `/home/SuperSkorp_7/intergenos-src`, changed the keyboard modprobe loop for compat, and bundled it into the initramfs CPIO. This enabled typing the passphrase with the built-in keyboard (no external keyboard needed).

### 4.5 Boot chain / module-signing wall (2026-08-30 evening → 2026-08-31)
A second set of failures centered on **kernel lock-down + module signature enforcement**:
- `module.sig_enforce=0` did **not** disable enforcement because the rebuilt kernel had `CONFIG_MODULE_SIG_FORCE=y`.
- The **built-in certificate did not match** the signatures of modules in the initramfs/rootfs.
- **Fix:** rebuild the kernel with the boot-critical drivers **built-in** (`CONFIG_*=y`) — **HID_APPLE, FAT, VFAT, MSDOS, NLS_UTF8** — so the boot path did not depend on signed loadable modules behind the lock-down wall.
- The **UKI was MOK-signed** with the recovered K1t3 MOK and deployed to the Kingston ESP.
- **Result:** *"K1t3 Kingston USB fully working with InterGenOS on MacBook"* — **full boot chain working** (milestone recorded 2026-08-31T04:54Z).

### 4.6 Post-boot hardware: lock-down & backlight
Post-boot hardware issues (wifi/brightness/backlight) were traced to kernel **lock-down**. Fix deployed 2026-08-31: set **`CONFIG_LOCK_DOWN_KERNEL_FORCE_INTEGRITY` → `FORCE_NONE`** (lock-down disabled) — the root-cause fix for post-boot hardware access problems.

### 4.7 A build hiccup
During a kernel rebuild (2026-08-30) the `make` hit **Error 2 in `drivers/gpu/drm`** (a silent failure during the nouveau LD step). This was resolved as part of the rebuild cycle.

---

## 5. The WiFi Saga (2026-08-29 → 2026-09-01)

Wifi was the longest-running and most complex problem. It had **two independent layers**, each fixed separately.

### 5.1 Layer 1 — Driver loading (module layer)
**Symptom:** no wireless device; `wl` not loading or being blocked.
- **2026-08-29:** Applied a persistent **blacklist of `b43`** and auto-loaded **`brcmfmac`** via config — later proven unnecessary on the real kernel.
- **2026-08-29/30:** The Broadcom STA driver could not load because the kernel had **`CONFIG_MODULE_SIG_FORCE=y`** (hardcoded module-signature enforcement). The real fix direction was to rebuild with **`CONFIG_MODULE_SIG_FORCE=n`** (or `MODULE_SIG=n`).
- **2026-08-31 (#7 kernel):** Rebuilt with **`CONFIG_BRCMFMAC=m` / `CONFIG_BRCMUTIL=m`** (brcmfmac as module, out of vmlinux) — resolving the earlier brcmfmac built-in "error -22" claim on the card.
- **2026-09-01:** Final module-layer blocker: `wl` failed to autoload with **"Exec format error."** Root cause: `cfg80211`/`rfkill`/`mac80211` are **built-in** to the kernel, but the rootfs still shipped **stale `cfg80211.ko.gz` + `rfkill.ko.gz`** modules and a stale `modules.builtin` that didn't mark them built-in. When `modprobe wl` ran, it tried to load the stale deps → kernel rejected them (duplicate symbol, already built-in) → load aborted.
  - **Fix (`fix-wl-autoload.sh`):** removed the stale `cfg80211.ko.gz`/`rfkill.ko.gz`, installed the authoritative `modules.builtin`/`modules.builtin.modinfo` from the new build, re-ran `depmod`.
  - **Result:** `wl` now **autoloads** and the BCM4360 adapter is found with no manual intervention.

### 5.2 Layer 2 — Scanning (nl80211 vs wext) — THE REAL SCAN ROOT CAUSE
Even with `wl` loaded and the device found, `nmcli device wifi list` / `rescan` returned **empty**, `/proc/net/wireless` showed flat zeros, and the regulatory domain sat at `00`. After ruling out driver/firmware, rfkill, and the regulatory database, the decisive finding was:

> **NetworkManager only drives wifi through `nl80211`, but the proprietary `wl` driver's cfg80211 registration is *partial*.** It exposes `phy80211` and satisfies rfkill/regulatory, but the scan operation itself is not functionally wired through the nl80211 path. Only **WEXT-mode `wpa_supplicant`** can actually scan on this driver.

Standalone `wpa_supplicant -Dwext -iwlp3s0 ...` scanned **immediately**, returning the full network list including **"Puffin"** at strong signal. This proved the driver and kernel were healthy all along — it was an **architectural mismatch**, not a build defect.

### 5.3 The persistent wifi fix (Claude + J-Bird, 2026-09-01)
1. **NetworkManager unmanages `wlp3s0`:** `/etc/NetworkManager/conf.d/99-unmanage-wlp3s0.conf` — `unmanaged-devices=interface-name:wlp3s0`.
2. **wpa_supplicant config:** `/etc/wpa_supplicant/wpa_supplicant-wlp3s0.conf` (SSID/PSK for "Puffin", `chmod 600`).
3. **systemd override forcing `wext`:** `/etc/systemd/system/wpa_supplicant@wlp3s0.service.d/override.conf` — `ExecStart=/usr/sbin/wpa_supplicant -Dwext -c/.../wpa_supplicant-wlp3s0.conf -iwlp3s0`; enabled via `systemctl enable --now wpa_supplicant@wlp3s0.service`.
4. **DHCP via systemd-networkd** (no `dhcpcd`/`dhclient` in InterGenOS's `pkm` repo): `/etc/systemd/network/25-wlp3s0.network` → `[Match] Name=wlp3s0`, `[Network] DHCP=yes`; enabled via `systemctl enable --now systemd-networkd`.

**Result:** `wlp3s0` associated to **Puffin**, DHCP lease `10.0.0.68/24` via gateway `10.0.0.1`, clean pings to `8.8.8.8` (19–50 ms). **Fully persistent across reboots** — no manual steps.

---

## 6. Kubernetes / networking scope notes

- The **session was conducted over BB (Moto G Play) USB tether** for internet access during parts of the wifi diagnosis (no working network on the stick yet).
- InterGenOS's package manager is **`pkm`** (repo ~1126 packages as of the 2026-08-21 sync). It has **no `iw`, `wireless-tools`, `net-tools`, `dhcpcd`, or `dhclient`** — very thin on standard networking diagnostics at this distro stage. `iproute2` and `wpa_supplicant` are present.
- `networkctl status` reports **`Driver: wl0`** (not `wl`) — a useful fingerprint if this NM/driver incompatibility resurfaces after a kernel/driver update.

---

## 7. Current Status & Known Remaining Items

| Item | Status |
|------|--------|
| Full boot chain (ESP + LUKS FDE) | ✅ Working |
| Built-in keyboard at passphrase | ✅ Working (`hid_apple`) |
| Kernel build (`6.18.10-igos-17 #7`) | ✅ Deployed |
| **Wifi — driver autoload** | ✅ Working (`wl` autoloads) |
| **Wifi — scan & connect (Puffin)** | ✅ Working (`wpa_supplicant -Dwext` + systemd-networkd) |
| DHCP on 10.0.0.68/24 | ✅ Working |
| Trackpad | ⏳ **Pending** — reported not working after boot on 2026-08-31; credibly needs `bcm5974`/`appletouch`/`i2c-hid` driver addressed separately post-boot. BCM5974 needs no firmware. |
| Desktop audio configuration | ⏳ **Cosmetic/desktop-layer** — kernel audio hardware is fine (CS4208 PCH + HDMI detected), but the desktop session shows empty output/input device dropdowns; volume buttons/click have no effect (same family as the brightness-button Linux quirk on this hardware). |
| USB wifi adapter (long-term option) | 🎯 Reserve — if BCM4360 keeps biting, a supported **USB wifi adapter** is the eventual clean fallback (not needed now). |

---

## 8. Key Lessons & Fingerprints

1. **`networkctl status` → `Driver: wl0`** — fingerprints the proprietary driver behind the interface.
2. **Built-in vs module metadata drift** — after any kernel rebuild, sync the rootfs `modules.builtin`/`modules.dep` with the build, or `modprobe` will try to load stale built-in modules and fail (the "duplicate symbol / Exec format error" class).
3. **`CONFIG_MODULE_SIG_FORCE` and lock-down** — must be aligned with signed/built-in module strategy for any self-built kernel on Macs.
4. **Broadcom proprietary `wl` + modern NetworkManager** = nl80211 scan incompatibility; drop to **WEXT-mode `wpa_supplicant`** for scanning.
5. **KingstonBMV is 128GB**, not 1TB. The fake-capacity red flag lives with the separate SuperStick (ChipsBank CBM2199, corrupts past ~14GB).
6. **Backup-before-wipe discipline:** existing Kingston concierge data was safely preserved on SKORPDRIVE and J-Bird explicitly authorized the wipe before installation.

---

## 9. Remote Access (Tailscale mesh + SSH) — added 2026-09-01

- InterGenOS joined the **Tailscale mesh** as node **`burrowforge`**, **100.70.251.5** (Tailscale OS type: linux, owner `jk.gibson@`).
- **SSH server (OpenSSH) is already listening on port 22** on the stick — no package install was needed.
- **Key auth:** K1t3's public key (`krypton1t3_burrow.pub`, ED25519) is installed at `~t3ls0n/.ssh/authorized_keys` on the stick. Public-key material only — no passphrases or private keys are recorded in this document.
- **Bootstrap path used:** `tailscale file cp` pushed the pubkey file (`k.pub`) to burrowforge's Tailscale inbox; retrieved on-box with `tailscale file get .` (note: this version requires the target-directory argument), then appended to `authorized_keys`.
- **Two working routes:**
  - **Mesh:** `ssh t3ls0n@100.70.251.5` (identity-based Tailscale check was approved once; K1t3's tailscaled re-auth loop was fixed by `sudo systemctl restart tailscaled` on K1t3).
  - **LAN fallback:** `ssh t3ls0n@10.0.0.69` (same LAN as K1t3; IP may change with DHCP).
- **K1t3 `~/.ssh/config`:** `Host burrowforge` → `HostName 100.70.251.5`, `User t3ls0n`, `IdentityFile ~/.ssh/krypton1t3_burrow`, `IdentitiesOnly yes`.
- **Verified 2026-09-01:** `ssh burrowforge` + `scp` both work; hostname `burrowforge`, kernel `6.18.10-igos-17`.
- **Next:** test the stick on K1t3; then add equivalent `Host burrowforge` entries to Jynx13 (macOS) and Echo so they can SSH in as well.

---

*Report compiled 2026-09-01 from Hindsight memory bank `krypton1t3kazm` and project journal `journal_2026-09-01_intergenos-wifi-fix.md`. No credentials, passphrases, or PSK values are included in this document.*
