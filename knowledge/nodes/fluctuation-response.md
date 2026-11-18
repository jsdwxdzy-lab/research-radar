```json
{
  "id": "fluctuation-response",
  "title": "涨落公式：从平衡涨落求响应张量",
  "type": "method",
  "parent": "ensembles",
  "research": ["piezo", "mlip"],
  "keywords": ["fluctuation-dissipation theorem", "fluctuation formula", "strain fluctuations", "dipole fluctuations", "finite-temperature piezoelectric", "Parrinello-Rahman"],
  "purpose": "说明为什么平衡态里应变和极化的涨落协方差就是压电、弹性、介电响应，公式里的体积和单位约定是什么，什么条件下这条路比 0 K 的二阶导数更有用，统计误差怎样估计。",
  "prereq": {
    "intuitive": ["[[ensembles]] 里的配分函数", "[[piezoelectric-tensor]] 里 $d$ 的定义"],
    "full": ["[[molecular-dynamics]]", "[[energy-structure-response]]", "[[berry-phase-polarization]]"]
  },
  "status": "draft",
  "version": "0.1",
  "updated": "2026-11-18",
  "sources": ["kubo-1966-fdt", "parrinello-1982-strain-fluct", "neumann-1983-dipole-fluct", "garcia-1998-batio3", "frenkel-2002-sim", "parrinello-1981-npt"],
  "origin": "用户请求（2026-11-18）：CSPpipeline 的 d33_theory 方案计划用 MD 轨迹的极化—应变涨落求 d(T)",
  "changelog": [{"version": "0.1", "date": "2026-11-18", "note": "初稿：线性响应推导、三个涨落公式、与 0 K 二阶导数的关系、系综与统计误差；配图 1 张"}]
}
```
## 直觉 {intuition}

0 K 的做法是“推一下，看它怎么动”：施加应变或电场，求能量的二阶导数（见 [[energy-structure-response]]）。有限温度下还有另一条路：什么都不推，让体系在热平衡里自己涨落，然后看两个量**一起**涨落的程度。

理由是线性响应理论的一个普遍结论：外场与某个量 $A$ 耦合时，另一个量 $B$ 的平均值对外场的响应，等于平衡态下 $A$ 与 $B$ 的协方差除以 $k_{\mathrm B}T$。这就是涨落—耗散定理 (fluctuation-dissipation theorem) 的静态形式 [@kubo-1966-fdt]。弹性对应应变自身的涨落 [@parrinello-1982-strain-fluct]，介电对应偶极自身的涨落 [@neumann-1983-dipole-fluct]，压电对应应变与极化的交叉涨落。

这条路的好处是温度、非谐性和构型无序都自动包含在轨迹里。代价是协方差是个统计量，要很长的轨迹才能压住误差，而压电又恰好是一个小的交叉项。

![涨落公式的统计图像（玩具数据，二维正态分布）。(a) 每个点是一帧的应变与极化涨落，椭圆是 1σ 与 2σ 等概率线，红线斜率是协方差除以方差。(b) 协方差的标准误随独立样本数下降。](figs/fluctuation-covariance.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $\delta\eta$ | 一帧的应变减去平均应变 | (a) 横轴 |
| $\delta P$ | 一帧的极化减去平均极化 | (a) 纵轴 |
| 协方差椭圆 | $(\delta\eta,\delta P)$ 联合分布的等概率线；倾斜程度反映协方差 | (a) 蓝色椭圆 |
| $N_{\mathrm{eff}}$ | 轨迹里统计上独立的样本数，约为总时长除以两倍自相关时间 | (b) 横轴 |

## 推导 {math}

在恒应力、恒温系综里，给哈密顿量加上电场耦合：

$$H'(\Gamma) = H(\Gamma) - V\,\mathcal E_\alpha P_\alpha(\Gamma)$$

其中 $\Gamma$ 是相空间点（原子坐标、动量与晶胞）；$V$ 是模拟盒子（超胞）体积；$P_\alpha$ 是**整个模拟盒子**的偶极除以 $V$；$\mathcal E_\alpha$ 是外加电场；重复下标求和。某个量 $A$ 的平均值是 $\langle A\rangle = \int A\,e^{-H'/k_{\mathrm B}T}d\Gamma \big/ \int e^{-H'/k_{\mathrm B}T}d\Gamma$。对 $\mathcal E_\alpha$ 求导并取 $\mathcal E\to 0$：

$$\frac{\partial\langle A\rangle}{\partial \mathcal E_\alpha}\bigg|_{\mathcal E=0} = \frac{V}{k_{\mathrm B}T}\,\bigl\langle \delta A\,\delta P_\alpha\bigr\rangle$$

其中 $\delta A = A - \langle A\rangle$。把 $A$ 换成应变、极化，或把耦合换成应力与应变，得到三个涨落公式：

$$d_{\alpha j} = \frac{V}{k_{\mathrm B}T}\,\langle \delta\eta_j\,\delta P_\alpha\rangle, \qquad s_{jk} = \frac{V}{k_{\mathrm B}T}\,\langle \delta\eta_j\,\delta\eta_k\rangle, \qquad \chi_{\alpha\beta} = \frac{V}{\epsilon_0 k_{\mathrm B}T}\,\langle \delta P_\alpha\,\delta P_\beta\rangle$$

其中 $d_{\alpha j}$ 是压电应变系数（恒应力），$\eta_j$ 是 Voigt 应变（剪切取工程应变，与 [[piezoelectric-tensor]] 相同）；$s_{jk}$ 是柔顺张量（弹性张量 $C$ 的逆）；$\chi_{\alpha\beta}$ 是介电极化率；$\epsilon_0$ 是真空介电常数。$\eta$ 从模拟盒子的晶胞矩阵相对参考晶胞算出。

::: definition 体积约定
公式里的 $V$ 和 $P$ 必须对应同一个盒子：$P$ 是**超胞**总偶极除以**超胞**体积。$\langle\delta P^{2}\rangle$ 随 $1/V$ 下降，乘上 $V$ 后结果与超胞大小无关。若误把单胞的 $P$ 和超胞的 $V$ 混用，结果会差一个超胞与单胞的体积比。
:::

::: theorem 简谐极限
若能量对原子位移和应变是二次的，极化对它们是线性的，那么经典玻尔兹曼分布下的涨落公式与 0 K 弛豫离子的静态二阶导数**完全相同**，且与温度无关。所以 $d(T)$ 随温度的变化只来自非谐性（包括热膨胀）以及极化对位移的非线性。
:::

## 什么时候值得用 {mapping}

- **适用**：有低频、强非谐的模式（分子转动、氢键质子的运动、接近相变的软模），0 K 的二阶导数描述不了它们的有限温度行为。已有工作用有效哈密顿量的蒙特卡洛模拟，借涨落研究了钙钛矿铁电体压电响应随温度的变化 [@garcia-1998-batio3]。
- **不划算**：远离相变、近似简谐的刚性晶体。按上面的简谐极限，涨落公式只会以更大的统计误差重现 0 K 的结果。
- **极化从哪里来**：MD 每一帧都需要 $P$。DFT 级 MD 可以每帧算 Berry 相，但代价高；常见做法是训练一个预测偶极或玻恩电荷的模型（见 [[mlip-electrostatics]]）。只用固定的 $Z^{*}$ 乘以位移会漏掉夹持离子项 $\bar e$ 和 $Z^{*}$ 随构型的变化。

## 在本研究线里的样子 {mapping}

- **d33_theory 方案**：用 MLIP 跑恒压恒温 MD，用偶极模型给每帧的 $P$，按上面第一式求 $d(T)$。计算链里 DFPT 得到的 0 K 值可以作为低温端的检查：外推到低温时，两者应当接近（量子核效应除外，见下）。
- **系综**：恒压控压器必须给出正确的晶胞涨落。Parrinello–Rahman 一类全柔性晶胞的方法可以 [@parrinello-1981-npt]；Berendsen 控压只把压力往目标值拉，不产生正确的恒压系综，晶胞涨落是错的，不能用于涨落公式。
- **统计误差**：用分块平均 (block averaging) 估计 $N_{\mathrm{eff}}$。压电分量往往是小的交叉项，相对误差比弹性分量收敛得慢。

::: unverified 待核验
- 偶极模型在 MD 中极化跨越分支时，是否需要对 $P$ 做连续化（unwrap），取决于模型输出的是 Berry 相极化还是由电荷求和的偶极；按所用模型的文档确认。
- 周期体系里偶极涨落公式的边界条件：Ewald 求和取导电（tin-foil）边界时对应恒电场 $\mathcal E = 0$；其他边界条件需要修正项。按 [@neumann-1983-dipole-fluct] 核对。
- 分子晶体在室温下哪些模式可以按经典处理，需要具体计算的振动谱判断；含氢的高频模式通常不能。
:::

## 常见坑 {mapping}

- **控压器错误**：用了 Berendsen 或只允许各向同性变胞的控压器，剪切涨落被抑制，剪切分量（例如 $d_{16}$）会系统性偏小或为零。
- **参考晶胞**：$\eta$ 应当相对于平均晶胞计算；参考晶胞选错只改变 $\langle\eta\rangle$，不改变涨落，但转换到晶体坐标系时会把分量转错。
- **样本相关**：把相邻帧当作独立样本，会严重低估误差。
- **量子核效应**：经典 MD 在低温下高估振动幅度。低温端与 DFPT 比较时，要考虑这一点。

## 检验自己 {mapping}

::: question 推导
从 $H' = H - V\mathcal E_\alpha P_\alpha$ 出发，写出 $\partial\langle\eta_j\rangle/\partial\mathcal E_\alpha$ 的推导，确认 $V/k_{\mathrm B}T$ 的因子是怎么来的。
:::

::: question 解释
为什么在简谐、线性极化的极限下，涨落公式给出的 $d$ 与温度无关？这对解释 $d(T)$ 的温度依赖有什么意义？
:::

::: question 迁移
一条 1 ns 的 MD 轨迹，极化—应变的自相关时间约为 5 ps。估计 $N_{\mathrm{eff}}$，并据图 (b) 判断这能否把一个中等大小的协方差压到 10% 的相对误差以内。
:::
