"""Excel chart builders used by Finance Utility Suite reports."""

from __future__ import annotations

from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.worksheet.worksheet import Worksheet


def add_exposure_pie_chart(
    worksheet: Worksheet,
    data_sheet: Worksheet,
    start_row: int,
    end_row: int,
    anchor: str = "H4",
) -> None:
    """Add an exposure allocation pie chart from a helper range."""

    if end_row < start_row:
        return

    chart = PieChart()
    chart.title = "Exposure Allocation"
    chart.height = 8.2
    chart.width = 12.5
    chart.style = 10

    labels = Reference(data_sheet, min_col=1, min_row=start_row, max_row=end_row)
    values = Reference(data_sheet, min_col=2, min_row=start_row - 1, max_row=end_row)
    chart.add_data(values, titles_from_data=True)
    chart.set_categories(labels)
    chart.dataLabels = DataLabelList()
    chart.dataLabels.showPercent = True
    chart.legend.position = "r"
    worksheet.add_chart(chart, anchor)


def add_top_holdings_bar_chart(
    worksheet: Worksheet,
    data_sheet: Worksheet,
    start_row: int,
    end_row: int,
    anchor: str = "H20",
) -> None:
    """Add a horizontal bar chart for top holdings by exposure."""

    if end_row < start_row:
        return

    chart = BarChart()
    chart.type = "bar"
    chart.style = 10
    chart.title = "Top Holdings by Exposure"
    chart.y_axis.title = "Symbol"
    chart.x_axis.title = "Exposure"
    chart.height = 8.2
    chart.width = 12.5
    chart.legend = None

    labels = Reference(data_sheet, min_col=1, min_row=start_row, max_row=end_row)
    values = Reference(data_sheet, min_col=2, min_row=start_row - 1, max_row=end_row)
    chart.add_data(values, titles_from_data=True)
    chart.set_categories(labels)
    chart.dataLabels = DataLabelList()
    chart.dataLabels.showVal = True
    worksheet.add_chart(chart, anchor)
