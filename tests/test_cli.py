import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
