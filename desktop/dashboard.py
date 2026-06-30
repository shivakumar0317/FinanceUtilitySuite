import customtkinter as ctk

from desktop.dashboard_page import DashboardPage
from desktop.sidebar import Sidebar
from desktop.stock_page import StockPage


class Dashboard(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Finance Utility Suite")
        self.geometry("1400x800")

        self.create_layout()

    def create_layout(self):

        # -----------------------------
        # Sidebar
        # -----------------------------
        self.sidebar = Sidebar(
            self,
            self.change_page
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        # -----------------------------
        # Main Area
        # -----------------------------
        self.main = ctk.CTkFrame(self)

        self.main.pack(
            side="right",
            fill="both",
            expand=True
        )

        # -----------------------------
        # Default Page
        # -----------------------------
        DashboardPage(self.main).pack(
            fill="both",
            expand=True
        )

    def change_page(self, page):

        # Remove current page
        for widget in self.main.winfo_children():
            widget.destroy()

        if page == "dashboard":

            DashboardPage(self.main).pack(
                fill="both",
                expand=True
            )

        elif page == "stocks":

            StockPage(self.main).pack(
                fill="both",
                expand=True
            )

        else:

            label = ctk.CTkLabel(
                self.main,
                text=page.title(),
                font=("Segoe UI", 30, "bold")
            )

            label.pack(pady=30)

    def load_dashboard(self):

     stats = self.dashboard.get_statistics()

     self.total.set_value(stats["stocks"])

     self.report.set_value(stats["reports"])

     self.beta.set_value(stats["avg_beta"])

     self.risk.set_value(stats["high_risk"])