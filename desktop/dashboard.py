import customtkinter as ctk

from desktop.analytics_page import AnalyticsPage
from desktop.dashboard_page import DashboardPage
from desktop.sidebar import Sidebar
from desktop.stock_page import StockPage
from desktop.portfolio_page import PortfolioPage


class Dashboard(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Finance Utility Suite")
        self.geometry("1400x800")

        self.create_layout()

    def create_layout(self):

        self.sidebar = Sidebar(
            self,
            self.change_page
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.main = ctk.CTkFrame(self)

        self.main.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.show_dashboard()

    def clear_main(self):

        for widget in self.main.winfo_children():
            widget.destroy()

    def show_dashboard(self):

        self.clear_main()

        DashboardPage(self.main).pack(
            fill="both",
            expand=True
        )

    def show_analytics(self):

        self.clear_main()

        AnalyticsPage(self.main).pack(
            fill="both",
            expand=True
        )

    def show_stocks(self):

        self.clear_main()

        StockPage(self.main).pack(
            fill="both",
            expand=True
        )

    def change_page(self, page):

        if page == "dashboard":
            self.show_dashboard()

        elif page == "analytics":
            self.show_analytics()

        elif page == "stocks":
            self.show_stocks()

        elif page == "portfolio":
            self.clear_main()

            PortfolioPage(self.main).pack(
             fill="both",
             expand=True
    )    

        else:
            self.clear_main()

            label = ctk.CTkLabel(
                self.main,
                text=page.title(),
                font=("Segoe UI", 30, "bold")
            )

            label.pack(pady=30)