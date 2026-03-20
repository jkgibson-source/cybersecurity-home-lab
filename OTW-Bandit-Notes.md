# OverTheWire — Bandit Notes

## Progress Tracker
| Level | Status |
|-------|--------|
| Level 0 → 1 | ✅ Complete |
| Level 1 → 2 | ✅ Complete |
| Level 2 → 3 | ✅ Complete |
| Level 3 → 4 | ✅ Complete |
| Level 4 → 5 | ✅ Complete |
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

## Level 2 → 3
**Objective:** Read a file named "--spaces in this filename--"

**Solution:**
Quotation marks are necessary around the filename due to the spaces
and double dashes in the filename.

**Commands Used:** 
- `cat ./"--spaces in the filename--"`

**Key Concept:** Files with spaces in the name require quotation 
marks in order to be acurately processed.

---

## Level 3 → 4
**Objective:** Find and read a hidden file

**Solution:**
Change into the proper directory, list all files, locate the hidden
file, then use the `cat` command to read it.

**Comands Used:**
- `cd inhere`
- 'ls -la'
- `cat ...Hiding-From-You`

**Key Concept:** The -la flag on the ls command tells linux to list 
the contents of the directory in long form - including hidden files.

---

## Level 4 → 5
**Objective:** Procure the human readable data hidden amongst ten 
files.

**Solution:**
Once in the proper directory, use cat to cycle thorugh the files 
using the up arrow keyboard shortcut.

**Alternative Solution:**
`file ./-file0*` — identifies file types across multiple 
files simultaneously using wildcard

**Commands Used:**
- `cd inhere`
- `ls -la`
- `cat ./-file0x`
- `file ./-file0*`

**Key Concept:** Human-readable = `ASCII text`, `file` command identifies
file types, wildcard `*` runs commands against multiple files
simultaneously

---

*Passwords stored locally only — not published out of respect 
for other players working through these challenges.*
