from __future__ import annotations

from typing import Sequence

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


class ChartWidget(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()

        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        toolbar_frame = ctk.CTkFrame(self, fg_color="transparent")
        toolbar_frame.grid(row=1, column=0, sticky="ew")

        self.toolbar = NavigationToolbar2Tk(
            self.canvas, toolbar_frame, pack_toolbar=False
        )
        self.toolbar.update()
        self.toolbar.pack(fill="x")

    def clear(self):
        self.axes.clear()
        self.canvas.draw_idle()

    def _finish_chart(self, title="", xlabel="", ylabel=""):
        self.axes.set_title(title)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        self.axes.grid(True, linestyle="--", alpha=0.3)
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def plot_line(self, x: Sequence, y: Sequence, title="", xlabel="", ylabel=""):
        self.axes.clear()
        self.axes.plot(x, y, marker="o", linewidth=2)
        self._finish_chart(title, xlabel, ylabel)

    def plot_bar(self, x: Sequence, y: Sequence, title="", xlabel="", ylabel=""):
        self.axes.clear()
        self.axes.bar(x, y)
        self._finish_chart(title, xlabel, ylabel)

    def plot_pie(self, labels: Sequence, values: Sequence, title=""):
        self.axes.clear()
        self.axes.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
        self.axes.set_title(title)
        self.axes.axis("equal")
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def plot_histogram(self, values: Sequence, title="", xlabel="", ylabel="Frequency"):
        self.axes.clear()
        self.axes.hist(values, bins=10)
        self._finish_chart(title, xlabel, ylabel)
