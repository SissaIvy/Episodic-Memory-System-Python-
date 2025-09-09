chore(license): add Apache-2.0 LICENSE/NOTICE and update packaging metadata

Summary
- Add Apache-2.0 LICENSE and NOTICE template.
- Add README License section + badge.
- Align packaging metadata: license file embedded in wheels/sdists; add OS Independent + OSI classifier; authors updated.

Rationale
- Make licensing explicit and machine-detectable for scanners and registries.
- Keep legal/metadata changes isolated and auditable.

Scope
- Documentation + packaging only. No behavior change.

Validation
- Unit tests: python -m unittest discover -s tests -p "test_*.py" -v (green).
- Build: python -m build (ok).
- Twine check: python -m twine check dist/* (passed).

Follow-ups
- Squash-merge to main.
- Tag v0.2.1 “License alignment” to trigger release workflow.
- (Optional) Set default branch to main and migrate to SPDX fields when upgrading setuptools.

Notes
- CI checks: Lint and Test (Python 3.9/3.10/3.11), CLI smoke (search flags), Smoke (FAISS + NumPy) Python 3.11.

GH PR (Draft)
Create draft PR from current feature branch:
gh pr create --base main --head feat/faiss-smoke-tests --title "chore(license): add Apache-2.0 LICENSE/NOTICE and update packaging metadata" --body-file pr_body.md --draft

Or inline body (no file):
gh pr create --base main --head feat/faiss-smoke-tests --title "chore(license): add Apache-2.0 LICENSE/NOTICE and update packaging metadata" --body "Adds Apache-2.0 LICENSE and NOTICE; README License section + badge; packaging embeds LICENSE and adds classifiers; no code changes." --draft

Patch (private share)
Full branch patch against main:
git fetch origin && git format-patch origin/main..feat/faiss-smoke-tests --stdout > license-alignment.patch

Single-commit patch (latest change):
git format-patch -1 a65d9e1b3a82c793a531fcb6d43b96d439d624d9 --stdout > docs-badge-only.patch

