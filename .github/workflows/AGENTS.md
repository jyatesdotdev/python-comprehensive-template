# AGENTS.md — .github/workflows/

Two workflows, deliberately split: `ci.yml` answers "does the code work and
conform?", `security.yml` answers "is it safe?". Keep the split — security
scans are also on a weekly cron (Monday 06:00 UTC) to catch *newly disclosed*
CVEs in unchanged code, which a test-only workflow would never re-run for.

## ci.yml

Lint (`ruff check` **and** `ruff format --check`) plus pytest. Note pytest
inherits `addopts` from `pyproject.toml`, so the 80% coverage gate applies in
CI even though the workflow doesn't mention coverage — don't "add coverage to
CI" twice, and don't remove it from `pyproject.toml` thinking CI still has it.
CI installs with `uv sync --frozen`: `--frozen` means the lockfile is
authoritative, so any dependency change must be accompanied by a regenerated
`uv.lock` (`uv lock`) or CI fails at install. Test/lint tooling lives in the
`[dependency-groups] dev` group, which `uv sync` includes by default — the
production Docker image opts out with `--no-dev`.

## security.yml

- `permissions: security-events: write` exists solely so the trivy job can
  upload SARIF to the GitHub Security tab; removing it breaks that upload
  with a confusing 403.
- **bandit runs twice on purpose:** once with `|| true` to always produce the
  full JSON report artifact, then again with `-ll -ii` as the actual gate
  (fail on medium+ severity, high+ confidence findings). Don't "deduplicate"
  the two steps — they serve different purposes.
- Suppressing a bandit finding in code requires `# nosec B###` on the line
  (see the `0.0.0.0` bind in `cli/main.py`); ruff `# noqa` does nothing for
  bandit.
- pip-audit gates on vulnerable dependencies; if it fails after a dependency
  bump, the fix is choosing a patched version, not pinning the scan.

## Editing rules

Actions are pinned to major versions (`@v4`, `@v5`) except
`trivy-action@master`; prefer pinning if you touch that line. Workflows run
on pushes and PRs to `main` only — new long-lived branches need to be added
to the `branches:` filters or they get no CI.
