# Azure ML Battle-Test for Closed-Loop Security System

This folder (`aml/`) contains an offline, deterministic battle-test for `closed_loop_security.py` using Azure Machine Learning components and a pipeline. It generates synthetic events, simulates strict vs exploratory profiles, evaluates gates, and optionally emits a bandit allocation suggestion.

## Contents

- Environment: `aml/env/conda.yml`
- Components:
  - `generate_scenarios` (JSONL synthetic events)
  - `simulate_closed_loop` (invokes orchestrator)
  - `evaluate_personas` (gates & metrics)
  - `bandit_allocator` (optional traffic split)
- Pipeline: `aml/pipelines/closed_loop_battletest.pipeline.yaml`
- Submitters: `aml/submit/submit_pipeline.sh`, `aml/submit/submit_pipeline.py`
- Sample data: `aml/data/scenarios.template.jsonl`

## Local quick check (no Azure account required)

```bash
python aml/components/generate_scenarios.py --n_events 50 --out_path /tmp/scenarios.jsonl
python aml/components/simulate_closed_loop.py --scenarios /tmp/scenarios.jsonl --profile strict --results_json /tmp/strict.json
python aml/components/simulate_closed_loop.py --scenarios /tmp/scenarios.jsonl --profile explore --results_json /tmp/explore.json
python aml/components/evaluate_personas.py --strict_results /tmp/strict.json --explore_results /tmp/explore.json --report_json /tmp/report.json
cat /tmp/report.json
```

## Azure ML (CLI) — one-time setup then submit

```bash
# Install ML extension
az extension add -n ml --yes

# (Optional) create compute
az ml compute create --name cpu-cluster --size STANDARD_DS3_V2 --min-instances 0 --max-instances 3 --type amlcompute || true

# Register env + components, then submit pipeline
bash aml/submit/submit_pipeline.sh
```

## Azure ML (SDK) alternative

```bash
export AZURE_SUBSCRIPTION_ID="<sub>"
export AZURE_RESOURCE_GROUP="<rg>"
export AZUREML_WORKSPACE_NAME="<ws>"
python aml/submit/submit_pipeline.py --seed 42 --n-events 500 --bandit-enable false
```

## Gates and decisions

Evaluation reports PASS/HOLD based on:
- strict failure_rate <= 0.10
- explore failure_rate <= 0.15
- explainability_rate >= 0.95 for both

All steps operate in dry-run overlays; no external side effects.

