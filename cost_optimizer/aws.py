from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def collect_inventory(
    region: str,
    *,
    ec2_client: Any = None,
    elbv2_client: Any = None,
    now: datetime | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Collect a complete, read-only inventory; uncollected metrics remain unknown."""
    if ec2_client is None or elbv2_client is None:
        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError("Install AWS support with: pip install '.[aws]'") from exc
        ec2_client = ec2_client or boto3.client("ec2", region_name=region)
        elbv2_client = elbv2_client or boto3.client("elbv2", region_name=region)
    ec2, elbv2 = ec2_client, elbv2_client
    collected_at = now or datetime.now(timezone.utc)

    instances = []
    for page in ec2.get_paginator("describe_instances").paginate():
        for reservation in page.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                instances.append(
                    {
                        "id": instance["InstanceId"],
                        "region": region,
                        "type": instance["InstanceType"],
                        "state": instance["State"]["Name"],
                        "cpu_avg_14d": None,
                        "monthly_cost": 0,
                        "tags": _tags(instance.get("Tags", [])),
                    }
                )

    volumes = []
    for page in ec2.get_paginator("describe_volumes").paginate():
        for volume in page.get("Volumes", []):
            attachments = volume.get("Attachments", [])
            volumes.append(
                {
                    "id": volume["VolumeId"],
                    "region": region,
                    "state": volume["State"],
                    "attached_to": attachments[0]["InstanceId"] if attachments else None,
                    "size_gb": volume["Size"],
                    "monthly_cost": 0,
                    "tags": _tags(volume.get("Tags", [])),
                }
            )

    snapshots = []
    for page in ec2.get_paginator("describe_snapshots").paginate(OwnerIds=["self"]):
        for snapshot in page.get("Snapshots", []):
            snapshots.append(
                {
                    "id": snapshot["SnapshotId"],
                    "region": region,
                    "age_days": max(0, (collected_at - snapshot["StartTime"]).days),
                    "monthly_cost": 0,
                    "tags": _tags(snapshot.get("Tags", [])),
                }
            )

    load_balancers = []
    for page in elbv2.get_paginator("describe_load_balancers").paginate():
        for load_balancer in page.get("LoadBalancers", []):
            load_balancers.append(
                {
                    "id": load_balancer["LoadBalancerArn"],
                    "region": region,
                    "request_count_7d": None,
                    "healthy_target_count": None,
                    "monthly_cost": 0,
                    "tags": None,
                }
            )
    # ELBv2 accepts at most 20 ARNs per describe_tags call.
    for offset in range(0, len(load_balancers), 20):
        batch = load_balancers[offset:offset + 20]
        response = elbv2.describe_tags(ResourceArns=[item["id"] for item in batch])
        tags_by_arn = {
            item["ResourceArn"]: _tags(item.get("Tags", []))
            for item in response.get("TagDescriptions", [])
        }
        for item in batch:
            item["tags"] = tags_by_arn.get(item["id"])

    return {
        "instances": instances,
        "volumes": volumes,
        "snapshots": snapshots,
        "load_balancers": load_balancers,
    }


def _tags(tags: list[dict[str, str]]) -> dict[str, str]:
    return {tag["Key"]: tag["Value"] for tag in tags}
