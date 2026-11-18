"""Figures for theory-harvest 2026-11-18 drafts.

Run: MPLCONFIGDIR=/tmp/mpl-xxx python3 knowledge/figs/make_figs_harvest_20261118.py
Schematic only; not data for any material.
"""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyArrowPatch  # noqa: E402

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
    preview = os.environ.get("FIG_PREVIEW_DIR")
    if preview:
        fig.savefig(Path(preview) / f"{name}.png", dpi=110, bbox_inches="tight")
    plt.close(fig)


def arrow(ax, x0, y0, x1, y1, color="k", lw=1.4, style="-|>", ms=10):
    ax.add_patch(
        FancyArrowPatch(
            (x0, y0), (x1, y1), arrowstyle=style, mutation_scale=ms,
            color=color, lw=lw, shrinkA=0, shrinkB=0,
        )
    )


def fig_imag_mode_projection():
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.4), sharey=True)
    eigs = np.array([-0.8, -0.25, 0.0, 0.0, 0.0, 0.4, 1.1, 1.6, 2.2])
    for ax, keep_neg, title in [
        (axes[0], True, "完整谱（含虚模）"),
        (axes[1], False, "丢掉 λ<0 后重建响应"),
    ]:
        ax.axhline(0, color=GREY, lw=1)
        ax.set_xlim(-0.5, len(eigs) - 0.5)
        ax.set_ylim(-1.2, 2.6)
        ax.set_xticks([])
        if ax is axes[0]:
            ax.set_ylabel("力常数本征值 λ")
        ax.set_title(title, fontsize=11)
        for i, lam in enumerate(eigs):
            if (not keep_neg) and lam < 0:
                ax.plot([i, i], [0, lam], color=GREY, lw=1.2, ls=":")
                ax.plot(i, lam, "o", color=GREY, ms=6)
                ax.text(i, lam - 0.18, "丢掉", color=GREY, ha="center", fontsize=8)
                continue
            color = RED if lam < 0 else (GREY if abs(lam) < 1e-9 else BLUE)
            ax.plot([i, i], [0, lam], color=color, lw=2.2)
            ax.plot(i, lam, "o", color=color, ms=6)
        if keep_neg:
            ax.text(0.5, -1.05, "虚模 λ<0", color=RED, fontsize=9)
            ax.text(6.2, 2.25, "稳定光学模", color=BLUE, fontsize=9)
        else:
            ax.text(5.2, 2.25, "只对正本征值求逆", color=BLUE, fontsize=9)
            ax.annotate(
                "平移零模保留为 0",
                xy=(2, 0.05),
                xytext=(3.2, 0.9),
                fontsize=8,
                color=GREY,
                arrowprops=dict(arrowstyle="->", color=GREY, lw=0.8),
            )
    fig.suptitle("示意：用 K$^{-1}$ 重建离子响应时如何对待虚模", fontsize=12, y=1.02)
    save(fig, "imag-mode-projection")


def fig_cross_hamiltonian_reopt():
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    ax.set_xlim(-0.2, 6.2)
    ax.set_ylim(-0.3, 3.2)
    ax.axis("off")

    x = np.linspace(0.3, 5.8, 400)
    ya = 0.55 * (x - 2.0) ** 2 + 0.35
    yb = 0.45 * (x - 3.3) ** 2 + 0.55
    ax.plot(x, ya, color=BLUE, lw=2.0, label="哈密顿量 A 的能量")
    ax.plot(x, yb, color=ORANGE, lw=2.0, label="哈密顿量 B 的能量")
    ax.plot(2.0, 0.35, "o", color=BLUE, ms=8)
    ax.plot(3.3, 0.55, "o", color=ORANGE, ms=8)
    y_start_on_B = 0.55 + 0.45 * (2.0 - 3.3) ** 2
    ax.plot(2.0, y_start_on_B, "s", color=GREEN, ms=7)
    arrow(ax, 2.0, y_start_on_B, 3.15, 0.62, color=GREEN, lw=1.6)
    ax.text(2.0, 0.12, "A 的极小\n(起始结构)", color=BLUE, ha="center", fontsize=9)
    ax.text(3.3, 0.12, "B 的极小\n(再优化终点)", color=ORANGE, ha="center", fontsize=9)
    ax.text(2.55, 1.55, "在 B 上再优化", color=GREEN, fontsize=10)
    ax.text(0.4, 2.85, "横轴：某一结构坐标（示意，如体积或剪切）", color=GREY, fontsize=9)
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    ax.set_title("示意：换哈密顿量后，原极小不再是极小", fontsize=12)
    save(fig, "cross-hamiltonian-reopt")


if __name__ == "__main__":
    fig_imag_mode_projection()
    fig_cross_hamiltonian_reopt()
    print("wrote imag-mode-projection.svg, cross-hamiltonian-reopt.svg")
