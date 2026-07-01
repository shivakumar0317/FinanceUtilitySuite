import customtkinter as ctk
from tkinter import filedialog

from desktop.widgets.dashboard_card import DashboardCard
from desktop.widgets.result_table import ResultTable


class PortfolioPage(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)

        self.build_ui()

    # -------------------------------------------------
    # UI
    # -------------------------------------------------

    def build_ui(self):

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # -------------------------------
        # Title
        # -------------------------------

        title = ctk.CTkLabel(
            self,
            text="Portfolio Analyzer",
            font=("Segoe UI", 28, "bold")
        )

        title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(20, 10)
        )

        # -------------------------------
        # Top Controls
        # -------------------------------

        top_frame = ctk.CTkFrame(self)

        top_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=20
        )

        import_btn = ctk.CTkButton(
            top_frame,
            text="📂 Import Portfolio",
            command=self.import_portfolio
        )

        import_btn.pack(
            side="left",
            padx=10,
            pady=10
        )

        # -------------------------------
        # Summary Cards
        # -------------------------------

        cards = ctk.CTkFrame(self)

        cards.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=20,
            pady=10
        )

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
            subtitle="Net Gain"
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

        # -------------------------------
        # Holdings Table
        # -------------------------------

        table_frame = ctk.CTkFrame(self)

        table_frame.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(0, 20)
        )

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.table = ResultTable(table_frame)

        self.table.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

    # -------------------------------------------------
    # Import Portfolio
    # -------------------------------------------------

    def import_portfolio(self):

        file_path = filedialog.askopenfilename(

            title="Select Portfolio",

            filetypes=[

                ("Excel Files", "*.xlsx"),

                ("CSV Files", "*.csv")

            ]
        )

        if file_path:

            print(file_path)