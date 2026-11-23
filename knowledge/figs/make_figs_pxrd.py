"""Figures for the theory map: powder-diffraction-guided structure solution.

Run from the repository root:  python3 knowledge/figs/make_figs_pxrd.py
Writes knowledge/figs/pxrd-pattern-fit.svg. Peak positions, intensities and widths are
made up to look like a profile fit; this is a sketch, not data for any material.
Set FIG_PREVIEW_DIR to also write PNG copies (outside the repository) for checking.
"""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

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
INK = "#212529"


def save(fig, name):
    fig.savefig(OUT / f"{name}.svg", format="svg", bbox_inches="tight", metadata={"Date": None})
    preview = os.environ.get("FIG_PREVIEW_DIR")
    if preview:
        fig.savefig(Path(preview) / f"{name}.png", dpi=110, bbox_inches="tight")
    plt.close(fig)


def peak(x, mu, amp, fwhm=0.20):
    s = fwhm / 2.3548
    return amp * np.exp(-0.5 * ((x - mu) / s) ** 2)


positions = np.array([8.1, 11.6, 13.2, 15.1, 16.8, 18.4, 19.7, 21.3, 23.0, 24.4, 26.2, 27.9])
intens = np.array([0.92, 0.35, 0.70, 0.24, 0.52, 0.80, 0.30, 0.46, 0.60, 0.20, 0.36, 0.26])
x = np.linspace(6.0, 30.0, 2400)


def pattern(pos, amp, shift=0.0):
    y = np.zeros_like(x)
    for p, a in zip(pos, amp):
        y += peak(x, p + shift, a)
    return y


observed = pattern(positions, intens) + 0.012
calc_good = pattern(positions, intens)
calc_bad = pattern(positions * 1.008, intens[::-1] * 0.9 + 0.05, shift=0.04)

fig, axes = plt.subplots(1, 2, figsize=(10.0, 3.7))

ax = axes[0]
ax.plot(x, observed, color=INK, lw=1.2)
for p, a in zip(positions, intens):
    ax.vlines(p, -0.06, -0.02, color=GREY, lw=1.0)
    ax.text(p, -0.115, f"{int(round(p))}", ha="center", va="top", fontsize=8, color=GREY)
ax.set_xlabel("2θ（度）")
ax.set_ylabel("强度")
ax.set_title("实验粉末图（示意）：峰位与强度可读出，三维信息丢失")
ax.set_ylim(-0.16, 1.05)
ax.set_yticks([])

ax = axes[1]
ax.plot(x, observed, color=INK, lw=2.4, alpha=0.25, label="实验")
ax.plot(x, calc_good, color=BLUE, lw=1.4, label="候选 A：峰位与强度都对上")
ax.plot(x, calc_bad, color=RED, lw=1.1, ls="--", label="候选 B：部分峰位、强度不符")
ax.set_xlabel("2θ（度）")
ax.set_ylabel("强度")
ax.set_title("把候选结构的模拟粉末图与实验比较（示意）")
ax.set_ylim(-0.02, 1.12)
ax.set_yticks([])
ax.legend(frameon=False, fontsize=8.5, loc="upper right")

fig.tight_layout()
save(fig, "pxrd-pattern-fit")
