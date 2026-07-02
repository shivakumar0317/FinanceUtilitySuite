import customtkinter as ctk

from config import (
    APP_NAME,
    APP_VERSION,
    COLOR_THEME,
    THEME,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from ui.dashboard import Dashboard

ctk.set_appearance_mode(THEME)
ctk.set_default_color_theme(COLOR_THEME)


class FinanceApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        Dashboard(self)


if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()
