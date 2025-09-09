import argparse, json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict_results", type=str, required=True)
    ap.add_argument("--explore_results", type=str, required=True)
    ap.add_argument("--report_json", type=str, required=True)
    args = ap.parse_args()

    strict = json.loads(Path(args.strict_results).read_text(encoding="utf-8"))
    explore = json.loads(Path(args.explore_results).read_text(encoding="utf-8"))

    def metrics(r):
        m = r["meta"]["counts"]
        actions = m.get("actions", 0)
        events = m.get("events", 1)
        failures = m.get("failures", 0)
        frate = failures / max(1, events)
        # crude proxies; refine with labeled truth later
        insights = r.get("insights", [])
        severity_weight = sum(i.get("trace", {}).get("severity", 0) for i in insights) / max(1, len(insights))
        explainability = sum(1 for i in insights if i.get("trace") and i.get("explain")) / max(1, len(insights))
        return {
            "events": events,
            "actions": actions,
            "failure_rate": frate,
            "avg_severity": round(severity_weight, 2),
            "explainability_rate": round(explainability, 2),
        }

    s = metrics(strict)
    e = metrics(explore)
    # gate examples
    gates = {
        "fail_rate_strict_max": 0.10,
        "fail_rate_explore_max": 0.15,
        "explainability_min": 0.95,
    }
    decision = "PASS"
    issues = []
    if s["failure_rate"] > gates["fail_rate_strict_max"]:
        decision = "HOLD"
        issues.append("Strict failure rate too high")
    if e["failure_rate"] > gates["fail_rate_explore_max"]:
        decision = "HOLD"
        issues.append("Explore failure rate too high")
    if min(s["explainability_rate"], e["explainability_rate"]) < gates["explainability_min"]:
        decision = "HOLD"
        issues.append("Explainability below threshold")

    report = {
        "evaluated_at_et": strict["meta"]["generated_at_et"],
        "strict": s,
        "explore": e,
        "gates": gates,
        "decision": decision,
        "issues": issues,
    }
    Path(args.report_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report_json).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()

