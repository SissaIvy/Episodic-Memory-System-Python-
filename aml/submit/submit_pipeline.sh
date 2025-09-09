#!/usr/bin/env bash
set -euo pipefail

# Prereqs: Azure CLI + ML extension
# az extension add -n ml --yes

# Register environment (uses conda.yml contents). If your CLI requires explicit name/image, create via SDK alternative.
az ml environment create --file aml/env/conda.yml || true

# Register components
az ml component create --file aml/components/generate_scenarios.yaml
az ml component create --file aml/components/simulate_closed_loop.yaml
az ml component create --file aml/components/evaluate_personas.yaml
az ml component create --file aml/components/bandit_allocator.yaml

# Ensure compute exists
az ml compute create --name cpu-cluster --size STANDARD_DS3_V2 --min-instances 0 --max-instances 3 --type amlcompute || true

# Submit pipeline
az ml job create --file aml/pipelines/closed_loop_battletest.pipeline.yaml

