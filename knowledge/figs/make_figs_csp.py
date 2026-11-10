"""Figures for the theory map (crystal structure prediction, batch 4).

Run from the repository root:  python3 knowledge/figs/make_figs_csp.py
Writes knowledge/figs/<name>.svg. Landscape, pipeline and packing figures are schematic. The fingerprint, free-energy
and quasi-harmonic figures evaluate small model systems for real (toy lattices, Einstein oscillators, a model
equation of state); they are not data for any material. Set FIG_PREVIEW_DIR to also write PNG copies.
"""
from __future__ import annotations

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
def _pes(x, y):
    wells = [(-1.2, 0.3, 1.00, 0.55), (0.9, -0.4, 0.86, 0.45), (0.2, 1.3, 0.55, 0.35)]
    e = 0.06 * (x ** 2 + y ** 2)
    for cx, cy, depth, w in wells:
        e = e - depth * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * w ** 2))
    return e


def fig_energy_landscape():
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.0), gridspec_kw={"width_ratios": [1.05, 1]})
    ax = axes[0]
    x = np.linspace(-2.6, 2.4, 300)
    y = np.linspace(-1.8, 2.6, 300)
    X, Y = np.meshgrid(x, y)
    Z = _pes(X, Y)
    ax.contourf(X, Y, Z, levels=22, cmap="Blues_r", alpha=0.85)
    ax.contour(X, Y, Z, levels=22, colors="white", linewidths=0.4)
    # path between the two deepest wells, along the straight line (illustrative)
    t = np.linspace(0, 1, 200)
    px, py = -1.2 + 2.1 * t, 0.3 - 0.7 * t
    ax.plot(px, py, color=ORANGE, lw=1.6, ls="--")
    e_path = _pes(px, py)
    k = int(np.argmax(e_path[20:-20])) + 20
    ax.scatter([-1.2, 0.9, 0.2], [0.3, -0.4, 1.3], s=40, color="k", zorder=3)
    ax.scatter([px[k]], [py[k]], s=60, marker="x", color=RED, zorder=4, lw=2)
    ax.text(-1.2, 0.05, "A", ha="center", va="top", fontsize=12, color="k")
    ax.text(0.9, -0.65, "B", ha="center", va="top", fontsize=12, color="k")
    ax.text(0.2, 1.55, "C", ha="center", fontsize=12, color="k")
    ax.text(px[k] + 0.08, py[k] + 0.15, "鞍点", color=RED, fontsize=10)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("结构坐标 1")
    ax.set_ylabel("结构坐标 2")
    for s in ("top", "right"):
        ax.spines[s].set_visible(True)

    ax = axes[1]
    s = np.linspace(0, 1, 200)
    ax.plot(s, e_path, color=ORANGE, lw=2)
    eA, eB, eS = e_path[0], e_path[-1], e_path[k]
    ax.axhline(eA, color=GREY, lw=0.7, ls=":")
    ax.axhline(eB, color=GREY, lw=0.7, ls=":")
    ax.annotate("", xy=(0.06, eS), xytext=(0.06, eA), arrowprops=dict(arrowstyle="<->", color=RED, lw=1.0))
    ax.text(0.09, (eA + eS) / 2, r"势垒 $E^{\ddagger}$", color=RED, fontsize=10.5, va="center")
    ax.annotate("", xy=(0.95, eB), xytext=(0.95, eA), arrowprops=dict(arrowstyle="<->", color=BLUE, lw=1.0))
    ax.text(0.92, (eA + eB) / 2, r"$\Delta E_{\mathrm{AB}}$", color=BLUE, fontsize=11, va="center", ha="right")
    ax.text(0.0, eA - 0.04, "A", ha="center", va="top", fontsize=12)
    ax.text(1.0, eB - 0.04, "B", ha="center", va="top", fontsize=12)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("沿虚线路径")
    ax.set_ylabel("能量")
    save(fig, "energy-landscape-pes")


def fig_csp_pipeline():
    fig = plt.figure(figsize=(9.8, 4.2))
    ax = fig.add_axes([0.0, 0.0, 0.47, 1.0])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    steps = [
        (9.0, "生成候选结构", "随机 / 进化 / 生成模型", GREY, 9.4),
        (7.0, "快速能量模型预优化", "力场或 MLIP", BLUE, 7.8),
        (5.0, "去重与筛选", "相似度 + 能量窗口", BLUE, 6.0),
        (3.0, "DFT 精修与重排序", "例如 PBE-D3", ORANGE, 4.2),
        (1.0, "有限温度修正", "振动自由能", GREEN, 2.6),
    ]
    for y, lab, sub, col, w in steps:
        x0 = 5 - w / 2
        ax.add_patch(FancyBboxPatch((x0, y - 0.72), w, 1.44, boxstyle="round,pad=0.04", facecolor="white",
                                    edgecolor=col, lw=1.4))
        ax.text(5, y + 0.22, lab, ha="center", va="center", fontsize=10.5)
        ax.text(5, y - 0.33, sub, ha="center", va="center", fontsize=8.8, color=GREY)
    for y in (8.28, 6.28, 4.28, 2.28):
        arrow(ax, 5, y, 5, y - 0.55, GREY, lw=1.1, ms=10)
    ax.text(0.15, 5, "结构数逐级减少，\n每个结构的计算代价逐级增加", rotation=90, ha="center", va="center",
            fontsize=8.8, color=GREY)

    ax = fig.add_axes([0.56, 0.14, 0.42, 0.78])
    rng = np.random.default_rng(7)
    n = 160
    dens = rng.normal(1.0, 0.045, n)
    e = 6.0 * np.abs(rng.normal(0, 1, n)) + 25 * (1.0 - dens).clip(0, None) + rng.normal(0, 0.6, n)
    e = e - e.min()
    win = 5.0
    inw = e < win
    ax.scatter(dens[~inw], e[~inw], s=10, color="#ced4da", lw=0)
    ax.scatter(dens[inw], e[inw], s=16, color=BLUE, lw=0)
    best = np.argmin(e)
    ax.scatter([dens[best]], [e[best]], s=60, facecolor="none", edgecolor=RED, lw=1.5)
    ax.axhline(win, color=ORANGE, lw=1.0, ls="--")
    ax.text(dens.max(), win + 0.5, "能量窗口", color=ORANGE, fontsize=9.5, ha="right")
    ax.set_xlabel("密度")
    ax.set_ylabel("相对能量")
    ax.set_xticks([])
    ax.set_yticks([0])
    ax.set_title("示意：能量–密度图", fontsize=10)
    save(fig, "csp-pipeline")


def _rdf(points, cell, rmax=3.2, nb=160, sigma=0.06):
    """Gaussian-smeared pair-distance histogram for a 2D periodic point set (toy fingerprint)."""
    r = np.linspace(0.3, rmax, nb)
    g = np.zeros_like(r)
    shifts = [np.array([i, j]) for i in (-2, -1, 0, 1, 2) for j in (-2, -1, 0, 1, 2)]
    frac = points @ np.linalg.inv(cell)
    for a in range(len(points)):
        for b in range(len(points)):
            for s in shifts:
                if a == b and not s.any():
                    continue
                d = np.linalg.norm(((frac[b] + s) - frac[a]) @ cell)
                if d < rmax + 0.3:
                    g += np.exp(-(r - d) ** 2 / (2 * sigma ** 2)) / (d ** 2)
    g /= len(points)
    return r, g / np.linalg.norm(g)


def fig_structure_similarity():
    cell = np.array([[2.0, 0.0], [0.0, 1.7]])
    base = np.array([[0.2, 0.2], [1.2, 1.05], [0.75, 0.55]])
    rng = np.random.default_rng(2)
    struct = {
        "A": (base, cell),
        "A′（A 加小扰动、换原子顺序、平移）": (((base + rng.normal(0, 0.04, base.shape))[[2, 0, 1]] + [0.3, 0.1]), cell),
        "B（不同堆积）": (np.array([[0.2, 0.2], [1.2, 0.2], [0.7, 1.05]]), np.array([[2.0, 0.0], [0.4, 1.7]])),
    }
    fps = {k: _rdf(*v) for k, v in struct.items()}
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.8), gridspec_kw={"width_ratios": [1.5, 1]})
    ax = axes[0]
    cols = [BLUE, GREEN, ORANGE]
    lss = ["-", "--", "-"]
    for (k, (r, g)), c, ls in zip(fps.items(), cols, lss):
        ax.plot(r, g, color=c, lw=1.6, ls=ls, label=k)
    ax.set_xlabel("原子间距离 $r$")
    ax.set_ylabel("指纹 $f(r)$（归一化）")
    ax.set_yticks([])
    ax.legend(frameon=False, fontsize=8.8, loc="upper right")

    ax = axes[1]
    keys = list(fps)
    D = np.array([[0.5 * (1 - np.dot(fps[a][1], fps[b][1])) for b in keys] for a in keys])
    im = ax.imshow(D, cmap="Oranges", vmin=0, vmax=max(D.max(), 0.05))
    short = ["A", "A′", "B"]
    ax.set_xticks(range(3))
    ax.set_yticks(range(3))
    ax.set_xticklabels(short)
    ax.set_yticklabels(short)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{D[i, j]:.3f}", ha="center", va="center", fontsize=9.5,
                    color="white" if D[i, j] > 0.6 * D.max() else "k")
    ax.set_title(r"余弦距离 $d = \frac{1}{2}(1-\cos\theta)$", fontsize=10.5)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    save(fig, "structure-similarity-fingerprint")


def _f_einstein(T, omegas, e0):
    """Harmonic free energy per cell in reduced units (hbar = k_B = 1)."""
    T = np.asarray(T, dtype=float)[:, None]
    w = np.asarray(omegas)[None, :]
    zp = 0.5 * w
    with np.errstate(divide="ignore", invalid="ignore"):
        th = np.where(T > 0, T * np.log1p(-np.exp(-w / np.where(T > 0, T, 1))), 0.0)
    return e0 + (zp + th).sum(axis=1)


def fig_free_energy():
    T = np.linspace(0, 3.0, 400)
    wA = [1.0, 1.4, 2.0]
    wB = [0.55, 1.2, 2.0]
    eA, eB = 0.0, 0.5
    FA = _f_einstein(T, wA, eA)
    FB = _f_einstein(T, wB, eB)
    dF = FB - FA
    k = np.where(np.diff(np.sign(dF)))[0]
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.8))
    ax = axes[0]
    ax.plot(T, FA - FA[0], color=BLUE, lw=2, label="多晶型 A（较硬）")
    ax.plot(T, FB - FA[0], color=ORANGE, lw=2, label="多晶型 B（较软）")
    ax.set_xlabel("温度 $T$")
    ax.set_ylabel("自由能 $F$（相对 A 在 0 K）")
    ax.legend(frameon=False, fontsize=9, loc="lower left")
    ax.set_xticks([0])
    ax.set_yticks([0])
    ax = axes[1]
    ax.plot(T, dF, color="k", lw=2)
    ax.axhline(0, color=GREY, lw=0.8)
    ax.fill_between(T, dF, 0, where=dF > 0, color=BLUE, alpha=0.10, lw=0)
    ax.fill_between(T, dF, 0, where=dF < 0, color=ORANGE, alpha=0.12, lw=0)
    ax.text(0.05, dF[0] * 0.25, "A 更稳定", color=BLUE, fontsize=10)
    ax.text(T[-1] * 0.72, dF[-1] * 0.5, "B 更稳定", color=ORANGE, fontsize=10)
    ax.annotate(r"$\Delta E + \Delta E_{\mathrm{ZP}}$", xy=(0, dF[0]), xytext=(0.75, dF[0] * 1.6), fontsize=10,
                arrowprops=dict(arrowstyle="->", color=GREY, lw=0.8))
    if len(k):
        tc = T[k[0]]
        ax.axvline(tc, color=RED, lw=1.0, ls=":")
        ax.text(tc + 0.05, dF[0] * 0.15, "$T_{\\mathrm{t}}$", color=RED, fontsize=12)
    ax.set_xlabel("温度 $T$")
    ax.set_ylabel(r"$\Delta F = F_{\mathrm{B}} - F_{\mathrm{A}}$")
    ax.set_xticks([0])
    ax.set_yticks([0])
    save(fig, "free-energy-crossing")


def fig_quasi_harmonic():
    V = np.linspace(0.95, 1.12, 400)
    B0, V0 = 200.0, 1.0
    E = 0.5 * B0 * (V - V0) ** 2 / V0
    gam = 2.0
    w0 = np.array([0.6, 1.0, 1.5, 2.2])
    temps = [0.0, 0.6, 1.2, 1.8]
    cols = [BLUE, GREEN, ORANGE, RED]
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.8), gridspec_kw={"width_ratios": [1.3, 1]})
    ax = axes[0]
    vmins = []
    for T, c in zip(temps, cols):
        w = w0[None, :] * (V[:, None] / V0) ** (-gam)
        zp = 0.5 * w.sum(axis=1)
        th = (T * np.log1p(-np.exp(-w / T))).sum(axis=1) if T > 0 else 0.0
        F = E + zp + th
        i = int(np.argmin(F))
        vmins.append(V[i])
        ax.plot(V, F - F.min() + 0.25 * temps.index(T), color=c, lw=1.8, label=f"$T={T}$")
        ax.scatter([V[i]], [0.25 * temps.index(T)], color=c, s=28, zorder=3)
    ax.set_xlabel("体积 $V$")
    ax.set_ylabel("$F(V,T)$（各条错开）")
    ax.set_yticks([])
    ax.set_ylim(-0.1, 1.9)
    ax.legend(frameon=False, fontsize=9, loc="upper center", ncol=2)
    ax = axes[1]
    Ts = np.linspace(0.0, 2.0, 60)
    vm = []
    for T in Ts:
        w = w0[None, :] * (V[:, None] / V0) ** (-gam)
        F = E + 0.5 * w.sum(axis=1) + ((T * np.log1p(-np.exp(-w / T))).sum(axis=1) if T > 0 else 0.0)
        vm.append(V[int(np.argmin(F))])
    fig.subplots_adjust(wspace=0.38)
    ax.plot(Ts, vm, color="k", lw=2)
    ax.axhline(V0, color=GREY, lw=0.8, ls=":")
    ax.text(Ts[-1], V0 - 0.002, "静态平衡体积 $V_0$", ha="right", va="top", fontsize=9, color=GREY)
    ax.set_xlabel("温度 $T$")
    ax.set_ylabel(r"平衡体积 $V^{*}(T)$")
    ax.set_xticks([0])
    save(fig, "quasi-harmonic-volume")


def fig_molecular_crystal():
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9), gridspec_kw={"width_ratios": [1.3, 1]})
    ax = axes[0]
    ax.set_xlim(-0.6, 6.4)
    ax.set_ylim(-0.7, 4.2)
    ax.set_aspect("equal")
    ax.axis("off")
    for row in range(3):
        for col in range(3):
            x0, y0 = col * 2.1, row * 1.35
            ang = 25 if row % 2 == 0 else -25
            ax.add_patch(Ellipse((x0 + 0.55, y0 + 0.4), 1.25, 0.48, angle=ang, facecolor="#e7f5ff",
                                 edgecolor=BLUE, lw=1.1))
            ax.scatter([x0 + 0.05, x0 + 1.05], [y0 + 0.4 - 0.23 * np.sign(ang), y0 + 0.4 + 0.23 * np.sign(ang)],
                       s=[30, 30], color=[RED, GREEN], zorder=3)
            if col < 2:
                ax.plot([x0 + 1.05 + 0.1, x0 + 2.1 + 0.05 - 0.1],
                        [y0 + 0.4 + 0.23 * np.sign(ang), y0 + 0.4 - 0.23 * np.sign(ang)], color=RED, lw=1.2,
                        ls=(0, (2, 2)))
    ax.annotate("", xy=(0.55, 1.35 + 0.15), xytext=(0.55, 0.65),
                arrowprops=dict(arrowstyle="<->", color=GREY, lw=0.9))
    ax.text(-0.45, 1.05, "层间：\n色散", fontsize=9, color=GREY, ha="center", va="center")
    ax.text(3.15, 3.95, "层内：氢键链（红色虚线）", fontsize=9.5, color=RED, ha="center")
    ax.text(3.15, -0.6, "分子内：共价键（椭圆内部）", fontsize=9.5, color=BLUE, ha="center")

    ax = axes[1]
    x = np.linspace(0, 10, 500)
    low = sum(a * np.exp(-(x - c) ** 2 / (2 * 0.12 ** 2)) for a, c in ((0.6, 0.6), (0.9, 0.95), (0.7, 1.4),
                                                                      (0.5, 1.9)))
    high = sum(a * np.exp(-(x - c) ** 2 / (2 * 0.1 ** 2)) for a, c in ((0.5, 4.2), (0.7, 5.6), (0.4, 6.4),
                                                                      (0.8, 8.8), (0.6, 9.3)))
    ax.fill_between(x, low, color=ORANGE, alpha=0.35, lw=0)
    ax.fill_between(x, high, color=BLUE, alpha=0.30, lw=0)
    ax.plot(x, low + high, color="k", lw=1.0)
    ax.text(1.2, 1.05, "分子间（晶格）振动", color=ORANGE, fontsize=9.5, ha="center")
    ax.text(6.8, 1.05, "分子内振动", color=BLUE, fontsize=9.5, ha="center")
    ax.set_xlabel("频率（示意）")
    ax.set_ylabel("态密度")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_ylim(0, 1.25)
    save(fig, "molecular-crystal-packing")


if __name__ == "__main__":
    for f in (fig_energy_landscape, fig_csp_pipeline, fig_structure_similarity, fig_free_energy, fig_quasi_harmonic,
              fig_molecular_crystal):
        f()
    print("figures written to", OUT)
