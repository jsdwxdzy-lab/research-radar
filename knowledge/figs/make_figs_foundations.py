"""Figures for the theory map (foundations, batch 2).

Run from the repository root:  python3 knowledge/figs/make_figs_foundations.py
Writes knowledge/figs/<name>.svg. All figures are schematic: model functions chosen to show a shape or an idea,
not data for any material. Set FIG_PREVIEW_DIR to also write PNG copies (outside the repository) for checking.
"""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

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
def fig_tensor_rotation():
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.6), gridspec_kw={"width_ratios": [1, 1.15]})
    ax = axes[0]
    ax.set_xlim(-0.4, 2.3)
    ax.set_ylim(-0.4, 2.1)
    ax.set_aspect("equal")
    ax.axis("off")
    th = np.deg2rad(30)
    arrow(ax, 0, 0, 2.0, 0, GREY)
    arrow(ax, 0, 0, 0, 1.9, GREY)
    ax.text(2.05, -0.12, "$x_1$", color=GREY)
    ax.text(-0.2, 1.9, "$x_2$", color=GREY)
    arrow(ax, 0, 0, 1.9 * np.cos(th), 1.9 * np.sin(th), BLUE)
    arrow(ax, 0, 0, -1.6 * np.sin(th), 1.6 * np.cos(th), BLUE)
    ax.text(1.9 * np.cos(th) + 0.03, 1.9 * np.sin(th) + 0.03, "$x'_1$", color=BLUE)
    ax.text(-1.6 * np.sin(th) - 0.15, 1.6 * np.cos(th) + 0.05, "$x'_2$", color=BLUE)
    a = np.linspace(0, th, 30)
    ax.plot(0.6 * np.cos(a), 0.6 * np.sin(a), color=BLUE, lw=1)
    ax.text(0.65, 0.12, r"$\theta$", color=BLUE)
    v = np.array([1.2, 1.35])
    arrow(ax, 0, 0, *v, ORANGE, lw=2)
    ax.text(v[0] + 0.05, v[1] + 0.03, r"$\mathbf{v}$", color=ORANGE, fontsize=12)
    ax.plot([v[0], v[0]], [0, v[1]], color=ORANGE, lw=0.8, ls=":")
    ax.text(v[0] - 0.05, -0.2, "$v_1$", color=ORANGE, ha="center")
    ax.set_title("同一个矢量，两套坐标下分量不同", fontsize=10.5)
    # right: Voigt map
    ax = axes[1]
    ax.set_xlim(-0.2, 7.4)
    ax.set_ylim(-0.4, 3.6)
    ax.axis("off")
    ax.set_title("对称二阶张量的 Voigt 编号", fontsize=10.5)
    lab = {(0, 0): "1", (1, 1): "2", (2, 2): "3", (1, 2): "4", (2, 1): "4", (0, 2): "5", (2, 0): "5",
           (0, 1): "6", (1, 0): "6"}
    col = {"1": BLUE, "2": BLUE, "3": BLUE, "4": ORANGE, "5": GREEN, "6": RED}
    for i in range(3):
        for j in range(3):
            c = col[lab[(i, j)]]
            ax.add_patch(Rectangle((j * 1.0, 2 - i * 1.0), 0.92, 0.92, color=c, alpha=0.22 if i != j else 0.35, lw=0))
            ax.text(j + 0.46, 2 - i + 0.6, f"$\\varepsilon_{{{i + 1}{j + 1}}}$", ha="center", va="center", fontsize=11)
            ax.text(j + 0.46, 2 - i + 0.22, lab[(i, j)], ha="center", va="center", fontsize=9.5, color=c)
    ax.text(3.4, 1.5, r"$\rightarrow$", fontsize=18, va="center")
    names = ["11", "22", "33", "23", "13", "12"]
    for k in range(6):
        c = col[str(k + 1)]
        ax.add_patch(Rectangle((4.1 + k * 0.52, 1.1), 0.48, 0.8, color=c, alpha=0.3, lw=0))
        ax.text(4.1 + k * 0.52 + 0.24, 1.5, str(k + 1), ha="center", va="center", fontsize=10.5)
        ax.text(4.1 + k * 0.52 + 0.24, 0.85, names[k], ha="center", va="top", fontsize=8.5, color=GREY)
    ax.text(4.1 + 1.56, 2.15, "6 个独立分量", ha="center", fontsize=9.5, color=GREY)
    save(fig, "tensor-rotation-voigt")


def fig_kohn_sham_map():
    x = np.linspace(-3, 3, 400)
    vext = 0.35 * (x**2 - 2.0) ** 2 - 1.2 * np.exp(-((x - 0.0) ** 2) / 0.3)
    n = np.exp(-((x - 1.25) ** 2) / 0.35) + np.exp(-((x + 1.25) ** 2) / 0.35)
    n /= n.max()
    vs = 0.32 * (x**2 - 2.1) ** 2 - 0.4 * np.exp(-(x**2) / 0.5)
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.2), sharey=True)
    for ax, v, t, c in ((axes[0], vext, "真实体系：相互作用电子在 $v_{\\mathrm{ext}}$ 中", BLUE),
                        (axes[1], vs, "Kohn–Sham 体系：无相互作用电子在 $v_{s}$ 中", ORANGE)):
        ax.plot(x, v, color=c, lw=2, label="势")
        ax.fill_between(x, -1.6, -1.6 + 1.2 * n, color=GREEN, alpha=0.25, lw=0)
        ax.plot(x, -1.6 + 1.2 * n, color=GREEN, lw=1.5, label=r"密度 $n(\mathbf{r})$（两边相同）")
        ax.set_title(t, fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel("位置（示意）")
        ax.set_ylim(-1.7, 2.6)
    axes[0].legend(frameon=False, fontsize=9, loc="upper center")
    axes[1].text(0, 2.25, r"$v_s = v_{\mathrm{ext}} + v_{\mathrm{H}}[n] + v_{\mathrm{xc}}[n]$", ha="center", fontsize=11)
    save(fig, "kohn-sham-mapping")


def fig_paw_radial():
    r = np.linspace(0.0, 4.0, 800)
    rc = 1.5
    f = r * np.exp(-0.45 * r) * 1.6  # smooth part (pseudo wave function)
    g = np.where(r < rc, 0.55 * np.sin(np.pi * r / rc * 3) * (1 - r / rc) ** 2 * np.exp(-0.4 * r) * 2.2, 0)
    ae = f + g
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    ax.axvspan(0, rc, color=GREY, alpha=0.10, lw=0)
    ax.plot(r, ae, color=BLUE, lw=2, label=r"全电子波函数 $\psi$（核附近剧烈振荡）")
    ax.plot(r, f, color=ORANGE, lw=2, ls="--", label=r"赝波函数 $\tilde\psi$（平滑）")
    ax.axvline(rc, color=GREY, lw=1, ls=":")
    ax.text(rc + 0.05, -0.55, "$r_c$", color=GREY, fontsize=11)
    ax.text(rc / 2, -0.55, "缀加球内：两者不同", ha="center", fontsize=9.5, color=GREY)
    ax.text(2.8, -0.55, "球外：两者重合", ha="center", fontsize=9.5, color=GREY)
    ax.axhline(0, color="k", lw=0.7)
    ax.set_xlabel("到原子核的距离 $r$（示意）")
    ax.set_ylabel(r"$r\,\psi(r)$（任意单位）")
    ax.set_yticks([0])
    ax.set_ylim(-0.7, 1.5)
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    save(fig, "paw-radial")


def fig_planewave_sphere():
    fig, ax = plt.subplots(figsize=(4.4, 4.2))
    ax.set_aspect("equal")
    ax.axis("off")
    gmax = 3.3
    for i in range(-5, 6):
        for j in range(-5, 6):
            inside = i * i + j * j <= gmax**2
            ax.plot(i, j, "o", ms=5 if inside else 3.5, color=BLUE if inside else "#ced4da")
    t = np.linspace(0, 2 * np.pi, 300)
    ax.plot(gmax * np.cos(t), gmax * np.sin(t), color=ORANGE, lw=1.8)
    arrow(ax, 0, 0, gmax * np.cos(0.6), gmax * np.sin(0.6), ORANGE, lw=1.5)
    ax.text(1.0, 1.55, r"$G_{\max}$", color=ORANGE, fontsize=12)
    arrow(ax, 0, 0, 1, 0, "k", lw=1.2, ms=9)
    arrow(ax, 0, 0, 0, 1, "k", lw=1.2, ms=9)
    ax.text(1.05, -0.38, r"$\mathbf{b}_1$", fontsize=10)
    ax.text(-0.45, 1.05, r"$\mathbf{b}_2$", fontsize=10)
    ax.text(0, -5.9, r"保留 $\frac{\hbar^2}{2m}|\mathbf{k}+\mathbf{G}|^2 < E_{\mathrm{cut}}$ 的倒格矢（蓝）", ha="center",
            fontsize=10)
    ax.set_xlim(-5.6, 5.6)
    ax.set_ylim(-6.3, 5.6)
    save(fig, "planewave-sphere")


def fig_reciprocal_bz():
    a1, a2 = np.array([1.0, 0.0]), np.array([0.35, 0.95])
    A = np.array([a1, a2]).T
    B = 2 * np.pi * np.linalg.inv(A).T
    b1, b2 = B[:, 0], B[:, 1]
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.9))
    ax = axes[0]
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("实空间晶格", fontsize=10.5)
    for i in range(-2, 3):
        for j in range(-2, 3):
            p = i * a1 + j * a2
            ax.plot(*p, "o", color=GREY, ms=4)
    arrow(ax, 0, 0, *a1, BLUE, lw=1.8)
    arrow(ax, 0, 0, *a2, BLUE, lw=1.8)
    ax.text(*(a1 + [0.02, -0.25]), r"$\mathbf{a}_1$", color=BLUE)
    ax.text(*(a2 + [-0.3, 0.05]), r"$\mathbf{a}_2$", color=BLUE)
    ax.set_xlim(-2.6, 2.6)
    ax.set_ylim(-2.2, 2.2)
    ax = axes[1]
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("倒空间：第一布里渊区与 4×4 k 点网格", fontsize=10.5)
    # Brillouin zone = points closer to origin than to any other reciprocal lattice point
    L = 6.0
    gx, gy = np.meshgrid(np.linspace(-L, L, 500), np.linspace(-L, L, 500))
    d0 = gx**2 + gy**2
    dmin = np.full_like(d0, np.inf)
    for i in range(-2, 3):
        for j in range(-2, 3):
            if i == 0 and j == 0:
                continue
            g = i * b1 + j * b2
            dmin = np.minimum(dmin, (gx - g[0]) ** 2 + (gy - g[1]) ** 2)
    ax.contourf(gx, gy, (d0 < dmin).astype(float), levels=[0.5, 1.5], colors=[BLUE], alpha=0.12)
    ax.contour(gx, gy, (d0 < dmin).astype(float), levels=[0.5], colors=[BLUE], linewidths=1.5)
    for i in range(-1, 2):
        for j in range(-1, 2):
            g = i * b1 + j * b2
            ax.plot(*g, "o", color=GREY, ms=4)
    arrow(ax, 0, 0, *b1, RED, lw=1.8)
    arrow(ax, 0, 0, *b2, RED, lw=1.8)
    ax.text(*(b1 + [0.15, -0.5]), r"$\mathbf{b}_1$", color=RED)
    ax.text(*(b2 + [0.15, 0.1]), r"$\mathbf{b}_2$", color=RED)
    N = 4
    for n1 in range(1, N + 1):
        for n2 in range(1, N + 1):
            u1, u2 = (2 * n1 - N - 1) / (2 * N), (2 * n2 - N - 1) / (2 * N)
            k = u1 * b1 + u2 * b2
            ax.plot(*k, "s", color=ORANGE, ms=4)
    ax.plot(0, 0, "+", color="k", ms=8)
    ax.text(0.12, 0.12, r"$\Gamma$", fontsize=10)
    ax.set_xlim(-L, L)
    ax.set_ylim(-L * 0.85, L * 0.85)
    save(fig, "reciprocal-bz-kmesh")


def fig_scf_loop():
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.6), gridspec_kw={"width_ratios": [1.05, 1]})
    ax = axes[0]
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    boxes = [(5, 9.0, r"输入密度 $n_{\mathrm{in}}$"), (5, 6.6, r"构造 $v_s[n_{\mathrm{in}}]$"),
             (5, 4.2, "解 Kohn–Sham 方程，得 $\\psi_i$"), (5, 1.8, r"输出密度 $n_{\mathrm{out}}=\sum_i f_i|\psi_i|^2$")]
    for x, y, t in boxes:
        ax.add_patch(FancyBboxPatch((x - 3.3, y - 0.65), 6.6, 1.3, boxstyle="round,pad=0.1", fc="#f1f3f5", ec=GREY))
        ax.text(x, y, t, ha="center", va="center", fontsize=10)
    for y0, y1 in ((8.35, 7.25), (5.95, 4.85), (3.55, 2.45)):
        arrow(ax, 5, y0, 5, y1, "k", lw=1.2, ms=10)
    ax.annotate("", xy=(1.55, 9.0), xytext=(1.55, 1.8),
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.6, connectionstyle="arc3,rad=0"))
    ax.plot([1.55, 1.7], [1.8, 1.8], color=ORANGE, lw=1.6)
    ax.plot([1.55, 1.7], [9.0, 9.0], color=ORANGE, lw=1.6)
    ax.text(1.35, 5.4, "混合：\n新输入由\n$n_{\\mathrm{in}}$ 与\n$n_{\\mathrm{out}}$\n组合", ha="right", va="center", fontsize=9,
            color=ORANGE)
    ax.text(5, 0.25, r"直到 $|n_{\mathrm{out}}-n_{\mathrm{in}}|$ 与能量变化足够小", ha="center", fontsize=9.5, color=GREY)
    ax = axes[1]
    it = np.arange(0, 31)
    ax.semilogy(it, 0.5 * 0.86**it, "o-", ms=3, color=BLUE, lw=1.2, label="简单混合、系数小：稳但慢")
    osc = 0.5 * 1.12**it * (1 + 0.3 * np.cos(it * 2.6))
    ax.semilogy(it[:20], osc[:20], "o-", ms=3, color=RED, lw=1.2, label="简单混合、系数大：振荡发散")
    pul = 0.5 * np.exp(-0.55 * it) * (1 + 0.5 * np.abs(np.sin(it)))
    ax.semilogy(it[:20], pul[:20], "o-", ms=3, color=GREEN, lw=1.2, label="Pulay（DIIS）类混合")
    ax.axhline(1e-6, color=GREY, lw=1, ls=":")
    ax.text(30, 1.6e-6, "收敛阈值", color=GREY, fontsize=9, ha="right")
    ax.set_xlabel("自洽迭代步")
    ax.set_ylabel("密度残差（对数，示意）")
    ax.set_yticks([])
    ax.minorticks_off()
    ax.set_ylim(1e-8, 50)
    ax.legend(frameon=False, fontsize=8.5, loc="lower left")
    save(fig, "scf-loop")


def fig_pbe_enhancement():
    s = np.linspace(0, 3, 300)
    kappa = 0.804
    mu_pbe = 0.2195149727645171
    mu_sol = 10 / 81
    F = lambda mu: 1 + kappa - kappa / (1 + mu * s**2 / kappa)  # noqa: E731
    fig, ax = plt.subplots(figsize=(5.6, 3.5))
    ax.plot(s, np.ones_like(s), color=GREY, lw=1.6, ls="--", label="LDA：$F_x = 1$")
    ax.plot(s, F(mu_pbe), color=BLUE, lw=2, label="PBE")
    ax.plot(s, F(mu_sol), color=ORANGE, lw=2, label="PBEsol（较小的 $\\mu$）")
    ax.axhline(1 + kappa, color=RED, lw=1, ls=":")
    ax.text(0.05, 1 + kappa + 0.03, r"上限 $1+\kappa = 1.804$（局域 Lieb–Oxford 界）", color=RED, fontsize=9.5)
    ax.set_xlabel(r"约化密度梯度 $s = |\nabla n| / (2 k_F n)$")
    ax.set_ylabel(r"交换增强因子 $F_x(s)$")
    ax.set_ylim(0.9, 1.95)
    ax.legend(frameon=False, fontsize=9.5, loc="lower right")
    save(fig, "pbe-enhancement")


def fig_hellmann_feynman():
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.3))
    ax = axes[0]
    lam = np.linspace(-1.2, 1.6, 200)
    E = 0.5 * (lam - 0.4) ** 2 - 0.08 * lam**3
    ax.plot(lam, E, color=BLUE, lw=2)
    l0 = 1.0
    E0 = 0.5 * (l0 - 0.4) ** 2 - 0.08 * l0**3
    dE = (l0 - 0.4) - 0.24 * l0**2
    ax.plot(lam, E0 + dE * (lam - l0), color=ORANGE, lw=1.4, ls="--")
    ax.plot(l0, E0, "o", color=ORANGE)
    ax.text(l0 + 0.05, E0 - 0.17, r"斜率 $\frac{dE}{d\lambda}=\langle\psi|\frac{\partial H}{\partial\lambda}|\psi\rangle$",
            fontsize=10, color=ORANGE)
    ax.set_xlabel(r"参数 $\lambda$（例如原子坐标）")
    ax.set_ylabel(r"基态能量 $E(\lambda)$")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_ylim(-0.25, 0.9)
    ax.set_title("能量的切线斜率 = 力（取负号）", fontsize=10.5)
    ax = axes[1]
    ax.axis("off")
    ax.set_xlim(-0.2, 10.2)
    ax.set_ylim(-0.8, 5.2)
    ax.set_title("基组会不会跟着原子移动", fontsize=10.5)
    x = np.linspace(0, 4.4, 200)
    for c, a in ((1.9, 0.35), (2.5, 1.0)):
        ax.plot(x, 3.2 + 1.2 * np.exp(-((x - c) ** 2) / 0.35), color=BLUE, alpha=a, lw=1.8)
    ax.add_patch(Circle((2.5, 3.2), 0.1, color=RED))
    arrow(ax, 1.9, 2.8, 2.5, 2.8, RED, lw=1.2, ms=9)
    ax.text(2.2, 2.25, "原子居中的基函数\n随原子移动 → Pulay 力", ha="center", fontsize=9, color=BLUE)
    x2 = np.linspace(5.6, 10, 300)
    for k in (1, 2, 3):
        ax.plot(x2, 3.4 + 0.25 * k + 0.22 * np.cos(2 * np.pi * k * (x2 - 5.6) / 4.4), color=GREEN, lw=1.2)
    ax.add_patch(Circle((8.1, 3.2), 0.1, color=RED))
    arrow(ax, 7.5, 2.8, 8.1, 2.8, RED, lw=1.2, ms=9)
    ax.text(7.8, 2.25, "平面波固定在晶胞上\n原子移动时不变 → 无 Pulay 力", ha="center", fontsize=9, color=GREEN)
    ax.text(5.0, 0.3, "但晶胞形状变化时平面波会变 → Pulay 应力", ha="center", fontsize=9.5, color=ORANGE)
    save(fig, "hellmann-feynman-pulay")


def fig_two_level():
    lam = np.linspace(-1.0, 1.0, 300)
    d, v = 1.0, 0.9
    ep = 0.5 * np.sqrt(d**2 + (2 * v * lam) ** 2)
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    ax.plot(lam, ep, color=BLUE, lw=2, label=r"精确能级 $E_\pm(\lambda)$")
    ax.plot(lam, -ep, color=BLUE, lw=2)
    ax.plot(lam, 0.5 + (v * lam) ** 2 / d, color=ORANGE, lw=1.5, ls="--", label="二阶微扰近似")
    ax.plot(lam, -0.5 - (v * lam) ** 2 / d, color=ORANGE, lw=1.5, ls="--")
    ax.axhline(0.5, color=GREY, lw=1, ls=":")
    ax.axhline(-0.5, color=GREY, lw=1, ls=":")
    ax.annotate("", xy=(-0.9, 0.5), xytext=(-0.9, -0.5), arrowprops=dict(arrowstyle="<->", color=GREY))
    ax.text(-0.86, 0.0, r"$\Delta$", color=GREY, fontsize=12, va="center")
    ax.text(0.98, 0.6, "未扰动能级", color=GREY, fontsize=9, ha="right")
    ax.set_xlabel(r"扰动强度 $\lambda$")
    ax.set_ylabel("能量")
    ax.set_xticks([0])
    ax.set_yticks([])
    ax.set_ylim(-1.35, 1.35)
    ax.legend(frameon=False, fontsize=9.5, loc="upper center")
    save(fig, "two-level-perturbation")


def fig_diatomic_chain():
    m1, m2, K = 1.0, 2.0, 1.0
    q = np.linspace(-np.pi, np.pi, 400)  # q a, with a the cell length
    s = K * (1 / m1 + 1 / m2)
    root = np.sqrt(s**2 - 4 * K**2 * np.sin(q / 2) ** 2 / (m1 * m2))
    w_ac = np.sqrt(s - root)
    w_op = np.sqrt(s + root)
    fig = plt.figure(figsize=(6.2, 4.4))
    ax0 = fig.add_axes([0.08, 0.80, 0.86, 0.17])
    ax0.axis("off")
    ax0.set_xlim(-0.5, 8.5)
    ax0.set_ylim(-0.7, 0.8)
    for k in range(4):
        x1, x2 = 2 * k, 2 * k + 1
        ax0.plot([x1, x2], [0, 0], color=GREY, lw=1.2, zorder=0)
        if k < 3:
            ax0.plot([x2, x2 + 1], [0, 0], color=GREY, lw=1.2, zorder=0)
        ax0.add_patch(Circle((x1, 0), 0.18, color=BLUE))
        ax0.add_patch(Circle((x2, 0), 0.26, color=ORANGE))
    ax0.text(0, 0.42, "$m_1$", ha="center", color=BLUE)
    ax0.text(1, 0.48, "$m_2$", ha="center", color=ORANGE)
    ax0.text(0.5, -0.55, "$K$", ha="center", color=GREY)
    ax0.annotate("", xy=(2, -0.45), xytext=(0, -0.45), arrowprops=dict(arrowstyle="<->", color=GREY, lw=0.8))
    ax0.text(1.6, -0.65, "$a$", ha="center", color=GREY, va="top")
    ax = fig.add_axes([0.12, 0.10, 0.82, 0.62])
    ax.plot(q, w_ac, color=BLUE, lw=2, label="声学支")
    ax.plot(q, w_op, color=ORANGE, lw=2, label="光学支")
    ax.axvline(0, color=GREY, lw=0.8, ls=":")
    ax.set_xticks([-np.pi, 0, np.pi])
    ax.set_xticklabels([r"$-\pi/a$", r"$\Gamma$", r"$\pi/a$"])
    ax.set_yticks([0])
    ax.set_xlabel("波矢 $q$")
    ax.set_ylabel(r"频率 $\omega(q)$")
    ax.fill_between(q, np.sqrt(2 * K / m2), np.sqrt(2 * K / m1), color=GREY, alpha=0.12, lw=0)
    ax.text(0, (np.sqrt(2 * K / m2) + np.sqrt(2 * K / m1)) / 2, "频隙", ha="center", va="center", fontsize=9.5,
            color=GREY)
    ax.legend(frameon=False, fontsize=9.5, loc="lower right")
    ax.set_ylim(0, 2.0)
    save(fig, "diatomic-chain-phonons")


if __name__ == "__main__":
    for f in (fig_tensor_rotation, fig_kohn_sham_map, fig_paw_radial, fig_planewave_sphere, fig_reciprocal_bz,
              fig_scf_loop, fig_pbe_enhancement, fig_hellmann_feynman, fig_two_level, fig_diatomic_chain):
        f()
    print("figures written to", OUT)
