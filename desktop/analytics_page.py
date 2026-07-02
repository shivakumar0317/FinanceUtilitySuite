import customtkinter as ctk

from desktop.widgets.dashboard_card import DashboardCard
from desktop.widgets.chart_widget import ChartWidget


class AnalyticsPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.build_ui()

    def build_ui(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        title = ctk.CTkLabel(
            self, text="Analytics Dashboard", font=("Segoe UI", 28, "bold")
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # KPI Cards
        cards_frame = ctk.CTkFrame(self)
        cards_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1)

        cards = [
            ("Portfolio Value", "₹18,42,500", "+5.24% Today"),
            ("Investment Score", "87 / 100", "Excellent"),
            ("Risk Score", "LOW", "Stable"),
            ("MTF Exposure", "₹5,20,000", "82% Used"),
        ]

        for index, (title, value, subtitle) in enumerate(cards):
            card = DashboardCard(
                cards_frame, title=title, value=value, subtitle=subtitle
            )
            card.grid(row=0, column=index, padx=10, pady=10, sticky="nsew")

        # Charts Area
        charts_frame = ctk.CTkFrame(self)
        charts_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)
        charts_frame.grid_rowconfigure(0, weight=2)
        charts_frame.grid_rowconfigure(1, weight=1)

        self.price_chart = ChartWidget(charts_frame)
        self.price_chart.grid(
            row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10
        )

        self.sector_chart = ChartWidget(charts_frame)
        self.sector_chart.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.risk_chart = ChartWidget(charts_frame)
        self.risk_chart.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.load_sample_data()

    def load_sample_data(self):

        self.price_chart.plot_line(
            ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            [1450, 1520, 1490, 1580, 1640, 1705],
            title="Stock Price History",
            xlabel="Month",
            ylabel="Price",
        )

        self.sector_chart.plot_pie(
            ["IT", "Banking", "Auto", "Pharma"],
            [35, 30, 20, 15],
            title="Sector Allocation",
        )

        self.risk_chart.plot_bar(
            ["Low", "Medium", "High"],
            [45, 30, 25],
            title="Risk Distribution",
            xlabel="Risk Level",
            ylabel="Stocks",
        )
