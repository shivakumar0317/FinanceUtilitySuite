from __future__ import annotations

import pandas as pd

from core.services.risk_engine import RiskEngine


def sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "AccountId": ["A1", "A1", "A2", "A3"],
            "Symbol": ["AAA", "BBB", "AAA", "CCC"],
            "NetValue": [400_000, 100_000, 250_000, 250_000],
            "Exposure": [400_000, 100_000, 250_000, 250_000],
            "MarkToMarket": [-40_000, -5_000, 10_000, -15_000],
            "MTF VAR": [60_000, 15_000, 35_000, 35_000],
            "MTF MARGIN": [280_000, 70_000, 175_000, 175_000],
        }
    )


def test_risk_engine_summary() -> None:
    result = RiskEngine().analyze(sample_dataframe())

    assert result.records == 4
    assert result.clients == 3
    assert result.symbols == 3
    assert result.total_exposure == 1_000_000.0
    assert result.total_mtm == -50_000.0
    assert result.total_margin == 700_000.0
    assert result.mtm_loss_percent == 5.0
    assert result.margin_utilization_percent == 70.0
    assert result.top_client_concentration_percent == 50.0
    assert result.top_symbol_concentration_percent == 65.0
    assert 0.0 <= result.overall_score <= 100.0
    assert result.health in {"Healthy", "Warning", "Critical"}
    assert len(result.top_clients) == 3
    assert len(result.top_symbols) == 3


def test_to_dict() -> None:
    payload = RiskEngine().analyze(sample_dataframe()).to_dict()
    assert payload["records"] == 4
    assert isinstance(payload["top_clients"], list)
    assert payload["top_clients"][0]["name"] == "A1"


if __name__ == "__main__":
    test_risk_engine_summary()
    test_to_dict()
    print("RMS Sprint 4.0 Risk Engine tests passed successfully.")
