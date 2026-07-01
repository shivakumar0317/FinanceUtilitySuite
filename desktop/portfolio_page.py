import customtkinter as ctk
from tkinter import filedialog, messagebox

from desktop.widgets.dashboard_card import DashboardCard
from desktop.widgets.result_table import ResultTable
from desktop.widgets.chart_widget import ChartWidget
from core.services.portfolio_service import PortfolioService


class PortfolioPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)
        self.portfolio_df = None
        self.build_ui()

    def build_ui(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        title = ctk.CTkLabel(
            self,
            text="Portfolio Analyzer",
            font=("Segoe UI", 28, "bold")
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=1, column=0, sticky="ew", padx=20)

        import_btn = ctk.CTkButton(
            top_frame,
            text="📂 Import Portfolio",
            command=self.import_portfolio
        )
        import_btn.pack(side="left", padx=10, pady=10)

        self.status_label = ctk.CTkLabel(
            top_frame,
            text="Ready",
            anchor="w"
        )
        self.status_label.pack(side="left", padx=20)

        cards = ctk.CTkFrame(self)
        cards.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        for i in range(4):
            cards.grid_columnconfigure(i, weight=1)

        self.total_investment = DashboardCard(
            cards,
            title="Investment",
            value="₹0",
            subtitle="Total Invested"
        )
        self.current_value = DashboardCard(
            cards,
            title="Current Value",
            value="₹0",
            subtitle="Market Value"
        )
        self.pnl = DashboardCard(
            cards,
            title="Profit / Loss",
            value="₹0",
            subtitle="Return %"
        )
        self.holdings = DashboardCard(
            cards,
            title="Holdings",
            value="0",
            subtitle="Total Stocks"
        )

        self.total_investment.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self.current_value.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        self.pnl.grid(row=0, column=2, padx=8, pady=8, sticky="nsew")
        self.holdings.grid(row=0, column=3, padx=8, pady=8, sticky="nsew")

        charts_frame = ctk.CTkFrame(self)
        charts_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))

        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)

        self.allocation_chart = ChartWidget(charts_frame)
        self.allocation_chart.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.pnl_chart = ChartWidget(charts_frame)
        self.pnl_chart.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)

        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=(0, 20))

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.table = ResultTable(table_frame)
        self.table.grid(row=0, column=0, sticky="nsew")

    def import_portfolio(self):

        file_path = filedialog.askopenfilename(
            title="Select Portfolio",
            filetypes=[
                ("Excel Files", "*.xlsx"),
                ("CSV Files", "*.csv")
            ]
        )

        if not file_path:
            return

        try:
            self.status_label.configure(text="Loading portfolio...")

            dataframe, summary = PortfolioService.load(file_path)

            self.portfolio_df = dataframe

            self.table.load_dataframe(dataframe)
            self.update_cards(summary)
            self.update_charts(dataframe)

            self.status_label.configure(text="Portfolio loaded successfully")

        except Exception as error:
            self.status_label.configure(text="Import failed")
            messagebox.showerror("Portfolio Import", str(error))

    def update_cards(self, summary):

        self.total_investment.set_value(
            f"₹{summary['investment']:,.2f}"
        )

        self.current_value.set_value(
            f"₹{summary['current_value']:,.2f}"
        )

        self.pnl.set_value(
            f"₹{summary['profit']:,.2f}"
        )

        self.pnl.set_subtitle(
            f"{summary.get('return_percent', 0)}%"
        )

        self.holdings.set_value(
            summary["holdings"]
        )

    def update_charts(self, dataframe):

        if dataframe is None or dataframe.empty:
            return

        top_df = dataframe.sort_values(
            by="Current Value",
            ascending=False
        ).head(8)

        self.allocation_chart.plot_pie(
            labels=top_df["Symbol"].tolist(),
            values=top_df["Current Value"].tolist(),
            title="Portfolio Allocation"
        )

        pnl_df = dataframe.sort_values(
            by="Profit",
            ascending=False
        ).head(10)

        self.pnl_chart.plot_bar(
            x=pnl_df["Symbol"].tolist(),
            y=pnl_df["Profit"].tolist(),
            title="Top Profit / Loss",
            xlabel="Symbol",
            ylabel="Profit"
        )