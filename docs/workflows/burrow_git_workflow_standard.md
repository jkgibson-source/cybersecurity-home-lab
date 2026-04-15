# Burrow Git Workflow Standard
**Operational Version Control Guide for the Cybersecurity Home Lab**

---

## Purpose

This document defines the Git workflow used in **The Burrow** to ensure:

- Clean, professional commit history  
- Reproducibility of investigations and builds  
- Safe handling of ongoing work  
- Portfolio-grade presentation for review by hiring managers  

This is not a beginner guide — it is an **operational standard**.

---

## Core Philosophy

The Burrow repository is treated as a **professional artifact**, not a scratchpad.

Every commit should:
- Tell a clear story
- Represent intentional progress
- Be understandable to a third party

---

## Daily Start Routine

Before making any changes:

```bash
git pull origin main
git status
```

This ensures:
- Your local repo is up to date
- You avoid merge conflicts
- You are working from a stable baseline

---

## Branching Strategy

### Use `main` for:
- Small fixes
- README updates
- Minor documentation edits

### Use feature branches for:
- Investigations
- Case studies
- Multi-file changes
- Structural updates

Create a branch:

```bash
git checkout -b feature/descriptive-name
```

Merge back into main when complete.

---

## Naming Conventions

### Branch Names

```bash
feature/wazuh-case-study
feature/osint-investigation
fix/diagram-link
docs/git-workflow-standard
```

### Commit Messages

Format:

```bash
type: concise description
```

Types:
- `feat:` new content
- `fix:` corrections
- `docs:` documentation updates
- `refactor:` structure changes
- `chore:` maintenance

Examples:

```bash
docs: add Wazuh troubleshooting case study
fix: correct diagram path in README
feat: add OSINT investigation report
```

---

## Safe Commit Workflow

```bash
git pull origin main
git status
git add <relevant files>
git commit -m "clear, professional message"
git push origin main
```

Avoid blind commits with `git add .` unless verified.

---

## Pre-Commit Checklist

Always run:

```bash
git status
git diff
```

Verify:
- No unintended deletions
- No junk/system files
- No sensitive data
- Correct file paths
- Clean formatting

---

## macOS File Protection

Add to `.gitignore`:

```gitignore
.DS_Store
```

Remove existing:

```bash
git rm --cached .DS_Store
find . -name .DS_Store -delete
git commit -m "chore: remove macOS metadata files"
```

---

## Repository Structure Standard

```text
README.md
builds/
investigations/
case-studies/
docs/
diagrams/
scripts/
```

---

## Common Recovery Commands

### Unstage a file

```bash
git restore --staged <file>
```

### Discard changes

```bash
git restore <file>
```

### Restore deleted file

```bash
git restore <file>
```

### Fix last commit message

```bash
git commit --amend -m "new message"
```

---

## Clean History Practice

Avoid:

```bash
update
stuff
fix
```

Prefer:

```bash
docs: update Burrow README and structure
feat: add pentest phase documentation
fix: resolve diagram rendering issue
```

---

## Standard Workflows

### New Investigation

```bash
git checkout -b feature/investigation-name
git add investigations/
git commit -m "feat: add new investigation"
git push origin feature/investigation-name
```

---

### README Update

```bash
git add README.md
git commit -m "docs: refresh README"
git push origin main
```

---

### Diagram Update

```bash
git add diagrams/
git add README.md
git commit -m "fix: update diagram and references"
git push origin main
```

---

## Emergency Debug Sequence

If something feels wrong:

```bash
pwd
git branch
git status
git diff
git log --oneline -5
```

---

## Golden Rules

### Do
- Pull before starting
- Check status frequently
- Use descriptive commits
- Keep repo clean and readable

### Do Not
- Commit blindly
- Use vague messages
- Push broken or incomplete work
- Panic — inspect first

---

## Final Note

This workflow reflects how work is managed in a **professional security environment**:

- Structured  
- Traceable  
- Reproducible  
- Reviewable  

Maintaining this standard ensures that The Burrow remains both a **learning environment** and a **portfolio-quality artifact**.
