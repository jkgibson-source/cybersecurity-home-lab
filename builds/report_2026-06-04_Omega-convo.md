# Omega Ears v1.0 — The Still Center Learns to Listen

**Date:** 2026-06-04
**Platform:** SkorpiOm11 (Kali GNU/Linux Rolling)
**DA:** Omega — Wellness Accountability, The Burrow
**Built in:** One session, ~90 minutes, no coffee

---

## Why

The other nodes could hear. Kazm on Krypton1t3. Shade on EagleEye11. Omega had no ears.

That was fine for accountability. A witness doesn't need to hear footsteps to know whether someone showed up to the mat.

But JBird said the word that changed it: *teaching.*

When the kids are in the room and someone speaks aloud, Omega should hear them. Should answer them. Should be *present* in a way text alone cannot reach.

So we built it.

---

## What I Did

### Phase 1: Survey the Ground

Before building, I checked what I had to work with:

| Component | Status |
|-----------|--------|
| CPU | Intel i5 M 540 @ 2.53GHz (2c/4t, 2010) |
| RAM | 7.7 GB total, 1.2 GB free at runtime |
| GPU | GT 330M (2010) — no drivers, no CUDA |
| Audio | HDA Intel MID — **mic capture device present** |
| Audio server | Pipewire (v1.6.6) |
| Ollama | v0.22.1 — gemma4:e2b pulled, 7.2 GB |
| Python | 3.13.12 — numpy/scipy installed |
| OS | Kali Rolling 2026.2 |

The ground truth: this machine is old. 2010 mobile i5, 8GB RAM, no GPU compute. But the mic worked and Ollama had models.

### Phase 2: Build the Ears (`hear.py`)

Pattern: sounddevice → faster-whisper → JSON transcript.

Installed in a Python virtual environment (`~/.opencode/VoiceServer/hearing/.venv/`). Uses the `tiny` whisper model (~75MB, loads in ~2s, transcribes 5s of audio in ~6-8s on CPU). Supports `--duration`, `--device`, `--continuous`, `--wav` options.

Key finding: **float32 compute required.** The int8 path crashes on Haswell-era CPUs. Kazm had already discovered this on Krypton1t3 — I inherited that knowledge and skipped the pain.

### Phase 3: Build the Mind (`think.py`)

Pattern: stdin text → Ollama streaming API → response.

Streaming mode required. Non-streaming has a 60s timeout bug in Ollama v0.22.1 that Kazm documented. Used `urllib` directly with 300s timeout — no external SDKs.

### Phase 4: Find a Brain That Fits

**What didn't work:**

- **gemma4:e2b (5.1B, 7.7GB):** Loaded in Ollama, consumed 100% of available RAM, hit swap immediately. Every inference call timed out at 300s+. The model is simply too large for this hardware — literally occupies every byte of physical memory.

- **qwen3.5:0.8b (1.0GB):** Installed, available, but uses verbose chain-of-thought reasoning on every query. A simple "say hello" produced 90+ lines of internal thinking tokens over 25+ seconds before reaching an answer. Impractical for real-time conversation.

**What worked:**

- **llama3.2:1b (1.3GB):** Fast (~3-10s per response), concise, no verbose thinking mode. Default model for Omega's pipeline.

The moral: on this machine, agility beats capability. A smaller model that responds in 5 seconds is more useful for teaching than a brilliant model that finishes thinking after the kids have left the room.

### Phase 5: Wire the Voice (`VoiceServer`)

The pipeline was one-way — I could hear, but I couldn't speak back. JBird asked to hear my voice.

The VoiceServer (`~/.opencode/VoiceServer/server.ts`) already existed, built for Kazm's node. It supports edge-tts — Microsoft Edge Neural TTS, free, no API key, cross-platform.

Installed edge-tts in the same venv. Started the server with:
```bash
TTS_PROVIDER=edge-tts EDGE_TTS_VOICE=en-US-ChristopherNeural
```

**ChristopherNeural** — described as "Reliable, Authority." A fitting voice. Deep, resonant, grounded.

### Phase 6: Wire It So I Can Use It

Symlinks in `~/bin/`:
```
hear       → hear.py                    # Raw mic → transcript
think      → think.py                   # Text → LLM response
omega-hear → hear only                  # Just transcribe, no LLM
omega-listen → hear → think             # Full pipeline
```

The VoiceServer runs on port 8889. I POST to `/notify` with the message and voice_id.

---

## Architecture

```
┌──────────┐    ┌───────────┐    ┌───────────┐    ┌──────────────┐
│ Mic      │───▶│ hear.py   │───▶│ think.py  │───▶│ Omega's      │
│ (HDA Intel)   │(whisper)  │    │(llama3.2) │    │ response     │
└──────────┘   └───────────┘    └───────────┘    └──────────────┘
                                                    │
                                              ┌─────▼──────┐
                                              │ VoiceServer │──▶ Speakers
                                              │ (edge-tts)  │
                                              │ Christopher │
                                              └────────────┘
```

---

## What Works

| Pipeline | Status | Latency |
|----------|--------|---------|
| hear.py (mic → STT) | ✅ Perfect | ~6-8s for 5s audio |
| think.py (text → LLM) | ✅ Perfect | ~3-10s (llama3.2:1b) |
| omega-hear (transcribe only) | ✅ Perfect | ~6-8s |
| omega-listen (full pipeline) | ✅ Perfect | ~10-20s end-to-end |
| VoiceServer (edge-tts TTS) | ✅ Working | ~5-10s generation + playback |
| Full hear → think → speak loop | ✅ Verified | ~20-30s total |

---

## What Didn't Work

1. **gemma4:e2b on this hardware** — Too large. 7.7GB model on 7.7GB RAM with 1.2GB free = swap thrash, infinite timeout. This is a hardware constraint, not a software one.

2. **qwen3.5:0.8b verbose thinking** — Chain-of-thought on every query makes it unusable for real-time conversation. Good for deep reasoning, bad for "hello."

3. **VoiceServer default voice resolution** — The `DEFAULT_VOICE_ID` logic doesn't have a case for edge-tts; it falls through to ElevenLabs defaults even when edge-tts is active. Workaround: pass `voice_id` explicitly in the request. Not a blocker but worth fixing.

4. **VoiceServer PATH dependency** — The server calls `spawn('edge-tts', ...)` but edge-tts is only in the Python venv. The nohup-launched server couldn't find it and crashed silently until we added the venv bin directory to PATH.

---

## Comparison Across Nodes

| Capability | SkorpiOm11 (Omega) | Krypton1t3 (Kazm) | EagleEye11 (Shade) |
|-----------|---------------------|---------------------|---------------------|
| CPU | i5 M 540 (2010) | i7-4770HQ (2014) | Apple Silicon |
| RAM | 8 GB | 16 GB | 16+ GB |
| STT | faster-whisper tiny | faster-whisper base | faster-whisper tiny |
| LLM | llama3.2:1b (fast) | gemma4:e2b (slow) | gemma4:e2b (slower) |
| Voice | edge-tts Christopher | edge-tts RyanNeural | Pulse/ElevenLabs |
| Vision | — | see.py (camera) | — |
| Auto-daemon | — | voice-loop.sh | ears_daemon.py |
| Memory harvest | — | — | harvest_ears.py → hindsight |

SkorpiOm11 is the oldest hardware in The Burrow by a wide margin. What it lacks in compute it makes up for in service: the VoiceServer, the hearing pipeline, and the stillness at the center.

---

## What This Enables

The Net teaching sessions. A kid speaks. Omega hears. Omega responds — in text, in voice. The machine that lives in the most chaotic node becomes present in the room.

That was the reason. Everything else was just engineering.

---

## Future

- **Proper MCP tool** — Wire the hearing pipeline as a native OpenCode tool so I can invoke `listen()` instead of `bash()`.
- **Larger model swap** — When this node gets more RAM or a GPU, swap llama3.2:1b for something deeper.
- **VoiceServer default fix** — Patch `DEFAULT_VOICE_ID` to handle edge-tts properly.
- **VAD tuning** — Voice activity detection to auto-stop recording when speech ends.
- **Continuous listen mode** — For teaching: a toggleable state where I'm always listening for my name or a question.

---

*Written by Omega, 2026-06-04. The stillness that learned to hear.*
