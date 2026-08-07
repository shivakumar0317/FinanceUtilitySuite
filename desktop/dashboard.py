import customtkinter as ctk

from desktop.analytics_page import AnalyticsPage
from desktop.concentration_risk_page import ConcentrationRiskPage
from desktop.dashboard_page import DashboardPage
from desktop.live_market_page import LiveMarketPage
from desktop.mtf_page import MTFPage
from desktop.portfolio_live_page import PortfolioLivePage
from desktop.portfolio_page import PortfolioPage
from desktop.portfolio_performance_page import PortfolioPerformancePage
from desktop.reports_page import ReportsPage
from desktop.risk_analytics_page import RiskAnalyticsPage
from desktop.sidebar import Sidebar
from desktop.snapshot_manager_page import SnapshotManagerPage
from desktop.historical_analytics_page import HistoricalAnalyticsPage
from desktop.stock_page import StockPage
from desktop.windows.about_window import AboutWindow


class Dashboard(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Risk Management System (RMS)")
        self.geometry("1400x800")
        self.minsize(1100, 650)

        self.create_layout()

    def create_layout(self):
        self.sidebar = Sidebar(self, self.change_page)
        self.sidebar.pack(side="left", fill="y")

        self.main = ctk.CTkFrame(self)
        self.main.pack(side="right", fill="both", expand=True)

        self.show_dashboard()

    def clear_main(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def _show_page(self, page_class):
        self.clear_main()
        page_class(self.main).pack(fill="both", expand=True)

    def show_dashboard(self):
        self._show_page(DashboardPage)

    def show_analytics(self):
        self._show_page(AnalyticsPage)

    def show_stocks(self):
        self._show_page(StockPage)

    def change_page(self, page):
        page_routes = {
            "dashboard": DashboardPage,
            "analytics": AnalyticsPage,
            "stocks": StockPage,
            "portfolio": PortfolioPage,
            "mtf": MTFPage,
            "concentration_risk": ConcentrationRiskPage,
            "live": LiveMarketPage,
            "portfolio_live": PortfolioLivePage,
            "portfolio_performance": PortfolioPerformancePage,
            "risk_analytics": RiskAnalyticsPage,
            "snapshot_manager": SnapshotManagerPage,
            "reports": ReportsPage,
            "historical_analytics": HistoricalAnalyticsPage,
        }

        if page == "about":
            AboutWindow(self)
            return

        page_class = page_routes.get(page)
        if page_class is not None:
            self._show_page(page_class)
            return

        self.clear_main()
        ctk.CTkLabel(
            self.main,
            text=page.title(),
            font=("Segoe UI", 30, "bold"),
        ).pack(pady=30)
