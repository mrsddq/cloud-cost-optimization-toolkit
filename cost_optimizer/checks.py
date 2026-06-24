from __future__ import annotations

from typing import Any

from .models import Finding


DEFAULT_CONFIG: dict[str, Any] = {
    "idle_cpu_threshold": 5.0,
    "rightsize_cpu_threshold": 15.0,
    "old_snapshot_days": 90,
    "required_tags": ["Owner", "CostCenter", "Environment"],
    "rightsize_recommendations": {
        "m5.4xlarge": "m5.xlarge",
        "m5.2xlarge": "m5.large",
        "c5.4xlarge": "c5.xlarge",
        "r5.4xlarge": "r5.xlarge",
    },
}


def run_all_checks(inventory: dict[str, Any], config: dict[str, Any] | None = None) -> list[Finding]:
    active_config = {**DEFAULT_CONFIG, **(config or {})}
    findings: list[Finding] = []
    findings.extend(find_idle_ec2(inventory.get("instances", []), active_config))
    findings.extend(find_unattached_ebs(inventory.get("volumes", [])))
    findings.extend(find_old_snapshots(inventory.get("snapshots", []), active_config))
    findings.extend(find_unused_load_balancers(inventory.get("load_balancers", [])))
    findings.extend(find_oversized_instances(inventory.get("instances", []), active_config))
    findings.extend(find_missing_tags(inventory, active_config))
    return sorted(findings, key=lambda item: (item.severity, item.resource_type, item.resource_id))


def find_idle_ec2(instances: list[dict[str, Any]], config: dict[str, Any]) -> list[Finding]:
    findings = []
    threshold = float(config["idle_cpu_threshold"])
    for instance in instances:
        if instance.get("state") != "running":
            continue
        cpu = float(instance.get("cpu_avg_14d", 0))
        if cpu <= threshold:
            findings.append(
                Finding(
                    check_id="idle-ec2",
                    severity="high",
                    resource_type="ec2",
                    resource_id=instance["id"],
                    region=instance.get("region", "unknown"),
                    message=f"EC2 instance averaged {cpu:.1f}% CPU over 14 days.",
                    recommendation="Stop, schedule, terminate, or rightsize after owner review.",
                    estimated_monthly_savings=float(instance.get("monthly_cost", 0)),
                    tags=instance.get("tags", {}),
                    metadata={"cpu_avg_14d": cpu, "instance_type": instance.get("type")},
                )
            )
    return findings


def find_unattached_ebs(volumes: list[dict[str, Any]]) -> list[Finding]:
    findings = []
    for volume in volumes:
        if volume.get("state") == "available" or not volume.get("attached_to"):
            findings.append(
                Finding(
                    check_id="unattached-ebs",
                    severity="medium",
                    resource_type="ebs",
                    resource_id=volume["id"],
                    region=volume.get("region", "unknown"),
                    message="EBS volume is not attached to an instance.",
                    recommendation="Snapshot if needed, then delete after owner approval.",
                    estimated_monthly_savings=float(volume.get("monthly_cost", 0)),
                    tags=volume.get("tags", {}),
                    metadata={"size_gb": volume.get("size_gb")},
                )
            )
    return findings


def find_old_snapshots(snapshots: list[dict[str, Any]], config: dict[str, Any]) -> list[Finding]:
    findings = []
    max_age = int(config["old_snapshot_days"])
    for snapshot in snapshots:
        age = int(snapshot.get("age_days", 0))
        if age > max_age:
            findings.append(
                Finding(
                    check_id="old-snapshot",
                    severity="low",
                    resource_type="snapshot",
                    resource_id=snapshot["id"],
                    region=snapshot.get("region", "unknown"),
                    message=f"Snapshot is {age} days old, above {max_age}-day policy.",
                    recommendation="Confirm retention requirement, then delete if obsolete.",
                    estimated_monthly_savings=float(snapshot.get("monthly_cost", 0)),
                    tags=snapshot.get("tags", {}),
                    metadata={"age_days": age},
                )
            )
    return findings


def find_unused_load_balancers(load_balancers: list[dict[str, Any]]) -> list[Finding]:
    findings = []
    for load_balancer in load_balancers:
        requests = int(load_balancer.get("request_count_7d", 0))
        targets = int(load_balancer.get("healthy_target_count", 0))
        if requests == 0 or targets == 0:
            findings.append(
                Finding(
                    check_id="unused-load-balancer",
                    severity="high",
                    resource_type="load_balancer",
                    resource_id=load_balancer["id"],
                    region=load_balancer.get("region", "unknown"),
                    message="Load balancer has no traffic or no healthy targets.",
                    recommendation="Confirm ownership, then remove unused listener and load balancer resources.",
                    estimated_monthly_savings=float(load_balancer.get("monthly_cost", 0)),
                    tags=load_balancer.get("tags", {}),
                    metadata={"request_count_7d": requests, "healthy_target_count": targets},
                )
            )
    return findings


def find_oversized_instances(instances: list[dict[str, Any]], config: dict[str, Any]) -> list[Finding]:
    findings = []
    threshold = float(config["rightsize_cpu_threshold"])
    recommendations = config["rightsize_recommendations"]
    for instance in instances:
        instance_type = instance.get("type")
        cpu = float(instance.get("cpu_avg_14d", 0))
        if instance.get("state") == "running" and instance_type in recommendations and cpu <= threshold:
            monthly_cost = float(instance.get("monthly_cost", 0))
            findings.append(
                Finding(
                    check_id="oversized-instance",
                    severity="medium",
                    resource_type="ec2",
                    resource_id=instance["id"],
                    region=instance.get("region", "unknown"),
                    message=f"{instance_type} averaged {cpu:.1f}% CPU and may be oversized.",
                    recommendation=f"Evaluate resize to {recommendations[instance_type]} in a maintenance window.",
                    estimated_monthly_savings=monthly_cost * 0.45,
                    tags=instance.get("tags", {}),
                    metadata={"current_type": instance_type, "suggested_type": recommendations[instance_type]},
                )
            )
    return findings


def find_missing_tags(inventory: dict[str, Any], config: dict[str, Any]) -> list[Finding]:
    findings = []
    required = set(config["required_tags"])
    collections = {
        "ec2": inventory.get("instances", []),
        "ebs": inventory.get("volumes", []),
        "snapshot": inventory.get("snapshots", []),
        "load_balancer": inventory.get("load_balancers", []),
    }
    for resource_type, resources in collections.items():
        for resource in resources:
            tags = resource.get("tags", {})
            missing = sorted(required - set(tags))
            if missing:
                findings.append(
                    Finding(
                        check_id="missing-tags",
                        severity="low",
                        resource_type=resource_type,
                        resource_id=resource["id"],
                        region=resource.get("region", "unknown"),
                        message=f"Resource is missing required tags: {', '.join(missing)}.",
                        recommendation="Apply required ownership, environment, and cost allocation tags.",
                        tags=tags,
                        metadata={"missing_tags": missing},
                    )
                )
    return findings
