```json
{
  "id": "perturbation-theory",
  "title": "微扰理论与线性响应",
  "type": "concept",
  "parent": "quantum",
  "keywords": [
    "perturbation theory",
    "linear response",
    "Sternheimer equation"
  ],
  "purpose": "一阶、二阶微扰能量和波函数修正怎样来，怎样推广到 DFT 的线性响应（DFPT）和 Sternheimer 方程。",
  "prereq": {
    "intuitive": [
      "[[eigenproblems]]：本征值与本征矢",
      "两能级体系"
    ],
    "full": [
      "[[kohn-sham-dft]]",
      "[[hellmann-feynman]]"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "baroni-2001-dfpt",
    "gonze-1997-dfpt",
    "martin-2020-electronic"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：Rayleigh–Schrödinger 微扰、两能级例子、二阶能量与响应、2n+1 定理、Sternheimer 方程与 DFPT、常见坑；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

哈密顿量受到一个小扰动 $\lambda V$（电场、原子位移、应变），能级和波函数会怎样变？如果扰动小，就可以按 $\lambda$ 的幂次展开，逐阶求解。

几个关键结论：

- **一阶能量**是扰动在原态上的期望值，这其实就是 [[hellmann-feynman]]。
- **二阶能量**来自扰动把原态和其他态混合起来，分母是能级差。能级差越小，混合越强，响应越大。
- **响应量**（极化率、介电常数、力常数、压电系数）都是能量对扰动的二阶导数，所以都需要一阶波函数。

固体中对所有空态求和太贵。Sternheimer 方程把“对空态求和”换成解一个线性方程，这是密度泛函微扰理论 (DFPT) 的核心 [@baroni-2001-dfpt]。

![两能级体系（Δ=1，耦合强度 V=0.9 的示意参数）：实线是精确能级，虚线是二阶微扰近似。λ 小时两者重合，λ 大时偏离；扰动把两个能级推开。](figs/two-level-perturbation.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $\lambda$ | 扰动强度 | 横轴 |
| $\Delta$ | 未扰动的能级差 | 左侧双向箭头 |
| $V$ | 两态之间的耦合矩阵元 | 决定曲线弯曲程度的参数 |
| $E_\pm$ | 精确本征值 | 实线 |
| 二阶近似 | $\pm\bigl(\Delta/2 + (V\lambda)^{2}/\Delta\bigr)$ | 虚线 |

## 定义与公式 {math}

::: definition Rayleigh–Schrödinger 微扰
设 $H = H^{(0)} + \lambda V$，$H^{(0)}|n\rangle = E_n|n\rangle$，能级不简并。则

$$E_n(\lambda) = E_n + \lambda\,V_{nn} + \lambda^{2}\sum_{m\neq n}\frac{|V_{mn}|^{2}}{E_n - E_m} + O(\lambda^{3})$$

$$|n^{(1)}\rangle = \sum_{m\neq n}|m\rangle\,\frac{V_{mn}}{E_n - E_m}$$

其中 $V_{mn} = \langle m|V|n\rangle$；$|n^{(1)}\rangle$ 是一阶波函数修正（乘以 $\lambda$ 后加到 $|n\rangle$ 上）[@martin-2020-electronic]。
:::

对基态，所有 $E_n - E_m < 0$，所以二阶能量总是负的：扰动总能降低基态能量。

### 2n+1 定理

知道 $n$ 阶波函数，就能算到 $2n+1$ 阶能量。特别地，一阶波函数足以给出二阶和三阶能量。这一结论在 DFT 中同样成立，因为 DFT 能量也是变分的 [@gonze-1997-dfpt]。

::: definition Sternheimer 方程
$$\bigl(H^{(0)} - \varepsilon_n\bigr)\,P_c\,|\psi_n^{(1)}\rangle = -P_c\,\Delta V\,|\psi_n\rangle$$

其中 $\psi_n$ 是占据的 KS 轨道，$\varepsilon_n$ 是其本征值；$P_c$ 是投影到空态子空间的算符（$P_c = 1 - \sum_{v}|\psi_v\rangle\langle\psi_v|$，$v$ 遍历占据态）；$\Delta V$ 是一阶有效势变化。它是一个线性方程组，不需要显式求出空态 [@baroni-2001-dfpt]。
:::

在 DFPT 中，$\Delta V$ 本身依赖一阶密度变化（Hartree 和交换关联势随密度变化），所以 Sternheimer 方程也要自洽求解，类似 [[scf-cycle]]。

::: assumption 不简并与绝缘
上述公式要求能级不简并；简并时先在简并子空间内对角化扰动。DFPT 的标准形式针对有能隙的绝缘体，金属需要额外处理费米面附近的占据变化 [@baroni-2001-dfpt]。
:::

## 在本研究线里的样子 {mapping}

| 扰动 | 二阶导数 | 对应的量 |
| --- | --- | --- |
| 电场 × 电场 | $\partial^{2}E/\partial\mathcal{E}^{2}$ | 电子介电张量 $\varepsilon^{\infty}$ |
| 原子位移 × 电场 | $\partial^{2}E/\partial u\,\partial\mathcal{E}$ | Born 有效电荷 $Z^{*}$ |
| 原子位移 × 原子位移 | $\partial^{2}E/\partial u^{2}$ | 力常数、声子 |
| 应变 × 电场 | $\partial^{2}E/\partial\eta\,\partial\mathcal{E}$ | 钳位离子压电张量 |

- **VASP `LEPSILON = .TRUE.`**：用 DFPT 算 $\varepsilon^{\infty}$、$Z^{*}$ 和钳位离子压电张量（见 [[dielectric-born]] 与 [[piezoelectric-tensor]]）。
- **离子弛豫部分**：压电张量的离子贡献需要力常数和内应变，通常用 `IBRION = 7/8`（DFPT）或 `IBRION = 5/6`（有限差分）（见 [[finite-difference-vs-dfpt]]）。
- **能隙与响应**：二阶能量的分母是能级差，所以 PBE 低估能隙会让电子介电常数偏大（见 [[pbe]]）。

::: unverified 待核验
- 应变扰动在 DFPT 中的处理（Hamann 等的应变 DFPT）及其在 VASP 中是否用 DFPT 还是有限差分，按 VASP 文档与原文核对。
:::

## 常见坑 {mapping}

- **把“微扰”理解为“近似”**：DFPT 算的是精确的解析二阶导数，和足够小步长的有限差分在收敛极限下应一致。
- **忽略局域场与自洽**：独立粒子近似（不自洽 $\Delta V$）会明显高估介电常数。
- **简并能级直接套公式**：分母为零，必须先处理简并子空间。

## 检验自己 {mapping}

::: question 解释
为什么基态的二阶能量修正总是负的？这和“扰动把能级推开”有什么关系？
:::

::: question 推导
对两能级体系 $H = \begin{pmatrix}-\Delta/2 & \lambda V\\ \lambda V & \Delta/2\end{pmatrix}$，求精确本征值，展开到 $\lambda^{2}$，与二阶微扰公式比较。
:::

::: question 迁移
DFPT 和有限差分算出的 β-甘氨酸 Born 电荷差了 5%。你会依次检查哪些设置？
:::
