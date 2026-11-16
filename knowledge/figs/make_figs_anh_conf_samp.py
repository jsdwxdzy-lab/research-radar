"""Figures for the theory map (batch: enhanced sampling, conformational polymorphism, anharmonicity).

Run from the repository root:  python3 knowledge/figs/make_figs_anh_conf_samp.py
Writes knowledge/figs/<name>.svg. All three figures are schematic or use toy model functions chosen to show
an idea; they are not data for any material.
Set FIG_PREVIEW_DIR to also write PNG copies (outside the repository) for checking.
"""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Arc, FancyArrowPatch  # noqa: E402

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


def arrow(ax, x0, y0, x1, y1, color="k", lw=1.3, ms=11):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw,
                                 shrinkA=0, shrinkB=0))


# ---------------------------------------------------------------------------
# 1. Enhanced sampling: umbrella windows and reweighting
def fig_enhanced_sampling():
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 3.9))

    # --- left: free energy profile with umbrella windows
    ax = axes[0]
    xi = np.linspace(-2.2, 2.2, 500)
    # double well with a barrier, in reduced units (k_B T = 1)
    f0 = 0.9 * (xi ** 2 - 1.0) ** 2 + 0.55 * np.exp(-((xi - 0.0) ** 2) / 0.55) * 0
    f0 = f0 + 0.35 * xi
    f0 -= f0.min()
    ax.plot(xi, f0, color="k", lw=2, label="真实自由能 F(ξ)")
    centers = np.linspace(-1.5, 1.5, 7)
    kappa = 3.0
    for c in centers:
        b = 0.5 * kappa * (xi - c) ** 2
        ax.plot(xi, f0 + b, color=BLUE, lw=0.9, alpha=0.75,
                label="F(ξ) + w_i(ξ)" if c == centers[0] else None)
        ax.plot([c, c], [-0.28, -0.05], color=BLUE, lw=2.2,
                label="窗口中心 ξ_i" if c == centers[0] else None)
    ax.set_ylim(-0.4, 3.0)
    ax.set_xlim(-2.2, 2.2)
    ax.set_xlabel("反应坐标 ξ")
    ax.set_ylabel("能量 (k_B T)")
    ax.set_title("加偏置：每个窗口一条抛物线偏置", fontsize=11)
    ax.legend(fontsize=8.5, frameon=False, loc="upper center", ncol=2, handlelength=1.4)

    # --- right: biased distribution (sum over windows) -> reweighted
    ax = axes[1]
    dxi = xi[1] - xi[0]
    p_b = np.zeros_like(xi)
    for c in centers:
        w_i = 0.5 * kappa * (xi - c) ** 2
        p_i = np.exp(-(f0 + w_i) / 1.0)          # k_B T = 1
        p_i /= p_i.sum() * dxi
        p_b += p_i / len(centers)
    ax.plot(xi, p_b, color=GREY, lw=1.0)
    ax.fill_between(xi, 0, p_b, color="#ced4da", alpha=0.85,
                    label="偏置采样得到的 $p_b(ξ)$（各窗口之和）")
    nearest = centers[np.argmin(np.abs(xi[:, None] - centers[None, :]), axis=1)]
    w_near = 0.5 * kappa * (xi - nearest) ** 2
    p0 = p_b * np.exp(w_near)                    # divide out the bias
    p0 /= p0.sum() * dxi
    ax.plot(xi, p0, color=ORANGE, lw=2, label="重加权后 $p_0(ξ) \\propto p_b e^{+βw}$")
    ax.set_ylim(0, None)
    ax.set_xlim(-2.2, 2.2)
    ax.set_xlabel("反应坐标 ξ")
    ax.set_ylabel("概率密度")
    ax.set_title("重加权：把偏置除掉", fontsize=11)
    ax.legend(fontsize=8.5, frameon=False, loc="upper right")
    save(fig, "enhanced-sampling-bias")


# ---------------------------------------------------------------------------
# 2. Conformational polymorphism: conformational cost vs packing gain
def fig_conformational_polymorphism():
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 3.9), gridspec_kw={"width_ratios": [1.0, 1.15]})

    # --- left: two conformers sketched by the torsion angle
    ax = axes[0]
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.4, 1.5)
    ax.axis("off")
    # conformer A: torsion 0
    for x0, lab, th, col in ((-0.85, "构象 A", 0.0, BLUE), (0.55, "构象 B", 0.75, RED)):
        ax.plot([x0 - 0.45, x0], [0, 0], color=col, lw=2.2, solid_capstyle="round")
        ax.plot([x0, x0 + 0.37 * np.cos(th)], [0, 0.37 * np.sin(th)], color=col, lw=2.2, solid_capstyle="round")
        ax.plot([x0 + 0.37 * np.cos(th), x0 + 0.37 * np.cos(th) + 0.34],
                [0.37 * np.sin(th), 0.37 * np.sin(th)], color=col, lw=2.2, solid_capstyle="round")
        ax.scatter([x0], [0], s=55, color=col, zorder=3)
        ax.text(x0, -0.30, lab, ha="center", fontsize=10, color=col)
        if th > 0:
            ax.add_patch(Arc((x0, 0), 0.52, 0.52, theta1=0, theta2=43, color=col, lw=1.0))
            ax.text(x0 + 0.30, 0.22, "θ", color=col, fontsize=11)
    ax.text(0, 1.05, "同一分子，不同扭转角 θ", ha="center", fontsize=10.5)
    ax.text(0, 0.62, "→ 不同晶体堆积", ha="center", fontsize=10.5, color=GREY)

    # --- right: E_conf(θ) and packing energy vs θ
    ax = axes[1]
    th = np.linspace(0, np.pi, 300)
    e_conf = 6.0 * np.sin(th) ** 2          # conformational cost, minimum at 0
    e_pack = -8.5 * (1 - np.exp(-((th - 0.95) ** 2) / 0.35))  # packing gain, best near theta ~ 0.95
    ax.plot(th, e_conf, color=BLUE, lw=2, label="构象能 $E_{conf}(θ)$")
    ax.plot(th, e_pack - 0.0, color=GREEN, lw=2, label="堆积能 $E_{pack}(θ)$")
    tot = e_conf + e_pack
    ax.plot(th, tot, color="k", lw=2.2, label="总和")
    i0 = int(np.argmin(e_conf))
    i1 = int(np.argmin(tot))
    ax.scatter([th[i0]], [e_conf[i0]], s=40, color=BLUE, zorder=4)
    ax.scatter([th[i1]], [tot[i1]], s=55, facecolor="none", edgecolor=RED, lw=1.6, zorder=5)
    ax.annotate("气相最优构象\n（堆积不一定最好）", xy=(th[i0] + 0.03, e_conf[i0] + 0.15), xytext=(0.02, 5.05),
                fontsize=9, color=BLUE, ha="left", arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    ax.annotate("晶体的最优构象\n（构象代价被堆积能补偿）", xy=(th[i1] - 0.05, tot[i1] - 0.25), xytext=(0.78, -6.7),
                fontsize=9, color=RED, arrowprops=dict(arrowstyle="-", color=RED, lw=0.7))
    ax.set_xlabel("扭转角 θ (rad)")
    ax.set_ylabel("相对能量 (kJ/mol，示意)")
    ax.axhline(0, color=GREY, lw=0.7, ls=":")
    ax.legend(fontsize=8.5, frameon=False, loc="upper right")
    save(fig, "conformational-polymorphism")


# ---------------------------------------------------------------------------
# 3. Anharmonicity: real well vs harmonic, frequency softening, free energy shift
def fig_anharmonicity():
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 3.9))

    # --- left: Morse-like well vs harmonic
    ax = axes[0]
    x = np.linspace(-1.1, 1.5, 400)
    a, de = 1.35, 2.2
    morse = de * (1 - np.exp(-a * x)) ** 2
    harm = 0.5 * (2 * de * a ** 2) * x ** 2
    ax.plot(x, harm, color=GREY, lw=1.8, ls="--", label="谐振近似 $\\frac{1}{2}\\Phi u^2$")
    ax.plot(x, morse, color=PURPLE, lw=2.2, label="真实势（Morse 型示意）")
    ax.set_ylim(0, 2.6)
    ax.set_xlim(-1.1, 1.5)
    ax.axhline(0.55, color=BLUE, lw=1.0, ls=":")
    ax.axhline(1.15, color=ORANGE, lw=1.0, ls=":")
    ax.text(-1.08, 0.55, "低温", color=BLUE, fontsize=9.5, va="center")
    ax.text(-1.08, 1.15, "高温", color=ORANGE, fontsize=9.5, va="center")
    ax.annotate("", xy=(0.62, 0.55), xytext=(-0.62, 0.55), arrowprops=dict(arrowstyle="<->", color=BLUE, lw=1.0))
    ax.annotate("", xy=(1.02, 1.15), xytext=(-0.72, 1.15), arrowprops=dict(arrowstyle="<->", color=ORANGE, lw=1.0))
    ax.set_xlabel("位移 u")
    ax.set_ylabel("能量 (示意)")
    ax.legend(fontsize=8.8, frameon=False, loc="upper left")
    ax.set_title("真实势阱不对称：压缩比拉伸更“硬”", fontsize=10.5)

    # --- right: frequency vs T and free energy difference
    ax = axes[1]
    T = np.linspace(0, 900, 300)
    w0, alpha = 200.0, 3.2e-4
    w_harm = np.full_like(T, w0)
    w_anh = w0 * (1 - alpha * T)
    ax.plot(T, w_harm, color=GREY, lw=1.8, ls="--", label="谐振：频率不随 T 变")
    ax.plot(T, w_anh, color=PURPLE, lw=2.2, label="非谐：声子软化")
    ax.set_xlabel("温度 T (K)")
    ax.set_ylabel("声子频率 (cm⁻¹，示意)")
    ax.set_ylim(120, 215)
    ax2 = ax.inset_axes([0.56, 0.13, 0.40, 0.34])
    k_b = 1.0
    # toy: F_anh - F_harm using a shift of the effective frequency (sign only, schematic)
    dF = -1.9 * (T / 900.0) ** 2
    ax2.plot(T, dF, color=ORANGE, lw=1.8)
    ax2.axhline(0, color=GREY, lw=0.6, ls=":")
    ax2.set_title("ΔF = F_anh − F_harm", fontsize=7.5)
    ax2.tick_params(labelsize=6.5)
    ax2.set_xlabel("T", fontsize=7)
    ax.legend(fontsize=8.8, frameon=False, loc="upper right")
    save(fig, "anharmonicity-well")


if __name__ == "__main__":
    fig_enhanced_sampling()
    fig_conformational_polymorphism()
    fig_anharmonicity()
    print("wrote:", OUT)
