"""Figures for the theory map: nested sampling and finite-temperature free energy.

Run from the repository root:  python3 knowledge/figs/make_figs_nested.py
Writes knowledge/figs/nested-sampling-volumes.svg. The left panel is a toy 2D energy
surface; the right panel uses the analytic 2D harmonic model U = r^2/2, not data for
any material. Set FIG_PREVIEW_DIR to also write PNG copies (outside the repository).
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


fig, axes = plt.subplots(1, 2, figsize=(10.0, 3.9))

# ---- left: nested energy shells and live points ----------------------------
ax = axes[0]
gx, gy = np.meshgrid(np.linspace(-2.6, 2.6, 400), np.linspace(-2.6, 2.6, 400))
U = 0.55 * ((gx - 0.6) ** 2 + 1.6 * (gy - 0.3) ** 2) + 0.35 * ((gx + 1.0) ** 2 + 0.7 * (gy + 0.9) ** 2)
levels = np.linspace(0.15, 3.2, 9)
cs = ax.contour(gx, gy, U, levels=levels, colors=GREY, linewidths=1.0)
ax.clabel(cs, inline=True, fontsize=7, fmt="%.1f")
rng = np.random.default_rng(3)
theta = rng.uniform(0, 2 * np.pi, 26)
rad = np.sqrt(rng.uniform(0.55, 1.0, 26))
ax.scatter(0.6 + 0.55 * rad * np.cos(theta), 0.3 + 0.44 * rad * np.sin(theta), s=16, color=ORANGE,
           zorder=3, label="活点（当前能量上限以内）")
ax.scatter(0.6, 0.3, s=40, color=RED, zorder=4, label="最低能处")
ax.set_xlim(-2.6, 2.6)
ax.set_ylim(-2.6, 2.6)
ax.set_aspect("equal")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("能量等值面与活点（示意）")
ax.legend(frameon=False, fontsize=8.5, loc="lower left")

# ---- right: X vs exp(-beta U) ---------------------------------------------
ax = axes[1]
X = np.linspace(1e-4, 1.0 - 1e-3, 600)
# 2D harmonic toy: U(X) with prior volume X = pi r^2 / (pi R^2) -> U = -ln(1 - X) scaled
# Use U(X) = -2 ln(1 - X) / beta0 with beta0 = 1 to make a monotone example.
UofX = -2.0 * np.log1p(-X)
for beta, c, lab in ((0.6, BLUE, "β = 0.6"), (1.4, RED, "β = 1.4")):
    L = np.exp(-beta * UofX)
    ax.plot(X, L, color=c, lw=1.9, label=lab)
    ax.fill_between(X, 0, L, color=c, alpha=0.16)
ax.set_xlabel("先验体积 X（能量从高到低累计的体积分数）")
ax.set_ylabel(r"$e^{-\beta U(X)}$")
ax.set_title("把配分函数变成一维积分（示意）")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1.02)
ax.legend(frameon=False, fontsize=9)

fig.tight_layout()
save(fig, "nested-sampling-volumes")
