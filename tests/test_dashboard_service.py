from __future__ import annotations

from unittest.mock import patch

from core.dashboard_service import DashboardService
from core.models.risk_summary import RiskSummary


def build_summary() -> RiskSummary:
    return RiskSummary(
        overall_score=37.69,
        health="Critical",
        health_reason="MTM loss crossed the critical threshold.",
        records=1417,
        clients=419,
        symbols=368,
        portfolio_value=394_410_546.59,
        total_exposure=394_410_546.59,
        total_mtm=-33_525_195.75,
        total_var=0.0,
        total_margin=126_250_000.0,
        mtm_loss_percent=8.50,
        margin_utilization_percent=32.01,
        top_client_concentration_percent=5.40,
        top_symbol_concentration_percent=6.47,
        exposure_score=0.0,
        mtm_score=75.0,
        margin_score=21.34,
        client_concentration_score=21.60,
        symbol_concentration_score=32.35,
        diversification_score=73.01,
    )


def test_dashboard_service_success() -> None:
    with patch(
        "core.dashboard_service.RiskEngine.analyze_current_portfolio",
        return_value=build_summary(),
    ):
        result = DashboardService().get_dashboard_data()

    assert result.available is True
    assert result.summary is not None
    assert result.summary.health == "Critical"
    assert result.summary.records == 1417


def test_dashboard_service_empty_state() -> None:
    with patch(
        "core.dashboard_service.RiskEngine.analyze_current_portfolio",
        side_effect=ValueError("No master portfolio is loaded."),
    ):
        result = DashboardService().get_dashboard_data()

    assert result.available is False
    assert result.summary is None
    assert "No master portfolio" in result.message


if __name__ == "__main__":
    test_dashboard_service_success()
    test_dashboard_service_empty_state()
    print("RMS Sprint 4.1 dashboard service tests passed successfully.")
