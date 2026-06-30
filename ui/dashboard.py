import os
import threading
from tkinter import filedialog

import customtkinter as ctk

from modules.stock_analyzer import StockAnalyzer
from modules.excel_export import ExcelExporter


class Dashboard:

    def __init__(self, root):

        self.root = root
        self.selected_file = ""

        self.analyzer = StockAnalyzer()
        self.exporter = ExcelExporter()

        self.build_ui()

    def build_ui(self):

        sidebar = ctk.CTkFrame(self.root, width=220)
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(
            sidebar,
            text="Finance Utility Suite",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=25)

        ctk.CTkButton(
            sidebar,
            text="Stock Analyzer"
        ).pack(pady=10)

        # ---------------- Main Area ----------------

        main = ctk.CTkFrame(self.root)
        main.pack(fill="both", expand=True)

        ctk.CTkLabel(
            main,
            text="Stock Analyzer",
            font=("Segoe UI", 28, "bold")
        ).pack(pady=20)

        ctk.CTkButton(
            main,
            text="Browse CSV / Excel",
            command=self.browse_file
        ).pack()

        self.file_label = ctk.CTkLabel(
            main,
            text="No file selected"
        )

        self.file_label.pack(pady=10)

        self.start_btn = ctk.CTkButton(
            main,
            text="Start Analysis",
            command=self.start_analysis
        )

        self.start_btn.pack(pady=15)

        self.progress = ctk.CTkProgressBar(main, width=500)
        self.progress.pack(pady=10)
        self.progress.set(0)

        self.log = ctk.CTkTextbox(
            main,
            width=850,
            height=300
        )

        self.log.pack(pady=20)

        self.write_log("Application Ready.")

    def browse_file(self):

        filename = filedialog.askopenfilename(
            filetypes=[
                ("CSV", "*.csv"),
                ("Excel", "*.xlsx")
            ]
        )

        if filename:

            self.selected_file = filename
            self.file_label.configure(text=filename)

            self.write_log("File Selected.")

    def write_log(self, text):

        self.log.insert("end", text + "\n")
        self.log.see("end")

    def start_analysis(self):

        if self.selected_file == "":
            self.write_log("Please select a file first.")
            return

        self.start_btn.configure(state="disabled")

        threading.Thread(
            target=self.run_analysis,
            daemon=True
        ).start()

    def run_analysis(self):

        self.write_log("Reading Stock File...")

        df = self.analyzer.analyze_file(self.selected_file)

        self.progress.set(0.80)

        os.makedirs("output", exist_ok=True)

        output_file = "output/Stock_Analysis_Report.xlsx"

        self.exporter.export(df, output_file)

        self.progress.set(1)

        self.write_log("Excel Report Created Successfully.")

        self.write_log(output_file)

        self.start_btn.configure(state="normal")