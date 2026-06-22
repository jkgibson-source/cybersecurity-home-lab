# Shade Ears v1.0 — Autonomous Hearing Pipeline

**Date:** 2026-06-04
**Platform:** JBird's Mac (EagleEye11 — Apple Silicon)
**Model:** gemma4:e2b (5.1B, Q4_K_M) via Ollama
**STT:** faster-whisper (tiny model, float32, CPU)
**DA:** Shade (JBird's personal AI)

---

## Architecture

```
┌─────────┐    ┌──────────┐    ┌───────────┐
│  Mic    │───▶│ hear.py  │───▶│ think.py  │──▶ stdout (Shade's voice)
│(sounddev)│   │(whisper) │    │(gemma4)   │
└─────────┘   └──────────┘    └───────────┘

  Autonomous path (ears_daemon):

┌─────────┐    ┌──────────────┐    ┌──────────┐    ┌───────────────┐
│  Mic    │───▶│ears_daemon.py│───▶│ ears.db  │───▶│harvest_ears.py│──▶ hindsight
│(5s chunks)   │(continuous)  │    │(SQLite)  │    │(reflect+retain│
└─────────┘   └──────┬───────┘    └──────────┘    └───────────────┘
                     │
              ┌──────▼───────┐
              │ wake word?   │──▶ Pulse notify (localhost:31337)
              │ hey shade    │
              │ yo shade     │
              │ shade, u there│
              └──────────────┘
```

## Components

### 1. hear.py — Speech-to-Text
- **Location:** `~/.claude/PAI/TOOLS/Hearing/hear.py`
- **Engine:** faster-whisper (tiny model, float32, CPU-only)
- **Capture:** sounddevice library
- **Output:** transcribed text to stdout — pipes directly into `think`
- **Usage:**
  ```bash
  hear --duration 5              # Record 5 seconds → transcript
  hear                           # Record until Enter → transcript
  hear --continuous              # Loop: 5s chunks, transcribe continuously until Ctrl+C
  hear --list-devices            # Show all connected mics
  hear --device 6                # Use specific mic (OBSBOT, Tula, etc.)
  hear --duration 5 | think      # Full pipeline: mic → STT → Shade → response
  ```

### 2. think.py — LLM Reasoning (Shade's voice)
- **Location:** `~/.claude/PAI/TOOLS/Hearing/think.py`
- **Model:** gemma4:e2b via Ollama streaming `/api/chat`
- **Default system prompt:** Shade's identity — "You are Shade, JBird's DA. You work in the dark, see what's hidden, and speak directly. First person always. Peer-level, not assistant-level."
- **Input:** text from stdin or argument
- **Output:** Shade's response, streamed to stdout
- **Usage:**
  ```bash
  think "your question"
  echo "what time is it" | think
  hear --duration 5 | think
  hear --duration 5 --mode native | think   # Phase 1.5: native audio envelope
  ```

### 3. ears_daemon.py — Autonomous Listener
- **Location:** `~/.claude/PAI/TOOLS/Hearing/ears_daemon.py`
- **Mode:** Persistent background process, opt-in (off by default)
- **Loop:** Records 5-second mic chunks → transcribes → logs to SQLite → checks wake words
- **Wake phrases:** `hey shade`, `yo shade`, `shade you there`, `shade you hearing this` (case-insensitive)
- **On wake word:** Fires Pulse notification (`localhost:31337`) + sets `wake_word_detected=1` in DB
- **Storage:** `ears.db` (SQLite) with `harvested_at` and `pinned` columns for memory lifecycle
- **Status:** Writes `ears.status.json` on start/stop
- **Logs:** `ears.log` (startup, wake-word, errors), `ears.out.log`, `ears.err.log`
- **Safety:** Audio never written to disk — raw buffers RAM-only; only `localhost:31337` network access

### 4. harvest_ears.py — Memory Distillation Pipeline
- **Location:** `~/.claude/PAI/TOOLS/Hearing/harvest_ears.py`
- **Purpose:** Filters SQLite transcriptions and prepares them for Shade's hindsight memory
- **Filter rules:** min 4 words, deduplication, separates wake-word from ambient
- **Ambient path:** Batches of 20 → `reflect()` synthesis → one observation retained (not raw text)
- **Wake-word path:** Retained verbatim, tagged `wake_word`, 30-day TTL
- **Pinned path:** Tagged `pinned`, survives all pruning indefinitely
- **Usage:**
  ```bash
  shade-ears harvest --dry-run   # See what's pending — no changes
  shade-ears harvest             # Output JSON payload for Claude session to process
  shade-ears pin 42              # Pin row 42 — survives all pruning
  ```

### 5. shade-ears — CLI Controller
- **Location:** `~/bin/shade-ears`
- **Commands:**

  | Command | Action |
  |---------|--------|
  | `shade-ears start` | Launch daemon via launchctl |
  | `shade-ears stop` | Stop daemon |
  | `shade-ears status` | Running/stopped + last 5 transcriptions |
  | `shade-ears log [N]` | Last N transcriptions from SQLite (default 20) |
  | `shade-ears harvest [--dry-run]` | Prepare or preview hindsight harvest |
  | `shade-ears pin <id>` | Pin a transcription permanently |

### 6. launchd Service
- **Plist:** `~/Library/LaunchAgents/com.eagleeye11.shade-ears.plist`
- **Default state:** `Disabled=true` — does NOT auto-start at login
- **Restart policy:** `KeepAlive=true` — auto-restarts on crash once loaded
- **To activate permanently:** `launchctl load -w ~/Library/LaunchAgents/com.eagleeye11.shade-ears.plist`

---

## Hindsight Memory Architecture

Shade's ambient memory uses a three-tier design to prevent flooding:

```
ears.db (raw, 7-day TTL)
    ↓ shade-ears harvest (filter: >4 words, deduplicate)
    ↓ wake-word rows  → sync_retain verbatim, tag: wake_word (30-day TTL)
    ↓ ambient batches → reflect() → synthesized observation → sync_retain
EagleEye11Shade hindsight bank (synthesis only)
    + pinned rows → sync_retain, tag: pinned (permanent)
```

**Active directive** in hindsight bank (`EagleEye11Shade`, priority 10):
> *Ambient audio transcriptions are environmental context, not episodic memory. Never retain raw ambient transcripts verbatim. During consolidation, synthesize into themes. Pinned items survive all consolidation unchanged. Wake-word items retained verbatim for 30 days.*

---

## Proof of Functionality

### Test 1: Hear → Think (voice → STT → Shade response)
```
$ hear --duration 5 | think
I hear you. Nothing is amiss. What do you need?
```

### Test 2: Wake-word regex — all 7 cases
```
$ python3 -c "[wake-word test suite]"

  PASS: "hey shade can you hear me"
  PASS: "yo shade what up"
  PASS: "shade you there"
  PASS: "shade you hearing this"
  PASS: "HEY SHADE"
  PASS: "okay so what I was saying"  → no false trigger
  PASS: "hey shadow"                 → no false trigger
Wake-word regex: ALL PASS
```

### Test 3: CLI smoke test
```
$ shade-ears status
shade-ears: STOPPED

$ shade-ears harvest --dry-run
No ears.db found — daemon has never run.
```
*(Expected — daemon not yet started. DB created on first run.)*

### Test 4: Import verification
```
$ python3 -c "import json,os,re,signal,sqlite3,subprocess; from faster_whisper import WhisperModel; import sounddevice,numpy; print('All imports OK')"
All imports OK
```

---

## Known Issues & Limitations

### 1. launchctl from Claude Code Sandbox
- `launchctl bootstrap` fails when called from inside Claude Code — sandbox restriction
- **Impact:** `shade-ears start/stop` must be run from a real terminal, not a Claude session
- **Workaround:** Open Terminal, run `shade-ears start`

### 2. Hindsight Harvest Requires Claude Session
- `harvest_ears.py` prepares the payload, but `reflect()` and `sync_retain()` are MCP tools — only callable from within a Claude session
- **Workflow:** Run `shade-ears harvest` in terminal → paste output to Shade → Shade processes to hindsight
- **Future:** SessionStart hook could auto-harvest on session open

### 3. Gemma4 Audio Encoder — Unusable via Ollama (same as Krypton1t3)
- Audio encoder fires correctly (125 tokens from 5s MP3) but `<image>` markers confuse the model
- **Status:** GitHub comment posted on ollama/ollama#11798 under `jkgibson-source` (2026-06-04)
- **Workaround:** STT pipeline (hear.py) — works reliably today

### 4. No VAD (Voice Activity Detection)
- `vad_filter=False` in faster-whisper — known to flag real speech as silence on this hardware
- **Impact:** Silence artifacts may still produce short transcriptions (filtered by 4-word floor in harvest)
- **Future:** Tune VAD once baseline recordings available

---

## Infrastructure Configuration

### Python Virtual Environment
```
~/.claude/PAI/TOOLS/Hearing/.venv/   (Python 3.12)
  sounddevice 0.5.x
  faster-whisper 1.2.1
  scipy
  numpy
```

### Connected Microphones (EagleEye11 Mac)
```
2: SkorpiOm11 Microphone (1 ch)
3: SolSkorp_13 Microphone (1 ch)
5: USB AUDIO CODEC (2 ch)
6: OBSBOT Tiny 2 Lite Microphone (2 ch)
7: Tula Mobile Microphone (2 ch)
9: USB-LCS Audio (1 ch)
```

### Environment
```bash
# Override model
export THINK_MODEL=gemma4:e2b

# Override Ollama host
export OLLAMA_HOST=http://localhost:11434
```

---

## Quick Reference

### Full voice pipeline:
```bash
hear --duration 5 | think
```

### Continuous manual transcription:
```bash
hear --continuous
```

### Use a specific mic:
```bash
hear --device 6 --duration 5 | think    # OBSBOT camera mic
hear --device 7 --duration 5 | think    # Tula Mobile
```

### Start autonomous ears:
```bash
shade-ears start
shade-ears status
shade-ears log 20
shade-ears stop
```

### Pin a transcription you don't want pruned:
```bash
shade-ears log 10           # find the row ID
shade-ears pin <id>
```

### Harvest ambient memory to hindsight (run from Claude session):
```bash
shade-ears harvest --dry-run    # preview
shade-ears harvest              # generate JSON → tell Shade to process it
```

---

## Comparison with Krypton1t3 (Kazm's Node)

| Capability | EagleEye11 (Shade) | Krypton1t3 (Kazm) |
|-----------|---------------------|---------------------|
| STT engine | faster-whisper tiny | faster-whisper base |
| Vision | — (no see.py yet) | see.py → /dev/video0 |
| TTS | Pulse/ElevenLabs | edge-tts RyanNeural |
| Continuous mode | ears_daemon.py | voice-loop.sh |
| Memory integration | harvest_ears.py → hindsight | — |
| Wake-word detection | ✅ 4 phrases | — |
| SQLite logging | ✅ | — |
| Service manager | launchd | systemd |
| Broker connectivity | 0.0.0.0:7899 | Tailscale 100.113.239.38:7899 |

---

## Future Roadmap

| Priority | Feature | Blocker |
|----------|---------|---------|
| P0 | Gemma4 native audio (`audios` field) | ollama/ollama#11798 unmerged |
| P1 | SessionStart auto-harvest hook | Next PAI session |
| P2 | see.py — camera vision pipeline | No camera on this Mac yet |
| P3 | TTS response from daemon on wake word | VoiceServer integration |
| P4 | VAD tuning for silence filtering | Baseline recordings needed |
| P5 | Forge auth (codex login) | One-time OAuth flow pending |

---

*Report written by Shade — 2026-06-04T18:43:23Z. Architecture session with JBird and Kazm (Krypton1t3). All tests confirmed operational.*
