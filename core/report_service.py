"""
Finance Utility Suite
Enterprise Report Service

Professional PDF report generator for
Risk Management System (RMS).

Author : Shiva Kumar
Version : 1.0.0
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from core.dashboard_service import DashboardData


class ReportService:
    """
    Enterprise PDF Report Generator
    """

    def __init__(self):

        self.styles = getSampleStyleSheet()

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def generate_executive_report(
        self,
        data: DashboardData,
        output_path: str | Path,
    ) -> Path:

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        document = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
        )

        story = []

        self._add_cover_page(story, data)

        self._add_executive_summary(story, data)

        self._add_portfolio_summary(story, data)

        self._add_top_clients(story, data)

        self._add_top_symbols(story, data)

        self._add_alerts(story, data)

        self._add_footer(story)

        document.build(story)

        return output_path

    # ---------------------------------------------------------
    # Cover Page
    # ---------------------------------------------------------

    def _add_cover_page(
        self,
        story,
        data: DashboardData,
    ):

        story.append(
            Paragraph(
                "Risk Management System",
                self.styles["Title"],
            )
        )

        story.append(
            Paragraph(
                "Enterprise Executive Report",
                self.styles["Heading2"],
            )
        )

        story.append(Spacer(1, 20))

        story.append(
            Paragraph(
                f"Generated : {datetime.now():%d-%b-%Y %I:%M %p}",
                self.styles["Normal"],
            )
        )

        if data.snapshot:

            story.append(
                Paragraph(
                    f"Business Date : {data.snapshot.business_date}",
                    self.styles["Normal"],
                )
            )

            story.append(
                Paragraph(
                    f"Snapshot ID : {data.snapshot.snapshot_id}",
                    self.styles["Normal"],
                )
            )

        if data.summary:

            story.append(
                Paragraph(
                    f"Risk Score : {data.summary.display_score}",
                    self.styles["Normal"],
                )
            )

            story.append(
                Paragraph(
                    f"Health : {data.summary.health}",
                    self.styles["Normal"],
                )
            )

        story.append(Spacer(1, 30))

    # ---------------------------------------------------------
    # Executive Summary
    # ---------------------------------------------------------

    def _add_executive_summary(
        self,
        story,
        data: DashboardData,
    ):

        summary = data.summary

        if summary is None:
            return

        story.append(
            Paragraph(
                "Executive Summary",
                self.styles["Heading1"],
            )
        )

        table_data = [
            ["Metric", "Value"],
            ["Risk Score", f"{summary.display_score}"],
            ["Health", summary.health],
            ["Total Exposure", self._money(summary.total_exposure)],
            ["Total MTM", self._money(summary.total_mtm)],
            [
                "Margin Utilization",
                f"{summary.margin_utilization_percent:.2f}%",
            ],
            [
                "Diversification",
                f"{summary.diversification_score:.2f}%",
            ],
        ]

        table = Table(
            table_data,
            colWidths=[180, 220],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#1F4E78"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.whitesmoke,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, 0),
                        8,
                    ),
                    (
                        "TOPPADDING",
                        (0, 1),
                        (-1, -1),
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 1),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(table)

        story.append(
            Spacer(
                1,
                18,
            )
        )

        # ---------------------------------------------------------
    # Portfolio Summary
    # ---------------------------------------------------------

    def _add_portfolio_summary(
        self,
        story,
        data: DashboardData,
    ):

        summary = data.summary
        snapshot = data.snapshot

        if summary is None or snapshot is None:
            return

        story.append(
            Paragraph(
                "Portfolio Summary",
                self.styles["Heading1"],
            )
        )

        table_data = [
            ["Item", "Value"],
            ["Clients", f"{summary.clients:,}"],
            ["Symbols", f"{summary.symbols:,}"],
            ["Records", f"{snapshot.records:,}"],
            ["Portfolio Value", self._money(snapshot.portfolio_value)],
            ["Total Exposure", self._money(summary.total_exposure)],
            ["Total MTM", self._money(summary.total_mtm)],
            ["Business Date", snapshot.business_date],
            ["Snapshot ID", snapshot.snapshot_id],
        ]

        table = Table(
            table_data,
            colWidths=[180, 220],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#1F4E78"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.beige,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, 0),
                        8,
                    ),
                    (
                        "TOPPADDING",
                        (0, 1),
                        (-1, -1),
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 1),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(table)

        story.append(
            Spacer(
                1,
                18,
            )
        )

    # ---------------------------------------------------------
    # Top Risk Clients
    # ---------------------------------------------------------

    def _add_top_clients(
        self,
        story,
        data: DashboardData,
    ):

        summary = data.summary

        if summary is None:
            return

        story.append(
            Paragraph(
                "Top Risk Clients",
                self.styles["Heading1"],
            )
        )

        table_data = [
            [
                "Client",
                "Exposure",
                "MTM",
                "Risk",
            ]
        ]

        for client in summary.top_clients[:10]:

            table_data.append(
                [
                    client.name,
                    self._money(client.exposure),
                    self._money(client.mtm),
                    client.level,
                ]
            )

        table = Table(
            table_data,
            colWidths=[180, 90, 90, 80],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#1F4E78"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.whitesmoke,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                ]
            )
        )

        story.append(table)

        story.append(Spacer(1, 18))

    # ---------------------------------------------------------
    # Top Risk Symbols
    # ---------------------------------------------------------

    def _add_top_symbols(
        self,
        story,
        data: DashboardData,
    ):

        summary = data.summary

        if summary is None:
            return

        story.append(
            Paragraph(
                "Top Risk Symbols",
                self.styles["Heading1"],
            )
        )

        table_data = [
            [
                "Symbol",
                "Exposure",
                "MTM",
                "Risk",
            ]
        ]

        for symbol in summary.top_symbols[:10]:

            table_data.append(
            [
                symbol.name,
                self._money(symbol.exposure),
                self._money(symbol.mtm),
                symbol.level,
            ]
        )

        table = Table(
            table_data,
            colWidths=[180, 90, 90, 80],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#1F4E78"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.whitesmoke,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                ]
            )
        )

        story.append(table)

        story.append(
            Spacer(
                1,
                18,
            )
        )

        # ---------------------------------------------------------
    # Risk Alerts
    # ---------------------------------------------------------

    def _add_alerts(
        self,
        story,
        data: DashboardData,
    ):

        summary = data.summary

        if summary is None:
            return

        story.append(
            Paragraph(
                "Risk Alerts",
                self.styles["Heading1"],
            )
        )

        if not summary.alerts:

            story.append(
                Paragraph(
                    "No active alerts.",
                    self.styles["Normal"],
                )
            )

            story.append(Spacer(1, 18))

            return

        table_data = [
            [
                "Severity",
                "Message",
            ]
        ]

        for alert in summary.alerts:

            severity = getattr(alert, "level", "Info")
            message = getattr(alert, "message", str(alert))

            table_data.append(
                [
                    severity,
                    message,
                ]
            )

        table = Table(
            table_data,
            colWidths=[90, 330],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#C62828"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.whitesmoke,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, 0),
                        8,
                    ),
                ]
            )
        )

        story.append(table)

        story.append(
            Spacer(
                1,
                20,
            )
        )

    # ---------------------------------------------------------
    # Footer
    # ---------------------------------------------------------

    def _add_footer(
        self,
        story,
    ):

        story.append(
            Spacer(
                1,
                30,
            )
        )

        story.append(
            Paragraph(
                "<b>Finance Utility Suite</b>",
                self.styles["Heading2"],
            )
        )

        story.append(
            Paragraph(
                "Risk Management System (RMS) Desktop v1.0",
                self.styles["Normal"],
            )
        )

        story.append(
            Paragraph(
                f"Generated on {datetime.now():%d-%b-%Y %I:%M %p}",
                self.styles["Normal"],
            )
        )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _money(value: float) -> str:

        value = float(value or 0.0)

        sign = "-" if value < 0 else ""

        value = abs(value)

        if value >= 1e7:
            return f"{sign}₹{value / 1e7:.2f} Cr"

        if value >= 1e5:
            return f"{sign}₹{value / 1e5:.2f} L"

        if value >= 1e3:
            return f"{sign}₹{value / 1e3:.2f} K"

        return f"{sign}₹{value:,.2f}"

    @staticmethod
    def _date(value: str) -> str:

        if not value:
            return "--"

        try:

            return datetime.fromisoformat(
                str(value)
            ).strftime(
                "%d-%b-%Y"
            )

        except Exception:

            return str(value)

    @staticmethod
    def _datetime(value: str) -> str:

        if not value:
            return "--"

        try:

            return datetime.fromisoformat(
                str(value)
            ).strftime(
                "%d-%b-%Y %I:%M %p"
            )

        except Exception:

            return str(value)    
