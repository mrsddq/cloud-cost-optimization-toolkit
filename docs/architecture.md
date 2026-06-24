# Architecture

## High-Level Flow

```mermaid
flowchart LR
    Inventory["AWS or sample inventory"] --> Checks["Cost checks"]
    Checks --> Findings["Findings"]
    Findings --> JSON["JSON report"]
    Findings --> Markdown["Markdown report"]
    Findings --> HTML["HTML report"]
    Findings --> Notify["Slack or email review"]
```

## CI/CD Flow

```mermaid
flowchart LR
    PR["Pull request"] --> Tests["Unit tests"]
    PR --> Lint["Python compile checks"]
    PR --> Security["Read-only security scan"]
    PR --> Docker["Docker Smoke"]
    Docker --> Report["Sample report output"]
```

## Local Demo Flow

```mermaid
flowchart LR
    Docker["Docker image"] --> CLI["cloud-cost-audit"]
    CLI --> Sample["examples/sample_inventory.json"]
    Sample --> Report["Markdown report"]
```

## Safety Model

The toolkit is read-only by default. It reports opportunities rather than deleting, stopping, resizing or tagging resources. Cleanup automation should be added only behind approvals, ticket links, allowlists and change windows.

## AWS Collection

The AWS adapter collects inventory through Boto3. Cost values and utilization placeholders should be enriched from Cost Explorer and CloudWatch in a production rollout.

## Extension Points

- Add Cost Explorer monthly spend enrichment.
- Add CloudWatch utilization windows per account and region.
- Write findings to S3 or an internal ticketing system.
- Add allowlisted remediation workflows after approval.
