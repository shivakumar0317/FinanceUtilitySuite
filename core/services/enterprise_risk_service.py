"""
Finance Utility Suite
Enterprise RMS

Module:
enterprise_risk_service.py

Description:
Compatibility façade for the central Enterprise RMS RiskEngine.

The Enterprise Dashboard continues to call
EnterpriseRiskService.analyze(), while all actual
risk calculations are delegated to the central RiskEngine.
"""

from __future__ import annotations

import pandas as pd

from core.models.risk_summary import RiskSummary
from core.services.risk_config import RiskConfig
from core.services.risk_engine import RiskEngine


class EnterpriseRiskService:
    """
    Enterprise RMS service façade.

    Keeps the existing Enterprise Dashboard interface stable
    while delegating all risk calculations to the central RiskEngine.
    """

    @classmethod
    def analyze(
        cls,
        dataframe: pd.DataFrame,
    ) -> RiskSummary:
        """
        Analyze an Enterprise RMS dataframe using the central RiskEngine.
        """

        engine = RiskEngine(
            config=RiskConfig(),
        )

        return engine.analyze(dataframe)