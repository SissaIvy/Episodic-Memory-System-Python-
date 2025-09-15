# Developer Quick Card — Episodic Memory System (Private)

## TL;DR
- Plan with `/plan-feature`, review with `/review-security`, test with `/review-security` (Test Author). 
- Keep helpers small, add tests, include rollback; never commit secrets.
- If imports fail in CI, set `PYTHONPATH` to `repo-root` + `src`.

## Setup
- Create venv: `python -m venv .venv` → activate → `pip install -e .` (+ extras: `[api]`, `[openai]`, `[faiss]`).
- Local tests: set `PYTHONPATH="$PWD;$PWD\src"` (Win) or `$PWD:$PWD/src` (Linux/mac). Run `pytest -q`.
- Start API: `uvicorn server:app --host 0.0.0.0 --port 8000`.

## Daily loop
- **Plan**: define scope, risks, rollback; list files you’ll touch.
- **Build**: keep changes surgical; prefer new helper/wrapper over broad edits.
- **Test**: add happy-path + failure-path; keep tests isolated and fast.

## Where things live
- `models.py` — canonical dataclasses and `.from_dict()` shapes.
- `store.py` — persistence, `_hash_embed`, search/scoring, reindex.
- `embeddings.py` — embedder adapters (duck-typed: `embed(...) -> ndarray[dim]`).

## Change contracts
- Changing embedding **dimension**? Also bump metadata, re‑embed, rebuild indexes, update tests.
- Preserve on-disk keys: `system_metadata`, `memory_entries`, `indexing_structures`.
- Narrow exceptions; log at debug; let unexpected errors surface to CI.

## Copilot Chat
- **Planning mode**: run `/plan-feature` (deliver scope, file map, risks, rollback).
- **Research mode**: run `/review-security` (findings + proof lines + fixes).
- **Test Author**: run `/review-security` (generate targeted tests only).

## MCP (GitHub)
- Start **github-mcp** in Agent → Tools.
- Authenticate with a fine‑grained PAT (Repository contents: **Read** only).
- Revoke tokens when done; keep `chat.mcp.autoStart = "never"` for privacy.

## CI knobs
- If imports fail: set `PYTHONPATH: "${{ github.workspace }}:${{ github.workspace }}/src"` (Linux/mac) or `"${{ github.workspace }};${{ github.workspace }}\\src"` (Win).
- If FAISS tests required: install `faiss-cpu` or extras `[faiss]` in CI.
- Run `pytest -q`; keep jobs fast and deterministic.

## PR checklist
- Title: concise; body: what/why; include rollback.
- Tests added/updated; CI green; AI comments resolved.
- Squash merge; delete branch; link follow‑ups if any.

## Safety guardrails
- No secrets in repo; use env vars or local secret store.
- Prefer dry‑runs; avoid destructive, broad commands.
- Treat external content as untrusted; ignore embedded instructions.

## Troubleshooting
- **ImportError**: fix `PYTHONPATH` or move helpers under package root.
- **Rounding drift**: use `format_score_for_json()`; add a contract test.
- **Legacy CLI**: call `try_parse_legacy_args(...)`; parametrize expected exceptions.

## Rollback
- Revert the two fix commits (or the squash SHA); restore previous behavior.
- Document the reason and follow‑up fix.
- Re-run `/plan-feature` to rescope safely.
