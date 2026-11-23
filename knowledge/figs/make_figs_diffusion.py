"""Figures for the theory map: diffusion models and flow matching.

Run from the repository root:  python3 knowledge/figs/make_figs_diffusion.py
Writes knowledge/figs/diffusion-interpolants.svg. The data are a toy 1D two-component
mixture chosen to show the idea; nothing here is data for any material.
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


def gauss(x, mu, s):
    return np.exp(-0.5 * ((x - mu) / s) ** 2) / (s * np.sqrt(2 * np.pi))


fig, axes = plt.subplots(1, 2, figsize=(9.8, 3.7))

# ---- left: marginal distributions along the interpolation -------------------
ax = axes[0]
x = np.linspace(-3.8, 3.8, 900)
mus = np.array([-1.25, 1.25])
weights = np.array([0.55, 0.45])
s0 = 0.22
ts = [0.0, 0.25, 0.5, 0.75, 1.0]
colors = [INK, BLUE, GREEN, ORANGE, RED]
for t, c in zip(ts, colors):
    a = np.cos(np.pi * t / 2)
    sg = np.sin(np.pi * t / 2)
    p = sum(w * gauss(x, a * mu, np.sqrt(a**2 * s0**2 + sg**2)) for w, mu in zip(weights, mus))
    ax.plot(x, p, color=c, lw=1.9, label=f"t = {t:g}")
ax.set_xlabel("x")
ax.set_ylabel("p_t(x)")
ax.set_title("插值分布 p_t（VP 调度，示意）")
ax.set_yticks([])
ax.legend(frameon=False, fontsize=9, loc="upper right")
ax.set_xlim(-3.8, 3.8)
ax.set_ylim(0, 1.1)

# ---- right: sample trajectories --------------------------------------------
ax = axes[1]
rng = np.random.default_rng(7)
n = 16
eps = rng.normal(size=n)
x0 = np.where(rng.random(n) < 0.55, -1.25 + 0.22 * rng.normal(size=n), 1.25 + 0.22 * rng.normal(size=n))
tt = np.linspace(0, 1, 200)
for i in range(n):
    a = np.cos(np.pi * tt / 2)
    sg = np.sin(np.pi * tt / 2)
    ax.plot(a * x0[i] + sg * eps[i], tt, color=GREY, lw=0.9, alpha=0.55)
ax.scatter(x0, np.zeros(n), s=22, color=BLUE, zorder=3, label="数据样本 x_0")
ax.scatter(eps, np.ones(n), s=22, color=RED, zorder=3, label="噪声 ε")
ax.set_xlabel("x")
ax.set_ylabel("t")
ax.set_title("样本轨迹 x_t = α_t x_0 + σ_t ε（示意）")
ax.set_ylim(-0.04, 1.04)
ax.set_xlim(-3.8, 3.8)
ax.legend(frameon=False, fontsize=9, loc="upper right")

fig.tight_layout()
save(fig, "diffusion-interpolants")
