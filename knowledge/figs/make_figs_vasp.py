"""Figures for the theory map (VASP workflow in CSPpipeline, batch 5).

Run from the repository root:  python3 knowledge/figs/make_figs_vasp.py
Writes knowledge/figs/<name>.svg. The workflow and band-tilt figures are schematic. The smearing, relaxation and
fluctuation figures evaluate textbook formulas or toy models for real; they are not data for any material.
Set FIG_PREVIEW_DIR to also write PNG copies.
"""
from __future__ import annotations

import math
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch  # noqa: E402

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


def arrow(ax, x0, y0, x1, y1, color="k", lw=1.4, ms=12):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw,
                                 shrinkA=0, shrinkB=0))


# ---------------------------------------------------------------------------
def fig_workflow():
    """Schematic: the four VASP stages, what each outputs, and where D3 is (not) included."""
    fig, ax = plt.subplots(figsize=(10.4, 5.2))
    ax.set_xlim(0, 10.4)
    ax.set_ylim(0, 5.2)
    ax.axis("off")
    boxes = [
        (0.2, 3.3, "① 变胞优化", "ISIF=3, IBRION=2\nENCUT=800, D3 零阻尼", "平衡结构\n(力、应力≈0)", BLUE, True),
        (2.8, 3.3, "② 有限差分", "IBRION=6, ISIF=3\nNFREE=2, POTIM=0.01", r"$\bar C$, $C$, 力常数 $K$" + "\n内应变 Λ", GREEN, True),
        (5.4, 3.3, "③ 微扰 DFPT", "IBRION=8\nLEPSILON=.TRUE.", r"$\varepsilon^\infty$, $Z^*$, $\bar e$" + "\n力常数 $K$", ORANGE, False),
        (8.0, 3.3, "④ 合成", "calc_piezo_dij.py", r"$e=\bar e+\Omega^{-1}Z^*K^{-1}\Lambda$" + "\n" + r"$d=e\,C^{-1}$", GREY, None),
    ]
    w, h = 2.2, 1.7
    for x, y, title, tags, out, col, d3 in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04", fc="white", ec=col, lw=1.8))
        ax.text(x + w / 2, y + h - 0.25, title, ha="center", va="center", fontsize=12, color=col, weight="bold")
        ax.text(x + w / 2, y + h - 0.75, tags, ha="center", va="center", fontsize=9)
        ax.text(x + w / 2, y - 0.55, out, ha="center", va="center", fontsize=10)
        if d3 is True:
            ax.text(x + w - 0.1, y + 0.12, "含 D3", ha="right", va="bottom", fontsize=9, color=GREEN)
        elif d3 is False:
            ax.text(x + w - 0.1, y + 0.12, "不含 D3", ha="right", va="bottom", fontsize=9, color=RED, weight="bold")
    for x in (2.4, 5.0, 7.6):
        arrow(ax, x + 0.02, 4.15, x + 0.38, 4.15)
    # cross-check branch
    ax.add_patch(FancyBboxPatch((2.8, 0.25), 4.8, 1.25, boxstyle="round,pad=0.04", fc="#f8f9fa", ec=GREY, lw=1.2,
                                ls="--"))
    ax.text(5.2, 1.12, "交叉检查：固定小应变 η，ISIF=2 只弛豫离子（含 D3）", ha="center", fontsize=10)
    ax.text(5.2, 0.62, r"LCALCPOL 算 Berry 相极化 $P(\eta)$  →  $e\approx\Delta P/\Delta\eta$", ha="center", fontsize=10)
    arrow(ax, 1.3, 2.3, 2.75, 1.0, color=GREY, lw=1.1)
    arrow(ax, 7.65, 0.9, 9.0, 2.15, color=GREY, lw=1.1)
    ax.text(8.55, 1.15, "比较 $e$", fontsize=9, color=GREY)
    return fig


def fig_smearing():
    """Occupation functions vs (ε-μ)/σ, and their 'density' -df/dx (real formulas)."""
    x = np.linspace(-4, 4, 801)
    fd = 1 / (np.exp(x) + 1)
    gauss = 0.5 * np.array([math.erfc(v) for v in x])
    # Methfessel–Paxton N=1: f = f0 + A1 H1(x) exp(-x^2), A1 = -1/(4 sqrt(pi)), H1 = 2x
    mp1 = gauss + (-1 / (4 * math.sqrt(math.pi))) * (2 * x) * np.exp(-x ** 2)
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.7))
    ax = axes[0]
    ax.plot(x, fd, color=GREY, lw=1.8, label="Fermi–Dirac")
    ax.plot(x, gauss, color=BLUE, lw=1.8, label="Gaussian (ISMEAR=0)")
    ax.plot(x, mp1, color=RED, lw=1.8, ls="--", label="Methfessel–Paxton N=1 (ISMEAR=1)")
    ax.axhline(0, color="k", lw=0.6)
    ax.axhline(1, color="k", lw=0.6, ls=":")
    ax.set_xlabel(r"$(\varepsilon-\mu)/\sigma$")
    ax.set_ylabel(r"占据数 $f$")
    ax.set_title("(a) 占据函数", loc="left", fontsize=11)
    ax.legend(fontsize=8.5, frameon=False, loc="lower left")
    ax.annotate("f > 1", xy=(-0.9, mp1[np.argmax(mp1)]), xytext=(-3.3, 1.12), fontsize=9, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED))
    ax.set_ylim(-0.15, 1.2)
    ax = axes[1]
    # insulator: VB top at -g/2, CB bottom at +g/2, gap g in units of sigma
    ax.plot(x, gauss, color=BLUE, lw=1.8)
    for g, col, y, txt in ((6.0, BLUE, 0.80, "带隙 = 6σ：价带满、导带空"), (1.0, ORANGE, 0.45, "带隙 = σ：导带被部分占据")):
        ax.axvline(-g / 2, color=col, lw=1, ls=":")
        ax.axvline(g / 2, color=col, lw=1, ls=":")
        ax.annotate("", xy=(g / 2, y), xytext=(-g / 2, y), arrowprops=dict(arrowstyle="<->", color=col))
        ax.text(0, y + 0.04, txt, ha="center", va="bottom", fontsize=9, color=col,
                bbox=dict(fc="white", ec="none", pad=1))
    ax.set_xlabel(r"$(\varepsilon-\mu)/\sigma$")
    ax.set_title("(b) 绝缘体：带隙远大于 σ 时展宽不起作用", loc="left", fontsize=11)
    ax.set_ylim(-0.05, 1.1)
    return fig


def fig_band_tilt():
    """Schematic: band edges tilted by a uniform field; tunnelling length L = Eg/(eE)."""
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    xs = np.linspace(0, 10, 50)
    slope = -0.35
    vb = 0 + slope * xs
    cb = 2.0 + slope * xs
    ax.fill_between(xs, vb - 1.2, vb, color=BLUE, alpha=0.18)
    ax.fill_between(xs, cb, cb + 1.2, color=RED, alpha=0.15)
    ax.plot(xs, vb, color=BLUE, lw=2, label="价带顶")
    ax.plot(xs, cb, color=RED, lw=2, label="导带底")
    x0 = 2.0
    L = 2.0 / -slope
    ax.annotate("", xy=(x0 + L, vb[0] + slope * x0), xytext=(x0, vb[0] + slope * x0),
                arrowprops=dict(arrowstyle="<->", color="k"))
    ax.text(x0 + L / 2, slope * x0 + 0.15, r"$L = E_g/(eE)$", ha="center", fontsize=11)
    ax.annotate("", xy=(x0, 2.0 + slope * x0), xytext=(x0, slope * x0), arrowprops=dict(arrowstyle="<->", color=GREY))
    ax.text(x0 - 0.15, 1.0 + slope * x0, r"$E_g$", ha="right", fontsize=11, color=GREY)
    ax.annotate("", xy=(9.5, 0.4), xytext=(6.5, 0.4), arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.6))
    ax.text(8.0, 0.55, r"外加电场 $E$", ha="center", color=GREEN, fontsize=10)
    ax.annotate("", xy=(10.0, -4.6), xytext=(0.0, -4.6), arrowprops=dict(arrowstyle="<->", color=ORANGE))
    ax.text(5.0, -4.45, r"k 点串对应的实空间长度 $N_k a$", ha="center", color=ORANGE, fontsize=10)
    ax.set_xlabel("位置 x（沿电场方向）")
    ax.set_ylabel("电子能量")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_ylim(-5.0, 3.6)
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    return fig


def fig_relax():
    """Toy anisotropic quadratic surface: steepest descent vs conjugate gradient; force/energy stop criteria."""
    A = np.array([[1.0, 0.0], [0.0, 25.0]])  # soft (molecular rotation) and stiff (bond) directions
    x0 = np.array([-2.6, 0.55])

    def grad(p):
        return A @ p

    def energy(p):
        return 0.5 * p @ A @ p

    # steepest descent with exact line search
    sd = [x0.copy()]
    p = x0.copy()
    for _ in range(40):
        g = grad(p)
        a = (g @ g) / (g @ A @ g)
        p = p - a * g
        sd.append(p.copy())
    sd = np.array(sd)
    # linear CG
    cg = [x0.copy()]
    p = x0.copy()
    r = -grad(p)
    d = r.copy()
    for _ in range(2):
        a = (r @ r) / (d @ A @ d)
        p = p + a * d
        rn = r - a * (A @ d)
        d = rn + (rn @ rn) / (r @ r) * d
        r = rn
        cg.append(p.copy())
    cg = np.array(cg)
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 3.9), gridspec_kw={"width_ratios": [1.2, 1]})
    ax = axes[0]
    X, Y = np.meshgrid(np.linspace(-3, 1, 200), np.linspace(-0.8, 0.8, 200))
    Z = 0.5 * (A[0, 0] * X ** 2 + A[1, 1] * Y ** 2)
    ax.contour(X, Y, Z, levels=np.geomspace(0.02, 6, 12), colors=GREY, linewidths=0.6)
    ax.plot(sd[:, 0], sd[:, 1], "-o", color=RED, ms=2.5, lw=1, label="最速下降（逐步之字形）")
    ax.plot(cg[:, 0], cg[:, 1], "-s", color=BLUE, ms=5, lw=1.8, label="共轭梯度（二次面上 2 步）")
    ax.plot(0, 0, "k*", ms=10)
    ax.set_xlabel("软方向（如分子转动）")
    ax.set_ylabel("硬方向（如键长）")
    ax.set_title("(a) 各向异性能量面上的优化路径", loc="left", fontsize=11)
    ax.legend(fontsize=8.5, frameon=False, loc="lower right")
    ax = axes[1]
    fmax = np.array([np.max(np.abs(grad(q))) for q in sd])
    de = np.abs(np.diff([energy(q) for q in sd]))
    steps = np.arange(len(sd))
    ax.semilogy(steps, fmax, color=RED, lw=1.8, label="最大力 |F|")
    ax.semilogy(steps[1:], de, color=GREEN, lw=1.8, ls="--", label="相邻步能量差 |ΔE|")
    ax.axhline(5e-3, color=RED, lw=0.9, ls=":")
    ax.text(40, 6.2e-3, "力判据", ha="right", va="bottom", fontsize=9, color=RED)
    ax.axhline(1e-3, color=GREEN, lw=0.9, ls=":")
    ax.text(40, 0.85e-3, "能量判据", ha="right", va="top", fontsize=9, color=GREEN)
    ax.set_xlabel("离子步（最速下降）")
    ax.set_title("(b) 能量先满足判据，力还没有", loc="left", fontsize=11)
    ax.legend(fontsize=8.5, frameon=False, loc="upper right")
    return fig


def fig_fluctuation():
    """Toy Gaussian (strain, polarization) samples: covariance ellipse and error vs trajectory length."""
    rng = np.random.default_rng(7)
    cov = np.array([[1.0, 0.35], [0.35, 1.0]])
    n = 600
    s = rng.multivariate_normal([0, 0], cov, size=n)
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9))
    ax = axes[0]
    ax.scatter(s[:, 0], s[:, 1], s=3, color=GREY, alpha=0.35, lw=0)
    vals, vecs = np.linalg.eigh(cov)
    ang = math.degrees(math.atan2(vecs[1, 1], vecs[0, 1]))
    for k in (1, 2):
        ax.add_patch(Ellipse((0, 0), 2 * k * math.sqrt(vals[1]), 2 * k * math.sqrt(vals[0]), angle=ang, fill=False,
                             ec=BLUE, lw=1.4))
    xx = np.linspace(-3, 3, 10)
    ax.plot(xx, 0.35 * xx, color=RED, lw=1.8, label=r"回归斜率 = Cov/Var")
    ax.set_xlabel(r"应变涨落 $\delta\eta$（标准化）")
    ax.set_ylabel(r"极化涨落 $\delta P$（标准化）")
    ax.set_title("(a) 涨落样本与协方差椭圆（玩具数据）", loc="left", fontsize=11)
    ax.legend(fontsize=9, frameon=False, loc="upper left")
    ax.set_aspect("equal")
    ax.set_xlim(-3.6, 3.6)
    ax.set_ylim(-3.6, 3.6)
    ax = axes[1]
    neff = np.geomspace(20, 2e4, 60)
    rho = 0.35
    se = np.sqrt((1 + rho ** 2) / neff)  # std. error of a sample covariance for bivariate normal
    ax.loglog(neff, se, color=BLUE, lw=1.8, label="协方差的标准误")
    ax.axhline(rho, color=RED, lw=1, ls="--", label="协方差本身 (0.35)")
    ax.axhline(0.1 * rho, color=RED, lw=0.9, ls=":", label="10% 相对误差")
    ax.set_xlabel(r"独立样本数 $N_{\mathrm{eff}}$")
    ax.set_title(r"(b) 误差 $\propto 1/\sqrt{N_{\mathrm{eff}}}$", loc="left", fontsize=11)
    ax.legend(fontsize=8.5, frameon=False, loc="lower left")
    return fig


if __name__ == "__main__":
    save(fig_workflow(), "vasp-workflow")
    save(fig_smearing(), "smearing-occupations")
    save(fig_band_tilt(), "finite-field-band-tilt")
    save(fig_relax(), "relax-paths")
    save(fig_fluctuation(), "fluctuation-covariance")
