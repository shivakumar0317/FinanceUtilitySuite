"""
Stock Analyzer Page
Finance Utility Suite
"""
import threading
import customtkinter as ctk
from tkinter import filedialog

from core.stock_service import StockService
from core.excel_service import ExcelService


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
    # Analyze
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

    def run_analysis(self):

     try:

        self.progress.set(0.10)

        self.log_message("Reading file...")

        dataframe = self.stock_service.read_file(
            self.selected_file
        )

        self.progress.set(0.30)

        self.stock_service.validate_dataframe(dataframe)

        symbols = self.stock_service.prepare_symbols(
            dataframe
        )

        self.progress.set(0.50)

        self.log_message(
            f"Found {len(symbols)} symbols."
        )

        report = self.stock_service.analyze_symbols(
         symbols[:5],
          self.update_progress
        )

        self.progress.set(0.90)

        self.log_message("Creating Excel report...")

        output = self.excel_service.export(report)

        self.progress.set(1)

        self.log_message("Completed Successfully.")

        self.log_message(output)

     except Exception as e:

        self.log_message(f"ERROR : {e}")

     finally:

        self.is_running = False

        self.analyze_btn.configure(
            state="normal"
        )    

    # ----------------------------------------------------
    # Logger
    # ----------------------------------------------------

    def log_message(self, message):

        self.log.insert("end", str(message) + "\n")

        self.log.see("end")

    # ----------------------------------------------------
    # UI
    # ----------------------------------------------------

    def create_widgets(self):

        # Title

        title = ctk.CTkLabel(
            self,
            text="Stock Analyzer",
            font=("Segoe UI", 28, "bold")
        )

        title.pack(pady=20)

        # File Label

        self.file_label = ctk.CTkLabel(
            self,
            text="No file selected",
            font=("Segoe UI", 14),
            wraplength=700
        )

        self.file_label.pack(pady=10)

        # Browse Button

        self.browse_btn = ctk.CTkButton(
            self,
            text="Browse Excel / CSV",
            command=self.browse_file,
            width=220
        )

        self.browse_btn.pack(pady=10)

        # Analyze Button

        self.analyze_btn = ctk.CTkButton(
            self,
            text="Analyze",
            command=self.start_analysis,
            width=220
        )

        self.analyze_btn.pack(pady=10)

        # Progress Bar

        self.progress = ctk.CTkProgressBar(
            self,
            width=600
        )

        self.progress.pack(pady=20)

        self.progress.set(0)

        # Activity Log

        log_title = ctk.CTkLabel(
            self,
            text="Activity Log",
            font=("Segoe UI", 18, "bold")
        )

        log_title.pack(pady=(10, 5))

        self.log = ctk.CTkTextbox(
            self,
            width=850,
            height=250
        )

        self.log.pack(pady=10)

        self.log_message("Application Ready...")

    def update_progress(self, current, total, symbol, progress):

     self.progress.set(progress)

     self.log_message(
        f"Analyzing {current}/{total} : {symbol}"
    )