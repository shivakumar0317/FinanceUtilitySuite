"""
Finance Utility Suite
MTF Concentration Risk Dashboard

Author  : Shiva Kumar
Version : 1.30
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
import pandas as pd

from core.concentration_service import ConcentrationService
from desktop.base_page import BasePage
from desktop.theme import Theme
from desktop.widgets.activity_log import ActivityLog
from desktop.widgets.chart_widget import ChartWidget
from desktop.widgets.dashboard_card import DashboardCard
from desktop.widgets.mini_table import MiniTable
from desktop.widgets.progress_widget import ProgressWidget
from desktop.widgets.result_table import ResultTable


class ConcentrationRiskPage(BasePage):
    """MTF Concentration Risk Dashboard page."""

    VERSION = "v1.30"
    SEARCH_COLUMNS = ("AccountId", "Largest Stock", "Risk Level")

    def __init__(self, master):
        super().__init__(master, title="MTF Concentration Risk Dashboard")

        self.service = ConcentrationService()
        self.source_dataframe: pd.DataFrame | None = None
        self.summary_dataframe: pd.DataFrame | None = None
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

    def _build_cards(self) -> None:
        cards_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        cards_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(5, 12))

        for column in range(6):
            cards_frame.grid_columnconfigure(column, weight=1)

        self.total_clients_card = DashboardCard(cards_frame, title="Total Clients", value="0", icon="👥")
        self.total_clients_card.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.single_stock_card = DashboardCard(cards_frame, title="Single Stock", value="0", icon="🎯")
        self.single_stock_card.grid(row=0, column=1, sticky="ew", padx=10)

        self.multiple_stock_card = DashboardCard(cards_frame, title="Multiple Stocks", value="0", icon="📚")
        self.multiple_stock_card.grid(row=0, column=2, sticky="ew", padx=10)

        self.critical_risk_card = DashboardCard(cards_frame, title="Critical Risk", value="0", icon="⚠️")
        self.critical_risk_card.grid(row=0, column=3, sticky="ew", padx=10)

        self.highest_concentration_card = DashboardCard(
            cards_frame,
            title="Highest Single Stock %",
            value="0.00%",
            icon="📊",
        )
        self.highest_concentration_card.grid(row=0, column=4, sticky="ew", padx=10)

        self.total_exposure_card = DashboardCard(
            cards_frame,
            title="Total Exposure",
            value="₹0.00",
            icon="💰",
        )
        self.total_exposure_card.grid(row=0, column=5, sticky="ew", padx=(10, 0))

    def _build_toolbar(self) -> None:
        toolbar = ctk.CTkFrame(self.content)
        toolbar.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))
        toolbar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            toolbar,
            text="Search Client / Stock / Risk",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=(12, 8), pady=12)

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            toolbar,
            textvariable=self.search_var,
            placeholder_text="Type AccountId, largest stock, or risk level...",
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

        self.clear_button = ctk.CTkButton(
            toolbar,
            text="Clear",
            command=self.clear_dashboard,
            width=95,
            height=34,
        )
        self.clear_button.grid(row=0, column=4, padx=(0, 12), pady=12)

    def _build_progress(self) -> None:
        self.import_button = ctk.CTkButton(
            self.header,
            text="Import MTF File",
            command=self.import_file,
            width=160,
        )
        self.import_button.grid(row=0, column=2, padx=(10, 0))

        self.progress = ProgressWidget(self.content, title="Import Progress")
        self.progress.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 12))

    def _build_analytics_area(self) -> None:
        analytics_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        analytics_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 12))
        analytics_frame.grid_columnconfigure(0, weight=1)
        analytics_frame.grid_columnconfigure(1, weight=1)

        self.concentration_chart = ChartWidget(
            analytics_frame,
            title="Client Concentration Distribution",
        )
        self.concentration_chart.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))

        self.risk_chart = ChartWidget(analytics_frame, title="Risk Distribution")
        self.risk_chart.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))

        self.single_stock_table = MiniTable(analytics_frame, title="Single Stock Clients")
        self.single_stock_table.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=10)

        self.top_concentrated_table = MiniTable(
            analytics_frame,
            title="Top Concentrated Clients",
        )
        self.top_concentrated_table.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=10)

        self.activity_log = ActivityLog(analytics_frame, height=150)
        self.activity_log.grid(row=2, column=0, sticky="nsew", padx=(0, 10), pady=(10, 0))

        self.multiple_stock_table = MiniTable(
            analytics_frame,
            title="Multiple Stock Clients",
        )
        self.multiple_stock_table.grid(row=2, column=1, sticky="nsew", padx=(10, 0), pady=(10, 0))

    def _build_result_table(self) -> None:
        table_frame = ctk.CTkFrame(self.content)
        table_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=1)

        self.table_title = ctk.CTkLabel(
            table_frame,
            text="Client Concentration Summary",
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

        self.records_status = ctk.CTkLabel(self.status_bar, text="Clients: 0", anchor="w")
        self.records_status.grid(row=0, column=0, sticky="w", padx=12, pady=6)

        self.filtered_status = ctk.CTkLabel(self.status_bar, text="Filtered: 0", anchor="w")
        self.filtered_status.grid(row=0, column=1, sticky="w", padx=12, pady=6)

        self.refresh_status = ctk.CTkLabel(self.status_bar, text="Last Refresh: -", anchor="w")
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

            self.status_label.configure(text="Importing MTF concentration data...")
            self.activity_log.success("Loading MTF file...")
            self.progress.update_progress(0.15, "Loading file")

            dataframe = self._read_file(file_path)

            self.activity_log.success("Validating concentration columns...")
            self.progress.update_progress(0.35, "Validating file")
            self.service.load_dataframe(dataframe)

            self.activity_log.success("Calculating client concentration...")
            self.progress.update_progress(0.60, "Calculating concentration")
            summary = self.service.calculate_concentration()

            self.source_dataframe = dataframe
            self.summary_dataframe = summary
            self.filtered_dataframe = summary.copy()
            self._last_file_path = file_path
            self.search_var.set("")

            self.activity_log.success("Updating dashboard...")
            self.progress.update_progress(0.80, "Updating dashboard")
            self._refresh_all(summary)

            self.progress.update_progress(0.95, "Loading table")
            self._refresh_result_table(summary)

            self._last_refresh_time = datetime.now()
            self.progress.complete("Ready")
            self.activity_log.success("Concentration analysis completed")
            self._update_table_title(summary)
            self._update_footer_status(summary)
            self.status_label.configure(text="MTF concentration analysis completed successfully")
            self.search_entry.focus_set()
            self.after(900, self._hide_progress)

        except Exception as error:
            self.status_label.configure(text="Concentration import failed")
            self.progress.update_progress(0, "Import failed")
            self.activity_log.error(str(error))
            messagebox.showerror("Concentration Import Error", str(error))
        finally:
            self._set_busy_state(False)

    def refresh_dashboard(self) -> None:
        if self.source_dataframe is None or self.source_dataframe.empty:
            messagebox.showinfo("Refresh Dashboard", "Please import an MTF file first.")
            return

        try:
            self._set_busy_state(True)
            self.service.load_dataframe(self.source_dataframe)
            summary = self.service.calculate_concentration()

            self.summary_dataframe = summary
            self.filtered_dataframe = summary.copy()
            self.search_var.set("")
            self._last_refresh_time = datetime.now()

            self._refresh_all(summary)
            self._refresh_result_table(summary)
            self._update_table_title(summary)
            self._update_footer_status(summary)
            self.status_label.configure(text="Concentration dashboard refreshed")
            self.activity_log.success("Concentration dashboard refreshed")
        except Exception as error:
            self.activity_log.error(str(error))
            messagebox.showerror("Refresh Error", str(error))
        finally:
            self._set_busy_state(False)

    def clear_dashboard(self) -> None:
        if self.summary_dataframe is None or self.summary_dataframe.empty:
            return

        if not messagebox.askyesno("Clear Dashboard", "Clear the imported concentration data?"):
            return

        self.source_dataframe = None
        self.summary_dataframe = None
        self.filtered_dataframe = None
        self._last_file_path = None
        self._last_refresh_time = None
        self.service = ConcentrationService()
        self.search_var.set("")

        self._reset_cards()
        self.concentration_chart.clear()
        self.risk_chart.clear()
        self.single_stock_table.set_data([])
        self.top_concentrated_table.set_data([])
        self.multiple_stock_table.set_data([])
        self.result_table.load_dataframe(ConcentrationService._empty_summary())
        self.activity_log.clear()
        self.status_label.configure(text="Concentration dashboard cleared")
        self._update_table_title(None)
        self._update_footer_status()

    def export_excel(self) -> None:
        export_data = self._get_active_dataframe()

        if export_data is None or export_data.empty:
            messagebox.showinfo("Export Excel", "No concentration data available to export.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"MTF_Concentration_Risk_{timestamp}.xlsx"

        file_path = filedialog.asksaveasfilename(
            title="Export Concentration Risk Report",
            defaultextension=".xlsx",
            initialfile=default_name,
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
        )

        if not file_path:
            return

        try:
            self._set_busy_state(True)
            self._show_progress()
            self.progress.reset()
            self.progress.update_progress(0.20, "Preparing export")

            output_path = Path(file_path)
            summary = self.summary_dataframe.copy() if self.summary_dataframe is not None else pd.DataFrame()
            single_stock = self.service.get_single_stock_clients()
            multiple_stock = summary[summary["Holdings"] > 1].copy()
            distribution = self.service.get_distribution()

            self.progress.update_progress(0.45, "Writing worksheets")

            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                export_data.to_excel(writer, sheet_name="Filtered Summary", index=False)
                summary.to_excel(writer, sheet_name="Full Summary", index=False)
                single_stock.to_excel(writer, sheet_name="Single Stock", index=False)
                multiple_stock.to_excel(writer, sheet_name="Multiple Stocks", index=False)
                distribution.to_excel(writer, sheet_name="Distribution", index=False)

            self.progress.update_progress(1.00, "Export complete")
            self.status_label.configure(text=f"Exported: {output_path.name}")
            self.activity_log.success(f"Exported Excel file: {output_path.name}")
            messagebox.showinfo(
                "Export Complete",
                f"Concentration risk report exported successfully.\n\n{output_path}",
            )
            self.after(700, self._hide_progress)

        except Exception as error:
            self.status_label.configure(text="Export failed")
            self.activity_log.error(str(error))
            messagebox.showerror("Export Error", str(error))
        finally:
            self._set_busy_state(False)

    def _on_search(self, _event=None) -> None:
        if self.summary_dataframe is None or self.summary_dataframe.empty:
            return

        filtered = self._filter_dataframe(self.search_var.get())
        self.filtered_dataframe = filtered
        self._refresh_result_table(filtered)
        self._update_table_title(filtered)
        self._update_footer_status(filtered)

        if filtered.empty:
            self.status_label.configure(text="No matching concentration records found")
        else:
            self.status_label.configure(text=f"Showing {len(filtered):,} matching clients")

    def _filter_dataframe(self, search_text: str) -> pd.DataFrame:
        if self.summary_dataframe is None:
            return pd.DataFrame()

        query = search_text.strip()
        if not query:
            return self.summary_dataframe.copy()

        searchable_columns = [
            column for column in self.SEARCH_COLUMNS
            if column in self.summary_dataframe.columns
        ]

        if not searchable_columns:
            return self.summary_dataframe.copy()

        mask = pd.Series(False, index=self.summary_dataframe.index)

        for column in searchable_columns:
            values = self.summary_dataframe[column].fillna("").astype(str)
            mask |= values.str.contains(query, case=False, na=False)

        return self.summary_dataframe.loc[mask].copy()

    def _refresh_all(self, _dataframe: pd.DataFrame) -> None:
        self.activity_log.success("Updating concentration charts and tables...")
        self._refresh_dashboard_cards()
        self._refresh_concentration_chart()
        self._refresh_risk_chart()
        self._refresh_single_stock_table()
        self._refresh_top_concentrated_table()
        self._refresh_multiple_stock_table()

    def _refresh_dashboard_cards(self) -> None:
        summary = self.service.get_summary()

        self._update_card(self.total_clients_card, str(summary["total_clients"]))
        self._update_card(self.single_stock_card, str(summary["single_stock_clients"]))
        self._update_card(self.multiple_stock_card, str(summary["multiple_stock_clients"]))
        self._update_card(self.critical_risk_card, str(summary["critical_clients"]))
        self._update_card(
            self.highest_concentration_card,
            f'{summary["highest_concentration_percent"]:,.2f}%',
        )
        self._update_card(
            self.total_exposure_card,
            self._format_currency(summary["total_exposure"]),
        )

        self.single_stock_card.set_value_color(Theme.ERROR)
        self.single_stock_card.set_status("error")
        self.multiple_stock_card.set_value_color(Theme.SUCCESS)
        self.multiple_stock_card.set_status("success")

        if int(summary["critical_clients"]) > 0:
            self.critical_risk_card.set_value_color(Theme.ERROR)
            self.critical_risk_card.set_status("error")
        else:
            self.critical_risk_card.set_value_color(Theme.SUCCESS)
            self.critical_risk_card.set_status("success")

        highest = float(summary["highest_concentration_percent"])
        if highest >= 90:
            self.highest_concentration_card.set_value_color(Theme.ERROR)
            self.highest_concentration_card.set_status("error")
        elif highest >= 70:
            self.highest_concentration_card.set_value_color(Theme.WARNING)
            self.highest_concentration_card.set_status("warning")
        else:
            self.highest_concentration_card.set_value_color(Theme.SUCCESS)
            self.highest_concentration_card.set_status("success")

    def _refresh_concentration_chart(self) -> None:
        summary = self.service.get_summary()
        labels = ["Single Stock", "Multiple Stocks"]
        values = [
            int(summary["single_stock_clients"]),
            int(summary["multiple_stock_clients"]),
        ]

        if sum(values) <= 0:
            self.concentration_chart.clear()
            return

        if hasattr(self.concentration_chart, "plot_pie"):
            self.concentration_chart.plot_pie(
                labels=labels,
                values=values,
                title="Client Concentration Distribution",
            )
        else:
            self.concentration_chart.plot_bar(
                labels=labels,
                values=values,
                title="Client Concentration Distribution",
                xlabel="Category",
                ylabel="Clients",
            )

    def _refresh_risk_chart(self) -> None:
        if self.summary_dataframe is None or self.summary_dataframe.empty:
            self.risk_chart.clear()
            return

        risk_counts = self.summary_dataframe["Risk Level"].value_counts()
        labels = ["Critical", "High", "Medium", "Low"]
        values = [int(risk_counts.get(label, 0)) for label in labels]

        self.risk_chart.plot_bar(
            labels=labels,
            values=values,
            title="Risk Distribution",
            xlabel="Risk Level",
            ylabel="Clients",
        )

    def _refresh_single_stock_table(self) -> None:
        self._load_mini_table(
            self.single_stock_table,
            self.service.get_single_stock_clients(),
            ["AccountId", "Largest Stock", "Total Exposure"],
        )

    def _refresh_top_concentrated_table(self) -> None:
        self._load_mini_table(
            self.top_concentrated_table,
            self.service.get_top_concentrated_clients(limit=10),
            ["AccountId", "Largest Holding %", "Risk Level"],
        )

    def _refresh_multiple_stock_table(self) -> None:
        if self.summary_dataframe is None or self.summary_dataframe.empty:
            self.multiple_stock_table.set_data([])
            return

        table_data = (
            self.summary_dataframe[self.summary_dataframe["Holdings"] > 1]
            .sort_values(
                by=["Largest Holding %", "Total Exposure"],
                ascending=[False, False],
            )
            .head(10)
            .reset_index(drop=True)
        )

        self._load_mini_table(
            self.multiple_stock_table,
            table_data,
            ["AccountId", "Holdings", "Largest Holding %"],
        )

    def _refresh_result_table(self, dataframe: pd.DataFrame) -> None:
        self.result_table.load_dataframe(dataframe)

    @staticmethod
    def _read_file(file_path: str) -> pd.DataFrame:
        suffix = Path(file_path).suffix.lower()

        if suffix in {".xlsx", ".xls"}:
            return pd.read_excel(file_path)
        if suffix == ".csv":
            return pd.read_csv(file_path)

        raise ValueError("Unsupported file format. Please select an Excel or CSV file.")

    def _load_mini_table(
        self,
        table: MiniTable,
        dataframe: pd.DataFrame | None,
        preferred_columns: list[str],
        limit: int = 10,
    ) -> None:
        if dataframe is None or dataframe.empty:
            table.set_data([])
            return

        display_columns = [
            column for column in preferred_columns if column in dataframe.columns
        ]

        if not display_columns:
            display_columns = list(dataframe.columns[:3])

        rows = [
            [self._format_cell(value) for value in row.tolist()]
            for _, row in dataframe[display_columns].head(limit).iterrows()
        ]

        table.set_headers(display_columns)
        table.set_data(rows)

    def _reset_cards(self) -> None:
        self._update_card(self.total_clients_card, "0")
        self._update_card(self.single_stock_card, "0")
        self._update_card(self.multiple_stock_card, "0")
        self._update_card(self.critical_risk_card, "0")
        self._update_card(self.highest_concentration_card, "0.00%")
        self._update_card(self.total_exposure_card, "₹0.00")

    def _show_progress(self) -> None:
        self.progress.grid()

    def _hide_progress(self) -> None:
        self.progress.grid_remove()

    def _get_active_dataframe(self) -> pd.DataFrame | None:
        return self.filtered_dataframe if self.filtered_dataframe is not None else self.summary_dataframe

    def _update_table_title(self, dataframe: pd.DataFrame | None) -> None:
        if dataframe is None:
            self.table_title.configure(text="Client Concentration Summary")
            return

        total_rows = len(self.summary_dataframe) if self.summary_dataframe is not None else len(dataframe)
        visible_rows = len(dataframe)

        if visible_rows == total_rows:
            title = f"Client Concentration Summary ({total_rows:,} clients)"
        else:
            title = f"Filtered Concentration Summary ({visible_rows:,} of {total_rows:,} clients)"

        self.table_title.configure(text=title)

    def _update_footer_status(self, dataframe: pd.DataFrame | None = None) -> None:
        total_records = len(self.summary_dataframe) if self.summary_dataframe is not None else 0
        filtered_records = len(dataframe) if dataframe is not None else total_records

        if self._last_refresh_time is None:
            refresh_text = "Last Refresh: -"
        else:
            refresh_time = self._last_refresh_time.strftime("%d-%b-%Y %I:%M:%S %p")
            refresh_text = f"Last Refresh: {refresh_time}"

        self.records_status.configure(text=f"Clients: {total_records:,}")
        self.filtered_status.configure(text=f"Filtered: {filtered_records:,}")
        self.refresh_status.configure(text=refresh_text)
        self.version_status.configure(text=f"Version: {self.VERSION}")

    def _set_busy_state(self, is_busy: bool) -> None:
        cursor = "watch" if is_busy else ""
        state = "disabled" if is_busy else "normal"

        try:
            self.configure(cursor=cursor)
            self.import_button.configure(state=state)
            self.refresh_button.configure(state=state)
            self.export_excel_button.configure(state=state)
            self.clear_button.configure(state=state)
            self.search_entry.configure(state="disabled" if is_busy else "normal")
            self.update_idletasks()
        except Exception:
            return

    def _on_refresh_shortcut(self, _event=None) -> None:
        self.refresh_dashboard()

    def _on_export_shortcut(self, _event=None) -> None:
        self.export_excel()

    def _on_escape_shortcut(self, _event=None) -> None:
        self.search_var.set("")
        self._on_search()

    def _update_card(self, card: DashboardCard, value: str) -> None:
        if hasattr(card, "set_value"):
            card.set_value(value)
        elif hasattr(card, "update_value"):
            card.update_value(value)
        elif hasattr(card, "value_label"):
            card.value_label.configure(text=value)

    @staticmethod
    def _format_currency(value: float | int | str) -> str:
        try:
            amount = float(value)
        except (TypeError, ValueError):
            amount = 0.0
        return f"₹{amount:,.2f}"

    @staticmethod
    def _format_cell(value: object) -> str:
        if pd.isna(value):
            return ""
        if isinstance(value, float):
            return f"{value:,.2f}"
        if isinstance(value, int):
            return f"{value:,}"
        return str(value)
