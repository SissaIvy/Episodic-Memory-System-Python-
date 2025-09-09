"""
Submit the closed-loop battle-test pipeline via AML SDK v2.

Requires environment variables:
- AZURE_SUBSCRIPTION_ID
- AZURE_RESOURCE_GROUP
- AZUREML_WORKSPACE_NAME

Usage:
  python aml/submit/submit_pipeline.py --bandit-enable false --seed 42 --n-events 500
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import AmlCompute
from azure.ai.ml import load_component, load_job


def ensure_compute(ml_client: MLClient, name: str = "cpu-cluster") -> None:
    try:
        _ = ml_client.compute.get(name)
        return
    except Exception:
        pass
    comp = AmlCompute(name=name, size="STANDARD_DS3_V2", min_instances=0, max_instances=3)
    ml_client.begin_create_or_update(comp).wait()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-events", type=int, default=500)
    ap.add_argument("--bandit-enable", type=str, default="false")
    args = ap.parse_args()

    sub = os.environ["AZURE_SUBSCRIPTION_ID"]
    rg = os.environ["AZURE_RESOURCE_GROUP"]
    ws = os.environ["AZUREML_WORKSPACE_NAME"]

    cred = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
    ml_client = MLClient(cred, sub, rg, ws)

    ensure_compute(ml_client, "cpu-cluster")

    # Register components (loads from YAML in repo)
    comps_dir = Path("aml/components")
    for comp_yaml in [
        "generate_scenarios.yaml",
        "simulate_closed_loop.yaml",
        "evaluate_personas.yaml",
        "bandit_allocator.yaml",
    ]:
        comp = load_component(source=str(comps_dir / comp_yaml))
        ml_client.components.create_or_update(comp)

    # Load and submit pipeline job
    pipeline_job = load_job(source="aml/pipelines/closed_loop_battletest.pipeline.yaml")
    pipeline_job.inputs["seed"] = args.seed
    pipeline_job.inputs["n_events"] = args.n_events
    pipeline_job.inputs["bandit_enable"] = args.bandit_enable.lower() in {"1", "true", "yes"}

    submitted = ml_client.jobs.create_or_update(pipeline_job)
    print(f"Submitted job: {submitted.name}")
    print(f"Studio link: {submitted.studio_url}")


if __name__ == "__main__":
    main()

