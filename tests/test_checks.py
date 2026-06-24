import unittest

from cost_optimizer.checks import run_all_checks


class ChecksTest(unittest.TestCase):
    def test_detects_idle_instance_and_missing_tags(self):
        inventory = {
            "instances": [
                {
                    "id": "i-idle",
                    "region": "us-east-1",
                    "type": "m5.4xlarge",
                    "state": "running",
                    "cpu_avg_14d": 2,
                    "monthly_cost": 100,
                    "tags": {"Owner": "platform"},
                }
            ]
        }
        findings = run_all_checks(inventory)
        check_ids = {finding.check_id for finding in findings}
        self.assertIn("idle-ec2", check_ids)
        self.assertIn("oversized-instance", check_ids)
        self.assertIn("missing-tags", check_ids)

    def test_healthy_inventory_has_no_findings(self):
        inventory = {
            "instances": [
                {
                    "id": "i-healthy",
                    "region": "us-east-1",
                    "type": "t3.large",
                    "state": "running",
                    "cpu_avg_14d": 50,
                    "monthly_cost": 60,
                    "tags": {"Owner": "app", "CostCenter": "prod", "Environment": "prod"},
                }
            ],
            "volumes": [],
            "snapshots": [],
            "load_balancers": [],
        }
        self.assertEqual(run_all_checks(inventory), [])


if __name__ == "__main__":
    unittest.main()
