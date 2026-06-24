from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Finding:
    check_id: str
    severity: str
    resource_type: str
    resource_id: str
    region: str
    message: str
    recommendation: str
    estimated_monthly_savings: float = 0.0
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["estimated_monthly_savings"] = round(self.estimated_monthly_savings, 2)
        return data
