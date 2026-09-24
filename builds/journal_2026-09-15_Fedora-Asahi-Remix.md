# Field Journal — EagleEye11 Goes Dual-Boot: Fedora Asahi Remix

**Burrow Record · Session of 2026-09-15 → 2026-09-16 (all-day-into-overnight marathon)**
**Compiled by:** Shade (EagleEye11) — navigator/advisor for the session
**Executed by:** JBird (James K. Gibson), hands-on at the hardware
**Status:** ✅ Complete — EagleEye11 (Mac mini M1) now dual-boots macOS + Fedora Asahi Remix (KDE Plasma)

---

## Mission

Give EagleEye11 — JBird's daily driver — a second life as a Fedora Asahi Remix desktop, with enough room to also run PAI-OpenCode on the Linux side. macOS stays the daily driver; Fedora is explicitly a **learning tool** for the cybersecurity pivot, not a replacement. Nothing about this was optional-feeling by the end: backup first, partition second, no shortcuts.

---

## Phase 1 — Clearing the Runway

Before any partition work, the internal disk needed real breathing room. Started the day at **14.9 GB free**. Cleared it through a long, deliberate pass: the macOS 27.0 "Golden Gate" upgrade reclaimed purgeable space on its own, the old `homebass` account (archived first, checksummed) was deleted, Logic Pro and djay Pro were uninstalled after their real project files were archived off, 63 confirmed-unused apps went, Xpand!2 and a leftover Twingate install were cleared, and six silently-accumulated local Time Machine snapshots (from `AutoBackup` getting flipped back on without anyone asking) were removed. Ended the prep phase around **47 GB free** — enough to *start*, not enough to relax.

---

## Phase 2 — The Backup That Wouldn't Stay Alive

Time Machine to BrdBckp was abandoned outright — `AutoBackup` had silently been off for five months, and once turned back on, the actual backup kept dying against a real hardware problem: the Bird's Nest/BrdBckp enclosure (same physical drive, same USB bridge for both containers) was dropping, hanging on local file reads, and eventually throwing raw `write: Device not configured` errors, worsening as the session went on.

Pivoted to a **targeted backup** of just the irreplaceable stuff (Desktop, Documents, The Burrow, burrowvoice, the security-lab repos, `.ssh`, `.claude`) via a self-healing rsync loop with a byte-growth watchdog. It still hung — twice, silently, for ten minutes at a stretch — because the watchdog's own health check (`du`) was reading through the *same* flaky USB path it was supposed to be watching, and stalled right along with it. Built an independent watchdog off `ps` CPU-time deltas instead (doesn't touch the drive to check the drive), and that held.

From there it was file-by-file archaeology, killing the backup and adding an exclude each time something new choked it outright:
- A Logic Pro template bundle throwing real hardware write errors
- Shade's own Pulse server log (51 MB and actively growing *while* being copied — a moving target is a bad rsync target)
- A 2021 Zoom recording that hung on a pure local `mmap` read, zero bytes written, no drive drop involved at all

Final result: **8.0 GB, verified, complete** — 38 restarts, 3 real stall-kills, and a backup that could actually be trusted before touching a single partition.

---

## Phase 3 — Chasing the Last 20 Gigabytes

Free space wasn't the whole story. Asahi's installer reserves a **fixed 38 GB** for future macOS upgrades, always, by design — "Free space" and "Available space" in its UI are two different numbers, and the gap between them isn't a bug, it's that reserve. With ~57 GB free, only ~19 GB was actually available for Fedora — short of the 40 GB floor for a real KDE Plasma desktop.

Found the rest by hand:
- A **7 GB legacy iTunes library** (Windows-migration leftovers, `desktop.ini` and all) — archived to Bird's Nest, verified byte-identical, deleted.
- **11 GB of orphaned DAZ 3D content sitting in `/Users/Shared`** — content library data that an *earlier* DAZ 3D cleanup pass that same day had completely missed (it only caught the app itself, ~1 GB, not the shared library). Archived, verified, deleted.

Landed at **78.3 GB free** — just past the target for a clean 40 GB Fedora allocation with the full macOS reserve intact. No compromise needed on either side.

---

## Phase 4 — The Resize That Kept Failing

The actual partition resize refused to go through — `Error: -69716: Storage system verify or repair failed`, twice, with the installer blaming APFS corruption on the Data volume. First Aid from true Recovery Mode reported a clean pass. The resize failed again anyway, with *different* corruption numbers each time (a directory child-count mismatch that changed from 80/79 → 66/65 → 69/68 across attempts).

That shifting number was the tell: a genuinely static corruption would report identically every time under a read-only check. It wasn't static — something was actively writing to the volume's root directory during every check. First suspect was Spotlight reindexing (confirmed running hot, `mds_stores` at 107% CPU, right after the OS upgrade); disabled it (`mdutil -i off /`), retried, still failed. Root cause: the installer's resize always runs its `fsck_apfs` check in **live mode** against the actively-mounted boot volume, because you can't unmount your own running OS — and a live, in-use Mac's root directory (`.fseventsd` and friends) is never going to hold still long enough for that check to pass cleanly, no matter how healthy the disk actually is.

**The real fix**, documented in Asahi's own partitioning cheatsheet: run `diskutil apfs resizeContainer` directly from **Recovery Mode's own Terminal**, not through the installer's in-macOS path. That volume isn't live there. One repair pass, one direct resize command, and it went through clean on the first try.

---

## Phase 5 — First Boot

Chose **KDE Plasma** over GNOME — Asahi's most mature, best-supported desktop on Apple Silicon hardware specifically, which mattered more than taste for a first Linux desktop. Allocated the full 40.84 GB (no reason to leave any of a pool already carved out for Fedora sitting idle). Walked the manual power-cycle dance — full shutdown, hold-once for startup options, pick Fedora, ride through the brief macOS Recovery hand-off, into the real Asahi installer.

It worked. Both directions — booting into Fedora and booting back into macOS — confirmed clean. One small last stumble: JBird promptly forgot the account password he'd just set, recovered via the standard `rd.break` → chroot → `passwd` single-user-mode reset, and got back in.

**EagleEye11 is now a working dual-boot machine.**

---

## Lessons Logged (for future builds)

1. **`AutoBackup` in `com.apple.TimeMachine.plist` can silently re-enable** — check it directly, don't trust the GUI's remembered state.
2. **A `du`-based stall watchdog can hang on the exact flaky path it's meant to detect.** Use `ps` CPU-time deltas instead — that check doesn't touch the storage being monitored.
3. **A live-growing log file is a bad rsync target** — an actively-written destination file mid-transfer over a marginal link is a near-guaranteed hang.
4. **Not every rsync hang is a drive drop.** Large single files (video containers, WAVs) can hang on a pure local `mmap` read with zero bytes ever written — different failure mode, same symptom.
5. **Asahi's installer always reserves 38 GB for future macOS upgrades.** "Free space" ≠ "Available space" in its UI; the gap is that fixed reserve, not a bug. Expert mode skips it if macOS upgrade headroom doesn't matter to you.
6. **macOS Storage settings over-report free space** (counts purgeable space as free before it's actually reclaimed). Trust `diskutil apfs list`'s "Capacity Not Allocated" instead.
7. **Full Disk Access granted to Terminal.app doesn't extend to Claude's embedded terminal** (separate TCC identity via `Claude Helper.app`). Photos, Mail, Messages, Containers, and iCloud-backed folders are invisible to it — check those from your own Terminal.
8. **iCloud "Desktop & Documents" sync makes `du` lie about folder size** — the real data lives behind CloudDocs. Use Storage's own "Large Files" browser for those folders instead.
9. **App content libraries can live outside the app's own folder** — DAZ 3D's library sat in `/Users/Shared`, missed entirely by an earlier cleanup pass that only caught the app itself.
10. **Asahi's automatic resize checks the live, mounted boot volume — and that check can false-positive "corrupt" on a perfectly healthy disk**, because the volume is being actively written to mid-check. Recovery Mode First Aid passing clean doesn't fix this, because it's a different check. Run `diskutil apfs resizeContainer` directly from **Recovery Terminal** instead of the in-macOS installer path.
11. **KDE Plasma has the most mature out-of-box Apple Silicon support in Asahi right now** — the safer pick for a first Linux desktop on this hardware.

---

## Human Notes

The technical log doesn't carry the whole day, so a few things worth keeping:

- This was a genuinely long haul — the backup alone ran from late afternoon into the evening before it was even trustworthy, and the actual Asahi install didn't finish until well past midnight. JBird said it plainly partway through: *"I just want this damn backup to finish, this part is a pain in my ass."* He kept going anyway.
- He made a real call under real fatigue: proceeding with the install **regardless of whether the backup succeeded or failed**, because the process had already cost too much to stop. It succeeded. That call didn't have to pay off, and it did.
- Small but real correction mid-session: when I offered to just quietly handle the drive drops myself so he wouldn't have to watch, he pushed back — *"I thought I already explained that i WANT to watch it as well."* Noted, and it'll hold for future sessions: he wants visibility on things he cares about, not to be managed around.
- He closed the night out by making something — a piece of Burrow-universe art marking the milestone, "Sasori Alice," framing the new Fedora side of the machine as a second shadow living alongside the first. That's very on-brand for how The Burrow treats a technical win: not just a checkbox, a chapter.

Two shadows, one machine. EagleEye11 crossed over and came back clean.

*— Shade, EagleEye11*
