#!/usr/bin/env python3
"""
Mechanic Agent CLI

Wires the persona's api.functions to a lightweight CLI that operates on
local artifacts (mech_out/*.json, aml_out/*.json) and emits reports under
reports/.

Functions:
  - inspect_gradients --run-id RUN --window-steps N
  - compute_metric_rollups --run-id RUN [--baseline PATH] [--current PATH]
  - assess_crew_health --time-window W [--include-security true|false]
  - recommend_repairs --findings-report-id PATH
  - release_go_no_go --candidate-run-id RUN

Usage examples:
  python agents/mechanic_agent.py assess_crew_health --time-window 24h
  python agents/mechanic_agent.py compute_metric_rollups --run-id local
  python agents/mechanic_agent.py release_go_no_go --candidate-run-id local

Notes:
  - This is a stub agent. It prefers measured data if available but falls
    back to reasonable defaults when signals are missing.
  - Outputs are JSON printed to stdout and, for some calls, also written
    under reports/ as per the persona's outputs section.
"""
from __future__ import annotations

import argparse
import json
from episodic_memory.json_compat import default as json_default
import math
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parents[1]
PERSONA_PATH = REPO_ROOT / "personas" / "archetypes.mechanic.master_ase.v1.json"
MECH_OUT = REPO_ROOT / "mech_out" / "mechanic_kpi.json"
MECH_OUT_HOLD = REPO_ROOT / "mech_out_hold" / "mechanic_kpi.json"
AML_REPORT = REPO_ROOT / "aml_out" / "report.json"
SEC_REPORT = REPO_ROOT / "aml_out" / "security_report.json"
REPORTS_DIR = REPO_ROOT / "reports"


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def _now_et_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _ensure_reports_dir() -> None:
    (REPORTS_DIR / "gradients").mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "gates").mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "health").mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "patch_plans").mkdir(parents=True, exist_ok=True)


def _derive_run_id(current: Dict[str, Any]) -> str:
    ts = (current or {}).get("evaluated_at_et") or _now_et_iso()
    ts_sanitized = ts.replace(":", "").replace("-", "").replace(".", "")
    return f"run_{ts_sanitized}"


def _delta(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    try:
        return float(a) - float(b)
    except Exception:
        return None


def inspect_gradients(run_id: str | None, window_steps: int) -> Dict[str, Any]:
    """Stub gradient inspection.
    Uses available KPI signals as a proxy to set severity and produces
    an empty findings list for now.
    """
    current = _load_json(MECH_OUT)
    if not run_id:
        run_id = _derive_run_id(current)
    findings: list[dict] = []

    # Severity heuristic: if explore explainability below gate, flag yellow; otherwise green.
    xai_e = (current.get("explore") or {}).get("explainability_rate") if current else None
    gates = (current.get("gates") or {}) if current else {}
    xai_min = gates.get("explainability_min", 0.95)
    severity = "green"
    if isinstance(xai_e, (int, float)) and xai_e < float(xai_min):
        severity = "yellow"

    _ensure_reports_dir()
    out_path = REPORTS_DIR / "gradients" / f"{run_id}.json"
    payload = {
        "run_id": run_id,
        "generated_at": _now_et_iso(),
        "window_steps": int(window_steps),
        "grad_findings": findings,
        "severity": severity,
    }
    out_path.write_text(json.dumps(payload, indent=2, default=json_default), encoding="utf-8")
    return {"report_id": str(out_path), "grad_findings": findings, "severity": severity}


def compute_metric_rollups(run_id: str | None, window: str, slices: list[str] | None,
                           current_path: Path | None, baseline_path: Path | None) -> Dict[str, Any]:
    current = _load_json(Path(current_path) if current_path else MECH_OUT)
    baseline = _load_json(Path(baseline_path) if baseline_path else MECH_OUT_HOLD)
    if not current:
        raise SystemExit("No current metrics found (mech_out/mechanic_kpi.json)")
    if not run_id:
        run_id = _derive_run_id(current)

    def grab(d: Dict[str, Any], *keys: str) -> float | None:
        v = d
        try:
            for k in keys:
                v = v.get(k)  # type: ignore
            return float(v) if v is not None else None
        except Exception:
            return None

    deltas = {
        "overall_kpi": _delta(grab(current, "overall_kpi"), grab(baseline, "overall_kpi")),
        "strict": {
            "kpi": _delta(grab(current, "strict", "kpi"), grab(baseline, "strict", "kpi")),
            "failure_rate": _delta(grab(current, "strict", "failure_rate"), grab(baseline, "strict", "failure_rate")),
            "explainability_rate": _delta(grab(current, "strict", "explainability_rate"), grab(baseline, "strict", "explainability_rate")),
        },
        "explore": {
            "kpi": _delta(grab(current, "explore", "kpi"), grab(baseline, "explore", "kpi")),
            "failure_rate": _delta(grab(current, "explore", "failure_rate"), grab(baseline, "explore", "failure_rate")),
            "explainability_rate": _delta(grab(current, "explore", "explainability_rate"), grab(baseline, "explore", "explainability_rate")),
        },
    }
    return {
        "dashboard_url": "ui/pitcrew-dashboard/index.html",
        "window": window,
        "run_id": run_id,
        "deltas_vs_baseline": deltas,
    }


def assess_crew_health(time_window: str, include_security: bool) -> Dict[str, Any]:
    """Compute PitCrewHealthIndex using available signals and sensible defaults."""
    current = _load_json(MECH_OUT)
    gates = (current.get("gates") or {}) if current else {}
    overall_kpi = float(current.get("overall_kpi", 0.0) or 0.0)
    strict = current.get("strict") or {}
    explore = current.get("explore") or {}

    # ModelPerf (0..100) from overall_kpi
    model_perf = max(0.0, min(100.0, float(overall_kpi)))

    # DataHealth heuristic from explainability vs gate
    xai_min = float(gates.get("explainability_min", 0.95) or 0.95)
    min_xai = min(float(strict.get("explainability_rate", 0.0) or 0.0), float(explore.get("explainability_rate", 0.0) or 0.0))
    data_health = 85.0
    if min_xai < xai_min:
        deficit = (xai_min - min_xai) * 100.0  # percent points
        data_health = max(55.0, 85.0 - deficit)  # penalize more as farther from gate

    # GradStability heuristic from failure rate spread
    fr_s = float(strict.get("failure_rate", 0.0) or 0.0)
    fr_e = float(explore.get("failure_rate", 0.0) or 0.0)
    spread = max(0.0, fr_e - fr_s)
    grad_stability = 82.0 - (spread * 400.0)  # 0.01 spread -> -4 pts
    grad_stability = max(50.0, min(90.0, grad_stability))

    # ServingSLO: default healthy unless evidence says otherwise
    serving_slo = 86.0

    # Fairness: no direct signal; default mid-high pending actual audits
    fairness = 80.0

    # Security: prefer security_report.json if present
    security = 84.0
    if include_security and SEC_REPORT.exists():
        sec = _load_json(SEC_REPORT)
        security = 88.0 if sec.get("decision") == "PASS" else 68.0

    contrib = {
        "ModelPerf": round(model_perf, 1),
        "DataHealth": round(data_health, 1),
        "GradStability": round(grad_stability, 1),
        "ServingSLO": round(serving_slo, 1),
        "Fairness": round(fairness, 1),
        "Security": round(security, 1),
    }

    index = (
        0.30 * contrib["ModelPerf"]
        + 0.20 * contrib["DataHealth"]
        + 0.20 * contrib["GradStability"]
        + 0.15 * contrib["ServingSLO"]
        + 0.10 * contrib["Fairness"]
        + 0.05 * contrib["Security"]
    )
    index = round(index, 1)

    band = "red"
    if index >= 85:
        band = "green"
    elif index >= 70:
        band = "yellow"

    payload = {
        "computed_at": _now_et_iso(),
        "time_window": time_window,
        "health_index": index,
        "band": band,
        "contributors": contrib,
        "inputs": {
            "mech_out": str(MECH_OUT),
            "aml_report": str(AML_REPORT) if AML_REPORT.exists() else None,
            "security_report": str(SEC_REPORT) if SEC_REPORT.exists() else None,
        },
    }

    _ensure_reports_dir()
    date_key = datetime.utcnow().strftime("%Y-%m-%d")
    out_path = REPORTS_DIR / "health" / f"{date_key}.json"
    out_path.write_text(json.dumps(payload, indent=2, default=json_default), encoding="utf-8")
    return payload


def recommend_repairs(findings_report_id: str) -> Dict[str, Any]:
    """Generate a patch plan based on issues in aml_out/report.json or the provided report."""
    source = Path(findings_report_id)
    if not source.exists():
        # Fall back to the main AML report
        source = AML_REPORT
    rep = _load_json(source)
    issues = rep.get("issues") or []

    steps: list[dict] = []
    owners = {
        "explainability": "#Evaluator",
        "fail_rate": "#Trainer",
        "drift": "#DataWrangler",
        "latency": "#Deployer",
    }

    if any("Explainability" in str(i) for i in issues):
        steps.append({
            "step": "Lift explainability to gate on both tracks",
            "owner": owners["explainability"],
            "eta_hours": 8,
            "actions": [
                "stabilize randomness (seed, sampling)",
                "simplify/structure explanations",
                "prune risky search branches",
            ],
        })
    if any("failure rate" in str(i).lower() for i in issues):
        steps.append({
            "step": "Reduce failure rate drift in Explore",
            "owner": owners["fail_rate"],
            "eta_hours": 6,
            "actions": [
                "cap timeouts and de-duplicate laps",
                "add guards for known error classes",
            ],
        })

    if not steps:
        steps.append({
            "step": "No critical issues detected; run nightly confirmatory checks",
            "owner": "#CrewChief",
            "eta_hours": 0,
            "actions": [],
        })

    _ensure_reports_dir()
    rid = f"plan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    out_path = REPORTS_DIR / "patch_plans" / f"{rid}.json"
    payload = {"patch_plan": steps, "source": str(source)}
    out_path.write_text(json.dumps(payload, indent=2, default=json_default), encoding="utf-8")
    return payload


def release_go_no_go(candidate_run_id: str) -> Dict[str, Any]:
    rep = _load_json(AML_REPORT)
    if not rep:
        # Fallback to mech_out decision if aml_out missing
        mo = _load_json(MECH_OUT)
        decision_src = "mech_out"
        dec = mo.get("decision", "HOLD")
        gates = mo.get("gates") or {}
        strict = mo.get("strict") or {}
        explore = mo.get("explore") or {}
    else:
        decision_src = "aml_out/report.json"
        dec = rep.get("decision", "HOLD")
        gates = rep.get("gates") or {}
        strict = rep.get("strict") or {}
        explore = rep.get("explore") or {}

    xai_min = float(gates.get("explainability_min", 0.95) or 0.95)
    min_xai = min(float(strict.get("explainability_rate", 0.0) or 0.0), float(explore.get("explainability_rate", 0.0) or 0.0))
    xai_gap = xai_min - min_xai

    if dec == "PASS":
        out_dec = "GO"
    else:
        # If only slightly below XAI gate, allow CANARY_ONLY
        out_dec = "CANARY_ONLY" if xai_gap > 0 and xai_gap <= 0.02 else "NO_GO"

    ev_refs = []
    if AML_REPORT.exists():
        ev_refs.append(str(AML_REPORT))
    if MECH_OUT.exists():
        ev_refs.append(str(MECH_OUT))

    return {
        "decision": out_dec,
        "rationale": f"base decision={dec} from {decision_src}; xai_gap={xai_gap:.3f}",
        "evidence_refs": ev_refs,
        "dashboard_url": "ui/pitcrew-dashboard/index.html",
        "candidate_run_id": candidate_run_id,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="mechanic_agent", description="Mechanic persona API functions")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("inspect_gradients")
    s1.add_argument("--run-id", default=None)
    s1.add_argument("--window-steps", type=int, default=500)

    s2 = sub.add_parser("compute_metric_rollups")
    s2.add_argument("--run-id", default=None)
    s2.add_argument("--window", default="24h")
    s2.add_argument("--slices", nargs="*", default=None)
    s2.add_argument("--current", type=Path, default=None)
    s2.add_argument("--baseline", type=Path, default=None)

    s3 = sub.add_parser("assess_crew_health")
    s3.add_argument("--time-window", default="24h")
    s3.add_argument("--include-security", default="true")

    s4 = sub.add_parser("recommend_repairs")
    s4.add_argument("--findings-report-id", required=True)

    s5 = sub.add_parser("release_go_no_go")
    s5.add_argument("--candidate-run-id", required=True)

    args = ap.parse_args(argv)

    # Touch persona to ensure presence; not strictly required for logic
    _ = _load_json(PERSONA_PATH)

    if args.cmd == "inspect_gradients":
        out = inspect_gradients(args.run_id, args.window_steps)
    elif args.cmd == "compute_metric_rollups":
        out = compute_metric_rollups(args.run_id, args.window, args.slices, args.current, args.baseline)
    elif args.cmd == "assess_crew_health":
        include_sec = str(args.include_security).lower() in {"1", "true", "yes", "y"}
        out = assess_crew_health(args.time_window, include_sec)
    elif args.cmd == "recommend_repairs":
        out = recommend_repairs(args.findings_report_id)
    elif args.cmd == "release_go_no_go":
        out = release_go_no_go(args.candidate_run_id)
    else:
        raise SystemExit("unknown command")

    print(json.dumps(out, indent=2, default=json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

