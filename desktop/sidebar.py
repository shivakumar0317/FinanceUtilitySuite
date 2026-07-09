import customtkinter as ctk


class Sidebar(ctk.CTkFrame):

    def __init__(self, master, callback):

        super().__init__(master, width=220, corner_radius=0)

        self.callback = callback
        self.pack_propagate(False)

        self.create_widgets()

    def create_widgets(self):

        title = ctk.CTkLabel(
            self, text="Finance\nUtility Suite", font=("Segoe UI", 22, "bold")
        )

        title.pack(pady=(30, 25))

        menu = [
            ("🏠 Dashboard", "dashboard"),
            ("📊 Analytics", "analytics"),
            ("📈 Stock Analyzer", "stocks"),
            ("💼 Portfolio", "portfolio"),
            ("🏦 MTF Analyzer", "mtf"),
            ("📡 Live Market", "live"),
            ("💰 Portfolio Live", "portfolio_live"),
            ("💰 Loan Calculator", "loan"),
            ("📄 Reports", "reports"),
            ("⚙ Settings", "settings"),
            ("ℹ About", "about")
        ]

        for text, page in menu:

            btn = ctk.CTkButton(
                self,
                text=text,
                width=180,
                anchor="w",
                command=lambda p=page: self.callback(p),
            )

            btn.pack(pady=8, padx=20)
