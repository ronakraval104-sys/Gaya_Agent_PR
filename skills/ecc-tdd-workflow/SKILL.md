---
name: ecc-tdd-workflow
description: Enforce strict Test-Driven Development (TDD) Red-Green-Refactor cycle. Mandates running and verifying failing tests before implementing production code, then verifying clean pass before committing.
---

# ECC TDD Workflow Skill

## Overview
Adapted from ECC's canonical `tdd-workflow` and `tdd-guide`.
Enforces the strict, non-negotiable **RED -> GREEN -> REFACTOR** lifecycle for any feature, refactor, or bugfix.

```text
RED (Write test & confirm failure) -> GREEN (Minimal code to pass) -> REFACTOR (Clean up & verify still passing)
```

## Protocol Gates

### 1. RED Phase (Failing Test First)
- Write the unit or integration test before touching implementation code.
- Execute the test runner (e.g. `python -m unittest <test_path>` or `pytest <test_path>`).
- **Receipt Gate**: Confirm the test fails with the specific expected failure reason (e.g. `ModuleNotFoundError`, `AttributeError`, or `AssertionError`).
- If the test passes immediately without implementation changes, the test is invalid or redundant.

### 2. GREEN Phase (Minimal Code)
- Write the minimum working code required to satisfy the test.
- Do not build speculative abstractions, helpers, or unrequested features (adhere to YAGNI).
- Run the test runner again. Confirm clean 0 exit code and 100% test pass.

### 3. REFACTOR Phase (Clean & Verify)
- Remove duplication, improve variable naming, and optimize structures.
- Re-run the full test suite to guarantee zero regression.
- Commit atomically with clear conventional commit messages: `feat: ...`, `fix: ...`, `refactor: ...`.

## Anti-Patterns (Forbidden)
- Writing implementation code before writing tests.
- Claiming tests pass without running them in the shell.
- Writing test files without assertions.
- Skipping tests for "simple" functions.
