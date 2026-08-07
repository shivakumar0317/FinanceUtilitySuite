"""Enterprise-polished Snapshot Manager page for RMS."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from core.services.snapshot_manager_service import SnapshotManagerService
from desktop.base_page import BasePage
from desktop.widgets.metric_card import MetricCard
from desktop.widgets.result_table import ResultTable
from desktop.widgets.snapshot_details_panel import SnapshotDetailsPanel


class SnapshotViewerWindow(ctk.CTkToplevel):
    def __init__(self, master, snapshot_id: str, dataframe) -> None:
        super().__init__(master)
        self.title(f"Snapshot Viewer - {snapshot_id}")
        self.geometry("1300x720")
        self.minsize(900, 500)
        self.transient(master.winfo_toplevel())
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 10))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header,
            text=f"Snapshot: {snapshot_id}",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header,
            text=f"Rows: {len(dataframe):,} | Columns: {len(dataframe.columns):,}",
        ).grid(row=0, column=1, sticky="e")

        table = ResultTable(self)
        table.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table.load_dataframe(dataframe)
        table.auto_fit_columns()
        self.after(150, self.focus_force)


class SnapshotManagerPage(BasePage):
    TREE_STYLE = "Snapshot.Treeview"

    def __init__(self, master) -> None:
        super().__init__(master, "Snapshot Manager")
        self.service = SnapshotManagerService()
        self._metadata_by_item = {}
        self._search_job = None
        self._last_refresh_text = "—"
        self._build_page()
        self.refresh_snapshots()

    def _build_page(self) -> None:
        self.content.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(self.content, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=20, pady=(0, 10))
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            top,
            text="Historical portfolio snapshots and audit-ready position data",
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self.health_label = ctk.CTkLabel(
            top,
            text="● No Data",
            corner_radius=12,
            fg_color="#6B7280",
            text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100,
            height=26,
        )
        self.health_label.grid(row=0, column=1, padx=(12, 0))

        self.refresh_label = ctk.CTkLabel(top, text="")
        self.refresh_label.grid(row=0, column=2, padx=(16, 0))

        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 10))
        for col in range(5):
            cards.grid_columnconfigure(col, weight=1)

        self.card_snapshots = MetricCard(cards, "Snapshots", "📂", "0", "Available history")
        self.card_records = MetricCard(cards, "Records", "📄", "0", "Latest snapshot")
        self.card_clients = MetricCard(cards, "Clients", "👥", "0", "Latest snapshot")
        self.card_symbols = MetricCard(cards, "Symbols", "📈", "0", "Latest snapshot")
        self.card_exposure = MetricCard(cards, "Exposure", "💰", "₹0.00", "Latest snapshot")
        for col, card in enumerate(
            [self.card_snapshots, self.card_records, self.card_clients, self.card_symbols, self.card_exposure]
        ):
            card.grid(row=0, column=col, sticky="nsew", padx=6)

        toolbar = ctk.CTkFrame(self.content, corner_radius=10)
        toolbar.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        toolbar.grid_columnconfigure(0, weight=1)

        self.search_var = ctk.StringVar()
        search = ctk.CTkEntry(
            toolbar,
            textvariable=self.search_var,
            placeholder_text="🔍 Search Snapshot ID, source file, date or status...",
            height=34,
        )
        search.grid(row=0, column=0, sticky="ew", padx=(12, 10), pady=10)
        self.search_var.trace_add("write", self._schedule_search)

        button_specs = [
            ("🔄 Refresh", 108, self.refresh_snapshots, None),
            ("📂 Open", 96, self.open_selected_snapshot, None),
            ("📊 Compare", 108, None, "disabled"),
            ("📤 Export", 102, self.export_selected_snapshot, None),
        ]
        for index, (text, width, command, state) in enumerate(button_specs, start=1):
            button = ctk.CTkButton(toolbar, text=text, width=width, command=command)
            if state:
                button.configure(state=state)
            button.grid(row=0, column=index, padx=4, pady=10)

        ctk.CTkButton(
            toolbar,
            text="🗑 Delete",
            width=98,
            fg_color="#B3261E",
            hover_color="#8C1D18",
            command=self.delete_selected_snapshot,
        ).grid(row=0, column=5, padx=(4, 12), pady=10)

        split = ctk.CTkFrame(self.content, fg_color="transparent")
        split.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 10))
        split.grid_columnconfigure(0, weight=4)
        split.grid_columnconfigure(1, weight=2)
        split.grid_rowconfigure(0, weight=1)

        table_frame = ctk.CTkFrame(split, corner_radius=12, border_width=1)
        table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            table_frame,
            text="Snapshot List",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 8))

        self._configure_tree_style()
        columns = ("business_date", "imported_on", "status", "records", "clients", "symbols", "exposure", "mtm", "source_file")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=14,
            style=self.TREE_STYLE,
        )

        headings = {
            "business_date": "Business Date",
            "imported_on": "Imported On",
            "status": "Status",
            "records": "Records",
            "clients": "Clients",
            "symbols": "Symbols",
            "exposure": "Exposure",
            "mtm": "MTM",
            "source_file": "Source File",
        }
        widths = {
            "business_date": 110,
            "imported_on": 165,
            "status": 100,
            "records": 80,
            "clients": 75,
            "symbols": 75,
            "exposure": 120,
            "mtm": 120,
            "source_file": 180,
        }
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(
                column,
                width=widths[column],
                minwidth=65,
                anchor="e" if column in {"records", "clients", "symbols", "exposure", "mtm"} else "center",
                stretch=True,
            )

        self.tree.tag_configure("healthy", foreground="#7BE495")
        self.tree.tag_configure("warning", foreground="#F7C948")
        self.tree.tag_configure("critical", foreground="#FF8A80")
        self.tree.tag_configure("neutral", foreground="#D1D5DB")

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.tree.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=(0, 8))
        y_scroll.grid(row=1, column=1, sticky="ns", pady=(0, 8))
        x_scroll.grid(row=2, column=0, sticky="ew", padx=(10, 0))
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_changed)
        self.tree.bind("<Double-1>", lambda _event: self.open_selected_snapshot())

        self.details = SnapshotDetailsPanel(split)
        self.details.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        footer = ctk.CTkFrame(self.content, corner_radius=8)
        footer.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 18))
        footer.grid_columnconfigure(0, weight=1)
        footer.grid_columnconfigure(1, weight=1)
        footer.grid_columnconfigure(2, weight=1)
        self.footer_count = ctk.CTkLabel(footer, text="Showing 0 snapshots", anchor="w")
        self.footer_count.grid(row=0, column=0, sticky="w", padx=12, pady=8)
        self.footer_selected = ctk.CTkLabel(footer, text="Selected: —", anchor="center")
        self.footer_selected.grid(row=0, column=1, sticky="ew", padx=12, pady=8)
        self.footer_refresh = ctk.CTkLabel(footer, text="Last refresh: —", anchor="e")
        self.footer_refresh.grid(row=0, column=2, sticky="e", padx=12, pady=8)

    def _configure_tree_style(self) -> None:
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            self.TREE_STYLE,
            background="#252525",
            fieldbackground="#252525",
            foreground="#F2F2F2",
            rowheight=30,
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10),
        )
        style.map(
            self.TREE_STYLE,
            background=[("selected", "#1F6AA5")],
            foreground=[("selected", "#FFFFFF")],
        )
        style.configure(
            f"{self.TREE_STYLE}.Heading",
            background="#1E1E1E",
            foreground="#F5F5F5",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padding=(8, 7),
        )
        style.map(
            f"{self.TREE_STYLE}.Heading",
            background=[("active", "#2F3B47")],
            foreground=[("active", "#FFFFFF")],
        )

    def _schedule_search(self, *_args) -> None:
        if self._search_job is not None:
            self.after_cancel(self._search_job)
        self._search_job = self.after(250, self.refresh_snapshots)

    def refresh_snapshots(self) -> None:
        self._search_job = None
        try:
            snapshots = self.service.list_metadata(self.search_var.get())
            snapshots.sort(
            key=lambda x: x.business_date,
            reverse=True,
        )
            summary = self.service.summary(snapshots)
        except Exception as exc:
            self.set_status("Unable to load snapshots")
            messagebox.showerror("Snapshot Manager", str(exc), parent=self)
            return

        self.tree.delete(*self.tree.get_children())
        self._metadata_by_item.clear()
        for metadata in snapshots:
            status, level = self.service.health_status(metadata)
            icon = {"healthy": "●", "warning": "●", "critical": "●", "neutral": "●"}.get(level, "●")
            values = (

                datetime.fromisoformat(
                    metadata.business_date
                ).strftime("%d-%b-%Y"),

                self.service.format_timestamp(
                    metadata.timestamp
                ),

                f"{icon} {status}",

                f"{metadata.records:,}",

                f"{metadata.clients:,}",

                f"{metadata.symbols:,}",

                self.service.format_indian_compact(
                    metadata.total_exposure
                ),

                self.service.format_indian_compact(
                    metadata.total_mtm
                ),

                Path(metadata.source_file).name
                if metadata.source_file else "",
            )
            item = self.tree.insert("", "end", values=values, tags=(level,))
            self._metadata_by_item[item] = metadata

        self.card_snapshots.set_value(f"{summary['snapshots']:,}")
        self.card_records.set_value(f"{summary['records']:,}")
        self.card_clients.set_value(f"{summary['clients']:,}")
        self.card_symbols.set_value(f"{summary['symbols']:,}")
        self.card_exposure.set_value(self.service.format_indian_compact(summary["exposure"]))

        latest = snapshots[0] if snapshots else None
        status, level = self.service.health_status(latest)
        status_colors = {
            "healthy": "#2E7D32",
            "warning": "#D97706",
            "critical": "#C62828",
            "neutral": "#6B7280",
        }
        self.health_label.configure(
            text=f"● {status}",
            fg_color=status_colors.get(level, status_colors["neutral"]),
        )

        self._last_refresh_text = datetime.now().strftime("%I:%M:%S %p")
        self.refresh_label.configure(text=f"Last refresh: {self._last_refresh_text}")
        self.footer_count.configure(text=f"Showing {len(snapshots):,} snapshot(s)")
        self.footer_selected.configure(text="Selected: —")
        self.footer_refresh.configure(text=f"Last refresh: {self._last_refresh_text}")
        self.details.clear()
        self.set_status(f"Loaded {len(snapshots):,} snapshot(s)")

    def _selected_metadata(self):
        selected = self.tree.selection()
        return self._metadata_by_item.get(selected[0]) if selected else None

    def _on_selection_changed(self, _event=None) -> None:
        metadata = self._selected_metadata()
        if metadata is None:
            self.details.clear()
            self.footer_selected.configure(text="Selected: —")
            return

        status, level = self.service.health_status(metadata)
        self.details.load(
            metadata,
            status,
            level,
            self.service.format_timestamp,
            self.service.format_money,
        )
        self.footer_selected.configure(text=f"Selected: {metadata.snapshot_id}")
        self.set_status(f"Selected {metadata.snapshot_id}")

    def open_selected_snapshot(self) -> None:
        metadata = self._selected_metadata()
        if metadata is None:
            messagebox.showinfo("Snapshot Manager", "Please select a snapshot first.", parent=self)
            return
        try:
            dataframe = self.service.load_snapshot(metadata.snapshot_id)
            SnapshotViewerWindow(self, metadata.snapshot_id, dataframe)
            self.set_status(f"Opened {metadata.snapshot_id}")
        except Exception as exc:
            messagebox.showerror("Open Snapshot", str(exc), parent=self)

    def export_selected_snapshot(self) -> None:
        metadata = self._selected_metadata()
        if metadata is None:
            messagebox.showinfo("Snapshot Manager", "Please select a snapshot first.", parent=self)
            return

        output_path = filedialog.asksaveasfilename(
            parent=self,
            title="Export Snapshot to Excel",
            initialfile=f"{metadata.snapshot_id}.xlsx",
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
        )
        if not output_path:
            return

        try:
            target = self.service.export_to_excel(metadata.snapshot_id, output_path)
            self.set_status(f"Exported {target.name}")
            messagebox.showinfo(
                "Export Complete",
                f"Snapshot exported successfully:\n\n{target}",
                parent=self,
            )
        except Exception as exc:
            messagebox.showerror("Export Snapshot", str(exc), parent=self)

    def delete_selected_snapshot(self) -> None:
        metadata = self._selected_metadata()
        if metadata is None:
            messagebox.showinfo("Snapshot Manager", "Please select a snapshot first.", parent=self)
            return

        if not messagebox.askyesno(
            "Delete Snapshot",
            f"Delete snapshot {metadata.snapshot_id}?\n\nThis cannot be undone.",
            icon="warning",
            parent=self,
        ):
            return

        try:
            if not self.service.delete_snapshot(metadata.snapshot_id):
                raise FileNotFoundError(f"Snapshot not found: {metadata.snapshot_id}")
            self.refresh_snapshots()
            self.set_status(f"Deleted {metadata.snapshot_id}")
        except Exception as exc:
            messagebox.showerror("Delete Snapshot", str(exc), parent=self)
