"""
Run this after importing an MTF file through the RMS application,
or replace the dataframe load below with one of your Parquet snapshots.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.services.risk_engine import RiskEngine


SNAPSHOT = Path(
    "data/snapshots/2026-07/20260731_113057_963145_391dde.parquet"
)

if not SNAPSHOT.exists():
    raise FileNotFoundError(
        f"Snapshot not found: {SNAPSHOT}\n"
        "Update SNAPSHOT in this script to one of your existing parquet files."
    )

dataframe = pd.read_parquet(SNAPSHOT, engine="pyarrow")
summary = RiskEngine().analyze(dataframe)

print("\nRMS ENTERPRISE RISK SUMMARY")
print("=" * 50)
print(f"Health                  : {summary.health}")
print(f"Overall Risk Score      : {summary.overall_score:.2f}/100")
print(f"Reason                  : {summary.health_reason}")
print(f"Records                 : {summary.records:,}")
print(f"Clients                 : {summary.clients:,}")
print(f"Symbols                 : {summary.symbols:,}")
print(f"Exposure                : ₹{summary.total_exposure:,.2f}")
print(f"MTM                     : ₹{summary.total_mtm:,.2f}")
print(f"MTM Loss %              : {summary.mtm_loss_percent:.2f}%")
print(f"Margin Utilization      : {summary.margin_utilization_percent:.2f}%")
print(f"Top Client Concentration: {summary.top_client_concentration_percent:.2f}%")
print(f"Top Symbol Concentration: {summary.top_symbol_concentration_percent:.2f}%")
print(f"Diversification Score   : {summary.diversification_score:.2f}/100")

if summary.warnings:
    print("\nWarnings")
    for warning in summary.warnings:
        print(f"- {warning}")

print("\nTop 5 Clients")
for item in summary.top_clients[:5]:
    print(
        f"{item.name:15} Exposure ₹{item.exposure:,.2f} | "
        f"{item.concentration_percent:.2f}% | {item.level}"
    )

print("\nTop 5 Symbols")
for item in summary.top_symbols[:5]:
    print(
        f"{item.name:15} Exposure ₹{item.exposure:,.2f} | "
        f"{item.concentration_percent:.2f}% | {item.level}"
    )
