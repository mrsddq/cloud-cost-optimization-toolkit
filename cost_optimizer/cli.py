from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .aws import collect_inventory
from .checks import DEFAULT_CONFIG, run_all_checks
from .reporting import render_html, render_json, render_markdown


def load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def render(findings, output_format: str, dry_run: bool) -> str:
    if output_format == "json":
        return render_json(findings)
    if output_format == "markdown":
        return render_markdown(findings, dry_run=dry_run)
    if output_format == "html":
        return render_html(findings, dry_run=dry_run)
    raise ValueError(f"unsupported format: {output_format}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find AWS cost optimization opportunities.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--inventory", help="Path to offline inventory JSON.")
    source.add_argument("--from-aws", action="store_true", help="Collect inventory from AWS.")
    parser.add_argument("--region", default="us-east-1", help="AWS region for --from-aws.")
    parser.add_argument("--config", help="Path to config JSON.")
    parser.add_argument("--format", choices=["json", "markdown", "html"], default="markdown")
    parser.add_argument("--output", help="Write report to file instead of stdout.")
    parser.add_argument("--dry-run", action="store_true", help="Report only; never modify resources.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    config = {**DEFAULT_CONFIG, **(load_json(args.config) if args.config else {})}
    inventory = collect_inventory(args.region) if args.from_aws else load_json(args.inventory)
    findings = run_all_checks(inventory, config)
    rendered = render(findings, args.format, dry_run=args.dry_run)

    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)


if __name__ == "__main__":
    main()
