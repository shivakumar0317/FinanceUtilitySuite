import customtkinter as ctk


class StatCard(ctk.CTkFrame):

    def __init__(self, master, title, value):

        super().__init__(master, corner_radius=12)

        self.configure(width=180, height=120)

        self.pack_propagate(False)

        title_label = ctk.CTkLabel(self, text=title, font=("Segoe UI", 16))

        title_label.pack(pady=(20, 5))

        self.value_label = ctk.CTkLabel(self, text=value, font=("Segoe UI", 28, "bold"))

        self.value_label.pack()

    def set_value(self, value):

        self.value_label.configure(text=value)
