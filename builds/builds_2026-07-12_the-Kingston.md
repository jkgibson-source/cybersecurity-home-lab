# The Kingston — Build Log 2026-07-12

**Project:** The Kingston (formerly BMV — Burrow Model Vault)  
**Date:** 2026-07-12  
**Author:** Kazm (with J-Bird / JBird)  
**Target:** Portable AI model vault on Kingston USB (exFAT, GPT) for the Burrow mesh

---

## Executive Summary

Built a portable, cross-platform AI model vault running llama.cpp on a Kingston USB stick. Supports **4 platforms** (Linux x86_64, macOS ARM64, macOS x86_64, Windows x86_64) with a unified CLI (`bmv`), capability presets instead of DA personae, and a Kingston concierge TUI. 5 GGUF models deployed (4 complete, 1 paused).

---

## Phase 0: Origin — The Original BMV Spec

**Source:** `/The Burrow/Markdown Files/Burrow_Model_Vault_Kazm_Prompt.md`

Original vision (pre-correction):
- **BMV** = Burrow Model Vault
- **7 DA profiles** (Kazm, Echo, Shade, Omega, Splice, Flex, Spec) — each DA got a tailored system prompt, model prefs, context size, temperature
- Path A: Direct human chat through BMV TUI
- Path B: DA tool calls returning structured results
- Host profiles per Burrow node (Krypton1t3, Jynx13, EagleEye11, SkorpiOm, SpliceStick, FlexStick, SpecStick)
- 4 target models: `gemma4:e4b`, `gemma4:12b`, `WhiteRabbitNeo-2.5-Qwen-2.5-Coder-7B`, `llama3.2:3b`
- 8 dev phases: Discovery → Design → MVP → Krypton1t3 Validation → Linux Portability → macOS Validation → Windows Validation → v1.0

---

## Phase 1: The Architectural Correction — DA Council Mandate

**Date:** 2026-07-12  
**Document:** `DA_Council/Kazm/build_2026-07-12_the-Kingston.md`

**The Correction:**
> **No generic LLM may impersonate, simulate, substitute for, or wear the identity of a DA.**

This was the watershed moment. The 7 DA profiles were **architecturally invalid** — they let a generic LLM "pretend" to be a DA. The DA Council rejected this entirely.

**The Correction:**
- **BMV renamed → "The Kingston"** (a concierge/librarian, never claims to be a DA)
- **7 DA profiles DELETED** (`profiles/da/` removed, `da.ts` command removed)
- **11 Capability Presets CREATED** — pure task profiles, no identity claims:
  1. `general` — balanced conversation
  2. `lightweight` — minimal resources
  3. `vision-analysis` — image/video understanding
  4. `screenshot-analysis` — UI/desktop analysis
  5. `document-analysis` — PDF/text extraction
  6. `code-review` — security, correctness, style
  7. `security-research` — threat modeling, vuln analysis
  8. `creative-writing` — fiction, poetry, narrative
  9. `brainstorming` — ideation, lateral thinking
  10. `structured-extraction` — JSON/CSV/schema extraction
  11. `troubleshooting` — debugging, root cause
- **Kingston Interface Files:**
  - `interface/kingston.toml` — identity config
  - `interface/concierge-prompt.md` — system prompt (explicit: "I am the Kingston, a concierge/librarian")
  - `interface/messages/` — 5 templates (welcome, model-selected, insufficient-memory, checksum-failure, session-closed)

**Migration Path:** Legacy `active-da.json` → auto-migrates to nearest preset (Kazm→general, Shade→security-research, Echo→vision-analysis, etc.)

---

## Phase 2: llama.cpp Build — Linux (Krypton1t3)

**Host:** Krypton1t3 (Intel i7-4770HQ, 15GB RAM, Fedora Linux)

```bash
# Build llama.cpp from source
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
mkdir build && cd build
cmake .. -DLLAMA_BUILD_SERVER=ON -DLLAMA_BUILD_EXAMPLES=OFF -DLLAMA_BUILD_TESTS=OFF -DBUILD_SHARED_LIBS=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release --target llama-server -j$(nproc)

# Result: runtimes/linux-x86_64/llama-server (16.6 MB ELF x86-64)
```

**Verified:** `llama-server --version` → `version: 1 (6b4dc21)`

---

## Phase 3: BMV CLI Build — Linux (Ink + React TUI)

**Stack:** Bun, TypeScript, Ink 7.1.0, React 19

```bash
bun add ink react react-devtools-core
bun build src/main.ts --compile --target=bun-linux-x64 --outfile=bmv
```

**Result:** `bmv` (1.9 MB Linux ELF)

**Symlink for global access:**
```bash
ln -sf /home/SuperSkorp_7/BMV/bmv ~/.local/bin/bmv
```

---

## Phase 4: Architectural Refactor — Presets Replace DA Profiles

**Files Modified:**
- `src/lib/profiles.ts` — new Preset type, TOML parser, active preset state, `applyPreset()`, `recommendedModel()`
- `src/commands/start.ts` — applies active preset on server start
- `src/commands/chat.ts` — **system prompt now uses `preset.task_instructions`**, temperature from preset
- `src/commands/preset.ts` — list/show/activate/clear presets
- `src/commands/start.ts` / `status.ts` — updated for "The Kingston" branding

**Chat Command Now:**
- Reads active preset → uses `task_instructions` as system prompt
- Applies `preset.defaults.temperature` to API calls
- `/preset` command in chat to switch modes mid-conversation
- Banner shows active preset + temperature

---

## Phase 5: Kingston Concierge TUI (Ink + React)

**Built:** `src/tui/kingston.tsx` → `src/commands/kingston.tsx`

**Features:**
- Double-bordered header: "THE KINGSTON — Burrow Model Vault"
- Live status: model, runtime, port, preset, temperature
- 8-item keyboard-navigable menu:
  1. Start Server
  2. Chat
  3. Presets
  4. Models
  5. Status
  6. Config
  7. Diagnostics
  8. Exit
- Diagnostics view: disk, memory, runtime health, active model

**Command:** `bmv kingston` (requires TTY)

---

## Phase 6: Cross-Compilation — macOS (The Hard Part)

### Problem
Cross-compiling llama.cpp for macOS from Linux **requires macOS SDK** (Metal headers, Mach-O linker, libSystem). Not feasible on Linux without osxcross + Apple SDK (legally complex).

### Solution: Build ON Mac Hardware

**Jynx13** — Intel Mac (x86_64, macOS 12.7.6, "Echo's host")  
**EagleEye11** — Apple Silicon Mac (ARM64, macOS 26.5.2 "Tahoe", "Shade's host")

### SSH Setup
```bash
# Krypton1t3 generates ed25519 key
ssh-keygen -t ed25519 -f ~/.ssh/krypton1t3_burrow -N "" -C "krypton1t3@burrow"

# Add to ~/.ssh/config
Host jynx13
  HostName 100.108.182.39
  User jbird13
  IdentityFile ~/.ssh/krypton1t3_burrow
  IdentitiesOnly yes

Host eagleeye11
  HostName 100.113.239.38
  User EagleEye11
  IdentityFile ~/.ssh/krypton1t3_burrow
  IdentitiesOnly yes
```

**J-Bird manually added public key to both Macs' `~/.ssh/authorized_keys`**

### Jynx13 (x86_64) — Intel Mac
```bash
ssh jynx13
# Install cmake via Homebrew
brew install cmake
# Build
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp && mkdir build && cd build
cmake .. -DLLAMA_BUILD_SERVER=ON -DLLAMA_BUILD_EXAMPLES=OFF -DLLAMA_BUILD_TESTS=OFF -DBUILD_SHARED_LIBS=OFF -DCMAKE_BUILD_TYPE=Release -DGGML_METAL=ON
cmake --build . --config Release -j$(sysctl -n hw.ncpu) --target llama-server
```
**Result:** `llama-server` (17.4 MB Mach-O x86_64, Metal enabled)

### EagleEye11 (ARM64) — Apple Silicon
```bash
ssh eagleeye11
# No cmake, no Homebrew → downloaded static cmake binary
curl -L "https://github.com/Kitware/CMake/releases/download/v4.3.0/cmake-4.3.0-macos-universal.tar.gz" -o /tmp/cmake.tar.gz
tar -xzf /tmp/cmake.tar.gz -C /tmp/
export PATH="/tmp/cmake-4.3.0-macos-universal/CMake.app/Contents/bin:$PATH"
# Build
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp && mkdir build && cd build
export PATH="/tmp/cmake-4.3.0-macos-universal/CMake.app/Contents/bin:$PATH"
cmake .. -DLLAMA_BUILD_SERVER=ON -DLLAMA_BUILD_EXAMPLES=OFF -DLLAMA_BUILD_TESTS=OFF -DBUILD_SHARED_LIBS=OFF -DCMAKE_BUILD_TYPE=Release -DGGML_METAL=ON
cmake --build . --config Release -j$(sysctl -n hw.ncpu) --target llama-server
```
**Result:** `llama-server` (15.5 MB Mach-O ARM64, Metal enabled)

### Pulled to Kingston
```
runtimes/darwin-x86_64/llama-server  (17.4 MB, Mach-O x86_64)
runtimes/darwin-arm64/llama-server   (15.5 MB, Mach-O arm64)
```

---

## Phase 7: Windows — The Oriel Saga

### Problem
No Windows build environment on Krypton1t3. Cross-compile with mingw64 failed (CMake generator mismatch, missing OpenSSL, NMake issues).

### Oriel (WinToGo on USB) — Physical Access
**Host:** Oriel (Windows 10 Pro, "Spec's host") — Tailscale IP `100.114.10.94` ("oriel-spec-hopper")

### The Pivot: Download Pre-built Binary
Instead of fighting mingw64/CMake on Linux, downloaded official release on Oriel:

```powershell
# On Oriel (PowerShell as Admin)
$url = "https://github.com/ggml-org/llama.cpp/releases/download/b9977/llama-b9977-bin-win-cpu-x64.zip"
$zip = "C:\llama-cpu.zip"
$dest = "C:\llama-win"
Invoke-WebRequest -Uri $url -OutFile $zip
Expand-Archive -Path $zip -DestinationPath $dest -Force
Copy-Item "$dest\llama-server.exe" "K:\runtimes\windows-x86_64\llama-server.exe" -Force
```
*(K: = Kingston drive letter on Oriel)*

**Result:** `runtimes/windows-x86_64/llama-server.exe` (PE32+ x86-64, stub + `llama-server-impl.dll` + all CPU variant DLLs)

**Also built BMV CLI for Windows on Krypton1t3:**
```bash
bun build src/main.ts --compile --target=bun-windows-x64 --outfile=bmv.exe
```
Deployed to `KingstonBMV/bmv-windows.exe` (PE32+ x86-64)

---

## Phase 8: Kingston USB Preparation

**Drive:** Kingston USB (115 GB exFAT, GPT, label `KingstonBMV`)

**Structure:**
```
KingstonBMV/
├── bmv                          # Linux CLI (symlink target)
├── bmv-darwin-x64               # macOS x86_64 CLI
├── bmv-darwin-arm64             # macOS ARM64 CLI
├── bmv-windows.exe              # Windows CLI
├── config/                      # Host configs (created by bmv install)
├── interface/
│   ├── kingston.toml
│   ├── concierge-prompt.md
│   └── messages/ (5 templates)
├── models/
│   ├── llama-3.2-3b-instruct-q4_k_m.gguf        (1.7 GB)
│   ├── phi-4-mini-instruct-q4_k_m.gguf           (2.0 GB)
│   ├── gemma-4-e4b-it-q4_k_m.gguf                (4.7 GB)
│   ├── white-rabbit-neo-2.5-qwen-2.5-coder-7b-q4_k_m.gguf  (4.4 GB)
│   └── gemma-4-12b-it-q4_k_m.gguf                (0.7 GB / ~7.5 GB, paused)
├── presets/ (11 TOML files)
├── runtimes/
│   ├── linux-x86_64/llama-server        (16.6 MB ELF)
│   ├── darwin-x86_64/llama-server       (17.4 MB Mach-O x86_64)
│   ├── darwin-arm64/llama-server        (15.5 MB Mach-O arm64)
│   └── windows-x86_64/
│       ├── llama-server.exe             (9 KB stub)
│       ├── llama-server-impl.dll        (9.2 MB)
│       ├── ggml.dll + 14 CPU variant DLLs
│       ├── llama.dll, llama-common.dll, etc.
│       └── libomp140.x86_64.dll
└── presets/ (11 TOML files)
```

---

## Phase 9: Model Downloads (All via wget with resume)

| Model | Source | Size | Status |
|-------|--------|------|--------|
| `llama-3.2-3b-instruct-q4_k_m.gguf` | bartowski/Llama-3.2-3B-Instruct-GGUF | 1.7 GB | ✅ |
| `phi-4-mini-instruct-q4_k_m.gguf` | unsloth/Phi-4-mini-instruct-GGUF | 2.0 GB | ✅ |
| `gemma-4-e4b-it-q4_k_m.gguf` | unsloth/gemma-4-E4B-it-GGUF | 4.7 GB | ✅ |
| `white-rabbit-neo-2.5-qwen-2.5-coder-7b-q4_k_m.gguf` | bartowski/WhiteRabbitNeo-2.5-Qwen-2.5-Coder-7B-GGUF | 4.4 GB | ✅ |
| `gemma-4-12b-it-q4_k_m.gguf` | unsloth/gemma-4-12b-it-GGUF | ~7.5 GB | ⏸️ Paused (0.7/7.5 GB) |

**Download Tool:** `wget -c` (resume support, handles 416 Range errors gracefully)

---

## Phase 10: BMV CLI Rebuilds for All Platforms

```bash
# Linux (Krypton1t3)
bun build src/main.ts --compile --target=bun-linux-x64 --outfile=bmv

# macOS x86_64
bun build src/main.ts --compile --target=bun-darwin-x64 --outfile=bmv-darwin-x64

# macOS ARM64
bun build src/main.ts --compile --target=bun-darwin-arm64 --outfile=bmv-darwin-arm64

# Windows
bun build src/main.ts --compile --target=bun-windows-x64 --outfile=bmv.exe
```

All deployed to Kingston root + platform runtime dirs.

---

## Phase 10.5: Critical Fix — `vaultRoot()` Detection

**Bug:** `bmv` only worked from `/home/SuperSkorp_7/BMV` because `vaultRoot()` used `process.cwd()`

**Fix in `src/lib/platform.ts`:**
```typescript
export function vaultRoot(): string {
  const devRoot = process.env.BMV_ROOT;
  if (devRoot) return devRoot;

  const path = require("path");
  const execDir = path.dirname(process.execPath);  // Binary location!
  if (execDir && execDir !== "." && execDir !== "/") {
    const fs = require("fs");
    if (fs.existsSync(path.join(execDir, "runtimes")) ||
        fs.existsSync(path.join(execDir, "models")) ||
        fs.existsSync(path.join(execDir, "presets"))) {
      return execDir;
    }
  }
  return process.cwd();
}
```

Now `bmv` works from **any directory** via symlink.

---

## Model Registry & Preset Configs

### 11 Presets (`presets/*.toml`)
Each defines: `task_instructions` (system prompt), `defaults` (model, context, temp, threads, ngl, flash_attn), `multimodal`, `resource` requirements.

Example (`code-review.toml`):
```toml
[preset]
name = "Code Review"
description = "Analyze code for quality, security, and correctness"
task_instructions = "You are a code review assistant. Analyze code carefully for bugs, security issues, performance problems, and maintainability concerns. Provide specific, actionable feedback with line references where possible. Be thorough but focused on real issues, not style preferences."

[defaults]
preferred_model = "WhiteRabbitNeo-2.5-Qwen-2.5-Coder-7B"
fallback_model = "llama3.2:3b"
context_size = 8192
temperature = 0.3
threads = 4
ngl = 0
flash_attn = false

[resource]
min_ram_gb = 4
recommended_ram_gb = 8
```

---

## Testing Matrix (Planned)

| Platform | Host | Runtime | BMV Binary | Status |
|----------|------|---------|------------|--------|
| Linux x86_64 | Krypton1t3 (Kazm) | ✅ | ✅ `bmv` | Ready |
| macOS x86_64 | Jynx13 (Echo) | ✅ | ✅ `bmv-darwin-x64` | Untested |
| macOS ARM64 | EagleEye11 (Shade) | ✅ | ✅ `bmv-darwin-arm64` | Untested |
| Windows x64 | Oriel (Spec) | ✅ | ✅ `bmv-windows.exe` | Untested |
| Linux x86_64 | SkorpiOm (Omega) | ✅ | Shared `bmv` | Ready |
| Linux x86_64 | SpliceStick (Splice) | ✅ | Shared `bmv` | Ready |
| Linux x86_64 | FlexStick (Flex) | ✅ | Shared `bmv` | Ready |

**Test Flow per Node:**
```bash
# Plug Kingston, cd to mount point
./bmv install        # Creates host config, verifies runtime
./bmv preset use general
./bmv start          # Launches llama-server with active preset
./bmv chat           # Opens Kingston concierge TUI
```

---

## Key Decisions & Lessons

| Decision | Rationale |
|----------|-----------|
| **Presets over DA profiles** | DA Council mandate: no LLM impersonation |
| **Kingston = concierge, not DA** | Explicit in system prompt: "I am the Kingston, a concierge" |
| **Build on target hardware (macOS)** | Cross-compile from Linux → macOS requires Apple SDK (legal/technical blocker) |
| **Windows: download pre-built** | mingw64 cross-compile from Linux is broken (CMake generators, OpenSSL, NMake) |
| **exFAT + GPT for Kingston** | Cross-platform R/W (Linux, macOS, Windows), >4GB file support |
| `vaultRoot()` via `process.execPath` | Binary works from anywhere via symlink |
| `wget -c` for downloads | Resume support, handles CDN 416 errors, faster than `hf download` |
| Presets drive chat system prompt | `chat.ts` now uses `preset.task_instructions` + `preset.defaults.temperature` |

---

## Open Items

1. **gemma4:12b** — 742 MB / ~7.5 GB (paused, resume later)
2. **Physical testing** on Jynx13, EagleEye11, Oriel, SkorpiOm
3. **Windows launcher scripts** (`.bat` / `.ps1`) for non-technical users
4. **Model registry** — register downloaded GGUFs with `bmv` registry
5. **SpecStick backup verification** — Kingston was SpecStick backup target

---

## Files Created/Modified

### New
- `builds_2026-07-12_the-Kingston.md` (this file)
- `interface/kingston.toml`
- `interface/concierge-prompt.md`
- `interface/messages/{welcome,model-selected,insufficient-memory,checksum-failure,session-closed}.md`
- `presets/{general,lightweight,vision-analysis,screenshot-analysis,document-analysis,code-review,security-research,creative-writing,brainstorming,structured-extraction,troubleshooting}.toml`
- `src/tui/kingston.tsx`
- `src/commands/kingston.tsx`
- `src/commands/preset.ts`

### Modified
- `src/main.ts` — added `kingston` command
- `src/lib/profiles.ts` — complete rewrite (Preset system, DA migration)
- `src/commands/start.ts` — applies preset, shows preset info
- `src/commands/chat.ts` — preset system prompt + temperature, `/preset` command
- `src/commands/status.ts` — "The Kingston" branding
- `src/lib/platform.ts` — `vaultRoot()` fix
- `package.json` — added `ink`, `react`, `react-devtools-core`, build scripts

### Deleted
- `profiles/da/` (7 DA profiles)
- `src/commands/da.ts`

---

## Burrow Mesh Readiness

**Kingston is a deployable portable vault.** Plug into any Burrow node:

| Node | Arch | Action |
|------|------|--------|
| Krypton1t3 | linux-x86_64 | `bmv install` → `bmv start` → `bmv chat` |
| Jynx13 | darwin-x86_64 | `./bmv-darwin-x64 install` → `start` → `chat` |
| EagleEye11 | darwin-arm64 | `./bmv-darwin-arm64 install` → `start` → `chat` |
| Oriel | windows-x86_64 | `bmv-windows.exe install` → `start` → `chat` |
| SkorpiOm/SpliceStick/FlexStick | linux-x86_64 | Shared `bmv` binary |

**DA Council mandate satisfied:** Kingston is a tool, not a person. No impersonation. Pure utility.

---

**End of Build Log — 2026-07-12**