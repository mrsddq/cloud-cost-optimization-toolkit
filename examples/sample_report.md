# Cloud Cost Optimization Report

Mode: dry-run
Findings: 8
Estimated monthly savings: $615.00

| Severity | Check | Resource | Region | Savings | Recommendation |
| --- | --- | --- | --- | ---: | --- |
| high | idle-ec2 | ec2/i-0123456789idle | us-east-1 | $560.00 | Stop, schedule, terminate, or rightsize after owner review. |
| high | unused-load-balancer | load_balancer/app/unused-lb/123 | us-east-1 | $22.00 | Confirm ownership, then remove unused listener and load balancer resources. |
| low | missing-tags | ebs/vol-0unused | us-east-1 | $0.00 | Apply required ownership, environment, and cost allocation tags. |
| low | missing-tags | ec2/i-0123456789idle | us-east-1 | $0.00 | Apply required ownership, environment, and cost allocation tags. |
| low | missing-tags | load_balancer/app/unused-lb/123 | us-east-1 | $0.00 | Apply required ownership, environment, and cost allocation tags. |
| low | old-snapshot | snapshot/snap-0old | us-east-1 | $8.00 | Confirm retention requirement, then delete if obsolete. |
| medium | unattached-ebs | ebs/vol-0unused | us-east-1 | $25.00 | Snapshot if needed, then delete after owner approval. |
| medium | oversized-instance | ec2/i-0123456789idle | us-east-1 | $252.00 | Evaluate resize to m5.xlarge in a maintenance window. |

No resources are modified by this report.
