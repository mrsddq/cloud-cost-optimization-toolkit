# Cost Estimate

The default demo is free because it runs against `examples/sample_inventory.json`.

## AWS Mode

| Component | Cost driver | Control |
|---|---|---|
| EC2, EBS, snapshots and ELB APIs | Standard API usage | Keep read-only scans periodic, not continuous |
| Cost Explorer enrichment | API requests | Cache reports and run on a weekly schedule |
| CloudWatch metrics | API requests | Query only required utilization windows |
| Notifications | Slack/email transport | Send summary first, attach full report only when needed |

## Guardrails

- Start with one sandbox account and one region.
- Run in dry-run mode first.
- Use read-only IAM permissions.
- Store generated reports with timestamps.
- Track accepted, rejected and postponed recommendations.

## Sample Savings Report

The included sample inventory produces a report with idle compute, unused storage, stale snapshots, load-balancer waste, missing tags and rightsizing opportunities. Treat sample savings as demo data, not a real forecast.
