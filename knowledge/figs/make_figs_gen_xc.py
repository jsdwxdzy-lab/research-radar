"""Figures for the theory map (batch: generative models, exchange-correlation functionals).

Run from the repository root:  python3 knowledge/figs/make_figs_gen_xc.py
Writes knowledge/figs/<name>.svg. Both figures are schematic.
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
BLUE, RED, GREY, GREEN, ORANGE, PURPLE = "#3b5bdb", "#e03131", "#868e96", "#2b8a3e", "#e8590c", "#7048e8"


def save(fig, name):
    fig.savefig(OUT / f"{name}.svg", format="svg", bbox_inches="tight", metadata={"Date": None})
    preview = os.environ.get("FIG_PREVIEW_DIR")
    if preview:
        fig.savefig(Path(preview) / f"{name}.png", dpi=110, bbox_inches="tight")
    plt.close(fig)


def trap(y, x):
    """Trapezoidal integral, independent of the numpy version."""
    return float(np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(x)))


def arrow(ax, x0, y0, x1, y1, color="k", lw=1.4, ms=12, style="-|>"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=ms, color=color, lw=lw,
                                 shrinkA=0, shrinkB=0))


# ---------------------------------------------------------------------------
# 1. Generative models: forward noising path and the learned reverse path
def fig_generative_skeleton():
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 3.8), gridspec_kw={"width_ratios": [1.25, 1.0]})

    # --- left: distributions along the forward path
    ax = axes[0]
    rng = np.random.default_rng(7)

    def blobs(scale, n, seed):
        r = np.random.default_rng(seed)
        c1 = np.array([-1.0, -0.35]) * scale
        c2 = np.array([0.9, 0.55]) * scale
        c3 = np.array([0.0, 0.9]) * scale
        return np.vstack([r.normal(c1, 0.22 + 0.5 * (1 - scale), size=(n, 2)),
                          r.normal(c2, 0.22 + 0.5 * (1 - scale), size=(n, 2)),
                          r.normal(c3, 0.18 + 0.5 * (1 - scale), size=(n, 2))])

    stages = [(1.0, 0.0), (0.62, 0.45), (0.28, 0.75), (0.0, 1.0)]
    cols = [RED, ORANGE, PURPLE, GREY]
    labels = ["$x_0$：数据", "$x_t$：中间", "$x_t$：噪声更大", "$x_1$：纯噪声"]
    xs = [-3.3, -1.1, 1.1, 3.3]
    for (sc, noise), col, lab, xc in zip(stages, cols, labels, xs):
        pts = blobs(max(sc, 0.0), 260, int(11 * noise) + 3) * (1.0 if sc > 0 else 1.0)
        pts = pts + rng.normal(0, noise * 1.25, size=pts.shape)
        ax.scatter(xs[xs.index(xc)] + (pts[:, 0] + 1.0) * 0.42, pts[:, 1] * 0.42, s=5, color=col, alpha=0.55,
                   linewidths=0)
        ax.text(xc, -1.75, lab, ha="center", fontsize=9, color=col)
    for x0, x1 in zip(xs[:-1], xs[1:]):
        arrow(ax, x0 + 0.55, 1.95, x1 - 0.55, 1.95, color=GREY, lw=1.6)
    ax.text(0.0, 2.25, "前向：固定加噪 $q(x_t\\mid x_{t-1})$（不学）", ha="center", fontsize=10, color=GREY)
    for x0, x1 in zip(xs[1:], xs[:-1]):
        arrow(ax, x0 - 0.55, -1.35, x1 + 0.55, -1.35, color=BLUE, lw=1.6)
    ax.text(0.0, -1.15, "反向：模型学 $p_\\theta(x_{t-1}\\mid x_t)$", ha="center", fontsize=10, color=BLUE)
    ax.set_xlim(-4.3, 4.3)
    ax.set_ylim(-2.1, 2.6)
    ax.axis("off")

    # --- right: sampling trajectory from noise back to data
    ax = axes[1]
    t = np.linspace(0, 1, 400)
    # toy velocity field: pull towards two attractors
    for sign, col in ((-1, BLUE), (1, GREEN)):
        x = sign * 1.35 * t ** 0.75 + 0.12 * np.sin(9 * t) * (1 - t)
        y = sign * 0.55 * t ** 0.75 + 0.10 * np.cos(7 * t) * (1 - t)
        ax.plot(x, y, color=col, lw=1.4, alpha=0.9)
        ax.scatter([x[-1]], [y[-1]], s=45, color=col, zorder=5)
    pts = rng.normal(0, 0.30, size=(90, 2))
    ax.scatter(pts[:, 0], pts[:, 1], s=12, color=GREY, alpha=0.6, linewidths=0)
    ax.text(0.0, -1.28, "$x_1$：从纯噪声出发", ha="center", fontsize=9, color=GREY)
    ax.text(1.35, -0.95, "$x_0$ 采样结果", ha="center", fontsize=9, color=GREEN)
    ax.set_xlim(-2.3, 2.3)
    ax.set_ylim(-1.5, 1.3)
    ax.set_title("采样：沿速度场走回去", fontsize=10.5)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ("left", "bottom"):
        ax.spines[s].set_visible(False)
    save(fig, "generative-model-skeleton")


# ---------------------------------------------------------------------------
# 2. Exchange-correlation functionals: the ladder
def fig_xc_ladder():
    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 9)
    ax.axis("off")

    rungs = [
        (7.5, "双杂化 (double hybrid)", "占据轨道 + 虚轨道", "Görling–Levy 微扰", "#f3d9fa"),
        (5.7, "杂化（含 HF 精确交换）", "$\\psi_i$（占据轨道）+ $\\rho$", "HSE / B3LYP", "#d0bfff"),
        (3.9, "meta-GGA", "$\\rho,\\ \\nabla\\rho,\\ \\tau$", "TPSS / SCAN", "#bac8ff"),
        (2.1, "GGA", "$\\rho,\\ \\nabla\\rho$", "PBE / PBEsol", "#a5d8ff"),
        (0.3, "LDA", "$\\rho$", "PW92", "#d3f9d8"),
    ]
    for y, name, ingredients, ex, col in rungs:
        ax.add_patch(plt.Rectangle((1.4, y), 7.2, 0.95, facecolor=col, edgecolor="#495057", lw=1.0))
        ax.text(1.65, y + 0.62, name, fontsize=11, va="center")
        ax.text(1.65, y + 0.22, ingredients, fontsize=9, color="#495057", va="center")
        ax.text(8.45, y + 0.47, ex, fontsize=8.6, color="#495057", ha="right", va="center")

    for y0, y1 in ((1.25, 2.1), (3.05, 3.9), (4.85, 5.7), (6.65, 7.5)):
        ax.plot([5.0, 5.0], [y0, y1], color="#495057", lw=1.2, ls=(0, (4, 3)))
    ax.text(5.0, 8.75, "信息逐渐增多 →", ha="center", fontsize=10, color=GREY)
    ax.annotate("", xy=(9.35, 8.1), xytext=(9.35, 1.0),
                arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.3, ls=":"))
    ax.text(9.6, 4.6, "代价与\n复杂性\n上升", fontsize=8.5, color=GREY, va="center")
    ax.text(5.0, -0.35, "每一级只用上一级的信息，外加一种新的半局域量", ha="center", fontsize=9.2, color="#495057")
    save(fig, "xc-functional-ladder")


# ---------------------------------------------------------------------------
# 3. Benchmarking: two error distributions with the same mean, different tails
def fig_benchmark_errors():
    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    x = np.linspace(0, 0.30, 600)
    # in-distribution: narrow gamma-like peak
    import math
    def gl(x, k, theta):
        return np.where(x > 0, x ** (k - 1) * np.exp(-x / theta) / (theta ** k * math.gamma(k)), 0.0)
    p_in = gl(x, 6.0, 0.0090)
    # out of distribution: same mean, heavier tail plus a small far-out bump
    p_ood = 0.86 * gl(x, 3.2, 0.0090) + 1.10 * np.exp(-((x - 0.235) ** 2) / (2 * 0.011 ** 2))
    p_in /= trap(p_in, x)
    p_ood /= trap(p_ood, x)

    ax.fill_between(x, 0, p_in, color="#a5d8ff", alpha=0.75)
    ax.plot(x, p_in, color=BLUE, lw=2.0, label="分布内测试集")
    ax.fill_between(x, 0, p_ood, color="#ffc9c9", alpha=0.75)
    ax.plot(x, p_ood, color=RED, lw=2.0, ls="--", label="分布外测试集（含长尾）")

    m_in = trap(x * p_in, x)
    m_ood = trap(x * p_ood, x)
    ax.axvline(m_in, color=BLUE, lw=1.1, ls=":")
    ax.axvline(m_ood, color=RED, lw=1.1, ls=":")
    ax.annotate("平均误差几乎相同", xy=(0.5 * (m_in + m_ood) + 0.004, 0.93 * max(p_in.max(), p_ood.max())),
                xytext=(0.105, 0.72 * max(p_in.max(), p_ood.max())), fontsize=9, color="#495057",
                arrowprops=dict(arrowstyle="-", color="#495057", lw=0.8))
    ax.annotate("长尾：少数构型上误差很大", xy=(0.235, 1.10), xytext=(0.140, 3.4),
                fontsize=9, color=RED, arrowprops=dict(arrowstyle="-", color=RED, lw=0.8))

    ax.set_xlabel("单次预测的能量误差 $|\\Delta E|$（示意，无量纲）")
    ax.set_ylabel("概率密度")
    ax.set_xlim(0, 0.30)
    ax.set_ylim(0, None)
    ax.legend(fontsize=9, frameon=False, loc="upper right")
    ax.set_title("平均误差相同，不代表失效方式相同", fontsize=10.5)
    save(fig, "benchmark-error-distribution")


if __name__ == "__main__":
    fig_generative_skeleton()
    fig_xc_ladder()
    fig_benchmark_errors()
    print("wrote:", OUT)
