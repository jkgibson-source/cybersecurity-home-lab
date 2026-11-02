# Operation FatBoy Flashing

## PS3 Fat NOR patch and Evilnat 4.90 CEX CFW installation record

> **Status:** Completed successfully
> **Console nickname:** FatBoy
> **Outcome:** The console booted Evilnat 4.90 CEX CFW, returned to the XMB, and retained Joe's original user profile.

## Purpose and evidence standard

This report records the successful NOR-patching and custom-firmware installation performed on a PlayStation 3 Fat known as **FatBoy**. It is written as a preservation and technical record, with special attention to Joe's existing profile and data.

The surviving conversation contains strong evidence for the result and several important operational details, but it does **not** expose every earlier message or screenshot from the dumping and patching phase. Accordingly, this report uses the following labels:

- **Verified** — directly stated in the surviving conversation or visible in its retained photographs.
- **Reported** — stated in the conversation's retrospective summary, but the underlying earlier screen or command output is not available in the retained record.
- **Unknown / not preserved** — not recoverable from the available conversation; no value is invented.
- **Reproduction guidance** — a safe checklist for a future, comparable operation, not a claim that every named command was used during this one.

No calendar date is asserted because the retained evidence does not establish one. No download URL is supplied because the original source URL was not preserved. The console's unique MAC address is deliberately omitted, and its private LAN address is redacted for a public repository.

## Executive summary

FatBoy was identified as a **NOR-based PS3 Fat**. Its original 16 MiB NOR flash was backed up and reported as verified before the flash was patched. Evilnat **4.90 CEX** custom firmware was then installed through the PS3's normal system-update interface from removable media. The installer completed and rebooted the console. An **EVILNAT** boot logo appeared, the XMB loaded, and the existing **Joe** profile was still present.

The post-install System Information screen showed:

| Item | Verified result |
|---|---|
| System software | Version 4.90 |
| Firmware identity | Evilnat 4.90 CEX, shown by the update screen and EVILNAT boot logo |
| Flash architecture | NOR |
| Internal storage | 74 GB reported capacity |
| Free space | 4,390 MB (approximately 4.39 GB) |
| Existing user data | Joe's profile remained present |
| Network | Connected on a private `10.0.0.0/8` LAN; exact host address redacted |
| MAC address | Omitted from this public record |

The system was therefore operational after the patch and CFW installation. The most urgent follow-up is a genuine backup of the internal hard drive's irreplaceable content before adding homebrew, repartitioning, attempting OtherOS, or making other substantial changes.

## Scope and key distinction: NOR is not the hard drive

The verified NOR dump is a rescue artifact for the console's flash. It does **not** contain the contents of FatBoy's internal hard drive.

Specifically, a 16 MiB NOR backup does **not** back up:

- Joe's profile data stored on the HDD;
- save data;
- installed games or game data;
- photos, music, videos, or other user files;
- the complete HDD filesystem or its encryption-dependent contents.

This distinction matters because the post-install screen showed only **4,390 MB free out of 74 GB**. Roughly 69–70 GB was occupied. The successful firmware operation preserved access to that data, but did not create a copy of it.

## Hardware, storage, and network record

### Verified hardware facts

- The target was a PlayStation 3 Fat nicknamed **FatBoy**.
- The console uses **NOR**, not NAND, flash architecture.
- A NOR dump size of **16 MiB** was reported and is consistent with the identified architecture.
- The internal drive reported **74 GB** total and **4,390 MB** free after installation.
- Removable media referred to as **BIGJOEDAWG** was used during the firmware-install phase.

### Unknown hardware details

The retained record does not establish the following, so they should be added later only from a label photograph or another authoritative record:

- exact PS3 model number (`CECH...`);
- motherboard revision;
- minimum version check result;
- original OFW version before the operation;
- internal HDD manufacturer/model;
- USB device filesystem and partition-table details;
- exact browser/flash-tool build or version.

### Privacy treatment

The System Information photograph includes a unique hardware MAC address. That value is intentionally **not transcribed**. It adds little reproducibility value and is an unnecessary device identifier in a public GitHub repository.

The console also displayed a private IPv4 address in the `10.0.0.0/8` range. Private addresses are not Internet-routable, but publishing the exact host address can still reveal local-network structure. This report therefore records only the private range and redacts the host portion.

## Artifacts and integrity record

### Original NOR backup

| Property | Record |
|---|---|
| Artifact | Original pre-patch NOR dump(s) |
| Expected size | 16 MiB (16,777,216 bytes) |
| Backup status | **Reported as verified before patching** |
| Number of independently captured dumps | Not preserved in the retrievable record |
| Original filename(s) | Unknown / not preserved |
| Storage locations | Unknown / not preserved |
| SHA-256 | Unknown / not preserved |
| MD5 | Unknown / not preserved |
| Validator and result details | Exact tool/version and full output unknown / not preserved |

The conversation's completion summary explicitly says the original NOR was **verified and backed up**, and later distinguishes that verified 16 MiB NOR backup from an HDD backup. However, the surviving transcript does not include the earlier command output or hash strings. Supplying plausible-looking values would corrupt the preservation record, so no checksum is fabricated here.

If the original dump files still exist, calculate and append their hashes without renaming or modifying the originals:

```sh
shasum -a 256 original-nor-dump.bin
md5 original-nor-dump.bin
wc -c original-nor-dump.bin
```

On Linux, the equivalent commands are commonly:

```sh
sha256sum original-nor-dump.bin
md5sum original-nor-dump.bin
stat --format='%s bytes' original-nor-dump.bin
```

For two independently created dumps, a byte-for-byte comparison can be recorded with:

```sh
cmp --silent dump-1.bin dump-2.bin && echo 'IDENTICAL' || echo 'DIFFERENT'
```

These commands are **reproduction guidance**. The retained conversation does not prove which operating system or exact commands were used during Operation FatBoy Flashing.

### Evilnat update package

| Property | Record |
|---|---|
| Firmware | Evilnat 4.90 CEX CFW |
| Package filename on PS3 media | Normally `PS3UPDAT.PUP`; exact on-media filename not preserved |
| Expected update-media path | Normally `/PS3/UPDATE/PS3UPDAT.PUP`; exact retained path not available |
| Edition/build suffix | Unknown / not preserved beyond “4.90 Evilnat CEX” |
| SHA-256 | Unknown / not preserved |
| MD5 | Unknown / not preserved |
| Download source URL | Unknown / not preserved |

The PS3 update screen itself displayed **“System Software Version 4.90 Evilnat CEX,”** which verifies the firmware family and target type selected by the console. The exact build variant and package checksum cannot be recovered from the available evidence.

## Chronology

The source material establishes sequence, but not trustworthy wall-clock dates or times. The chronology is therefore phase-based.

### 1. Identify the console and flash architecture

- FatBoy was established to be a PS3 Fat using **NOR** flash.
- The NOR-specific workflow was chosen; the Evilnat agreement's NAND-specific warning was noted as not directly applicable to this console.
- This did **not** make the operation risk-free: writing system flash always carries brick risk if validation, compatibility, power, or the write process fails.

### 2. Create and verify the original flash backup

- A **16 MiB original NOR backup** was created.
- The backup was reported as verified before proceeding.
- The precise filenames, count of dumps, validator, validation output, and hashes are absent from the retrievable record.
- The backup was treated as a critical recovery artifact and not confused with an HDD/user-data backup.

### 3. Patch the NOR

- The NOR was successfully patched.
- The console remained bootable and proceeded to the custom-firmware update stage.
- The retained record does not establish the exact patching utility, utility version, browser URL, button labels, or patch output; those details are therefore not claimed.

### 4. Prepare the CFW update

- Evilnat **4.90 CEX** was placed on removable media associated with the name **BIGJOEDAWG**.
- The PS3's System Update process found and checked the update data.
- The update information screen identified the package as **System Software Version 4.90 Evilnat CEX**.
- The retained record does not contain the package's source URL or checksum.

### 5. Review warnings and preserve scope

The installer agreement presented several advanced-feature warnings:

- QA Flags were recommended for later flexibility with compatible CFW versions and downgrades.
- OtherOS setup on the internal HDD requires a destructive restore/repartition workflow and a complete prior data backup.
- Swapping kernels while an external kernel is loaded from USB/flash can brick the console and may require a hardware flasher for repair.
- NAND OtherOS operations carry a specific severe warning; FatBoy was already identified as NOR, but OtherOS and kernel operations remain dangerous.

The operation intentionally did **not** include OtherOS configuration, HDD repartitioning or formatting, account-ID changes, or kernel experiments.

### 6. Install Evilnat 4.90 CEX

- The “turn off automatically after update” option was left unchecked.
- Installation was started from the PS3 update interface.
- Power and removable media were not to be interrupted or removed during the update.
- A retained photograph shows installation underway at 5% with the system warning not to turn it off and stating that it would restart automatically after completion.
- The installation completed and the PS3 rebooted.

### 7. Validate the result

Post-install validation consisted of multiple independent observations:

1. The startup screen displayed **EVILNAT** rather than the standard PlayStation branding.
2. The console successfully reached the XMB.
3. The existing **Joe** user profile was visible and usable at the user-selection area.
4. `Settings → System Settings → System Information` reported **Version 4.90**.
5. The same screen reported **4,390 MB / 74 GB** free space and showed active private-LAN connectivity.

The standard System Information screen displaying only `4.90` is normal and, by itself, does not distinguish OFW from CFW. In this operation, the Evilnat-labeled update screen and EVILNAT boot logo supplied the stronger CFW identification.

## Joe's profile and data preservation

Preserving Joe's existing material was a primary constraint, not an incidental success condition.

### What was preserved and verified

- The console returned to the XMB after CFW installation.
- The user named **Joe** was still present.
- The update did not visibly force an HDD format.
- The drive still showed substantial occupied space, consistent with existing content remaining on it.

### What was not yet proven

The retained record does not show a file-by-file audit of saves, installed content, media, licenses, trophies, or account activation state. The continued presence of the profile is excellent evidence of non-destructive installation, but it is not a complete integrity check of every HDD object.

### Required preservation follow-up

Before experimenting further:

1. Inventory the Joe profile's important saves, media, installed titles, and account-dependent content.
2. Make at least one HDD/user-data backup using a method appropriate to the content and the console's encryption/activation constraints.
3. Copy irreplaceable exports to a second physical device.
4. Verify copied files by reopening them or comparing hashes where practical.
5. Keep the original NOR dump in at least two separate, clearly labeled locations.
6. Do not assume a raw HDD transplant or PC copy will be independently readable; PS3 storage is console-bound and recovery planning should account for that.

## OtherOS and future-change cautions

OtherOS is explicitly **out of scope** for the completed operation.

The Evilnat agreement states that preparing the internal HDD for OtherOS involves entering Recovery Menu and selecting **Restore PS3 System**, which formats the HDD and creates an OtherOS partition. On FatBoy, doing that before preserving Joe's data would defeat the project's preservation goal.

Before any future OtherOS attempt:

- complete and verify an HDD/user-data backup;
- document the current partition and storage state;
- confirm the instructions for the exact PS3 model, NOR architecture, installed Evilnat build, and intended kernel;
- obtain a tested recovery plan and understand whether hardware flashing equipment would be required after a failure;
- never swap kernels while an external kernel is loaded from USB/flash;
- do not treat the NOR backup as protection against HDD formatting;
- ensure stable power and do not combine OtherOS work with unrelated firmware changes.

QA Flags may be useful, and the installer recommended enabling them, but the retained record does not prove they were enabled. Their status should be checked before documenting them as active.

## Troubleshooting record and decision notes

### System Information shows only “4.90”

**Observation:** The post-install System Information page displayed `Version 4.90`, not an Evilnat suffix.

**Resolution:** This was treated as expected behavior. CFW identity was instead corroborated by the **4.90 Evilnat CEX** update screen and the **EVILNAT** boot logo, together with a successful XMB boot.

### Installer offers automatic shutdown after the update

**Decision:** Leave the option unchecked.

**Reasoning:** A normal restart made it possible to immediately observe whether Evilnat booted successfully. The option was not characterized as dangerous; it was simply unnecessary for this validation plan.

### Installer displays severe OtherOS, NAND, and kernel warnings

**Decision:** Continue only with the CFW installation; perform no OtherOS setup, formatting, account-ID change, or kernel switching.

**Reasoning:** FatBoy was identified as NOR, so the NAND-specific warning was not the console's architecture. The broader risks of formatting, kernel misuse, and flash changes still applied.

### Very low free space discovered

**Observation:** Only **4,390 MB** remained free on a **74 GB** drive.

**Implication:** Avoid piling on homebrew or large packages before inventorying and backing up existing data. Low space can also complicate updates, package installation, temporary extraction, and backup workflows.

### If a future update is not detected

This did not block the recorded operation, but a comparable future workflow should check:

- that the USB media is readable by the PS3;
- that the package is named exactly `PS3UPDAT.PUP`;
- that the directory is exactly `/PS3/UPDATE/`;
- that the package hash matches a trusted publication for the exact build;
- that the firmware is compatible with the console and current flash state;
- that no unrelated storage devices are confusing device selection.

### If a flash dump fails validation

Do **not** patch or write the flash. Create fresh dumps, compare them byte-for-byte, check their exact size, and investigate every validator warning. A validator's “danger” or “bad dump” result is not a prompt to force the next step.

## Lessons learned

1. **Back up before writing.** A recoverable original NOR dump is foundational evidence and a potential recovery asset.
2. **Verification must be recorded, not merely remembered.** Future operations should save filenames, byte counts, validator versions/output, and at least SHA-256 hashes in the project log at the moment they are produced.
3. **Flash backup and user-data backup solve different problems.** The NOR copy protects firmware-level recovery; it does not preserve Joe's HDD content.
4. **Use multiple success signals.** Successful XMB boot, the EVILNAT logo, the Evilnat-labeled package screen, system-version reporting, and profile survival together provide stronger evidence than any single screen.
5. **Protect privacy in public documentation.** Unique MAC addresses should not be published. Exact private IPs are rarely useful and can be redacted.
6. **Treat installer warnings as scope boundaries.** OtherOS, repartitioning, account-ID changes, and kernel swapping were postponed rather than folded into an already high-risk firmware operation.
7. **Storage pressure deserves immediate attention.** With only 4.39 GB free, preservation and cleanup planning should precede substantial additions.
8. **Preserve source provenance.** Future logs should retain the trusted download URL, release name, package size, SHA-256/MD5, and a copy of the release notes without relying on browser history.

## Known unknowns and recommended additions

The following fields should be filled only if the original artifacts or screenshots are recovered:

- operation date and timezone;
- exact `CECH` model;
- original OFW version;
- minimum-version-check result;
- flash-tool name, URL, and version;
- exact NOR dump filenames and number of independent dumps;
- dump validator name/version and full result;
- SHA-256 and MD5 of every original dump;
- whether multiple dumps were byte-identical;
- patched-dump filename and hashes, if a patched file was produced;
- exact Evilnat release/build suffix;
- source URL and publisher/release page;
- Evilnat PUP byte size, SHA-256, and MD5;
- exact USB filesystem and update path;
- QA Flag status;
- a post-install inventory or backup record for Joe's HDD data.

## Appendix A — concise reproduction checklist

This appendix is a cautious outline for a **comparable** NOR-console workflow. It is not a substitute for model-specific, release-specific instructions from trusted maintainers.

### Before touching flash

- [ ] Record the exact `CECH` model and verify that the console is CFW-capable.
- [ ] Confirm NOR versus NAND using authoritative model/hardware evidence.
- [ ] Confirm the current firmware and minimum-version result.
- [ ] Arrange stable power; do not proceed during outage risk.
- [ ] Preserve important HDD/user data separately.
- [ ] Obtain the flash tool and CFW only from trusted sources.
- [ ] Record the source URLs, release names, file sizes, and published hashes.
- [ ] Hash the downloaded PUP locally and compare it with the trusted value.

### Dump and validate

- [ ] Create at least two independent flash dumps if the selected workflow supports it.
- [ ] Confirm each NOR dump is exactly 16,777,216 bytes.
- [ ] Compare the dumps byte-for-byte.
- [ ] Validate the dump with the appropriate current validator.
- [ ] Stop on unexplained warnings or disagreement between dumps.
- [ ] Record SHA-256 and MD5 for each dump.
- [ ] Store verified originals in at least two physical locations; make one copy read-only.

### Patch and install

- [ ] Reconfirm that the patch method matches the exact console architecture and current firmware.
- [ ] Close unrelated browser work and do not interrupt the patch/write process.
- [ ] Confirm successful patch completion before rebooting or moving on.
- [ ] Put the verified CEX PUP at `/PS3/UPDATE/PS3UPDAT.PUP` on compatible removable media.
- [ ] Confirm the PS3 identifies the intended **Evilnat 4.90 CEX** package before accepting.
- [ ] Do not remove media or cut power during installation.
- [ ] Leave unrelated options and advanced features for a later, separately documented change.

### Validate and preserve

- [ ] Observe a normal reboot and the EVILNAT boot logo.
- [ ] Confirm the XMB loads.
- [ ] Confirm the expected user profiles remain, including Joe's profile in this case.
- [ ] Check `Settings → System Settings → System Information`.
- [ ] Record firmware, capacity, and free space; redact MAC and exact local IP in public records.
- [ ] Confirm important saves/content rather than relying only on profile visibility.
- [ ] Back up the HDD/user data before installing homebrew or attempting OtherOS.
- [ ] Record QA Flag state before relying on downgrade/recovery flexibility.

## Appendix B — hash-record template

```text
Artifact:
Original filename:
Purpose:
Source URL:
Retrieved date/time/timezone:
Size (bytes):
SHA-256:
MD5:
Validator name/version:
Validator result:
Compared byte-identical with:
Storage locations:
Notes:
```

## Final status

**Operation FatBoy Flashing succeeded.** FatBoy's NOR was backed up and reported verified, the NOR patch completed, Evilnat 4.90 CEX installed, the console rebooted to the XMB under Evilnat, and Joe's profile survived.

The operation's firmware goal is complete. The preservation goal is only partially complete until Joe's HDD-resident data has been inventoried and backed up independently of the 16 MiB NOR image.
