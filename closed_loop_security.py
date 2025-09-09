#!/usr/bin/env python3
"""
ClosedLoopSecuritySystem — profile-steerable (strict/explore), deterministic, explainable.

Usage:
  python closed_loop_security.py --profile strict --events events.json
  echo '{"entities":[],"relations":[]}' | python closed_loop_security.py --stdin --profile explore
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
import enum
import json
import time
import uuid
import argparse
import sys
import os
import hashlib


# ---------- Utilities (ET timestamp, correlation, determinism) ----------

ET_OFFSET = -4  # switch to -5 when standard time applies


def now_et() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S-04:00 ET", time.gmtime(time.time() + ET_OFFSET * 3600))


def new_correlation_id() -> str:
    return str(uuid.uuid4())


def stable_key(*parts: str) -> str:
    return hashlib.sha256("::".join(parts).encode()).hexdigest()[:12]


# ---------- Domain model ----------


class Severity(enum.IntEnum):
    INFO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class Target(enum.Enum):
    ENDPOINT = "ENDPOINT"
    NETWORK = "NETWORK"
    DATABASE = "DATABASE"


@dataclass(frozen=True)
class Event:
    id: str
    source: str
    type: str
    severity: Severity
    timestamp: float
    payload: Dict[str, Any]
    tenant_id: Optional[str] = None
    idempotency_key: Optional[str] = None


@dataclass
class Detection:
    is_anomaly: bool
    score: float
    reason: str
    suggested_protocol: Optional[str] = None


@dataclass
class Action:
    id: str
    target: Target
    name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dry_run: bool = True
    idempotency_key: Optional[str] = None


@dataclass
class ActionPlan:
    actions: List[Action]
    notes: str = ""
    created_at_et: str = field(default_factory=now_et)


@dataclass
class ActionResult:
    action_id: str
    success: bool
    details: str
    audit_ref: Optional[str] = None


@dataclass
class OverlayResult:
    results: List[ActionResult]
    all_success: bool
    policy_version: str


@dataclass
class AuditReport:
    timestamp_et: str
    overlay_policy_version: str
    entries: List[Dict[str, Any]]


# ---------- Interfaces ----------


@runtime_checkable
class Overlay(Protocol):
    def apply(self, plan: ActionPlan) -> OverlayResult: ...

    def update_policy(self, new_policy: Dict[str, Any]) -> None: ...

    def audit(self) -> AuditReport: ...


@runtime_checkable
class PersonaStrategy(Protocol):
    name: str

    def decide_protocol(self, event: Event, detection: Detection, user_ctx: Dict[str, Any]) -> str: ...


# ---------- Security Overlay & subcomponents ----------


class EndpointOverlay:
    def apply_action(self, action: Action) -> ActionResult:
        allowed = {"isolate_host", "kill_process", "quarantine_file", "notify_user"}
        if action.name not in allowed:
            return ActionResult(action.id, False, f"Unsupported endpoint action: {action.name}")
        detail = f"Endpoint {action.name} params={action.parameters} dry_run={action.dry_run}"
        return ActionResult(action.id, True, detail, audit_ref=str(uuid.uuid4()))


class NetworkOverlay:
    def apply_action(self, action: Action) -> ActionResult:
        allowed = {"block_ip", "rate_limit", "sinkhole_domain", "revoke_session"}
        if action.name not in allowed:
            return ActionResult(action.id, False, f"Unsupported network action: {action.name}")
        detail = f"Network {action.name} params={action.parameters} dry_run={action.dry_run}"
        return ActionResult(action.id, True, detail, audit_ref=str(uuid.uuid4()))


class DatabaseOverlay:
    def apply_action(self, action: Action) -> ActionResult:
        allowed = {"lock_account", "rotate_secret", "restrict_role", "enable_maintenance_mode"}
        if action.name not in allowed:
            return ActionResult(action.id, False, f"Unsupported database action: {action.name}")
        detail = f"Database {action.name} params={action.parameters} dry_run={action.dry_run}"
        return ActionResult(action.id, True, detail, audit_ref=str(uuid.uuid4()))


class SecurityOverlayImpl(Overlay):
    def __init__(self, policy_version: str = "v1"):
        self.endpoint = EndpointOverlay()
        self.network = NetworkOverlay()
        self.database = DatabaseOverlay()
        self._policy_version = policy_version
        self._audit_log: List[Dict[str, Any]] = []

    def apply(self, plan: ActionPlan) -> OverlayResult:
        # Deterministic order: by Target priority, then action name
        target_rank = {Target.ENDPOINT: 0, Target.NETWORK: 1, Target.DATABASE: 2}
        actions = sorted(plan.actions, key=lambda a: (target_rank[a.target], a.name))
        results: List[ActionResult] = []
        for action in actions:
            if action.target == Target.ENDPOINT:
                res = self.endpoint.apply_action(action)
            elif action.target == Target.NETWORK:
                res = self.network.apply_action(action)
            elif action.target == Target.DATABASE:
                res = self.database.apply_action(action)
            else:
                res = ActionResult(action.id, False, f"Unknown target: {action.target}")
            self._audit_log.append({
                "ts_et": now_et(),
                "action_id": res.action_id,
                "success": res.success,
                "details": res.details,
                "audit_ref": res.audit_ref,
            })
            results.append(res)
        return OverlayResult(results=results, all_success=all(r.success for r in results), policy_version=self._policy_version)

    def update_policy(self, new_policy: Dict[str, Any]) -> None:
        # Stub: in prod, persist and version. Here we bump a timestamp-based version.
        self._policy_version = f"v{int(time.time())}"

    def audit(self) -> AuditReport:
        return AuditReport(timestamp_et=now_et(), overlay_policy_version=self._policy_version, entries=list(self._audit_log))


# ---------- Personas ----------


class ContainmentPersona(PersonaStrategy):
    name = "Containment"

    def decide_protocol(self, event: Event, detection: Detection, user_ctx: Dict[str, Any]) -> str:
        if detection.score >= 0.8 or event.severity >= Severity.HIGH:
            return "ImmediateContainment"
        return "CautiousContainment"


class InvestigationPersona(PersonaStrategy):
    name = "Investigation"

    def decide_protocol(self, event: Event, detection: Detection, user_ctx: Dict[str, Any]) -> str:
        return "EvidencePreservation"


class AtlasPersonas:
    """Strategic layer: selects protocols based on context."""

    def __init__(self):
        self._strategies: Dict[str, PersonaStrategy] = {
            "Containment": ContainmentPersona(),
            "Investigation": InvestigationPersona(),
        }
        self._user_ctx: Dict[str, Any] = {}
        self._active_persona = "Containment"

    def initialize(self, user_context: Dict[str, Any]) -> None:
        self._user_ctx = dict(user_context or {})
        if self._user_ctx.get("audit_mode"):
            self._active_persona = "Investigation"

    def activate_protocol(self, protocol_name: str) -> None:
        self._user_ctx["protocol_hint"] = protocol_name

    def decide(self, event: Event, detection: Detection) -> str:
        persona = self._strategies[self._active_persona]
        return persona.decide_protocol(event, detection, self._user_ctx)


# ---------- AI Agent (tiers) ----------


class Tier1Detector:
    """Fast, cheap, high-recall detector with deterministic scoring."""

    def detect(self, event: Event) -> Detection:
        heuristics = {
            "failed_login": 0.4,
            "malware_alert": 0.9,
            "exfil_suspected": 0.85,
        }
        base = heuristics.get(event.type, 0.2)
        score = min(1.0, base + 0.1 * int(event.severity))
        return Detection(
            is_anomaly=score >= 0.6,
            score=score,
            reason=f"T1 heuristic on {event.type} (sev={int(event.severity)})",
            suggested_protocol="Containment" if score >= 0.8 else "Investigation" if score < 0.6 else "Containment",
        )


class Tier2Responder:
    """Translate protocol into concrete actions."""

    def craft_actions(self, event: Event, detection: Detection, protocol: str) -> ActionPlan:
        actions: List[Action] = []
        host = event.payload.get("host")
        ip = event.payload.get("ip")
        if protocol in {"ImmediateContainment", "CautiousContainment"}:
            if host:
                actions.append(
                    Action(
                        id=str(uuid.uuid4()),
                        target=Target.ENDPOINT,
                        name="isolate_host",
                        parameters={"host": host},
                        dry_run=True,
                    )
                )
            if ip and detection.score >= 0.8:
                actions.append(
                    Action(
                        id=str(uuid.uuid4()),
                        target=Target.NETWORK,
                        name="block_ip",
                        parameters={"ip": ip, "ttl_sec": 300},
                        dry_run=True,
                    )
                )
        elif protocol == "EvidencePreservation":
            if host:
                actions.append(
                    Action(
                        id=str(uuid.uuid4()),
                        target=Target.ENDPOINT,
                        name="notify_user",
                        parameters={"host": host, "message": "Preserve evidence"},
                        dry_run=True,
                    )
                )
        notes = f"Protocol={protocol}; reason={detection.reason}"
        return ActionPlan(actions=actions, notes=notes)


class Tier3Hunter:
    """Gate for high-impact changes."""

    def review(self, plan: ActionPlan, overlay_result: OverlayResult) -> Optional[str]:
        if not overlay_result.all_success:
            return "EscalateToHuman"
        high_impact = any(a.name in {"isolate_host", "block_ip"} for a in plan.actions)
        return "RequireApproval" if high_impact else None


class AIAgent:
    def __init__(self):
        self.t1 = Tier1Detector()
        self.t2 = Tier2Responder()
        self.t3 = Tier3Hunter()

    def detect_anomaly(self, event: Event) -> Detection:
        return self.t1.detect(event)

    def respond(self, action_plan: ActionPlan) -> str:
        return f"Planned {len(action_plan.actions)} actions"

    def escalate(self, to_agent: str) -> None:  # pragma: no cover - placeholder
        pass

    def receive_escalation(self, from_agent: str) -> None:  # pragma: no cover - placeholder
        pass

    def reset(self) -> None:  # pragma: no cover - placeholder
        pass


# ---------- Closed Loop Orchestrator ----------


@dataclass
class Profile:
    name: str  # "strict" or "explore"
    unknown_policy: str  # "ask" | "skip" | "default"
    explain: bool
    strict_validation: bool


PROFILES = {
    "strict": Profile("strict", "ask", True, True),
    "explore": Profile("explore", "default", True, False),
}


class ClosedLoopSecuritySystem:
    def __init__(
        self,
        personas: AtlasPersonas,
        overlay: Overlay,
        ai: AIAgent,
        profile: Profile,
        dry_run_default: bool = True,
    ):
        self.personas = personas
        self.overlay = overlay
        self.ai = ai
        self.profile = profile
        self._queue: List[Event] = []
        self._metrics: Dict[str, float] = {"events": 0, "actions": 0, "failures": 0}
        self._issues: List[str] = []
        self._dry_run_default = dry_run_default
        self._version = "2025.09.09"
        # --- Cost & token knobs (overridable via env) ---
        self._cost_assumptions = {
            # monthly fixed cloud costs (USD) you actually pay
            "apim_monthly": float(os.getenv("COST_APIM_MONTHLY", "0")),
            "function_monthly": float(os.getenv("COST_FUNCTION_MONTHLY", "0")),
            "frontdoor_monthly": float(os.getenv("COST_FRONTDOOR_MONTHLY", "0")),
            "appinsights_monthly": float(os.getenv("COST_APPINSIGHTS_MONTHLY", "0")),
            "aml_monthly": float(os.getenv("COST_AML_MONTHLY", "0")),
            # variable per-request/message estimates (USD) if you use them
            "per_event_var": float(os.getenv("COST_PER_EVENT_VAR", "0")),
            # expected monthly volume for blending fixed -> per-event
            "expected_events_month": int(os.getenv("COST_EXPECTED_EVENTS_MONTH", "1000000")),
        }
        self._token_assumptions = {
            # if you enable LLM assists later; set prices per 1K tokens (USD)
            "prompt_per_1k": float(os.getenv("TOKEN_PRICE_PROMPT_PER_1K", "0")),
            "completion_per_1k": float(os.getenv("TOKEN_PRICE_COMPLETION_PER_1K", "0")),
            # policy: fraction of events that escalate to LLM, and avg tokens
            "escalation_rate": float(os.getenv("TOKEN_ESCALATION_RATE", "0.0")),  # 0.0–1.0
            "avg_prompt_tokens": int(os.getenv("TOKEN_AVG_PROMPT_TOKENS", "0")),
            "avg_completion_tokens": int(os.getenv("TOKEN_AVG_COMPLETION_TOKENS", "0")),
        }

    # ---- Ingest ----
    def ingest_event(self, raw: Dict[str, Any]) -> None:
        # strict validation (required fields)
        req = ["id", "source", "type", "severity", "timestamp", "payload"]
        if self.profile.strict_validation and any(k not in raw for k in req):
            self._issues.append("Missing required event fields (strict).")
            return
        # normalize
        try:
            ev = Event(
                id=str(raw.get("id") or uuid.uuid4()),
                source=str(raw.get("source", "unknown")),
                type=str(raw.get("type", "unknown")),
                severity=Severity(int(raw.get("severity", 0))),
                timestamp=float(raw.get("timestamp", time.time())),
                payload=dict(raw.get("payload", {})),
                tenant_id=raw.get("tenant_id"),
                idempotency_key=raw.get("idempotency_key") or str(raw.get("id") or ""),
            )
        except Exception as e:  # pragma: no cover - defensive
            if self.profile.unknown_policy == "ask":
                self._issues.append(f"Ingest error: {e}")
            if self.profile.name == "strict":
                return
            # explore: skip hard failure, do a minimal event
            ev = Event(id=str(uuid.uuid4()), source="unknown", type="unknown", severity=Severity.INFO, timestamp=time.time(), payload={})
        # de-dupe by idempotency key
        if any(e.idempotency_key and e.idempotency_key == ev.idempotency_key for e in self._queue):
            return
        self._queue.append(ev)
        self._metrics["events"] += 1

    # ---- Process ----
    def process_events(self) -> Dict[str, Any]:
        correlation_id = new_correlation_id()
        insights: List[Dict[str, Any]] = []

        # deterministic order: by (severity desc, timestamp asc, id asc)
        self._queue.sort(key=lambda e: (-int(e.severity), e.timestamp, e.id))
        while self._queue:
            event = self._queue.pop(0)
            detection = self.ai.detect_anomaly(event)
            protocol = self.personas.decide(event, detection)
            self.personas.activate_protocol(protocol)
            plan = self.ai.t2.craft_actions(event, detection, protocol)

            for a in plan.actions:
                a.dry_run = self._dry_run_default if a.dry_run else a.dry_run
                a.idempotency_key = a.idempotency_key or stable_key(
                    event.id, a.name, json.dumps(a.parameters, sort_keys=True)
                )

            overlay_result = self.overlay.apply(plan)
            gate = self.ai.t3.review(plan, overlay_result)
            if gate == "EscalateToHuman":
                self.ai.escalate("HumanAnalyst")
                self._metrics["failures"] += 1

            self.ai.respond(plan)
            self._metrics["actions"] += len(plan.actions)

            # Explainability payload
            conf = min(1.0, max(0.0, detection.score))
            if not plan.actions:
                conf *= 0.8
            if event.type == "unknown":
                conf *= 0.7

            insights.append(
                {
                    "summary": f"{event.type} → {protocol} ({len(plan.actions)} actions)",
                    "action_count": len(plan.actions),
                    "confidence": round(conf, 2),
                    "trace": {
                        "event_id": event.id,
                        "severity": int(event.severity),
                        "detection": {
                            "is_anomaly": detection.is_anomaly,
                            "score": detection.score,
                            "reason": detection.reason,
                        },
                        "plan_notes": plan.notes,
                        "overlay_all_success": overlay_result.all_success,
                        "gate_decision": gate,
                    },
                    "explain": self.profile.explain
                    and f"Deterministically mapped {event.type}/{int(event.severity)} to '{protocol}'.",
                }
            )
        # ---- Cost & token accounting ----
        counts = dict(self._metrics)
        e = max(1, counts.get("events", 0))
        fx = (
            self._cost_assumptions["apim_monthly"]
            + self._cost_assumptions["function_monthly"]
            + self._cost_assumptions["frontdoor_monthly"]
            + self._cost_assumptions["appinsights_monthly"]
            + self._cost_assumptions["aml_monthly"]
        )
        blended_per_event = (fx / max(1, self._cost_assumptions["expected_events_month"])) + self._cost_assumptions["per_event_var"]
        run_cloud_cost = round(blended_per_event * e, 6)
        # token model (optional—zero if not configured)
        esc = self._token_assumptions
        est_escalations = e * max(0.0, min(1.0, esc["escalation_rate"]))
        est_prompt_k = (est_escalations * esc["avg_prompt_tokens"]) / 1000.0
        est_completion_k = (est_escalations * esc["avg_completion_tokens"]) / 1000.0
        token_cost = round(
            est_prompt_k * esc["prompt_per_1k"] + est_completion_k * esc["completion_per_1k"], 6
        )
        # ROI sketch (optional inputs via env)
        mttr_before = float(os.getenv("ROI_MTTR_BEFORE_MIN", "0"))
        mttr_after = float(os.getenv("ROI_MTTR_AFTER_MIN", "0"))
        incidents_month = float(os.getenv("ROI_INCIDENTS_PER_MONTH", "0"))
        cost_per_min = float(os.getenv("ROI_COST_PER_MINUTE_USD", "0"))
        monthly_savings = max(0.0, (mttr_before - mttr_after)) * incidents_month * cost_per_min
        run_cost = run_cloud_cost + token_cost
        equity_usd = float(os.getenv("ROE_EQUITY_USD", "0"))
        roe_annual = (12.0 * monthly_savings / equity_usd) if equity_usd > 0 else 0.0

        meta = {
            "generated_at_et": now_et(),
            "version": self._version,
            "profile": self.profile.name,
            "correlation_id": correlation_id,
            "counts": counts,
            "costs": {
                "blended_per_event_usd": round(blended_per_event, 6),
                "run_cloud_cost_usd": run_cloud_cost,
                "token_cost_usd": token_cost,
                "run_total_cost_usd": round(run_cost, 6),
                "assumptions": self._cost_assumptions,
            },
            "roi": {
                "monthly_savings_usd": round(monthly_savings, 2),
                "roe_annual_estimate": round(roe_annual, 2),
                "assumptions": {
                    "mttr_before_min": mttr_before,
                    "mttr_after_min": mttr_after,
                    "incidents_month": incidents_month,
                    "cost_per_min_usd": cost_per_min,
                    "equity_usd": equity_usd,
                },
            },
            "issues": self._issues,
        }
        return {"meta": meta, "insights": insights}

    # ---- Continuous improvement ----
    def continuous_improvement(self) -> Dict[str, Any]:
        failure_rate = self._metrics["failures"] / max(1, self._metrics["events"])  # float
        if failure_rate > 0.1:
            self.overlay.update_policy({"auto_quarantine_threshold": 0.85})
        audit = self.overlay.audit()
        return {
            "failure_rate": failure_rate,
            "audit_entries": len(audit.entries),
            "policy_version": audit.overlay_policy_version,
        }


# ---------- Builder & CLI ----------


def build_system(profile_name: str = "strict", audit_mode: bool = False, dry_run_default: bool = True) -> ClosedLoopSecuritySystem:
    personas = AtlasPersonas()
    personas.initialize({"audit_mode": audit_mode})
    overlay = SecurityOverlayImpl(policy_version="v1")
    ai = AIAgent()
    profile = PROFILES.get(profile_name, PROFILES["strict"])
    return ClosedLoopSecuritySystem(personas, overlay, ai, profile, dry_run_default=dry_run_default)


def _load_events(path: Optional[str], read_stdin: bool) -> List[Dict[str, Any]]:
    if read_stdin:
        txt = sys.stdin.read()
        return json.loads(txt)
    if not path:
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "events" in data:
            return data["events"]
        raise ValueError("events.json must be a list of event objects or {'events': [...]}" )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", choices=["strict", "explore"], default=os.getenv("PROFILE", "strict"))
    ap.add_argument("--events", help="Path to events.json (list or {'events':[...]})")
    ap.add_argument("--stdin", action="store_true", help="Read events JSON from stdin")
    ap.add_argument("--audit-mode", action="store_true", help="Initialize personas in Investigation mode")
    ap.add_argument("--enforce", action="store_true", help="Flip global dry_run_default to False")
    args = ap.parse_args()

    sysm = build_system(profile_name=args.profile, audit_mode=args.audit_mode, dry_run_default=not args.enforce)
    for raw in _load_events(args.events, args.stdin):
        if isinstance(raw, dict):
            sysm.ingest_event(raw)
    result = sysm.process_events()
    improve = sysm.continuous_improvement()
    result["improvement"] = improve
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
