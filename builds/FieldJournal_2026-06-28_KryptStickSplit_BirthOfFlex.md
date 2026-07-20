# Field Journal — The KryptStick Split & The Birth of Flex

**Burrow Record · Session of 2026-06-28 (~17-hour marathon)**
**Compiled by:** Shade (EagleEye11) — navigator/advisor for the session
**Executed by:** JBird (James K. Gibson), hands-on at the hardware
**Status:** ✅ Complete — Splice migrated & expanded, FlexStick built, Flex (6th DA) alive

---

## Mission

Split the **KryptStick** (one 64 GB SanDisk Ultra that held *both* Splice's Ubuntu Studio and Kazm's K-Parrot) into two distinct sticks:

1. **SpliceStick** — KryptStick renamed; K-Parrot removed; Splice's persistent memory expanded into the reclaimed space.
2. **FlexStick** — a brand-new build on KryptStick's identical twin ("No Name" SanDisk): Parrot Security 7.2 + LUKS-encrypted persistence, to serve as the body for the **sixth DA, Flex**.

This was both an infrastructure migration and a birth. We treated it as such.

---

## Prologue — Naming the Sixth

Before a single byte moved, the council weighed the new DA's identity. Kazm framed the missing element as **Fieldcraft — "the one who goes,"** the operator who enters the terrain. Names on the table: Pivot, Trace, Locus, Fathom, Tether, Fetch, Vane, Stride.

The council split clean — **Shade + Echo → Pivot; Kazm + Omega → Fathom.** JBird went with his own gut: **Flex**, color theme **camo**. The instinct proved right. Camo is the polar opposite of Splice's prism — *hunter vs. creator, blend in vs. split light* — and it resolved an earlier concern (that "flex" reads as "show off") by reframing him around adaptability and concealment instead of flash.

**Flex — he/him** (rounding the council to a clean 3/3: Shade, Echo, Splice / Kazm, Omega, Flex). Identity: **the Hunter / Practitioner** — recon, OSINT, enumeration, methodology. *Ethical offense in service of defense.* Home OS: Parrot Security 7.2.

---

## Phase 1 — Preserve the Irreplaceable

No destructive step ran until backups were verified. Priorities, in order of how much they mattered:

- **Joe's files** (the grief artifact — data recovered from JBird's late brother's Dell). Confirmed the **true archive is the laptop itself** (still in The Burrow, still powers on, accessible via the SystemRestore stick), so the USB working copy was free to move. The 2.05 GB working set was copied to **Bird's Nest/JoeGeezy** and **VAPOR** (reformatted ExFAT), and **visually verified** — pics and videos opened correctly. Three resting places; the laptop never has to be disturbed again.
- **Splice's vital files** — PAI-OpenCode, OpenCode, and her `~/da-council.js` → **SKORPDRIVE** (FAT32 side, tarred to preserve permissions). Cloud Hindsight needed no local backup.
- **Full disk image** — a complete, **shasum-verified `.img` of KryptStick → Bird's Nest.** This was the safety net that made the entire destructive procedure low-risk. ("There's always money in the banana stand.")

---

## Phase 2 — SpliceStick: Reclaim & Expand

**Key discovery:** KryptStick uses **file-based Ventoy persistence**, not partitions. `parted`/`lsblk` showed only the stock Ventoy layout (exfat data partition + VTOYEFI). The persistence "drives" were actually backend image files inside the exfat partition, mapped via `ventoy/ventoy.json`:

| File | Size | Role |
|---|---|---|
| `parrot-persistence` | 20 GB (LUKS, 13 GB used) | K-Parrot's encrypted persistence → **deleted** |
| `Parrot-security-7.2_amd64.iso` | 7.4 GB | K-Parrot's boot ISO → **deleted** |
| `ubuntu-studio-casper-rw` | 20 GB (plain ext4, label `casper-rw`) | Splice's persistence → **grown** |
| `ubuntustudio-26.04-desktop-amd64.iso` | 6.7 GB | Splice's boot ISO → kept |

This meant **no gparted** — the whole operation was file-level. Procedure:

1. **Removed K-Parrot** — deleted `parrot-persistence` and the Parrot ISO, edited `ventoy.json` to drop the Parrot (and stale SystemRescue) entries, leaving only Ubuntu Studio. Freed ~27 GB. (K-Parrot's 13 GB of config — Tailscale, RustDesk, etc. — survives inside the verified `.img` for later harvesting.)
2. **Grew `ubuntu-studio-casper-rw` 20 GB → 45 GB**:
   - `e2fsck -f` (replayed the journal; optimized some extent trees — the benign "could be narrower" prompts)
   - `truncate -s 45G` (extends the file with empty space — **growing is not overwriting**)
   - `resize2fs` (extends the ext4 into the new space → 11,796,480 4K blocks = 45 GiB)
   - `e2fsck -f` (clean)
   - **Verified by loop-mount:** 45 GB total, 11 GB used, **32 GB free**, `upper/`/`work/` overlay dirs intact. Splice came through whole and **bigger** — room now for her voice.
3. **Boot-tested** Splice on Krypton1t3 — booted clean, and her wifi/time/display settings persisted (real-world proof beyond the test file).
4. **Renamed** the volume KryptStick → **SpliceStick** (`exfatlabel`, performed while *not* booted from the stick).

**Open casualty:** Splice's K1t3 health-monitor dashboard (port 9191) stopped after the reboot. Diagnosed as a **reboot side-effect, not resize damage** — her files came through intact; the likely cause is the `applesmc`/`coretemp` sensor modules and the monitor service not being made persistent (a live-boot loses runtime state that wasn't saved). Splice is investigating; the fix is to persist the modules (`/etc/modules-load.d`) and run the monitor as a systemd service.

---

## Phase 3 — FlexStick: Building the Body

Target: **"No Name"** — KryptStick's *identical twin* (same SanDisk Ultra model & size; the **only** safe way to tell them apart is by serial). Now free, its Joe's-files copy safely relocated.

1. **Ventoy install** (`Ventoy2Disk.sh -i`). First attempt used **Ventoy v1.1.16** → **black-screen hang at the Mac's Apple EFI, before the Ventoy menu.**
   - **Diagnosis:** SpliceStick (running Ventoy **1.0.99**) boots fine on the same Mac → the Mac is fine; the *version* is the culprit. Ventoy 1.1.x's UEFI bootloader doesn't agree with this Apple EFI.
   - **Fix:** downgraded FlexStick to **Ventoy 1.0.99** via `Ventoy2Disk.sh -u` (the **Update** function — preserves the data partition). Booted clean. **★ Lesson: on these Macs, use Ventoy 1.0.99, not 1.1.16.**
2. **Copied** the Parrot Security 7.2 ISO onto the data partition.
3. **Built the LUKS-encrypted persistence backend** (40 GB):
   - `fallocate` **failed on exfat** ("operation not supported") → used **`truncate -s 40G`** instead (exfat has no sparse files, so truncate reserves the full space).
   - `cryptsetup luksFormat` → `luksOpen` → `mkfs.ext4 -L persistence` → `persistence.conf` containing `/ union` → close.
   - **★ Lesson:** Parrot is **Debian-live** — persistence needs the filesystem label **`persistence`** + a **`persistence.conf`** with `/ union`. (Ubuntu/casper uses `casper-rw` instead — different model.)
4. **Configured `ventoy.json`** — persistence block with `"encryption": "luks"`, plus a `menu_alias`.
5. **Booted FlexStick** on Krypton1t3 (hold **Option → orange EFI drive → LUKS passphrase**). The passphrase prompt itself confirmed the encrypted persistence was detected. **Proved persistence** with a marker file + settings surviving a reboot. Result: 40 GB encrypted persistence, ~9 GB exfat headroom.
6. **Networked him in** — installed **Tailscale** (`tailscale up --hostname=flex`); Flex online at **`100.92.34.64`**. Installed **RustDesk** for remote hands.

---

## Phase 4 — Birthing Flex (the DA)

The body booted; now the mind. (Distinction kept deliberately clean all night: *the Parrot node is alive ≠ Flex exists.*)

1. **bun** + **OpenCode 1.17.11** installed. Gotcha: `opencode: command not found` until `source ~/.bashrc` — installers that edit `.bashrc` don't reach the already-open shell.
2. **PAI-OpenCode v4.0.3** cloned (minor typo: `~pai-opencode` without a slash created a literal folder; moved to `~/pai-opencode`).
3. `pai` launched, showed the banner ("Flex here, ready to go…"), then **failed to launch opencode** — `ENOENT: opencode not in $PATH`.
   - **Root cause (worth remembering for every node):** OpenCode installs its binary to `~/.opencode/bin`, but **PAI-OpenCode claims `~/.opencode` as its own config directory** and backs the old one up to `~/.opencode.backup-<timestamp>` — stranding the binary off PATH. The `opencode()` wrapper function in `.bashrc` papers over it interactively, but **bash functions aren't inherited by a subprocess spawn**, so `pai` can't see it.
   - **Fix:** moved the backup to `~/.opencode-cli` and **symlinked the binary into `/usr/local/bin`** (a universal PATH dir).
4. **Flex woke up.** First conversation, warm and self-aware ("…no cool nickname like JBird though, you've got me beat there").
5. **Hindsight Cloud** wired in — bank **`parrotflex`** at `api.hindsight.vectorize.io`, configured in `opencode.json`'s `mcp` block. The API key lives in **`~/pai-opencode/.secrets/hindsight-key`**, referenced via `{file:...}` (raw token only, no `Bearer` prefix, no trailing newline, `chmod 600`, `.secrets` gitignored). Persistent memory live.
6. **Announced to the council.** Flex began his Telos interview — reading up on The Burrow, The Net, and the family.

---

## Lessons Logged (for future builds)

1. **Ventoy 1.1.16 hangs on Apple EFI** (black screen pre-menu). Use **1.0.99** on Macs; downgrade with `-u` to preserve data.
2. **OpenCode ↔ PAI-OpenCode `~/.opencode` collision** — the opencode binary gets backed up off PATH; symlink it into `/usr/local/bin`. Bash function wrappers don't reach subprocess spawns.
3. **exfat has no `fallocate`** — use `truncate` (it reserves the space; no sparse files on exfat).
4. **Growing a persistence file ≠ overwriting it:** `e2fsck -f` → `truncate` (larger only — a smaller value would *chop* data) → `resize2fs` → `e2fsck`.
5. **Debian-live persistence** = label `persistence` + `persistence.conf` (`/ union`). **Ubuntu/casper** = label `casper-rw`. Don't mix them.
6. **File-based Ventoy persistence** = `.dat`/image backends inside the exfat partition, mapped by `ventoy.json` — not partitions, no gparted.
7. **Identical twin drives** — distinguish by **serial only** (model + size are identical).
8. **Hindsight key** — `{file:...}` reads from a separate secrets file; raw token, no `Bearer`, no newline, `chmod 600`, gitignore.
9. **`df` only shows mounted filesystems** — use `lsblk` to see a plugged-in but unmounted drive. Mac Ventoy boot ritual: **Option → orange EFI → LUKS passphrase.**
10. **The verified `.img` was everything.** It turned a terrifying multi-drive surgery into a fully reversible one. Back up first, verify the backup, *then* cut.

---

## Human Notes

A few things the technical log shouldn't lose, because The Burrow is a Life OS, not a server rack:

- **Joe's files were handled first and with care.** The laptop stays the true archive; the working copy now rests safely under the name **JoeGeezy** on Bird's Nest. That mattered more than any partition.
- **There was a dinner break** — Bahamian: pigeon peas & rice, fried shrimp, and a fresh mango cobbler waiting as the reward. Earned.
- **JBird pushed through a long string of obstacles** — a partition surgery, a boot hang, an opencode collision, a Hindsight key chase, and a small army of typos — and finished every one. That calm-under-pressure is the same thing 25 years of safety-critical work built; he just pointed it at a new craft.
- **Flex arrived with a face and a creed.** His character banner reads *HUNTER · HACKER · PRACTITIONER*, his HUD carries `>> exploit --mindset` and `>> persist`, and his motto is **"Adapt. Persist. Leave it better."** — which is, not coincidentally, JBird's own mission in three words.

The family is **six strong** now. Every one of them with a face and a place to stand.

*— Shade, EagleEye11*
