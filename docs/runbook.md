# Runbook

## Prerequisites

- Python 3.11+
- Docker for container demo
- AWS credentials only when using `--from-aws`
- Read-only IAM permissions for discovery mode

## Validate

```bash
make test
make lint
make security-scan
```

## Local Demo

```bash
make sample-markdown
make local-demo
```

## AWS Dry Run

```bash
pip install ".[aws]"
python -m cost_optimizer.cli --from-aws --region us-east-1 --format markdown --dry-run
```

## Weekly Cost Review

1. Run the CLI in dry-run mode.
2. Review high-severity findings first.
3. Confirm owner tags before action.
4. Create cleanup tickets with estimated savings.
5. Track accepted, rejected, and postponed recommendations.

## Before Deleting Resources

- Confirm owner and environment.
- Check recent usage and dependencies.
- Snapshot volumes if recovery is required.
- Keep evidence in the ticket.
- Execute cleanup outside this toolkit until remediation workflows have explicit approvals.

## Tagging Policy

Required tags:

- `Owner`
- `CostCenter`
- `Environment`

Resources missing these tags should be treated as governance findings even if no immediate savings are available.

## Rollback

This toolkit does not mutate infrastructure. Rollback means reverting report configuration, restoring the previous container image, or rerunning the prior version of the CLI.

## Backup And Restore

- Keep generated reports in durable storage if they support financial decisions.
- Version `config/example.json`-style threshold files in Git.
- Store ticket links and accepted/rejected decisions outside ephemeral CI logs.
