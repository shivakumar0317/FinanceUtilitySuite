"""Finance Utility Suite - Base Dashboard Report v1.37.2."""
from __future__ import annotations
from abc import ABC
from collections.abc import Sequence
from datetime import datetime
from typing import Any
import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet
from desktop.reports.report_engine import ExcelReportEngine
from desktop.reports.report_utils import write_kpi_cards, write_report_title, write_section_header

class BaseDashboardReport(ExcelReportEngine, ABC):
    VERSION = "1.37.2"
    def __init__(self, *, report_title: str, report_subject: str, report_description: str, report_keywords: str = "", creator: str | None = None) -> None:
        super().__init__(report_title=report_title, report_subject=report_subject, report_description=report_description, report_keywords=report_keywords, creator=creator)
    def add_report_header(self, worksheet: Worksheet, title: str, subtitle: str | None = None, *, start_row: int = 1, start_column: int = 1, end_column: int = 8) -> int:
        return write_report_title(worksheet, title=title, subtitle=subtitle, export_time=self.export_time, start_row=start_row, start_column=start_column, end_column=end_column)
    def add_section(self, worksheet: Worksheet, row: int, title: str, *, start_column: int = 1, end_column: int = 8) -> int:
        return write_section_header(worksheet, row=row, title=title, start_column=start_column, end_column=end_column)
    def add_kpis(self, worksheet: Worksheet, metrics: Sequence[tuple[str, Any]], start_row: int, *, start_column: int = 1, cards_per_row: int = 4, card_width: int = 2, number_formats: dict[str, str] | None = None) -> int:
        return write_kpi_cards(worksheet, metrics=metrics, start_row=start_row, start_column=start_column, cards_per_row=cards_per_row, card_width=card_width, number_formats=number_formats)
    def build(self, writer: pd.ExcelWriter, export_time: datetime) -> None:
        raise NotImplementedError("Subclasses must implement build().")
