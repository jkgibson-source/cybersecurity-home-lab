# OverTheWire — Bandit Notes

## Progress Tracker
| Level | Status |
|-------|--------|
| Level  0 → 1  | ✅ Complete |
| Level  1 → 2  | ✅ Complete |
| Level  2 → 3  | ✅ Complete |
| Level  3 → 4  | ✅ Complete |
| Level  4 → 5  | ✅ Complete |
| Level  5 → 6  | ✅ Complete |
| Level  6 → 7  | ✅ Complete |
| Level  7 → 8  | ✅ Complete |
| Level  8 → 9  | ✅ Complete |
| Level  9 → 10 | ✅ Complete |
| Level 10 → 11 | ✅ Complete |
| Level 11 → 12 | ✅ Complete |
| Level 12 → 13 | ✅ Complete |
| Level 13 → 14 | ✅ Complete |
| Level 14 → 15 | ✅ Complete |
| Level 15 → 16 | ✅ Complete |

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
- `ls -la`
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

## Level 5 → 6
**Objective:** Locate and read a file with specific properties mixed in 
amongst multiple diretories.

**Solution:**
Use `find` with the appropriate combined flags to locate the file, then 
use `cat` to read it.

**Commands Used:**
- `cd inhere`
- `ls -la`
- `find . -size 1033c -readable ! -executable`
- `cat ./filepath/.file2`

**Key Concept:** 
- `find` with multiple conditions chains filters together
- the c suffix in `size 1033c` means bytes
- in `! -executable`, the `!` negates the flag `-executable`
- `.` searches the current directory recursively 

---

## Level 6 → 7
**Objective:** Locate the password, located somewhere on the server, 
using the given specifications.

**Solution:**
Use the `find` with the appropriate combined flags to locate the 
file, then use `cat` to read it, silencing any permission denied errors.

**Commands Used:**
- `find / -size 33c -user bandit7 -group bandit6 2>/dev/null`
- `cat /file/path/bandit7.password`

**Key Concept:**
- using the `-user` and `-group` flags
- searching from root using `/`
- stream redirection using `2>/dev/null`

---

## Level 7 → 8
**Objective:** Locate the target phrase and password in a very 
long list of data.

**Solution:**
Use `grep` to pinpoint the given target phrase and password.

**Commands Used:**
- `cat data.txt`
- `grep -w 'millionth' data.txt`

**Key Concept:**
- using `grep` to locate a specific pattern or string.

---

## Level 8 → 9
**Objective:** Locate the password as the only non-duplicate line
in a long data set.

**Solution:**
Use `sort` and `uniq` to find the password, piping the output from
`sort` into `uniq` with the appropriate flag.

**Commands Used:**
- `sort data.txt | uniq -u`

**Key Concept:**
- pipng output from one command into another
- using `sort` to compare data in a file
- using `uniq -u` to filter and print unique data. 

---

## Level 9 → 10
**Objective:** Locate the human-readable password from the data set.

**Solution:** Pipe the output from `strings` into `grep` to locate the
"==" pattern and find the password.

**Commands Used:**
- `strings data.txt | grep "=="`

**Key Concept:**
- using `strings` to decipher human-readable text
- using `grep` to locate a pattern
- piping output from one command into another

---

## Level 10 → 11
**Objective:** Decode the password from base64.

**Solution:** Use the `-d` flag with `base64` to read the file.

**Commands Used:**
- `base64 -d data.txt`

**Key Concept:**
- `base64` can be used from the command line to encode or decode a string
-  the `-d` flag tells the command to decode

---

## Level 11 → 12
**Objective:** Decode the password from Rot13.

**Solution:** Use the `tr` command to "translate" the string.

**Commands Used:**
- cat data.tx | tr 'A-Za-z' 'N-ZA-Mn-za-m'

**Key Concept:**
- `rot13` is actually also a command that will directly decode the sting,
however, it isn't installed am I am unable to install it.

---

## Level 12 → 13
**Objective:** Find the password in a hexdump that has been compressed 
using several different formats.

**Solution:** Decompress the file until it is in ASCII format, then use
cat to read the password.

**Commands Used:** 
- `TMPDIR=$(mktemp -d /tmp/bandit12/XXXX)`
- `cp ~/data.txt $TMPDIR`
- `cd $TMPDIR`
- `xxd -r data.txt > data.bin`
- `file data.bin`
- `gunzip data*.gz`, `bunzip2 data*.bz2`, `tar xf data*.tar`
- `file data*`

**Key Concept:** 
- Utilizing `gzip`, `bzip2`, and `tar` to decompress a file
- Using `file` to discern file types.

---

## Level 13 → 14
**Objective:** Get in to the next level using a private ssh key instead of
a password.

**Solution:** Make a copy of the ssh key to my local system called
`banditkey14.key`. Modify the permissons to user read only, then use `ssh`
to enter Level 14.

**Commands Used:**
- `cat sshkey.private`
- `nano bandit14.key`
- `chmod 400 ~/bandit4.key`
- `ssh -i ~/bandit14.key bandit14@bandit.labs.overthewire.org -p 2220`

**Key Concept:**
- Key-based SSH authentication.

---

## Level 14 → 15
**Objective:** Submit the last level's password via localhost at post 30000
to proceed.

**Solution:** Use netcat to submit the level 14 password and gain access to
level 16.

**Commands Used:** 
- `nc localhost 30000`

**Key Concept:** 
- Using `netcat`

---

## Level 15 → 16
**Ojective:** Submit the current level passsword to port 30001 on localhost 
using SSL/TLS

**Solution:** Connect to localhost port 30001 using `openssl`

**Commands Used:** `openssl s_client -connect localhost:30001`

**Key Concept:** Using `openssl` to connect to localhost for encryption.

---
*Passwords stored locally only — not published out of respect 
for other players working through these challenges.*
