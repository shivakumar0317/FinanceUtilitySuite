"""
Finance Utility Suite
Enterprise Dashboard Page

Professional dashboard assembled from reusable widgets.

Author : Shiva Kumar
Version : 2.1.0
"""

from __future__ import annotations

import customtkinter as ctk

from core.dashboard_service import DashboardService
from core.report_service import ReportService

from tkinter import filedialog, messagebox
import os
import subprocess
import sys

from desktop.widgets.dashboard.dashboard_header import DashboardHeader
from desktop.widgets.dashboard.executive_cards import ExecutiveCards
from desktop.widgets.dashboard.latest_snapshot_panel import LatestSnapshotPanel
from desktop.widgets.dashboard.risk_summary_panel import RiskSummaryPanel
from desktop.widgets.dashboard.dashboard_footer import DashboardFooter

from desktop.widgets.risk_table import RiskTable
from desktop.widgets.risk_alert_panel import RiskAlertPanel


class DashboardPage(ctk.CTkFrame):

    """
    Enterprise Risk Dashboard.
    """

    def __init__(self, master):

        super().__init__(master)

        self.service = DashboardService()

        self.report_service = ReportService()

        self.data = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build()

        self.load_dashboard()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------

    def _build(self):

        # =====================================================
        # Header
        # =====================================================

        self.header = DashboardHeader(self)

        self.header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=24,
            pady=(18, 10),
        )

        self.header.set_refresh_callback(
            self.load_dashboard,
        )

        self.header.set_report_callback(
            self.generate_report,
        )

        # =====================================================
        # Scrollable Area
        # =====================================================

        self.body = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )

        self.body.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=16,
            pady=(0, 12),
        )

        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=1)

        # =====================================================
        # Executive Cards
        # =====================================================

        self.cards = ExecutiveCards(self.body)

        self.cards.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=4,
            pady=(6, 12),
        )

        # =====================================================
        # Executive Panels
        # =====================================================

        self.snapshot_panel = LatestSnapshotPanel(self.body)

        self.snapshot_panel.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(4, 6),
            pady=(2, 10),
        )

        self.summary_panel = RiskSummaryPanel(self.body)

        self.summary_panel.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(6, 4),
            pady=(2, 10),
        )

        # =====================================================
        # Risk Tables
        # =====================================================

        self.client_table = RiskTable(
            self.body,
            "Top Risky Clients",
        )

        self.client_table.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=(4, 6),
            pady=8,
        )

        self.symbol_table = RiskTable(
            self.body,
            "Top Risky Symbols",
        )

        self.symbol_table.grid(
            row=2,
            column=1,
            sticky="nsew",
            padx=(6, 4),
            pady=8,
        )

        # =====================================================
        # Alert Panel
        # =====================================================

        self.alert_panel = RiskAlertPanel(
            self.body,
        )

        self.alert_panel.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=4,
            pady=8,
        )

        # =====================================================
        # Footer
        # =====================================================

        self.footer = DashboardFooter(
            self.body,
        )

        self.footer.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=4,
            pady=(8, 16),
        )

        # =====================================================
        # Empty State
        # =====================================================

        self.empty_label = ctk.CTkLabel(
            self.body,
            text="",
            font=("Segoe UI", 12),
        )

        self.empty_label.grid(
            row=5,
            column=0,
            columnspan=2,
            pady=(0, 10),
        )

        self.body.grid_rowconfigure(
            2,
            weight=1,
        )

            # ---------------------------------------------------------
    # Dashboard
    # ---------------------------------------------------------

    def load_dashboard(self):
        """
        Load enterprise dashboard.
        """
        from core.state.application_state import ApplicationState

        print("=" * 60)
        print("DASHBOARD")
        print("Has Portfolio :", ApplicationState.has_master_portfolio())
        master = ApplicationState.get_master_portfolio()
        print("Rows :", 0 if master is None else len(master))
        print("=" * 60)

        self.data = self.service.get_dashboard_data()

        if not self.data.available or self.data.summary is None:

            self._empty(self.data.message)

            return

        self._populate(
            self.data.summary,
            self.data.snapshot,
        )

    # ---------------------------------------------------------

    def _populate(self, summary, snapshot):

        # -----------------------------------------------------
        # Header
        # -----------------------------------------------------

        self.header.set_status(
            f"Risk Engine : {summary.engine_status}",
          "#22C55E",
        )

        # -----------------------------------------------------
        # Executive Cards
        # -----------------------------------------------------

        self.cards.load(
            risk_score=summary.display_score,
            health=summary.health,
            exposure=self._money(summary.total_exposure),
            mtm=self._money(summary.total_mtm),
            margin=summary.margin_utilization_percent,
            diversification=summary.diversification_score,
        )

        # -----------------------------------------------------
        # Latest Snapshot
        # -----------------------------------------------------

        # NOTE:
        # Once DashboardService exposes SnapshotMetadata,
        # replace this with:
        #
        # self.snapshot_panel.load(summary.snapshot)
        #
        # For now we clear it.

        self.snapshot_panel.load(snapshot)

        # -----------------------------------------------------
        # Risk Summary
        # -----------------------------------------------------

        self.summary_panel.load(
            risk_score=summary.display_score,
            health=summary.health,
            margin_utilization=summary.margin_utilization_percent,
            diversification=summary.diversification_score,
            top_client=summary.top_client_concentration_percent,
            top_symbol=summary.top_symbol_concentration_percent,
        )

        # -----------------------------------------------------
        # Tables
        # -----------------------------------------------------

        self.client_table.load_items(
            summary.top_clients,
        )

        self.symbol_table.load_items(
            summary.top_symbols,
        )

        # -----------------------------------------------------
        # Alerts
        # -----------------------------------------------------

        self.alert_panel.load_alerts(
            summary.alerts,
        )

        # -----------------------------------------------------
        # Footer
        # -----------------------------------------------------

        self.footer.load(
            snapshot=summary.snapshot_id or "Current",
            refresh=self._time(summary.last_refresh),
            portfolio=f"{summary.clients} Clients",
            engine=summary.engine_status,
        )

        self.empty_label.configure(text="")

    # ---------------------------------------------------------

    def _empty(
        self,
        message: str,
    ):

        self.cards.clear()

        self.snapshot_panel.clear()

        self.summary_panel.clear()

        self.client_table.load_items([])

        self.symbol_table.load_items([])

        self.alert_panel.load_alerts([])

        self.footer.clear()

        self.header.set_status(
            "Risk Engine : Waiting",
            "#3B82F6",
        )

        self.empty_label.configure(
            text=message,
        )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _money(value):

        value = float(value)

        sign = "-" if value < 0 else ""

        value = abs(value)

        if value >= 1e7:
            return f"{sign}₹{value/1e7:.2f} Cr"

        if value >= 1e5:
            return f"{sign}₹{value/1e5:.2f} L"

        return f"{sign}₹{value:,.2f}"

    @staticmethod
    def _time(value):

        if not value:
            return "--"

        try:

            from datetime import datetime

            return datetime.fromisoformat(
                str(value)
            ).strftime("%d-%b-%Y %I:%M %p")

        except Exception:

            return str(value)

    def generate_report(self):

        if self.data is None or not self.data.available:
            messagebox.showwarning(
                "Executive Report",
                "No dashboard data available.",
                parent=self,
            )
            return

        filename = filedialog.asksaveasfilename(
            parent=self,
            title="Save Executive Report",
            defaultextension=".pdf",
            initialfile="Executive_Risk_Report.pdf",
            filetypes=[
                ("PDF Files", "*.pdf"),
            ],
        )

        if not filename:
            return

        try:

            pdf = self.report_service.generate_executive_report(
                self.data,
                filename,
            )

            messagebox.showinfo(
                "Executive Report",
                f"Report generated successfully.\n\n{pdf}",
                parent=self,
            )

            try:

                if sys.platform.startswith("win"):
                    os.startfile(pdf)

                elif sys.platform == "darwin":
                    subprocess.call(["open", pdf])

                else:
                    subprocess.call(["xdg-open", pdf])

            except Exception:
                pass

        except Exception as exc:

            messagebox.showerror(
                "Executive Report",
                str(exc),
                parent=self,
            )    