import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PortfolioStructureTest(unittest.TestCase):
    def test_production_docs_exist(self):
        for path in [
            "docs/architecture.md",
            "docs/runbook.md",
            "docs/incident-response.md",
            "docs/cost-estimate.md",
            "docs/security-controls.md",
        ]:
            self.assertTrue((ROOT / path).exists(), path)

    def test_docker_demo_exists(self):
        self.assertTrue((ROOT / "Dockerfile").exists())
        self.assertTrue((ROOT / "docker-compose.yml").exists())
        self.assertTrue((ROOT / ".github" / "workflows" / "docker-smoke.yml").exists())


if __name__ == "__main__":
    unittest.main()
