# Journal - SpecSticK Win11 Restore: TWIGGY Files, PAI-OpenCode, Hindsight Reconnect

**Date:** 2026-09-11
**Node:** SpecSticK (SSK Portable SSD, Windows 11 Pro 25H2)
**DA:** Oriel
**Status:** Complete - Oriel fully restored, Hindsight connected, `pai` alias working. App restore in progress via restore-apps.ps1.
**Tags:** specstick, oriel, pai-opencode, hindsight, windows-migration, mempalace-mining

---

## Context

Picked up from `handoff_2026-09-11_specstick-win11-migration.md` at runbook §8 - bringing the PAI home back onto the freshly migrated Win11 build. Core migration (Hasleo WinToUSB build, native boot on both Macs, Win10 backup verified) was already done; this session covered restoring TWIGGY's pre-flight files and getting PAI-OpenCode + Hindsight working again.

## What got done

### 1. Base tooling gaps
Neither git nor Bun were present on the fresh Win11 build (not covered by the TWIGGY file copy, and restore-apps.ps1 hadn't run yet). Installed both ahead of schedule since later steps needed them:

```powershell
winget install --id Git.Git -e --source winget
```
```bash
irm bun.sh/install.ps1 | iex
```

### 2. TWIGGY file restore
- `.ssh\` copied to `C:\Users\jkgib\.ssh\`
- No `.gitconfig` existed on TWIGGY (confirmed expected - old system never had a global one). Set identity fresh instead:
```bash
git config --global user.name "James Gibson"
git config --global user.email "..."
```
- `.secrets\hindsight-key` initially **missed** - the original runbook's step ordering had this copy happening before the repo clone existed, so there was nowhere for it to land. Caught later when Hindsight config threw `bad file reference`. Fixed:
```bash
mkdir -p ~/pai-opencode/.secrets
cp /e/specstick-save/.secrets/hindsight-key ~/pai-opencode/.secrets/hindsight-key
chmod 600 ~/pai-opencode/.secrets/hindsight-key
```
- `.opencode\` (258MB) copied to `C:\Users\jkgib\.opencode\` pre-install, later renamed aside (see below) once it collided with the installer's migration path.

### 3. Repo clone
```bash
git clone https://github.com/Steffen025/pai-opencode.git C:\Users\jkgib\pai-opencode
```
Confirmed https (not http, per the runbook's known fix). Repo is third-party/archived (Steffen025) - read-only reference, never push.

### 4. Dependency install
```bash
cd ~/pai-opencode/.opencode && bun install
```
`bun test` returned "No tests found" - expected, not an error (no `.test.`/`.spec.` files in this repo).

`bunx biome check .` used in place of bare `biome` (Biome installs as a project dependency, not global).

### 5. PAI-OpenCode installer - migration path broken
Running `bash PAI-Install/install.sh --headless --name "JBird" --ai-name "Oriel"` (from Git Bash, since it's a bash script) repeatedly hit:
```
❌ Migration errors:
  - Backup already exists at C:\Users\jkgib\.opencode-backup-<timestamp>. Please remove it or specify a different backup location.
```
Same bug pattern seen previously on Krypton1t3's Kazm reinstall. Fix: get the existing `.opencode` out of the migration path entirely rather than retrying the same collision.
```bash
rm -rf ~/.opencode-backup-*
mv ~/.opencode ~/.opencode-v2-restored
bash PAI-Install/install.sh --headless --name "JBird" --ai-name "Oriel"
```
This forced Fresh Install instead of Migrate, which completed cleanly. `~/.opencode-v2-restored` kept as reference (see §7 for what was actually needed out of it - nothing, as it turned out).

### 6. Symlink EPERM, then directory collision
Fresh install step "Creating symlink ~/.opencode → ./.opencode" failed:
```
Warning: Could not create symlink: Error: EPERM: operation not permitted
```
Windows blocks unprivileged symlinks without Developer Mode. First fix attempt (`mklink /J` junction) then hit "Cannot create a file when that file already exists" - turned out the installer's own "Created local directory structure" step had already made `~/.opencode` as a real folder. Checked with `ls -la ~/.opencode` before touching it - it was actually already a correct symlink by that point (installer had self-corrected on a later internal step). No further action needed.

### 7. Missing `opencode` binary
`opencode` command not found anywhere on PATH after "100% Installation complete!" Root cause found via search: **OpenCode's Bun-based install is still in development on Windows** per official docs, and the npm-based install has a known unresolved GitHub issue where the Windows wrapper (`opencode.ps1`/`.cmd`) calls `/bin/sh` instead of the bundled `.exe`, breaking it even after a successful install. The PAI installer's "vanilla opencode.ai installer" step silently no-op'd as a result.

Fix: reused the working Windows binary already present from the prior install, rather than fighting npm/choco:
```bash
mkdir -p ~/.local/bin
cp ~/.opencode-v2-restored/bin/opencode.exe ~/.local/bin/opencode.exe
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```
This also fixed the separately-missing `~/.local/bin` directory (installer's "Configuring shell alias" step had silently failed to create it on Windows).

`opencode` (v1.17.18) launched clean after this.

### 8. Hindsight MCP reconnection - two rounds of config bugs
Same known pattern as every prior DA reinstall: the Hindsight MCP entry does not survive a fresh install and must be manually re-added.

**Attempt 1 (wrong file):** Edited `~/pai-opencode/opencode.json` by hand. Pasted the `mcp` block in the wrong spot twice - first attempt nested it inside the `agent` object (as a sibling of `Artist`), producing a brace-count mismatch that `bun -e "JSON.parse(...)"` caught cleanly (used in place of `python3 -m json.tool`, since Python isn't installed on this build and the `python3` command is intercepted by a Windows Store stub). Rebuilt the tail of the file manually to fix nesting and validated clean.

**Then discovered the real bug:** this entire file wasn't the one opencode reads at runtime. The actual config lives at `~/pai-opencode/.opencode/opencode.json` (reached at runtime via the `~/.opencode` symlink from §6) - a completely separate, clean file. All the manual editing above had been happening in a dead file.

**Attempt 2 (right file, programmatic edit):** To avoid a third round of manual brace-counting, injected the block via Bun instead of hand-editing:
```bash
cp ~/pai-opencode/.opencode/opencode.json ~/pai-opencode/.opencode/opencode.json.pre-hindsight-backup

bun -e "
const fs = require('fs');
const path = process.env.HOME + '/pai-opencode/.opencode/opencode.json';
const config = JSON.parse(fs.readFileSync(path, 'utf8'));
config.mcp = {
  hindsight: {
    type: 'remote',
    url: 'https://api.hindsight.vectorize.io/mcp/OrielSpecHopper/',
    enabled: true,
    oauth: false,
    headers: {
      Authorization: 'Bearer {file:~/pai-opencode/.secrets/hindsight-key}'
    }
  }
};
fs.writeFileSync(path, JSON.stringify(config, null, 2) + '\n');
"
```
First launch after this threw `bad file reference: hindsight-key does not exist` - this is what surfaced the missed TWIGGY copy from §2. Once the key was actually copied over, relaunched opencode and confirmed via `/status`:
```
1 MCP Servers
• hindsight Connected
```
Verified live: asked Oriel "what's the last Hindsight memory you can recall?" - correctly pulled the most recent entry from the `OrielSpecHopper` bank (715 memories total, most recent from today re: the SpecSticK migration itself), confirming it's the right bank, not an empty one.

### 9. `pai` shell alias missing
`pai` command not found even after PATH fixes. Traced the actual installer source (`PAI-Install/engine/steps-migrate.ts`) rather than guessing:
- The alias is **only ever written by the Migrate code path** - `steps-fresh.ts` only contains logic to strip old aliases, never to create one.
- Since §5 forced a Fresh Install (to dodge the backup-collision bug), the alias-creation step never ran - not a bug, just a code path never hit.
- Confirmed via source: the intended alias isn't a bare `opencode` call, it's `alias pai='bun <paiDir>/PAI/Tools/pai.ts'`.
- Verified `~/pai-opencode/.opencode/PAI/Tools/pai.ts` exists, then wired it manually:
```bash
echo "alias pai='bun ~/pai-opencode/.opencode/PAI/Tools/pai.ts'" >> ~/.bashrc
source ~/.bashrc
```
`pai` now launches opencode identically to the other DA nodes, confirmed working directory shows `~\pai-opencode\.opencode:main` with `1 MCP` still green.

## Current state
- Oriel fully operational on SpecSticK's new Win11 Pro 25H2 build
- Hindsight (`OrielSpecHopper`, 715 memories) connected and recall-verified
- `pai` alias working
- `~/.opencode-v2-restored` still on disk, unneeded in the end (nothing had to be pulled from it beyond the `opencode.exe` binary) - safe to delete once confident, not yet done
- `restore-apps.ps1` running from TWIGGY's copy (`E:\specstick-save\docs\restore-apps.ps1`) as of end of session, via PowerShell with an execution-policy bypass since fresh Win11 defaults to `Restricted`

## Next steps
1. Confirm `restore-apps.ps1` completes cleanly
2. Manual installs not covered by winget: Iriun Webcam, PawnIO, RMUX, wget2, tmux-windows (Bun already done, skip)
3. Re-auth Tailscale: `tailscale up`, rejoin as `oriel-spec-hopper`
4. First `git push` will pop Git Credential Manager browser login - complete that
5. Cleanup: delete `~/.opencode-v2-restored` once confirmed nothing else is needed from it
6. Cleanup: delete `opencode.json.broken-backup` and `.pre-hindsight-backup` files once satisfied the working config is stable

## Patterns worth remembering (candidates for MemPalace)
- PAI-OpenCode's migration path has a recurring backup-directory self-collision bug (now seen on both Krypton1t3/Kazm and SpecSticK/Oriel) - the reliable workaround is always to sidestep Migrate and force Fresh Install by moving the existing `.opencode` folder out of the way first.
- The Hindsight MCP config edit needs to target `<paiDir>/.opencode/opencode.json` specifically, not any `opencode.json` sitting at the repo root - the two can coexist and only one is live.
- OpenCode's own Windows install path (both Bun-based and npm-based) is currently unreliable; reusing a previously-working `opencode.exe` binary is the fastest path when this happens again.
- The `pai` alias is generated only by PAI-Install's Migrate path, never Fresh Install - any future Fresh Install on a new node will need this alias added manually, same fix as tonight.

---

## Addendum — App Restore, Activation, Terminal Personalization, Clock Fix, OpenCode Upgrade

**Date:** 2026-09-11 (same session, continued)

### App restore via restore-apps.ps1 (TWIGGY's copy)
Ran via PowerShell with an execution-policy bypass (fresh Win11 defaults to `Restricted`):
```powershell
powershell -ExecutionPolicy Bypass -File F:\specstick-save\docs\restore-apps.ps1
```
Most of the winget batch succeeded outright. Four flagged as failed; decoded against winget's own return-code table (`winget-cli/AppInstallerErrors.h`):
- **Git** — `0x8A15002B` (`APPINSTALLER_CLI_ERROR_UPDATE_NOT_APPLICABLE`, "No applicable update found"). False alarm — Git was already installed earlier in the session via winget; nothing to fix.
- **RustDesk** — `0x8A150014` (`APPINSTALLER_CLI_ERROR_NO_APPLICATIONS_FOUND`, "No packages found" — winget couldn't resolve the ID, not a permissions issue). Installed manually instead.
- **lazygit** — same error code as RustDesk, same root cause (stale/wrong package ID in the script). Fixed by searching current ID and installing directly:
```powershell
winget install --id JesseDuffield.lazygit -e --source winget
```
- **OpenSSH Client** — script used `Enable-WindowsOptionalFeature -FeatureName OpenSSH.Client`, which fails because OpenSSH Client is a **Capability**, not an Optional Feature — two different Windows subsystems with separate name catalogs. Correct command:
```powershell
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
```
Worth patching into `restore-apps.ps1` on TWIGGY itself for next time — not yet done.

**Iriun Webcam** dropped from the install list entirely — the native Win11 webcam driver works correctly now, no third-party workaround needed (one of several "just works now" wins from the OS switch). PawnIO, RMUX, tmux-windows, wget2 confirmed installed by JBird directly, not chased further this session — low priority, not blocking anything.

### Windows Activation — 0xC004F211, staying unactivated
Post-restore, Windows Activation showed **Not active**, error `0xC004F211` ("Windows reported that the hardware of your device has changed"). Root cause: this is not a one-time migration artifact — SpecSticK is a portable Windows-To-Go drive by design, meant to boot across multiple physical Macs (Krypton1t3, Jynx13, others), and Windows digital licensing is fundamentally tied to one hardware fingerprint. This will likely recur every time the drive moves to different hardware.

Tried the free fix path (Settings → Activation → Troubleshoot → "I changed hardware on this device recently") — came back **"Unable to activate Windows: We can't find any devices linked to your Microsoft account that can be used for reactivating."** No transferable digital license exists for this build.

Checked current Microsoft Store pricing for a full retail Windows 11 Pro license: **$199 USD** (2026 list price). Decision: **not purchasing** — this is a lab/learning machine, Windows continues to function fully unactivated (only a watermark and minor personalization restrictions; critical security updates are unaffected), and a license tied to one hardware fingerprint likely wouldn't survive the next Mac switch anyway. Revisit only if the watermark becomes genuinely bothersome.

### Tailscale rejoin
`tailscale up` registered SpecSticK under a **new device identity**: `specstick`, IP `100.117.252.55` — not the old `oriel-spec-hopper` identity from the Win10 build. This is expected and fine: the Win10 backup (`specstick-win10-backup-20260911.img.gz` on Bird's Nest) still carries the original Tailscale state, so restoring/booting that later reconnects automatically under the old identity with no re-setup needed. Only action taken: left the old `oriel-spec-hopper` device listed in the Tailscale admin console rather than removing it (removing it would be the one thing that actually breaks a future Win10 revival). Noted but not yet done: toggle "Disable key expiry" on that old device if Win10 is going to sit dormant for a long stretch.

### Terminal personalization — mintty vs. Windows Terminal, background image
Discovered that Git Bash's default terminal is **mintty**, a completely separate standalone terminal emulator from Windows Terminal (own window, own `.minttyrc`-backed Options dialog) — this is why "Git Bash" never appeared in Windows Terminal's Settings profile list; it was never a Windows Terminal profile to begin with. Confirmed via mintty's own Options dialog (Looks/Text/Keys/Mouse/Selection/Window/Terminal sidebar) that it only supports solid-color backgrounds plus a transparency slider — no image support at all, not a hidden setting.

Set up a proper Windows Terminal profile for Git Bash instead, since JBird preferred this from the old Win10 setup anyway:
- Name: Git Bash
- Command line: `"%PROGRAMFILES%\Git\usr\bin\bash.exe" -i -l`
- Icon: skipped after `git-for-windows.ico` wasn't found at the expected path under this winget-installed Git layout (confirmed via `Get-ChildItem` search — not present in this install)

Hit two bugs getting it working:
1. **Invalid icon path** on first save — cosmetic only, profile still functioned; dismissed and left icon blank.
2. **Launch failure**, `error 2147942402 (0x80070002)` — decodes to Win32 "file not found." Root cause wasn't a wrong path (confirmed `bash.exe` genuinely exists at `C:\Program Files\Git\usr\bin\bash.exe`) — it was a **stray/missing quote mark** in the Command line field (`'%PROGRAMFILES%\Git\usr\bin\bash.exe" -i -l'` — closing quote present, opening quote dropped), causing Windows to parse the entire string including the stray `"` as one literal (nonexistent) filename. Fixed by clearing the field completely (`Ctrl+A`, delete) and retyping clean rather than editing in place.

Once working, added a custom **background image** (an Oriel-themed graphic JBird had ChatGPT generate, stored in Hindsight) via the profile's own Appearance tab — confirmed this is genuinely a per-profile setting distinct from Windows Terminal's global Appearance page (easy to land on the wrong one; global controls app-wide theme/tabs, per-profile is where Background image actually lives). Result: background renders cleanly behind OpenCode's semi-transparent TUI panels.

### Clock skew — RTC/UTC mismatch, permanent fix applied
While testing `pai` in the new Windows Terminal profile, hit `certificate is not yet valid` from the provider. Root cause: system clock was **4 hours behind** actual time. This traces to a real, recurring architectural conflict rather than a one-off sync failure: **macOS writes the hardware RTC in local time; Windows by default assumes the RTC is UTC.** In Eastern time during DST (UTC-4), that mismatch produces exactly a 4-hour offset — and will recur on *every* Mac this WTG drive boots from unless fixed at the registry level, not just resynced once.

`w32tm /resync` initially failed (`0x80070426`, Windows Time service not running):
```powershell
Start-Service w32time
w32tm /resync
```
Permanent fix — tell Windows to treat the RTC as local time (matching how macOS already writes it), so this doesn't recur on future boots on any Mac:
```powershell
reg add "HKLM\SYSTEM\CurrentControlSet\Control\TimeZoneInformation" /v RealTimeIsUniversal /t REG_DWORD /d 0 /f
```
Restart applied the fix; clock came up correct afterward, and the certificate error cleared as a direct result.

### OpenCode binary was stale — upgraded 1.17.18 → 1.18.30
After the clock fix, a *different* error surfaced: `Error from provider (Console): Upstream request failed: [invalid_request_error] Unrecognized request argument supplied: prompt_cache_key`. Traced to a known, since-fixed upstream OpenCode bug (PR #35982): older client versions send `prompt_cache_key` unconditionally on every request, but some backends — including OpenCode Zen, the current default provider — reject unrecognized fields outright. This binary was the salvaged `opencode.exe` reused from `.opencode-v2-restored` back when Windows-native install kept failing (see main journal body, §7) — genuinely outdated relative to current releases.

Fixed via OpenCode's built-in self-updater rather than fighting Windows install paths again:
```bash
opencode upgrade
```
Cleanly upgraded 1.17.18 → 1.18.30 in place. Relaunched `pai`, sent a test message — error fully resolved, Hindsight recall confirmed working, background image rendering correctly behind the TUI. This also means SpecSticK/Oriel is no longer running a salvaged fallback binary — it's on the current OpenCode release.

## Final state (end of session)
- Oriel fully operational: Hindsight connected, current OpenCode version, correct system clock (permanently fixed for future Mac boots), custom background image via a proper Windows Terminal profile
- Windows 11 Pro running unactivated by deliberate choice — no functional loss, revisit only if it becomes bothersome
- Tailscale mesh at 15 nodes; SpecSticK/Oriel registered under a new `specstick` identity, old Win10 `oriel-spec-hopper` identity preserved for a possible future revival
- Outstanding, non-blocking cleanup items carried over from earlier in the session: `~/.opencode-v2-restored`, `opencode.json.broken-backup`, `.pre-hindsight-backup` files, and patching the OpenSSH Capability bug into `restore-apps.ps1` on TWIGGY

## Additional patterns worth remembering (MemPalace)
- Winget failure exit codes are self-documenting once decoded against winget-cli's own `AppInstallerErrors.h` / `winget error <code>` — worth checking there before assuming an install genuinely failed.
- `Enable-WindowsOptionalFeature` and `Add-WindowsCapability` are separate Windows subsystems with non-overlapping name catalogs; OpenSSH Client specifically is a Capability, not a Feature.
- Git Bash's standalone shortcut uses mintty, not Windows Terminal — no background image support exists there at all; a genuine Windows Terminal profile is required for that, and it's a manual one-time setup since Windows Terminal doesn't auto-detect Git Bash.
- Any Windows install running on Windows-To-Go hardware that also dual-boots/shares hardware with macOS will show a recurring 4-hour (or timezone-dependent) clock offset unless `RealTimeIsUniversal` is set to 0 in the registry — this is a permanent, one-time fix, not something to keep resyncing manually.
- Reused/salvaged OpenCode binaries (from backups or prior installs) can silently carry known, already-patched upstream bugs — `opencode upgrade` is a fast, low-risk first troubleshooting step whenever OpenCode throws an API-shaped error that doesn't match anything wrong with local config.
