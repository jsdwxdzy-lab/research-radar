"""Figures for the theory map: Born-Oppenheimer surfaces.

Run from the repository root:  python3 knowledge/figs/make_figs_bo.py
Writes knowledge/figs/born-oppenheimer-surfaces.svg. Toy two-state model chosen to show
an avoided crossing; not data for any molecule.
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


R = np.linspace(0.7, 3.3, 500)
Rc = 1.9
gap = 0.32
v11 = 0.9 * (R - 1.35) ** 2 - 0.05
v22 = 0.55 * (R - 2.55) ** 2 + 0.55
W = np.full_like(R, gap / 2)
mean = 0.5 * (v11 + v22)
diff = 0.5 * (v11 - v22)
adiab_low = mean - np.sqrt(diff**2 + W**2)
adiab_high = mean + np.sqrt(diff**2 + W**2)

fig, ax = plt.subplots(figsize=(6.6, 4.4))
ax.plot(R, v11, color=GREY, lw=1.1, ls="--", label="透热态 1（示意）")
ax.plot(R, v22, color=GREY, lw=1.1, ls=":", label="透热态 2（示意）")
ax.plot(R, adiab_low, color=BLUE, lw=2.0, label=r"$E_0(R)$ 基态")
ax.plot(R, adiab_high, color=RED, lw=2.0, label=r"$E_1(R)$ 第一激发态")
ax.axvline(Rc, color=INK, lw=1.0, ls="-.")
ax.annotate("", xy=(Rc, adiab_high[np.argmin(abs(R - Rc))]), xytext=(Rc, adiab_low[np.argmin(abs(R - Rc))]),
            arrowprops=dict(arrowstyle="<->", color=ORANGE, lw=1.4))
ax.text(Rc + 0.05, 0.72, "能隙最小处", color=ORANGE, fontsize=10)
ax.text(Rc + 0.05, 0.30, r"$R_c$", color=INK, fontsize=11)
ax.set_xlabel(r"核坐标 $R$（示意单位）")
ax.set_ylabel("能量（示意单位）")
ax.set_title("（示意）两个电子态的避免交叉：远离 $R_c$ 时绝热态接近透热态")
ax.set_xlim(0.7, 3.3)
ax.set_ylim(-0.45, 2.6)
ax.legend(frameon=False, fontsize=9, loc="upper left")
ax.set_yticks([])
fig.tight_layout()
save(fig, "born-oppenheimer-surfaces")
