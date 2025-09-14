---
applyTo: "**/*.py,**/*.ts,**/*.tsx,**/*.cs"
description: Ensure new code ships with tests and docs; enforce isolation.
---
# Test & Docs Defaults (MasterMind)
- For any new or modified function/class: add/update tests (>=1 happy path, >=1 failure path). Frameworks: Python=pytest; TypeScript=Vitest; C#=xUnit.
- Module header must include: Summary, Contracts (inputs/outputs/invariants), Side‑effects, Errors, Example, Version.
- Keep unit tests isolated: avoid network/I/O/time; mock or inject abstractions; prefer parameterized tests; keep fast and deterministic.
