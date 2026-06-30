"""
Stock Analyzer Page
Finance Utility Suite
"""

import threading
import customtkinter as ctk
from tkinter import filedialog

from core.stock_service import StockService
from core.excel_service import ExcelService

from desktop.widgets.result_table import ResultTable


class StockPage(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)

        # Services
        self.stock_service = StockService()
        self.excel_service = ExcelService()

        # Variables
        self.selected_file = ""
        self.is_running = False

        # Build UI
        self.create_widgets()

    # ----------------------------------------------------
    # Browse File
    # ----------------------------------------------------

    def browse_file(self):

        filename = filedialog.askopenfilename(
            title="Select Excel or CSV File",
            filetypes=[
                ("Excel Files", "*.xlsx"),
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )

        if filename:

            self.selected_file = filename

            self.file_label.configure(text=filename)

            self.log_message("File selected successfully.")

    # ----------------------------------------------------
    # Start Analysis
    # ----------------------------------------------------

    def start_analysis(self):

        if self.selected_file == "":

            self.log_message("Please select a file first.")
            return

        if self.is_running:
            return

        self.is_running = True

        self.analyze_btn.configure(state="disabled")

        self.progress.set(0)

        worker = threading.Thread(
            target=self.run_analysis,
            daemon=True
        )

        worker.start()

    # ----------------------------------------------------
    # Background Analysis
    # ----------------------------------------------------

    def run_analysis(self):

        try:

            self.progress.set(0.10)

            self.log_message("Reading file...")

            dataframe = self.stock_service.read_file(
                self.selected_file
            )

            self.progress.set(0.30)

            self.stock_service.validate_dataframe(
                dataframe
            )

            symbols = self.stock_service.prepare_symbols(
                dataframe
            )

            self.progress.set(0.50)

            self.log_message(
                f"Found {len(symbols)} symbols."
            )

            # Analyze first 5 stocks (testing)
            report = self.stock_service.analyze_symbols(
                symbols[:5],
                self.update_progress
            )

            self.log_message("Displaying results...")

            self.result_table.load_dataframe(report)

            self.progress.set(0.90)

            self.log_message(
                "Creating Excel report..."
            )

            output = self.excel_service.export(
                report
            )

            self.progress.set(1)

            self.log_message(
                "Analysis Completed Successfully."
            )

            self.log_message(output)

        except Exception as e:

            self.log_message(f"ERROR : {e}")

        finally:

            self.is_running = False

            self.analyze_btn.configure(
                state="normal"
            )

    # ----------------------------------------------------
    # Progress Callback
    # ----------------------------------------------------

    def update_progress(
        self,
        current,
        total,
        symbol,
        progress
    ):

        self.progress.set(progress)

        self.log_message(
            f"Analyzing {current}/{total} : {symbol}"
        )

    # ----------------------------------------------------
    # Logger
    # ----------------------------------------------------

    def log_message(self, message):

        self.log.insert(
            "end",
            str(message) + "\n"
        )

        self.log.see("end")

    # ----------------------------------------------------
    # Search
    # ----------------------------------------------------

    def search_table(self, event=None):

        self.result_table.search(
            self.search_var.get()
        )

    # ----------------------------------------------------
    # UI
    # ----------------------------------------------------

    def create_widgets(self):

        # ----------------------------------------
        # Title
        # ----------------------------------------

        title = ctk.CTkLabel(
            self,
            text="Stock Analyzer",
            font=("Segoe UI", 28, "bold")
        )

        title.pack(pady=20)

        # ----------------------------------------
        # File Label
        # ----------------------------------------

        self.file_label = ctk.CTkLabel(
            self,
            text="No file selected",
            font=("Segoe UI", 14),
            wraplength=700
        )

        self.file_label.pack(pady=10)

        # ----------------------------------------
        # Browse Button
        # ----------------------------------------

        self.browse_btn = ctk.CTkButton(
            self,
            text="Browse Excel / CSV",
            command=self.browse_file,
            width=220
        )

        self.browse_btn.pack(pady=10)

        # ----------------------------------------
        # Analyze Button
        # ----------------------------------------

        self.analyze_btn = ctk.CTkButton(
            self,
            text="Analyze",
            command=self.start_analysis,
            width=220
        )

        self.analyze_btn.pack(pady=10)

        # ----------------------------------------
        # Progress Bar
        # ----------------------------------------

        self.progress = ctk.CTkProgressBar(
            self,
            width=600
        )

        self.progress.pack(pady=20)
        self.progress.set(0)

        # ----------------------------------------
        # Activity Log
        # ----------------------------------------

        log_title = ctk.CTkLabel(
            self,
            text="Activity Log",
            font=("Segoe UI", 18, "bold")
        )

        log_title.pack(pady=(10, 5))

        self.log = ctk.CTkTextbox(
            self,
            width=850,
            height=180
        )

        self.log.pack(pady=10)

        self.log_message("Application Ready...")

        # ----------------------------------------
        # Search
        # ----------------------------------------

        search_title = ctk.CTkLabel(
            self,
            text="Search Symbol",
            font=("Segoe UI", 16, "bold")
        )

        search_title.pack(pady=(15, 5))

        self.search_var = ctk.StringVar()

        search_entry = ctk.CTkEntry(
            self,
            width=350,
            textvariable=self.search_var,
            placeholder_text="Type a symbol..."
        )

        search_entry.pack(pady=(0, 15))

        search_entry.bind(
            "<KeyRelease>",
            self.search_table
        )

        # ----------------------------------------
        # Result Table
        # ----------------------------------------

        table_title = ctk.CTkLabel(
            self,
            text="Analysis Results",
            font=("Segoe UI", 18, "bold")
        )

        table_title.pack(pady=(5, 10))

        self.result_table = ResultTable(self)

        self.result_table.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )