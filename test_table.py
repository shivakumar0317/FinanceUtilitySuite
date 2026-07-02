import customtkinter as ctk
import pandas as pd

from desktop.widgets.result_table import ResultTable

app = ctk.CTk()

app.title("Result Table Test")
app.geometry("900x500")

table = ResultTable(app)
table.pack(fill="both", expand=True, padx=20, pady=20)

df = pd.DataFrame(
    {
        "Symbol": ["RELIANCE", "TCS", "INFY", "HDFCBANK"],
        "CMP": [1485.20, 3610.10, 1588.60, 1850.75],
        "Beta": [0.88, 0.91, 1.05, 0.82],
        "PE": [24.5, 31.2, 28.7, 19.4],
        "Risk": ["Low", "Low", "Moderate", "Low"],
        "Score": [94, 91, 82, 96],
        "Rating": ["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐☆", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"],
    }
)

table.load_dataframe(df)

app.mainloop()
