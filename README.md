Episodic Memory System (Python)

Overview
- Robust loader that extracts the last valid JSON object from files that may contain extra fragments.
- Typed, dependency-free models and a `MemoryStore` API to add, save, and search memories.
- Simple hash-based embeddings to enable demo retrieval without external services.
- CLI for validation, search, and adding memories.
 - JSON Schema for validation and a `fix` command to normalize files.
 - Pluggable embeddings: built-in hash (default) and OpenAI backend (optional).

Quick Start
- Validate the sample file:
  - `python memory_cli.py validate EpisodicMemorySystem.json`
  - With schema: `python memory_cli.py validate EpisodicMemorySystem.json --schema`
- Search (override threshold for the demo):
  - `python memory_cli.py search EpisodicMemorySystem.json "episodic" --threshold 0.1`
- Add a memory and persist:
  - `python memory_cli.py add EpisodicMemorySystem.json "My new memory" --tags test foo --importance 0.6`
  - With OpenAI embeddings: `python memory_cli.py add EpisodicMemorySystem.json "My new memory" --embedder openai --openai-model text-embedding-3-small`
    - Requires `OPENAI_API_KEY` in env and installing optional dep: `pip install -e .[openai]`

Fix and Normalize
- Fix inconsistencies (counts, indexes), optionally re-embed and write back:
  - Dry run to new file: `python memory_cli.py fix EpisodicMemorySystem.json --output fixed.json --schema`
  - In-place: `python memory_cli.py fix EpisodicMemorySystem.json --in-place --schema`
  - Force re-embed with OpenAI at 512 dims: `python memory_cli.py fix EpisodicMemorySystem.json --in-place --reembed --embedder openai --openai-model text-embedding-3-small --embed-dim 512`

Schema-Only Validation
- `python memory_cli.py schema-validate EpisodicMemorySystem.json` (auto-loads bundled schema)

Tests
- Run tests:
  - `python -m unittest discover -s tests -p "test_*.py" -v`

Packaging
- Build/install locally:
  - `pip install -e .`
  - CLI entrypoint: `episodic-memory` (mirrors `python memory_cli.py`)

API Server
- Install API extras: `pip install -e .[api]`
- Run: `uvicorn server:app --host 0.0.0.0 --port 8000`
- Endpoints:
  - `GET /health`
  - `POST /validate` { path or data, schema: true }
  - `POST /search` { path, query, top_k, threshold? }
  - `POST /add` { path, text, tags[], importance, reward, tone, embedder?, openai_model?, embed_dim? }

Embedding Backends
- Hash (default): No dependencies, deterministic, dimension configurable.
- OpenAI (optional): Set `OPENAI_API_KEY`, install `pip install -e .[openai]`, choose model via `--openai-model` or env `OPENAI_EMBEDDING_MODEL`.

Notes
- The included embedding is a placeholder. Swap `_hash_embed` in `episodic_memory/store.py` with a production embedding model or a vector DB integration for commercial deployments.
- The loader tolerates extra JSON fragments by extracting the final valid object; keep files clean in production.
 - The fixer rebuilds clusters and temporal index to align with embeddings and metadata.
