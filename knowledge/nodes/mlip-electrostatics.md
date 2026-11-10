```json
{
  "id": "mlip-electrostatics",
  "title": "机器学习势中的长程静电与电场响应",
  "type": "concept",
  "parent": "mlip-basics",
  "research": [
    "mlip",
    "piezo"
  ],
  "keywords": [
    "Born effective charge",
    "electric field",
    "long-range electrostatics",
    "charge equilibration",
    "Ewald"
  ],
  "purpose": "局域的机器学习势只给能量、力和应力，没有电荷与极化；要算介电、压电这类对电场的响应，需要额外学习玻恩有效电荷或显式的静电项。",
  "prereq": {
    "intuitive": [
      "[[mlip-basics]]：截断半径与局域性",
      "库仑相互作用"
    ],
    "full": [
      "[[dielectric-born]]",
      "[[piezoelectric-tensor]]",
      "[[berry-phase-polarization]]",
      "[[equivariance]]"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "behler-2021-generations",
    "ko-2021-4g",
    "wu-2005-strain",
    "unke-2021-mlff",
    "doyu-2026-dipole",
    "husistein-2026-qmmm"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：局域模型缺什么、压电离子项需要哪些量、几类做法（点电荷加 Ewald、电荷平衡、直接学 Born 电荷或极化）、求和规则、在 β-甘氨酸上的组合方案、常见坑；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

[[mlip-basics]] 中的局域模型有两个与电场相关的缺口。

1. **长程静电**：库仑相互作用按 $1/r$ 衰减，很慢。截断半径之外的部分被丢掉，或者只能被“平均地”吸收进局域项。对中性的分子晶体，总能里这部分的影响可能不大，但对离子体系、界面和带电缺陷影响明显。
2. **没有电场这个输入，也没有极化这个输出**：模型只把原子坐标映射到能量。介电常数、玻恩有效电荷、压电张量都是对电场的响应（见 [[dielectric-born]] 与 [[piezoelectric-tensor]]），局域 MLIP 的标准输出给不出来。

对压电来说，第二个缺口更要紧：离子弛豫贡献需要 Born 有效电荷 $Z^{*}$，它描述电场在原子上产生多大的力，或者原子位移产生多大的极化。

![左（示意）：库仑相互作用与截断后的局域模型，红色区域是丢掉的长程部分。右：电场在原子上产生的力由 Born 有效电荷张量决定，方向不一定和电场平行。](figs/mlip-electrostatics.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $r$ | 两个电荷的距离 | 左图横轴 |
| $r_c$ | 局域模型的截断半径 | 左图蓝色点线 |
| $\boldsymbol{\mathcal{E}}$ | 外加宏观电场 | 右图灰色箭头 |
| $\kappa$ | 原子标号 | 右图蓝色原子 |
| $Z^{*}_{\kappa}$ | 原子 $\kappa$ 的 Born 有效电荷张量（3×3） | 右图力与电场的关系 |
| $F_{\kappa\beta}$ | 电场在原子上产生的力的 $\beta$ 分量 | 右图橙色箭头 |

## 定义与公式 {math}

### 压电离子项需要什么

压电张量的离子弛豫贡献（记号与 [[piezoelectric-tensor]] 相同）：

$$e_{\alpha j} = \bar e_{\alpha j} + \frac{1}{\Omega}\sum_{m} Z^{*}_{m\alpha}\,\frac{\partial u_m}{\partial \eta_j}$$

其中 $\bar e$ 是钳位离子项（纯电子响应）；$\Omega$ 是晶胞体积；$m$ 遍历所有原子位移自由度；$Z^{*}_{m\alpha}$ 是 Born 有效电荷；$\partial u_m / \partial \eta_j$ 是应变引起的内部原子弛豫 [@wu-2005-strain]。

拆开来看：

- $\partial u_m / \partial \eta_j$ 只需要能量对坐标和应变的二阶导数（力常数和内应变张量），**普通的 MLIP 可以给**。
- $Z^{*}$ 和 $\bar e$ 是电场响应，**普通的 MLIP 给不了**。

::: definition Born 有效电荷（回顾）
$$Z^{*}_{\kappa,\alpha\beta} = \frac{\Omega}{e}\,\frac{\partial P_\alpha}{\partial u_{\kappa\beta}} = \frac{1}{e}\,\frac{\partial F_{\kappa\beta}}{\partial \mathcal{E}_\alpha}, \qquad \sum_{\kappa} Z^{*}_{\kappa,\alpha\beta} = 0$$

其中 $P_\alpha$ 是宏观极化，$u_{\kappa\beta}$ 是原子 $\kappa$ 沿 $\beta$ 方向的位移，$F_{\kappa\beta}$ 是它受的力，$\mathcal{E}_\alpha$ 是电场，$e$ 是元电荷。第二式是声学求和规则：整体平移不产生极化（见 [[dielectric-born]]）。
:::

### 几类做法

| 做法 | 模型学什么 | 能给什么 | 局限 |
| --- | --- | --- | --- |
| 局域 MLIP | 原子能 | 能量、力、应力 | 没有电场响应 |
| 局域 MLIP + 固定或学习的点电荷 + Ewald 求和 | 每个原子的标量电荷 | 长程静电能 | 标量电荷给出的 $Z^{*}$ 是各向同性的，通常不够 |
| 电荷平衡（第四代神经网络势） | 原子电负性，再全局求解电荷分布 | 长程静电与非局域电荷转移 | 计算量更大 [@ko-2021-4g] |
| 直接学 $Z^{*}$ 或极化 | 等变的二阶张量或向量输出 | Born 电荷、红外强度、电场下的力 | 需要 DFT 的 $Z^{*}$ 或极化标签 |

神经网络势的发展从局域的第二代，到加入长程静电的第三代，再到含非局域电荷转移的第四代，Behler 的综述有系统梳理 [@behler-2021-generations]。

直接学 $Z^{*}$ 时，输出要是等变的二阶张量（一般不对称，可以分解为 $l=0,1,2$ 三部分，见 [[equivariance]]），并且要满足求和规则（例如预测后把每个分量的平均值减掉）。

::: unverified 待核验
- 学极化 $P$ 再求导得 $Z^{*}$：周期体系的极化只定义到一个“极化量子”，标签需要选在同一分支上（见 [[berry-phase-polarization]]）；具体做法以相关论文为准。
- 雷达里触发本条目的两篇预印本：一篇在 MLIP 的电场驱动模拟中讨论集体偶极效应 [@doyu-2026-dipole]，一篇把外电场直接写进 MLIP 的表示 [@husistein-2026-qmmm]。这里只按标题概括，尚未精读。
:::

## 在本研究线里的样子 {mapping}

β-甘氨酸压电的一种组合方案：

1. 钳位离子项 $\bar e$ 和 $Z^{*}$ 用 DFT（DFPT 或有限差分）算一次；
2. 力常数和内应变用 MLIP 算，或者也用 DFT；
3. 按上面的公式合成 $e_{\alpha j}$，再用弹性张量换算成 $d_{ij}$（见 [[piezoelectric-tensor]] 与 [[elastic-tensor]]）。

这样 MLIP 只负责它擅长的部分，是否值得取决于 DFT 计算力常数的代价。其他要点：

- **有限温度**：若要在 MD 采样的多个构型上平均压电系数，每个构型都需要 $Z^{*}$，这时学习 $Z^{*}$ 的模型才真正有用（见 [[molecular-dynamics]]）。
- **分子晶体的长程静电**：中性分子的偶极–偶极相互作用随 $1/r^{3}$ 衰减，比单电荷快，但仍可能超出截断。是否影响多晶型排序，要用 DFT 对照检查。

## 常见坑 {mapping}

- **用 MLIP 的力常数配 DFT 的 $Z^{*}$，两者对应的结构不同**：所有量都要在同一个平衡结构上算。
- **忘记求和规则**：$Z^{*}$ 的小误差违反求和规则时，会在压电和介电结果里产生虚假的贡献。
- **把标量部分电荷当成 Born 电荷**：Born 电荷是动态响应量，与 Bader、Mulliken 这类静态电荷分配不同，通常也不一样大。
- **以为局域模型“学到了”静电就能算电场响应**：能量里吸收了平均的静电效应，不代表模型知道电场下会怎样。

## 检验自己 {mapping}

::: question 解释
在压电离子项公式里，哪些量普通 MLIP 能给，哪些不能？为什么？
:::

::: question 推导
如果每个原子的 Born 电荷都是标量乘单位矩阵 $Z^{*}_\kappa = q_\kappa I$，写出由此得到的离子项，并说明它丢掉了什么。
:::

::: question 迁移
你想用 MD 采样 300 K 下的 β-甘氨酸 $d_{16}$。设计一个最少 DFT 计算量的方案，说明哪些步骤用 MLIP、哪些必须用 DFT。
:::
