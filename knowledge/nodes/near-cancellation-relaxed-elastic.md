```json
{
  "id": "near-cancellation-relaxed-elastic",
  "title": "弛豫离子弹性常数中的近相消",
  "type": "concept",
  "parent": "elastic-tensor",
  "research": ["piezo"],
  "keywords": [
    "subtractive cancellation",
    "clamped-ion elastic constants",
    "ionic relaxation contribution",
    "internal strain",
    "condition number"
  ],
  "purpose": "说明弛豫离子弹性常数怎样由两项大数相减得到，以及为什么分子晶体里这种近相消会把不大的绝对数值误差变成软本征方向上很大的相对误差。",
  "prereq": {
    "intuitive": [
      "[[elastic-tensor]] 里夹持离子与弛豫离子",
      "[[energy-structure-response]] 里“软方向放大误差”"
    ],
    "full": [
      "矩阵求逆与本征值条件数的基本概念",
      "[[piezoelectric-tensor]] 中 $d = e\\,s$ 的换算"
    ]
  },
  "status": "draft",
  "version": "0.1",
  "updated": "2026-11-27",
  "origin": "工作提炼（2026-11-27）",
  "sources": [
    "wu-2005-strain",
    "ieee-176-piezo"
  ],
  "changelog": [
    {
      "version": "0.1",
      "date": "2026-11-27",
      "note": "初稿：近相消的代数结构、相对误差估计、与压电换算的联系；配图 1 张"
    }
  ]
}
```

## 直觉 {intuition}

弛豫离子弹性常数不是“另算一套曲率”，而是把夹持离子曲率里**会被原子弛豫抹掉的那一块减掉**。分子晶体里，夹持离子项往往很大（分子内共价键很硬），离子弛豫项也几乎同样大（应变后分子可以整体平移、转动把力卸掉）。两者相减，剩下的才是分子间作用决定的有效刚度，常常只有几个 GPa 甚至更小。

这是典型的**近相消** (near cancellation / subtractive cancellation)：结果远小于参与运算的两项。两项里只要各自带一点绝对误差，相对误差就会被放大到结果上。[[energy-structure-response]] 说的“软方向放大误差”解释的是：曲率已经很小之后，再出错会怎样；本条目解释的是：为什么软曲率会以“两项大数相减”的方式出现。

![示意：夹持离子项与离子弛豫项都很大、彼此接近，相减后的弛豫离子弹性常数很小。](figs/near-cancellation-elastic.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $\bar C$ | 夹持离子弹性常数 | 左侧蓝色高柱 |
| $\Lambda K^{-1}\Lambda/\Omega$ | 离子弛豫贡献（示意） | 中间橙色高柱 |
| $C$ | 弛豫离子弹性常数 | 右侧绿色矮柱 |
| “−” | 从夹持项减去弛豫贡献 | 两柱之间的箭头 |

图是示意，柱高不对应任何具体材料的数值。

## 定义与关键公式 {math}

在均匀应变 $\eta$ 下，先让原子保持分数坐标（夹持），再允许内坐标 $u$ 弛豫到新的力为零。对弛豫后的能量求二阶导数，得到 [@wu-2005-strain]

$$
C_{ij} = \bar C_{ij} - \frac{1}{\Omega}\sum_{m,n}\Lambda_{mi}\,(K^{-1})_{mn}\,\Lambda_{nj}.
$$

其中 $\bar C$ 是夹持离子弹性张量；$\Omega$ 是晶胞体积；$\Lambda_{mi}=-\partial^{2}E/\partial u_m\partial\eta_i$ 是内应变耦合（应变在原子上产生的力）；$K$ 是去掉整体平移后的力常数矩阵。第二项半正定，所以弛豫只会让晶体变软或不变（见 [[elastic-tensor]]）。

取某一个单位应变方向 $v$，记标量

$$
\lambda = v^{\mathsf T} C v,\qquad
\lambda_{\mathrm{cl}} = v^{\mathsf T}\bar C v,\qquad
\lambda_{\mathrm{ion}} = v^{\mathsf T}\!\left(\frac{1}{\Omega}\Lambda^{\mathsf T}K^{-1}\Lambda\right)\!v.
$$

则 $\lambda = \lambda_{\mathrm{cl}}-\lambda_{\mathrm{ion}}$。当 $\lambda_{\mathrm{cl}}\approx\lambda_{\mathrm{ion}}\gg\lambda$ 时，相对误差的一阶估计是

$$
\frac{\delta\lambda}{\lambda}
\approx
\frac{\delta\lambda_{\mathrm{cl}}-\delta\lambda_{\mathrm{ion}}}{\lambda}.
$$

其中 $\delta\lambda_{\mathrm{cl}}$、$\delta\lambda_{\mathrm{ion}}$ 是两项各自的绝对误差。若它们的量级不随 $\lambda$ 变小而变小（例如有限差分步长噪声、自洽残余、色散是否进入力常数等带来的绝对底噪），则相对误差大致按 $1/\lambda$ 放大。

::: definition 近相消放大因子（示意定义）
在固定方向 $v$ 上，把放大因子写成 $A=\lambda_{\mathrm{cl}}/\lambda$（当 $\lambda>0$）。$A$ 大，说明结果只占夹持项的很小一部分；同样大小的绝对误差，相对影响约为无相消时的 $A$ 倍。
:::

::: unverified 待核验
- 具体程序里 $\bar C$ 与离子项是否在同一次计算、同一能量面上得到，按所用实现核对；若夹持项与离子项来自不同哈密顿量或不同数值设定，上式仍可形式写出，但不再是同一势能面的精确分解。
- “绝对底噪大致不随材料软硬改变”是对数值误差结构的经验说法，不是定理；需要在具体方法（有限差分步长、自洽阈值、对称性处理）下核验。
:::

## 在本研究线里的样子 {mapping}

- **换算 $d$**：实验常报告的压电应变系数满足 $d=e\,s^{E}$，$s^{E}=C^{-1}$ [@ieee-176-piezo]。$\lambda$ 越小，$s$ 在该方向越大，$d$ 对 $C$ 的误差越敏感。近相消同时推高了“需要很大 $d$ 的软晶体”和“算不准 $C$ 的风险”。
- **交叉检查**：同一能量面上，用不同数值路线（例如应变有限差分与位移有限差分，或有限差分与微扰）比较 $\lambda_{\mathrm{cl}}$、$\lambda_{\mathrm{ion}}$ 和 $\lambda$。若两项各自接近、只有差 $\lambda$ 分歧大，优先怀疑近相消放大，而不是“压电 $e$ 算错了”（见 [[finite-difference-vs-dfpt]]）。
- **报告方式**：对很软的方向，除了报 $C$ 或 $d$，同时报 $\lambda$ 或该方向的杨氏模量量级，并说明 $\lambda_{\mathrm{cl}}$ 与 $\lambda_{\mathrm{ion}}$ 是否接近。

## 常见坑 {mapping}

- **把符号不稳的 $\lambda$ 当成材料性质**：当 $|\lambda|$ 已落到绝对数值底噪量级时，正负号可以由噪声决定，不能直接当力学失稳或高 $d$ 的证据。
- **只收紧总能相关参数**：提高截断能或收紧能量判据，主要压的是绝对误差；若 $A$ 已经很大，相对误差仍可能大。要对目标量本身（软本征值、$d$）做收敛，见 [[convergence-testing]]。
- **夹持项与离子项能量面不一致**：一边含色散校正、一边不含，或截断能、k 点不同，会在相减里留下系统偏差；偏差同样按 $1/\lambda$ 放大。

## 检验自己 {mapping}

::: question 解释
为什么“夹持离子弹性常数算得很准”仍可能得不到可靠的弛豫离子 $C$？
:::

::: question 推导
设 $\lambda_{\mathrm{cl}}=100$、$\lambda_{\mathrm{ion}}=97$，两项的绝对误差都是 $\pm 0.5$（彼此无关）。估计 $\lambda$ 的相对误差量级。
:::

::: question 迁移
若某方向上 $\lambda$ 已经接近你估计的数值底噪，你会优先改计算参数，还是改报告口径（例如只报告 $e$ 与 $\lambda$ 的区间）？理由是什么？
:::
