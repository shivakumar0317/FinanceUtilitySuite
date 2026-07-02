import customtkinter as ctk

from desktop.widgets.dashboard_card import DashboardCard

ctk.set_appearance_mode("Dark")

app = ctk.CTk()
app.geometry("900x500")

card1 = DashboardCard(
    app, title="Portfolio Value", value="₹18,42,500", subtitle="+5.24% Today"
)

card1.pack(padx=20, pady=20)

card2 = DashboardCard(
    app, title="Investment Score", value="87 / 100", subtitle="Excellent"
)

card2.pack(padx=20, pady=20)

app.mainloop()
