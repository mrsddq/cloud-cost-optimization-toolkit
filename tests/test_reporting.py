import json
import unittest

from cost_optimizer.models import Finding
from cost_optimizer.reporting import render_html, render_json, render_markdown, total_savings


class ReportingTest(unittest.TestCase):
    def setUp(self):
        self.findings = [
            Finding(
                check_id="idle-ec2",
                severity="high",
                resource_type="ec2",
                resource_id="i-idle",
                region="us-east-1",
                message="idle",
                recommendation="stop it",
                estimated_monthly_savings=12.345,
            )
        ]

    def test_total_savings_rounds(self):
        self.assertEqual(total_savings(self.findings), 12.35)

    def test_json_report_is_parseable(self):
        payload = json.loads(render_json(self.findings))
        self.assertEqual(payload["finding_count"], 1)
        self.assertEqual(payload["estimated_monthly_savings"], 12.35)

    def test_markdown_and_html_include_resource(self):
        self.assertIn("i-idle", render_markdown(self.findings))
        self.assertIn("i-idle", render_html(self.findings))


class SavingsAggregationTest(unittest.TestCase):
    def test_alternative_actions_do_not_double_count_the_same_resource(self):
        from dataclasses import replace
        idle = Finding("idle-ec2", "high", "ec2", "i-1", "us-east-1", "", "", 100)
        resize = replace(idle, check_id="oversized-instance", estimated_monthly_savings=45)
        self.assertEqual(total_savings([idle, resize]), 100)
        self.assertEqual(total_savings([resize, idle, idle]), 100)
        self.assertEqual(json.loads(render_json([idle, resize]))["estimated_monthly_savings"], 100)

    def test_different_resource_and_region_savings_are_additive(self):
        from dataclasses import replace
        idle = Finding("idle-ec2", "high", "ec2", "i-1", "us-east-1", "", "", 100)
        self.assertEqual(total_savings([idle, replace(idle, region="us-west-2"), replace(idle, resource_id="i-2")]), 300)


if __name__ == "__main__":
    unittest.main()
