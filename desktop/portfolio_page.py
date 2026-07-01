import customtkinter as ctk
from tkinter import filedialog, messagebox

from desktop.widgets.dashboard_card import DashboardCard
from desktop.widgets.result_table import ResultTable
from desktop.widgets.chart_widget import ChartWidget
from desktop.widgets.mini_table import MiniTable
from desktop.widgets.performance_widget import PerformanceWidget
from core.services.portfolio_service import PortfolioService


class PortfolioPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.portfolio_df = None

        self.build_ui()

    def build_ui(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)

        self.content = ctk.CTkScrollableFrame(self)
        self.content.grid(row=0, column=0, sticky="nsew")

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(6, weight=1)

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

        mini_tables_frame = ctk.CTkFrame(self)
        mini_tables_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 10))

        mini_tables_frame.grid_columnconfigure(0, weight=1)
        mini_tables_frame.grid_columnconfigure(1, weight=1)

        self.top_gainers_table = MiniTable(
            mini_tables_frame,
            title="Top Gainers"
        )
        self.top_gainers_table.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.top_losers_table = MiniTable(
            mini_tables_frame,
            title="Top Losers"
        )
        self.top_losers_table.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)

        self.performance_widget = PerformanceWidget(
            self,
            title="Portfolio Performance"
        )
        self.performance_widget.grid(
            row=5,
            column=0,
            sticky="ew",
            padx=20,
            pady=(0, 10)
        )

        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=6, column=0, sticky="nsew", padx=20, pady=(0, 20))

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
            self.update_mini_tables(dataframe)
            self.update_performance(dataframe)

            self.status_label.configure(text="Portfolio loaded successfully")

        except Exception as error:
            self.status_label.configure(text="Import failed")
            messagebox.showerror("Portfolio Import", str(error))

    def update_cards(self, summary):

        self.total_investment.set_value(f"₹{summary['investment']:,.2f}")
        self.current_value.set_value(f"₹{summary['current_value']:,.2f}")
        self.pnl.set_value(f"₹{summary['profit']:,.2f}")
        self.pnl.set_subtitle(f"{summary.get('return_percent', 0)}%")
        self.holdings.set_value(summary["holdings"])

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

    def update_mini_tables(self, dataframe):

        if dataframe is None or dataframe.empty:
            return

        required_columns = ["Symbol", "Current Price", "Return %"]

        for column in required_columns:
            if column not in dataframe.columns:
                return

        gainers_df = dataframe.sort_values(
            by="Return %",
            ascending=False
        ).head(5)

        losers_df = dataframe.sort_values(
            by="Return %",
            ascending=True
        ).head(5)

        gainers = []

        for _, row in gainers_df.iterrows():
            gainers.append(
                (
                    row["Symbol"],
                    row["Current Price"],
                    row["Return %"]
                )
            )

        losers = []

        for _, row in losers_df.iterrows():
            losers.append(
                (
                    row["Symbol"],
                    row["Current Price"],
                    row["Return %"]
                )
            )

        self.top_gainers_table.load_data(gainers)
        self.top_losers_table.load_data(losers)

    def update_performance(self, dataframe):

        if dataframe is None or dataframe.empty:
            return

        required_columns = ["Symbol", "Return %", "Profit"]

        for column in required_columns:
            if column not in dataframe.columns:
                return

        best_row = dataframe.loc[dataframe["Return %"].idxmax()]
        worst_row = dataframe.loc[dataframe["Return %"].idxmin()]

        average_return = dataframe["Return %"].mean()
        winning_stocks = dataframe[dataframe["Return %"] > 0].shape[0]
        losing_stocks = dataframe[dataframe["Return %"] < 0].shape[0]
        total_profit = dataframe["Profit"].sum()

        metrics = {
            "Best Performer": (
                f"{best_row['Symbol']} "
                f"({best_row['Return %']:.2f}%)"
            ),
            "Worst Performer": (
                f"{worst_row['Symbol']} "
                f"({worst_row['Return %']:.2f}%)"
            ),
            "Average Return": f"{average_return:.2f}%",
            "Winning Stocks": winning_stocks,
            "Losing Stocks": losing_stocks,
            "Total Profit": f"₹{total_profit:,.2f}"
        }

        self.performance_widget.update_metrics(metrics)