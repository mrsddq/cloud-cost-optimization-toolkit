"""AWS collection contracts without credentials, network calls, or optional SDKs."""
from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import Mock

from cost_optimizer.aws import collect_inventory
from cost_optimizer.checks import run_all_checks


NOW = datetime(2026, 9, 17, tzinfo=timezone.utc)
TAGS = [{"Key": key, "Value": "demo"} for key in ("Owner", "CostCenter", "Environment")]


def client_for(pages):
    client = Mock()
    paginators = {}
    for operation, responses in pages.items():
        paginator = Mock()
        paginator.paginate.return_value = responses
        paginators[operation] = paginator
    client.get_paginator.side_effect = paginators.__getitem__
    return client, paginators


class AwsCollectionTest(unittest.TestCase):
    def setUp(self):
        self.ec2, self.paginators = client_for({
            "describe_instances": [
                {"Reservations": [{"Instances": [{
                    "InstanceId": f"i-{number}", "InstanceType": "m5.4xlarge",
                    "State": {"Name": "running"}, "Tags": TAGS,
                }]}]} for number in (1, 2)
            ],
            "describe_volumes": [
                {"Volumes": [{"VolumeId": f"vol-{number}", "State": "available",
                              "Size": 10, "Tags": TAGS}]} for number in (1, 2)
            ],
            "describe_snapshots": [
                {"Snapshots": [{"SnapshotId": f"snap-{age}", "StartTime": NOW - timedelta(days=age),
                                "Tags": TAGS}]} for age in (5, 120)
            ],
        })
        self.elb, _ = client_for({"describe_load_balancers": [
            {"LoadBalancers": [{"LoadBalancerArn": f"arn:lb:{i}"} for i in range(15)]},
            {"LoadBalancers": [{"LoadBalancerArn": f"arn:lb:{i}"} for i in range(15, 25)]},
        ]})
        self.elb.describe_tags.side_effect = lambda ResourceArns: {
            "TagDescriptions": [{"ResourceArn": arn, "Tags": TAGS} for arn in ResourceArns]
        }

    def collect(self):
        return collect_inventory("us-east-1", ec2_client=self.ec2, elbv2_client=self.elb, now=NOW)

    def test_all_pages_are_included_and_snapshots_scoped_to_owner(self):
        inventory = self.collect()
        self.assertEqual([item["id"] for item in inventory["instances"]], ["i-1", "i-2"])
        self.assertEqual(len(inventory["volumes"]), 2)
        self.assertEqual(len(inventory["load_balancers"]), 25)
        self.paginators["describe_snapshots"].paginate.assert_called_once_with(OwnerIds=["self"])

    def test_snapshot_age_uses_start_time(self):
        inventory = self.collect()
        self.assertEqual([item["age_days"] for item in inventory["snapshots"]], [5, 120])
        old = [f.resource_id for f in run_all_checks(inventory) if f.check_id == "old-snapshot"]
        self.assertEqual(old, ["snap-120"])

    def test_uncollected_utilization_does_not_create_idle_findings(self):
        inventory = self.collect()
        self.assertIsNone(inventory["instances"][0]["cpu_avg_14d"])
        self.assertIsNone(inventory["load_balancers"][0]["request_count_7d"])
        ids = {f.check_id for f in run_all_checks(inventory)}
        self.assertFalse(ids & {"idle-ec2", "oversized-instance", "unused-load-balancer"})
        self.assertNotIn("missing-tags", ids)

    def test_load_balancer_tags_are_batched_at_twenty(self):
        self.collect()
        calls = self.elb.describe_tags.call_args_list
        self.assertEqual([len(call.kwargs["ResourceArns"]) for call in calls], [20, 5])

    def test_missing_tag_response_remains_unknown(self):
        self.elb.describe_tags.side_effect = None
        self.elb.describe_tags.return_value = {"TagDescriptions": []}
        inventory = self.collect()
        self.assertIsNone(inventory["load_balancers"][0]["tags"])
        self.assertNotIn("missing-tags", {f.check_id for f in run_all_checks(inventory)})
