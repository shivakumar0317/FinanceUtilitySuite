"""
Finance Utility Suite
Base Page

Every application page inherits from this class.
"""

from __future__ import annotations

import customtkinter as ctk


class BasePage(ctk.CTkFrame):
    """
    Base class for all application pages.

    Child pages should override:
        build_ui()
        load_data()

    The refresh() method already works for every page.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._configure_grid()

        self.build_ui()

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    def _configure_grid(self):

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    # --------------------------------------------------
    # Methods to Override
    # --------------------------------------------------

    def build_ui(self):
        """Create all widgets."""
        pass

    def load_data(self):
        """Load page data."""
        pass

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def refresh(self):
        """Refresh page contents."""

        self.load_data()