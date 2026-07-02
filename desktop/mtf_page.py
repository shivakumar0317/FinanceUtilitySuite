"""
Finance Utility Suite
MTF Analyzer Page
"""

from __future__ import annotations

from tkinter import filedialog, messagebox

import customtkinter as ctk
import pandas as pd

from core.services.mtf_service import MTFService
from desktop.widgets.chart_widget import ChartWidget
from desktop.widgets.dashboard_card import DashboardCard
from desktop.widgets.mini_table import MiniTable
from desktop.widgets.result_table import ResultTable



class MTFPage(ctk.CTkFrame):
    """MTF Analyzer page."""

    def __init__(self, master):
        super().__init__(master)

        self.dataframe: pd.DataFrame | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._build_header()
        self._build_cards()
        self._build_analytics_area()
        self._build_result_table()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            header,
            text="MTF Analyzer",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.grid(row=0, column=0, sticky="w")

        self.status_label = ctk.CTkLabel(
            header,
            text="No file imported",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.status_label.grid(row=0, column=1, sticky="e", padx=10)

        import_button = ctk.CTkButton(
            header,
            text="Import MTF File",
            command=self.import_file,
            width=160,
        )
        import_button.grid(row=0, column=2, sticky="e")

    def _build_cards(self) -> None:
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        for column in range(4):
            cards_frame.grid_columnconfigure(column, weight=1)

        self.clients_card = DashboardCard(
            cards_frame,
            title="Clients",
            value="0",
        )
        self.clients_card.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.positions_card = DashboardCard(
            cards_frame,
            title="Positions",
            value="0",
        )
        self.positions_card.grid(row=0, column=1, sticky="ew", padx=10)

        self.buy_value_card = DashboardCard(
            cards_frame,
            title="Buy Value",
            value="₹0.00",
        )
        self.buy_value_card.grid(row=0, column=2, sticky="ew", padx=10)

        self.mtm_card = DashboardCard(
            cards_frame,
            title="Total MTM",
            value="₹0.00",
        )
        self.mtm_card.grid(row=0, column=3, sticky="ew", padx=(10, 0))

    def _build_analytics_area(self) -> None:
        analytics_frame = ctk.CTkFrame(self, fg_color="transparent")
        analytics_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        analytics_frame.grid_columnconfigure(0, weight=2)
        analytics_frame.grid_columnconfigure(1, weight=1)
        analytics_frame.grid_rowconfigure(0, weight=1)
        analytics_frame.grid_rowconfigure(1, weight=1)

        self.exposure_chart = ChartWidget(
            analytics_frame,
            title="Top Symbol Exposure",
        )
        self.exposure_chart.grid(
            row=0,
            column=0,
            rowspan=2,
            sticky="nsew",
            padx=(0, 10),
        )

        self.top_exposure_table = MiniTable(
            analytics_frame,
            title="Top Exposure Clients",
        )
        self.top_exposure_table.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(10, 0),
            pady=(0, 10),
        )

        self.gainers_table = MiniTable(
            analytics_frame,
            title="Top MTM Gainers",
        )
        self.gainers_table.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(10, 0),
            pady=(10, 0),
        )

    def _build_result_table(self) -> None:
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(10, 20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(
            table_frame,
            text="Full MTF Data",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 5))

        self.result_table = ResultTable(table_frame)
        self.result_table.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    def import_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select MTF File",
            filetypes=[
                ("Excel Files", "*.xlsx *.xls"),
                ("CSV Files", "*.csv"),
                ("All Files", "*.*"),
            ],
        )

        if not file_path:
            return

        try:
            self.status_label.configure(text="Importing file...")

            dataframe = MTFService.load(file_path)
            MTFService.validate_dataframe(dataframe)

            self.dataframe = dataframe

            self._refresh_dashboard(dataframe)
            self._refresh_chart(dataframe)
            self._refresh_top_exposure_table(dataframe)
            self._refresh_gainers_table(dataframe)
            self._refresh_result_table(dataframe)

            self.status_label.configure(text="MTF file imported successfully")

        except Exception as error:
            self.status_label.configure(text="Import failed")
            messagebox.showerror("MTF Import Error", str(error))

    def _refresh_dashboard(self, dataframe: pd.DataFrame) -> None:
        summary = MTFService.calculate_summary(dataframe)

        self._update_card(
            self.clients_card,
            str(summary.get("clients", 0)),
        )
        self._update_card(
            self.positions_card,
            str(summary.get("positions", 0)),
        )
        self._update_card(
            self.buy_value_card,
            self._format_currency(summary.get("buy_value", 0)),
        )
        self._update_card(
            self.mtm_card,
            self._format_currency(summary.get("total_mtm", 0)),
        )

    def _refresh_chart(self, dataframe: pd.DataFrame) -> None:
        chart_data = MTFService.symbol_exposure(dataframe)

        if chart_data is None or chart_data.empty:
            self.exposure_chart.clear()
            return

        label_column = "Symbol"
        value_column = "BUY VALUE"

        if label_column not in chart_data.columns:
            label_column = chart_data.columns[0]

        if value_column not in chart_data.columns:
            value_column = chart_data.columns[-1]

        self.exposure_chart.plot_bar(
            labels=chart_data[label_column].astype(str).tolist(),
            values=chart_data[value_column].astype(float).tolist(),
            title="Top Symbol Exposure",
            xlabel="Symbol",
            ylabel="Exposure",
        )

    def _refresh_top_exposure_table(self, dataframe: pd.DataFrame) -> None:
        table_data = MTFService.top_exposure(dataframe)
        self._load_mini_table(
            table=self.top_exposure_table,
            dataframe=table_data,
            preferred_columns=["AccountId", "BUY VALUE", "MarkToMarket"],
        )

    def _refresh_gainers_table(self, dataframe: pd.DataFrame) -> None:
        table_data = MTFService.top_mtm_gainers(dataframe)
        self._load_mini_table(
            table=self.gainers_table,
            dataframe=table_data,
            preferred_columns=["AccountId", "Symbol", "MarkToMarket"],
        )

    def _refresh_result_table(self, dataframe: pd.DataFrame) -> None:
        self.result_table.load_dataframe(dataframe)

    def _load_mini_table(
        self,
        table: MiniTable,
        dataframe: pd.DataFrame | None,
        preferred_columns: list[str],
    ) -> None:
        if dataframe is None or dataframe.empty:
            table.set_data([])
            return

        display_columns = [
            column for column in preferred_columns if column in dataframe.columns
        ]

        if not display_columns:
            display_columns = list(dataframe.columns[:3])

        rows = []

        for _, row in dataframe[display_columns].iterrows():
            rows.append([self._format_cell(value) for value in row.tolist()])

        table.set_headers(display_columns)
        table.set_data(rows)

    def _update_card(self, card: DashboardCard, value: str) -> None:
        if hasattr(card, "set_value"):
            card.set_value(value)
            return

        if hasattr(card, "update_value"):
            card.update_value(value)
            return

        if hasattr(card, "value_label"):
            card.value_label.configure(text=value)

    def _format_currency(self, value: float | int | str) -> str:
        try:
            amount = float(value)
        except (TypeError, ValueError):
            amount = 0

        return f"₹{amount:,.2f}"

    def _format_cell(self, value: object) -> str:
        if pd.isna(value):
            return ""

        if isinstance(value, float):
            return f"{value:,.2f}"

        if isinstance(value, int):
            return f"{value:,}"

        return str(value)