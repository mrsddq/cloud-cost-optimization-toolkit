# Security Controls

## Implemented

- Dry-run CLI mode.
- Read-only AWS inventory collection path.
- No cleanup or destructive AWS calls in the toolkit.
- Security scan for committed secrets and mutating AWS APIs.
- Docker image runs as a non-root user.
- Unit tests for report rendering and checks.

## Recommended Production Additions

- GitHub OIDC to AWS instead of long-lived keys.
- Account and region allowlists.
- Least-privilege read-only IAM policy.
- Trivy image scanning in CI.
- Bandit or Semgrep for Python static analysis.
- Signed release images for scheduled runs.

## Security Review Questions

- Can this code delete, stop or resize resources?
- Which IAM permissions are required for collection?
- Where are Slack webhooks and SMTP credentials stored?
- How are false positives reviewed before action?
- Are generated reports safe to share outside engineering?
