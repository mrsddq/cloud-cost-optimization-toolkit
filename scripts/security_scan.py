from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCAN_PATHS = ["cost_optimizer", "config", "examples", "README.md", "docs"]
SECRET_PATTERNS = {
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "generic_private_key": re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "slack_webhook": re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9/_-]+"),
}
MUTATING_AWS_CALLS = [
    "delete_volume",
    "delete_snapshot",
    "terminate_instances",
    "stop_instances",
    "modify_instance_attribute",
    "delete_load_balancer",
]


def iter_files() -> list[Path]:
    files: list[Path] = []
    for item in SCAN_PATHS:
        path = ROOT / item
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(candidate for candidate in path.rglob("*") if candidate.is_file())
    return files


def main() -> None:
    failures: list[str] = []
    for path in iter_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel_path = path.relative_to(ROOT)
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                failures.append(f"{rel_path}: matched secret pattern {name}")
        if path.parts[-2:] == ("cost_optimizer", "aws.py"):
            for call in MUTATING_AWS_CALLS:
                if call in text:
                    failures.append(f"{rel_path}: mutating AWS call is not allowed in read-only mode: {call}")

    cli_text = (ROOT / "cost_optimizer" / "cli.py").read_text(encoding="utf-8")
    if "--dry-run" not in cli_text:
        failures.append("cost_optimizer/cli.py: missing --dry-run safety flag")

    if failures:
        raise SystemExit("Security scan failed:\n" + "\n".join(failures))

    print("security scan passed")


if __name__ == "__main__":
    main()
