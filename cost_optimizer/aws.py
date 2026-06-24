from __future__ import annotations

from typing import Any


def collect_inventory(region: str) -> dict[str, list[dict[str, Any]]]:
    try:
        import boto3
    except ImportError as exc:
        raise RuntimeError("Install AWS support with: pip install '.[aws]'") from exc

    ec2 = boto3.client("ec2", region_name=region)
    elbv2 = boto3.client("elbv2", region_name=region)

    instances = []
    reservations = ec2.describe_instances().get("Reservations", [])
    for reservation in reservations:
        for instance in reservation.get("Instances", []):
            instances.append(
                {
                    "id": instance["InstanceId"],
                    "region": region,
                    "type": instance["InstanceType"],
                    "state": instance["State"]["Name"],
                    "cpu_avg_14d": 0,
                    "monthly_cost": 0,
                    "tags": _tags(instance.get("Tags", [])),
                }
            )

    volumes = []
    for volume in ec2.describe_volumes().get("Volumes", []):
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
    for snapshot in ec2.describe_snapshots(OwnerIds=["self"]).get("Snapshots", []):
        snapshots.append(
            {
                "id": snapshot["SnapshotId"],
                "region": region,
                "age_days": 0,
                "monthly_cost": 0,
                "tags": _tags(snapshot.get("Tags", [])),
            }
        )

    load_balancers = []
    for load_balancer in elbv2.describe_load_balancers().get("LoadBalancers", []):
        load_balancers.append(
            {
                "id": load_balancer["LoadBalancerArn"],
                "region": region,
                "request_count_7d": 0,
                "healthy_target_count": 0,
                "monthly_cost": 0,
                "tags": {},
            }
        )

    return {
        "instances": instances,
        "volumes": volumes,
        "snapshots": snapshots,
        "load_balancers": load_balancers,
    }


def _tags(tags: list[dict[str, str]]) -> dict[str, str]:
    return {tag["Key"]: tag["Value"] for tag in tags}
