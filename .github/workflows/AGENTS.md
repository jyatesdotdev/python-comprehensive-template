# AGENTS.md — .github/workflows/

Two workflows, deliberately split: `ci.yml` answers "does the code work and
conform?", `security.yml` answers "is it safe?". Keep the split — security
scans are also on a weekly cron (Monday 06:00 UTC) to catch *newly disclosed*
CVEs in unchanged code, which a test-only workflow would never re-run for.

Beware: GitHub **auto-disables cron-triggered workflows after ~60 days of
repo inactivity**, silently. This happened to `security.yml` once (July 2026);
it had to be re-enabled with `gh workflow enable security.yml`. Its
`workflow_dispatch` trigger exists partly for that reason — manual runs count
as activity and make the workflow testable without a push.

## ci.yml

Lint (`ruff check` **and** `ruff format --check`) plus pytest. Note pytest
inherits `addopts` from `pyproject.toml`, so the 80% coverage gate applies in
CI even though the workflow doesn't mention coverage — don't "add coverage to
CI" twice, and don't remove it from `pyproject.toml` thinking CI still has it.
CI installs with `uv sync --frozen`: `--frozen` means the lockfile is
authoritative, so any dependency change must be accompanied by a regenerated
`uv.lock` (`uv lock`) or CI fails at install. Test/lint/security tooling (pytest, ruff, bandit, pip-audit) lives in the
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
- Suppressing a bandit finding in code requires `# nosec B###` on the line;
  ruff `# noqa` does nothing for bandit. Bandit and pip-audit live in the
  `dev` group so `make security` matches CI (`uv run bandit` / `uv run pip-audit`).
- pip-audit scans the locked **runtime** graph (`uv export --frozen --no-dev
  --no-emit-project`, then `pip-audit -r ... --no-deps --disable-pip`) so it
  does not re-resolve or install the local editable package. If it fails after
  a dependency bump, the fix is choosing a patched version, not pinning the scan.
- Trivy fs scan uses `exit-code: "1"` and `severity: CRITICAL,HIGH` so HIGH+
  findings fail the job. SARIF upload is `if: always()` so results still land
  in the Security tab when the gate fails.

## Editing rules

Actions are pinned to **commit SHAs** with the human tag in a comment
(`uses: actions/checkout@<sha> # v7`). Do not go back to floating major tags
or to trivy-action `@master`. Dependabot (`uv`, `github-actions`, `docker`,
weekly Monday) is what moves those SHAs — when bumping by hand, take the SHA
from `gh api repos/<owner>/<repo>/commits/<tag> --jq .sha`. `ci.yml` sets
`permissions: contents: read` so the default GITHUB_TOKEN cannot write.
Workflows run on pushes and PRs to `main` only — new long-lived branches need
to be added to the `branches:` filters or they get no CI.
