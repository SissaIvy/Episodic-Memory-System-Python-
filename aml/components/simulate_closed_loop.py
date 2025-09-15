import argparse, json, sys
from pathlib import Path

# import orchestrator from repo root
sys.path.append(".")
from closed_loop_security import build_system  # noqa: E402
from episodic_memory.json_compat import default as json_default


def stream_jsonl(path: str):
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", type=str, required=True)  # jsonl
    ap.add_argument("--profile", choices=["strict", "explore"], default="strict")
    ap.add_argument("--results_json", type=str, required=True)
    args = ap.parse_args()

    sysm = build_system(profile_name=args.profile)
    for evt in stream_jsonl(args.scenarios):
        sysm.ingest_event(evt)
    result = sysm.process_events()
    improvement = sysm.continuous_improvement()
    result["improvement"] = improvement
    Path(args.results_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.results_json).write_text(json.dumps(result, default=json_default), encoding="utf-8")
    print(json.dumps({"status": "ok", "profile": args.profile, "actions": result["meta"]["counts"].get("actions", 0)}, default=json_default))


if __name__ == "__main__":
    main()

