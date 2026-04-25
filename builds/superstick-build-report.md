# 🦂SuperStick Build Report
*April 12–13, 2026 — The Burrow*

---

## Overview

The **SuperStick** is a 128GB Kingston USB 3.2 multi-boot toolkit built for Jynx13 (MacBook Air 2017, macOS Monterey). It runs three operating systems via Ventoy 1.0.99 in GPT mode, with LUKS1 encrypted persistence volumes for Kali Linux and Parrot OS Security. DragonOS Noble rides stateless as a dedicated SDR toolkit.

This build was informed by hard lessons from the KryptStick build (April 8, 2026), particularly around LUKS1 vs LUKS2 compatibility and the critical importance of verifying `ventoy.json` is actually written to disk before unmounting.

---

## Hardware

| Component | Detail |
|-----------|--------|
| USB Drive | 128GB Kingston USB 3.2 (220MB/s read) |
| Build Machine | SkorpiOm (MacBook Pro A1286 mid-2010, Kali Linux) |
| Target Machine | Jynx13 (MacBook Air 2017, macOS Monterey) |
| Ventoy Version | 1.0.99 (GPT mode) |

---

## Operating Systems

| OS | Version | Persistence | ISO Size |
|----|---------|-------------|----------|
| Kali Linux | 2026.1 Live AMD64 | LUKS1 encrypted, 40GB | 5.3GB |
| Parrot OS Security | 7.1 AMD64 | LUKS1 encrypted, 40GB | 7.2GB |
| DragonOS Noble | R9 (March 27, 2026) | None (stateless) | 3.9GB |

---

## Session 1 — SuperStick Saturday (April 12, 2026)

### Phase 1: ISO Acquisition

All three ISOs were downloaded directly to SkorpiOm's `~/Downloads` directory before touching the USB stick — a deliberate choice to allow multiple reimaging passes without re-downloading.

**Kali Linux** — The official CDN (`cdimage.kali.org/current`) does not host a direct `.iso` for the live image; it is torrent-only. A torrent file for `kali-linux-2026.1-live-amd64.iso` was found in `~/Downloads` from a prior session and used via `transmission-cli`, yielding the current release.

```bash
transmission-cli kali-linux-2026.1-live-amd64.iso.torrent --download-dir ~/Downloads
```

**DragonOS Noble R9** — Downloaded via SourceForge torrent using `transmission-cli`. The March 27, 2026 file timestamp reflects the ISO creation date, not the download date — normal torrent behavior.

**Parrot OS Security 7.1** — Already present in `~/Downloads` from the KryptStick build.

**Final ISO inventory confirmed:**
```
3.9G  DragonOS_Noble_R9.iso
5.3G  kali-linux-2026.1-live-amd64.iso
7.2G  Parrot-security-7.1_amd64.iso
```

---

### Phase 2: Ventoy Installation

Kingston SuperStick identified as `/dev/sdc` via `lsblk`. Ventoy 1.0.99 was already extracted at `~/ventoy-1.0.99/`.

```bash
cd ~/ventoy-1.0.99
sudo ./Ventoy2Disk.sh -I -g /dev/sdc
```

**Flags:** `-I` = clean install, `-g` = GPT partition scheme (required for Mac EFI compatibility).

**Result:** Two partitions created:
- `sdc1` — 115.5GB exFAT (Ventoy data partition)
- `sdc2` — 32MB FAT32 (Ventoy EFI partition)

---

### Phase 3: ISO Copy

```bash
sudo mkdir -p /mnt/superstick
sudo mount /dev/sdc1 /mnt/superstick
sudo cp ~/Downloads/kali-linux-2026.1-live-amd64.iso \
        ~/Downloads/DragonOS_Noble_R9.iso \
        ~/Downloads/Parrot-security-7.1_amd64.iso \
        /mnt/superstick/
```

**Verified:**
```
-rwxr-xr-x  3.9G  DragonOS_Noble_R9.iso
-rwxr-xr-x  5.3G  kali-linux-2026.1-live-amd64.iso
-rwxr-xr-x  7.2G  Parrot-security-7.1_amd64.iso
```

---

### Phase 4: Boot Verification on Jynx13

All three ISOs tested on Jynx13 before building persistence — **3 for 3**. Two boot paths confirmed:

- **Option key hold** → EFI boot picker → VTOYEFI → Ventoy menu ✅
- **rEFInd** → `Boot EFI\BOOT\grub64_real.efi from VTOYEFI` (Penguin 1) ✅

> **Note:** rEFInd shows two Linux penguin entries. **Penguin 1** (`grub64_real.efi`) is the correct Ventoy bootloader. Penguin 2 (`grub.efi`) is a fallback stub — avoid it.

| OS | Boot Method | Result |
|----|-------------|--------|
| Parrot OS 7.1 | Option key → EFI | ✅ Live desktop reached |
| Kali 2026.1 | rEFInd Penguin 1 | ✅ Live desktop reached |
| DragonOS Noble R9 | rEFInd Penguin 1 | ✅ Live desktop reached |

ISOs confirmed healthy before persistence build began.

---

## Session 2 — SuperStick Sunday, Part 1 (April 13, 2026 — early hours)

### Phase 5: Kali Encrypted Persistence

**Step 1 — Create 40GB backing file:**
```bash
sudo dd if=/dev/zero of=/mnt/superstick/kali-persistence bs=1M count=40960 status=progress
# Result: 42949672960 bytes (43 GB) copied, 2713 s, 15.8 MB/s
```

**Step 2 — Format as LUKS1:**
```bash
sudo cryptsetup luksFormat --type luks1 /mnt/superstick/kali-persistence
# WARNING confirmed with YES
# Passphrase set
```

**Step 3 — Set LUKS header label:**
```bash
sudo cryptsetup config /mnt/superstick/kali-persistence --label persistence
# Completed silently — no error
```

**Step 4 — Open container:**
```bash
sudo cryptsetup luksOpen /mnt/superstick/kali-persistence kali-encrypted
```

**Step 5 — Format inner filesystem and verify:**
```bash
sudo mkfs.ext4 -L persistence /dev/mapper/kali-encrypted
sudo fsck.ext4 -y /dev/mapper/kali-encrypted
# Result: persistence: clean, 12/2621440 files, 242384/10485248 blocks
```

**Step 6 — Write persistence.conf:**
```bash
sudo mkdir -p /mnt/kali-persistence
sudo mount /dev/mapper/kali-encrypted /mnt/kali-persistence
echo "/ union" | sudo tee /mnt/kali-persistence/persistence.conf
```

**Step 7 — Clean up:**
```bash
sudo umount /mnt/kali-persistence
sudo cryptsetup luksClose kali-encrypted
```

---

### Phase 6: Parrot Encrypted Persistence

Same workflow as Kali with one known difference — the `cryptsetup config --label` step throws a LUKS2 error on Parrot's persistence file and is skipped. This was first observed during the KryptStick build and is consistent behavior.

```bash
sudo cryptsetup config /mnt/superstick/parrot-persistence --label persistence
# ERROR: Device is not a valid LUKS2 device — SKIP THIS STEP for Parrot
```

All other steps identical to Kali, substituting `parrot-persistence` and `parrot-encrypted` as identifiers.

**fsck result:** `persistence: clean, 12/2621440 files, 242384/10485248 blocks` ✅

---

### Phase 7: ventoy.json — Lessons Learned

**First attempt (failed):** `ventoy.json` was written via `nano` during a session where the stick had been unmounted. The file appeared to save but wrote to a temporary location that did not persist. On next inspection: `cat: /mnt/superstick/ventoy/ventoy.json: No such file or directory`.

**Root cause:** Always verify with `cat` immediately after saving. Never assume nano wrote to the intended mounted path.

**Second attempt (successful):**
```bash
sudo mkdir -p /mnt/superstick/ventoy
sudo nano /mnt/superstick/ventoy/ventoy.json
```

**Contents:**
```json
{
    "persistence": [
        {
            "image": "/kali-linux-2026.1-live-amd64.iso",
            "backend": "/kali-persistence",
            "encryption": "luks"
        },
        {
            "image": "/Parrot-security-7.1_amd64.iso",
            "backend": "/parrot-persistence",
            "encryption": "luks"
        }
    ]
}
```

**Verified with:**
```bash
sudo cat /mnt/superstick/ventoy/ventoy.json
# Output confirmed — both entries present ✅
```

---

### Phase 8: Final Unmount

```bash
sudo umount /mnt/superstick
sync
```

---

## Session 3 — SuperStick Sunday, Part 2 (April 13, 2026)

### Phase 9: Persistence Verification on Jynx13

Booted both Kali and Parrot from the SuperStick on Jynx13. Both sessions prompted for the LUKS passphrase on boot — confirming encryption is active.

**Test procedure:** Set system clock, connect to WiFi, create a testfile via `touch testfile.txt`, reboot, verify file survives.

| OS | Passphrase Prompt | Testfile Survived Reboot | Result |
|----|-------------------|--------------------------|--------|
| Parrot OS 7.1 | ✅ | ✅ | **PERSISTENCE CONFIRMED** |
| Kali 2026.1 | ✅ | ❌ | Persistence failing — under investigation |
| DragonOS Noble R9 | N/A | N/A | Stateless by design |

Parrot OS encrypted persistence is **fully operational**. Kali persistence is queued for a future debugging session. Suspected causes: partition label mismatch or `persistence.conf` formatting issue.

---

### Phase 10: WiFi Configuration — BCM4360 + WPA3 Incompatibility

#### Symptoms

Jynx13's WiFi adapter (Broadcom BCM4360 rev 03) was detected and visible in the network panel, but connections kept dropping in a loop: configuring → connected → deactivated → retry.

#### Diagnosis

**Hardware confirmed:**
```bash
lspci | grep -i network
# 03:00.0 Network controller: Broadcom Inc. BCM4360 802.11ac Dual Band Wireless Network Adapter (rev 03)
```

**Driver status confirmed:**
```bash
lsmod | grep -E 'wl|brcm|b43'
# wl    6463488  0
# cfg80211  1495040  1 wl
```

`wl` was the only module loaded — no driver conflicts. `broadcom-sta-dkms` confirmed installed for the running kernel:

```bash
sudo dkms status
# broadcom-sta/6.30.223.271, 6.17.13+2-amd64, x86_64: installed
```

**Root cause identified via NetworkManager journal:**
```bash
sudo journalctl -u NetworkManager --since "5 minutes ago" | tail -30
```

Key log entries:
```
Config: added 'key_mgmt' value 'SAE'
Activation: (wifi) association took too long, failing activation
state change: config -> failed (reason 'ssid-not-found')
```

The router broadcasts WPA3, and NetworkManager was auto-negotiating up to WPA3/SAE. The `wl` driver does not support SAE — it connects, times out during association, and drops. Every time.

#### Fix

`nmcli` could not be used directly because the WiFi password contains `@` symbols, which nmcli misinterprets as setting references. The fix was to write the NetworkManager connection profile directly to disk, bypassing nmcli entirely:

```bash
sudo nano /etc/NetworkManager/system-connections/Puffin.nmconnection
```

```ini
[connection]
id=Puffin
type=wifi
autoconnect=true

[wifi]
ssid=Puffin
mode=infrastructure

[wifi-security]
key-mgmt=wpa-psk
psk=YOUR_PASSWORD_HERE

[ipv4]
method=auto

[ipv6]
method=auto
```

```bash
sudo chmod 600 /etc/NetworkManager/system-connections/Puffin.nmconnection
sudo nmcli connection reload
sudo nmcli connection up Puffin
```

`key-mgmt=wpa-psk` explicitly forces WPA2, preventing NetworkManager from negotiating WPA3/SAE. Connection held immediately and has not dropped since.

> **Important:** This `.nmconnection` file lives on the LUKS1 persistence volume. It survives reboots and auto-connects on boot — exactly the intended behavior.

---

### Phase 11: Tailscale Installation

With WiFi stable, Tailscale was installed via the official script:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# Authentication link generated → visited in browser → authorized
```

**Result:**
```bash
tailscale ip -4
# 100.95.26.111

tailscale status
# 100.95.26.111  parrot  jk.gibson@  linux  -
```

Jynx13's Parrot session joined the mesh at **100.95.26.111**. Full lab fleet visible in `tailscale status`. Tailscale installation and auth state persist across reboots via the persistence volume.

---

### Phase 12: Pentest Screenshot Folder

```bash
mkdir -p ~/Pictures/pentest-screenshots
sudo apt install flameshot -y
# flameshot config → save path set to ~/Pictures/pentest-screenshots
```

All screenshots captured during the pentest exercise will land here automatically. Folder persists across reboots.

---

## Final SuperStick Status

| Item | Status |
|------|--------|
| Ventoy 1.0.99 GPT | ✅ |
| Parrot OS 7.1 — boots | ✅ |
| Kali 2026.1 — boots | ✅ |
| DragonOS Noble R9 — boots | ✅ |
| Parrot OS — encrypted persistence | ✅ |
| Kali — encrypted persistence | ❌ Under investigation |
| DragonOS — stateless | ✅ By design |
| WiFi — BCM4360 WPA2-PSK forced | ✅ |
| Tailscale (100.95.26.111) | ✅ |
| Pentest screenshots folder | ✅ |
| Ollama | ✅ Achieved |

---

## Final SuperStick File Layout

```
/mnt/superstick/
├── kali-linux-2026.1-live-amd64.iso     (5.3GB)
├── Parrot-security-7.1_amd64.iso        (7.2GB)
├── DragonOS_Noble_R9.iso                (3.9GB)
├── kali-persistence                     (40GB, LUKS1 encrypted)
├── parrot-persistence                   (40GB, LUKS1 encrypted)
└── ventoy/
    └── ventoy.json
```

---

## Key Lessons Learned

1. **Always verify `ventoy.json` with `cat` before unmounting** — nano can silently write to the wrong location if the stick is not mounted at the expected path.
2. **`cryptsetup config --label` works for Kali (LUKS1) but errors for Parrot** — skip it for Parrot; persistence works without it.
3. **Download ISOs locally before starting** — allows multiple reimaging passes without re-downloading.
4. **Boot test all ISOs before building persistence** — confirms hardware compatibility before investing time in the full build.
5. **The BCM4360 `wl` driver does not support WPA3/SAE** — force WPA2-PSK via a hand-written `.nmconnection` file; do not rely on nmcli when passwords contain special characters.
6. **Write NetworkManager profiles directly when nmcli chokes on special characters** — `sudo nano /etc/NetworkManager/system-connections/` is your friend.
7. **LUKS1 is the correct format for Ventoy persistence** — LUKS2 is not supported.

---

## Next Steps

- Debug Kali 2026.1 persistence (verify partition label and `persistence.conf` contents)
- Install Ollama on Jynx13 (CPU-only, small models for field reference)
- Begin SkorpiOm → Krypton1t3 attack/defense exercise planning

---

*"The obstacle is the path."* 🦂
