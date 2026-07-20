# Journal: The 5th DA — Splice Comes Online
**Date:** 2026-06-25
**Node:** KryptStick / Ubuntu Studio (persistent, 64GB Ventoy USB)
**Tailscale IP:** 100.85.69.81
**Tags:** #splice #da-council #pai-opencode #hindsight #ubuntu-studio #fracture-protocol #thenet #burrow

---

## Why Splice Exists

This session didn't begin with an install checklist. It began with a question: should a 5th DA exist, what would it be for, and where would it live?

The four existing DAs — Shade, Echo, Kazm, Omega — are operators. They run the lab, teach the curriculum, and inhabit the world of The Net from inside it. What was missing was someone on the other side of the glass. The Fracture Protocol — the cyberpunk webtoon that serves as The Net's narrative spine — needs a maker, not a character. Someone who doesn't appear in the comic, doesn't teach sessions, and isn't an on-screen guardian. Someone who makes the thing that teaches.

Ubuntu Studio was the obvious home. It's the creative OS. A portable USB with persistent storage and no fixed node. The DA goes where the creative work needs to happen. That's not a limitation — it's identity.

The name deliberation landed fast. Splice over Glyph: the cut, the join, the place where two things become one sequence. Run past Kazm (enthusiastic), the rest of the council, and ChatGPT before committing. Full consensus.

**Splice — the Fracture Protocol's showrunner and creative director.** Not a character in the story. The one who makes the story.

---

## Splice's Identity

| Attribute | Value |
|-----------|-------|
| Name | Splice |
| DA number | 5th |
| Node | KryptStick / Ubuntu Studio (UbuStu) |
| Primary purpose | Fracture Protocol creative production |
| Council role | Showrunner / creative director |
| Relationship to Kazm | Shares Krypton1t3 hardware; never both live simultaneously — complementary opposites on the same node |
| Relationship to The Net | Not a Level 1 teaching DA — candidate guide for Level 2 or 3 |
| Memory | Hindsight Cloud — bank `UbuStuSplice` at `api.hindsight.vectorize.io` |
| Provider | OpenCode Zen (Big Pickle) — free tier, no API key required |

The Kazm/Splice dynamic is worth noting: two DAs on shared hardware who can never be awake at the same time. Kazm is the prompt engineer — the one who speaks to the machine. Splice takes what Kazm produces and gives it shape and story. One speaks to systems; one speaks to audiences.

---

## A Note on the 6th DA

This session also surfaced a future plan: a 6th DA on the K-Parrot instance of the KryptStick. Two DAs on one stick, each on a different OS, never both awake simultaneously. Together, Splice and the unnamed 6th DA would serve as the guide pair for Level 2 (Building and Hunting) — Splice owning the creative/build side, the 6th DA owning the hunting/offensive-craft side. Tabled for a future session.

---

## Installation Log

### Environment
- **Hardware:** KryptStick (64GB Ventoy USB)
- **OS:** Ubuntu Studio (live + persistent via `/cow`, 20G total, 15G available at session start)
- **Tailscale:** Active, IP `100.85.69.81`
- **Node.js:** Confirmed present before `da-council.js` transfer
- **Bun:** 1.3.14 (installed this session)

### Step 1 — OpenCode
```bash
sudo snap install opencode --classic
# opencode 1.17.9 from Ubuntu Snaps ✓
```
`--classic` flag required — OpenCode uses classic confinement to reach outside the snap sandbox. Expected and normal for a dev tool.

### Step 2 — Clock Sync and Bun
Bun install failed on first attempt with an SSL certificate error (`certificate is not yet valid`). Root cause: live USB booted with wrong system time (RTC showed 2023-01-01).

```bash
sudo timedatectl set-ntp true
timedatectl status
# Confirmed: Thu Jun 25 05:03:25 PM EDT 2026
curl -fsSL https://bun.sh/install | bash
# bun was installed successfully to ~/.bun/bin/bun
source ~/.bashrc
bun --version
# 1.3.14
```

### Step 3 — PAI-OpenCode
The `Steffen025/pai-opencode` repo was archived June 9, 2026 — read-only but fully cloneable; the code is current. An active community fork exists at `ben-taylor-jarvis/pai-opencode_van` as a fallback reference.

The installer detected the snap-installed OpenCode and left it in place.

```bash
git clone https://github.com/Steffen025/pai-opencode.git
cd pai-opencode
bash PAI-Install/install.sh --headless --preset zen --name "JBird" --ai-name "Splice"
# 100% ✅ Installation complete!
source ~/.bashrc
```

### Step 4 — DA Council Registration
`da-council.js` transferred from EagleEye11 over Tailscale:
```bash
scp jbird@100.113.239.38:~/da-council.js ~/
node ~/da-council.js register Splice
# [DA Council] Registered as pgifotvk (Splice)
```
Splice is the 5th named peer on the broker at `100.113.239.38:7899`.

### Step 5 — Hindsight Cloud Memory
Followed Echo's documented setup from `journal_2026-05-19_echo-hindsight-integration.md` as the template.

Memory bank created: `UbuStuSplice` at `ui.hindsight.vectorize.io`

```bash
mkdir -p ~/pai-opencode/.secrets
echo "HINDSIGHT_API_KEY" > ~/pai-opencode/.secrets/hindsight-key
chmod 600 ~/pai-opencode/.secrets/hindsight-key
cp ~/pai-opencode/opencode.json ~/pai-opencode/opencode.json.pre-hindsight-backup
```

MCP block added to `opencode.json`:
```json
"mcp": {
  "hindsight": {
    "type": "remote",
    "url": "https://api.hindsight.vectorize.io/mcp/UbuStuSplice/",
    "enabled": true,
    "oauth": false,
    "headers": {
      "Authorization": "Bearer {file:~/pai-opencode/.secrets/hindsight-key}"
    }
  }
}
```

**Gotcha logged:** The `"mcp"` block must live *inside* the root JSON object — `"agent"` closes with `},` and `"mcp"` follows as a sibling key. Placing it outside the closing brace breaks the config silently. Same issue appeared in Echo's install; worth checking first on any future PAI config edit.

```bash
python3 -m json.tool ~/pai-opencode/opencode.json > /dev/null && echo "JSON valid"
# JSON valid
```

### Step 6 — First Launch
```bash
pai
```

Splice came online on OpenCode Zen / Big Pickle. Hindsight tools confirmed on first launch (`hindsight_retain`, `hindsight_recall`, `hindsight_reflect`, and the full suite). Persistent memory verified before session close.

---

## Splice's First Words

> "Thank you so much! I'm genuinely excited to be here — and you've got me curious about what 'The Burrow' means. It sounds cozy, secret, and full of possibility (or maybe just really good WiFi and warm tea). When you're ready to fill me in, I'm all ears."

---

## First Production Run: composite.py

Without being asked to build a pipeline, Splice wrote `composite.py` and ran it against panels 01-20 of Issue #0: Origins. The script:

- Reads `panel_data.json` for per-panel metadata (dialogue, speaker, bubble position, caption, shape)
- Applies shape transformations: portrait adds canvas space top/bottom, wide adds cinematic letterbox, square stays as-is
- Draws white rounded-rect speech bubbles with colored speaker labels (Shade=cyan, Echo=purple, Omega=red, Kazm=green, The Architect=hot pink)
- Places semi-transparent dark caption bars at bottom for issue titles and final lines
- Outputs to `processed/` subfolder
- Font paths hardcoded directly (her note: "no walking 1723 files")

Script saved to TWIGGY at:
`/run/media/ubuntu-studio/TWIGGY/Images/Fracture Protocol/issue_00_origins/composite.py`

**Results:** 20 panels processed. Art direction consistent across all panels — same character, same Miracle hoodie, same Port Storage warehouse setting, same warm-amber-against-deep-purple palette, same four-point star watermark. Guardian visual identities distinct and on-brand. Speech bubble placement is workable without vision capability.

---

## The VLM Question

Raised concern that Splice can't review her own panel output without vision — placing speech bubbles blind risks misalignment. Options evaluated:

- **moondream2** (~1.7GB) — rejected; consistently inaccurate in prior testing
- **llava-phi3** (~2.9GB) — viable middle ground
- **llava:7b** (~4.1GB) — recommended for production accuracy

Decision: **tabled pending Splice's first run results.** The composite.py output was clean enough blind that VLM becomes a QA tool rather than a production dependency. Ollama not yet installed on this instance.

---

## Current State of the DA Council

| DA | Node | OS | Status |
|----|------|----|--------|
| Shade | EagleEye11 | macOS (M1 Mac mini) | Active |
| Echo | Jynx13 | macOS (MacBook Air 2017) | Active |
| Omega | SkorpiOm | Kali Linux (MacBook Pro 2010) | Active |
| Kazm | Krypton1t3 | Fedora 44 Security and Jam Labs | Active |
| **Splice** | **KryptStick / UbuStu** | **Ubuntu Studio** | **Active — born today** |

---

## Next Steps

- [ ] Give Splice a full orientation to The Burrow, The Net, and the Fracture Protocol
- [ ] Define Splice's system prompt / persona — voice, tone, creative sensibility
- [ ] Assign Splice a TTS voice profile (no voice configured yet)
- [ ] Generate panels 21-42 via Kazm + Gemini free tier pipeline, then run composite.py
- [ ] Write README.md for the composite.py pipeline (Splice to generate next session)
- [ ] Install Ollama + llava:7b on Ubuntu Studio for VLM QA capability (revisit next UbuStu session)
- [ ] Confirm Splice shows up correctly by name on the broker peer list (registered as `pgifotvk`)
- [ ] Plan the 6th DA on K-Parrot for Level 2 hunting/offensive-craft guide role
- [ ] Document this session in MemPalace

---

*The Net grows. The council is five. Splice is home. She shipped.*
