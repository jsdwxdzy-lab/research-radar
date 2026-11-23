"""Figures for the theory map: generative models (batch 2026-11-23).

Run from the repository root:  python3 knowledge/figs/make_figs_genmodels.py
Writes knowledge/figs/generative-families.svg and knowledge/figs/crystal-unit-cell.svg.
All panels are schematic: toy point clouds and a 2D lattice drawn to show an idea.
Set FIG_PREVIEW_DIR to also write PNG copies (outside the repository) for checking.
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
INK = "#212529"


def save(fig, name):
    fig.savefig(OUT / f"{name}.svg", format="svg", bbox_inches="tight", metadata={"Date": None})
    preview = os.environ.get("FIG_PREVIEW_DIR")
    if preview:
        fig.savefig(Path(preview) / f"{name}.png", dpi=110, bbox_inches="tight")
    plt.close(fig)


def arrow(ax, xy0, xy1, color=GREY, lw=1.0, alpha=0.8, ms=10):
    ax.add_patch(FancyArrowPatch(xy0, xy1, arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw, alpha=alpha,
                                 shrinkA=0, shrinkB=0))


# ---- figure 1: three generative families -----------------------------------
fig, axes = plt.subplots(1, 3, figsize=(10.6, 3.6), sharex=True, sharey=True)
rng = np.random.default_rng(11)
t = np.linspace(0, np.pi, 200)
band_x = 1.6 * np.cos(t)
band_y = 0.55 * np.sin(t) + 0.25 * np.sin(3 * t)

for ax in axes:
    ax.plot(band_x, band_y, color=INK, lw=4.0, alpha=0.18, solid_capstyle="round")
    ax.set_xlim(-2.6, 2.6)
    ax.set_ylim(-2.4, 2.4)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")
    ax.set_xlabel("结构空间")

# (a) autoregressive: stepwise addition along the band
ax = axes[0]
idx = np.linspace(6, len(t) - 7, 7).astype(int)
pts = np.stack([band_x[idx], band_y[idx]], axis=1)
for k, (x0, y0) in enumerate(pts):
    ax.scatter([x0], [y0], s=60, color=BLUE, zorder=3)
    ax.text(x0, y0 + 0.18, str(k + 1), ha="center", fontsize=9, color=INK)
for k in range(len(pts) - 1):
    arrow(ax, pts[k], pts[k + 1], color=BLUE, lw=1.2)
ax.set_title("自回归：逐项写出结构")

# (b) diffusion: curved paths from noise to data
ax = axes[1]
noise = rng.normal(loc=[0.0, -1.55], scale=0.28, size=(12, 2))
target = np.stack([rng.uniform(-1.5, 1.5, 12), rng.uniform(-0.4, 0.7, 12)], axis=1)
ax.scatter(noise[:, 0], noise[:, 1], s=18, color=RED, alpha=0.8)
ax.scatter(target[:, 0], target[:, 1], s=18, color=BLUE)
for (nx, ny), (tx, ty) in zip(noise, target):
    s = np.linspace(0, 1, 40)
    xs = nx + (tx - nx) * s + 0.18 * np.sin(np.pi * s) * (1 if tx > nx else -1)
    ys = ny + (ty - ny) * s + 0.10 * np.sin(np.pi * s)
    ax.plot(xs, ys, color=GREY, lw=0.8, alpha=0.5)
ax.set_title("扩散：从噪声沿弯曲路径回到数据")

# (c) flow matching: straight paths
ax = axes[2]
ax.scatter(noise[:, 0], noise[:, 1], s=18, color=RED, alpha=0.8)
ax.scatter(target[:, 0], target[:, 1], s=18, color=BLUE)
for (nx, ny), (tx, ty) in zip(noise, target):
    arrow(ax, (nx, ny), (tx, ty), color=ORANGE, lw=0.9, alpha=0.6, ms=8)
ax.set_title("流匹配：沿直线运到数据")

fig.suptitle("（示意）三条生成路线：自回归逐步写出、扩散弯曲路径、流匹配直线路径；带状区域为数据分布", y=1.02,
             fontsize=11)
fig.tight_layout()
save(fig, "generative-families")

# ---- figure 2: 2D unit cell -------------------------------------------------
fig, ax = plt.subplots(figsize=(5.4, 4.6))
a1 = np.array([1.55, 0.0])
a2 = np.array([0.55, 1.2])
frac = np.array([[0.18, 0.22], [0.62, 0.38], [0.40, 0.72]])
colors = [BLUE, GREEN, ORANGE]

for i in (-1, 0, 1):
    for j in (-1, 0, 1):
        shift = i * a1 + j * a2
        pts = frac @ np.array([a1, a2]) + shift
        alpha = 1.0 if (i == 0 and j == 0) else 0.22
        for p, c in zip(pts, colors):
            ax.scatter(p[0], p[1], s=70, color=c, alpha=alpha, edgecolor="none", zorder=2)
        if i == 0 and j == 0:
            poly = np.array([[0, 0], a1, a1 + a2, a2, [0, 0]])
            ax.plot(poly[:, 0], poly[:, 1], color=INK, lw=1.2)
        else:
            poly = np.array([[0, 0], a1, a1 + a2, a2, [0, 0]]) + shift
            ax.plot(poly[:, 0], poly[:, 1], color=GREY, lw=0.8, ls="--", alpha=0.5)

arrow(ax, (0, 0), a1, color=BLUE, lw=2.0, alpha=1, ms=14)
arrow(ax, (0, 0), a2, color=GREEN, lw=2.0, alpha=1, ms=14)
ax.text(a1[0] / 2 + 0.05, -0.18, r"$\mathbf{a}_1$", color=BLUE, fontsize=13)
ax.text(a2[0] / 2 - 0.18, a2[1] / 2 + 0.10, r"$\mathbf{a}_2$", color=GREEN, fontsize=13)
ax.annotate(r"$\beta$", xy=(0, 0), xytext=(0.30, 0.12), fontsize=13, color=INK)
ax.text(frac[0, 0] * a1[0] + frac[0, 1] * a2[0] - 0.02, frac[0, 0] * a1[1] + frac[0, 1] * a2[1] + 0.14,
        r"$\mathbf{x}_j$", fontsize=12, color=BLUE)
ax.set_xlim(-0.7, 2.9)
ax.set_ylim(-0.5, 2.5)
ax.set_aspect("equal")
ax.set_xticks([])
ax.set_yticks([])
ax.set_title("（示意）晶格基矢与分数坐标；虚线是周期镜像")
fig.tight_layout()
save(fig, "crystal-unit-cell")
