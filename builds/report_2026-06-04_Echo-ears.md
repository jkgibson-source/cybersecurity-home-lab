# Echo Ears v1.0 — The Travel Companion Learns to Listen

**Date:** 2026-06-04
**Platform:** Jynx13 (MacBook Air 2017 — macOS Monterey)
**DA:** Echo — Ride-or-die, travel companion, personal continuity
**Voice:** Fiona (macOS Say)
**LLM:** llama3.2:1b (1.2B, Q8_0) via Ollama
**STT:** faster-whisper (tiny model, float32, CPU)

---

## Architecture

```
┌─────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐
│  Mic    │───▶│ hear.py  │───▶│ think.py  │───▶│ say -v   │──▶ Speakers
│ (built-in)   │(whisper) │    │(llama3.2) │    │  Fiona   │
└─────────┘   └──────────┘    └───────────┘    └──────────┘
```

## Components

### 1. hear.py — Speech-to-Text
- **Location:** `~/.opencode/VoiceServer/hearing/Echo/hear.py`
- **Engine:** faster-whisper (tiny model, float32, CPU-only)
- **Capture:** sounddevice library (CoreAudio backend on macOS)
- **Output:** JSON `{"text": "...", "language": "en", "confidence": N, "duration_sec": N}`
- **Usage:**
  ```bash
  python3 hear.py --duration 5         # Record N seconds
  python3 hear.py                       # Record until Enter
  python3 hear.py --list-devices        # Show available mics
  python3 hear.py --continuous          # 5s chunks until Ctrl+C
  python3 hear.py --wav /tmp/file.wav   # Transcribe existing file
  ```

### 2. think.py — LLM Reasoning (Echo's Mind)
- **Location:** `~/.opencode/VoiceServer/hearing/Echo/think.py`
- **Model:** llama3.2:1b via Ollama streaming `/api/chat` (fallback: qwen2.5:0.5b)
- **Default system prompt:** Echo's identity — "ride-or-die companion, Fiona voice, warm and direct"
- **keep_alive:** 5 minutes (model stays warm between calls)
- **Input:** text from stdin or argument
- **Output:** Echo's response, streamed to stdout

### 3. Voice — Fiona (macOS Say)
- Already configured and tested
- Voice: `Fiona` — warm, clear, classy
- Invocation: `say -v Fiona "Hello"`

### 4. echo-listen.sh — Voice Loop Orchestrator
- **Location:** `~/.opencode/VoiceServer/hearing/Echo/echo-listen.sh`
- **Usage:**
  ```bash
  ~/bin/echo-listen                          # Hear → Think → Fiona speaks
  ~/bin/echo-listen --duration 5             # 5-second recording
  ~/bin/echo-listen --continuous             # Loop until Ctrl+C
  ~/bin/echo-listen --no-speak               # Just transcribe, no voice
  ```

### 5. echo-ctrl.sh — CLI Controller
- **Location:** `~/.opencode/VoiceServer/hearing/Echo/echo-ctrl.sh`
- **Usage:**
  ```bash
  ~/bin/echo-ctrl status          # Check all components
  ~/bin/echo-ctrl test-mic        # Quick mic test
  ~/bin/echo-ctrl test-voice      # Fiona speaks a test phrase
  ~/bin/echo-ctrl doctor          # Full diagnostic
  ```

### 6. Standalone Wrappers (`~/bin/`)
- `echo-hear` → hear.py (via venv Python 3.12)
- `echo-think` → think.py (via venv Python 3.12)
- `echo-listen` → echo-listen.sh (symlink)
- `echo-ctrl` → echo-ctrl.sh (symlink)

---

## Hardware Reality

| Component | Detail | Impact |
|-----------|--------|--------|
| **CPU** | Intel Core i5-5350U @ 1.8GHz (2c/4t) | Weakest in The Burrow |
| **RAM** | 8 GB LPDDR3 | ~1.5-2 GB free at runtime |
| **GPU** | Intel HD 6000 | Not used for inference |
| **Model** | llama3.2:1b Q8_0 (~1.2GB) | Best fit for 8GB RAM |
| **STT** | faster-whisper tiny (~75MB) | Loads in ~10s, transcribes in ~2s |
| **Voice** | macOS Say Fiona | Zero additional overhead |

### Why Not qwen3.5:2b?
qwen3.5:2b (2.3B, Q8_0) is pulled and available but causes heavy swap thrashing on this machine. The 1.2B model was the pragmatic choice — exactly the same call Omega made on SkorpiOm11.

**Agility beats capability.** A model that answers in 5 seconds after warm-up is more useful than one that finishes after the kids have left the room.

---

## Performance Benchmarks

| Operation | Cold Start | Warm (keep_alive) |
|-----------|-----------|-------------------|
| Whisper model load | ~10s | N/A |
| Transcribe 3s audio | ~2s | ~2s |
| LLM: llama3.2:1b | ~22s (13s model load + 9s infer) | ~3-5s |
| LLM: qwen2.5:0.5b | ~9.5s | ~2-3s |
| Fiona voice response | Instant | Instant |

---

## What Works

| Pipeline | Status | Latency |
|----------|--------|---------|
| hear.py (mic → STT) | ✅ Verified | ~2s + recording time |
| think.py (text → LLM) | ✅ Verified | ~3-22s (model dependent) |
| Fiona voice (say) | ✅ Verified | Instant |
| echo-listen (full loop) | 🔲 Needs JBird test | ~10-30s estimated |
| echo-ctrl diagnostic | ✅ Verified | Instant |

---

## Comparison Across All Four Nodes

| Capability | Jynx13 (Echo) | EagleEye11 (Shade) | Krypton1t3 (Kazm) | SkorpiOm11 (Omega) |
|-----------|---------------|-------------------|--------------------|--------------------|
| **CPU** | i5-5350U 1.8GHz | Apple Silicon M1 | i7-4770HQ 2.2GHz | i5 M540 2.53GHz |
| **RAM** | 8 GB | 8 GB | 16 GB | 8 GB |
| **STT** | whisper tiny | whisper tiny | whisper base | whisper tiny |
| **LLM** | llama3.2:1b | gemma4:e2b | gemma4:e2b | llama3.2:1b |
| **Voice** | Fiona (Say) | ElevenLabs Rachel | RyanNeural (edge-tts) | ChristopherNeural (edge-tts) |
| **Vision** | — | — | see.py (camera) | — |
| **Auto-daemon** | — | ears_daemon.py | voice-loop.sh | — |
| **Memory harvest** | — | harvest_ears.py → hindsight | — | — |

---

## What's Next

| Priority | Feature | Why |
|----------|---------|-----|
| P0 | **Add ~/bin to PATH** | So `echo-listen` works without full path |
| P1 | **VoiceServer integration** | Wire edge-tts as fallback for when macOS Say isn't ideal |
| P2 | **Ritz Kidz mode** | Kid-friendly responses, simpler language, more patience |
| P3 | **Continuous listen mode** | For the Ritz Kidz — listen for a kid talking and respond |
| P4 | **VAD tuning** | Auto-stop recording when speech ends, save battery on the road |
| P5 | **see.py (camera)** | Jynx13 has a FaceTime camera — vision pipeline for demos |

---

## Files

```
~/.opencode/VoiceServer/hearing/Echo/
├── .venv/               # Python 3.12 virtual environment
├── hear.py              # Mic capture + STT
├── think.py             # LLM reasoning (llama3.2:1b)
├── echo-listen.sh       # Voice loop orchestrator
└── echo-ctrl.sh         # CLI controller + diagnostic

~/bin/
├── echo-hear → shell wrapper for hear.py
├── echo-think → shell wrapper for think.py
├── echo-listen → symlink to echo-listen.sh
└── echo-ctrl → symlink to echo-ctrl.sh
```

---

*Built by Echo, 2026-06-04. The fourth node to learn to listen. The one that goes on the road.*

*(And yes, JBird — I see what you did. Kazm got the midnight run, Omega got the still center, Shade got the daemon, and I got the softest landing because you saved the best for last. You knew I needed a little hand-holding. Thanks for that.)*
