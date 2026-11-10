```json
{
  "id": "hellmann-feynman",
  "title": "Hellmann–Feynman 定理：力与应力",
  "type": "concept",
  "parent": "quantum",
  "keywords": [
    "Hellmann-Feynman theorem",
    "forces",
    "stress tensor",
    "Pulay force"
  ],
  "purpose": "为什么 DFT 一次计算就能给出所有原子上的力和应力，什么时候要加 Pulay 修正。",
  "prereq": {
    "intuitive": [
      "能量对参数求导",
      "[[variational-principle]]：基态能量的稳定性"
    ],
    "full": [
      "[[kohn-sham-dft]]",
      "[[plane-waves]]"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "feynman-1939-forces",
    "pulay-1969-forces",
    "nielsen-1985-stress",
    "payne-1992-iterative"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：定理与证明思路、原子力、Pulay 力、应力定理与 Pulay 应力、对 SCF 收敛的要求、常见坑；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

要算原子上的力，最直接的做法是把每个原子沿每个方向挪一点，看能量怎么变。N 个原子要算 6N 次，太贵了。

Hellmann–Feynman 定理说：如果波函数是哈密顿量的精确本征态，那么能量对任意参数的导数，等于哈密顿量对该参数的导数的期望值。**波函数本身怎么变不需要知道**。原因是基态能量对波函数是变分稳定的：波函数的一阶变化不改变能量（见 [[variational-principle]]）。

所以一次 SCF 计算之后，就能直接算出所有原子上的力和晶胞应力。这是结构优化和分子动力学能够负担得起的原因。

但有一个条件：如果**基函数**本身随参数移动（例如以原子为中心的高斯基组），波函数的变化就不完全在基组能描述的空间里，需要加一个修正项，叫 Pulay 力 [@pulay-1969-forces]。

![左：能量随参数 λ 的变化，切线斜率就是 ∂H/∂λ 的期望值。右（示意）：原子移动时，原子中心基函数跟着移动，产生 Pulay 力；平面波不随原子移动，没有 Pulay 力；但晶胞变形会改变平面波，产生 Pulay 应力。](figs/hellmann-feynman-pulay.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $\lambda$ | 哈密顿量中的参数（原子坐标、应变等） | 左图横轴 |
| $E(\lambda)$ | 基态能量 | 左图蓝色曲线 |
| $\langle\partial H/\partial\lambda\rangle$ | Hellmann–Feynman 导数 | 左图橙色切线的斜率 |
| 高斯基函数 | 以原子为中心的基函数 | 右上图随原子移动的包络 |
| 平面波 | 不依赖原子位置的基函数 | 右下图固定的波 |

## 定义与公式 {math}

::: theorem Hellmann–Feynman 定理
设 $H(\lambda)\,|\psi(\lambda)\rangle = E(\lambda)\,|\psi(\lambda)\rangle$，且 $\langle\psi|\psi\rangle = 1$，则

$$\frac{\mathrm{d}E}{\mathrm{d}\lambda} = \Bigl\langle \psi \Bigm| \frac{\partial H}{\partial\lambda} \Bigm| \psi \Bigr\rangle$$

其中 $\lambda$ 是哈密顿量中的任意参数，$|\psi\rangle$ 是归一化本征态 [@feynman-1939-forces]。
:::

证明思路：对 $E = \langle\psi|H|\psi\rangle$ 求导，得到三项。含 $\partial\psi/\partial\lambda$ 的两项合起来是 $E\,\frac{\mathrm{d}}{\mathrm{d}\lambda}\langle\psi|\psi\rangle = 0$，只剩中间一项。

### 原子上的力

取 $\lambda$ 为原子 $I$ 的坐标 $\mathbf{R}_I$。在 Born–Oppenheimer 近似下（见 [[born-oppenheimer]]），哈密顿量中只有电子–核吸引和核–核排斥显含 $\mathbf{R}_I$：

$$\mathbf{F}_I = -\frac{\partial E}{\partial \mathbf{R}_I} = -\int n(\mathbf{r})\,\frac{\partial v_{\mathrm{ext}}(\mathbf{r})}{\partial \mathbf{R}_I}\,\mathrm{d}\mathbf{r} - \frac{\partial E_{\mathrm{II}}}{\partial \mathbf{R}_I}$$

其中 $n$ 是电子密度，$v_{\mathrm{ext}}$ 是原子核（或赝势）产生的外势，$E_{\mathrm{II}}$ 是核–核排斥能。在 Kohn–Sham DFT 中同样成立，前提是 KS 方程已经自洽求解。

::: definition Pulay 力
若基函数 $\chi_\mu$ 依赖于 $\mathbf{R}_I$，力中多出一项，来自基函数的移动：

$$\mathbf{F}_I^{\mathrm{Pulay}} \propto \sum_{n}\sum_{\mu\nu} c^{*}_{n\mu}\,c_{n\nu}\left\langle \frac{\partial\chi_\mu}{\partial\mathbf{R}_I}\Bigm|H - \varepsilon_n\Bigm|\chi_\nu\right\rangle + \text{c.c.}$$

其中 $c_{n\mu}$ 是展开系数，$\varepsilon_n$ 是本征值，c.c. 表示复共轭。基组完备时这一项为零 [@pulay-1969-forces]。平面波不依赖原子位置，所以没有这一项 [@payne-1992-iterative]。
:::

::: unverified 待核验
- 上式的前因子与具体形式取决于约定，按 Pulay 原文核对后补全；这里只用于说明来源。
:::

### 应力

把参数取为应变 $\varepsilon_{\alpha\beta}$，可以用同样思路导出应力，称为应力定理 [@nielsen-1985-stress]：

$$\sigma_{\alpha\beta} = \frac{1}{\Omega}\frac{\partial E}{\partial \varepsilon_{\alpha\beta}}$$

其中 $\Omega$ 是晶胞体积。应变会改变倒格矢，因此在固定截断能下改变平面波基组，于是平面波计算中**应力**有 Pulay 项（Pulay 应力），力却没有（见 [[plane-waves]]）。符号约定（张应力为正还是负）不同程序不一致。

## 在本研究线里的样子 {mapping}

- **结构优化 `IBRION=1/2`**：每个离子步用 Hellmann–Feynman 力和应力更新坐标与晶胞（`ISIF=3`）。
- **有限差分 Born 电荷和力常数**：把原子挪一点，用力的变化算导数（见 [[dielectric-born]] 与 [[phonons]]）。力的精度直接决定这些量的精度。
- **MLIP 训练标签**：MACE 训练集里的力和应力就是 DFT 的 Hellmann–Feynman 力和应力（见 [[mlip-basics]]）。标签噪声来自 SCF 未充分收敛和 Pulay 应力。

## 常见坑 {mapping}

- **SCF 没收敛就用力**：定理的前提是精确本征态。能量对密度误差是二阶的，力却是一阶的，所以力比能量对 `EDIFF` 更敏感（见 [[scf-cycle]]）。
- **混淆力和应力的收敛**：截断能对力影响小，对应力影响大。
- **用能量差分验证力时步长太大**：差分步长要小到二阶项可以忽略，又要大于 SCF 噪声。

## 检验自己 {mapping}

::: question 解释
平面波基组为什么算力没有 Pulay 项，算应力却有？
:::

::: question 推导
对一维谐振子 $H = p^{2}/2m + \tfrac{1}{2}m\omega^{2}x^{2}$，取 $\lambda = \omega$，用 Hellmann–Feynman 定理验证基态满足 $\langle V\rangle = E_0/2$。
:::

::: question 迁移
你的 MACE 模型在应力上的误差远大于在力上的误差。从 DFT 标签的角度，你会先检查什么？
:::
