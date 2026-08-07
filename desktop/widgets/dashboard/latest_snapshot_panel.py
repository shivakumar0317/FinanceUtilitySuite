"""
Finance Utility Suite
Latest Snapshot Panel

Reusable dashboard widget that displays
information about the most recent snapshot.

Author : Shiva Kumar
Version: 2.1.0
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import customtkinter as ctk

from core.models.snapshot import SnapshotMetadata


class LatestSnapshotPanel(ctk.CTkFrame):
    """
    Dashboard widget displaying the latest snapshot information.

    Public Methods
    --------------
    load(metadata)
        Display snapshot information.

    clear()
        Reset all values.
    """

    def __init__(self, master, **kwargs):

        super().__init__(
            master,
            corner_radius=12,
            border_width=1,
            **kwargs,
        )

        self._labels: dict[str, ctk.CTkLabel] = {}

        self._build()

        self.clear()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------

    def _build(self):

        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self,
            text="📂 Latest Snapshot",
            font=("Segoe UI", 16, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=16,
            pady=(14, 12),
        )

        fields = [
            ("Business Date", "business_date"),
            ("Imported On", "imported_on"),
            ("Snapshot ID", "snapshot_id"),
            ("Source File", "source_file"),

            ("Records", "records"),
            ("Clients", "clients"),
            ("Symbols", "symbols"),

            ("Portfolio Value", "portfolio_value"),
            ("Total Exposure", "total_exposure"),
            ("Total MTM", "total_mtm"),

            ("Health", "health"),
            ("Risk Score", "risk_score"),
        ]

        for row, (caption, key) in enumerate(fields, start=1):

            ctk.CTkLabel(
                self,
                text=caption,
                font=("Segoe UI", 11),
                anchor="w",
                text_color=("#666666", "#A0A0A0"),
            ).grid(
                row=row,
                column=0,
                sticky="w",
                padx=(16, 10),
                pady=6,
            )

            value = ctk.CTkLabel(
                self,
                text="--",
                font=("Segoe UI", 11, "bold"),
                anchor="w",
            )

            value.grid(
                row=row,
                column=1,
                sticky="ew",
                padx=(8, 16),
                pady=6,
            )

            self._labels[key] = value

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def clear(self):

        for label in self._labels.values():
            label.configure(text="--")

    def load(
        self,
        metadata: SnapshotMetadata | None,
    ):

        if metadata is None:

            self.clear()

            return

        self._labels["business_date"].configure(
            text=self._format_date(
                metadata.business_date,
            ),
        )

        self._labels["imported_on"].configure(
            text=self._format_timestamp(
                metadata.timestamp,
            ),
        )

        self._labels["snapshot_id"].configure(
            text=metadata.snapshot_id,
        )

        self._labels["source_file"].configure(
            text=Path(
                metadata.source_file,
            ).name
            if metadata.source_file
            else "--",
        )

        self._labels["records"].configure(
            text=f"{metadata.records:,}"
        )

        self._labels["clients"].configure(
            text=f"{metadata.clients:,}"
        )

        self._labels["symbols"].configure(
            text=f"{metadata.symbols:,}"
        )

        self._labels["portfolio_value"].configure(
            text=self._money(metadata.portfolio_value)
        )

        self._labels["total_exposure"].configure(
            text=self._money(metadata.total_exposure)
        )

        self._labels["total_mtm"].configure(
            text=self._money(metadata.total_mtm)
        )

        self._labels["health"].configure(
            text=metadata.health
        )

        self._labels["risk_score"].configure(
            text=f"{metadata.risk_score:.2f}"
        )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _format_date(
        value: str,
    ) -> str:

        try:

            return datetime.fromisoformat(
                value,
            ).strftime("%d-%b-%Y")

        except Exception:

            return value or "--"

    @staticmethod
    def _format_timestamp(
        value: str,
    ) -> str:

        try:

            return datetime.fromisoformat(
                value,
            ).strftime("%d-%b-%Y %I:%M %p")

        except Exception:

            return value or "--"

    @staticmethod
    def _money(value: float) -> str:
        value = float(value)

        sign = "-" if value < 0 else ""
        value = abs(value)

        if value >= 1e7:
            return f"{sign}₹{value/1e7:.2f} Cr"

        if value >= 1e5:
            return f"{sign}₹{value/1e5:.2f} L"

        return f"{sign}₹{value:,.2f}"