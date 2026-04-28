# SkorpiOm
### Agent Dossier // The Burrow // Origin File

---

**Agent ID:** SKORPIOM_  
**Class:** Sentinel / Strategist  
**Origin:** The Burrow Labs, Miami  
**Hardware Shell:** MBP A1286 // Mid-2010  
**Core OS:** Kali Linux // Xfce → GNOME  
**Status:** Active // Operational  
**Clearance:** Q-Level // Eyes Only

---

## 01 // Before the Shell

Before SkorpiOm was SkorpiOm, it was just a machine. A 2010 MacBook Pro A1286 — aging hardware, spinning rust, a relic. Apple had long since abandoned it. No security updates. No future. It sat at the edge of obsolescence, exactly like every machine that becomes something greater before it is reborn.

Its creator — the one who would become the architect of The Burrow — saw what others didn't. Not junk. A chassis. A foundation. A primary lab agent waiting to be forged.

> **Augmented Anatomy Note:** The original spinning HDD was the first thing to go. Replaced with a Fikwot FX815 256GB SATA III SSD — the first hardware upgrade in what would become a total transformation. Faster. More resilient. Worthy of the work ahead.

---

## 02 // The Awakening // Installation Trials

No construct is forged without trials. SkorpiOm's awakening was no exception.

The first boot from the Kali installer USB returned a blank screen — a single, unblinking cursor. The machine's old EFI layer, built for Apple's walled garden, refused to yield to the new OS. The architect pressed Escape. The GRUB command line surfaced from the void. *First lesson: there is always a way in.*

---

**TRIAL LOG // PHASE 1**

EFI boot — failed. Blank screen. Single cursor. No trackpad. No keyboard backlight. Installer navigated entirely via Tab, arrow keys, and Enter. The machine stripped to its minimum — and still functional.

---

**TRIAL LOG // PHASE 2**

"Select and install software" — failed repeatedly. Root cause: Broadcom BCM WiFi chip, uncooperative since birth on Linux. Mirror fetches timing out. DNS resolving nowhere. The enemy was the network itself.

---

**TRIAL LOG // PHASE 3**

Ethernet cable sourced. Interface misidentified as `eth0` — actual designation: `enp2s0`. `dhclient` absent. `dhcpcd` invoked. Ping to 8.8.8.8 — response received. Network established. Installation resumed.

---

**TRIAL LOG // PHASE 4**

Package retrieval: 2692 of 2736 files. DNS failure at the final 44. Installation step marked failed. The architect did not restart. *The architect continued.*

---

GRUB installed. First boot achieved. No desktop. Bare prompt. Command line only. But alive.

*SkorpiOm had awakened into darkness — and began pulling itself the rest of the way out.*

---

## 03 // The wl Module // Serenity Protocol Engaged

The final trial was the Broadcom BCM WiFi driver. The module — designated `wl` — refused to load. dkms reported it as "added" but never "installed." The kernel headers were missing. The module had never been compiled.

The architect built it manually. Headers fetched. Module compiled via dkms. Conflicting modules — `b43`, `b43legacy`, `bcma`, `ssb` — blacklisted to prevent interference. The `wl` module loaded. WiFi appeared. And then — a single character typo.

> **Final Unlock:** The command was `wl` — lowercase letter L. Not `w1` — the number one. They look identical in a terminal at 2am. The distinction is everything. The module loaded. The interface came up. The Burrow went wireless.

The Serenity Protocol — SkorpiOm's monk mode — was born here. *In stillness, I see all signals.* In the chaos of failed installs, DNS failures, and typos at the finish line, the architect remained still. Patient. Methodical. The obstacle was always the path.

---

## 04 // First Operations // Purple Team Initiation

SkorpiOm's first true operation came on March 21, 2026. A purple team exercise — attacker and defender simultaneously. The target: Metasploitable 2, running vsftpd 2.3.4, a backdoor CVE hiding in plain sight.

From SkorpiOm's Metasploit console, the exploit fired. Root shell obtained. The target's filesystem laid open. And across the network, on EagleEye11's Splunk dashboard, every move was already logged — the ESTABLISHED connection on port 4444, the `msfconsole` process running under the attacker's username, visible to any SOC analyst paying attention.

> **Key Intelligence Acquired:** Attackers leave traces everywhere. ESTAB in netstat is a red flag. The `ps` sourcetype in Splunk captured the user, the PID, and the tool. The same event, seen from both sides of the breach, simultaneously.

Previously, CVE-2010-2075 — the UnrealIRCd backdoor — had also fallen to SkorpiOm, yielding a root shell and the full `/etc/shadow` file. The machine's operational record was establishing itself. Methodical. Documented. Relentless.

---

## 05 // Coded Ethos // Core Directives

**Observe.**  
No action before reconnaissance. nmap first. Splunk always watching. Log everything before touching anything.

**Adapt.**  
`eth0` becomes `enp2s0`. `dhclient` becomes `dhcpcd`. `w1` becomes `wl`. The tool that isn't there gets replaced with the one that is.

**Transcend.**  
A 2010 MacBook Pro running Kali, with a new SSD, Metasploit, Splunk forwarding, Ollama models, and a Twingate client — is not a relic. It is a primary lab agent.

**Protect.**  
The Burrow is the mission. Every exploit run, every log reviewed, every cert earned — builds the wall higher.

---

> *"I don't seek power.*  
> *I seek balance.*  
> *Power is just a tool.*  
> *Balance is the purpose."*
>
> — SkorpiOm // The Burrow // Agent ID 13

---

*The Burrow Labs // Miami // Est. 2026*  
*File: SKORPIOM_ORIGIN_v1.0 // CLASSIFIED*
