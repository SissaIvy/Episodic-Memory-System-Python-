---
mode: "edit"
description: Create unit tests for new/changed modules, following project test policy.
tools: ["findTestFiles","codebase"]
---
Add or update tests under `tests/` mirroring source layout. Include one happy path and one failure path. Keep tests isolated; use mocks for I/O/network/time.
