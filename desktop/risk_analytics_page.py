"""
Finance Utility Suite
Risk Analytics Dashboard

Version: 1.30
"""

from __future__ import annotations

from tkinter import filedialog, messagebox

import customtkinter as ctk
import pandas as pd

from core.services.risk_analytics_service import RiskAnalyticsService
from desktop.base_page import BasePage
from desktop.widgets.chart_widget import ChartWidget
from desktop.widgets.dashboard_card import DashboardCard
from desktop.widgets.result_table import ResultTable


class RiskAnalyticsPage(BasePage):
    """Risk Analytics Dashboard."""

    def __init__(self, master):
        super().__init__(
            master,
            title="Risk Analytics Dashboard",
        )

        self.dataframe: pd.DataFrame | None = None
        self.history_df: pd.DataFrame | None = None

        self.beta_card: DashboardCard | None = None
        self.alpha_card: DashboardCard | None = None
        self.sharpe_card: DashboardCard | None = None
        self.volatility_card: DashboardCard | None = None
        self.drawdown_card: DashboardCard | None = None

        self.benchmark_chart: ChartWidget | None = None
        self.drawdown_chart: ChartWidget | None = None
        self.metrics_table: ResultTable | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        self.content.grid_columnconfigure(0, weight=1)

        self._build_toolbar()
        self._build_cards()
        self._build_charts()
        self._build_table()

    def _build_toolbar(self) -> None:
        toolbar = ctk.CTkFrame(self.content)
        toolbar.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 10))

        self.import_button = ctk.CTkButton(
            toolbar,
            text="Import Portfolio",
            command=self.import_file,
        )
        self.import_button.pack(side="left", padx=10, pady=10)

        self.period_option = ctk.CTkOptionMenu(
            toolbar,
            values=["6mo", "1y", "2y", "5y"],
        )
        self.period_option.set("1y")
        self.period_option.pack(side="left", padx=10, pady=10)

        self.refresh_button = ctk.CTkButton(
            toolbar,
            text="Calculate Risk",
            command=self.calculate_risk,
        )
        self.refresh_button.pack(side="left", padx=10, pady=10)

    def _build_cards(self) -> None:
        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))

        for column in range(5):
            cards.grid_columnconfigure(column, weight=1)

        self.beta_card = DashboardCard(cards, title="Beta", value="0.00", icon="β")
        self.alpha_card = DashboardCard(cards, title="Alpha", value="0.00%", icon="α")
        self.sharpe_card = DashboardCard(cards, title="Sharpe", value="0.00", icon="⚡")
        self.volatility_card = DashboardCard(cards, title="Volatility", value="0.00%", icon="📊")
        self.drawdown_card = DashboardCard(cards, title="Max DD", value="0.00%", icon="📉")

        self.beta_card.grid(row=0, column=0, sticky="ew", padx=6)
        self.alpha_card.grid(row=0, column=1, sticky="ew", padx=6)
        self.sharpe_card.grid(row=0, column=2, sticky="ew", padx=6)
        self.volatility_card.grid(row=0, column=3, sticky="ew", padx=6)
        self.drawdown_card.grid(row=0, column=4, sticky="ew", padx=6)

    def _build_charts(self) -> None:
        charts = ctk.CTkFrame(self.content, fg_color="transparent")
        charts.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 12))
        charts.grid_columnconfigure(0, weight=1)
        charts.grid_rowconfigure(0, weight=1)
        charts.grid_rowconfigure(1, weight=1)

        self.benchmark_chart = ChartWidget(charts)
        self.benchmark_chart.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.drawdown_chart = ChartWidget(charts)
        self.drawdown_chart.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

    def _build_table(self) -> None:
        table_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        table_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_columnconfigure(0, weight=1)

        self.metrics_table = ResultTable(table_frame)
        self.metrics_table.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

    def import_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select Portfolio File",
            filetypes=[
                ("Excel Files", "*.xlsx *.xls"),
                ("CSV Files", "*.csv"),
            ],
        )

        if not file_path:
            return

        try:
            if file_path.endswith(".csv"):
                self.dataframe = pd.read_csv(file_path)
            else:
                self.dataframe = pd.read_excel(file_path)

            self.set_status("Portfolio imported. Click Calculate Risk.")

        except Exception as error:
            messagebox.showerror("Import Error", str(error))

    def calculate_risk(self) -> None:
        if self.dataframe is None or self.dataframe.empty:
            self.set_status("Please import portfolio file first.")
            return

        try:
            self.set_status("Calculating risk analytics...")

            result = RiskAnalyticsService.analyze(
                self.dataframe,
                period=self.period_option.get(),
            )

            self.history_df = result.history

            self._update_cards(result.metrics)
            self._update_charts(result.history)
            self._update_table(result.metrics)

            self.set_status("Risk analytics calculated successfully.")

        except Exception as error:
            self.set_status("Risk calculation failed.")
            messagebox.showerror("Risk Analytics", str(error))

    def _update_cards(self, metrics: dict) -> None:
        self.beta_card.set_value(f"{metrics['Beta']:.2f}")
        self.alpha_card.set_value(f"{metrics['Alpha']:.2f}%")
        self.sharpe_card.set_value(f"{metrics['Sharpe Ratio']:.2f}")
        self.volatility_card.set_value(f"{metrics['Volatility']:.2f}%")
        self.drawdown_card.set_value(f"{metrics['Max Drawdown']:.2f}%")

        if metrics["Alpha"] >= 0:
            self.alpha_card.set_status("success")
        else:
            self.alpha_card.set_status("error")

        if metrics["Max Drawdown"] <= -10:
            self.drawdown_card.set_status("error")
        else:
            self.drawdown_card.set_status("success")

    def _update_charts(self, history: pd.DataFrame) -> None:
        if history is None or history.empty:
            return

        history = history.copy()
        history["DateLabel"] = pd.to_datetime(history["Date"]).dt.strftime("%d-%b")

        if self.benchmark_chart is not None:
            self.benchmark_chart.plot_line(
                x=history["DateLabel"].tolist(),
                y=history["Portfolio Growth"].tolist(),
                title="Portfolio Growth vs Nifty 50",
                xlabel="Date",
                ylabel="Growth Index",
            )

        if self.drawdown_chart is not None:
            self.drawdown_chart.plot_line(
                x=history["DateLabel"].tolist(),
                y=history["Drawdown %"].tolist(),
                title="Portfolio Drawdown",
                xlabel="Date",
                ylabel="Drawdown %",
            )

    def _update_table(self, metrics: dict) -> None:
        rows = [
            {"Metric": key, "Value": self._format_metric(key, value)}
            for key, value in metrics.items()
        ]

        metrics_df = pd.DataFrame(rows)

        if self.metrics_table is not None:
            self.metrics_table.load_dataframe(metrics_df)

    @staticmethod
    def _format_metric(key: str, value: float) -> str:
        if key in {
            "Portfolio Return",
            "Benchmark Return",
            "Alpha",
            "Volatility",
            "Max Drawdown",
        }:
            return f"{value:.2f}%"

        return f"{value:.2f}"
