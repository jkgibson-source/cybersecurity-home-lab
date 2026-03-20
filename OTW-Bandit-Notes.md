# OverTheWire — Bandit Notes

## Progress Tracker
| Level | Status |
|-------|--------|
| Level 0 → 1 | ✅ Complete |
| Level 1 → 2 | ✅ Complete |

---

## Level 0 → 1
**Objective:** Find the password stored in a file called `readme`

**Solution:**
Used `cat readme` to read the file contents from the home directory.

**Commands Used:**
- `ssh bandit0@bandit.labs.overthewire.org -p 2220`
- `cat readme`

**Key Concept:** Basic SSH connection and file reading with `cat`

---

## Level 1 → 2
**Objective:** Read a file named `-`

**Solution:**
The `-` character has special meaning in Linux — it tells commands 
to read from standard input. Used an explicit path to treat it as 
a filename instead.

**Commands Used:**
- `cat ./-` or `cat ~/-`

**Key Concept:** Files with special character names require explicit 
path references. `./` prefix forces Linux to interpret the argument 
as a filename rather than a flag.

---

*Passwords stored locally only — not published out of respect 
for other players working through these challenges.*
