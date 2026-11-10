"""Figures for the theory map (piezo line, batch 1).

Run from the repository root:  python3 knowledge/figs/make_figs_piezo.py
Writes knowledge/figs/<name>.svg. All figures are schematic: shapes and
trends are meant to explain an idea, not to report data for any material.
"""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle  # noqa: E402

OUT = Path(__file__).resolve().parent
plt.rcParams.update({
    "font.family": "Arial Unicode MS",
    "mathtext.fontset": "stix",
    "svg.fonttype": "path",      # text as outlines: looks the same on every device
    "svg.hashsalt": "theory-map",  # stable ids, so rebuilding does not change the file
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})
BLUE, RED, GREY, GREEN, ORANGE = "#3b5bdb", "#e03131", "#868e96", "#2b8a3e", "#e8590c"


def save(fig, name):
    fig.savefig(OUT / f"{name}.svg", format="svg", bbox_inches="tight", metadata={"Date": None})
    preview = os.environ.get("FIG_PREVIEW_DIR")  # optional PNG copies for checking, outside the repo
    if preview:
        fig.savefig(Path(preview) / f"{name}.png", dpi=110, bbox_inches="tight")
    plt.close(fig)


def arrow(ax, x0, y0, x1, y1, color="k", lw=1.4, style="-|>", ms=10):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=ms,
                                 color=color, lw=lw, shrinkA=0, shrinkB=0))


# ---------------------------------------------------------------------------
def fig_piezo_clamped_relaxed():
    """1D chain of +q/-q: reference, clamped-ion strain, relaxed-ion strain."""
    fig, ax = plt.subplots(figsize=(8.8, 3.6))
    ax.set_xlim(-3.6, 8.2)
    ax.set_ylim(-0.6, 3.4)
    ax.axis("off")
    rows = [("未应变", 1.0, 0.0, 2.7), ("夹持离子：\n均匀拉伸 η", 1.25, 0.0, 1.55), ("弛豫离子：\n再加内位移 Δu", 1.25, 0.12, 0.4)]
    u = 0.35
    for label, scale, du, y in rows:
        ax.text(-0.45, y, label, fontsize=10.5, ha="right", va="center")
        for k in range(3):
            xp = k * 2.2 * scale
            xm = xp + u * 2.2 * scale + du * 2.2
            ax.add_patch(Circle((xp, y), 0.17, color=BLUE))
            ax.text(xp, y, "+", color="w", ha="center", va="center", fontsize=11)
            ax.add_patch(Circle((xm, y), 0.17, color=RED))
            ax.text(xm, y, "−", color="w", ha="center", va="center", fontsize=12)
        # one cell bracket
        L = 2.2 * scale
        ax.plot([0, L], [y - 0.32, y - 0.32], color=GREY, lw=1)
        ax.plot([0, 0], [y - 0.38, y - 0.26], color=GREY, lw=1)
        ax.plot([L, L], [y - 0.38, y - 0.26], color=GREY, lw=1)
        ax.text(L / 2, y - 0.36, "L" if scale == 1 else "L(1+η)", ha="center", va="top", fontsize=9.5, color=GREY)
    # internal displacement marker on last row
    xm_c = 0 + u * 2.2 * 1.25
    ax.annotate("", xy=(xm_c + 0.12 * 2.2, 0.72), xytext=(xm_c, 0.72),
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.6))
    ax.text(xm_c + 0.13, 0.80, "Δu", color=ORANGE, fontsize=10.5, ha="center", va="bottom")
    ax.text(7.1, 1.55, r"$\Delta P = \bar e\,\eta$", fontsize=12, va="center")
    ax.text(7.1, 0.40, r"$\Delta P = \bar e\,\eta + \frac{Z^{*}\Delta u}{\Omega}$", fontsize=12, va="center")
    save(fig, "piezo-clamped-relaxed")


def fig_elastic_clamped_relaxed():
    eta = np.linspace(-1, 1, 200)
    fig, ax = plt.subplots(figsize=(5.4, 3.5))
    c0, c = 1.0, 0.62
    ax.plot(eta, 0.5 * c0 * eta**2, color=BLUE, lw=2, label=r"夹持离子 $E(\eta)$，曲率 $\bar C$")
    ax.plot(eta, 0.5 * c * eta**2, color=ORANGE, lw=2, label=r"弛豫离子 $E(\eta)$，曲率 $C$")
    e1 = 0.8
    ax.annotate("", xy=(e1, 0.5 * c * e1**2), xytext=(e1, 0.5 * c0 * e1**2),
                arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.3))
    ax.text(e1 + 0.04, 0.5 * (0.5 * c * e1**2 + 0.5 * c0 * e1**2), "原子弛豫\n降低能量", fontsize=9.5, color=GREY,
            va="center")
    ax.set_xlabel(r"应变 $\eta$")
    ax.set_ylabel(r"每单位体积能量 $E/\Omega$")
    ax.set_xticks([0])
    ax.set_yticks([0])
    ax.legend(frameon=False, fontsize=9.5, loc="upper center")
    ax.set_ylim(0, 0.62)
    save(fig, "elastic-clamped-relaxed")


def fig_born_charge():
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.1))
    for ax in axes:
        ax.set_xlim(-1.6, 1.8)
        ax.set_ylim(-1.2, 1.3)
        ax.set_aspect("equal")
        ax.axis("off")
    # left: rigid ion
    ax = axes[0]
    ax.set_title("刚性离子：电荷随核一起移动", fontsize=10.5)
    for x, a in ((-0.5, 0.35), (0.5, 1.0)):
        ax.add_patch(Circle((x, 0), 0.55, color=BLUE, alpha=0.18 * a, lw=0))
        ax.add_patch(Circle((x, 0), 0.12, color=BLUE, alpha=a))
    arrow(ax, -0.5, -0.85, 0.5, -0.85, color=ORANGE)
    ax.text(0, -1.05, r"位移 $u$", ha="center", va="top", fontsize=10, color=ORANGE)
    ax.text(0, 0.95, r"$\Delta p = Z_{\mathrm{nom}}\,e\,u$", ha="center", fontsize=11)
    # right: real ion, cloud lags and neighbours respond
    ax = axes[1]
    ax.set_title("真实体系：电子云不完全跟随，邻居也响应", fontsize=10.5)
    ax.add_patch(Circle((-0.5, 0), 0.55, color=BLUE, alpha=0.06, lw=0))
    ax.add_patch(Circle((-0.5, 0), 0.12, color=BLUE, alpha=0.35))
    ax.add_patch(Circle((0.3, 0), 0.6, color=BLUE, alpha=0.20, lw=0))
    ax.add_patch(Circle((0.5, 0), 0.12, color=BLUE))
    for xn in (1.45,):
        ax.add_patch(Circle((xn, 0), 0.25, color=RED, alpha=0.25, lw=0))
        arrow(ax, xn, 0.35, xn - 0.25, 0.35, color=RED, lw=1.1, ms=8)
    arrow(ax, -0.5, -0.85, 0.5, -0.85, color=ORANGE)
    ax.text(0, -1.05, r"位移 $u$", ha="center", va="top", fontsize=10, color=ORANGE)
    ax.text(0.1, 0.95, r"$\Delta p = Z^{*}e\,u,\ \ Z^{*}\neq Z_{\mathrm{nom}}$", ha="center", fontsize=11)
    save(fig, "born-charge")


def fig_polarization_lattice():
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 4.0), gridspec_kw={"height_ratios": [1.25, 1]})
    ax = axes[0]
    ax.set_xlim(-0.3, 6.4)
    ax.set_ylim(-0.9, 1.0)
    ax.axis("off")
    ax.set_title("同一个周期电荷分布，晶胞取法不同，“偶极”就不同", fontsize=10.5)
    for k in range(4):
        ax.add_patch(Circle((k * 2.0, 0), 0.16, color=BLUE))
        ax.text(k * 2.0, 0, "+", color="w", ha="center", va="center")
        ax.add_patch(Circle((k * 2.0 + 0.7, 0), 0.16, color=RED))
        ax.text(k * 2.0 + 0.7, 0, "−", color="w", ha="center", va="center")
    ax.add_patch(Rectangle((-0.35, -0.42), 2.0, 0.84, fill=False, ec=GREEN, lw=1.6))
    ax.text(0.65, -0.62, "晶胞 A：偶极向右", color=GREEN, ha="center", va="top", fontsize=9.5)
    ax.add_patch(Rectangle((2.35, -0.48), 2.0, 0.96, fill=False, ec=ORANGE, lw=1.6, ls="--"))
    ax.text(3.35, -0.62, "晶胞 B：偶极向左", color=ORANGE, ha="center", va="top", fontsize=9.5)
    ax = axes[1]
    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-0.6, 0.9)
    ax.axis("off")
    ax.plot([-3.4, 3.4], [0, 0], color=GREY, lw=1)
    for k in range(-3, 4):
        ax.plot([k + 0.3], [0], "o", color=BLUE, ms=7)
    ax.annotate("", xy=(1.3, 0.35), xytext=(0.3, 0.35), arrowprops=dict(arrowstyle="<->", color=GREY))
    ax.text(0.8, 0.42, r"极化量子 $eR/\Omega$", ha="center", va="bottom", fontsize=10)
    ax.text(0, -0.35, r"允许的极化值是一组格点 $P_0 + n\,eR/\Omega$；只有沿连续路径的变化 $\Delta P$ 有确定意义", ha="center",
            va="top", fontsize=9.8)
    save(fig, "polarization-lattice")


def fig_fd_step_error():
    h = np.logspace(-4, -0.5, 200)
    a, eps = 1.0, 1e-7
    trunc = a * h**2
    noise = eps / h
    fig, ax = plt.subplots(figsize=(5.4, 3.6))
    ax.loglog(h, trunc, color=BLUE, lw=1.6, ls="--", label=r"截断误差 $\propto h^{2}$（非谐项）")
    ax.loglog(h, noise, color=RED, lw=1.6, ls="--", label=r"噪声误差 $\propto \epsilon/h$（自洽、力的精度）")
    ax.loglog(h, trunc + noise, color="k", lw=2, label="总误差")
    hopt = (eps / (2 * a)) ** (1 / 3)
    ax.axvline(hopt, color=GREY, lw=1, ls=":")
    ax.text(hopt * 1.15, 3e-2, "最优步长", color=GREY, fontsize=9.5)
    ax.set_xlabel(r"位移步长 $h$（对数）")
    ax.set_ylabel("导数误差（对数）")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.minorticks_off()
    ax.legend(frameon=False, fontsize=9, loc="upper center")
    ax.set_ylim(1e-7, 3)
    save(fig, "fd-step-error")


def fig_convergence():
    x = np.arange(400, 1001, 50)
    e = 0.05 * np.exp(-(x - 400) / 70)
    q = 0.35 * np.exp(-(x - 400) / 170) * np.cos((x - 400) / 140)
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.2), sharex=True)
    for ax, y, title, tol in ((axes[0], e, "总能（每原子）", 0.002), (axes[1], q, "目标量（例如应力、压电系数）", 0.02)):
        ax.plot(x, y, "o-", color=BLUE, ms=4, lw=1.4)
        ax.axhspan(-tol, tol, color=GREEN, alpha=0.12, lw=0)
        idx = next(i for i in range(len(y)) if all(abs(v) < tol for v in y[i:]))
        ax.axvline(x[idx], color=GREEN, lw=1, ls=":")
        ax.text(x[idx] + 8, max(y) * 0.8, f"进入容差带", color=GREEN, fontsize=9.5)
        ax.axhline(0, color=GREY, lw=0.8)
        ax.set_title(title, fontsize=10.5)
        ax.set_xlabel("截断能 ENCUT（示意）")
        ax.set_yticks([0])
        ax.set_yticklabels(["收敛值"])
    axes[0].set_ylabel("与收敛值之差")
    save(fig, "convergence-target")


def fig_damping():
    r = np.linspace(0.35, 3.0, 400)
    c6, r0 = 1.0, 1.0
    bare = -c6 / r**6
    zero = -c6 / r**6 / (1 + 6 * (r / (1.217 * r0)) ** (-14))
    a1, a2 = 0.4, 0.45
    bj = -c6 / (r**6 + (a1 * r0 + a2) ** 6)
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    ax.plot(r, bare, color=GREY, lw=1.4, ls="--", label=r"无阻尼 $-C_6/r^{6}$")
    ax.plot(r, zero, color=BLUE, lw=2, label="零阻尼（D3 原始形式）")
    ax.plot(r, bj, color=ORANGE, lw=2, label="Becke–Johnson 阻尼")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_ylim(-1.6, 0.15)
    ax.set_xlim(0.35, 3.0)
    ax.set_xlabel(r"原子间距 $r/R_0$")
    ax.set_ylabel(r"色散能 $E_{\mathrm{disp}}$（任意单位）")
    ax.set_yticks([0])
    ax.legend(frameon=False, fontsize=9.5, loc="lower right")
    ax.annotate("短程：无阻尼形式发散", xy=(0.62, -1.5), xytext=(0.95, -1.25), fontsize=9.5, color=GREY,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    ax.annotate("BJ：趋于有限值", xy=(0.45, bj[10]), xytext=(1.05, -0.9), fontsize=9.5, color=ORANGE,
                arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.8))
    save(fig, "dispersion-damping")


def fig_point_group_counts():
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    ax.axis("off")
    ax.set_xlim(0, 32)
    ax.set_ylim(-1.6, 3.4)
    bars = [(0, 32, 2.4, "#dee2e6", "32 个晶体学点群"),
            (0, 11, 1.4, "#ffe3e3", "11 个中心对称（不压电）"),
            (11, 21, 1.4, "#d0ebff", "21 个无对称中心"),
            (11, 20, 0.4, "#b2f2bb", "20 个允许压电（432 除外）"),
            (11, 10, -0.6, "#ffd8a8", "10 个极性点群：还允许自发极化")]
    for x0, w, y, c, t in bars:
        ax.add_patch(Rectangle((x0, y), w, 0.8, color=c, lw=0))
        ax.text(x0 + 0.3, y + 0.4, t, va="center", fontsize=10)
    save(fig, "point-groups-piezo")


def fig_d_matrix_pg2():
    """Nonzero pattern of d (3x6, Voigt) for point group 2 with b (axis 2) unique."""
    nz = {(0, 3), (0, 5), (1, 0), (1, 1), (1, 2), (1, 4), (2, 3), (2, 5)}
    fig, ax = plt.subplots(figsize=(5.2, 2.6))
    ax.set_xlim(-0.6, 6)
    ax.set_ylim(-0.2, 3.6)
    ax.axis("off")
    for i in range(3):
        for j in range(6):
            on = (i, j) in nz
            hi = (i, j) == (0, 5)
            ax.add_patch(Rectangle((j, 2 - i), 0.92, 0.92, color=(ORANGE if hi else (BLUE if on else "#f1f3f5")),
                                   alpha=0.9 if on else 1, lw=0))
            ax.text(j + 0.46, 2 - i + 0.46, f"$d_{{{i + 1}{j + 1}}}$" if on else "0", ha="center", va="center",
                    color="w" if on else GREY, fontsize=10.5)
    for j in range(6):
        ax.text(j + 0.46, 3.1, str(j + 1), ha="center", fontsize=9.5, color=GREY)
    for i in range(3):
        ax.text(-0.25, 2 - i + 0.46, str(i + 1), ha="center", va="center", fontsize=9.5, color=GREY)
    ax.text(3.0, 3.45, "点群 2（b 轴为二重轴）的 $d_{ij}$：8 个独立分量", ha="center", fontsize=10.5)
    save(fig, "d-matrix-pg2")


def fig_pka():
    x = np.linspace(-4, 8, 400)
    p = np.clip((x + 1) / 5, 0, 1)
    fig, ax = plt.subplots(figsize=(5.8, 3.2))
    ax.plot(x, p, color=BLUE, lw=2)
    ax.axvspan(-4, -1, color=GREEN, alpha=0.10, lw=0)
    ax.axvspan(4, 8, color=ORANGE, alpha=0.10, lw=0)
    ax.text(-2.5, 0.88, "多为共晶\n（质子不转移）", ha="center", fontsize=9.5, color=GREEN)
    ax.text(6.0, 0.18, "多为盐\n（质子转移）", ha="center", fontsize=9.5, color=ORANGE)
    ax.text(1.5, 0.88, "过渡区：两者都可能，\n要看具体晶体环境", ha="center", fontsize=9.5, color=GREY)
    ax.set_xlabel(r"$\Delta\mathrm{p}K_a$ = p$K_a$(碱的共轭酸) − p$K_a$(酸)")
    ax.set_ylabel("成盐的可能性（示意）")
    ax.set_yticks([0, 1])
    ax.set_ylim(-0.05, 1.08)
    save(fig, "pka-salt-cocrystal")


def fig_proton_well():
    x = np.linspace(-1.4, 1.4, 300)
    fig, ax = plt.subplots(figsize=(5.4, 3.0))
    for shift, c, lab in ((0.35, GREEN, "共晶：质子靠近酸 O–H"), (-0.35, ORANGE, "盐：质子转移到碱 N⁺–H")):
        v = (x**2 - 1) ** 2 + shift * x
        ax.plot(x, v, color=c, lw=2, label=lab)
    ax.set_xlabel("质子沿氢键的位置")
    ax.set_xticks([-1, 1])
    ax.set_xticklabels(["靠酸（O）", "靠碱（N）"])
    ax.set_yticks([])
    ax.set_ylabel("势能（示意）")
    ax.legend(frameon=False, fontsize=9.5, loc="upper center")
    ax.set_ylim(-0.5, 2.3)
    save(fig, "proton-double-well")


if __name__ == "__main__":
    for f in (fig_piezo_clamped_relaxed, fig_elastic_clamped_relaxed, fig_born_charge, fig_polarization_lattice,
              fig_fd_step_error, fig_convergence, fig_damping, fig_point_group_counts, fig_d_matrix_pg2, fig_pka,
              fig_proton_well):
        f()
    print("figures written to", OUT)
