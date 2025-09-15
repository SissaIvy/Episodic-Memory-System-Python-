# README — Two‑Part Edition (Technical + Allegorical)

## Part I — Technical

### Direction
- Purpose: an **Episodic Memory System** in Python with repeatable **Copilot Chat** workflow (instructions, prompts, chat modes, MCP) to speed reliable development.
- Outcomes: fast retrieval, traceable reasoning, and test‑first contributions across `src/` and `tests/`.
- Guardrails: no secrets in repo; cautious operations with rollback by default.

### Design
- Architecture: **Ingest → Index → Retrieve/Reason** with a vector store (e.g., FAISS) and orchestrated prompts/modes for planning, research, and test authoring.
- Quality: unit tests live under `tests/`; coverage for happy‑path and failure‑path; isolation from network/I/O/time via mocks.
- Workflow: file‑based customization—`.github/copilot-instructions.md`, `*.instructions.md`, `.github/prompts/*.prompt.md`, `.github/chatmodes/*.chatmode.md`; VS Code wiring in `.vscode/settings.json` and `.vscode/mcp.json`.

### Deliverables
- Code & tests: `src/` implementation, `tests/` suites, minimal examples in docstrings.
- Developer experience: prompt files (`/plan-feature`, `/review-security`, `/generate-tests`) and modes (**Planning**, **Research**, **Test Author**).
- Integration: **GitHub MCP** server configured at workspace scope; instructions and PR/commit guidance under `.github/guidance/`.

### Directions
- Setup: install Python 3.11+, create a clean environment, install dependencies per your package manager.
- Verify: run unit tests; open VS Code, select a chat mode, and launch prompt files from the `/` picker.
- Secure: authenticate the GitHub MCP server via VS Code when prompted; use a fine‑grained PAT limited to repository contents.

---

## Part II — Allegorical (the system as a short fable)

### Direction
- In a quiet workshop, an **Archivist** keeps shards of experience, an **Orchestrator** asks the right questions, and a **Lantern** reveals only what is safe to see.
- Their pact: remember faithfully, reason carefully, and leave a chalk mark for the way back (rollback).
- Their law: never trade secrets for speed; truth wears a timestamp.

### Design
- Archivist ↔ Storage & Index: collects episodes, files them into vectors, and fetches close kin when asked.
- Orchestrator ↔ Prompts & Modes: chooses the ritual—planning, research, or test‑weaving—so effort follows intent.
- Lantern ↔ Safety & Proof: limits the gaze, cites sources when the world shifts, and guards against whispers in the margins (injections).

### Deliverables
- A map of **how** to build (instructions), **what** to ask (prompts), and **who** should speak (modes).
- A trail of tests proving the tale each time the code changes.
- A door to the outside—the MCP server—opened only with a key you hold.

### Directions
- Begin by asking the Orchestrator to plan; let the Archivist recall; confirm by the Lantern’s light.
- When in doubt, consult the margin notes: summary, contracts, side‑effects, errors, example.
- If you must undo, follow the chalk marks home and try again, slower.

