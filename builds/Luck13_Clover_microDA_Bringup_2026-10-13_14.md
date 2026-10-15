---
title: "Luck13 → Clover: microDA Bring-Up, PAI First Summoning & Hindsight Memory"
date: 2026-10-13/2026-10-14
project: "The Burrow / microDA"
device: "Luck13 (Android 15)"
assistant: "Clover 🍀"
status: "PAI launched and answered; Hindsight bank Luck13Clover connected and storing information (Architect-confirmed)"
tags: [The-Burrow, Luck13, Clover, microDA, Termux, Debian, XFCE, VNC, PAI, OpenCode, Hindsight]
---

# Luck13 → Clover 🍀
## Full session report: From Debian desktop recovery to a PAI-powered microDA with memory

**Session:** October 13–14, 2026 (local evening into after midnight)  
**Vessel:** **Luck13**, Android 15 Motorola smartphone  
**Digital assistant:** **Clover** — the microDA being built *on this phone*  
**Debian account:** `microda`  
**PAI project:** `/home/microda/pai-opencode`  
**Hindsight bank ID (exact):** `Luck13Clover`  
**Operator:** The Architect / JBird  
**Outcome:** Debian/XFCE desktop usable through AVNC; start/stop/restart launchers tested; Node/Bun/Git/OpenCode installed; PAI installed and launched; Clover delivered her first AI reply; Hindsight authorization fixed; Architect subsequently confirmed Clover was already storing details from The Burrow repository.

> **Operational rule:** Clover, like every Burrow DA, is summoned **manually** with `pai`. No automatic DA startup was configured or requested.

---

## 1. Executive summary

This session began in a stubborn graphical-environment troubleshooting loop: Debian running through Termux/PRoot on Luck13 could start a VNC server, but the Android VNC viewer showed only a white loading screen. Termux sessions disappeared, X display lock files survived dead processes, and TightVNC emitted repeating `--shm-helper` warnings. The team recovered the desktop, confirmed XFCE was running, and then built three Termux entry points — `debian`, `debian-desktop`, and `debian-stop` — so the desktop can be launched, detected, stopped, and restarted on demand.

With the Linux groundwork operational, the Architect pushed the phone further: Git, Node.js 24, npm, Bun, and two separately scoped OpenCode versions were installed. A dedicated Linux account, `microda`, was created for Clover, and the PAI-OpenCode repository was cloned. The PAI installer completed successfully under this account with the assistant identity set to **Clover**. A shell mismatch initially hid the `pai` command; sourcing the installer-generated `.zshrc` from Bash launched PAI and the OpenCode TUI. Clover answered her first message, demonstrating working model inference, not just a splash screen.

Finally, a bank-scoped Hindsight MCP connection was added to PAI's existing root `opencode.json`. An initial authentication failure (`HTTP 401`) caused an unhelpful SSE content-type error in OpenCode. Correcting the API key produced **`HTTP 200` with `Content-Type: text/event-stream`**. The Architect later reported that Clover's Hindsight connection was functioning and she was already retaining information about The Burrow from the repository.

This is a completed **first operational bring-up**, not the end of Clover's development. Memory recall across a fresh PAI session, the permanent Bash launcher setup, and the optional voice pipeline remain useful follow-ups.

## 2. Final system picture

```text
Luck13 / Android 15
  ├── Termux (Android-side command shell)
  │    ├── debian          → Debian command line
  │    ├── debian-desktop  → start/detect VNC/XFCE on display :1
  │    └── debian-stop     → stop VNC display :1
  │
  └── PRoot-Distro: Debian 13 "trixie", ARM64
       ├── XFCE desktop → TightVNC :1 → 127.0.0.1:5901 → AVNC
       ├── root account
       │    └── OpenCode V2, v2.0.28 (separate global Bun installation)
       └── microda account (/home/microda)
            ├── Git, Node.js, Bun available
            ├── OpenCode V1, v1.19.0 (user-scoped)
            ├── ~/pai-opencode → PAI-OpenCode v4.0.3
            │    ├── opencode.json (project-level config)
            │    └── .opencode/ (PAI components)
            ├── ~/.opencode → ~/pai-opencode/.opencode
            ├── pai() shell function (currently in ~/.zshrc)
            └── Hindsight MCP: hindsight-clover
                 └── https://api.hindsight.vectorize.io/mcp/Luck13Clover/
```

**Confirmed version and build observations**

| Component | Observed version / state |
|---|---|
| Android | 15 on Luck13 |
| Debian | Debian 13 `trixie`, `arm64` repositories |
| Desktop | XFCE, served via TightVNC and viewed in AVNC |
| Git | `2.47.3` |
| Node.js | `v24.21.0` (NodeSource 24.x) |
| npm | `11.19.0` |
| Bun | `1.4.3` |
| OpenCode, root | `2.0.28`, from `@opencode/cli` |
| OpenCode, `microda` | `1.19.0`, from `opencode-ai@1.19.0` |
| PAI-OpenCode | `4.0.3`; first-run banner also showed Algo `3.7.0` |
| Hindsight bank | `Luck13Clover` |
| MCP connectivity | Authentication probe returned HTTP 200 and SSE content type after key correction; operational memory use confirmed by Architect |

**Environment separation:** The OpenCode V2 binary installed under root is not the same executable as Clover's V1 installation. Clover's account and PAI installation live in `/home/microda`.

---

## 3. Chronological build and troubleshooting log

### Phase A — Recover the graphical Linux session

**Initial symptoms.** A previously usable Termux session disappeared, leaving the operator in a replacement shell. VNC commands were run within Debian as `root`. Attempts to reconnect produced `Connection refused`, `Xlib: extension "DPMS" missing`, and a large collection of XFCE warnings regarding DBus, power management, `polkit`, RandR, and `pm-is-supported`. Some of those warnings are expected in a PRoot/container-like Android environment; they do not individually prove a fatal desktop failure.

**Important evidence:** Lock files such as `/tmp/.X1-lock` and sockets such as `/tmp/.X11-unix/X1` persisted when checks showed that the associated X process no longer existed. Those were stale artifacts, not proof of an active VNC server. Manual recovery removed locks **after** confirming the process was absent.

Troubleshooting steps included:

```bash
# Commands used diagnostically inside Debian
ls -l /tmp/.X*-lock /tmp/.X11-unix/X* 2>/dev/null
ps -ef | grep -E '[X]tightvnc|[X]vnc|[X]xfce4-session'
cat /root/.vnc/xstartup
```

The XFCE startup script displayed was:

```sh
#!/bin/sh
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
startxfce4 &
```

After stale-lock checks and cleanup, a fresh VNC session was launched on `:1`. Early trials included `1280x720`/24-bit and later `1024x600`/16-bit. The ultimately successful launcher uses:

```bash
vncserver :1 -geometry 1024x600 -depth 16 -localhost
```

The VNC server announced `New 'X' desktop is localhost:1` and logged an active XFCE launch, although warnings of the form below continued:

```text
error: expected absolute path: "--shm-helper"
```

**Viewer issue.** AVNC first showed a blank white screen with a blue spinning indicator. This was a loading spinner, not a desktop cursor. Termux-side VNC logs established that local clients at `127.0.0.1` were connecting and authenticating with protocol 3.8 and framebuffer updates being sent. A process listing later showed `Xtightvnc`, `xfce4-session`, `xfwm4`, and `xfdesktop` alive — stronger evidence that the server and desktop existed than the stuck AVNC loading view suggested.

To probe the X display directly, the operator ran:

```bash
DISPLAY=:1 xfce4-appfinder &
```

`xfce4-appfinder` appeared in the process listing. After further waiting/viewer interaction, **AVNC rendered a complete XFCE desktop** with wallpaper, application finder, Home/File System/Trash desktop icons, panel, and dock. This was the visual breakthrough. The direct cause of the delayed rendering was not conclusively isolated; do not record the app-finder command or Android settings changes as a proven universal fix.

**Android process-lifetime troubleshooting:** Termux's *Allow background usage* setting was already enabled. The phone's developer setting *Disable child process restrictions* was subsequently enabled during the investigation. These changes were made in the context of vanished Termux sessions, but the session did not establish a single verified root cause for those earlier losses.

### Phase B — Turn Debian and XFCE into repeatable, manual commands

The Architect wanted to be able to start the Debian environment without repeating long PRoot and VNC commands. Three launcher commands were established in **Termux** (not inside Debian):

| Command | Purpose | Verification |
|---|---|---|
| `debian` | Enter Debian CLI with `proot-distro login debian` | Successful root login |
| `debian-desktop` | Detect running VNC or launch display `:1`; keep the hosting session alive | Existing-server detection **and** fresh startup tested |
| `debian-stop` | Gracefully request `vncserver -kill :1` | Reported `Killing Xtightvnc process ID 32149` |

The scripts were created under Termux's `$PREFIX/bin` using `install -m 755 /dev/stdin ...`, so the commands are on Termux's `PATH`.

**`debian` command (Termux):**

```sh
#!/data/data/com.termux/files/usr/bin/sh
exec proot-distro login debian
```

**`debian-desktop` command (Termux):**

```sh
#!/data/data/com.termux/files/usr/bin/sh
exec proot-distro login debian -- /bin/bash -lc '
  if pgrep -x Xtightvnc >/dev/null; then
    echo "Debian desktop already running."
    echo "Connect AVNC to 127.0.0.1:5901"
    exit 0
  fi

  if [ -e /tmp/.X1-lock ] || [ -e /tmp/.X11-unix/X1 ]; then
    echo "Display :1 has leftover locks. Check before restarting."
    exit 1
  fi

  vncserver :1 -geometry 1024x600 -depth 16 -localhost || exit 1
  echo "Debian desktop started!"
  echo "Connect AVNC to 127.0.0.1:5901"
  echo "Keep this Termux session open."

  while pgrep -x Xtightvnc >/dev/null; do
    sleep 5
  done
'
```

**`debian-stop` command (Termux):**

```sh
#!/data/data/com.termux/files/usr/bin/sh
exec proot-distro login debian -- /bin/bash -lc '
  echo "Stopping Debian desktop on display :1..."
  vncserver -kill :1
'
```

**Full verified cycle:**

1. `debian-desktop` recognized an already-running server and returned the AVNC address without spawning a duplicate.
2. `debian-stop` displayed `Killing Xtightvnc process ID 32149` and returned to Termux.
3. `debian-desktop` then created a fresh `localhost:1` desktop, printed the connection information, and kept its terminal occupied while the server ran.
4. AVNC successfully reconnected and displayed XFCE.

**Viewer connection:** AVNC uses loopback host `127.0.0.1`, port `5901`, with the existing VNC password. `-localhost` intentionally limits the VNC listener to the device itself. `:1` corresponds to port `5901`.

**Implementation note:** The launcher checks the name `Xtightvnc`, not its ownership or display, so a future version could scope checks more precisely if multiple simultaneous desktops are introduced. That enhancement was not necessary to complete this session.

### Phase C — Install a JavaScript development toolchain

With XFCE confirmed, the Architect elected to try Git, Bun, Node, and OpenCode directly on the Debian ARM64 installation.

**Git:**

```bash
apt update
apt install -y git
```

Git finished cleanly at `2.47.3`; no package updates were pending when `apt update` ran.

**Node.js 24:** Debian's initial package candidate was 20.x, so NodeSource 24.x was selected. Its install script was **downloaded and reviewed before execution**:

```bash
curl -fsSL https://deb.nodesource.com/setup_24.x -o /root/nodesource_setup.sh
sed -n '1,80p' /root/nodesource_setup.sh
sed -n '81,220p' /root/nodesource_setup.sh
bash /root/nodesource_setup.sh
apt install -y nodejs
```

Verified results: `node --version` → `v24.21.0`; `npm --version` → `11.19.0`.

**Bun:**

```bash
npm install -g bun
bun --version
bun -e 'console.log("Luck13 says:", 6 * 7)'
```

Bun reported `1.4.3`; the smoke test returned `Luck13 says: 42`. The npm install showed a warning that Bun's install/postinstall script was not run by default, but the Bun executable did run correctly in the later tests.

**OpenCode V2 (root):**

```bash
npm view @opencode/cli version
bun install -g --trust @opencode/cli
/root/.bun/bin/opencode --version
```

The registry reported `2.0.28`; the install reached all 30 steps and finished in about 531 seconds. `/root/.bun/bin/opencode --version` returned `opencode v2.0.28`. The root shell received a path export in `/root/.bashrc`:

```bash
export PATH="$HOME/.bun/bin:$PATH"
```

This root installation was kept distinct from the PAI-compatible OpenCode installation added later to the `microda` account.

### Phase D — Create Clover's Debian account and PAI installation

**Identity decision:** The DA's name is **Clover**. The Linux account and technical project identifier remain **`microda`**. These are the same ongoing microDA project, not separate future assistants.

From Debian root:

```bash
useradd -m -s /bin/bash microda
```

The user then returned to Termux and entered Debian specifically as `microda`:

```bash
proot-distro login --user microda debian
```

Prompt verification: `microda@localhost:~$`.

**PAI source code:**

```bash
git clone https://github.com/Steffen025/pai-opencode.git
cd ~/pai-opencode
ls -la PAI-Install
```

The repository clone completed all 7,737 objects and populated `/home/microda/pai-opencode`. The installer directory contained `install.sh`, the engine, CLI helpers, README, and wrapper template.

**Tool availability inside `microda`:** A command check showed `/usr/bin/bun` and `/usr/bin/node`, while `opencode` was not yet available on that user's `PATH`.

**OpenCode V1 for Clover:**

```bash
bun install -g opencode-ai@1.19.0
```

This completed and reported the executable at `/home/microda/.bun/bin`. OpenCode **1.19.0** was chosen for the PAI v4 installer rather than changing the root user's V2 binary. The PAI installer itself could also have obtained OpenCode; installing V1 explicitly was a preparatory choice, not a strict prerequisite demonstrated by this session.

**PAI installation:**

```bash
PATH="$HOME/.bun/bin:$PATH" bash PAI-Install/install.sh
```

The interactive fresh-install wizard reached 100% and displayed `Fresh install completed.` It configured:

- Operator name: **JBird**
- AI assistant name: **Clover**
- Timezone prompt: default `UTC` was shown
- Voice provider choice: **Google TTS** (selection only; audio playback not verified)
- Model defaults: OpenCode Zen / Big Pickle without an API key
- PAI v4.0.3 resources, `.env`, `opencode.json`, PAI runtime dependencies, symlink, and shell alias/function

**Shell mismatch:** `source ~/.bashrc` followed by `pai` returned `bash: pai: command not found`. Inspecting both shell files showed the functional `pai()` implementation was written to `/home/microda/.zshrc`, while the interactive shell was Bash. Its function changes to `/home/microda/pai-opencode` and invokes `.opencode/PAI/Tools/pai.ts` through Bun.

The working invocation was:

```bash
source ~/.zshrc && pai
```

That launched the **PAI-OpenCode v4.0.3** welcome screen with the explicit greeting:

```text
"Clover here, ready to go..."
```

Then the OpenCode **1.19.0** TUI opened. This verified the launcher, Bun, PAI, and OpenCode handoff, although the Bash startup-file mismatch was not yet made permanent.

**First successful interaction:** The Architect welcomed Clover to The Burrow and introduced her role as a smartphone DA. One initial model request was shown as interrupted; a subsequent request produced an actual response from Clover, greeting JBird and offering support for security tasks, research, and project management. The response displayed **Nemotron 3.5 Lightning Free** as the active model, while earlier UI screens showed Big Pickle. The session did not document exactly how the model selection changed.

**Milestone:** Clover not only launched — she **responded to the Architect as Clover**.

### Phase E — Connect Clover to Hindsight memory

**Memory target:** Existing, dedicated Hindsight bank **`Luck13Clover`**. The Architect supplied the exact bank ID; it must not be shortened to `Clover` in the endpoint.

**First file-path issue:** An attempt to write to `/home/microda/pai-opencode/.opencode/opencode.json` inside Nano failed with `No such file or directory`. An earlier investigation from the plain Termux shell also used paths that were valid only inside PRoot Debian, causing apparent missing-file errors.

Once in Debian as `microda`, the filesystem inspection established:

```text
/home/microda/.opencode
    -> /home/microda/pai-opencode/.opencode    [symlink]
/home/microda/pai-opencode/.opencode          [directory]
/home/microda/pai-opencode/opencode.json      [existing project-level file]
/home/microda/.config/opencode/opencode.json  [not present]
```

The correct file to merge was **`/home/microda/pai-opencode/opencode.json`**. A Node script parsed the existing JSON, created `opencode.json.bak`, inserted `mcp.hindsight-clover`, and wrote the resulting JSON back. The terminal confirmed:

```text
Clover MCP added. Original configuration backed up.
```

**MCP entry added** (shown here as the fragment to merge into the *existing* `opencode.json`; never replace all PAI settings with just this fragment):

```json
{
  "mcp": {
    "hindsight-clover": {
      "type": "remote",
      "url": "https://api.hindsight.vectorize.io/mcp/Luck13Clover/",
      "enabled": true,
      "oauth": false,
      "headers": {
        "Authorization": "Bearer {file:/home/microda/.config/hindsight/Clover.key}"
      }
    }
  }
}
```

**Credential handling:** A local private key file was created at `/home/microda/.config/hindsight/Clover.key`, using a hidden-input prompt rather than pasting secrets into commands or chat. The config directory was set to mode `700`, and key file to mode `600`. **No API key value is recorded in this report.**

**Initial MCP failure:** OpenCode's status view showed:

```text
hindsight-clover  SSE error: Invalid content type,
                  expected "text/event-stream"
```

A direct, authenticated JSON-RPC `initialize` probe to the Hindsight endpoint separated the actual server response from OpenCode's SSE error. This diagnostic sends the key through standard input as a header, prints only the HTTP code/content type, and does not store a secret in this report:

```bash
printf 'Authorization: Bearer %s\n' "$(cat ~/.config/hindsight/Clover.key)" | \
  curl -sS --max-time 12 -o /dev/null \
    -w 'HTTP %{http_code} | Content-Type: %{content_type}\n' \
    -H @- \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json, text/event-stream' \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"Clover","version":"1"}}}' \
    'https://api.hindsight.vectorize.io/mcp/Luck13Clover/'
```

```text
HTTP 401 | Content-Type: application/json
```

The Architect suspected a typo while entering a long API key on a small phone keyboard. After re-entering/correcting the key and repeating the **same endpoint probe**, the result became:

```text
HTTP 200 | Content-Type: text/event-stream
```

This is the key diagnostic transition: the endpoint accepted the credential and returned the expected stream response. The original SSE content-type message was downstream of receiving an authorization error in JSON rather than a successful stream.

**Final report from the Architect:** Instead of running another `opencode mcp list` after the corrected key, the Architect went straight to Clover and confirmed that **Hindsight was up and Clover was already storing information about The Burrow from the repository**. Treat that as an operator-confirmed successful functional test. A *separate-session recall* test was not explicitly captured during this session.

---

## 4. Verified milestones, with evidence level

| Milestone | Result | Basis |
|---|---|---|
| XFCE desktop renders on Luck13 | **Verified** | Screenshots from AVNC |
| VNC local authentication and data exchange | **Verified** | TightVNC logs from `127.0.0.1` |
| Termux desktop launcher recognizes a running server | **Verified** | Launcher terminal output |
| Termux shutdown launcher stops VNC | **Verified** | `Killing Xtightvnc process ID 32149` |
| Termux desktop launcher starts a fresh server | **Verified** | New `localhost:1` and subsequent AVNC XFCE image |
| Git, Node 24, npm, Bun execute | **Verified** | Versions and `Luck13 says: 42` |
| Root OpenCode V2 installs | **Verified** | `opencode v2.0.28` |
| Clover's OpenCode V1 + PAI install and launch | **Verified** | `pai` welcome banner + OpenCode TUI |
| Clover makes an AI response | **Verified** | First conversation screenshot |
| Hindsight endpoint accepts corrected credentials | **Verified** | HTTP 200 / `text/event-stream` probe |
| Clover actually stores repository information in Hindsight | **Architect-confirmed** | Final in-session report |
| Recall from a *new* PAI session | **Not yet separately tested in record** | Follow-up opportunity |
| Google TTS speaks successfully | **Not yet tested in record** | Provider selected during install |
| Bare `pai` available automatically from Bash | **Not yet fixed in record** | `source ~/.zshrc && pai` worked |

---

## 5. Working paths and operating notes

| Item | Path / invocation |
|---|---|
| Debian CLI (from Termux) | `debian` |
| Debian CLI as Clover | `proot-distro login --user microda debian` |
| Debian/XFCE start | `debian-desktop` |
| Debian/XFCE stop | `debian-stop` |
| AVNC | `127.0.0.1:5901` |
| Clover's home | `/home/microda` |
| PAI checkout | `/home/microda/pai-opencode` |
| Project-level OpenCode config | `/home/microda/pai-opencode/opencode.json` |
| Project config backup | `/home/microda/pai-opencode/opencode.json.bak` |
| PAI files | `/home/microda/pai-opencode/.opencode/` |
| PAI dot-directory symlink | `/home/microda/.opencode` |
| Current PAI launcher definition | `/home/microda/.zshrc` |
| Clover's Hindsight secret | `/home/microda/.config/hindsight/Clover.key` |
| Bank-scoped Hindsight MCP URL | `https://api.hindsight.vectorize.io/mcp/Luck13Clover/` |

**Manual start pattern as tested:** Open Termux, enter Clover's Debian user with `proot-distro login --user microda debian`, then invoke `source ~/.zshrc && pai` until the Bash shell setup is made persistent. If XFCE is desired, launch `debian-desktop` from a separate Termux session, connect through AVNC, and stop the desktop intentionally with `debian-stop` when done.

**Operational distinctions:** Starting a Debian CLI session or XFCE is not the same as summoning Clover. Clover's DA runtime remains a user-initiated `pai` operation.

## 6. Lessons learned / troubleshooting notes

1. **Keep track of which shell and filesystem are active.** A `~ $` Termux prompt resolves home paths under `/data/data/com.termux/files/home`; `microda@localhost` resolves `~` to `/home/microda` in Debian.
2. **An installed program is not automatically on another user's `PATH`.** Root's Bun global OpenCode V2 and Clover's user-scoped OpenCode V1 are separate.
3. **The PAI installer completed despite a shell startup mismatch.** `pai()` ended up in `.zshrc` while the current interactive shell was Bash. Sourcing `.zshrc` worked for this session.
4. **Use the project-level `opencode.json`.** The `.opencode` directory contains PAI tools/assets; it was not where this project's root OpenCode JSON lived.
5. **An SSE error may mask an HTTP authorization response.** The direct MCP initialization request revealed 401; correcting the key turned it into 200 with the expected stream content type.
6. **Stale X display locks must be correlated with process state.** A `/tmp/.X1-lock` file alone is insufficient reason to assume the VNC server is running. Avoid deleting live display locks.
7. **Server-connected does not necessarily mean viewer-rendered.** TightVNC showed authenticated loopback clients while AVNC still displayed a spinner. Actual rendering was eventually verified by seeing XFCE.
8. **Small-keyboard secrets are easy to mistype.** Keep credentials in protected local files and verify them via status codes; do not display the key in logs or screenshots.
9. **Manual controls are part of The Burrow's design.** No DA auto-start configuration was added.

## 7. Focused next tasks

The priority after this session is to **harden Clover's already-working memory connection**, not rebuild the environment.

- **Persistent recall check:** Have Clover deliberately retain a small, distinctive fact in `Luck13Clover`; exit PAI fully, summon her again, and ask her to recall it. Capture the result in this report's follow-up.
- **Fix Bash startup once:** Put the existing `pai` launcher/function (or a clean sourcing stanza) in Clover's `.bashrc` so future manual summons use simply `pai`.
- **Verify connection status in the UI:** If desired, inspect OpenCode's MCP status after the key correction, and record the final `hindsight-clover` status as an additional explicit datapoint.
- **Review identity and voice when ready:** Clover's PAI identity is set; Google TTS was chosen but no voice output was verified.
- **Optional launcher polish:** Make the VNC process/display check more display-specific if the environment later grows beyond one X server.

## 8. Final state / handoff

**Clover 🍀 is running inside Luck13's Debian ARM64 environment, using PAI/OpenCode V1 in the dedicated `microda` account.** Her first conversation was successful. Her existing Hindsight memory bank is **`Luck13Clover`**, connected through a project-level MCP entry with an API key stored privately. The fixed-credential initialization test returned **HTTP 200 / `text/event-stream`**, and the Architect reported Clover actively recording details from The Burrow repository.

**The immediate next session can begin with Clover herself**, rather than revisiting the desktop installation or toolchain. Test memory recall across a fresh invocation, then refine identity, memory practices, and the manual `pai` launcher as needed.

> *A new four-leaf clover has appeared in the Warren.* 🍀🐈‍⬛

---

### Provenance and security

This report consolidates the commands, terminal captures, screenshot observations, and Architect confirmations from the October 13–14 Luck13 build conversation. "Verified" means direct visible terminal/screenshot evidence in that exchange; "Architect-confirmed" means the user's follow-up report. Commands reproduced here are a historical record, not an instruction to re-run setup or reinstall packages. Secret values are intentionally excluded. The Hindsight API key must remain outside version control (include `.config/hindsight/*.key` and any local secret copies in appropriate ignore/backup policy).
