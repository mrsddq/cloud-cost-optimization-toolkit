from __future__ import annotations

import html
import json

from .models import Finding


def total_savings(findings: list[Finding]) -> float:
    return round(sum(item.estimated_monthly_savings for item in findings), 2)


def render_json(findings: list[Finding]) -> str:
    payload = {
        "finding_count": len(findings),
        "estimated_monthly_savings": total_savings(findings),
        "findings": [finding.to_dict() for finding in findings],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def render_markdown(findings: list[Finding], dry_run: bool = True) -> str:
    lines = [
        "# Cloud Cost Optimization Report",
        "",
        f"Mode: {'dry-run' if dry_run else 'reviewed action plan'}",
        f"Findings: {len(findings)}",
        f"Estimated monthly savings: ${total_savings(findings):.2f}",
        "",
        "| Severity | Check | Resource | Region | Savings | Recommendation |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]
    for finding in findings:
        lines.append(
            "| {severity} | {check} | {resource_type}/{resource_id} | {region} | ${savings:.2f} | {recommendation} |".format(
                severity=finding.severity,
                check=finding.check_id,
                resource_type=finding.resource_type,
                resource_id=finding.resource_id,
                region=finding.region,
                savings=finding.estimated_monthly_savings,
                recommendation=finding.recommendation,
            )
        )
    lines.extend(["", "No resources are modified by this report."])
    return "\n".join(lines) + "\n"


def render_html(findings: list[Finding], dry_run: bool = True) -> str:
    rows = []
    for finding in findings:
        rows.append(
            "<tr>"
            f"<td>{html.escape(finding.severity)}</td>"
            f"<td>{html.escape(finding.check_id)}</td>"
            f"<td>{html.escape(finding.resource_type)}/{html.escape(finding.resource_id)}</td>"
            f"<td>{html.escape(finding.region)}</td>"
            f"<td>${finding.estimated_monthly_savings:.2f}</td>"
            f"<td>{html.escape(finding.recommendation)}</td>"
            "</tr>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Cloud Cost Optimization Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #1f2937; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #d1d5db; padding: 8px; text-align: left; }}
    th {{ background: #f3f4f6; }}
  </style>
</head>
<body>
  <h1>Cloud Cost Optimization Report</h1>
  <p>Mode: {'dry-run' if dry_run else 'reviewed action plan'}</p>
  <p>Findings: {len(findings)}</p>
  <p>Estimated monthly savings: ${total_savings(findings):.2f}</p>
  <table>
    <thead>
      <tr><th>Severity</th><th>Check</th><th>Resource</th><th>Region</th><th>Savings</th><th>Recommendation</th></tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</body>
</html>
"""
