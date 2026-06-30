"""
Finance Utility Suite
Main Application Launcher
"""

import customtkinter as ctk

from config import (
    APP_NAME,
    APP_VERSION,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    THEME,
    COLOR_THEME
)

from desktop.dashboard import Dashboard


def main():

    ctk.set_appearance_mode(THEME)
    ctk.set_default_color_theme(COLOR_THEME)

    app = Dashboard()

    app.title(f"{APP_NAME} v{APP_VERSION}")

    app.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    app.mainloop()


if __name__ == "__main__":
    main()