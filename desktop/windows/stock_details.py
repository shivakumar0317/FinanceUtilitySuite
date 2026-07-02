import customtkinter as ctk


class StockDetailsWindow(ctk.CTkToplevel):

    def __init__(self, master, data):

        super().__init__(master)

        self.title("Stock Details")
        self.geometry("650x650")

        self.data = data

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # -----------------------------------
        # Header
        # -----------------------------------

        symbol = data.get("Symbol", "Unknown")

        title = ctk.CTkLabel(
            self, text=f"{symbol} Analysis", font=("Segoe UI", 24, "bold")
        )

        title.grid(row=0, column=0, pady=(20, 10))

        # -----------------------------------
        # Scrollable Content
        # -----------------------------------

        self.body = ctk.CTkScrollableFrame(self)

        self.body.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        # Show every column/value pair

        for key, value in data.items():

            row = ctk.CTkFrame(self.body)

            row.pack(fill="x", pady=4)

            label = ctk.CTkLabel(
                row, text=f"{key}", width=180, anchor="w", font=("Segoe UI", 12, "bold")
            )

            label.pack(side="left", padx=10, pady=8)

            val = ctk.CTkLabel(row, text=str(value), anchor="w")

            val.pack(side="left", padx=10)

        # -----------------------------------
        # Close Button
        # -----------------------------------

        close_btn = ctk.CTkButton(self, text="Close", command=self.destroy)

        close_btn.grid(row=2, column=0, pady=20)
