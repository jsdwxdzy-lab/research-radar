#!/usr/bin/env python3
"""Generate figures for theory-harvest 2026-11-24 nodes."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Ellipse, FancyBboxPatch

plt.rcParams["svg.fonttype"] = "path"
plt.rcParams["svg.hashsalt"] = "theory-map"
plt.rcParams["font.family"] = "Arial Unicode MS"

OUT = Path(__file__).resolve().parent


def fig_longitudinal():
    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    ax.set_aspect("equal")
    ax.set_xlim(-1.35, 1.55)
    ax.set_ylim(-1.25, 1.35)
    ax.axis("off")

    th = np.linspace(0, 2 * np.pi, 200)
    ax.plot(np.cos(th), np.sin(th), color="#4a5568", lw=1.2)
    ax.plot(
        0.75 * np.cos(th),
        0.45 * np.sin(th) - 0.05,
        color="#a0aec0",
        lw=0.8,
        ls="--",
    )

    ax.annotate(
        "",
        xy=(1.05, 0),
        xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", color="#718096", lw=1),
    )
    ax.annotate(
        "",
        xy=(0, 1.05),
        xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", color="#718096", lw=1),
    )
    ax.text(1.1, -0.12, "x", fontsize=11, color="#718096")
    ax.text(0.08, 1.08, "y", fontsize=11, color="#718096")

    ang = np.deg2rad(38)
    n = np.array([np.cos(ang), np.sin(ang)])
    ax.annotate(
        "",
        xy=n * 0.95,
        xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", color="#c53030", lw=2.2),
    )
    ax.text(
        n[0] * 1.08,
        n[1] * 1.08,
        r"$\mathbf{n}$",
        fontsize=13,
        color="#c53030",
    )

    ax.annotate(
        "",
        xy=n * 1.22,
        xytext=n * 0.98,
        arrowprops=dict(arrowstyle="->", color="#2b6cb0", lw=1.8),
    )
    ax.text(
        n[0] * 1.28 + 0.05,
        n[1] * 1.18,
        r"$\Delta P_\parallel$",
        fontsize=11,
        color="#2b6cb0",
    )

    p0 = n * 0.55
    t = np.array([-n[1], n[0]])
    for s in (-0.12, 0.12):
        q = p0 + s * t
        ax.plot(
            [q[0] - 0.08 * n[0], q[0] + 0.08 * n[0]],
            [q[1] - 0.08 * n[1], q[1] + 0.08 * n[1]],
            color="#2f855a",
            lw=1.5,
        )
    ax.text(
        -0.15,
        -1.15,
        r"纵向：$d_L(\mathbf{n})=\mathbf{n}\cdot\mathbf{d}:\mathbf{n}\mathbf{n}$（示意）",
        fontsize=10,
    )

    fig.savefig(
        OUT / "longitudinal-piezo-direction.svg",
        format="svg",
        bbox_inches="tight",
        metadata={"Date": None},
    )
    plt.close()


def fig_rigid():
    fig, ax = plt.subplots(figsize=(5.4, 3.6))
    ax.set_aspect("equal")
    ax.set_xlim(-0.2, 5.4)
    ax.set_ylim(-0.3, 3.2)
    ax.axis("off")

    cell = FancyBboxPatch(
        (0.3, 0.4),
        4.6,
        2.4,
        boxstyle="round,pad=0.02",
        linewidth=1.2,
        edgecolor="#4a5568",
        facecolor="#f7fafc",
    )
    ax.add_patch(cell)
    ax.text(0.4, 2.95, "晶胞（示意）", fontsize=10, color="#4a5568")

    mol = Ellipse(
        (2.4, 1.55),
        1.6,
        0.85,
        angle=25,
        facecolor="#fed7d7",
        edgecolor="#c53030",
        lw=1.6,
    )
    ax.add_patch(mol)
    ax.text(2.05, 1.45, "刚体分子", fontsize=10, color="#9b2c2c")

    ax.annotate(
        "",
        xy=(3.55, 1.55),
        xytext=(3.15, 1.55),
        arrowprops=dict(arrowstyle="->", color="#2b6cb0", lw=1.8),
    )
    ax.annotate(
        "",
        xy=(2.4, 2.25),
        xytext=(2.4, 1.95),
        arrowprops=dict(arrowstyle="->", color="#2b6cb0", lw=1.8),
    )
    ax.text(3.6, 1.65, r"平动 $t$", fontsize=11, color="#2b6cb0")

    arc = Arc(
        (2.4, 1.55), 1.9, 1.9, angle=0, theta1=40, theta2=110, color="#276749", lw=1.8
    )
    ax.add_patch(arc)
    ax.annotate(
        "",
        xy=(2.05, 2.35),
        xytext=(2.2, 2.45),
        arrowprops=dict(arrowstyle="->", color="#276749", lw=1.5),
    )
    ax.text(1.0, 2.45, r"转动 $\theta$", fontsize=11, color="#276749")

    ax.plot([1.75, 2.05], [1.2, 1.35], "o-", color="#718096", ms=3, lw=1)
    ax.plot([2.05, 2.45], [1.35, 1.15], "o-", color="#718096", ms=3, lw=1)
    ax.plot([2.45, 2.85], [1.15, 1.4], "o-", color="#718096", ms=3, lw=1)
    ax.text(0.5, 0.55, "键长/键角冻结（示意）", fontsize=9, color="#718096")

    fig.savefig(
        OUT / "rigid-molecule-dof.svg",
        format="svg",
        bbox_inches="tight",
        metadata={"Date": None},
    )
    plt.close()


if __name__ == "__main__":
    fig_longitudinal()
    fig_rigid()
    print("wrote", OUT / "longitudinal-piezo-direction.svg")
    print("wrote", OUT / "rigid-molecule-dof.svg")
