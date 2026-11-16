```json
{
  "id": "anharmonicity",
  "title": "非谐性",
  "type": "concept",
  "parent": "phonons",
  "research": [
    "piezo",
    "mlip",
    "csp"
  ],
  "keywords": [
    "anharmonicity",
    "quartic anharmonicity",
    "self-consistent phonon",
    "phonon softening",
    "thermal expansion",
    "finite-size correction",
    "phonon lifetime"
  ],
  "purpose": "谐振近似把晶格振动当成一组互不干扰的弹簧，但在高温、软模、强离子导体和分子晶体里它会给错频率、错自由能、错相变温度；这一条讲非谐性从哪里来、什么时候必须处理、以及几种处理办法各自的代价。",
  "prereq": {
    "intuitive": [
      "[[phonons]]：声子是什么、谐振近似做了什么",
      "[[quasi-harmonic]]：热膨胀怎样被处理"
    ],
    "full": [
      "[[perturbation-theory]]：把非谐项当微扰",
      "[[free-energy]]：振动自由能怎么算"
    ]
  },
  "status": "draft",
  "version": "0.1",
  "updated": "2026-11-16",
  "sources": [
    "tadano-2015-scph",
    "errea-2014-sscha",
    "hellman-2011-tdep",
    "makov-1995-finite-size"
  ],
  "origin": "定时任务 2026-11-16，由两篇 2026-11 的论文触发：Extreme anharmonicity determines the superionic transition in the prototypical antifluorite Li2O（Materials Cloud, doi:10.24435/materialscloud:5b-57）与 Low-temperature vibrational anomalies and thermal transport in polycyclic aromatic hydrocarbon crystals（arXiv:2611.16848）",
  "changelog": [
    {
      "version": "0.1",
      "date": "2026-11-16",
      "note": "初稿：非谐项从哪来、谐振近似在哪失效、自洽声子与 SSCHA、分子晶体与软模、有限尺寸修正、常见坑；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

谐振近似把每个原子受到的回复力写成 $-\Phi u$：位移多大，力就多大，线性。真实势能面不是抛物线：

- **不对称**：原子被压近时势能上升得比被拉开时快（排斥的短程性），所以同一个位移幅度，两个方向的能量代价不同；
- **有高阶项**：位移大时，三阶、四阶项不能再忽略。

后果是声子频率不再是常数：温度升高、振幅变大，平均频率会移动（通常软化）。图左边画了真实势与谐振势的差别，右边画了频率随温度的变化，以及由此带来的自由能修正。

![示意：左图是 Morse 型势与它的谐振近似，标出低温（小幅振动）与高温（大幅振动采样到不对称区域）两个窗口；右图是“频率不随温度变”（谐振）与“频率随温度软化”（非谐）两种情形，插图是振动自由能的差值。函数形式为玩具模型，坐标数值不对应具体材料。](figs/anharmonicity-well.svg)

| 符号 | 是什么 | 图里对应哪部分 |
| --- | --- | --- |
| $u$ | 原子相对平衡位置的位移 | 左图横轴 |
| $\frac{1}{2}\Phi u^2$ | 谐振近似下的势能 | 左图灰色虚线 |
| 真实势 | 含高阶项的实际势能 | 左图紫色实线 |
| $\omega(T)$ | 温度相关的有效声子频率 | 右图纵轴 |
| $\Delta F$ | 用非谐频率与用谐振频率算出的自由能之差 | 右图插图 |

核心机制一句话：**谐振近似只看二阶导数（曲率），非谐性看的是整个势的形状**。当振动幅度相对于势的非谐尺度不小的时候，二阶导数就不够用了。

## 定义与公式 {math}

### 非谐项从哪来

把总能量在平衡构型附近展开：

$$E = E_0 + \frac{1}{2!}\sum_{ij}\Phi_{ij}u_i u_j + \frac{1}{3!}\sum_{ijk}\Psi_{ijk}u_i u_j u_k + \frac{1}{4!}\sum_{ijkl}\Xi_{ijkl}u_i u_j u_k u_l + \cdots$$

其中 $u_i$ 是第 $i$ 个自由度的位移；$\Phi_{ij}$ 是二阶力常数（谐振项）；$\Psi_{ijk}$ 与 $\Xi_{ijkl}$ 是三阶、四阶力常数。谐振近似就是只保留 $\Phi_{ij}$，丢掉后面的所有项。

三阶项让势变得不对称，四阶项使势在两翼变陡或变缓。这两项合起来贡献了：

- 频率随温度移动（声子软化/硬化）；
- 声子之间的散射（有限寿命、热导率）；
- 热膨胀中超出准谐近似描述的部分。

### 自洽声子：把温度依赖吸收进频率

温度依赖有效声子 (temperature-dependent effective potential, TDEP) [@hellman-2011-tdep] 的做法：在有限温度 MD 轨迹上，**重新拟合**一组有效二阶力常数 $\Phi^{\mathrm{eff}}(T)$，使它在采样到的位移分布下最好地描述能量。频率由 $\Phi^{\mathrm{eff}}(T)$ 对角化得到。

自洽声子 (self-consistent phonon, SCP) [@tadano-2015-scph] 把这件事写成自洽方程：有效频率由四阶力常数与位移的均方值决定，而均方值又由频率决定，于是

$$\omega_q^2(T) = \omega_q^{(0)2} + \frac{1}{2}\sum_{q'} \Xi_{q,-q,q',-q'}\,\frac{\hbar}{2\omega_{q'}(T)}\coth\!\left(\frac{\hbar\omega_{q'}(T)}{2k_B T}\right)$$

其中 $\omega_q^{(0)}$ 是谐振频率；$\Xi$ 是四阶力常数（在声子表象里）；$\coth$ 项是量子谐振子的位移方差，温度越高、频率越低，这一项越大，修正越强。这是 SCP 的核心思想——把四阶项的效果变成对频率的自洽修正。

::: approximation 适用范围
SCP 抓住的是“振幅变大 → 平均曲率变小 → 频率软化”这一主要效应，对稳定声子的软化很有效。当某个模式在某个温度下软到零（结构失稳），SCP 方程会失效，此时需要随机自洽谐波近似 (stochastic self-consistent harmonic approximation, SSCHA) [@errea-2014-sscha]，它在路径积分框架下直接对位移分布求变分极小，可用于处理失稳模式与量子核效应。
:::

### 为什么不只是“加个修正”

在谐振近似里，振动自由能是

$$F_{\mathrm{vib}} = \sum_q \left[\frac{\hbar\omega_q}{2} + k_B T\ln\left(1 - e^{-\beta\hbar\omega_q}\right)\right]$$

其中第一项是零点能，第二项是热激发。频率变了这一整项都变——不只影响振动熵，也影响零点能。这就是为什么非谐性会改变相变温度、多晶型相对稳定性、以及热膨胀，而不只是“让声子谱好看一点”。

准谐近似 (quasi-harmonic approximation, QHA) 用“改变晶胞体积 → 改变频率”来处理热膨胀，本质上是把非谐性近似成对体积的依赖（见 [[quasi-harmonic]]）。当频率对**温度**本身的依赖（固定体积下）也很强时，QHA 不够，需要显式处理非谐性。

## 在本研究线里的样子 {mapping}

- **软模与相变**：铁电/反铁电材料的相变常由某个声子模式软化驱动。谐振声子谱只能给出“假设”，要判断相变温度与相变是否连续，需要把有限温度下的重正化频率算出来（见 [[phonons]]）。
- **离子导体**：超离子转变常伴随明显的声子软化与大的原子振幅，谐振近似会给出错误的转变温度。触发本条目的 Li2O 工作就是这一类。
- **分子晶体**：振动对多晶型能量差的贡献可以和方法本身的误差相当；分子晶体中的低频模式与分子间作用耦合，非谐性不可忽略 [@nyman-2015-vib]（该来源见 [[conformational-polymorphism]]）。含能材料与芳香分子晶体的热输运也更依赖非谐声子寿命。
- **有限尺寸修正**：用周期性超胞做 MD 或声子计算时，振动熵与长波声子的贡献需要外推到无限大体系；对带电缺陷或极性体系还有额外的静电修正，Makov–Payne 修正就是这一类 [@makov-1995-finite-size]。这是“数值上看起来非谐”的常见伪像来源。
- **MLIP 场景**：用机器学习势跑大超胞、长时间 MD 来直接采样非谐效应，是很自然的做法（见 [[mlip-basics]]、[[molecular-dynamics]]）；但 MLIP 在远离平衡的大振幅区域是否训练充分，决定了非谐效应是否可信——这与 [[mlip-finetuning]] 里“数据要覆盖什么”是同一个问题。

::: unverified 待核验
- 具体材料的软化幅度、转变温度、自由能修正数值因体系而异，本节不引用任何数值。
- SCP/SSCHA 的实现细节（四阶力常数的截断、q 点网格、自洽收敛标准）按所用程序（如 ALAMODE、SSCHA 代码）文档核对，正文不假设具体设置。
- 触发论文里报告的具体声子软化与相变温度尚未精读，不引用其数值。
:::

## 常见坑 {mapping}

- **把谐振声子谱当有限温度声子谱**：谐振频率是 0 K 结果，直接拿去算高温热容或自由能会系统性偏差。
- **以为 QHA 能处理所有非谐性**：QHA 只处理“频率随体积变”，固定体积下的温度重正化它管不了。
- **SCP 用在不稳定模式上**：软到零的模式会让 SCP 不收敛，要改用 SSCHA 或直接 MD。
- **有限尺寸伪像被当成物理**：超胞太小，长波声子缺失，振动熵与热容偏差大；做外推之前不要把差别解释成“非谐效应”。
- **三阶与四阶混用**：只加三阶项会得到不对称但仍是简谐的能量面，热膨胀与频率移动主要靠四阶项，缺一项会得出错误趋势。
- **MLIP 的非谐外推**：训练集没有覆盖大振幅构型时，非谐结果看起来“很合理”但其实是外推。

## 检验自己 {mapping}

::: question 解释
为什么谐振近似在低温下往往够用，而高温下容易失效？用位移的均方值相对于势的非谐尺度来说明。
:::

::: question 推导
设单模有效势 $E(u)=\frac{1}{2}\Phi u^2 + \frac{1}{4}\Xi u^4$。用谐振子基态的平均 $\langle u^2\rangle = \hbar/(2m\omega)$，把 $\Xi u^4$ 当作微扰，写出频率修正的一阶表达式，并说明它的符号。
:::

::: question 迁移
你要判断 β-甘氨酸某个多晶型在 300 K 下的相对稳定性。谐振 + QHA 给出的结果与含非谐修正的结果相差与你的目标精度同量级，设计一个用 MLIP 做长时间 MD、再用重加权或自由能方法交叉检验的方案。
:::
