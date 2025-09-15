#!/usr/bin/env python3
"""
PitCrew Dashboard — Self-test (CLI)
- Mirrors the normalize() logic in the React UI to ensure defaults and coercions work.
- No external dependencies. Python 3.8+.

Usage:
  python ui/pitcrew-dashboard/selftest.py            # run built-in unit tests
  python ui/pitcrew-dashboard/selftest.py mech_out/mechanic_kpi.json   # also verify a real file
"""
import json, sys, math, os

PAL = {}  # unused; present to mirror UI structure

DEFAULT_GATES = {"fr_strict": 0.10, "fr_explore": 0.15, "xai_min": 0.95}
DEFAULT_PROFILE = {"events": 0, "actions": 0, "failure_rate": 0.0, "explainability_rate": 0.0, "kpi": 0.0}
DEFAULT_DATA = {
    "evaluated_at_et": "",
    "decision": "HOLD",
    "decision_src": "recomputed",
    "strict": {**DEFAULT_PROFILE},
    "explore": {**DEFAULT_PROFILE},
    "overall_kpi": 0.0,
    "weights": {"strict": 0.7, "explore": 0.3},
    "gates": {**DEFAULT_GATES},
}


def num(n, d=0.0):
    if isinstance(n, (int, float)) and math.isfinite(n):
        return float(n)
    try:
        return float(n)
    except Exception:
        return float(d)


def normalize(raw: dict) -> dict:
    r = raw or {}
    gates = {**DEFAULT_GATES, **(r.get("gates") or {})}
    strict = {**DEFAULT_PROFILE, **(r.get("strict") or {})}
    explore = {**DEFAULT_PROFILE, **(r.get("explore") or {})}
    strict["failure_rate"] = num(strict.get("failure_rate"))
    strict["explainability_rate"] = num(strict.get("explainability_rate"))
    strict["kpi"] = num(strict.get("kpi"))
    explore["failure_rate"] = num(explore.get("failure_rate"))
    explore["explainability_rate"] = num(explore.get("explainability_rate"))
    explore["kpi"] = num(explore.get("kpi"))
    w = r.get("weights") or {}
    weights = {"strict": num(w.get("strict"), 0.7), "explore": num(w.get("explore"), 0.3)}
    out = {**DEFAULT_DATA, **r, "gates": gates, "strict": strict, "explore": explore, "overall_kpi": num(r.get("overall_kpi")), "weights": weights}
    return out


def run_unit_tests():
    cases = [
        ("fills gates when missing", {"decision": "PASS", "strict": {"kpi": 55}, "explore": {"kpi": 50}}, lambda d: isinstance(d.get("gates"), dict) and isinstance(d["gates"].get("xai_min"), float)),
        ("coerces numbers", {"strict": {"failure_rate": "0.02"}, "explore": {"failure_rate": "0.04"}}, lambda d: abs(d["strict"]["failure_rate"] - 0.02) < 1e-9 and abs(d["explore"]["failure_rate"] - 0.04) < 1e-9),
        ("weights default", {}, lambda d: abs(d["weights"]["strict"] - 0.7) < 1e-9 and abs(d["weights"]["explore"] - 0.3) < 1e-9),
    ]
    results = []
    ok = True
    for name, inp, pred in cases:
        try:
            out = normalize(inp)
            passed = bool(pred(out))
        except Exception:
            passed = False
        results.append((name, passed))
        ok = ok and passed
    return ok, results


def main(argv):
    ok, results = run_unit_tests()
    for name, passed in results:
        print(("OK" if passed else "FAIL"), name)
    if len(argv) > 1:
        path = argv[1]
        if os.path.exists(path):
            try:
                data = json.load(open(path, "r", encoding="utf-8"))
                norm = normalize(data)
                # basic sanity
                assert isinstance(norm.get("strict"), dict) and isinstance(norm.get("explore"), dict)
                print(f"OK normalized file: {path}")
            except Exception as e:
                print(f"✖ failed to normalize {path}: {e}")
                ok = False
        else:
            print(f"! file not found: {path}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
