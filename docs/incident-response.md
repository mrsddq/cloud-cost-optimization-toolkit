# Incident Response

## Example Incidents

| Symptom | First check | Likely mitigation |
|---|---|---|
| Report shows unexpectedly high savings | Validate inventory freshness and thresholds | Re-run with known sample config and review CloudWatch data |
| Missing AWS resources | Confirm region, account and IAM permissions | Expand read-only policy or run per region |
| Slack/email notification fails | Check webhook or SMTP settings | Send report as artifact and rotate credentials if exposed |
| False positive cleanup recommendation | Review tags, ownership and dependency notes | Mark as rejected and tune threshold config |

## SLOs And SLIs

| SLO | SLI | Review path |
|---|---|---|
| Weekly report generated successfully | Successful scheduled run / expected run | CI or scheduler status |
| Zero mutating AWS calls in dry-run path | Security scan pass rate | `make security-scan` |
| Findings reviewed within 5 business days | Ticket status age | FinOps review board |

## RCA Template

1. What report or automation failed?
2. Which account, region and resource types were affected?
3. Was any real infrastructure changed?
4. Which threshold, tag or inventory input caused the issue?
5. What evidence confirmed the mitigation?
6. What guardrail will prevent recurrence?

## What I Would Improve In Production

- Add scheduled GitHub Actions or EventBridge execution.
- Add ticket creation with approval states.
- Add account and region allowlists.
- Add Cost Explorer and CloudWatch-backed confidence scores.
- Add remediation behind change-management gates.
