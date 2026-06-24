# Portfolio Evidence

This repo demonstrates safe cloud cost automation with dry-run behavior and reports. It is intentionally read-only by default.

## Verified Locally

```bash
python -m unittest discover -s tests
python -m cost_optimizer.cli --inventory examples/sample_inventory.json --format markdown --dry-run
```

Sample report summary:

```text
Findings: 8
Estimated monthly savings: $867.00
```

## Reviewer Evidence

| Evidence | Location | What it proves |
|---|---|---|
| CI badge | `README.md` | Tests and sample report rendering run in CI. |
| CLI | `cost_optimizer/cli.py` | Dry-run report generation. |
| Checks | `cost_optimizer/checks.py` | EC2, EBS, snapshots, load balancers, tags and rightsizing. |
| Reports | `cost_optimizer/reporting.py` | JSON, Markdown and HTML output. |
| AWS adapter | `cost_optimizer/aws.py` | Optional Boto3 inventory collection path. |
| Sample inventory | `examples/sample_inventory.json` | Offline recruiter-safe demo input. |
| Docker demo | `Dockerfile` | Containerized CLI that runs without AWS credentials. |
| Docker Smoke | `.github/workflows/docker-smoke.yml` | Container build and sample report execution in CI. |
| Runbook | `docs/runbook.md` | Weekly review, deletion safety and tagging policy. |
| Security scan | `scripts/security_scan.py` | Read-only guardrail and secret-pattern check. |
