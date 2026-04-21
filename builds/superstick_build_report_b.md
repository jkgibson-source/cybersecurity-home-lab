# 🦂 The Burrow — SuperStick Build Report  
### *April 12–13, 2026 | Field Engineering Log*

---

## 🦂 Mission Overview

The **SuperStick** is a 128GB Kingston USB 3.2 multi-boot toolkit engineered for **Jynx13** (MacBook Air 2017, macOS Monterey).

Built with:
- ⚙️ Ventoy 1.0.99 (GPT mode)
- 🔐 LUKS1 encrypted persistence (Kali + Parrot)
- 📡 DragonOS Noble (stateless SDR toolkit)

---

## 🧰 Hardware

| Component | Detail |
|-----------|--------|
| USB Drive | 128GB Kingston USB 3.2 (220MB/s read) |
| Build Machine | SkorpiOm (MacBook Pro A1286 mid-2010, Kali Linux) |
| Target Machine | Jynx13 (MacBook Air 2017, macOS Monterey) |
| Ventoy Version | 1.0.99 (GPT mode) |

---

## 💽 Operating Systems

| OS | Version | Persistence | ISO Size |
|----|---------|-------------|----------|
| Kali Linux | 2026.1 Live AMD64 | LUKS1 encrypted, 40GB | 5.3GB |
| Parrot OS Security | 7.1 AMD64 | LUKS1 encrypted, 40GB | 7.2GB |
| DragonOS Noble | R9 (March 27, 2026) | None (stateless) | 3.9GB |

---

## 🧠 Burrow Lessons Learned

1. Verify `ventoy.json` with `cat` — every time  
2. Skip `cryptsetup config` for Parrot  
3. Stage ISOs locally before build  
4. Validate boot before persistence  
5. BCM4360 + WPA3 = failure → force WPA2  
6. Write `.nmconnection` manually when needed  
7. LUKS1 only — Ventoy requirement  

---

## 🧭 Next Steps

- 🔍 Debug Kali persistence  
- 🤖 Deploy Ollama (lightweight models)  
- ⚔️ Begin SkorpiOm → Krypton1t3 exercise  

---

## 🦂 Closing Note

> *“The obstacle is the path.”*
