# Runbook

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

## Tagging Policy

Required tags:

- `Owner`
- `CostCenter`
- `Environment`

Resources missing these tags should be treated as governance findings even if no immediate savings are available.
