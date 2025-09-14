<!-- .github/copilot-instructions.md - guidance for AI coding agents -->

This file gives focused, repository-specific guidance for an AI coding assistant to be immediately productive.

High-level architecture (why and what to change)
- Purpose: a minimal, dependency-free episodic memory store (JSON-based) with pluggable embedding backends, an optional FAISS ANN index, and a small HTTP API.
- Key components:
  - `episodic_memory/` — core datamodels (`models.py`), in-memory store and persistence (`store.py`), embedding adapters (`embeddings.py`), and small utilities (`utils.py`).
  - `memory_cli.py` — CLI entrypoints for validate, search, add, fix, and index operations; packaging exposes `episodic-memory` script.
  - `server.py` — lightweight FastAPI wrapper used for programmatic access (endpoints: `/health`, `/validate`, `/search`, `/add`).
  - `README.md` — authoritative quick-start, CLI and index flags, and developer workflows.

Important developer workflows (concrete commands)
- Install editable dev package: `pip install -e .` (optional extras: `[openai]`, `[api]`, `[faiss]`, `[local]`).
- Run tests (unittest): `python -m unittest discover -s tests -p "test_*.py" -v` (used by CI). For faster iterative runs use `pytest -q` if installed.
- Run the API locally: `uvicorn server:app --host 0.0.0.0 --port 8000` (requires `[api]` extras).
- Typical CLI examples (see `README.md`):
  - Validate: `python memory_cli.py validate EpisodicMemorySystem.json --schema`
  - Search (hash embedder): `python memory_cli.py search EpisodicMemorySystem.json "episodic" --embedder hash`
  - Add memory: `python memory_cli.py add EpisodicMemorySystem.json "text" --tags a b --importance 0.6`
  - Index build/search: `closed-loop-security index-build ...` and `closed-loop-security index-search ...` (see README index flags).

Quick setup & CI knobs
- Virtualenv + editable install (Win):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

- If you see ImportError in CI, set `PYTHONPATH` to include repo root and `src` (Windows uses `;` separator):

```yaml
env:
  PYTHONPATH: "${{ github.workspace }};${{ github.workspace }}\src"
```

- FAISS tests are optional. Install faiss extras in CI when required: `pip install -e .[faiss]`.

Repository conventions & patterns to follow
- Small, typed dataclasses in `episodic_memory/models.py` are the canonical schema — use `.from_dict` and `.to_dict` shapes when adding or reading data.
- Embedding duck-typing: any embedder should implement `.embed(text, dim)` and can be wrapped by `CachedEmbedder`. See `embeddings.py` for examples (`HashEmbedder`, `OpenAIEmbedder`, `SentenceTransformerEmbedder`).
- The fast but deterministic `_hash_embed` in `store.py` is the default; avoid changing its output shape unless you update `SystemMetadata.embedding_dimension` and tests.
- Indexing behavior: clusters are created/updated in `MemoryStore._assign_cluster` and `_update_indexes_for_new_entry`. Maintain centroid length and avoid mixing dims across entries without calling `reembed_all`.
- Persistence: `MemoryStore.to_dict()`/`save(path)` control the on-disk format. Tests and the CLI depend on stable keys like `system_metadata`, `memory_entries`, and `indexing_structures`.

Daily loop & Copilot modes
- Daily loop: plan (scope + rollback), make small focused changes, add tests (happy + failure paths), run tests locally.
- Copilot/Chat modes (useful prompts):
  - Planning: `/plan-feature` — produce scoped file map, risks, rollback steps.
  - Research/Review: `/review-security` — produce findings, exact code lines to inspect, and concrete fixes.
  - Test author: generate focused unit tests for a targeted failure.

Integration points & external dependencies
- Optional OpenAI backend: `OPENAI_API_KEY` and `[openai]` extras. OpenAI client usage is guarded in `embeddings.OpenAIEmbedder` with fallbacks for SDK versions.
- Optional local sentence-transformers (`[local]`) and FAISS (`[faiss]`) used by CLI index features (see `pyproject.toml` optional-dependencies).
- API uses FastAPI/uvicorn (`[api]`) and expects embedder concurrency throttling via `EMBED_CONCURRENCY` (env var) in `server.py`.

Tests and edge cases to watch for
- Tests run with the built-in hash embedder by default; changes to `_hash_embed` or embedding dimension will require updating tests in `tests/` (e.g., `test_memory_store.py`, `test_faiss_cli_meta.py`).
- Be careful with time/format: timestamps are ISO Zulu `YYYY-MM-DDTHH:MM:SSZ` and parsed/produced in `store.py` helpers.
- Many functions accept both path or raw data (see `server.validate` and `utils.load_system_from_path`) — preserve both input modes when refactoring.

PR checklist & safety guardrails
- PR checklist: clear title + body (what/why), add tests, CI green, AI comments resolved, include rollback notes. Prefer squash-merge and delete branch.
- Guardrails: never commit secrets; use env vars. Prefer dry-runs for destructive ops; treat external content as untrusted and avoid executing arbitrary scripts from data files.

How to make safe changes (mini contract)
- Inputs: JSON memory files conforming to `episodic_memory/schemas/episodic_memory.schema.json` or `EpisodicMemorySystem.json` samples.
- Outputs: functions must preserve on-disk `to_dict()` shape unless intentionally bumping package version and tests.
- Error modes: missing `OPENAI_API_KEY` should raise clear errors only when OpenAI embedder is instantiated; other code paths should continue to work with `HashEmbedder`.

Quick references (files to inspect for any change)
- Data model & persistence: `episodic_memory/models.py`, `episodic_memory/store.py`
- Embedding adapters & caching: `episodic_memory/embeddings.py`, `episodic_memory/cache.py`
- CLI surface: `memory_cli.py` and packaging entry in `pyproject.toml` (`episodic-memory`).
- HTTP surface: `server.py` (throttling via `EMBED_CONCURRENCY`)
- Tests: `tests/` (run the test suite after changes)

If unsure, follow these investigations first
1. Run the unit tests locally to see failures: `python -m unittest discover -s tests -p "test_*.py" -v`.
2. Search for failing keys in `MemoryStore.to_dict()`/`from_dict()` mappings.
3. If changing embedding dimensionality, call `MemoryStore.reembed_all()` in migration code and update `SystemMetadata.embedding_dimension`.

Ask for feedback: If any runtime detail or external workflow (CI, packaging, project automation) is missing or unclear, tell me which area to expand (tests, indexes, API, or packaging) and I'll iterate.
