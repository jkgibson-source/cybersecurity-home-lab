# 🦂 SuperStick Build Report — Kali Persistence Layer Addendum

![Status](https://img.shields.io/badge/status-validated-brightgreen?style=for-the-badge)
![Platform](https://img.shields.io/badge/platform-Jynx13%20%7C%20SuperStick-blue?style=for-the-badge)
![Mode](https://img.shields.io/badge/mode-Kali%20Live%20Persistence-purple?style=for-the-badge)
![The Burrow](https://img.shields.io/badge/The%20Burrow-build%20log-black?style=for-the-badge)

> **The Burrow | April 26, 2026**  
> **Prepared by:** JBird | [`jkgibson-source`](https://github.com/jkgibson-source)  
> **Build Track:** SuperStick / Jynx13 / Portable Cybersecurity Toolkit  
> **Session Result:** ✅ Kali persistence validated with a 6GB plain ext4 backend

---

## 🧭 Document Purpose

This addendum supplements the original **SuperStick** build documentation with findings from the April 26, 2026 persistence rebuild session. It supersedes prior notes regarding **Kali Linux persistence configuration on Ventoy 1.0.99** and establishes the validated baseline for future SuperStick builds.

This session confirmed that **Jynx13 can now boot Kali mode with working persistence**, using a plain ext4 persistence file instead of a LUKS-encrypted file backend.

---

## ⚡ Build Snapshot

| Category | Result |
|---|---|
| Primary Objective | Restore working Kali persistence on SuperStick |
| Target Machine | Jynx13 — 13" 2017 MacBook Air |
| Build Machine | SkorpiOm — MacBook Pro A1286 running Kali Linux Xfce |
| Boot Platform | Ventoy 1.0.99, GPT mode |
| Validated Kali Backend | `kali-test-persist` |
| Working Kali Persistence Size | 6GB |
| Working Kali Persistence Type | Plain ext4 file backend |
| Failed Kali Persistence Type | LUKS-encrypted file backend |
| Parrot Persistence Status | Still working with 40GB LUKS1 backend |

---

## 🧰 Hardware & Software Reference

| Component | Detail |
|---|---|
| USB Drive | Kingston DataTraveler 128GB USB 3.2 Gen 1 |
| Boot Manager | Ventoy 1.0.99, GPT mode |
| Build Machine | SkorpiOm — MacBook Pro A1286, Kali Linux Xfce |
| Test Machine | Jynx13 — MacBook Air 2017, macOS Monterey host |
| Kali Version | Kali Linux 2026.1 live-amd64 |
| Parrot Version | Parrot OS Security 7.1 amd64 |

---

## 🧪 Findings Summary

### Finding 1 — Ventoy File-Based LUKS Persistence Is Not Compatible with Kali 2026.1

**Status:** ❌ Incompatible  
**Impact:** Kali boots successfully, but persistence silently fails.

Kali 2026.1 live-boot does not successfully unlock LUKS-encrypted file-based persistence backends when booted through Ventoy 1.0.99. The kernel command line shows `rdinit=/vtoy/vtoy`, which indicates that Ventoy replaces the standard initramfs init process with its own `vtoy` script.

That script passes the `persistence` kernel parameter, but the LUKS-encrypted file backend is not mounted into `/run/live/persistence/`. The result is a clean live boot with no persistent storage attached.

**Evidence:**

```text
dmesg output:
BOOT_IMAGE=/live/vmlinuz-6.18.12+kali-amd64 boot=live components quiet splash
noeject findiso= persistence rdinit=/vtoy/vtoy
```

```text
ls /run/live/persistence/   →   empty
mount | grep persistence    →   no output
```

The overlay upper directory maps to `tmpfs`, meaning the live session is writing to RAM. Any session changes are lost after reboot.

**Validated workaround:** Use a plain ext4 persistence file for Kali.

> **Burrow Note:** Parrot OS 7.1 is unaffected in this build. Its live-boot implementation handles Ventoy’s LUKS handoff correctly, and the 40GB LUKS1 Parrot persistence file continues to function normally.

---

### Finding 2 — File Size Limit Exists for Kali Persistence on Ventoy 1.0.99

**Status:** ⚠️ Confirmed constraint  
**Impact:** Persistence files that are too large may fail without warning.

Ventoy 1.0.99 combined with Kali 2026.1 live-boot appears to enforce an effective file size limit for file-based persistence backends. The failure mode is silent: no obvious error appears during boot, but persistence does not activate.

| File Size | Filesystem | Result |
|---|---|---|
| 2GB | Plain ext4 | ✅ Works |
| 6GB | Plain ext4 | ✅ Works |
| 10GB | Plain ext4 | ❌ Fails silently |
| 10GB | LUKS1 | ❌ Fails — LUKS incompatibility plus size constraint |
| 40GB | LUKS1 | ❌ Fails — original broken Kali persistence file |

**Validated ceiling:** 6GB  
**Unresolved boundary:** Somewhere between 6GB and 10GB

**Recommendation:** Do not exceed 6GB for Kali persistence files on this configuration unless the larger file size is tested and validated first.

---

### Finding 3 — Diagnostic Path for Persistence Failures Has Changed in Kali 2026.1

**Status:** ℹ️ Reference update  
**Impact:** Older diagnostic paths may produce false assumptions.

Prior documentation referenced `/lib/live/mount/` as the live-boot mount path. That directory does not exist in this Kali 2026.1 build. The correct diagnostic path is now:

```text
/run/live/
```

**Updated diagnostic commands:**

```bash
# Check whether the persistence backend is mounted.
# This is the key indicator.
ls /run/live/persistence/

# Check overlay mount behavior.
# The upper directory should NOT be tmpfs if persistence is working.
mount | grep -E "persistence|loop|overlay"

# Confirm the persistence kernel parameter was passed.
dmesg | grep -i persistence

# Verify a file's actual filesystem type before debugging.
sudo mount -o loop /path/to/persistence-file /mnt/test

# If output is:
# unknown filesystem type 'crypto_LUKS'
# then the file is LUKS, not plain ext4.
```

---

### Finding 4 — Persistence File Identity Must Be Verified Before Debugging

**Status:** ℹ️ Process note  
**Impact:** Filename assumptions can waste boot cycles.

During this session, a LUKS-encrypted file was renamed to a plain-sounding filename, `kali-test-persist`, and was initially tested as though it were a plain ext4 file. Running `mount -o loop` immediately revealed the actual filesystem type: `crypto_LUKS`.

**Rule:** Always verify a persistence file’s actual type with `mount -o loop` before assuming its contents. Do not rely on filename alone.

---

## ✅ Validated Build Procedure — Kali Plain ext4 Persistence

The following procedure is validated for **Kali 2026.1 on Ventoy 1.0.99**. Execute on **SkorpiOm** with SuperStick attached as `/dev/sdc`.

> ⚠️ Confirm the correct block device before running write operations. Device names can change between sessions.

```bash
# 1. Mount SuperStick
sudo mount /dev/sdc1 /mnt/superstick

# 2. Create 6GB persistence file
sudo dd if=/dev/zero of=/mnt/superstick/kali-test-persist bs=1M count=6144 status=progress

# 3. Format as ext4 with persistence label
sudo mkfs.ext4 -L persistence /mnt/superstick/kali-test-persist

# 4. Mount and write persistence.conf
sudo mkdir -p /mnt/kali-persistence
sudo mount -o loop /mnt/superstick/kali-test-persist /mnt/kali-persistence
echo "/ union" | sudo tee /mnt/kali-persistence/persistence.conf

# 5. Verify
cat /mnt/kali-persistence/persistence.conf
# Must show: / union

# 6. Clean up
sudo umount /mnt/kali-persistence
sync
sudo umount /mnt/superstick
```

---

## 🧩 Validated `ventoy.json`

```json
{
    "persistence": [
        {
            "image": "/kali-linux-2026.1-live-amd64.iso",
            "backend": "/kali-test-persist"
        },
        {
            "image": "/Parrot-security-7.1_amd64.iso",
            "backend": "/parrot-persistence",
            "encryption": "luks"
        }
    ]
}
```

**Validated Kali boot path:**

```text
Ventoy
└── Select Kali ISO
    └── Boot with /kali-test-persist
        └── Kali GRUB
            └── Live system with USB persistence
```

---

## 🗂️ Current SuperStick Partition & File Layout

```text
/dev/sdc1   115.5G   exFAT   Ventoy data partition
/dev/sdc2      32M   vFAT    VTOYEFI

/mnt/superstick/
├── kali-linux-2026.1-live-amd64.iso     5.3GB
├── Parrot-security-7.1_amd64.iso        7.2GB
├── DragonOS_Noble_R9.iso                3.9GB
├── kali-test-persist                    6GB, plain ext4 — WORKING
├── parrot-persistence                   40GB, LUKS1 — WORKING
└── ventoy/
    └── ventoy.json
```

---

## 🔍 Future Investigation Queue

| Item | Purpose | Priority |
|---|---|---|
| Test 8GB Kali persistence file | Narrow the ceiling between 6GB and 10GB | Medium |
| Test partition-based LUKS persistence | Determine whether a LUKS1 partition bypasses the Ventoy file-backend issue | Medium |
| Review Ventoy changelog before upgrade | Check whether later Ventoy versions address Kali 2026.1 LUKS compatibility | Low |
| Revalidate Parrot after any Ventoy upgrade | Ensure the currently working 40GB LUKS1 Parrot backend remains intact | High if upgrading |

---

## 🧠 Lessons Captured

- Kali 2026.1 persistence through Ventoy works reliably with a **6GB plain ext4 file backend**.
- Kali 2026.1 does **not** currently work with this build’s LUKS-encrypted file backend.
- Parrot OS 7.1 continues to support the existing **40GB LUKS1 persistence backend**.
- `/run/live/` is the correct Kali 2026.1 diagnostic path for this build.
- Persistence debugging should begin with filesystem identity verification, not filename assumptions.

---

## 🏁 Build Session Result

**SuperStick now has a validated Kali persistence layer for Jynx13.**

This gives Jynx13 a functional Kali mode for portable field use while preserving the existing Parrot OS encrypted persistence setup. The result is not the original ideal design, but it is a clean, tested, and repeatable baseline.

> **Outcome:** Persistence achieved. SuperStick survives another build session. The Burrow gets sharper. 🦂

---

## 📎 Suggested Repo Placement

Recommended location:

```text
/builds/superstick/superstick-persistence-addendum-2026-04-26.md
```

Alternate location if SuperStick becomes a dedicated project folder:

```text
/projects/superstick/docs/superstick-persistence-addendum-2026-04-26.md
```

---

## 🦂 The Burrow Footer

**The Burrow — Miami, FL**  
*Portable labs. Persistent lessons. Clean documentation.*  
*"The obstacle is the path."* 🦂
