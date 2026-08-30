"""Shared plot styling. Call apply_theme() once near the top of a notebook.

Font is Inter with a system sans-serif fallback chain — it only renders as
actual Inter if that font is installed on the machine; otherwise matplotlib
silently falls back to the next font in the stack. No auto-download.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns

PALETTE = ["#2A6F97", "#EE6C4D", "#3D9970", "#F4A259", "#7768AE", "#5C4742"]

FONT_STACK = ["Inter", "Helvetica Neue", "Arial", "sans-serif"]


def apply_theme(dpi: int = 150) -> None:
    sns.set_theme(style="whitegrid", palette=PALETTE)
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": FONT_STACK,
            "figure.dpi": dpi,
            "savefig.dpi": dpi,
            "axes.titleweight": "bold",
            "axes.edgecolor": "#333333",
        }
    )


def add_source_footnote(fig, source: str) -> None:
    """Repo-wide plot rule: every plot gets a 'Source: {data_source}' footnote."""
    fig.text(
        0.99,
        0.01,
        f"Source: {source}",
        ha="right",
        va="bottom",
        fontsize=8,
        color="#666666",
    )
