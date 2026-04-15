# Krypton1t3 Pre-Engagement Checklist

**Author:** JBird (James Gibson)  
**Lab:** The Burrow Cybersecurity Lab  
**Date:** April 2026  
**Reference:** Krypton1t3 Unified Pentest Plan

Complete all items before launching any Phase 0 OSINT or Phase A attack activity. Check each item off and note any issues. Do not proceed if a critical item is unresolved.

---

## 1. SIEM — EagleEye11 (Splunk)

- [ ] Splunk Enterprise is running on EagleEye11
- [ ] Bird's Nest external drive is mounted and Splunk index is active
- [ ] Splunk is receiving on TCP port 9997 — verify in Settings → Data Inputs
- [ ] SkorpiOm Splunk Universal Forwarder is running and sending logs
  ```bash
  # On SkorpiOm
  sudo systemctl status SplunkForwarder
  ```
- [ ] Krypton1t3 Splunk Universal Forwarder is running and sending logs
  ```bash
  # On Krypton1t3
  sudo /Applications/SplunkForwarder/bin/splunk status
  ```
- [ ] Both hosts appear in Splunk search (`index=* | stats count by host`) with recent events
- [ ] "SkorpiOm Security Monitor" dashboard is loading cleanly
- [ ] Time range on all dashboard panels set to cover the engagement window

---

## 2. Network Connectivity

- [ ] Tailscale is active on SkorpiOm, EagleEye11, and Jynx13
  ```bash
  tailscale status
  ```
- [ ] Jynx13 can reach EagleEye11 over Tailscale (ping or SSH test)
- [ ] SkorpiOm can reach Krypton1t3 on the local network
  ```bash
  ping <krypton1t3_ip>
  ```
- [ ] Krypton1t3 target IP is confirmed and noted before starting
- [ ] Twingate connector is active on EagleEye11 (if remote access needed)

---

## 3. Target — Krypton1t3

- [ ] Krypton1t3 is powered on and connected to the network
- [ ] Target IP address is confirmed:  `____________________`
- [ ] Remote Management (VNC, port 5900) is enabled in System Preferences → Sharing
- [ ] Printer Sharing (CUPS/IPP, port 631) is enabled
- [ ] Any other planned target services are enabled and noted
- [ ] Splunk Forwarder on Krypton1t3 is confirmed active (see Section 1)
- [ ] A quick pre-engagement nmap confirms expected ports are open:
  ```bash
  nmap -sV <krypton1t3_ip>
  ```

---

## 4. Attacker Machine — SkorpiOm

- [ ] Kali Linux is booted and up to date
- [ ] Metasploit Framework is functional:
  ```bash
  msfconsole -v
  ```
- [ ] nmap is installed and working
- [ ] All planned tools are installed and accessible (verify each):
  - [ ] nmap
  - [ ] Metasploit
  - [ ] Hydra (or equivalent auth testing tool)
  - [ ] Wireshark / tcpdump
  - [ ] scp / ssh client
- [ ] Exfiltration staging directory exists:
  ```bash
  mkdir -p ~/exfil
  ```
- [ ] Test exfiltration file created (non-sensitive):
  ```bash
  echo "CONFIDENTIAL: Sample internal data" > ~/Documents/sample_sensitive.txt
  # (create on Krypton1t3, not SkorpiOm — confirm this step is ready)
  ```

---

## 5. OSINT Machine — Jynx13

- [ ] Jynx13 is powered on and connected to the network
- [ ] OSINT tools are installed and working:
  - [ ] sherlock
  - [ ] theHarvester
  - [ ] nmap
  - [ ] whois / nslookup
  - [ ] exiftool
- [ ] Parrot OS on SuperStick is confirmed bootable (if Mode 2 OSINT is in scope)
- [ ] Anonsurf tested and functional on Parrot OS boot (if applicable)
- [ ] Screenshots folder structure created on Jynx13:
  ```bash
  mkdir -p ~/pentest/krypton1t3/screenshots/{phase0_osint,phaseA_attack,phaseB_armor,jynx13_observer}
  ```
- [ ] SCP transfer from Jynx13 to EagleEye11 tested:
  ```bash
  scp test.png jbird13@<eagleeye11_tailscale_ip>:~/pentest/krypton1t3/screenshots/jynx13_observer/
  ```

---

## 6. Evidence & Documentation

- [ ] Screenshot folder structure confirmed on EagleEye11:
  ```bash
  mkdir -p ~/pentest/krypton1t3/screenshots/{phase0_osint,phaseA_attack,phaseB_armor,jynx13_observer}
  ```
- [ ] Engagement log file created for timestamped notes:
  ```bash
  touch ~/pentest/krypton1t3/engagement_log.md
  ```
  Start the log with:
  ```
  # Krypton1t3 Engagement Log
  **Date:** YYYY-MM-DD
  **Start time:** HH:MM
  
  ## Timeline
  | Timestamp | Phase | Action | Notes |
  |---|---|---|---|
  | T+0 | Phase 0 | OSINT started | |
  ```
- [ ] File naming convention confirmed: `tool_what-it-shows.png`
- [ ] GitHub repo is accessible from EagleEye11 and credentials are working:
  ```bash
  cd ~/path/to/cybersecurity-home-lab && git status
  ```

---

## 7. Phase B Preparation (Netgear Armor)

- [ ] Netgear Armor subscription is active
- [ ] SolSkorp_13 is available for Armor alert monitoring
- [ ] Armor app is open and notifications are enabled on SolSkorp_13
- [ ] Confirm Armor is **disabled** at Phase A start and **enabled** at Phase B start

---

## 8. Final Go / No-Go

| Check | Status |
|---|---|
| Splunk receiving from both machines | ☐ Go / ☐ No-Go |
| Krypton1t3 online with target services active | ☐ Go / ☐ No-Go |
| Tailscale mesh confirmed across all nodes | ☐ Go / ☐ No-Go |
| Evidence folders created on Jynx13 and EagleEye11 | ☐ Go / ☐ No-Go |
| Engagement log file created and open | ☐ Go / ☐ No-Go |
| All tools on SkorpiOm and Jynx13 verified | ☐ Go / ☐ No-Go |

**All items Go?** Proceed to Phase 0 OSINT.  
**Any No-Go?** Resolve before starting. Do not skip.

---

*This checklist is part of the Krypton1t3 pentest documentation for The Burrow Cybersecurity Lab.*
