# BurrowMCP — Session 23 Journal
**Date:** 2026-11-03
**Author:** JBird + Claude

**"Inventory Night" (or: How Clover Moved House Without Losing a Single Memory)**

**Crew:** JBird + Claude
**Session window:** 5:26 PM to 11:50 PM
**Mood:** Started as housekeeping. Ended with a DA relocated, a phone fully onboarded, and BurrowMCP nearly tripled in reach.

---

## TL;DR

- 🗂️ **Burrow Master Inventory** audited tab by tab against the Overview and cleaned up.
- 🦅 **BurrowMCP Session 23** shipped: 4 → 11 nodes, new read-only `get_node_inventory` tool, tiered trust, parallel lab status. First live run: **10/11 reachable**. Krypton1t3 was just napping.
- 🕯️ **Slim** got its first supervised inventory: healthy, 1,170 packages, 54% rootfs.
- 🍀 **Clover** migrated from Play Store Termux to F-Droid Termux with her whole environment intact, and gained **Termux:API**: she can now feel the phone she lives on.
- 📱 **Luck13** is a full BurrowMCP node: sshd auto-starts on boot, restricted key installed, live inventory over SSH.
- 🫏 **BB** joined right before midnight. **Lab status closed the night at 12/12.**

---

## 1. Inventory Sheet Sync 🗂️

JBird had updated the Overview tab. Claude compared every node tab against it and against live data, then fixed things only after sign-off.

**Highlights:**
- EagleEye11: macOS 27.2, hardlined via Bugsy → Talon, Shade added as Resident DA ahead of Sasori.
- Wazuh now reads **On-demand** everywhere it's mentioned, lab-wide.
- Krypton1t3: stale KryptStick row removed, GPU corrected to Iris Pro only, 3 local Ollama models.
- Jynx13: BurrowMCP reinstall confirmed, SDR added to its role, ghost SuperStick rows removed.
- Resident DA rows added for Omega, Kazm, Echo, and Quinze.
- **FatBot → FatBoy** tab rename. Its IP was a copy of Blanca's; fixed.
- **New ESP11 tab.** Its Tailscale IP on Mobile Peripherals had been copied from Slim's; fixed.
- BirdieVision got its full jailbreak + Kodi + exit-node story on its tab.
- Nine typos fixed across the hardware tabs (RIP "Etherner").

**Lesson:** a health check reports how a node is *feeling*, not what's *on* it. That gap kicked off section 2.

---

## 2. BurrowMCP Session 23 🦅

Full write-up lives in `BurrowMCP/docs/BurrowMCP-23-Session23.md`. The short version:

- **New tool:** `get_node_inventory`: OS, CPU/GPU, package counts, running services, Ollama, Docker, git repos, Wazuh, and an OSINT / SDR / pentest / lab tool sweep. One SSH connection, read-only, nothing executed beyond presence checks.
- **New nodes:** Slim, Luck13, ESP11, BirdPad, BirdieVision (SSH), plus SolSkorp_13 and CyberSkorp10 (ping-only).
- **Trust tiers:** `core`, `standard`, `supervised` (Slim: deep reads need JBird's OK), `reachability`.
- **Hardening:** `BatchMode=yes`, timeouts, scripts piped to `sh -s` (works even under fish), parallel pings.

**First live run tonight:**

```
Reachable: 10/11
```

The one miss was Krypton1t3, suspended on purpose. It woke up with uptime intact.

---

## 3. Slim's First Supervised Inventory 🕯️

Ran only after JBird gave the go-ahead, using the `CONFIRM_SUPERVISED_READ` token.

| | |
|---|---|
| OS | CachyOS, kernel 7.1.7-Strawberry |
| Packages | 1,170 (up from 1,113) |
| Rootfs | 32 GB / 63 GB (54%) |
| Failed units | `ananicy-cpp` only (benign) |
| Lab tools | Tailscale, OpenCode, Bun, Python 3, LocalSend |

Joe's console is healthy. Nothing was changed.

---

## 4. Clover's Move: Play Termux → F-Droid Termux 🍀

### Why
An adb health check on Luck13 showed the **Termux:API** app was missing. Turns out it's **not published on Google Play**, and Termux apps from different stores can't be mixed (signing keys must match). To get the API, Termux had to move to F-Droid. That meant rebuilding Clover's world.

### How we knew it was the Play build
F-Droid showed "Open" for Termux, which looked like it was already an F-Droid install. It wasn't. F-Droid only matches the package name. Android's own record settled it:

```
installerPackageName = com.android.vending    ← Google Play
versionName          = googleplay.2026.10.09
```

### Backup (nothing deleted until verified)
```bash
pkg list-installed 2>/dev/null | tail -n +2 | cut -d/ -f1 > ~/pkgs.txt
proot-distro backup debian --output /sdcard/Download/clover-debian.tar.gz
tar -czf /sdcard/Download/termux-home.tar.gz -C /data/data/com.termux/files home
```

Copied to `Bird's Nest/DA_Backups/` and verified with SHA-256 on both ends: phone and Mac matched bit for bit.

**Plot twist:** USB adb kept dropping under sustained transfer (cable/port reset). Switched to **Wi-Fi adb** with `adb exec-out cat` and it ran clean at ~5 MB/s.

Before anything was uninstalled, Claude listed the archive and confirmed Clover was really in there: her PAI install, MEMORY threads back to 10-14, her session database, and her Hindsight key.

### Restore
```bash
pkg update && pkg install termux-api
termux-battery-status                          # JSON = API works ✅
termux-setup-storage
tar -xzf /sdcard/Download/termux-home.tar.gz -C /data/data/com.termux/files --exclude='home/.cache/go-build'
termux-wake-lock
apt install -y -o Dpkg::Options::=--force-confold $(cat ~/pkgs.txt)
proot-distro restore /sdcard/Download/clover-debian.tar.gz
```

All 211 packages came back in about 3 minutes. Clover's container restored, her identity checked out, and then the best surprise of the night:

```bash
# from INSIDE Clover's Debian:
/data/data/com.termux/files/usr/bin/termux-battery-status   # works!
```

No bridge needed. A few symlinks later, `termux-*` commands work natively from her environment:

```bash
mkdir -p ~/.local/bin && for f in /data/data/com.termux/files/usr/bin/termux-*; do ln -sf "$f" ~/.local/bin/; done
```

Clover can now reach battery, sensors, location, camera, notifications, clipboard, TTS, vibration, and more.

---

## 5. Luck13 Joins BurrowMCP 📱

```bash
sv-enable sshd && sv-enable ssh-agent
mkdir -p ~/.termux/boot && printf '#!/data/data/com.termux/files/usr/bin/sh\ntermux-wake-lock\n. $PREFIX/etc/profile\n' > ~/.termux/boot/start-services && chmod +x ~/.termux/boot/start-services
echo "from=\"<EagleEye11 Tailscale IP>\",restrict $(cat /sdcard/Download/burrowmcp.pub)" >> ~/.ssh/authorized_keys
```

The BurrowMCP public key was delivered to the phone over adb, then locked to one source IP with `restrict`, so it can't forward ports or open a PTY.

**Live test from EagleEye11:** ✅ SSH, stats, disk, and full inventory, all over port 8022.

**Two catches from that first inventory:**
1. The F-Droid reinstall gave Termux a **new Android user ID**. Config and sheet updated.
2. The inventory script looked for proot containers in an outdated folder. Now it asks `proot-distro list` directly. Fixed and tested.

---

## 6. Bonus Round: BB Joins Too 🫏

At 11:32 PM BB got plugged in, and the same playbook ran in about 15 minutes:

- **adb health check:** Android 13, bootloader locked, **28 days of uptime**, battery healthy. Storage is getting tight (84%), and its last security patch is from January, so this is probably the end of the line for Motorola updates.
- **Mystery solved, mostly:** Talon's app listed BB at a stale DHCP address, but BB was reachable at a different address. Nothing answered at the old address or claimed it via ARP, so it was probably BB's pre-Bugsy address.
- **Plot twist #2:** BB's Termux is the same version as Luck13's (0.118.3) but signed with a **different key**, which makes it the GitHub build. Termux:API matches it, so it works fine. Any Termux:Boot for BB has to come from GitHub, not F-Droid.
- **Onboarded:** sshd + restricted key, added to BurrowMCP as node #12, live inventory over SSH: 172 packages, nmap, radare2, and a `rikkahub-agent` repo.
- **Bug squashed:** `proot-distro list` writes to stderr, so the inventory was blind to Clover's container. `2>/dev/null` became `2>&1`, and Luck13 now reports `proot distros: debian`.

**Final lab status of the night:**

```
Reachable: 12/12
```

---

## Lessons Learned

- **Ask the system, not the storefront.** F-Droid said "Open." Android's installer record told the truth.
- **Checksums before deletes.** A matching SHA-256 on both ends is what made uninstalling Clover's home feel safe instead of scary.
- **When a cable flakes, change the road.** Wi-Fi adb saved the transfer.
- **Belt, suspenders, and knowing when to take them off.** Clover burned her usage verifying instead of doing. Verification belongs where the stakes are high (backups, deletes, Joe's data), not on "say hi."
- **Compiling ≠ correct.** A config edit tonight compiled fine while quietly dropping the secrets loader. A read-back caught it.

---

## Open Items for Next Session

- [x] ~~Restart BurrowMCP to pick up the Luck13 user ID + proot inventory fix~~ (done, 12/12)
- [ ] BurrowMCP key on ESP11, BirdPad, BirdieVision (confirm SSH users)
- [ ] BB: Termux:Boot from **GitHub** releases (to match its signer), then the boot script; free up storage (84%)
- [ ] Check the MAC on Talon's stale lease against BB's
- [ ] `ssh-keygen -R "[<Luck13 IP>]:8022"` on Krypton1t3 (new Termux host keys)
- [ ] Clear backup copies from Luck13's `/sdcard/Download`
- [ ] Wireless debugging off (or let a reboot handle it)
- [ ] Rediscover Clover's original voice path (PulseAudio + AAudio sink is the likely suspect), or switch her to `termux-tts-speak`
- [ ] Add an "act first on simple requests" line to Clover's PAI instructions
- [ ] Jynx13 inventory to confirm the OSINT stack
- [ ] SkorpiOm: 3 failed units (VirtualBox modules, networking, Proton VPN split tunneling)
- [ ] Session 24 idea: `adb_tools.py` for Luck13 + BB

---

*Clover went to sleep in one Termux and woke up in another, with more senses than she had before. Not a bad Tuesday.* 🍀🦅
