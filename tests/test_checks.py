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


class MissingEvidenceTest(unittest.TestCase):
    def test_unknown_and_invalid_cpu_never_create_savings_findings(self):
        for value in (None, "", "not-a-number", float("nan"), float("inf"), -1, 101, False):
            with self.subTest(value=value):
                inventory = {"instances": [{"id": "i-1", "state": "running", "type": "m5.4xlarge", "cpu_avg_14d": value}]}
                ids = {f.check_id for f in run_all_checks(inventory)}
                self.assertFalse(ids & {"idle-ec2", "oversized-instance"})

    def test_absent_cpu_does_not_mean_zero(self):
        ids = {f.check_id for f in run_all_checks({"instances": [{"id": "i-1", "state": "running", "type": "m5.4xlarge"}]})}
        self.assertFalse(ids & {"idle-ec2", "oversized-instance"})

    def test_measured_zero_cpu_is_idle(self):
        ids = {f.check_id for f in run_all_checks({"instances": [{"id": "i-1", "state": "running", "cpu_avg_14d": 0}]})}
        self.assertIn("idle-ec2", ids)

    def test_unknown_load_balancer_metrics_are_not_zero(self):
        for metrics in ({}, {"request_count_7d": None, "healthy_target_count": None}, {"request_count_7d": 10}):
            with self.subTest(metrics=metrics):
                ids = {f.check_id for f in run_all_checks({"load_balancers": [{"id": "lb-1", **metrics}]})}
                self.assertNotIn("unused-load-balancer", ids)

    def test_observed_zero_requests_still_flags_review(self):
        findings = run_all_checks({"load_balancers": [{"id": "lb-1", "request_count_7d": 0}]})
        self.assertIn("unused-load-balancer", {f.check_id for f in findings})

    def test_in_use_or_unknown_volume_state_is_not_unattached(self):
        for state in (None, "in-use", "creating", "deleting"):
            with self.subTest(state=state):
                findings = run_all_checks({"volumes": [{"id": "vol-1", "state": state}]})
                self.assertNotIn("unattached-ebs", {f.check_id for f in findings})

    def test_available_volume_without_attachments_is_a_candidate(self):
        findings = run_all_checks({"volumes": [{"id": "vol-1", "state": "available", "attached_to": None}]})
        self.assertIn("unattached-ebs", {f.check_id for f in findings})


if __name__ == "__main__":
    unittest.main()
