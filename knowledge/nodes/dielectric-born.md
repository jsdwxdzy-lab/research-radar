```json
{
  "id": "dielectric-born",
  "title": "介电张量与玻恩有效电荷",
  "type": "concept",
  "parent": "energy-structure-response",
  "research": [
    "piezo"
  ],
  "keywords": [
    "dielectric tensor",
    "Born effective charge",
    "LEPSILON"
  ],
  "purpose": "电场与原子位移之间的耦合：介电响应和玻恩有效电荷描述什么，怎样计算。",
  "prereq": {
    "intuitive": [
      "电偶极矩、极化与电场",
      "[[energy-structure-response]] 里的力常数矩阵"
    ],
    "full": [
      "[[perturbation-theory]] 与 [[phonons]] 的简正模式",
      "[[berry-phase-polarization]]"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "gonze-1997-dfpt",
    "baroni-2001-dfpt",
    "vasp-wiki-lepsilon"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：Z* 定义与求和规则、ε∞ 与 ε0、模式分解、VASP 对应与常见坑；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

把一个原子挪动一点，晶体的宏观极化会变多少？如果离子是带固定电荷的刚性小球，答案就是“名义电荷 × 位移”。真实体系里电子云不会刚性跟着原子走，周围原子的电子也会重新分布，所以实际的偶极变化可以比名义电荷大很多，方向也可以不同。这个“实际的”比例就是**玻恩有效电荷** (Born effective charge) $Z^{*}$。

$Z^{*}$ 是电场和原子运动之间的耦合常数，从两个方向读都一样：原子位移引起多少极化；电场在原子上产生多大的力。所以它同时出现在：

- 介电响应的离子部分（电场推动原子，原子位移再贡献极化）；
- 压电响应的内应变项（应变推动原子，原子位移再贡献极化，见 [[piezoelectric-tensor]]）。

![左：刚性离子模型，偶极变化等于名义电荷乘位移。右：真实体系中电子云滞后、邻近原子响应，有效电荷 Z* 与名义电荷不同。](figs/born-charge.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $u$ | 一个原子的位移 | 橙色箭头 |
| $Z_{\mathrm{nom}}$ | 名义（形式）电荷 | 左图：浅色圆是原位置，深色圆是新位置，电子云整体跟随 |
| $Z^{*}$ | 玻恩有效电荷 | 右图：电子云（浅蓝）没完全跟上，邻近原子（红）也有响应 |
| $\Delta p$ | 晶胞偶极变化 | 两图上方公式 |

## 定义与公式 {math}

::: definition 玻恩有效电荷
$$Z^{*}_{\kappa,\alpha\beta} = \frac{\Omega}{e}\,\left.\frac{\partial P_\alpha}{\partial u_{\kappa\beta}}\right|_{\mathcal{E}=0} = \frac{1}{e}\,\left.\frac{\partial F_{\kappa\beta}}{\partial \mathcal{E}_\alpha}\right|_{u=0}$$

其中 $\kappa$ 标记晶胞中的原子；$\alpha, \beta$ 是笛卡尔方向；$u_{\kappa\beta}$ 是原子 $\kappa$ 在 $\beta$ 方向的位移（所有周期像一起移动）；$P_\alpha$ 是宏观极化；$\Omega$ 是晶胞体积；$e$ 是元电荷；$F_{\kappa\beta}$ 是原子受力；$\mathcal{E}$ 是宏观电场。两种写法相等，因为它们是同一个能量 $E(u, \mathcal{E})$ 的混合二阶导数 [@gonze-1997-dfpt]。
:::

$Z^{*}$ 对每个原子是一个 $3\times 3$ 张量，一般不对称。

::: theorem 声学求和规则
整个晶体整体平移不改变极化，所以

$$\sum_{\kappa} Z^{*}_{\kappa,\alpha\beta} = 0$$

其中求和遍历晶胞中所有原子。数值计算一般只近似满足这一条，偏离的大小可以作为计算质量的一个检查 [@gonze-1997-dfpt]。
:::

### 两种介电常数

::: definition 高频与静态介电张量
$$\varepsilon^{\infty}_{\alpha\beta} = \delta_{\alpha\beta} + 4\pi\,\left.\frac{\partial P_\alpha}{\partial \mathcal{E}_\beta}\right|_{u}, \qquad \varepsilon^{0}_{\alpha\beta} = \varepsilon^{\infty}_{\alpha\beta} + \frac{4\pi e^{2}}{\Omega}\sum_{m} \frac{S_{m,\alpha\beta}}{\omega_m^{2}}$$

其中下标 $u$ 表示原子位置固定；$\varepsilon^{\infty}$ 只含电子的响应（原子不动，对应远高于声子频率的光频）；$\varepsilon^{0}$ 还包含原子位移的贡献；求和遍历布里渊区中心的光学模式 $m$；$\omega_m$ 是模式频率；$S_{m,\alpha\beta} = \bigl(\sum_{\kappa\gamma} Z^{*}_{\kappa,\alpha\gamma}\,U_{m,\kappa\gamma}\bigr)\bigl(\sum_{\kappa'\gamma'} Z^{*}_{\kappa',\beta\gamma'}\,U_{m,\kappa'\gamma'}\bigr)$ 是模式振子强度；$U_m$ 是按质量归一化的模式位移向量。这里用高斯单位，SI 单位下 $4\pi$ 换成 $1/\varepsilon_0$ [@gonze-1997-dfpt]。
:::

上式和 [[energy-structure-response]] 中的 $u^{*} = K^{-1}f$ 是同一个结构：电场给原子的力是 $Z^{*}\mathcal{E}$，位移由力常数的逆给出，再乘 $Z^{*}$ 回到极化。分母里的 $\omega_m^{2}$ 就是力常数矩阵的本征值，所以**低频而又带电的模式**主导离子介电响应，也最容易放大误差。

::: unverified 待核验
- 振子强度的归一化（是否含质量因子、$\Omega$ 放在哪里）按 [@gonze-1997-dfpt] 的式子逐项核对。
:::

## 在本研究线里的样子 {mapping}

- **VASP**：`LEPSILON = .TRUE.` 用微扰方法计算 $\varepsilon^{\infty}$、玻恩电荷和夹持离子压电张量 [@vasp-wiki-lepsilon]；配合 `IBRION = 7` 或 `8` 还会给出离子对介电张量的贡献。具体能和哪些设置组合（例如对泛函、自旋的限制）以文档为准。
- **β-甘氨酸**：两性离子 $\mathrm{NH_3^{+}}$、$\mathrm{COO^{-}}$ 上的原子预计有较大的 $Z^{*}$。它们和氢键网络中的软模式一起，决定内应变项的大小。哪个原子贡献最大，应从实际计算的 $Z^{*}$ 和模式分解读出，这里不预设。
- **机器学习势**：通常的 MACE 势只拟合能量和力，不给 $Z^{*}$，所以压电的离子项需要 DFT 的 $Z^{*}$，或者另外训练预测 $Z^{*}$ 的模型（见 [[mlip-electrostatics]]）。

## 常见坑 {mapping}

- **求和规则偏离大**：通常说明 k 点或截断能不够，或者自洽不够紧（`EDIFF`）。
- **$\varepsilon^{\infty}$ 与 $\varepsilon^{0}$ 混用**：和实验比较时，要看实验测的是光频还是低频介电常数。
- **局域场效应**：在 DFT 中是否包含局域场效应，会改变 $\varepsilon^{\infty}$ 的数值；VASP 的设置要看清楚是否包含交换相关的局域场贡献。
- **金属或带隙很小**：$Z^{*}$ 和介电张量对小带隙体系不再有通常的意义；半局域泛函低估带隙，会让 $\varepsilon^{\infty}$ 偏大。

## 检验自己 {mapping}

::: question 解释
为什么 $Z^{*}$ 可以同时理解为“位移引起的极化”和“电场引起的力”？
:::

::: question 推导
只有一个光学模式时，写出 $\varepsilon^{0} - \varepsilon^{\infty}$。如果这个模式的频率被低估 10%，它的贡献变大多少？
:::

::: question 迁移
如果计算得到某个原子的 $Z^{*}$ 远大于它的名义电荷，这说明了它周围电子结构的什么特点？
:::
