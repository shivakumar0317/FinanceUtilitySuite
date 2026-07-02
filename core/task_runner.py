"""
Finance Utility Suite
Background Task Runner
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any


class TaskRunner:
    """Run background tasks without blocking the UI."""

    def __init__(self, widget):
        """
        widget:
            Any tkinter/customtkinter widget.
            Used for safely scheduling callbacks on the UI thread.
        """
        self.widget = widget

    def run(
        self,
        task: Callable[..., Any],
        *,
        on_success: Callable[[Any], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
        args: tuple = (),
        kwargs: dict | None = None,
    ) -> None:
        """Execute a task in a background thread."""

        if kwargs is None:
            kwargs = {}

        def worker() -> None:
            try:
                result = task(*args, **kwargs)

                if on_success:
                    self.widget.after(
                        0,
                        lambda: on_success(result),
                    )

            except Exception as exc:
                if on_error:
                    self.widget.after(
                        0,
                        lambda: on_error(exc),
                    )

        threading.Thread(
            target=worker,
            daemon=True,
        ).start()