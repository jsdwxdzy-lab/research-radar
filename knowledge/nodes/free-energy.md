```json
{
  "id": "free-energy",
  "title": "自由能与熵",
  "type": "concept",
  "parent": "statmech",
  "research": [
    "csp"
  ],
  "keywords": [
    "free energy",
    "entropy",
    "Gibbs free energy"
  ],
  "purpose": "有限温度下为什么比较自由能而不是能量，振动熵和构型熵怎样进来。",
  "prereq": {
    "intuitive": [
      "[[ensembles]]：正则系综与配分函数",
      "熵的统计解释"
    ],
    "full": [
      "[[phonons]]",
      "[[molecular-dynamics]]"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "frenkel-2002-sim",
    "nyman-2015-vib",
    "hoja-2019-polymorphs",
    "kirkwood-1935",
    "zwanzig-1954"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：亥姆霍兹与吉布斯自由能、谐振振动自由能与零点能、软模式带来的熵、构型熵、热力学积分与自由能微扰、多晶型排序中的作用、常见坑；配图 1 张（真实计算 Einstein 模型）"
    }
  ]
}
```
## 直觉 {intuition}

0 K 时体系待在能量最低的结构里。温度升高后，体系会在许多微观状态之间涨落，**能占据的状态越多越有利**，这就是熵的作用。所以有限温度下判断哪个结构稳定，要比较自由能

$$F = E - TS$$

而不是能量 $E$。

对晶体来说，最重要的熵来自原子振动。振动越“软”（频率越低），同样温度下能激发的振动状态越多，熵越大。于是能量稍高但更软的多晶型，可能在高温下反超能量更低但更硬的多晶型。

![用 Einstein 模型真实计算的两个多晶型（约化单位，ħ=k_B=1）：A 的 0 K 能量更低但振动更硬，B 能量高一些但有一个更软的模式。左：两者的自由能。右：自由能差，在转变温度 T_t 处变号。](figs/free-energy-crossing.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $T$ | 温度 | 横轴 |
| $F_{\mathrm{A}}, F_{\mathrm{B}}$ | 两个多晶型的自由能 | 左图蓝线、橙线 |
| $\Delta F$ | $F_{\mathrm{B}} - F_{\mathrm{A}}$ | 右图黑线 |
| $\Delta E + \Delta E_{\mathrm{ZP}}$ | 0 K 时的差：静态能量差加零点能差 | 右图 $T=0$ 处的值 |
| $T_{\mathrm{t}}$ | 转变温度，$\Delta F = 0$ | 右图红色点线 |

模型参数：A 的三个频率为 1.0、1.4、2.0，B 为 0.55、1.2、2.0；B 的静态能量比 A 高 0.5。

## 定义与公式 {math}

::: definition 自由能
$$F = -k_B T \ln Z = E - TS, \qquad G = F + pV$$

其中 $Z$ 是正则配分函数；$k_B$ 是玻尔兹曼常数；$E$ 是内能（系综平均）；$S$ 是熵；$G$ 是吉布斯自由能，$p$ 是压力，$V$ 是体积。恒温恒压下比较 $G$，恒温恒容下比较 $F$。对固体在常压下，$pV$ 项通常很小 [@frenkel-2002-sim]。
:::

::: definition 谐振振动自由能
$$F_{\mathrm{vib}}(T) = \sum_{\mathbf{q}j}\left[\frac{\hbar\omega_{\mathbf{q}j}}{2} + k_B T\ln\!\left(1 - \mathrm{e}^{-\hbar\omega_{\mathbf{q}j}/k_B T}\right)\right]$$

其中求和遍历布里渊区中的波矢 $\mathbf{q}$ 和声子支 $j$（见 [[phonons]]）；$\omega_{\mathbf{q}j}$ 是声子频率；$\hbar$ 是约化普朗克常数。第一项是零点能 (zero-point energy)，第二项在 $T \to 0$ 时为零。总的自由能是 $F = E_{\mathrm{static}} + F_{\mathrm{vib}}$。
:::

高温极限下，每个模式的自由能约为 $k_B T\ln(\hbar\omega/k_B T)$，所以低频模式让自由能下降更多。这就是图中软的多晶型 B 在高温下胜出的原因。

### 构型熵

如果晶体中存在无序（分子取向无序、质子位置无序、部分占据），不同排列方式也贡献熵。$W$ 种等能排列给出 $S_{\mathrm{conf}} = k_B\ln W$。CSP 通常只考虑有序结构，会漏掉这一项（见 [[proton-position]]）。

### 超出谐振近似

强非谐体系（分子转动、大振幅运动、接近熔点）用谐振公式不可靠，需要用分子动力学或蒙特卡洛做自由能计算 [@frenkel-2002-sim]：

::: definition 热力学积分与自由能微扰
$$\Delta F = \int_{0}^{1}\left\langle \frac{\partial U(\lambda)}{\partial\lambda}\right\rangle_{\lambda}\mathrm{d}\lambda, \qquad \Delta F = -k_B T\ln\left\langle \mathrm{e}^{-(U_1 - U_0)/k_B T}\right\rangle_{0}$$

其中 $U(\lambda)$ 是在参考势 $U_0$（$\lambda=0$）和目标势 $U_1$（$\lambda=1$）之间连续变化的势能；$\langle\cdot\rangle_\lambda$ 是在 $U(\lambda)$ 下的系综平均。前者是热力学积分 [@kirkwood-1935]，后者是自由能微扰 [@zwanzig-1954]。常见做法是以谐振晶体作为参考态，再积分到真实势。
:::

## 在本研究线里的样子 {mapping}

- **CSP 的最后一步**：在 DFT 能量排序的基础上加入振动自由能，可能改变低能候选的顺序（见 [[csp-search-ranking]]）[@hoja-2019-polymorphs]。
- **代价**：每个候选结构都要算声子，比单点能贵得多；常用 MLIP 算声子来降低代价，但要先验证 MLIP 的频率（见 [[mace]]）。
- **β-甘氨酸**：讨论它在室温下的稳定性时，要比较的是自由能；0 K 能量排序只是近似。

::: unverified 待核验
- Nyman 与 Day 统计了大量多晶型对的静态能量差和振动自由能差，结论是振动贡献足以改变一部分多晶型对的排序 [@nyman-2015-vib]。具体比例与量级按原文核对后补上。
:::

## 常见坑 {mapping}

- **只用 Γ 点频率**：$F_{\mathrm{vib}}$ 需要对整个布里渊区求和，低频声学支贡献大；只用 Γ 点会系统地偏差。
- **虚频直接丢掉**：虚频说明结构不在极小，自由能没有意义；要先解决结构问题（见 [[phonons]]）。
- **不同多晶型用不同 q 网格**：误差不抵消，可能大于自由能差本身。
- **固定体积**：谐振自由能在 0 K 的体积上算，忽略了热膨胀，这正是 [[quasi-harmonic]] 要补的。

## 检验自己 {mapping}

::: question 解释
为什么振动更软的多晶型在高温下更有利？用谐振自由能的高温极限说明。
:::

::: question 推导
对单个频率为 $\omega$ 的谐振子，从配分函数 $Z = \sum_n \mathrm{e}^{-\hbar\omega(n+1/2)/k_B T}$ 出发推出上面的 $F_{\mathrm{vib}}$ 表达式。
:::

::: question 迁移
两个候选结构的 PBE-D3 能量差是 1 kJ/mol，振动自由能差在 300 K 是 −1.5 kJ/mol。在下结论之前，你还要检查哪些误差来源？
:::
