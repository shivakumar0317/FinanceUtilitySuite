"""
Finance Utility Suite
Base Page

All application pages inherit from this class.
"""

from __future__ import annotations

import customtkinter as ctk


class BasePage(ctk.CTkFrame):
    """
    Base class for every application page.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.build_ui()

    # --------------------------------------------------
    # Override in child pages
    # --------------------------------------------------

    def build_ui(self):
        """Create page widgets."""
        pass

    def load_data(self):
        """Load page data."""
        pass

    def refresh(self):
        """Refresh page."""
        self.load_data()