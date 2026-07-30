"""Report Center registry for Finance Utility Suite.

The registry deliberately stores metadata only. Report-specific input collection and
export execution are handled by the Report Center workflow in later sprints.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class ReportDefinition:
    """Immutable metadata describing one report exposed in the Report Center."""

    report_id: str
    title: str
    icon: str
    description: str
    status: str = "available"
    category: str = "Portfolio"

    def __post_init__(self) -> None:
        report_id = self.report_id.strip().lower()
        title = self.title.strip()
        description = self.description.strip()
        status = self.status.strip().lower()
        category = self.category.strip()

        if not report_id:
            raise ValueError("report_id cannot be empty")
        if not report_id.replace("_", "").replace("-", "").isalnum():
            raise ValueError("report_id may contain only letters, numbers, '-' and '_'")
        if not title:
            raise ValueError("title cannot be empty")
        if not description:
            raise ValueError("description cannot be empty")
        if status not in {"available", "coming_soon"}:
            raise ValueError("status must be 'available' or 'coming_soon'")
        if not category:
            raise ValueError("category cannot be empty")

        object.__setattr__(self, "report_id", report_id)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "category", category)

    @property
    def is_available(self) -> bool:
        return self.status == "available"


class ReportRegistry:
    """Ordered, duplicate-safe registry used by the Report Center UI."""

    def __init__(self, reports: Iterable[ReportDefinition] | None = None) -> None:
        self._reports: dict[str, ReportDefinition] = {}
        for report in reports or ():
            self.register(report)

    def register(self, report: ReportDefinition, *, replace: bool = False) -> None:
        if not isinstance(report, ReportDefinition):
            raise TypeError("report must be a ReportDefinition")
        if report.report_id in self._reports and not replace:
            raise ValueError(f"Report already registered: {report.report_id}")
        self._reports[report.report_id] = report

    def unregister(self, report_id: str) -> bool:
        return self._reports.pop(report_id.strip().lower(), None) is not None

    def get(self, report_id: str) -> ReportDefinition:
        key = report_id.strip().lower()
        try:
            return self._reports[key]
        except KeyError as exc:
            raise KeyError(f"Unknown report: {report_id}") from exc

    def all(self, *, include_coming_soon: bool = True) -> tuple[ReportDefinition, ...]:
        reports = tuple(self._reports.values())
        if include_coming_soon:
            return reports
        return tuple(report for report in reports if report.is_available)

    def available(self) -> tuple[ReportDefinition, ...]:
        return self.all(include_coming_soon=False)

    def search(self, query: str) -> tuple[ReportDefinition, ...]:
        term = query.strip().lower()
        if not term:
            return self.all()
        return tuple(
            report
            for report in self._reports.values()
            if term in report.title.lower()
            or term in report.description.lower()
            or term in report.category.lower()
        )

    def __len__(self) -> int:
        return len(self._reports)


DEFAULT_REPORTS = (
    ReportDefinition(
        report_id="portfolio",
        title="Portfolio Report",
        icon="📄",
        description="Portfolio summary, holdings, allocation, performance and charts.",
    ),
    ReportDefinition(
        report_id="analytics",
        title="Analytics Report",
        icon="📊",
        description="Executive analytics, performance trends, sectors and attribution.",
    ),
    ReportDefinition(
        report_id="client_holdings",
        title="Client Holdings Report",
        icon="👥",
        description="Client-level holdings, positions and account summary.",
        category="Client",
    ),
    ReportDefinition(
        report_id="mtf_risk",
        title="MTF Risk Report",
        icon="⚠️",
        description="MTF exposure, margin utilisation and risk monitoring.",
        status="coming_soon",
        category="Risk",
    ),
    ReportDefinition(
        report_id="risk_analytics",
        title="Risk Analytics Report",
        icon="📉",
        description="Portfolio volatility, concentration and advanced risk metrics.",
        status="coming_soon",
        category="Risk",
    ),
)

REPORT_REGISTRY = ReportRegistry(DEFAULT_REPORTS)


def get_report_registry() -> ReportRegistry:
    """Return the application-wide report registry."""

    return REPORT_REGISTRY
