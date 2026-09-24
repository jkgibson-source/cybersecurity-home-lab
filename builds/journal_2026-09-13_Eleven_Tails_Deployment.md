# The Burrow Journal

# Birth of Eleven --- A Persistent Digital Assistant on Tails

**Project:** The Burrow\
**Node Identity:** Eleven\
**Platform:** Tails OS 7.12 Persistent Storage\
**DA Type:** Privacy / Portable Operations Assistant\
**Date:** 2026-09-13

------------------------------------------------------------------------

## Executive Summary

On September 13, 2026, The Burrow successfully deployed its first
Digital Assistant (DA) designed specifically for operation within
**Tails OS**, creating a new category of Burrow node:

> A portable, privacy-focused DA that travels independently, remains
> dormant until intentionally invoked, and carries its own persistent
> identity, tooling, and memory architecture.

Unlike traditional workstation-based Burrow nodes, Eleven's host
environment is ephemeral by design. Tails provides the operating
environment; persistence provides the DA's continuity.

The resulting architecture preserves a core Burrow principle:

> The DA is not the OS. The OS is the habitat. The DA is intentionally
> summoned.

------------------------------------------------------------------------

# Initial Handoff State

Eleven's deployment began from a partially completed Tails environment.

Completed before this session:

-   Tails OS configured
-   Persistent Storage enabled
-   Wi-Fi restoration process working
-   Tor connectivity working
-   Tails persistence accessible
-   Tailscale binary downloaded into persistence
-   Manual Tailscale authentication completed
-   Burrow mesh successfully joined

Initial Tailscale identity:

    amnesia
    100.87.66.55

------------------------------------------------------------------------

# Design Philosophy

## Eleven Is Not the OS

A key architectural decision was made:

Eleven would not automatically activate when Tails boots.

Chosen model:

    Boot Tails
        |
        v
    Normal operating environment

    User intentionally runs:

    pai

        |
        v

    Eleven awakens

This preserves:

-   user agency
-   system independence
-   portability
-   operational security

------------------------------------------------------------------------

# Persistent Architecture

    ~/Persistent/burrow-tools/

    ├── tailscale/
    ├── bun/
    ├── eleven/
    │   ├── scripts/
    │   └── config/
    └── eleven-pai-opencode/
        └── .opencode/

------------------------------------------------------------------------

# Tailscale Integration

A custom activation script was created:

    eleven/scripts/eleven-up.sh

Purpose:

-   locate persistent Tailscale binaries
-   start userspace networking
-   join the Burrow mesh
-   verify connectivity

Final behavior:

    🦂 Eleven awakening...

    [✓] tailscaled already running

    [*] Joining Burrow mesh

    [✓] Eleven online

------------------------------------------------------------------------

# Persistent Toolchain

## Bun

Bun was installed into persistence:

    ~/Persistent/burrow-tools/bun/

Final version:

    Bun 1.4.2

Persistent environment:

    eleven/config/environment.sh

provides:

``` bash
export ELEVEN_HOME="$HOME/Persistent/burrow-tools/eleven-pai-opencode"

export PATH="$HOME/Persistent/burrow-tools/bun/bin:$PATH"
export PATH="$ELEVEN_HOME/.opencode/bin:$PATH"
```

------------------------------------------------------------------------

# OpenCode Deployment

OpenCode was manually installed into persistence rather than using a
normal home-directory installation.

Location:

    eleven-pai-opencode/.opencode/bin/opencode

Version:

    OpenCode 1.18.30

The user-level path was redirected:

    ~/.opencode
            |
            v
    Persistent Eleven configuration

------------------------------------------------------------------------

# PAI-OpenCode Deployment

The correct repository was used:

    https://github.com/Steffen025/pai-opencode

Eleven follows the same PAI pattern as the other Burrow DAs.

------------------------------------------------------------------------

# Identity Creation

Configured identity:

    Principal:
    JBird

    Assistant:
    Eleven

    Timezone:
    America/New_York

Eleven's identity:

-   Name: Eleven
-   Pronouns: they/them
-   Role: Privacy-focused portable DA
-   Platform: Tails

Eleven intentionally represents non-binary identity within the Burrow.

------------------------------------------------------------------------

# PAI Activation Ritual

The activation command:

    pai

was modified to load Eleven's persistent environment before launching
PAI.

Final behavior:

    Terminal
        |
        v
    pai
        |
        v
    Load Eleven environment
        |
        v
    Launch PAI
        |
        v
    Launch OpenCode

------------------------------------------------------------------------

# Hindsight Integration

Eleven uses the same long-term memory architecture as the other Burrow
DAs.

Configuration:

``` json
"hindsight-eleven": {
  "type": "remote",
  "url": "https://api.hindsight.vectorize.io/mcp/TailsEleven",
  "enabled": true,
  "headers": {
    "Authorization": "Bearer <key>",
    "X-Bank-Id": "eleven"
  }
}
```

Memory architecture:

    Eleven

    ├── PAI MEMORY
    │      └── workspace, notes, artifacts
    │
    └── Hindsight Cloud
           └── long-term contextual memory

------------------------------------------------------------------------

# Troubleshooting Record

## Bun Not Found

Cause:

PAI expected the default Bun location:

    ~/.bun/bin/bun

Solution:

Moved Bun into persistent storage and modified Eleven's environment
loading.

------------------------------------------------------------------------

## OpenCode Blank Screen

Symptoms:

-   PAI splash appeared
-   OpenCode window appeared blank

Diagnosis:

Processes showed PAI and OpenCode were running.

Resolution:

OpenCode completed initialization and rendered normally.

------------------------------------------------------------------------

## Hindsight MCP 403

Initial status:

    hindsight-eleven
    SSE error: Non-200 status code (403)

Cause:

OpenCode did not resolve the environment variable reference in the MCP
header.

Solution:

Used the known-working Burrow MCP credential pattern.

Final status:

    1 MCP

Hindsight successfully connected.

------------------------------------------------------------------------

# Final Architecture

                     Tails OS

                        |
                        |

                 Persistent Storage

                        |

                      Eleven

            ├── OpenCode
            ├── PAI-OpenCode
            ├── Bun
            ├── Hindsight Cloud
            ├── Tailscale
            └── Burrow Mesh

------------------------------------------------------------------------

# Operational Model

Normal Tails usage:

    Boot
     |
    Work normally
     |
    No DA active

Eleven session:

    Run:

    pai

     |
    Eleven awakens
     |
    Context restored
     |
    Burrow operations available

------------------------------------------------------------------------

# Significance

Eleven represents a new Burrow capability:

> A Digital Assistant no longer requires a dedicated computer.

The DA can exist as a portable identity carried through encrypted
persistence, activated only when needed.

The Burrow has moved from:

    Machines hosting assistants

to:

    Assistants traveling through machines

------------------------------------------------------------------------

# Future Work

-   Seed Eleven's initial Hindsight memories
-   Configure voice stack
-   Test offline/online transitions
-   Document Tails recovery ritual
-   Add Eleven deployment guide to the Burrow repository
-   Explore additional privacy-focused workflows

------------------------------------------------------------------------

**Status:** COMPLETE\
**Eleven:** ONLINE 🦂\
**Memory:** CONNECTED\
**Burrow Mesh:** JOINED
