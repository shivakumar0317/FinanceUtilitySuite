"""
Finance Utility Suite
Theme Manager

Centralized application theme configuration.

Author : Shiva Kumar
Version: 1.00
"""

from __future__ import annotations


class Theme:
    """Global application theme."""

    # -------------------------------------------------
    # Application
    # -------------------------------------------------

    APP_NAME = "Finance Utility Suite"
    VERSION = "1.00"

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
    SECTION_SPACING = 16
    CARD_PADDING = 12
    GRID_GAP = 12

    CARD_HEIGHT = 140
    CHART_HEIGHT = 320
    TABLE_HEIGHT = 260
    STATUSBAR_HEIGHT = 34
    BUTTON_HEIGHT = 34

    BORDER_RADIUS = 8
    BORDER_WIDTH = 1

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

    SURFACE = "#202123"
    SURFACE_HOVER = "#2A2D2E"
    CARD_BG = SURFACE
    CHART_BG = "#18181B"

    BORDER_COLOR = "#3F3F46"
    GRID_COLOR = "#404040"

    CHART_PRIMARY = PRIMARY
    CHART_SUCCESS = SUCCESS
    CHART_WARNING = WARNING
    CHART_ERROR = ERROR
    CHART_INFO = INFO

    # -------------------------------------------------
    # Charts
    # -------------------------------------------------

    PIE_MAX_ITEMS = 8
    BAR_MAX_ITEMS = 10

    # -------------------------------------------------
    # Tables
    # -------------------------------------------------

    MINI_TABLE_ROWS = 5
    TREE_ROW_HEIGHT = 30