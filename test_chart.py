import customtkinter as ctk

from desktop.widgets.chart_widget import ChartWidget

app = ctk.CTk()
app.geometry("900x600")

chart = ChartWidget(app)
chart.pack(fill="both", expand=True, padx=20, pady=20)

chart.plot_line(
    ["Jan", "Feb", "Mar", "Apr", "May"],
    [120, 150, 140, 180, 210],
    title="Monthly Price",
    xlabel="Month",
    ylabel="Price"
)

app.mainloop()