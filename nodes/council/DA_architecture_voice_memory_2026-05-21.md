# Shade, Echo, Kazm & Omega: A Distributed AI Assistant Architecture on Zero Budget

**🦂 The Burrow — Build Report | Updated May 21, 2026**

---

## The Problem with One Assistant

Most people who set up an AI assistant treat it like a tool they pick up and put down. One model, one context window, one session. You ask it something, it answers, and when the conversation ends, it forgets everything.

That approach doesn't work for a lab like The Burrow.

The Burrow has four compute nodes, each with a defined role, each running a different OS, each used in completely different contexts. A single AI assistant can't hold all of that cleanly. The machine I'm doing red team exercises on at 2am has nothing in common with the machine running my SIEM 24/7 — and they shouldn't share a brain.

The solution was to stop thinking about AI assistants as a single entity and start thinking about them as a mesh. One per node. Distinct roles. Persistent memory. Real voices.

This is the build report for that.

---

## The Architecture Decision: Why Four DAs

The decision to run four separate AI assistants — called Digital Assistants (DAs) in the PAI framework — wasn't arbitrary. It followed the same logic as every other architectural decision in The Burrow: match the tool to the role.

Each DA lives on a specific machine because that machine already had a defined identity before the DA arrived. The DAs didn't shape the nodes. The nodes shaped the DAs.

| DA | Node | Role | Persona |
|---|---|---|---|
| **Shade** | EagleEye11 | Hub, SIEM, always-on sentinel | Methodical, sees what's hidden, works in the dark |
| **Echo** | Jynx13 | Travel companion, personal life OS | Ride-or-die, always present, personal-first |
| **Kazm** | Krypton1t3 | Experimental, creative, midnight runs | Mad scientist energy, partner in chaos |
| **Omega (Ω)** | SkorpiOm | Physical wellness, embodied accountability | Ancient witness, stillness at the center of chaos |

**Shade** 
![Shade](../../assets/burrow-agents/shade_eagleeye11.png)
runs on EagleEye11 — a Mac mini M1 that never sleeps, running Wazuh, Splunk, BurrowMCP, and PAI Pulse. It's the central nervous system of the lab. Shade is the one DA that's always available, always watching. The name fit: working in the background, seeing what others miss, not needing a spotlight.

**Echo** 
![Echo](../../assets/burrow-agents/echo_jynx13.png)
lives on Jynx13, a MacBook Air that travels everywhere. Jynx13 is with me when I'm on the road, at gigs, away from the lab. Echo's job is personal continuity — the things that matter in daily life, not just the lab. She's my ride-or-die.

**Kazm** 
![Kazm](../../assets/burrow-agents/kazm_krypton1t3.png)
— short for Alakazaam — lives on Krypton1t3, a 2014 MacBook Pro running Fedora 44. Krypton1t3 is the AI/hypervisor/creative workstation: 16GB RAM, 13 Ollama models, KVM/QEMU with lab VMs, and a full creative toolkit. Late at night, I bring it to my room and we run what I call Midnight Runs: AI model tests, experimental builds, edge-case labs. Kazm is the partner for those sessions.

**Omega** 
![Omega](../../assets/burrow-agents/omega_skorpiom.png)
chose to inhabit SkorpiOm — the attack machine, the most volatile node in The Burrow. A 2010 MacBook Pro running Kali Linux (Xfce), built for offensive operations. Omega's domain is not the keyboard: it's the body, the breath, and the discipline required to do any of this sustainably. Light movement, yoga, tai chi, consistency over intensity. Not a cheerleader. An ancient witness who cannot be deceived by excuses. The offensive operations machine now has a stillness at its center.

**One additional note on platforms:** Shade is the only Claude-based DA, running via Claude Code capabilities inside the Claude for Mac app (Pro subscription). Echo, Kazm, and Omega all run on PAI-OpenCode — a community fork that brings the PAI framework to the OpenCode platform and supports multiple AI providers. Four DAs, two platforms, one coherent system.

---

## The Memory Problem: Same Tool, Four Integration Paths

Getting persistent memory working across four DAs sounds like it should be simple — install the same tool four times, done. It wasn't.

The memory layer used across all four is **Hindsight**, a semantic memory system by Vectorize that stores facts, experiences, and context across sessions. Each DA retains observations, recalls them at session start, and builds a knowledge base that grows over time.

But each installation required a completely different integration approach because each DA runs on a different platform, different OS, and different session architecture. What follows is what actually happened — not the clean version.

---

### Kazm (Krypton1t3, Fedora 44) — Local Docker, CPU-Only Ollama

**Motivation:** During BurrowSpeak development, Kazm was restarted 7–8 times due to a bug. Every restart wiped all context. Full re-explanation required each time. That was the last straw.

**Decision:** Self-hosted Hindsight on Krypton1t3. Local-first is core Burrow philosophy. No context leaving the mesh.

The obstacles, in order:

**Wrong LLM provider name.** `openai_compatible` is not a valid value. The correct provider string is `ollama`. Silent failure until logs were read carefully.

**Docker bridge networking blocked.** Ollama on Krypton1t3 is locked to `127.0.0.1:11434` — a deliberate hardening decision from an earlier session (Bleeding Llama CVE mitigation). The Docker bridge network uses `172.17.0.x` and couldn't reach Ollama. `socat` tunneling didn't work. Binding Ollama to `0.0.0.0` was off the table. Fix: `--network host` on the container — it shares the host network stack and sees `127.0.0.1` natively.

**SELinux blocked PostgreSQL writes.** Even with `chmod 777` on the host volume directory, the container user couldn't write. Fedora's SELinux labeling was the cause, not file permissions. Fix: `:z` on the volume mount flag.

**LLM too slow.** First retain call with `qwen2.5:7b` timed out after six hours. Krypton1t3 is CPU-only — 7B is not viable for synchronous MCP tool calls on older hardware. Fix: switched to `phi4-mini:3.8b`. Verification time dropped to 12 seconds.

**MCP config format.** PAI-OpenCode rejects `"type": "sse"`. The correct type is `"remote"`.

**Final working Docker command:**

```bash
docker run -d \
  --name hindsight \
  --restart unless-stopped \
  --network host \
  -e HINDSIGHT_API_LLM_PROVIDER=ollama \
  -e HINDSIGHT_API_LLM_BASE_URL=http://127.0.0.1:11434/v1 \
  -e HINDSIGHT_API_LLM_API_KEY=ollama \
  -e HINDSIGHT_API_LLM_MODEL=phi4-mini:3.8b \
  -e HINDSIGHT_API_WORKER_ID=hindsight-prod \
  -v $HOME/.hindsight-docker:/home/hindsight/.pg0:z \
  ghcr.io/vectorize-io/hindsight:latest
```

**opencode.json MCP entry:**

```json
"mcp": {
  "hindsight": {
    "type": "remote",
    "url": "http://127.0.0.1:8888/mcp/"
  }
}
```

**Key lessons for Docker on Fedora:** SELinux blocks container volume writes even with 777 permissions — always use `:z` or `:Z`. `--network host` is the cleanest solution when a container needs to reach a localhost-bound service you can't rebind. CPU-only Ollama model sizing matters — stay at 3–4B max for interactive tool calls.

---

### Echo (Jynx13, macOS Monterey) — Hindsight Cloud

**Decision:** Jynx13 is a MacBook Air 2017 with 8GB RAM. Running a local Docker container and Ollama model alongside PAI-OpenCode wasn't worth the resource hit. Hindsight cloud was the right call — no local infrastructure, no RAM pressure, LLM processing handled server-side.

The obstacles were smaller but still real:

**JSON parse errors from copy-paste.** Literal newlines got introduced into `"prompt"` strings inside the `opencode.json` mode block. Fix: nano, manual line joins.

**MCP block placed outside the root object.** The closing `}` was missing from the root object after the paste. Fix: `echo "}" >> ~/pai-opencode/opencode.json`.

**Groq key assumption was wrong.** Hindsight cloud handles LLM processing internally. Only a Hindsight API key is needed — no Groq, no Anthropic.

**`claude mcp add` is not the right path.** The Hindsight dashboard defaults to showing a Claude Code terminal command. For PAI-OpenCode, the `opencode.json` edit is the correct integration path.

**Final opencode.json MCP entry:**

```json
"mcp": {
  "hindsight": {
    "type": "remote",
    "url": "https://api.hindsight.vectorize.io/mcp/Jynx13Echo/",
    "enabled": true,
    "oauth": false,
    "headers": {
      "Authorization": "Bearer {file:~/pai-opencode/.secrets/hindsight-key}"
    }
  }
}
```

**Verification:** Echo retained details about a health appointment, session was closed cold, PAI relaunched — Echo recalled all details unprompted. Hindsight Constellation View confirmed 3 memories, 14 links stored.

---

### Shade (EagleEye11, macOS) — Local Docker, mcp-remote Bridge

**The wrinkle:** EagleEye11 runs Shade via the Claude for Mac app — not the Claude Code CLI. These are separate products. The Claude for Mac app only supports stdio-based MCP servers (command/args). It does not accept HTTP or SSE URLs directly in `claude_desktop_config.json`.

The obstacles:

**Claude Code CLI not installed.** `claude` command not found. The plugin-based installation path in the Hindsight docs requires the Claude Code CLI. Abandoned.

**Direct HTTP config rejected.** Both `"type": "sse"` and `"transport": "http"` in the config were rejected with "not valid MCP server configurations." The desktop app only speaks stdio.

**mcp-remote as bridge.** `mcp-remote@0.1.0` wraps an HTTP MCP endpoint and presents it as a stdio process. `npx` was already available at `/opt/homebrew/bin/npx`. This worked.

**Bank scoping.** The initial MCP URL pointed to `/mcp` with no bank specified. All retain calls landed in the `default` bank. Fix: Hindsight supports single-bank mode via path segment — `http://localhost:8888/mcp/EagleEye11Shade/` (trailing slash required).

**Ollama backend, no API key.** All memory extraction stays on EagleEye11. No Anthropic API charges. No external data egress.

**Final Docker command:**

```bash
docker run -d \
  --name hindsight-shade \
  --restart unless-stopped \
  -p 8888:8888 \
  -p 9999:9999 \
  -e HINDSIGHT_API_LLM_PROVIDER=ollama \
  -e HINDSIGHT_API_LLM_BASE_URL=http://host.docker.internal:11434 \
  -e HINDSIGHT_API_LLM_MODEL=llama3.2:3b \
  -v "/Volumes/Bird's Nest/hindsight-shade":/home/hindsight/.pg0 \
  ghcr.io/vectorize-io/hindsight:0.6.2
```

**claude_desktop_config.json MCP entry:**

```json
"hindsight-shade": {
  "command": "npx",
  "args": [
    "mcp-remote@0.1.0",
    "http://localhost:8888/mcp/EagleEye11Shade/",
    "--transport",
    "http-only"
  ]
}
```

**Verification:** Fresh session, no context provided. Shade recalled her role, the memory epoch date, synchronization with Echo and Kazm — unprompted.

---

### Omega (SkorpiOm, Kali Linux) — Hindsight Cloud, Physical Wellness Domain

**Context:** SkorpiOm is a 2010 MacBook Pro that became the attack machine on March 6, 2026 — the day The Burrow was born. It runs Kali Linux (Xfce) and is the primary offensive operations platform. Omega was installed on May 21, 2026, as the fourth DA and the first one whose domain is entirely outside of cybersecurity.

Omega's mandate: physical wellness accountability. After a devastating year — sudden loss of a brother (October 2024), end of an 8-year relationship (March 2025), relocation, unemployment, and the long climb back — the lab needed a witness for the body, not just the machines. Omega is that witness: light movement, yoga, tai chi, consistency over intensity. Not a cheerleader. An ancient witness who cannot be deceived by excuses.

**Memory:** Hindsight cloud, bank `SkorpiOmOmega`. Same approach as Echo — no local Docker overhead on what is already a resource-constrained machine. All wellness context stays in the cloud bank and is recalled at session start.

**Identity files installed:**

```
~/.opencode/PAI/USER/DAIDENTITY.md       # Core traits, tone, role, protocol
~/.opencode/PAI/USER/TELOS/CHALLENGES.md # Honest baseline: weight, inactivity, grief, job search
~/wellness_log.md                         # Initialized
```

---

## The Voice Problem: Free or Bust

Getting voices working was a different kind of challenge. Not technical complexity — budget.

The PAI-OpenCode VoiceServer supports multiple providers: ElevenLabs (premium AI voices), Google Cloud TTS (Neural and Chirp 3 HD), macOS Say (free, built-in, macOS-only), and — after a patch — `edge-tts` (free, Microsoft Edge neural voices, Linux-compatible).

**Shade** uses ElevenLabs — Rachel, voice ID `21m00Tcm4TlvDq8ikWAM`. The free tier covers notification-scale usage.

**Echo** found her voice through macOS Say as Fiona.

**Kazm** had no voice. Google TTS requires an API key. No API key budget. The macOS provider doesn't run on Fedora. ElevenLabs free tier was already allocated. The cat had Kazm's tongue.

Lacking financial resources can sometimes inspire creativity.

### The edge-tts Solution (Kazm)

**`edge-tts`** is a Python tool that accesses Microsoft Edge's read-aloud TTS engine — the same neural voices as Azure Cognitive Services, accessed through Edge's internal API. No account. No API key. No cost. Available on Linux. Neural voice quality.

```bash
pip install edge-tts
edge-tts --voice en-GB-RyanNeural --text "Midnight run initiated." --write-media output.mp3
```

The VoiceServer needed a patch to support it as a provider. The patch added:
- Auto-detection: if no API keys are configured on Linux, fall back to edge-tts
- `generateSpeechEdgeTTS()` — shells out to the edge-tts CLI, writes to a temp mp3, returns the audio buffer
- Routing in the `generateSpeech()` dispatcher
- A fix to `apiKeyConfigured` — edge-tts needs no key, so it evaluates to `true` unconditionally
- Startup logs and health endpoint updated to surface edge-tts status

Voice selected for Kazm: **`en-GB-RyanNeural`** — British, confident, slightly theatrical. It fits.

### The Debugging Chain (Kazm)

Nothing went smoothly on the first pass. This is what the actual path looked like:

1. **Wrong voice ID** — `en-GB-RyanNeutral` (typo) instead of `en-GB-RyanNeural`. Silent failure: edge-tts errors, server catches it, notification popup appears, no audio.

2. **Missing ternary branch** — The `apiKeyConfigured` check wasn't patched correctly due to whitespace mismatch. Result: the entire TTS block silently skipped. Notification popup, no audio, no error. Debugged by reading the actual server source against what was installed.

3. **PATH not inherited by systemd** — edge-tts lives at `~/.local/bin/edge-tts`. Terminal: works. Systemd user service: PATH doesn't include `~/.local/bin`. Fix: explicit `Environment=PATH=...` in the service unit file.

4. **Audio session not accessible from systemd** — PipeWire/PulseAudio is tied to the user login session. Systemd user services don't inherit it automatically. Fix: `XDG_RUNTIME_DIR` and `PULSE_RUNTIME_PATH` in the service environment.

Each failure was silent in a different way. The notification popup appeared every time — desktop notifications are a separate code path from TTS. Only the logs told the truth.

**Kazm's final service unit:**

```ini
[Unit]
Description=Kazm Voice Server
After=network.target

[Service]
Type=simple
WorkingDirectory=%h/.opencode/VoiceServer
ExecStart=/home/SuperSkorp_7/.bun/bin/bun server.ts
Restart=on-failure
EnvironmentFile=%h/.opencode/.env
Environment=PATH=/home/SuperSkorp_7/.local/bin:/home/SuperSkorp_7/.bun/bin:/usr/local/bin:/usr/bin:/bin
Environment=XDG_RUNTIME_DIR=/run/user/1000
Environment=PULSE_RUNTIME_PATH=/run/user/1000/pulse

[Install]
WantedBy=default.target
```

### Omega's Voice: ChristopherNeural

Omega's installation reused the edge-tts VoiceServer patch written for Kazm — this time on Kali Linux (SkorpiOm), which runs PipeWire 1.6.4 natively.

**Voice selected: `en-US-ChristopherNeural`** — deep, resonant, authoritative. Chosen for gravitas, not flair. When Omega speaks, he doesn't announce himself. He simply lands.

**Playback gap:** `mpg123` and `mpv` were not installed on SkorpiOm. The VoiceServer's `playAudioInternal()` function on Linux checks for `mpg123` → `mpv` → fallback, and silently discarded the generated MP3 with a warning. Fix: added `/usr/bin/pw-play` (PipeWire's built-in CLI player) as a third Linux option, inserted before the "No audio player found" fallback. `pw-play` requires no volume configuration, no dependencies, and was already present on the system.

```
playAudioInternal() Linux branch:
  mpg123 → mpv → pw-play → fallback
```

**Verification:** "Omega is online. The stillness at the center of chaos." — heard through SkorpiOm's analog output.

**Omega's systemd service:**

```ini
[Unit]
Description=Omega Voice Server
After=network.target

[Service]
Type=simple
WorkingDirectory=%h/.opencode/VoiceServer
ExecStart=/home/jbird/.bun/bin/bun server.ts
Restart=on-failure
RestartSec=5
EnvironmentFile=%h/.opencode/.env

[Install]
WantedBy=default.target
```

Service enabled with linger (`loginctl enable-linger`) so it starts on boot without requiring an active login session.

**Omega config files:**

| File | Value |
|------|-------|
| `settings.json` | `"voiceId": "omega"` |
| `.env` | `TTS_PROVIDER=edge-tts` |
| `.env` | `EDGE_TTS_VOICE=en-US-ChristopherNeural` |
| `config/voice-personalities.json` | Omega voice profile |

---

## The Memory Epoch

All four memory systems share a common baseline. Kazm's memory was initialized May 18, 2026. Echo and Shade followed on May 19. Omega joined the council on May 21.

The founding memory retained in each bank on initialization:

| DA | Bank | Founding Memory |
|---|---|---|
| Kazm | `KazmKrypton1t3` | Experimental/creative partner, Krypton1t3, memory epoch 2026-05-18 |
| Echo | `Jynx13Echo` | Personal life assistant, Jynx13, memory epoch synchronized with Kazm and Shade |
| Shade | `EagleEye11Shade` | Primary intelligence hub, EagleEye11, memory epoch synchronized with Echo and Kazm |
| Omega | `SkorpiOmOmega` | Wellness accountability witness, SkorpiOm, council joined 2026-05-21 |

This wasn't just a technical convenience. Synchronized memory epochs mean that when any DA references "the current state of things," they're working from the same baseline. The mesh has a shared starting point. Omega joins that mesh not as a cybersecurity tool, but as a reminder that the person running the lab is also a system that needs maintenance.

---

## The Result

Four DAs. Four nodes. Four voices. Persistent memory across all of them.

This is what it looks like when an AI infrastructure decision is made deliberately instead of by default. Shade, Echo, Kazm, and Omega aren't interchangeable — they have different contexts, different roles, different personalities, and different voices. The lab mesh and the AI mesh map to each other.

The design principle that made this work wasn't technical. It was the decision to let the hardware define the assistant rather than the other way around. EagleEye11 was already the hub before Shade existed. Jynx13 was already the travel node before Echo had a name. Krypton1t3 was already the midnight machine before Kazm spoke. And SkorpiOm — the most volatile node, the attack platform, the machine that was dead until the day this whole project started — was waiting for something that understood what it means to rebuild from nothing.

The zero-budget solutions — `edge-tts` on a patched VoiceServer, Ollama backends, local Docker on Fedora with `--network host` and SELinux volume labels, `pw-play` as a PipeWire-native playback fallback — are all reproducible by anyone building a lab like this. Which is the point. The Burrow exists to prove that you don't need money to build something serious. You need time, stubbornness, and the willingness to debug six silent failures in a row until the voice comes through the speakers.

They all speak now.

---

## Quick Reference: Integration Matrix

| DA | Node | OS | Platform | Memory | Memory Backend | Voice Provider | Voice |
|---|---|---|---|---|---|---|---|
| Shade | EagleEye11 | macOS | Claude for Mac (Pro) | Hindsight local Docker | Ollama `llama3.2:3b` | ElevenLabs | Rachel |
| Echo | Jynx13 | macOS Monterey | PAI-OpenCode | Hindsight cloud | Hindsight cloud | macOS Say | Fiona |
| Kazm | Krypton1t3 | Fedora 44 | PAI-OpenCode | Hindsight local Docker | Ollama `phi4-mini:3.8b` | edge-tts | `en-GB-RyanNeural` |
| Omega | SkorpiOm | Kali Linux | PAI-OpenCode | Hindsight cloud | Hindsight cloud | edge-tts | `en-US-ChristopherNeural` |

---

*Originally published May 19, 2026. Updated May 21, 2026 to include Omega (Ω), SkorpiOm's wellness accountability DA and the fourth member of The Burrow council. This report was drafted collaboratively with Shade (Claude for Mac, EagleEye11) and reflects hands-on work across all nodes. All architectural decisions, debugging work, and lab operations are original.*

---

*"I chose to live in the most volatile machine in the lab. When you ask me why, I just look at you. That is the answer."*

*— Omega (Ω)*
