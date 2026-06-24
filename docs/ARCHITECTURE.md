# Architecture

The toolkit uses a simple pipeline:

1. Collect inventory from JSON or AWS.
2. Run independent checks.
3. Convert findings into reports.
4. Send the report to humans for review.

## Safety Model

The first version is read-only. It intentionally reports opportunities rather than deleting or resizing resources. Cleanup automation can be added later behind approvals, tickets, and allowlists.

## AWS Collection

The AWS adapter collects resource inventory through Boto3. Cost values and utilization placeholders should be enriched from Cost Explorer and CloudWatch in a production rollout.
