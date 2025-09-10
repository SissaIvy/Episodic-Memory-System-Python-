### SISSA PitCrew — Live Status

![status](badges/status.svg) ![kpi](badges/kpi.svg) ![xai](badges/xai.svg) ![failrate](badges/failrate.svg)

![metrics](badges/metrics.svg)

<details>
<summary>More visuals</summary>

![pit lanes](badges/metrics_pitlanes.svg)

![redline stacks](badges/metrics_stacks.svg)

![telemetry bars](badges/metrics_telemetry.svg)

</details>

Nightly and on every PR, PitCrew runs the offline battle‑test (scenarios → simulator strict/explore → evaluator) and refreshes these badges. PASS/HOLD follows the evaluator’s gates (failure rates and explainability thresholds). Details: see `mech_out/mechanic_kpi.json` and CI job summaries.
