import customtkinter as ctk


class Sidebar(ctk.CTkFrame):

    def __init__(self, master, callback):
        super().__init__(master, width=240, corner_radius=0)

        self.callback = callback
        self.pack_propagate(False)
        self.create_widgets()

    def create_widgets(self):
        title = ctk.CTkLabel(
            self,
            text="Risk Management\nSystem (RMS)",
            font=("Segoe UI", 22, "bold"),
        )
        title.pack(pady=(25, 18))

        menu_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        menu_frame.pack(fill="both", expand=True, padx=0, pady=(0, 10))

        menu = [
            ("🏠 Dashboard", "dashboard"),
            ("📊 Analytics", "analytics"),
            ("📈 Stock Analyzer", "stocks"),
            ("💼 Portfolio", "portfolio"),
            ("🏦 MTF Analyzer", "mtf"),
            ("🎯 Concentration Risk", "concentration_risk"),
            ("📡 Live Market", "live"),
            ("💰 Portfolio Live", "portfolio_live"),
            ("📈 Portfolio Performance", "portfolio_performance"),
            ("📊 Risk Analytics", "risk_analytics"),
            ("🗂 Snapshot Manager", "snapshot_manager"),
            ("📄 Reports", "reports"),
            ("ℹ About", "about"),
        ]

        for text, page in menu:
            button = ctk.CTkButton(
                menu_frame,
                text=text,
                width=190,
                anchor="w",
                command=lambda selected_page=page: self.callback(selected_page),
            )
            button.pack(pady=6, padx=12)
