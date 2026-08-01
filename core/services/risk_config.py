"""
Risk Management System (RMS)
Risk Engine Configuration

All thresholds and score weights are kept in one place so business
rules can be revised without changing the calculation services.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class RiskWeights:
    mtm: float = 0.30
    margin: float = 0.25
    client_concentration: float = 0.20
    symbol_concentration: float = 0.20
    exposure: float = 0.05

    def validate(self) -> None:
        total = (
            self.mtm
            + self.margin
            + self.client_concentration
            + self.symbol_concentration
            + self.exposure
        )
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"Risk weights must total 1.0; received {total:.6f}")


@dataclass(frozen=True, slots=True)
class RiskThresholds:
    # Portfolio MTM loss as a percentage of exposure.
    mtm_warning_percent: float = 5.0
    mtm_critical_percent: float = 8.0

    # Margin / exposure.
    margin_warning_percent: float = 60.0
    margin_critical_percent: float = 80.0

    # Largest client exposure / total exposure.
    client_concentration_warning_percent: float = 10.0
    client_concentration_critical_percent: float = 20.0

    # Largest symbol exposure / total exposure.
    symbol_concentration_warning_percent: float = 8.0
    symbol_concentration_critical_percent: float = 15.0

    # Overall score bands. Higher score means higher risk.
    overall_warning_score: float = 40.0
    overall_critical_score: float = 70.0


@dataclass(frozen=True, slots=True)
class RiskConfig:
    weights: RiskWeights = field(default_factory=RiskWeights)
    thresholds: RiskThresholds = field(default_factory=RiskThresholds)
    top_n: int = 20

    def validate(self) -> None:
        self.weights.validate()
        if self.top_n < 1:
            raise ValueError("top_n must be at least 1.")
