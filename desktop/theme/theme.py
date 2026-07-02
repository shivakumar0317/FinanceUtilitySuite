"""
Finance Utility Suite
Theme Manager

Centralized application theme configuration.
"""

from __future__ import annotations


class Theme:
    """
    Global application theme.

    Contains:

    • Colors
    • Fonts
    • Sizes
    • Padding
    • Spacing
    """

    # -------------------------------------------------
    # Application
    # -------------------------------------------------

    APP_NAME = "Finance Utility Suite"
    VERSION = "0.95"

    # -------------------------------------------------
    # Fonts
    # -------------------------------------------------

    FONT_FAMILY = "Segoe UI"

    FONT_TITLE = (FONT_FAMILY, 28, "bold")

    FONT_HEADING = (FONT_FAMILY, 18, "bold")

    FONT_SUBHEADING = (FONT_FAMILY, 15, "bold")

    FONT_NORMAL = (FONT_FAMILY, 12)

    FONT_SMALL = (FONT_FAMILY, 11)

    FONT_BUTTON = (FONT_FAMILY, 12, "bold")

    # -------------------------------------------------
    # Layout
    # -------------------------------------------------

    PAGE_PADDING = 20

    SECTION_SPACING = 12

    CARD_PADDING = 8

    BORDER_RADIUS = 8

    # -------------------------------------------------
    # Colors
    # -------------------------------------------------

    PRIMARY = "#2563EB"

    SUCCESS = "#16A34A"

    WARNING = "#D97706"

    ERROR = "#DC2626"

    INFO = "#0891B2"

    TEXT_PRIMARY = "#FFFFFF"

    TEXT_SECONDARY = "#A1A1AA"

    # -------------------------------------------------
    # Charts
    # -------------------------------------------------

    PIE_MAX_ITEMS = 8

    BAR_MAX_ITEMS = 10

    # -------------------------------------------------
    # Tables
    # -------------------------------------------------

    MINI_TABLE_ROWS = 5

    TREE_ROW_HEIGHT = 28