#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from episodic_memory import MemoryStore, load_system_from_path
from episodic_memory.models import EpisodicMemorySystem
from episodic_memory.schema import load_schema, validate_instance
from episodic_memory.embeddings import get_embedder, CachedEmbedder
from episodic_memory.faiss_index import FaissIndexManager, _MissingFaiss


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        data = load_system_from_path(args.path)
        system = EpisodicMemorySystem.from_dict(data)
    except Exception as e:
        print(f"Invalid file: {e}", file=sys.stderr)
        return 2
    ok = True
    msg = None
    if args.schema:
        schema = load_schema(args.schema if args.schema != "auto" else None)
        ok, msg = validate_instance(data, schema)
    print("OK: Parsed episodic memory system")
    print(json.dumps({
        "total_memories": system.system_metadata.total_memories,
        "embedding_dimension": system.system_metadata.embedding_dimension,
    }, indent=2))
    if args.schema:
        if ok:
            print("Schema validation: OK")
        else:
            print("Schema validation: FAILED")
            print(msg or "Unknown schema error", file=sys.stderr)
            return 3
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    store = MemoryStore.load(args.path)
    if args.threshold is not None:
        store.system.system_metadata.configuration.similarity_threshold = float(args.threshold)
    results = store.search(args.query, top_k=args.top_k)
    if not results:
        print("No results above threshold.")
        return 0
    for r in results:
        print(f"- id={r.memory_id} score={r.score:.3f} sim={r.similarity:.3f} importance={r.importance:.2f}")
        print(f"  text: {r.raw_text}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    store = MemoryStore.load(args.path)
    embedder = None
    if args.embedder:
        base = get_embedder(args.embedder, model=args.openai_model)
        embedder = CachedEmbedder(base, backend_name=args.embedder, model_id=args.openai_model)
    mem_id = store.add_memory(
        raw_text=args.text,
        context_tags=args.tags,
        importance_score=args.importance,
        reward_signal=args.reward,
        emotional_tone=args.tone,
        embedder=embedder,
        embed_dim=args.embed_dim,
        location=args.location,
        source="cli",
        user_id=args.user_id,
    )
    store.save(args.path)
    print(f"Added memory: {mem_id}")
    return 0


def cmd_schema_validate(args: argparse.Namespace) -> int:
    try:
        data = load_system_from_path(args.path)
        schema = load_schema(args.schema if args.schema != "auto" else None)
        ok, msg = validate_instance(data, schema)
        if ok:
            print("Schema validation: OK")
            return 0
        print("Schema validation: FAILED")
        print(msg or "Unknown error", file=sys.stderr)
        return 3
    except Exception as e:
        print(f"Validation error: {e}", file=sys.stderr)
        return 2


def _write_output(data: dict, in_path: str, out_path: str | None, in_place: bool) -> str:
    path = in_path if in_place and not out_path else (out_path or in_path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def cmd_fix(args: argparse.Namespace) -> int:
    # Load messy file -> last object, coerce minimal consistency, optional re-embed and rebuild indexes
    data = load_system_from_path(args.path)
    system = EpisodicMemorySystem.from_dict(data)
    store = MemoryStore(system)

    # Ensure counts
    system.system_metadata.total_memories = len(system.memory_entries)

    # Embedding dimension reconciliation
    dims = {len(v.encoded_experience.vector_embedding) for v in system.memory_entries.values() if v.encoded_experience.vector_embedding}
    target_dim = args.embed_dim or (dims.pop() if len(dims) == 1 else (max(dims) if dims else system.system_metadata.embedding_dimension))
    if args.reembed or len(dims) > 0 or system.system_metadata.embedding_dimension != target_dim:
        base = get_embedder(args.embedder, model=args.openai_model) if args.embedder else get_embedder("hash")
        embedder = CachedEmbedder(base, backend_name=args.embedder or "hash", model_id=args.openai_model)
        store.reembed_all(embedder, dim=target_dim)
    else:
        # still align metadata dim
        system.system_metadata.embedding_dimension = target_dim

    # Fill missing last_accessed/time_index
    for entry in system.memory_entries.values():
        if not entry.index_map.last_accessed:
            entry.index_map.last_accessed = entry.memory_stamp.timestamp
        if not entry.index_map.time_index:
            entry.index_map.time_index = entry.memory_stamp.timestamp[:10]

    # Rebuild indexes for consistency
    store.rebuild_indexes()

    # Optionally validate against schema
    out_dict = store.to_dict()
    if args.schema:
        schema = load_schema(args.schema if args.schema != "auto" else None)
        ok, msg = validate_instance(out_dict, schema)
        if not ok:
            print("Warning: Schema validation failed post-fix:")
            print(msg or "Unknown schema error", file=sys.stderr)

    # Write out
    written = _write_output(out_dict, args.path, args.output, args.in_place)
    print(f"Wrote fixed file to: {written}")
    return 0


def cmd_index_build(args: argparse.Namespace) -> int:
    store = MemoryStore.load(args.path)
    try:
        mgr = FaissIndexManager.build_from_store(store, batch_size=args.batch_size, sleep_ms=args.sleep_ms)
        mgr.save(args.index)
        print(f"Index built and saved to: {args.index}")
        return 0
    except _MissingFaiss as e:
        print(str(e), file=sys.stderr)
        return 2


def cmd_index_search(args: argparse.Namespace) -> int:
    try:
        mgr = FaissIndexManager.load(args.index)
    except _MissingFaiss as e:
        print(str(e), file=sys.stderr)
        return 2
    # Build embedder and compute query vector
    store = MemoryStore.load(args.path)
    base = get_embedder(args.embedder, model=args.openai_model) if args.embedder else get_embedder("hash")
    embedder = CachedEmbedder(base, backend_name=args.embedder or "hash", model_id=args.openai_model)
    # Use index dimension to avoid mismatches
    dim = mgr.dim if hasattr(mgr, "dim") else store.system.system_metadata.embedding_dimension
    qv = embedder.embed(args.query, dim)
    hits = mgr.search(qv, top_k=args.top_k)
    for mid, score in hits:
        entry = store.system.memory_entries.get(mid)
        snippet = (entry.encoded_experience.raw_text[:120] + "...") if entry else ""
        print(f"- id={mid} score={score:.3f} text={snippet}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Episodic Memory CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="Validate and summarize the JSON file")
    v.add_argument("path", help="Path to EpisodicMemorySystem.json")
    v.add_argument("--schema", nargs="?", const="auto", default=None, help="Validate against JSON Schema (provide path or use 'auto')")
    v.set_defaults(func=cmd_validate)

    s = sub.add_parser("search", help="Search memories by query text")
    s.add_argument("path", help="Path to EpisodicMemorySystem.json")
    s.add_argument("query", help="Query text")
    s.add_argument("--top-k", type=int, default=5)
    s.add_argument("--threshold", type=float, default=None, help="Override similarity threshold for this search")
    s.set_defaults(func=cmd_search)

    a = sub.add_parser("add", help="Add a new memory entry")
    a.add_argument("path", help="Path to EpisodicMemorySystem.json")
    a.add_argument("text", help="Raw text to store")
    a.add_argument("--tags", nargs="*", default=[], help="Context tags")
    a.add_argument("--importance", type=float, default=0.5)
    a.add_argument("--reward", type=float, default=0.0)
    a.add_argument("--tone", default="neutral")
    a.add_argument("--location", default="")
    a.add_argument("--user-id", default="")
    a.add_argument("--embedder", choices=["hash", "openai"], default=None, help="Embedding backend for this add")
    a.add_argument("--openai-model", default=None, help="OpenAI embedding model (if using openai)")
    a.add_argument("--embed-dim", type=int, default=None, help="Embedding dimension override")
    a.set_defaults(func=cmd_add)

    sv = sub.add_parser("schema-validate", help="Validate file strictly against JSON Schema")
    sv.add_argument("path", help="Path to EpisodicMemorySystem.json")
    sv.add_argument("--schema", nargs="?", const="auto", default="auto", help="Schema path or 'auto'")
    sv.set_defaults(func=cmd_schema_validate)

    fx = sub.add_parser("fix", help="Fix and normalize file, optionally re-embed and rebuild indexes")
    fx.add_argument("path", help="Path to EpisodicMemorySystem.json")
    fx.add_argument("--in-place", action="store_true", help="Write changes back to the same file")
    fx.add_argument("--output", default=None, help="Optional output path")
    fx.add_argument("--schema", nargs="?", const="auto", default=None, help="Schema validation after fix")
    fx.add_argument("--embedder", choices=["hash", "openai"], default=None, help="Embedding backend for re-embedding")
    fx.add_argument("--openai-model", default=None, help="OpenAI embedding model (if using openai)")
    fx.add_argument("--embed-dim", type=int, default=None, help="Target embedding dimension for fix")
    fx.add_argument("--reembed", action="store_true", help="Force re-embedding all entries")
    fx.set_defaults(func=cmd_fix)

    ib = sub.add_parser("index-build", help="Build a FAISS index for fast search")
    ib.add_argument("path", help="Path to EpisodicMemorySystem.json")
    ib.add_argument("index", help="Path to write FAISS index (e.g., index.faiss)")
    ib.add_argument("--batch-size", type=int, default=1024)
    ib.add_argument("--sleep-ms", type=int, default=0, help="Sleep between batches to reduce CPU spikes")
    ib.set_defaults(func=cmd_index_build)

    isr = sub.add_parser("index-search", help="Search using a pre-built FAISS index")
    isr.add_argument("path", help="Path to EpisodicMemorySystem.json for metadata lookup")
    isr.add_argument("index", help="Path to FAISS index (.faiss)")
    isr.add_argument("query", help="Query text")
    isr.add_argument("--top-k", type=int, default=5)
    isr.add_argument("--embedder", choices=["hash", "openai", "local"], default=None)
    isr.add_argument("--openai-model", default=None)
    isr.set_defaults(func=cmd_index_search)

    return p


def main(argv: list[str] | None = None) -> int:
    p = build_parser()
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
