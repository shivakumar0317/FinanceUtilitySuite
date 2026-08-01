"""Enterprise snapshot details side panel."""
from __future__ import annotations

from pathlib import Path
import customtkinter as ctk

from core.models.snapshot import SnapshotMetadata


class SnapshotDetailsPanel(ctk.CTkFrame):
    STATUS_COLORS = {
        "healthy": "#2E7D32",
        "warning": "#D97706",
        "critical": "#C62828",
        "neutral": "#6B7280",
    }

    def __init__(self, master):
        super().__init__(master, corner_radius=12, border_width=1)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self,
            text="Snapshot Details",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(16, 10))

        self.status_badge = ctk.CTkLabel(
            self,
            text="No Data",
            corner_radius=12,
            fg_color="#6B7280",
            text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=92,
            height=26,
        )
        self.status_badge.grid(row=1, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 12))

        self.value_labels: dict[str, ctk.CTkLabel] = {}
        current_row = 2
        sections = [
            ("GENERAL", [("snapshot_id", "Snapshot ID"), ("timestamp", "Imported"), ("source_file", "Source File")]),
            ("PORTFOLIO", [("records", "Records"), ("clients", "Clients"), ("symbols", "Symbols"), ("portfolio_value", "Portfolio Value")]),
            ("RISK", [("exposure", "Exposure"), ("mtm", "MTM")]),
            ("IMPORT", [("notes", "Notes")]),
        ]

        for section, fields in sections:
            ctk.CTkLabel(
                self,
                text=section,
                anchor="w",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("#5B6573", "#8FA0B3"),
            ).grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=16, pady=(8, 4))
            current_row += 1

            for key, caption in fields:
                ctk.CTkLabel(
                    self,
                    text=caption,
                    anchor="w",
                    text_color=("#555555", "#AAAAAA"),
                ).grid(row=current_row, column=0, sticky="nw", padx=(16, 8), pady=5)

                label = ctk.CTkLabel(
                    self,
                    text="—",
                    anchor="w",
                    justify="left",
                    wraplength=250,
                )
                label.grid(row=current_row, column=1, sticky="ew", padx=(8, 16), pady=5)
                self.value_labels[key] = label
                current_row += 1

    def clear(self) -> None:
        self.status_badge.configure(text="No Data", fg_color=self.STATUS_COLORS["neutral"])
        for label in self.value_labels.values():
            label.configure(text="—")

    def load(self, metadata: SnapshotMetadata, status: str, level: str, format_timestamp, format_money) -> None:
        icon = {"healthy": "●", "warning": "●", "critical": "●", "neutral": "●"}.get(level, "●")
        self.status_badge.configure(
            text=f"{icon} {status}",
            fg_color=self.STATUS_COLORS.get(level, self.STATUS_COLORS["neutral"]),
        )

        values = {
            "snapshot_id": metadata.snapshot_id,
            "timestamp": format_timestamp(metadata.timestamp),
            "source_file": Path(metadata.source_file).name if metadata.source_file else "—",
            "records": f"{metadata.records:,}",
            "clients": f"{metadata.clients:,}",
            "symbols": f"{metadata.symbols:,}",
            "portfolio_value": format_money(metadata.portfolio_value),
            "exposure": format_money(metadata.total_exposure),
            "mtm": format_money(metadata.total_mtm),
            "notes": metadata.notes or "—",
        }
        for key, value in values.items():
            self.value_labels[key].configure(text=value)
