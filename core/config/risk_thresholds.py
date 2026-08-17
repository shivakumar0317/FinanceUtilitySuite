"""
Finance Utility Suite
Enterprise RMS

Module:
risk_thresholds.py

Description:
Centralized risk-control thresholds for Enterprise RMS.

Author:
Shiva Kumar

Version:
1.0
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConcentrationThresholds:
    """
    Concentration control thresholds.

    Values are percentages of total enterprise exposure.
    """

    good_max: float
    moderate_max: float
    critical_min: float


@dataclass(frozen=True, slots=True)
class RiskScoreThresholds:
    """
    Overall enterprise risk-score thresholds.

    Higher score = better risk condition.
    """

    critical_max: float
    moderate_max: float
    good_min: float


@dataclass(frozen=True, slots=True)
class EnterpriseRiskThresholds:
    """
    Central Enterprise RMS risk-control configuration.
    """

    client_concentration: ConcentrationThresholds
    symbol_concentration: ConcentrationThresholds
    risk_score: RiskScoreThresholds


DEFAULT_RISK_THRESHOLDS = EnterpriseRiskThresholds(
    client_concentration=ConcentrationThresholds(
        good_max=15.0,
        moderate_max=25.0,
        critical_min=25.0,
    ),
    symbol_concentration=ConcentrationThresholds(
        good_max=15.0,
        moderate_max=30.0,
        critical_min=30.0,
    ),
    risk_score=RiskScoreThresholds(
        critical_max=39.99,
        moderate_max=69.99,
        good_min=70.0,
    ),
)