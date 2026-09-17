import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cost_optimizer.cli import main


class CliTest(unittest.TestCase):
    def test_cli_outputs_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            inventory = Path(tmp) / "inventory.json"
            inventory.write_text(
                json.dumps(
                    {
                        "instances": [],
                        "volumes": [],
                        "snapshots": [],
                        "load_balancers": [],
                    }
                ),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                main(["--inventory", str(inventory), "--format", "json", "--dry-run"])
            payload = json.loads(buffer.getvalue())
            self.assertEqual(payload["finding_count"], 0)

    def test_aws_coverage_warning_keeps_json_stdout_parseable(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch("cost_optimizer.cli.collect_inventory", return_value={}) as collect:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                main(["--from-aws", "--region", "us-west-2", "--format", "json"])
        collect.assert_called_once_with("us-west-2")
        self.assertEqual(json.loads(stdout.getvalue())["finding_count"], 0)
        self.assertIn("not collected", stderr.getvalue())
        self.assertIn("No findings does not mean no waste", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
