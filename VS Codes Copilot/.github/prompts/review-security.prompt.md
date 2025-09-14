---
mode: "ask"
description: Perform a focused security review on changed files.
tools: ["codebase","search"]
---
Review the selected diff for:
- Input validation, authz/authn, secret handling, logging (PII/PHI), dependency risk.
- OWASP checks (injection, XSS, SSRF, deserialization), unsafe crypto/random.
- Output: Markdown report with findings grouped by severity + actionable fixes.
