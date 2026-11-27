"""Figures for theory harvest 20261127.

Run: MPLCONFIGDIR=/tmp/mpl-20261127 python3 knowledge/figs/make_figs_harvest_20261127.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = Path(__file__).resolve().parent
plt.rcParams.update({
    "font.family": "Arial Unicode MS",
    "mathtext.fontset": "stix",
    "svg.fonttype": "path",
    "svg.hashsalt": "theory-map",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})
BLUE, RED, GREY, GREEN, ORANGE = "#3b5bdb", "#e03131", "#868e96", "#2b8a3e", "#e8590c"


def save(fig, name):
    fig.savefig(OUT / f"{name}.svg", format="svg", bbox_inches="tight", metadata={"Date": None})
    plt.close(fig)


def fig_near_cancellation():
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.add_patch(Rectangle((1.2, 1.0), 1.6, 4.0, facecolor=BLUE, alpha=0.85, edgecolor="k", lw=0.8))
    ax.add_patch(Rectangle((4.0, 1.0), 1.6, 3.7, facecolor=ORANGE, alpha=0.85, edgecolor="k", lw=0.8))
    ax.add_patch(Rectangle((7.2, 1.0), 1.6, 0.35, facecolor=GREEN, alpha=0.9, edgecolor="k", lw=0.8))
    ax.text(2.0, 5.2, r"$\bar C$", ha="center", fontsize=13)
    ax.text(4.8, 5.0, r"$\Lambda K^{-1}\Lambda/\Omega$", ha="center", fontsize=11)
    ax.text(8.0, 1.7, r"$C$", ha="center", fontsize=13)
    ax.annotate("", xy=(3.9, 3.0), xytext=(2.9, 3.0), arrowprops=dict(arrowstyle="->", color=GREY, lw=1.5))
    ax.text(3.4, 3.35, "−", ha="center", fontsize=16, color=GREY)
    ax.annotate("", xy=(7.1, 1.2), xytext=(5.7, 2.8), arrowprops=dict(arrowstyle="->", color=GREY, lw=1.5))
    ax.text(5.0, 0.35, "示意：两项都很大、彼此接近，差出来的 C 很小", ha="left", fontsize=10, color=GREY)
    ax.text(1.2, 0.35, "夹持离子项", fontsize=9, color=BLUE)
    ax.text(4.0, 0.35, "离子弛豫项", fontsize=9, color=ORANGE)
    save(fig, "near-cancellation-elastic")


def fig_applied_stress():
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")
    ax.add_patch(Rectangle((1.0, 1.5), 2.2, 2.0, fill=False, edgecolor=BLUE, lw=1.5))
    ax.plot([2.1], [2.5], "o", color=RED, ms=8)
    ax.text(2.1, 3.7, r"$P^{(0)}$", ha="center", color=RED)
    ax.text(2.1, 1.1, "无外应力", ha="center", fontsize=10)
    ax.annotate("", xy=(4.6, 2.5), xytext=(3.5, 2.5), arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=2))
    ax.text(4.05, 2.9, r"$\sigma$", ha="center", color=ORANGE, fontsize=12)
    xs = [5.5, 8.0, 8.5, 6.0]
    ys = [1.5, 1.5, 3.5, 3.5]
    ax.fill(xs, ys, facecolor="none", edgecolor=GREEN, lw=1.5)
    ax.plot([7.0], [2.5], "o", color=RED, ms=8)
    ax.annotate("", xy=(7.9, 2.9), xytext=(7.0, 2.5), arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.5))
    ax.text(8.2, 3.2, r"$P(\sigma)$", color=RED, fontsize=11)
    ax.text(7.0, 1.05, "定应力弛豫后", ha="center", fontsize=10)
    ax.text(1.0, 4.5, r"示意：$d \sim \partial P/\partial\sigma$（Berry 相读极化差）", fontsize=11)
    save(fig, "applied-stress-berry-d")


if __name__ == "__main__":
    fig_near_cancellation()
    fig_applied_stress()
