"""Convert risk scores and controls into portfolio health."""

from __future__ import annotations

from core.services.risk_config import RiskThresholds


class HealthService:
    @staticmethod
    def evaluate(
        *,
        overall_score: float,
        mtm_loss_percent: float,
        margin_utilization_percent: float,
        thresholds: RiskThresholds,
    ) -> tuple[str, str]:
        # Hard controls take precedence over the weighted score.
        if mtm_loss_percent >= thresholds.mtm_critical_percent:
            return (
                "Critical",
                f"MTM loss is {mtm_loss_percent:.2f}% of exposure, above the "
                f"{thresholds.mtm_critical_percent:.2f}% critical threshold.",
            )

        if margin_utilization_percent >= thresholds.margin_critical_percent:
            return (
                "Critical",
                f"Margin utilization is {margin_utilization_percent:.2f}%, above the "
                f"{thresholds.margin_critical_percent:.2f}% critical threshold.",
            )

        if overall_score >= thresholds.overall_critical_score:
            return (
                "Critical",
                f"Overall risk score is {overall_score:.2f}/100.",
            )

        if mtm_loss_percent >= thresholds.mtm_warning_percent:
            return (
                "Warning",
                f"MTM loss is {mtm_loss_percent:.2f}% of exposure, above the "
                f"{thresholds.mtm_warning_percent:.2f}% warning threshold.",
            )

        if margin_utilization_percent >= thresholds.margin_warning_percent:
            return (
                "Warning",
                f"Margin utilization is {margin_utilization_percent:.2f}%, above the "
                f"{thresholds.margin_warning_percent:.2f}% warning threshold.",
            )

        if overall_score >= thresholds.overall_warning_score:
            return (
                "Warning",
                f"Overall risk score is {overall_score:.2f}/100.",
            )

        return (
            "Healthy",
            f"Overall risk score is {overall_score:.2f}/100.",
        )    