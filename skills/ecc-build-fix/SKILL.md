---
name: ecc-build-fix
description: Systematic compiler, runtime, and build error diagnostic and minimal-diff repair. Use when encountering failed builds, missing dependencies, syntax/type errors, or broken environments.
---

# ECC Build Fix & Diagnostic Skill

## Overview
Adapted from ECC's `build-fix` and `build-error-resolver`.
Provides a disciplined, minimal-diff protocol for diagnosing and resolving broken builds, syntax errors, missing packages, and test harness failures without wholesale rewrites.

## The 4-Step Resolution Method

### 1. Isolate the Root Diagnostic Trace
- Capture the raw stderr, traceback, or compiler log.
- Do not guess based on assumptions. Identify the exact file path and line number where the execution halted.
- Differentiate between:
  - Missing environment dependency / import error (`ModuleNotFoundError`).
  - Syntax or parsing error (`SyntaxError`, `ParseError`).
  - Type or attribute mismatches (`TypeError`, `AttributeError`).
  - Network / port conflicts (`EADDRINUSE`, connection refused).

### 2. Formulate the Minimal Surgical Diff
- Do not rewrite the entire file or surrounding architecture.
- Identify the smallest possible single-block change that resolves the error.
- Climb Ponytail's ladder: Can standard library solve it? Can an existing installed package solve it? Avoid adding unneeded heavy packages.

### 3. Verify Clean Resolution
- Execute the original failing build command.
- Confirm exit code 0 and absence of the original error.
- Check that neighboring components or tests are not broken by the fix.

### 4. Record the Fix Heuristic
- If the error represents a recurring environment pitfall (e.g. Windows DLL search paths, SAPI voice casing, port occupancy), log it to `INSTINCTS.md` so the agent council never repeats the mistake.
