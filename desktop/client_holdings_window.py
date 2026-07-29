"""
Finance Utility Suite
Client Holdings Drill-down Window

Author  : Shiva Kumar
Version : 1.36.0
"""

from __future__ import annotations

from typing import Any

import customtkinter as ctk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import filedialog, messagebox, ttk

from desktop.reports.client_holdings_report import ClientHoldingsReport
from desktop.theme import Theme
from desktop.widgets.scrollable_frame import ScrollableFrame
from desktop.windows.stock_details import StockDetailsWindow


class ClientHoldingsWindow(ctk.CTkToplevel):
    """Display one client's concentration summary and symbol holdings."""

    RISK_COLORS = {
        "Critical": "#DC2626",
        "High": "#EA580C",
        "Medium": "#CA8A04",
        "Low": "#16A34A",
    }

    COLUMNS = [
        "Symbol",
        "BUY VALUE",
        "NetValue",
        "Exposure",
        "MarkToMarket",
        "MTF VAR",
        "MTF MARGIN",
        "Holding %",
    ]

    def __init__(
        self,
        master,
        account_id: str,
        summary_data: dict[str, Any],
        holdings_df: pd.DataFrame,
    ) -> None:
        super().__init__(master)

        self.account_id = str(account_id).strip()
        self.summary_data = dict(summary_data or {})
        self.holdings_df = self._prepare_dataframe(holdings_df)
        self.filtered_df = self.holdings_df.copy()
        self.search_var = ctk.StringVar()
        self.sort_column = None
        self.sort_reverse = False
        self.stock_window = None

        self.title(f"Client Holdings - {self.account_id}")
        self.geometry("1280x900")
        self.minsize(1050, 700)
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind("<Escape>", lambda _event: self.destroy())
        self.bind("<Control-e>", lambda _event: self.export_to_excel())

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()

        self.body = ScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.body.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(10, 4),
            pady=(0, 10),
        )
        self.body.grid_columnconfigure(0, weight=1)

        self._build_kpis()
        self._build_content()
        self._build_footer()
        self._load_table()
        self._draw_charts()

        self.after(100, self._center_window)
        self.after(150, self._focus_window)

    def _build_header(self) -> None:
        header = ctk.CTkFrame(
            self,
            corner_radius=Theme.BORDER_RADIUS,
            border_width=1,
        )
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=f"Client Holdings — {self.account_id}",
            font=("Segoe UI", 22, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            header,
            text="Concentration exposure and symbol-level risk details",
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_SECONDARY,
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 14))

        risk = str(self.summary_data.get("Risk Level", "Unknown"))
        ctk.CTkLabel(
            header,
            text=f"  {risk} Risk  ",
            fg_color=self.RISK_COLORS.get(risk, "#64748B"),
            text_color="#FFFFFF",
            corner_radius=10,
            height=32,
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=1, rowspan=2, padx=18, pady=14)

    def _build_kpis(self) -> None:
        """Build the two-row client KPI dashboard."""

        frame = ctk.CTkFrame(self.body, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="ew", padx=6, pady=(4, 8))

        for column in range(5):
            frame.grid_columnconfigure(column, weight=1)

        holding_count = len(self.holdings_df)
        total_exposure = float(self.holdings_df["Exposure"].sum())
        total_mtm = float(self.holdings_df["MarkToMarket"].sum())
        total_margin = float(self.holdings_df["MTF MARGIN"].sum())

        weights = pd.to_numeric(
            self.holdings_df["Holding %"],
            errors="coerce",
        ).fillna(0.0)

        if weights.sum() <= 0 and total_exposure > 0:
            weights = (
                self.holdings_df["Exposure"]
                .clip(lower=0)
                .div(total_exposure)
                .mul(100)
            )

        largest_holding = float(weights.max()) if not weights.empty else 0.0
        average_holding = float(weights.mean()) if not weights.empty else 0.0
        top_three = float(weights.nlargest(3).sum()) if not weights.empty else 0.0
        average_exposure = (
            total_exposure / holding_count if holding_count else 0.0
        )

        diversification_score = self._calculate_diversification_score(weights)
        concentration_score = max(0.0, min(100.0, 100.0 - diversification_score))

        kpis = [
            (
                "Holdings",
                self._format_integer(
                    self.summary_data.get("Holdings", holding_count)
                ),
                None,
            ),
            (
                "Total Exposure",
                self._format_currency(
                    self.summary_data.get("Total Exposure", total_exposure)
                ),
                None,
            ),
            (
                "Mark to Market",
                self._format_currency(
                    self.summary_data.get("MarkToMarket", total_mtm)
                ),
                "#16A34A" if total_mtm >= 0 else "#DC2626",
            ),
            (
                "MTF Margin",
                self._format_currency(
                    self.summary_data.get("MTF MARGIN", total_margin)
                ),
                None,
            ),
            (
                "Largest Holding",
                self._format_percent(
                    self.summary_data.get(
                        "Largest Holding %",
                        largest_holding,
                    )
                ),
                self._risk_color_for_percent(largest_holding),
            ),
            (
                "Diversification Score",
                f"{diversification_score:.1f}/100",
                self._score_color(diversification_score, higher_is_better=True),
            ),
            (
                "Average Holding",
                self._format_percent(average_holding),
                None,
            ),
            (
                "Top 3 Holdings",
                self._format_percent(top_three),
                self._risk_color_for_percent(top_three),
            ),
            (
                "Concentration Score",
                f"{concentration_score:.1f}/100",
                self._score_color(concentration_score, higher_is_better=False),
            ),
            (
                "Average Exposure",
                self._format_currency(average_exposure),
                None,
            ),
        ]

        for index, (label, value, value_color) in enumerate(kpis):
            row = index // 5
            column = index % 5

            card = ctk.CTkFrame(
                frame,
                corner_radius=Theme.BORDER_RADIUS,
                border_width=1,
            )
            card.grid(
                row=row,
                column=column,
                sticky="nsew",
                padx=5,
                pady=5,
            )

            ctk.CTkLabel(
                card,
                text=label,
                font=Theme.FONT_SMALL,
                text_color=Theme.TEXT_SECONDARY,
            ).pack(anchor="w", padx=14, pady=(12, 3))

            ctk.CTkLabel(
                card,
                text=value,
                font=("Segoe UI", 17, "bold"),
                text_color=value_color,
            ).pack(anchor="w", padx=14, pady=(0, 12))

    @staticmethod
    def _calculate_diversification_score(weights: pd.Series) -> float:
        """Return a normalized diversification score from 0 to 100."""

        clean_weights = pd.to_numeric(
            weights,
            errors="coerce",
        ).fillna(0.0)
        clean_weights = clean_weights[clean_weights > 0]

        count = len(clean_weights)

        if count == 0:
            return 0.0

        if count == 1:
            return 0.0

        normalized = clean_weights / clean_weights.sum()
        hhi = float((normalized ** 2).sum())

        minimum_hhi = 1.0 / count
        denominator = 1.0 - minimum_hhi

        if denominator <= 0:
            return 0.0

        score = ((1.0 - hhi) / denominator) * 100.0
        return max(0.0, min(100.0, score))

    @staticmethod
    def _score_color(score: float, higher_is_better: bool) -> str:
        """Return a dashboard color for a score."""

        effective_score = score if higher_is_better else 100.0 - score

        if effective_score >= 75:
            return "#16A34A"
        if effective_score >= 50:
            return "#CA8A04"
        if effective_score >= 25:
            return "#EA580C"
        return "#DC2626"

    @staticmethod
    def _risk_color_for_percent(value: float) -> str:
        """Return a risk color for concentration percentages."""

        if value >= 75:
            return "#DC2626"
        if value >= 50:
            return "#EA580C"
        if value >= 25:
            return "#CA8A04"
        return "#16A34A"

    def _build_content(self) -> None:
        content = ctk.CTkFrame(self.body, fg_color="transparent")
        content.grid(row=1, column=0, sticky="ew", padx=6, pady=8)
        content.grid_columnconfigure((0, 1), weight=1, uniform="charts")

        self.pie_panel = self._panel(
            content,
            "Exposure Allocation",
            height=330,
        )
        self.pie_panel.grid(
            row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 8)
        )

        self.bar_panel = self._panel(
            content,
            "Exposure by Stock",
            height=330,
        )
        self.bar_panel.grid(
            row=0, column=1, sticky="nsew", padx=(6, 0), pady=(0, 8)
        )

        table_panel = self._panel(
            content,
            "Symbol-level Holdings",
            height=470,
        )
        table_panel.grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )
        table_panel.grid_rowconfigure(2, weight=1)
        table_panel.grid_columnconfigure(0, weight=1)

        search_frame = ctk.CTkFrame(
            table_panel,
            fg_color="transparent",
        )
        search_frame.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=12,
            pady=(2, 6),
        )
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            search_frame,
            text="Search Symbol",
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_SECONDARY,
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 8),
        )

        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Type a stock symbol...",
            height=32,
        )
        self.search_entry.grid(
            row=0,
            column=1,
            sticky="ew",
        )
        self.search_entry.bind(
            "<KeyRelease>",
            self._on_search,
        )

        ctk.CTkButton(
            search_frame,
            text="Clear",
            width=80,
            height=32,
            command=self._clear_search,
        ).grid(
            row=0,
            column=2,
            padx=(8, 0),
        )

        self._build_table(table_panel)

    def _panel(
        self,
        master,
        title: str,
        height: int | None = None,
    ) -> ctk.CTkFrame:
        panel = ctk.CTkFrame(
            master,
            corner_radius=Theme.BORDER_RADIUS,
            border_width=1,
            height=height or 0,
        )
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        if height:
            panel.grid_propagate(False)

        ctk.CTkLabel(
            panel,
            text=title,
            font=("Segoe UI", 13, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 6))

        return panel

    def _build_table(self, master) -> None:
        style = ttk.Style()
        style.configure(
            "ClientHoldings.Treeview",
            rowheight=getattr(Theme, "TREE_ROW_HEIGHT", 28),
            font=getattr(Theme, "FONT_NORMAL", ("Segoe UI", 10)),
        )
        style.configure(
            "ClientHoldings.Treeview.Heading",
            font=getattr(Theme, "FONT_SMALL", ("Segoe UI", 10, "bold")),
        )

        self.tree = ttk.Treeview(
            master,
            show="headings",
            selectmode="browse",
            style="ClientHoldings.Treeview",
            height=14,
        )
        self.tree.tag_configure("evenrow", background="#FFFFFF")
        self.tree.tag_configure("oddrow", background="#F7F7F7")
        self.tree.bind("<Double-1>", self._open_stock_details)

        y_scroll = ttk.Scrollbar(
            master, orient="vertical", command=self.tree.yview
        )
        x_scroll = ttk.Scrollbar(
            master, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
        )

        self.tree.grid(
            row=2, column=0, sticky="nsew", padx=(12, 0), pady=(4, 0)
        )
        y_scroll.grid(
            row=2, column=1, sticky="ns", padx=(0, 12), pady=(4, 0)
        )
        x_scroll.grid(
            row=3, column=0, sticky="ew", padx=(12, 0), pady=(0, 10)
        )

    def _build_footer(self) -> None:
        footer = ctk.CTkFrame(
            self.body,
            corner_radius=Theme.BORDER_RADIUS,
            border_width=1,
        )
        footer.grid(row=2, column=0, sticky="ew", padx=6, pady=(8, 12))
        footer.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            footer,
            text=self._status_text(),
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_SECONDARY,
            anchor="w",
        )
        self.status_label.grid(row=0, column=0, sticky="w", padx=14, pady=10)

        ctk.CTkButton(
            footer,
            text="Export to Excel",
            width=140,
            command=self.export_to_excel,
        ).grid(row=0, column=1, padx=6, pady=8)

        ctk.CTkButton(
            footer,
            text="Close",
            width=100,
            fg_color="#64748B",
            hover_color="#475569",
            command=self.destroy,
        ).grid(row=0, column=2, padx=(6, 14), pady=8)

    def _prepare_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if dataframe is None:
            dataframe = pd.DataFrame()

        dataframe = dataframe.copy()

        for column in self.COLUMNS:
            if column not in dataframe.columns:
                dataframe[column] = "" if column == "Symbol" else 0.0

        for column in self.COLUMNS[1:]:
            dataframe[column] = pd.to_numeric(
                dataframe[column], errors="coerce"
            ).fillna(0.0)

        dataframe["Symbol"] = (
            dataframe["Symbol"].fillna("").astype(str).str.strip().str.upper()
        )

        return (
            dataframe[self.COLUMNS]
            .sort_values("Exposure", ascending=False)
            .reset_index(drop=True)
        )

    def _load_table(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = self.COLUMNS

        for column in self.COLUMNS:
            self.tree.heading(
                column,
                text=column,
                command=lambda c=column: self._sort_by_column(c),
            )
            self.tree.column(
                column,
                width=150 if column == "Symbol" else 130,
                minwidth=90,
                anchor="center" if column == "Symbol" else "e",
                stretch=True,
            )

        for index, row in self.filtered_df.iterrows():
            values = [
                row["Symbol"],
                self._format_number(row["BUY VALUE"]),
                self._format_number(row["NetValue"]),
                self._format_number(row["Exposure"]),
                self._format_number(row["MarkToMarket"]),
                self._format_number(row["MTF VAR"]),
                self._format_number(row["MTF MARGIN"]),
                self._format_percent(row["Holding %"]),
            ]
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=values, tags=(tag,))

    def _draw_charts(self) -> None:
        chart_data = self.holdings_df[self.holdings_df["Exposure"] > 0].copy()
        self._draw_pie_chart(chart_data)
        self._draw_bar_chart(chart_data)

    def _draw_pie_chart(self, dataframe: pd.DataFrame) -> None:
        figure = Figure(figsize=(5.2, 2.6), dpi=100)
        axis = figure.add_subplot(111)

        if dataframe.empty:
            axis.text(0.5, 0.5, "No exposure data", ha="center", va="center")
            axis.axis("off")
        else:
            top = dataframe.head(10)
            labels = top["Symbol"].tolist()
            values = top["Exposure"].tolist()
            remaining = float(dataframe.iloc[10:]["Exposure"].sum())
            if remaining>0:
                labels.append("Others")
                values.append(remaining)

            explode=[0.08]+[0]*(len(values)-1)
            wedges,_,_=axis.pie(
                values,
                labels=None,
                explode=explode,
                autopct="%1.1f%%",
                startangle=90,
                pctdistance=0.75,
                textprops={"fontsize":8},
            )
            axis.legend(wedges,labels,loc="center left",
                        bbox_to_anchor=(1.02,0.5),
                        fontsize=8,frameon=False)
            axis.axis("equal")

        if hasattr(self,"pie_canvas"):
            self.pie_canvas.get_tk_widget().destroy()
        figure.tight_layout()
        canvas = FigureCanvasTkAgg(figure, master=self.pie_panel)
        canvas.draw()
        canvas.get_tk_widget().grid(
            row=1, column=0, sticky="nsew", padx=8, pady=(0, 8)
        )
        self.pie_canvas = canvas

    def _draw_bar_chart(self, dataframe: pd.DataFrame) -> None:
        figure = Figure(figsize=(5.2, 2.6), dpi=100)
        axis = figure.add_subplot(111)

        chart_data = dataframe.head(10).sort_values("Exposure")

        if chart_data.empty:
            axis.text(0.5, 0.5, "No exposure data", ha="center", va="center")
            axis.axis("off")
        else:
            bars=axis.barh(chart_data["Symbol"], chart_data["Exposure"])
            avg=float(chart_data["Exposure"].mean())
            axis.axvline(avg,linestyle="--",linewidth=1)
            axis.bar_label(bars,fmt="%.0f",padding=3,fontsize=7)
            axis.set_xlabel("Exposure")
            axis.tick_params(axis="both", labelsize=8)
            axis.grid(axis="x", alpha=0.25)

        if hasattr(self,"bar_canvas"):
            self.bar_canvas.get_tk_widget().destroy()
        figure.tight_layout()
        canvas = FigureCanvasTkAgg(figure, master=self.bar_panel)
        canvas.draw()
        canvas.get_tk_widget().grid(
            row=1, column=0, sticky="nsew", padx=8, pady=(0, 8)
        )
        self.bar_canvas = canvas

    def _on_search(self, _event=None) -> None:
        """Filter holdings by symbol as the user types."""

        query = self.search_var.get().strip()

        if not query:
            self.filtered_df = self.holdings_df.copy()
        else:
            symbol_values = (
                self.holdings_df["Symbol"]
                .fillna("")
                .astype(str)
            )

            mask = symbol_values.str.contains(
                query,
                case=False,
                na=False,
                regex=False,
            )
            self.filtered_df = self.holdings_df.loc[mask].copy()

        self._load_table()
        self._update_status_label()

    def _clear_search(self) -> None:
        """Clear the search and restore all holdings."""

        self.search_var.set("")
        self.filtered_df = self.holdings_df.copy()
        self._load_table()
        self._update_status_label()
        self.search_entry.focus_set()

    def _update_status_label(self) -> None:
        visible = len(self.filtered_df)
        total = len(self.holdings_df)

        if visible == total:
            count_text = f"Stocks: {total}"
        else:
            count_text = f"Filtered: {visible} of {total} stocks"

        self.status_label.configure(
            text=(
                f"{count_text}"
                f"  |  Total Exposure: "
                f"{self._format_currency(self.filtered_df['Exposure'].sum())}"
                "  |  Ctrl+E: Export  |  Esc: Close"
            )
        )


    def _sort_by_column(self, column: str) -> None:
        """Sort table by selected column."""

        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        if column == "Symbol":
            self.filtered_df = self.filtered_df.sort_values(
                by=column,
                ascending=not self.sort_reverse,
                key=lambda s: s.astype(str).str.upper(),
            )
        else:
            self.filtered_df = self.filtered_df.sort_values(
                by=column,
                ascending=not self.sort_reverse,
            )

        self.filtered_df = self.filtered_df.reset_index(drop=True)
        self._load_table()
        self._update_status_label()


    def _open_stock_details(self, _event=None) -> None:
        selection=self.tree.selection()
        if not selection:
            return
        item=self.tree.item(selection[0],"values")
        if not item:
            return

        data=dict(zip(self.COLUMNS, item))

        try:
            if self.stock_window is not None and self.stock_window.winfo_exists():
                self.stock_window.destroy()
        except Exception:
            pass

        self.stock_window=StockDetailsWindow(self, data)

    def export_to_excel(self) -> None:
        """Export the client holdings workbook through the report engine."""

        if self.holdings_df.empty:
            messagebox.showwarning(
                "No Data",
                "There are no client holdings to export.",
                parent=self,
            )
            return

        filepath = filedialog.asksaveasfilename(
            parent=self,
            title="Export Client Holdings",
            defaultextension=".xlsx",
            initialfile=f"Client_Holdings_{self.account_id}.xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
        )

        if not filepath:
            return

        try:
            report = ClientHoldingsReport(
                account_id=self.account_id,
                holdings_df=self.holdings_df,
                summary_data=self.summary_data,
            )
            output_path = report.export(filepath)
            self.status_label.configure(text=f"Exported: {output_path.name}")
            messagebox.showinfo(
                "Export Complete",
                "Professional client holdings report exported successfully.",
                parent=self,
            )
        except Exception as exc:
            messagebox.showerror(
                "Export Failed",
                f"Unable to export the workbook.\n\n{exc}",
                parent=self,
            )

    def _focus_window(self) -> None:
        """Bring the window forward without forcing dialog behaviour."""

        try:
            self.lift()
            self.focus_set()
        except Exception:
            pass

    def _center_window(self) -> None:
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()

        try:
            x = self.master.winfo_rootx() + max(
                (self.master.winfo_width() - width) // 2, 0
            )
            y = self.master.winfo_rooty() + max(
                (self.master.winfo_height() - height) // 2, 0
            )
        except Exception:
            x = max((self.winfo_screenwidth() - width) // 2, 0)
            y = max((self.winfo_screenheight() - height) // 2, 0)

        self.geometry(f"{width}x{height}+{x}+{y}")

    def _status_text(self) -> str:
        return (
            f"Stocks: {len(self.holdings_df)}"
            f"  |  Total Exposure: "
            f"{self._format_currency(self.holdings_df['Exposure'].sum())}"
            "  |  Ctrl+E: Export  |  Esc: Close"
        )

    @staticmethod
    def _to_float(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @classmethod
    def _format_currency(cls, value: Any) -> str:
        number = cls._to_float(value)
        sign = "-" if number < 0 else ""
        whole, decimal = f"{abs(number):.2f}".split(".")
        return f"{sign}₹{cls._indian_grouping(whole)}.{decimal}"

    @classmethod
    def _format_number(cls, value: Any) -> str:
        number = cls._to_float(value)
        sign = "-" if number < 0 else ""
        whole, decimal = f"{abs(number):.2f}".split(".")
        return f"{sign}{cls._indian_grouping(whole)}.{decimal}"

    @classmethod
    def _format_integer(cls, value: Any) -> str:
        return cls._indian_grouping(str(int(cls._to_float(value))))

    @classmethod
    def _format_percent(cls, value: Any) -> str:
        return f"{cls._to_float(value):.2f}%"

    @staticmethod
    def _indian_grouping(whole: str) -> str:
        whole = whole.lstrip("0") or "0"

        if len(whole) <= 3:
            return whole

        last_three = whole[-3:]
        remaining = whole[:-3]
        groups: list[str] = []

        while remaining:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]

        return ",".join(groups + [last_three])
