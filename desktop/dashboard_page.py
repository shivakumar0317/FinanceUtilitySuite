import customtkinter as ctk

from desktop.widgets.stat_card import StatCard
from core.dashboard_service import DashboardService


class DashboardPage(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)

        self.dashboard = DashboardService()

        self.create_widgets()

        self.load_dashboard()

    def create_widgets(self):

        title = ctk.CTkLabel(self, text="Dashboard", font=("Segoe UI", 30, "bold"))
        title.pack(pady=25)

        cards = ctk.CTkFrame(self)
        cards.pack(pady=20)

        self.total = StatCard(cards, "Stocks", "0")
        self.total.grid(row=0, column=0, padx=15)

        self.report = StatCard(cards, "Reports", "0")
        self.report.grid(row=0, column=1, padx=15)

        self.beta = StatCard(cards, "Avg Beta", "0.00")
        self.beta.grid(row=0, column=2, padx=15)

        self.risk = StatCard(cards, "High Risk", "0")
        self.risk.grid(row=0, column=3, padx=15)

        recent = ctk.CTkLabel(
            self, text="Recent Reports", font=("Segoe UI", 22, "bold")
        )
        recent.pack(pady=(40, 10))

        self.textbox = ctk.CTkTextbox(self, width=850, height=220)
        self.textbox.pack()

        self.textbox.insert("end", "No reports available...")

    def load_dashboard(self):

        stats = self.dashboard.get_statistics()

        self.total.set_value(stats["stocks"])
        self.report.set_value(stats["reports"])
        self.beta.set_value(stats["avg_beta"])
        self.risk.set_value(stats["high_risk"])
