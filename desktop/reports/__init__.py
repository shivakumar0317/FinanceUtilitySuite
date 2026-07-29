"""Finance Utility Suite universal reporting package."""
from desktop.reports.analytics_engine import AnalyticsDataError, AnalyticsSummary, PortfolioAnalyticsEngine
from desktop.reports.analytics_report import AnalyticsReport
from desktop.reports.base_dashboard_report import BaseDashboardReport
from desktop.reports.client_holdings_report import ClientHoldingsReport
from desktop.reports.portfolio_report import PortfolioReport
from desktop.reports.performance_engine import PerformanceDataError, PerformanceEngine, PerformanceSummary
from desktop.reports.recommendation_engine import ExecutiveRecommendationEngine, Recommendation
from desktop.reports.report_controller import ReportController
from desktop.reports.report_engine import ExcelReportEngine, ReportEngineError

REPORTING_VERSION = "1.38.1"
__all__ = ["REPORTING_VERSION", "ExcelReportEngine", "ReportEngineError", "BaseDashboardReport", "ReportController", "ClientHoldingsReport", "PortfolioReport", "PortfolioAnalyticsEngine", "AnalyticsSummary", "AnalyticsDataError", "AnalyticsReport", "PerformanceEngine", "PerformanceSummary", "PerformanceDataError", "ExecutiveRecommendationEngine", "Recommendation"]
