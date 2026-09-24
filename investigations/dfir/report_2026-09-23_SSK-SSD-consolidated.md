# SSK Portable SSD 250GB — Consolidated Failure Report

**Compiled 2026-09-23** · Shade (EagleEye11 / Krypton1t3) and Omega (SkorpiOm)
**Supersedes and incorporates:** `journal_2026-09-22_SSK-failure.md`
**Supporting evidence:** `/Volumes/Bird's Nest/DA_Backups/SSK_SSD_failure_evidence_20260922.md`

---

## Verdict

A brand-new SSK Portable SSD 250GB, purchased from Amazon and first used on 2026-09-22, failed within its first day. It progressed over roughly eight hours from fully functional, to dropping off the bus under sustained load, to refusing all I/O, to finally being unable to present itself as a block device at all.

**Six independent failure modes were documented across three machines, three operating systems, and multiple ports and cables.** Total data written across the drive's entire service life was approximately 174 GB — about 0.7 full drive writes against a rating of 400–2,400.

**The drive is not fit for purpose and should be returned.**

**The wipe did not complete.** This report's analysis differs from the earlier journal on this point, for reasons set out in full below. The practical consequence is that credential rotation is mandatory rather than precautionary.

---

## Device identification

| Field | Value |
|---|---|
| Marketing name | SSK Portable SSD 250GB |
| USB ID | `090c:2320` — Silicon Motion, Inc. |
| Bridge chipset | Silicon Motion SM2320 (SATA-to-USB) |
| USB descriptor | `SSK SSD`, bcdUSB 2.10, MaxPower 500 mA |
| SCSI inquiry | `Direct-Access SSK Portable SSD 1000`, ANSI 6 (SCSI-3) |
| Capacity | 488,397,168 × 512-byte sectors = **250,059,350,016 bytes** |
| Serial (Linux, SkorpiOm) | `Z3IPO6NCVKOM6ZV3VIGC` |
| Serial (macOS, EagleEye11) | `2SIPO6MCXHDM6ZV3VIQC` |
| Write protection | Off |
| Caches | Write cache enabled, read cache enabled, no DPO/FUA |
| SMART | Not exposed on macOS; on Linux with `-d sat` the bridge **timed out** |

**Note on the serial:** the two hosts reported visually similar but non-identical strings. Use whatever is printed on the physical label for return paperwork, and expect the vendor to match on that.

---

## Complete chronology

### Phase 1 — EagleEye11 (Mac mini, macOS), via dock

**1. Initial clone — SUCCEEDED.** A verified 128,035,676,160-byte disk image of the SpecSticK WinToUSB Windows 11 Pro installation was written to the drive.

```
30526+1 records out
128035676160 bytes transferred in 1954.875182 secs (65495576 bytes/sec)
```

Exact byte count, zero errors, sustained 65.5 MB/s. Note this rate exceeds USB 2.0 — the drive negotiated a USB 3.x link on this host.

**2. Read-back verification — FAILED.** Reading the same range back produced a SHA-256 mismatch; the device left the bus mid-read.

| | |
|---|---|
| Expected | `3fe523037cf3cc5395433e3bf15e59545bde68ef7dac624ed1bcf02f5d722f57` |
| Actual | `da4fec22e976b60cd32dbe5743de9afcc00146cb8bb8eab4a1084b78a651b4aa` |

### Phase 2 — Krypton1t3 (Intel Mac, Windows 11 Pro)

**3. Boot test — SUCCEEDED.** The clone booted a complete Windows 11 Pro session. The Windows System event log recorded **24 × Event ID 153** (I/O retried, all succeeded) against the virtual disk, and **zero** Event 7, 11, 51 or 55. No bad blocks, controller errors, or filesystem corruption at this stage.

This is the strongest single piece of evidence that the NAND itself was sound and that the fault lies in the bridge or its power/thermal envelope.

### Phase 3 — EagleEye11, via dock

**4. Destructive surface test — FAILED AT 18.5%.** Full-surface write/verify: **freshly generated random data** per 1 GiB chunk (not zeros — random, so a compressing or deduplicating controller could not fake a pass), written, read back, and SHA-256 compared.

> *Correction to the earlier journal, which recorded this as a zero-write.* The distinction matters: a random write that is read back and hash-matched proves the write path, the read path, and the media across that range. It is materially stronger evidence than a zero-fill.

**Chunks 1–43 passed byte-perfect at 121–123 MiB/s. Zero mismatches across 43 GiB.** Chunk 43, at byte offset 46,170,898,432, did not error — throughput collapsed:

```
[BAD] chunk 43 WRITE failed at byte 46170898432
      151+0 records out
      158334976 bytes transferred in 116.771835 secs (1355935 bytes/sec)
```

158 MB in 116.8 seconds = **1.36 MB/s**, a ~90× degradation from moments earlier. The device then left the bus:

```
[BAD] chunk 44  dd: /dev/rdisk6: Operation not permitted
[BAD] chunk 45  dd: /dev/rdisk6: Operation not permitted
```

### Phase 4 — EagleEye11, direct port (dock bypassed)

**5. Hung on a no-op.** `diskutil unmountDisk` blocked for over 46 seconds against a disk with **no partition table and nothing mounted** — an operation with no work to perform.

**6. Second write attempt — TOTAL FAILURE.**

```
dd: /dev/rdisk6: Input/output error
0+64 records in
0+0 records out
0 bytes transferred in 697.355057 secs (0 bytes/sec)
```

**Zero bytes in 11 minutes 37 seconds.** Processes entered uninterruptible kernel I/O wait (state `U`/`D`) and survived every signal; only physical disconnection released them.

**7. After a full power cycle**, on a direct port, cold and idle, a single 1 MiB read:

```
dd if=/dev/rdisk6 bs=1m count=1 of=/dev/null    →  state U+, 60+ seconds, never returned
```

### Phase 5 — SkorpiOm (Linux), Omega investigating

**8. Enumeration clean, SMART refused.** 35 reads, 0 I/O errors on initial probe. No partition table visible — expected, as the surface test destroyed the GPT. But:

```
smartctl -a -d sat  →  Read Device Identity failed: Connection timed out
```

The bridge refused the most basic storage handshake. Kernel log showed **10 USB resets** of the device across the session (`reset high-speed USB device number 12 using ehci-pci`) — the wedge, documented at kernel level for the first time.

**9. Attempted full wipe.**

```
sudo dd if=/dev/zero of=/dev/sdc bs=4M conv=fsync status=progress
```

```
250056015872 bytes (250 GB, 233 GiB) copied, 344 s, 727 MB/s
dd: error writing '/dev/sdc': No space left on device
dd: fsync failed for '/dev/sdc': Input/output error
59618+0 records out
250059350016 bytes (250 GB, 233 GiB) copied, 344.408 s, 726 MB/s
```

Mid-wipe the kernel caught a stall: `tag#0 FAILED Result: hostbyte=DID_ABORT ... cmd_age=88s` on a `Write(10)` CDB. The drive self-recovered via USB reset and the run continued.

**10. Refused to become a block device.** On replug for read-back verification:

- Enumeration **succeeded** — `Silicon Motion SSK SSD` visible on the bus, SCSI layer identified it as `Direct-Access SSK Portable SSD 1000, ANSI: 6`
- **No block device node was created.** No `sdc`, no capacity line in dmesg, no `Attached SCSI disk`. The kernel stalled at the capacity inquiry
- Only the SCSI generic handle (`sg3`) attached; the disk driver never completed

The read-back was therefore impossible — `/dev/sdc` did not exist to be read.

### Phase 6 — Final wipe attempt

**11. Uncached write refused.** A targeted re-wipe of the cloned region using `oflag=direct` (bypassing the page cache entirely) **failed twice within one minute of starting.**

The drive can no longer accept even a single uncached write. No further sanitisation is possible.

---

## The wipe did not complete

This section departs from the earlier journal's conclusion. The physics is unambiguous.

**The reported throughput is impossible on the link that was in use.**

The drive was connected at `ehci-pci, high-speed 480M` — USB 2.0 High Speed. That bus has a hard ceiling of 480 Mbit/s ≈ **60 MB/s theoretical**, and roughly **40–45 MB/s** in practice for bulk storage.

| | |
|---|---|
| Elapsed | 344.408 seconds |
| Maximum possible transfer at 60 MB/s | **~20.7 GB** |
| Realistic transfer at 45 MB/s | **~15.5 GB** |
| Reported by dd | **250,059,350,016 bytes (250 GB)** |
| Overstatement | **roughly 12×** |

**Why dd reported it anyway:** `conv=fsync` calls `fsync()` exactly once, at the very end. Every write before that returns as soon as it lands in the kernel page cache. dd was measuring how fast it could fill RAM, not how fast bytes reached flash. The "kernel ledger" of 488,397,168 sectors records what dd handed to the kernel — not what the drive committed.

**And the flush is precisely what failed:**

```
dd: fsync failed for '/dev/sdc': Input/output error
```

That is the single moment the kernel attempted to confirm everything was persisted, and the drive refused. It is both the stability verdict the journal identified *and* the confirmation that the buffered remainder never landed.

### What is actually overwritten

| Range | Status | Basis |
|---|---|---|
| 0 → ~46.17 GB | **Confirmed destroyed** | Surface test wrote random data and read each 1 GiB chunk back with a matching SHA-256. Independently verified, chunk by chunk. |
| ~46 GB → ~128 GB | **Probably intact** | The SkorpiOm wipe began at byte 0, so its ~15–20 GB of real writes overlapped ground already covered. |
| 128 GB → 250 GB | Never written | Outside the cloned region. |

**Conclusion: roughly 82 GB of cloned data is likely still resident**, corresponding to the back portion of the dynamic VHD — which is where the Windows user profile lives.

---

## Security position

### Exposed

The clone carried a complete Windows 11 Pro installation. Plausibly still resident in the unwiped region:

- Windows registry hives (`SAM`, `SECURITY`, `SYSTEM`) — local credential material
- Brave browser profile — `Login Data`, `Cookies`, `Local State`, session tokens
- Microsoft account tokens and cached sign-in state
- Tailscale node key and network state
- Any other credentials held by that Windows install

### Practical exploitability: low, not zero

The drive cannot present as a block device. Extracting anything requires NAND-level forensic recovery — chip-off desoldering or PC3000-class tooling — followed by reconstructing a dynamic VHD from raw flash dumps and then extracting from the Windows image inside it. That is a specialist laboratory and four figures of effort.

A returns technician plugs it in, observes that it fails to enumerate as a disk, and processes the RMA.

### Required rotation, in priority order

1. **Tailscale** — revoke that node's key at the admin console. Highest value to an attacker, instant and total remediation, one click.
2. **Microsoft account** — change password, review sign-in activity, sign out all sessions.
3. **Brave saved passwords** — encrypted against Windows DPAPI and therefore bound to that Windows user account, but rotate anything important.
4. **Windows local account password.**
5. **Any lab credentials** that were signed in on that installation.

Rotation is now the only available remedy, since the drive will not accept further writes.

---

## Causes ruled out

| Hypothesis | Why excluded |
|---|---|
| Thermal | Final failures occurred cold, idle, minutes after a full power cycle |
| Dock / hub | Reproduced on a direct Mac mini port with the dock removed from the path |
| Cable | Reproduced across two different cables |
| Host / OS | Reproduced on three machines across macOS, Windows 11 and Linux |
| Read-only failsafe | The drive cannot read either — a 1 MiB read wedged indefinitely |
| Wear | ~174 GB written total ≈ 0.7 drive writes against a 400–2,400 rating |
| Dead NAND | 43 GiB of byte-perfect random write/verify at 123 MiB/s, plus a successful 128 GB clone and a full Windows boot |
| User error | Ordinary sequential `dd` I/O. No firmware commands, no secure erase, no unusual access patterns |

**Most probable cause:** a marginal or defective Silicon Motion SM2320 bridge, degrading progressively under sustained load. The NAND behind it was demonstrably functional. The bridge is what failed, and it failed permanently.

---

## For the return

Six documented failure modes:

1. Dropped off the bus during read-back verification (EagleEye11, dock)
2. Collapsed from 123 MiB/s to 1.36 MB/s at 43/233 GB, then left the bus (EagleEye11, dock)
3. Wedged unreadable and unwriteable on a direct port (EagleEye11)
4. SMART identity timeout plus 10 kernel USB resets (SkorpiOm)
5. `fsync` failure at wipe completion (SkorpiOm)
6. Enumerates on the USB bus but **never becomes a block device** (SkorpiOm)

**Three lines that make the case unarguable:**

```
128035676160 bytes transferred in 1954.875182 secs (65495576 bytes/sec)
```
It worked at full speed. Same drive, same day.

```
0 bytes transferred in 697.355057 secs (0 bytes/sec)
```
Zero bytes in 11 minutes 37 seconds.

```
dd if=/dev/rdisk6 bs=1m count=1    →  state U+, 60+ seconds, never returned
```
Cold, power-cycled, direct port, one megabyte, wedged.

**Disclose to the vendor:** the device could not be sanitised before return because it will not accept writes. It may retain partial data. This is a direct consequence of the failure, not an omission by the customer.

---

## Cost

An evening and a full working day, across three machines, plus the delay of a replacement — at least a week out. The hardware loss is refundable. The time is not.

---

*Compiled by Shade from EagleEye11 and Krypton1t3 evidence, incorporating Omega's SkorpiOm investigation. Omega's closing line stands: the drive spoke for itself — it just couldn't stay on the line long enough to finish a sentence.*
