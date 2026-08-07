"""
Finance Utility Suite
Enterprise RMS

Unit Test:
    Enterprise Risk Service
"""

from __future__ import annotations

import pandas as pd

from core.services.enterprise_risk_service import EnterpriseRiskService


def sample_dataframe() -> pd.DataFrame:

    return pd.DataFrame(
        {
            "AccountId": [
                "C001",
                "C001",
                "C002",
                "C003",
            ],
            "Symbol": [
                "RELIANCE",
                "INFY",
                "TCS",
                "SBIN",
            ],
            "NetValue": [
                100000,
                50000,
                75000,
                25000,
            ],
            "MarkToMarket": [
                5000,
                -1000,
                2500,
                -500,
            ],
            "BUY VALUE": [
                95000,
                52000,
                70000,
                26000,
            ],
            "MTF VAR": [
                12000,
                5000,
                9000,
                3000,
            ],
            "MTF MARGIN": [
                20000,
                10000,
                15000,
                5000,
            ],
        }
    )


def run_test():

    df = sample_dataframe()

    summary = EnterpriseRiskService.analyze(df)

    print()
    print("=" * 50)
    print("Enterprise Risk Engine Test")
    print("=" * 50)

    print(f"Records           : {summary.records}")
    print(f"Clients           : {summary.clients}")
    print(f"Symbols           : {summary.symbols}")

    print()

    print(f"Portfolio Value   : ₹{summary.portfolio_value:,.2f}")
    print(f"Exposure          : ₹{summary.total_exposure:,.2f}")
    print(f"MTM               : ₹{summary.total_mtm:,.2f}")

    print()

    print(f"VAR               : ₹{summary.total_var:,.2f}")
    print(f"Margin            : ₹{summary.total_margin:,.2f}")

    print()

    print(
        f"Margin Utilization: "
        f"{summary.margin_utilization_percent:.2f}%"
    )

    print(
        f"MTM Loss %        : "
        f"{summary.mtm_loss_percent:.2f}%"
    )

    print()

    print(
        f"Top Client %      : "
        f"{summary.top_client_concentration_percent:.2f}%"
    )

    print(
        f"Top Symbol %      : "
        f"{summary.top_symbol_concentration_percent:.2f}%"
    )

    print()

    print(f"Overall Score     : {summary.overall_score:.2f}")
    print(f"Health            : {summary.health}")
    print(f"Reason            : {summary.health_reason}")

    print()

    print("Warnings")

    if summary.warnings:
        for warning in summary.warnings:
            print(f" • {warning}")
    else:
        print(" None")

    print()

    print("Top Clients")

    for item in summary.top_clients:

        print(
            f"{item.name:10}"
            f"{item.concentration_percent:8.2f}%"
        )

    print()

    print("Top Symbols")

    for item in summary.top_symbols:

        print(
            f"{item.name:12}"
            f"{item.concentration_percent:8.2f}%"
        )

    print()
    print("=" * 50)


if __name__ == "__main__":
    run_test()