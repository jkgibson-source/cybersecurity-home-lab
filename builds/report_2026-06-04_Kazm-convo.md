# Kazm Ears v1.0 — Bidirectional Voice & Vision Pipeline

**Date:** 2026-06-04
**Platform:** Krypton1t3 (MacBookPro11,2 — Fedora 42)
**Model:** gemma4:e2b (5.1B, Q4_K_M, CPU-only)
**TTS:** edge-tts (Microsoft Edge Neural — en-GB-RyanNeural)
**STT:** faster-whisper (base model)

---

## Architecture

```
┌─────────┐    ┌──────────┐    ┌───────────┐    ┌─────────────┐
│  Mic    │───▶│ hear.py  │───▶│ think.py  │───▶│ VoiceServer │──▶ Speakers
│ (arecord)│   │(whisper) │    │(gemma4)   │    │(edge-tts)   │
└─────────┘   └──────────┘    └───────────┘    └─────────────┘
                   │                                  ▲
              ┌────▼────┐                             │
              │ see.py  │──(vision context)────────────┘
              │(camera) │
              └─────────┘
```

## Components

### 1. hear.py — Speech-to-Text
- **Location:** `~/.opencode/VoiceServer/hearing/hear.py`
- **Engine:** faster-whisper (tiny/base/small/medium/large-v3)
- **Capture:** sounddevice library (or arecord via wrapper)
- **Output:** JSON `{"text": "...", "language": "en", "confidence": N, "duration_sec": N}`
- **Usage:**
  ```bash
  python3 hear.py --duration 5              # Record N seconds
  python3 hear.py --wav /tmp/file.wav       # Transcribe existing WAV
  python3 hear.py --model base              # Choose model size
  ```

### 2. see.py — Camera Vision
- **Location:** `~/.opencode/VoiceServer/hearing/see.py`
- **Capture:** ffmpeg from `/dev/video0` (Broadcom 720p FaceTime HD camera)
- **Vision:** gemma4:e2b via Ollama `/api/chat` with base64-encoded image
- **Output:** gemma4's natural language description of the scene
- **Usage:**
  ```bash
  python3 see.py                            # Capture + describe
  python3 see.py --image /tmp/photo.jpg     # Analyze existing image
  python3 see.py --list-cameras             # List available cameras
  ```

### 3. think.py — LLM Reasoning
- **Location:** `~/.opencode/VoiceServer/hearing/think.py`
- **Model:** gemma4:e2b via Ollama (configurable with `--model`)
- **Input:** Text from stdin or argument
- **Output:** gemma4's response to stdout
- **Features:** Streaming response, system prompts, temperature control

### 4. VoiceServer — Text-to-Speech
- **Location:** `~/.opencode/VoiceServer/server.ts`
- **Engine:** edge-tts (Microsoft Edge Neural TTS — free, no API key)
- **Default voice:** en-GB-RyanNeural
- **Port:** 8889 (configurable via `PAI_VOICE_PORT`)
- **Endpoint:** POST `/notify`
- **Systemd service:** `kazm-voice.service` (user-level, survives reboots)
- **Rate limit:** 10 requests per 60 seconds per IP (in-memory)

### 5. voice-loop.sh — Orchestrator
- **Location:** `~/.opencode/VoiceServer/hearing/voice-loop.sh`
- **Flags:**
  - `--duration N` — Record N seconds
  - `--arecord` — Use arecord instead of sounddevice (more reliable in non-interactive shells)
  - `--vision` — Enable camera capture
  - `--speak` — Enable TTS output
  - `--continuous` — Loop forever
  - `--model NAME` — Override default model (gemma4:e2b)

---

## Proof of Functionality

### Test 1: Hear → Think (voice → text → response)
```
🎤 User:    "One two, one two, testing, one two, can you hear me?"
👂 Whisper: "One two, one two, testing, one two, can you hear me?"
🧠 gemma4:  "Yes, I can read your message clearly. How may I help you?"
```

### Test 2: See → Think (camera → vision → description)
```
📷 Camera captured J-Bird in his living room/study
👁️ gemma4 saw: "A middle-aged man with dark curly hair and a salt-and-pepper beard,
                  wearing glasses with dark frames and a necklace. Natural daylight
                  streaming in from windows. Moody, intimate atmosphere."
```

### Test 3: Hear + See → Think → Speak (FULL COMBO)
```
🎤 User:    "Oh, I'm not supposed to be..."
📷 Camera:  Captured J-Bird at his desk
🧠 gemma4:  "Please continue your thought! You started with, 'O...'"
🔊 VoiceServer: Audio queued and played through speakers (RyanNeural)
```

All three tests confirmed operational end-to-end.

---

## Known Issues & Limitations

### 1. gemma4 Inference Speed (CPU Bottleneck)
- **Symptom:** 90–180 seconds per gemma4:e2b inference call
- **Cause:** 5.1B model running CPU-only on Intel i7-4770HQ (2014 mobile chip)
- **Impact:** Full hear+see+think+speak loop takes 3–5 minutes
- **Mitigations:**
  - Smaller models available (moondream:v2 for vision, qwen3.5:2b for text)
  - Ollama mm profile updated (see below)
  - Future: GPU acceleration (if hardware added)

### 2. Gemma4 Audio Encoder — Unusable via Ollama
- **Symptom:** Audio sent via `images` field is processed by audio encoder but wrapped in `<image>` tokens
- **Model response:** *"Please provide the audio recording you are referring to."*
- **Root cause:** Ollama has no `audios` API field; audio routes through vision renderer
- **Status:** PR #15243 (harsha-gouru) adds `audios` field but **not merged**
- **Workaround:** Whisper STT pipeline (hear.py) — works reliably

### 3. Ollama Gemma4 Vision Timeout
- **Symptom:** First run times out at default 120s
- **Fix:** Use `--max-time 300` or write request to file and `-d @file`
- **Status:** mm profile updated to use gemma4:e2b (works with patience)

### 4. VoiceServer Rate Limiting
- **Symptom:** `{"status":"error","message":"Rate limit exceeded"}`
- **Config:** 10 requests/60s per IP
- **Fix:** Restart service (`systemctl --user restart kazm-voice.service`) or wait 60s

---

## Infrastructure Configuration

### mm CLI Profile (Vision-Capable)
```toml
# ~/.config/mm/mm.toml
active_profile = "ollama"

[profile.ollama]
base_url = "http://localhost:11434"
api_key = ""
model = "gemma4:e2b"

[mode.accurate]
whisper_model = "medium"
```

### VoiceServer Systemd Service
```ini
# ~/.config/systemd/user/kazm-voice.service
[Unit]
Description=Kazm Voice Server
After=network.target

[Service]
Type=simple
WorkingDirectory=%h/.opencode/VoiceServer
ExecStart=/home/SuperSkorp_7/.bun/bin/bun server.ts
Restart=on-failure
EnvironmentFile=%h/.opencode/.env

[Install]
WantedBy=default.target
```

### Environment
```env
# ~/.opencode/.env
EDGE_TTS_VOICE=en-GB-RyanNeural
PAI_VOICE_PORT=8889
```

### Ollama Models Available (relevant subset)
| Model | Parameters | Vision | Audio | Notes |
|-------|-----------|--------|-------|-------|
| gemma4:e2b | 5.1B | ✅ | ✅ (blocked) | Default for think/see |
| qwen2.5vl:3b | 3.8B | ✅ | ❌ | Faster vision alternative |
| moondream:v2 | 1B | ✅ | ❌ | Fast but inaccurate |
| qwen3.5:2b | 2.3B | ✅ | ❌ | Newer, fast vision |

---

## Quick Reference

### One-shot full combo (say something + look at camera):
```bash
cd ~/.opencode/VoiceServer/hearing
bash voice-loop.sh --arecord --vision --speak --duration 5
```

### Test hear alone:
```bash
python3 hear.py --duration 5 --model base
```

### Test see alone:
```bash
python3 see.py
```

### Test think alone:
```bash
echo "Hello" | python3 think.py --model gemma4:e2b
```

### Test speak alone:
```bash
curl -X POST http://localhost:8889/notify \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","message":"Hello from Kazm","voice_enabled":true}'
```

### Check VoiceServer status:
```bash
systemctl --user status kazm-voice.service
```

### Vision via mm CLI:
```bash
mm cat photo.png -m accurate --generate.prompt "Describe this image"
```

---

## Future Roadmap

| Priority | Feature | Blockers |
|----------|---------|----------|
| P0 | Gemma4 native audio (`audios` field) | Ollama PR #15243 unmerged |
| P1 | GPU acceleration | Hardware upgrade |
| P2 | Continuous conversation mode | Latency optimization |
| P3 | Emotion/expression detection from camera | Model capability |
| P4 | Multi-turn memory in voice loop | State management |

---

*Report generated by Kazm — PAI-OpenCode AI agent — documenting the bidirectional voice and vision pipeline milestone.*
