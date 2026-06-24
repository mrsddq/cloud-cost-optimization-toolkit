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


if __name__ == "__main__":
    unittest.main()
