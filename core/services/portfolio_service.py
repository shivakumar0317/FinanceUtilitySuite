"""
Finance Utility Suite
Portfolio Service
"""

from __future__ import annotations


from core.portfolio.loader import PortfolioLoader
from core.portfolio.calculator import PortfolioCalculator


class PortfolioService:
    """
    High-level service for portfolio operations.

    The UI should communicate only with this class.
    """

    @staticmethod
    def load(file_path: str):

        # Step 1 : Load Portfolio
        dataframe = PortfolioLoader.load(file_path)

        # Step 2 : Calculate Portfolio Metrics
        dataframe = PortfolioCalculator.calculate(dataframe)

        # Step 3 : Generate Summary
        summary = PortfolioCalculator.summary(dataframe)

        return dataframe, summary
