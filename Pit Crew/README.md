# PitCrew Racing Edition — README

> Translate all technical checks into race car pit crew terms so any engineer can read the board like a mechanic.

---

## Garage Overview (Define)

* Your AI model is the race car; this repo’s CI is the pit crew that inspects it on every PR and nightly.
* Two test tracks: Strict (closed course) and Explore (wild conditions) run the car through the same laps.
* The pit board shows Status, KPI, XAI (explainability), and Fail Rate for both tracks.

## Dash & Gauges (Diagnose)

* XAI ≥ 90% is the safety inspection line; if gauges aren’t readable, the car can’t race.
* Fail Rate is breakdowns per 100 laps; too many and the crew keeps the car in the garage.
* KPI is the overall health sticker; helpful, but gates (XAI & reliability) decide PASS vs HOLD.

## Race Control (Decide)

* PASS only when both tracks meet all gates; otherwise the pit board reads HOLD.
* If timelines bite, ship Strict-only behind a switch and keep a rollback tow hook ready.
* Promote Explore to default after two clean races in a row (nightly history proves it’s not luck).

## Crew Playbook (Do)

* Open the run artifacts in `mech_out/mechanic_kpi.json` to see which laps (scenarios) dragged XAI or reliability down.
* Stabilize randomness (consistent seeds) and trim risky search to remove flakiness in Explore.
* Apply targeted fixes (guards, simpler explanations, feature pruning) to lift XAI without hurting accuracy.

---

## How to Read the Status Board

* Badges: `Status`, `KPI`, `XAI`, `FailRate` report as S|E → Strict | Explore.
* Bars: blue = Strict, amber = Explore; red dashed line marks the XAI threshold (default 90%).
* Alert icon means a gate is violated; one mode failing blocks the whole build.

## Gates & Release Rules

* Explainability gate: XAI must be ≥ threshold (default 90%) on both tracks.
* Reliability gate: Explore Fail Rate should be close to Strict (typical allowance: ≤ +1% absolute).
* Consecutive runs: Require 2 passing nightlies before enabling Explore by default.

## When the Board Says HOLD

* Identify offenders: sort laps in `mechanic_kpi.json` by lowest XAI and highest fail delta.
* Fix the cluster, not the one-off: look for patterns (input class, feature range, prompt family).
* Re-test: rerun CI; confirm uplift persists across both tracks and not just the patched laps.

## Safe-to-Ship Options

* Strict-only release: gate on Strict, keep Explore feature-flagged off.
* Guarded rollout: enable Explore for internal or canary users; monitor the same gates.
* Rollback: a simple switch returns the car to Strict-only if Explore misbehaves on track.

---

## CI Wiring (Paddock Ops)

* Every PR & nightly triggers both tracks and publishes the pit board (chart + badges) to the run summary.
* Artifacts: `mech_out/mechanic_kpi.json` (per-scenario metrics), plus logs and comparisons.
* The README board image (e.g., `docs/pitcrew_live_status.png`) mirrors the latest CI snapshot.

## Local Pit Lane Shakedown

* Use the provided local task (see project scripts) to run Strict and Explore on your machine.
* Compare your local `mechanic_kpi.json` with CI to spot env drift or seed differences.
* Keep the same thresholds locally so the garage rules match race control.

## Troubleshooting Quick Hits

* Explore XAI just under 90%: reduce search breadth, simplify explanations, add monotonic/guard rules.
* Fail Rate doubles in Explore: tame randomness, de-duplicate near-identical laps, cap timeouts.
* Flaky swings run-over-run: lock seeds, pin versions, and verify identical input bundles.

---

## Glossary — Garage Slang ⇄ Tech

* Strict = closed test track; Explore = open road stress test; Lap = test scenario.
* XAI = readable gauges (explainability %); Fail Rate = breakdowns per 100 laps; KPI = windshield health sticker.
* Gate = inspection rule; HOLD = stay in garage; Rollback = tow back to Strict-only.

## FAQ (3 Laps)

* Why fail if only Explore misses? One unsafe mode can still crash the car; both tracks must clear inspection.
* Can we raise the XAI bar? Yes—treat 90% as a minimum; stricter bars increase driver trust.
* What proves stability? Two consecutive nightlies passing the same gates with stable per-lap metrics.

## Release Checklist

* Gates green on both tracks; no alerts on the board.
* Two clean nightlies with stable XAI and Fail Rate trends.
* Rollback plan documented and the switch verified in staging.

---

Owner’s Note: Ship fast when the car’s safe. If not, keep it in the garage, fix the weak subsystem, and run another two laps before green-lighting the race.