"""
Finance Utility Suite
MTF Analyzer Page

Author : Shiva Kumar
Version: 0.99
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
import pandas as pd

from core.services.mtf_service import MTFService
from desktop.base_page import BasePage
from desktop.widgets.activity_log import ActivityLog
from desktop.widgets.chart_widget import ChartWidget
from desktop.widgets.dashboard_card import DashboardCard
from desktop.widgets.mini_table import MiniTable
from desktop.widgets.progress_widget import ProgressWidget
from desktop.widgets.result_table import ResultTable


class MTFPage(BasePage):
    """MTF Analyzer page."""

    VERSION = "v0.99"
    SEARCH_COLUMNS = ("AccountId", "Symbol")

    def __init__(self, master):
        super().__init__(
            master,
            title="MTF Risk Dashboard",
        )

        self.dataframe: pd.DataFrame | None = None
        self.filtered_dataframe: pd.DataFrame | None = None
        self._last_file_path: str | None = None
        self._last_refresh_time: datetime | None = None

        self._build_ui()
        self._bind_shortcuts()

    def _build_ui(self) -> None:
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(4, weight=1)

        self._build_cards()
        self._build_toolbar()
        self._build_progress()
        self._build_analytics_area()
        self._build_result_table()
        self._build_status_bar()

        self.progress.grid_remove()
        self._update_footer_status()

    def _build_progress(self) -> None:
        self.import_button = ctk.CTkButton(
            self.header,
            text="Import MTF File",
            command=self.import_file,
            width=160,
        )
        self.import_button.grid(
            row=0,
            column=2,
            padx=(10, 0),
        )

        self.progress = ProgressWidget(
            self.content,
            title="Import Progress",
        )
        self.progress.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=20,
            pady=(0, 12),
        )

    def _build_cards(self) -> None:
        cards_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        cards_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(5, 12))

        for column in range(6):
            cards_frame.grid_columnconfigure(column, weight=1)

        self.clients_card = DashboardCard(cards_frame, title="Clients", value="0")
        self.clients_card.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.positions_card = DashboardCard(cards_frame, title="Positions", value="0")
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
        self.mtm_card.grid(row=0, column=3, sticky="ew", padx=10)

        self.margin_card = DashboardCard(
            cards_frame,
            title="Margin Used",
            value="₹0.00",
        )
        self.margin_card.grid(row=0, column=4, sticky="ew", padx=10)

        self.risk_card = DashboardCard(
            cards_frame,
            title="Risk Level",
            value="LOW",
        )
        self.risk_card.grid(row=0, column=5, sticky="ew", padx=(10, 0))

    def _build_toolbar(self) -> None:
        toolbar = ctk.CTkFrame(self.content)
        toolbar.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))

        toolbar.grid_columnconfigure(1, weight=1)

        search_label = ctk.CTkLabel(
            toolbar,
            text="Search Client / Symbol",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        search_label.grid(row=0, column=0, sticky="w", padx=(12, 8), pady=12)

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            toolbar,
            textvariable=self.search_var,
            placeholder_text="Type AccountId or Symbol...",
            height=34,
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=12)
        self.search_entry.bind("<KeyRelease>", self._on_search)

        self.refresh_button = ctk.CTkButton(
            toolbar,
            text="Refresh",
            command=self.refresh_dashboard,
            width=115,
            height=34,
        )
        self.refresh_button.grid(row=0, column=2, padx=(0, 10), pady=12)

        self.export_excel_button = ctk.CTkButton(
            toolbar,
            text="Export Excel",
            command=self.export_excel,
            width=130,
            height=34,
        )
        self.export_excel_button.grid(row=0, column=3, padx=(0, 10), pady=12)

        self.export_pdf_button = ctk.CTkButton(
            toolbar,
            text="Export PDF",
            command=self.export_pdf,
            width=115,
            height=34,
            state="disabled",
        )
        self.export_pdf_button.grid(row=0, column=4, padx=(0, 12), pady=12)

    def _build_analytics_area(self) -> None:
        analytics_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        analytics_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 12))

        analytics_frame.grid_columnconfigure(0, weight=1)
        analytics_frame.grid_columnconfigure(1, weight=1)

        self.exposure_chart = ChartWidget(
            analytics_frame,
            title="Top Symbol Exposure",
        )
        self.exposure_chart.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 10),
            pady=(0, 10),
        )

        self.margin_chart = ChartWidget(
            analytics_frame,
            title="Margin Distribution",
        )
        self.margin_chart.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(10, 0),
            pady=(0, 10),
        )

        self.top_exposure_table = MiniTable(
            analytics_frame,
            title="Top Exposure Clients",
        )
        self.top_exposure_table.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(0, 10),
            pady=10,
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
            pady=10,
        )

        self.activity_log = ActivityLog(
            analytics_frame,
            height=150,
        )
        self.activity_log.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=(0, 10),
            pady=(10, 0),
        )

        self.losers_table = MiniTable(
            analytics_frame,
            title="Top MTM Losers",
        )
        self.losers_table.grid(
            row=2,
            column=1,
            sticky="nsew",
            padx=(10, 0),
            pady=(10, 0),
        )

    def _build_result_table(self) -> None:
        table_frame = ctk.CTkFrame(self.content)
        table_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=1)

        self.table_title = ctk.CTkLabel(
            table_frame,
            text="Full MTF Data",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.table_title.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 5))

        self.result_table = ResultTable(table_frame)
        self.result_table.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)


    def _build_status_bar(self) -> None:
        self.status_bar = ctk.CTkFrame(self, height=34)
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))

        for column in range(4):
            self.status_bar.grid_columnconfigure(column, weight=1)

        self.records_status = ctk.CTkLabel(
            self.status_bar,
            text="Records: 0",
            anchor="w",
        )
        self.records_status.grid(row=0, column=0, sticky="w", padx=12, pady=6)

        self.filtered_status = ctk.CTkLabel(
            self.status_bar,
            text="Filtered: 0",
            anchor="w",
        )
        self.filtered_status.grid(row=0, column=1, sticky="w", padx=12, pady=6)

        self.refresh_status = ctk.CTkLabel(
            self.status_bar,
            text="Last Refresh: -",
            anchor="w",
        )
        self.refresh_status.grid(row=0, column=2, sticky="w", padx=12, pady=6)

        self.version_status = ctk.CTkLabel(
            self.status_bar,
            text=f"Version: {self.VERSION}",
            anchor="e",
        )
        self.version_status.grid(row=0, column=3, sticky="e", padx=12, pady=6)

    def _bind_shortcuts(self) -> None:
        root = self.winfo_toplevel()

        root.bind("<F5>", self._on_refresh_shortcut)
        root.bind("<Control-e>", self._on_export_shortcut)
        root.bind("<Control-E>", self._on_export_shortcut)
        root.bind("<Escape>", self._on_escape_shortcut)

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
            self._set_busy_state(True)
            self._show_progress()
            self.progress.reset()
            self.activity_log.clear()

            self.status_label.configure(text="Importing file...")
            self.activity_log.success("Loading MTF file...")
            self.progress.update_progress(0.20, "Loading file")

            dataframe, _summary = MTFService.load(file_path)

            self.activity_log.success("Validating columns...")
            self.progress.update_progress(0.40, "Validating file")
            MTFService.validate_dataframe(dataframe)

            self.dataframe = dataframe
            self.filtered_dataframe = dataframe.copy()
            self._last_file_path = file_path
            self.search_var.set("")

            self.activity_log.success("Updating dashboard...")
            self.progress.update_progress(0.70, "Updating dashboard")
            self._refresh_all(dataframe)

            self.activity_log.success("Loading full MTF data...")
            self.progress.update_progress(0.90, "Loading table")
            self._refresh_result_table(dataframe)

            self._last_refresh_time = datetime.now()
            self.activity_log.success("Import completed")
            self.progress.complete("Ready")
            self._update_table_title(dataframe)
            self._update_footer_status(dataframe)
            self.status_label.configure(text="MTF file imported successfully")
            self.search_entry.focus_set()
            self.after(900, self._hide_progress)

        except Exception as error:
            self.status_label.configure(text="Import failed")
            self.progress.update_progress(0, "Import failed")
            self.activity_log.error(str(error))
            messagebox.showerror("MTF Import Error", str(error))
        finally:
            self._set_busy_state(False)

    def refresh_dashboard(self) -> None:
        if self.dataframe is None or self.dataframe.empty:
            messagebox.showinfo("Refresh Dashboard", "Please import an MTF file first.")
            return

        self.search_var.set("")
        self.filtered_dataframe = self.dataframe.copy()
        self._last_refresh_time = datetime.now()

        self._refresh_all(self.filtered_dataframe)
        self._refresh_result_table(self.filtered_dataframe)
        self._update_table_title(self.filtered_dataframe)
        self._update_footer_status(self.filtered_dataframe)
        self.status_label.configure(text="Dashboard refreshed")

        if hasattr(self, "activity_log"):
            self.activity_log.success("Dashboard refreshed")

    def export_excel(self) -> None:
        export_data = self._get_active_dataframe()

        if export_data is None or export_data.empty:
            messagebox.showinfo("Export Excel", "No data available to export.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"MTF_Risk_Dashboard_{timestamp}.xlsx"

        file_path = filedialog.asksaveasfilename(
            title="Export MTF Data",
            defaultextension=".xlsx",
            initialfile=default_name,
            filetypes=[
                ("Excel Files", "*.xlsx"),
                ("All Files", "*.*"),
            ],
        )

        if not file_path:
            return

        try:
            self._set_busy_state(True)
            self._show_progress()
            self.progress.reset()
            self.progress.update_progress(0.30, "Preparing export")

            output_path = Path(file_path)
            export_data.to_excel(output_path, index=False)

            self.progress.update_progress(1.00, "Export complete")
            self.status_label.configure(text=f"Exported: {output_path.name}")
            self.activity_log.success(f"Exported Excel file: {output_path.name}")
            messagebox.showinfo(
                "Export Complete",
                f"MTF data exported successfully.\n\n{output_path}",
            )
            self.after(700, self._hide_progress)

        except Exception as error:
            self.status_label.configure(text="Export failed")
            self.activity_log.error(str(error))
            messagebox.showerror("Export Error", str(error))
        finally:
            self._set_busy_state(False)

    def export_pdf(self) -> None:
        messagebox.showinfo(
            "Export PDF",
            "PDF export will be connected in a future version.",
        )

    def _on_search(self, _event=None) -> None:
        if self.dataframe is None or self.dataframe.empty:
            return

        filtered = self._filter_dataframe(self.search_var.get())
        self.filtered_dataframe = filtered

        self._refresh_result_table(filtered)
        self._update_table_title(filtered)
        self._update_footer_status(filtered)

        if filtered.empty:
            self.status_label.configure(text="No matching records found")
            return

        self.status_label.configure(text=f"Showing {len(filtered):,} matching records")

    def _filter_dataframe(self, search_text: str) -> pd.DataFrame:
        if self.dataframe is None:
            return pd.DataFrame()

        query = search_text.strip()

        if not query:
            return self.dataframe.copy()

        searchable_columns = [
            column for column in self.SEARCH_COLUMNS if column in self.dataframe.columns
        ]

        if not searchable_columns:
            return self.dataframe.copy()

        mask = pd.Series(False, index=self.dataframe.index)

        for column in searchable_columns:
            column_values = self.dataframe[column].fillna("").astype(str)
            mask |= column_values.str.contains(query, case=False, na=False)

        return self.dataframe.loc[mask].copy()

    def _refresh_all(self, dataframe: pd.DataFrame) -> None:
        self.activity_log.success("Updating charts and tables...")
        self._refresh_dashboard(dataframe)
        self._refresh_chart(dataframe)
        self._refresh_margin_chart(dataframe)
        self._refresh_top_exposure_table(dataframe)
        self._refresh_gainers_table(dataframe)
        self._refresh_losers_table(dataframe)

    def _refresh_dashboard(self, dataframe: pd.DataFrame) -> None:
        summary = MTFService.calculate_summary(dataframe)
        risk = MTFService.risk_summary(dataframe)

        self._update_card(self.clients_card, str(summary["clients"]))
        self._update_card(self.positions_card, str(summary["positions"]))
        self._update_card(
            self.buy_value_card,
            self._format_currency(summary["buy_value"]),
        )
        self._update_card(
            self.mtm_card,
            self._format_currency(summary["total_mtm"]),
        )
        self._update_card(
            self.margin_card,
            self._format_currency(summary["margin"]),
        )

        if risk["high"] > 0:
            level = "HIGH"
        elif risk["medium"] > 0:
            level = "MEDIUM"
        else:
            level = "LOW"

        self._update_card(self.risk_card, level)

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

    def _refresh_margin_chart(self, dataframe: pd.DataFrame) -> None:
        chart_data = MTFService.margin_distribution(dataframe)

        if chart_data is None or chart_data.empty:
            self.margin_chart.clear()
            return

        label_column = chart_data.columns[0]
        value_column = chart_data.columns[-1]

        self.margin_chart.plot_bar(
            labels=chart_data[label_column].astype(str).tolist(),
            values=chart_data[value_column].astype(float).tolist(),
            title="Margin Distribution",
            xlabel="Range",
            ylabel="Clients",
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

    def _refresh_losers_table(self, dataframe: pd.DataFrame) -> None:
        table_data = MTFService.top_mtm_losers(dataframe)

        self._load_mini_table(
            table=self.losers_table,
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


    def _show_progress(self) -> None:
        self.progress.grid()

    def _hide_progress(self) -> None:
        self.progress.grid_remove()

    def _get_active_dataframe(self) -> pd.DataFrame | None:
        if self.filtered_dataframe is not None:
            return self.filtered_dataframe

        return self.dataframe

    def _update_table_title(self, dataframe: pd.DataFrame | None) -> None:
        if dataframe is None:
            self.table_title.configure(text="Full MTF Data")
            return

        total_rows = len(self.dataframe) if self.dataframe is not None else len(dataframe)
        visible_rows = len(dataframe)

        if visible_rows == total_rows:
            title = f"Full MTF Data ({total_rows:,} records)"
        else:
            title = f"Filtered MTF Data ({visible_rows:,} of {total_rows:,} records)"

        self.table_title.configure(text=title)

    def _update_footer_status(self, dataframe: pd.DataFrame | None = None) -> None:
        total_records = len(self.dataframe) if self.dataframe is not None else 0
        filtered_records = len(dataframe) if dataframe is not None else total_records

        if self._last_refresh_time is None:
            refresh_text = "Last Refresh: -"
        else:
            refresh_time = self._last_refresh_time.strftime("%d-%b-%Y %I:%M:%S %p")
            refresh_text = f"Last Refresh: {refresh_time}"

        self.records_status.configure(text=f"Records: {total_records:,}")
        self.filtered_status.configure(text=f"Filtered: {filtered_records:,}")
        self.refresh_status.configure(text=refresh_text)
        self.version_status.configure(text=f"Version: {self.VERSION}")

    def _set_busy_state(self, is_busy: bool) -> None:
        cursor = "watch" if is_busy else ""
        state = "disabled" if is_busy else "normal"

        try:
            self.configure(cursor=cursor)
            self.refresh_button.configure(state=state)
            self.export_excel_button.configure(state=state)

            if is_busy:
                self.search_entry.configure(state="disabled")
            else:
                self.search_entry.configure(state="normal")

            self.update_idletasks()
        except Exception:
            return

    def _on_refresh_shortcut(self, _event=None) -> None:
        self.refresh_dashboard()

    def _on_export_shortcut(self, _event=None) -> None:
        self.export_excel()

    def _on_escape_shortcut(self, _event=None) -> None:
        if hasattr(self, "search_var"):
            self.search_var.set("")
            self._on_search()

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
