"""Figures for the theory map (machine-learning potentials, batch 3).

Run from the repository root:  python3 knowledge/figs/make_figs_mlip.py
Writes knowledge/figs/<name>.svg. Figures are schematic (model functions and toy systems chosen to show an idea,
not data for any material), except md-verlet-energy, which integrates a 1D model oscillator for real.
Set FIG_PREVIEW_DIR to also write PNG copies (outside the repository) for checking.
"""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch  # noqa: E402

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


def scatter_atoms(seed=3, n=46, box=4.6):
    rng = np.random.default_rng(seed)
    pts = []
    while len(pts) < n:
        p = rng.uniform(-box, box, 2)
        if all(np.hypot(*(p - q)) > 0.85 for q in pts) and np.hypot(*p) > 0.8:
            pts.append(p)
    return np.array(pts)


# ---------------------------------------------------------------------------
def fig_local_cutoff():
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.0), gridspec_kw={"width_ratios": [1, 1.2]})
    ax = axes[0]
    pts = scatter_atoms()
    rc = 2.3
    ax.add_patch(Circle((0, 0), rc, facecolor=BLUE, alpha=0.08, edgecolor=BLUE, lw=1.2, ls="--"))
    inside = np.hypot(pts[:, 0], pts[:, 1]) < rc
    ax.scatter(pts[~inside, 0], pts[~inside, 1], s=60, color="#dee2e6", edgecolor=GREY, lw=0.6, zorder=2)
    ax.scatter(pts[inside, 0], pts[inside, 1], s=70, color=BLUE, edgecolor="k", lw=0.6, zorder=3)
    ax.scatter([0], [0], s=120, color=ORANGE, edgecolor="k", lw=0.8, zorder=4)
    ax.text(0.12, -0.42, "$i$", fontsize=12)
    arrow(ax, 0, 0, rc * np.cos(np.deg2rad(200)), rc * np.sin(np.deg2rad(200)), GREY, lw=1.0, ms=9)
    ax.text(-1.55, -0.25, "$r_c$", color=GREY, fontsize=12)
    ax.set_xlim(-4.0, 4.0)
    ax.set_ylim(-4.0, 4.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("原子能只看截断球内的邻居", fontsize=11)

    ax = axes[1]
    r = np.linspace(0.75, 3.0, 400)
    true = (1 - np.exp(-2.0 * (r - 1.2))) ** 2 - 1
    rng = np.random.default_rng(5)
    rt = np.sort(rng.uniform(1.0, 1.9, 14))
    yt = (1 - np.exp(-2.0 * (rt - 1.2))) ** 2 - 1
    coef = np.polyfit(rt, yt, 5)
    fit = np.polyval(coef, r)
    ax.axvspan(1.0, 1.9, color=GREEN, alpha=0.08, lw=0)
    ax.plot(r, true, color="k", lw=1.8, label="真实势能面")
    ax.plot(r, fit, color=ORANGE, lw=1.8, ls="--", label="拟合模型")
    ax.scatter(rt, yt, s=22, color=GREEN, zorder=3, label="训练数据")
    ax.text(1.45, 1.05, "内插区", ha="center", color=GREEN, fontsize=10)
    ax.text(2.55, 1.05, "外推区", ha="center", color=GREY, fontsize=10)
    ax.set_ylim(-1.4, 1.3)
    ax.set_xlim(0.75, 3.0)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("构型坐标（例如键长）")
    ax.set_ylabel("能量")
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    save(fig, "mlip-local-cutoff")


def fig_mace_message_passing():
    fig = plt.figure(figsize=(9.6, 4.1))
    ax = fig.add_axes([0.0, 0.0, 0.42, 1.0])
    pts = scatter_atoms(seed=11, n=58, box=5.2)
    rc = 1.9
    ax.add_patch(Circle((0, 0), 2 * rc, facecolor=ORANGE, alpha=0.06, edgecolor=ORANGE, lw=1.1, ls=":"))
    ax.add_patch(Circle((0, 0), rc, facecolor=BLUE, alpha=0.10, edgecolor=BLUE, lw=1.2, ls="--"))
    d = np.hypot(pts[:, 0], pts[:, 1])
    c = np.where(d < rc, BLUE, np.where(d < 2 * rc, ORANGE, "#dee2e6"))
    ax.scatter(pts[:, 0], pts[:, 1], s=46, c=c, edgecolor=GREY, lw=0.5, zorder=3)
    ax.scatter([0], [0], s=110, color="k", zorder=4)
    ax.text(0.15, -0.45, "$i$", fontsize=12)
    ax.text(rc * 0.70, rc * 0.62, "$r_c$", color=BLUE, fontsize=11)
    ax.text(2 * rc * 0.72, 2 * rc * 0.70, "$2r_c$", color=ORANGE, fontsize=11)
    ax.set_xlim(-4.6, 4.6)
    ax.set_ylim(-4.6, 4.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(0, -4.55, "两层消息传递：感受野约为 2r_c", ha="center", fontsize=10)

    ax = fig.add_axes([0.45, 0.05, 0.55, 0.9])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    boxes = [
        (9.0, "邻居几何与元素", r"$\mathbf{r}_{ij},\ Z_j$", GREY),
        (7.0, "原子基（两体）", r"$A_{i}$", BLUE),
        (5.0, "张量积（多体）", r"$B_{i} \sim A_i \otimes A_i \otimes \cdots$", BLUE),
        (3.0, "消息与更新", r"$m_i \;\rightarrow\; h_i^{(t+1)}$", ORANGE),
        (1.0, "读出原子能", r"$E_i,\quad E=\sum_i E_i$", GREEN),
    ]
    for y, lab, formula, col in boxes:
        ax.add_patch(FancyBboxPatch((0.3, y - 0.7), 9.2, 1.4, boxstyle="round,pad=0.05", facecolor="white",
                                    edgecolor=col, lw=1.3))
        ax.text(0.7, y, lab, va="center", fontsize=10.5)
        ax.text(5.2, y, formula, va="center", fontsize=11.5, color=col)
    for y in (8.3, 6.3, 4.3, 2.3):
        arrow(ax, 4.9, y, 4.9, y - 0.6, GREY, lw=1.1, ms=10)
    ax.annotate("", xy=(9.75, 6.0), xytext=(9.75, 3.0),
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.1, connectionstyle="arc3,rad=0.5"))
    ax.text(9.9, 4.5, "重复\n$T$ 层", fontsize=9, color=ORANGE, va="center")
    save(fig, "mace-message-passing")


def fig_equivariance():
    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    ax.set_xlim(-1.6, 8.4)
    ax.set_ylim(-1.8, 2.0)
    ax.set_aspect("equal")
    ax.axis("off")
    base = np.array([[0.0, 0.0], [0.95, 0.35], [-0.35, 0.92]])
    forces = np.array([[-0.25, -0.15], [0.55, 0.05], [-0.15, 0.55]])
    cols = [RED, "#adb5bd", "#adb5bd"]

    def draw(offset, R):
        p = base @ R.T + offset
        f = forces @ R.T
        for k in (1, 2):
            ax.plot([p[0, 0], p[k, 0]], [p[0, 1], p[k, 1]], color=GREY, lw=2.2, zorder=1)
        for k in range(3):
            ax.scatter(*p[k], s=260 if k == 0 else 150, color=cols[k], edgecolor="k", lw=0.7, zorder=2)
            arrow(ax, p[k, 0], p[k, 1], p[k, 0] + f[k, 0], p[k, 1] + f[k, 1], BLUE, lw=1.6, ms=11)
        return p

    I = np.eye(2)
    th = np.deg2rad(70)
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    draw(np.array([0.0, 0.0]), I)
    draw(np.array([6.3, -0.3]), R)
    ax.annotate("", xy=(5.0, 0.3), xytext=(2.0, 0.3),
                arrowprops=dict(arrowstyle="-|>", color="k", lw=1.4, connectionstyle="arc3,rad=-0.25"))
    ax.text(3.5, 1.05, "旋转 $R$", ha="center", fontsize=11)
    ax.text(0.2, -1.35, r"能量 $E$，力 $\mathbf{F}_k$", ha="center", fontsize=11)
    ax.text(6.4, -1.35, r"能量 $E$（不变），力 $R\,\mathbf{F}_k$（等变）", ha="center", fontsize=11)
    save(fig, "equivariance-rotation")


def fig_md_verlet():
    def force(x):
        return -x - 0.4 * x ** 3

    def energy(x, v):
        return 0.5 * v ** 2 + 0.5 * x ** 2 + 0.1 * x ** 4

    def run(dt, steps, method):
        x, v = 1.2, 0.0
        xs, vs = [x], [v]
        for _ in range(steps):
            if method == "euler":
                x, v = x + dt * v, v + dt * force(x)
            else:
                a = force(x)
                x = x + dt * v + 0.5 * dt * dt * a
                v = v + 0.5 * dt * (a + force(x))
            xs.append(x)
            vs.append(v)
        return np.array(xs), np.array(vs)

    T = 20.0
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.8), gridspec_kw={"width_ratios": [1, 1.35]})
    ax = axes[0]
    xe, ve = run(0.02, int(T / 0.02), "euler")
    xv, vv = run(0.1, int(T / 0.1), "verlet")
    ax.plot(xe, ve, color=RED, lw=1.0, label=r"显式 Euler，$\Delta t=0.02$")
    ax.plot(xv, vv, color=BLUE, lw=1.8, label=r"速度 Verlet，$\Delta t=0.1$")
    ax.set_xlabel("位置 $x$")
    ax.set_ylabel("速度 $v$")
    ax.set_aspect("equal", adjustable="datalim")
    ax.legend(frameon=False, fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, 1.18))

    ax = axes[1]
    e0 = energy(1.2, 0.0)
    for dt, col in ((0.1, BLUE), (0.2, GREEN), (0.4, ORANGE)):
        x, v = run(dt, int(T / dt), "verlet")
        t = np.arange(len(x)) * dt
        ax.plot(t, (energy(x, v) - e0) / e0, color=col, lw=1.3, label=rf"Verlet $\Delta t={dt}$")
    x, v = run(0.02, int(T / 0.02), "euler")
    t = np.arange(len(x)) * 0.02
    ax.plot(t, (energy(x, v) - e0) / e0, color=RED, lw=1.3, ls="--", label=r"Euler $\Delta t=0.02$")
    ax.axhline(0, color=GREY, lw=0.7)
    ax.set_ylim(-0.07, 0.15)
    ax.set_xlim(0, T)
    ax.set_xlabel("时间 $t$")
    ax.set_ylabel(r"相对能量误差 $(E-E_0)/E_0$")
    ax.legend(frameon=False, fontsize=8.5, loc="upper right")
    save(fig, "md-verlet-energy")


def fig_electrostatics():
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.8), gridspec_kw={"width_ratios": [1.25, 1]})
    ax = axes[0]
    r = np.linspace(0.8, 10, 400)
    rc = 5.0
    coul = 1 / r
    fc = np.where(r < rc, 0.5 * (np.cos(np.pi * r / rc) + 1), 0.0)
    local = coul * fc
    ax.plot(r, coul, color="k", lw=1.8, label=r"库仑 $\propto 1/r$")
    ax.plot(r, local, color=ORANGE, lw=1.8, ls="--", label="截断后的局域模型")
    ax.axvline(rc, color=BLUE, lw=1.0, ls=":")
    ax.text(rc + 0.15, 0.95, "$r_c$", color=BLUE, fontsize=12)
    ax.fill_between(r, local, coul, where=r > 2.0, color=RED, alpha=0.10, lw=0)
    ax.text(7.2, 0.30, "丢掉的长程部分", color=RED, fontsize=10, ha="center")
    ax.set_xlim(0.8, 10)
    ax.set_ylim(0, 1.25)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("两个电荷的距离 $r$")
    ax.set_ylabel("相互作用能")
    ax.legend(frameon=False, fontsize=9, loc="upper right", bbox_to_anchor=(1.0, 0.88))

    ax = axes[1]
    ax.set_xlim(-1.8, 2.6)
    ax.set_ylim(-1.7, 2.0)
    ax.set_aspect("equal")
    ax.axis("off")
    for y in (-1.2, -0.4, 0.4, 1.2):
        arrow(ax, -1.7, y, -0.9, y, GREY, lw=1.1, ms=9)
    ax.text(-1.3, 1.6, r"电场 $\boldsymbol{\mathcal{E}}$", ha="center", color=GREY, fontsize=11)
    ax.scatter([0.5], [0], s=260, color=BLUE, edgecolor="k", lw=0.8, zorder=3)
    ax.text(0.5, -0.5, r"原子 $\kappa$", ha="center", fontsize=10)
    ang = np.deg2rad(32)
    arrow(ax, 0.5, 0, 0.5 + 1.7 * np.cos(ang), 1.7 * np.sin(ang), ORANGE, lw=2.0, ms=13)
    ax.text(0.5 + 1.75 * np.cos(ang), 1.7 * np.sin(ang) + 0.12,
            r"$F_{\kappa\beta} = e\sum_\alpha Z^{*}_{\kappa,\alpha\beta}\,\mathcal{E}_{\alpha}$", fontsize=11, color=ORANGE,
            ha="center")
    ax.plot([0.5, 2.3], [0, 0], color=GREY, lw=0.8, ls=":")
    ax.text(1.2, -1.25, "力不一定平行于电场", fontsize=9.5, ha="center", color=GREY)
    save(fig, "mlip-electrostatics")


def fig_finetuning():
    fig, ax = plt.subplots(figsize=(6.8, 3.9))
    s = np.linspace(0, 10, 300)
    target = 0.25 + 0.75 * np.exp(-s / 1.8)
    general_naive = 0.30 + 0.45 * (1 - np.exp(-s / 3.0))
    general_replay = 0.30 + 0.08 * (1 - np.exp(-s / 3.0))
    target_replay = 0.30 + 0.70 * np.exp(-s / 2.0)
    ax.plot(s, target, color=BLUE, lw=2, label="目标体系误差（只用新数据）")
    ax.plot(s, target_replay, color=BLUE, lw=1.6, ls="--", label="目标体系误差（混入原数据）")
    ax.plot(s, general_naive, color=RED, lw=2, label="原有领域误差（只用新数据）")
    ax.plot(s, general_replay, color=RED, lw=1.6, ls="--", label="原有领域误差（混入原数据）")
    ax.annotate("遗忘", xy=(8.5, 0.30 + 0.45 * (1 - np.exp(-8.5 / 3.0))), xytext=(6.2, 0.95),
                fontsize=10, color=RED, arrowprops=dict(arrowstyle="->", color=RED, lw=0.9))
    ax.set_xlabel("微调步数")
    ax.set_ylabel("误差")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_ylim(0, 1.1)
    ax.legend(frameon=False, fontsize=8.8, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
    save(fig, "mlip-finetuning-forgetting")


if __name__ == "__main__":
    for f in (fig_local_cutoff, fig_mace_message_passing, fig_equivariance, fig_md_verlet, fig_electrostatics,
              fig_finetuning):
        f()
    print("figures written to", OUT)
