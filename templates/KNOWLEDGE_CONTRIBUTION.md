# Knowledge Contribution Guide

**How to share your hard-won lessons with the Gaya community.**

---

## Why Contribute?

> *"Don't raw-dog every lesson. Learn from someone else's L."*
> — Chanakya Niti

Every lesson you contribute means someone else doesn't make the same mistake. Every pattern you share means someone builds faster. The shared knowledge base is what makes Gaya grow wiser with every user.

---

## The Contribution Flow

```
1. You learn something hard
2. Write it as a lesson → knowledge/user_profiles/<name>/lessons/
3. Submit to community/ → open a Pull Request
4. Maintainer reviews → merges into knowledge/base/
5. Every Gaya user benefits
```

---

## Step 1: Write Your Lesson

Use this template:

```markdown
# Lesson Title

**Author:** [Your Name]
**Date:** [Date]
**Domain:** [e.g., Voice/Audio, Python, Architecture, Workflow]
**Severity:** [⚠️ Project-killer / 🔴 Critical / ⚡ Principle / 📊 Medium]

## What Happened
(Describe the situation concisely)

## Root Cause
(What actually caused the failure)

## The Fix
(What solved it, with code/config snippets if relevant)

## What DID Work
(Reusable patterns or approaches that worked)

## Prevention
(How to avoid this in the future — encoded rules, patterns, middleware)
```

Save to: `knowledge/user_profiles/<your-name>/lessons/<lesson-name>.md`

## Step 2: Prepare a Submission

1. Copy your lesson to: `knowledge/community/submissions/<lesson-name>.md`
2. Add an entry to `knowledge/community/INDEX.md`

## Step 3: Open a Pull Request

1. Fork the Gaya-Agent repo (if you haven't)
2. Commit your changes to a branch: `git checkout -b lesson/<lesson-name>`
3. Push: `git push origin lesson/<lesson-name>`
4. Open a PR against the main repo

## Step 4: Maintainer Review

- Maintainer reviews for accuracy, clarity, and reusability
- May request edits or clarification
- Once approved → merged into `knowledge/base/`
- You're credited as the author

---

## What Makes a Good Contribution

| Good | Not Great |
|---|---|
| Specific, reproducible failure | Vague "it didn't work" |
| Root cause analysis | Surface-level symptoms |
| Code/config snippets | "I changed some settings" |
| What didn't work AND what did | Only the failure |
| Actionable prevention | "Be more careful next time" |

---

## Opt-Out Is Always OK

This is **never required**. If you don't want to share, don't. Your personal lessons stay in your user profile. No pressure, no guilt, no tracking of who contributes and who doesn't.

The shared knowledge base grows at the pace the community chooses.

---

> *"Knowledge shared is knowledge squared."*
