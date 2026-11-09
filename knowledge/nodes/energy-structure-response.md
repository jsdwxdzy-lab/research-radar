```json
{
  "id": "energy-structure-response",
  "title": "从能量到结构与响应",
  "type": "concept",
  "trunk": "state-evolution",
  "also_trunks": ["observation-validation"],
  "purpose": "说明平衡结构、力常数、弹性和压电响应分别对应能量曲面的哪一阶导数，从而理解为什么结构算得接近，响应仍可能差得明显。",
  "prereq": {
    "intuitive": ["函数的极小点、一阶导数和二阶导数", "应变和极化的物理含义"],
    "full": ["多元函数的 Hessian 矩阵、特征分解与矩阵求逆", "[[method-layers]] 中“理论近似决定能量曲面”这一点"]
  },
  "status": "draft",
  "version": "0.1",
  "updated": "2026-11-09",
  "sources": ["baroni-2001-dfpt", "wu-2005-strain", "king-smith-1993-polarization", "vanderbilt-2018-berry", "ieee-176-piezo"],
  "changelog": [{"version": "0.1", "date": "2026-11-09", "note": "初稿：一维例子与多维推广已写；压电公式的指标和符号约定尚未核对原文"}]
}
```
## 一个自由度的最小例子 {intuition}

只看一个结构自由度 $x$。设能量在极小点 $x_0$ 附近是抛物线，并受一个外加广义力 $F$ 作用：

$$E(x) = \tfrac{1}{2}k\,(x - x_0)^2 - F\,x$$

令 $\mathrm{d}E/\mathrm{d}x = 0$，得到平衡位置和它对外力的响应：

$$x^{*} = x_0 + \frac{F}{k}, \qquad \chi \equiv \frac{\mathrm{d}x^{*}}{\mathrm{d}F} = \frac{1}{k}$$

结构（$F = 0$ 时的 $x^{*} = x_0$）只由极小点位置决定；响应 $\chi$ 只由曲率 $k$ 决定。两者是能量曲面的不同信息。

## 结构对了，响应可以不对 {intuition}

假设某个近似方法给出的能量曲面极小点完全正确，但曲率偏了 $\delta k$。它预测的结构与真实值相同，响应的相对误差却是

$$\frac{\chi' - \chi}{\chi} = \frac{1/(k+\delta k) - 1/k}{1/k} = -\frac{\delta k}{k + \delta k}$$

所以“优化出的晶格参数与实验接近”并不能推出“响应系数可靠”。反过来，结构偏差也不一定意味着响应偏差大。

::: theorem 软方向放大误差（上式的直接推论）
同样的绝对曲率误差 $\delta k$，在 $k$ 小（软）的方向上造成的相对响应误差更大。这只用到上式的代数，不依赖具体体系；它说的是敏感程度，不说明哪种近似在哪个体系里曲率偏多少。
:::

## 推广到多个自由度 {math}

把原子位移（以及需要时的应变）记为向量 $u$。在平衡点附近展开到二阶：

$$E(u) \approx E_0 + \tfrac{1}{2}\,u^{\mathsf T} K\, u - f^{\mathsf T} u$$

其中 $K$ 是力常数矩阵（能量的 Hessian），$f$ 是外加广义力。平衡位移是

$$u^{*} = K^{-1} f = \sum_{m} \frac{e_m^{\mathsf T} f}{\lambda_m}\, e_m$$

$\lambda_m$、$e_m$ 是 $K$ 的本征值和本征向量。如果某个本征值偏了 $\delta\lambda_m$，该模式的贡献改变约 $-\delta\lambda_m / \lambda_m^{2}$ 倍的 $e_m^{\mathsf T} f$。本征值越小（软模），对误差越敏感。

::: assumption 这里用到的假设
- 只保留到二阶（谐近似、线性响应）。
- 在静态晶格上讨论，不含温度引起的统计平均。
- $K$ 在所讨论的子空间内正定；如果有零或负本征值，需要先处理平移不变性或结构不稳定的问题。
:::

## 压电响应是能量的混合二阶导数 {math}

在零电场下，压电应力系数描述均匀应变 $\eta_j$ 引起的极化变化：

$$e_{\alpha j} = \left.\frac{\partial P_\alpha}{\partial \eta_j}\right|_{\mathcal{E}=0}$$

晶体中的极化需要用 Berry 相位定义，只有极化的**变化**有确定意义 [@king-smith-1993-polarization]。

应变时原子会在晶胞内重新弛豫。于是 $e$ 可以分成两部分：原子固定在应变后的分数坐标上的**夹持离子项** $\bar e$，以及原子弛豫带来的贡献。后者把三样东西串起来：玻恩有效电荷 $Z$（位移引起多少极化）、力常数矩阵的逆 $K^{-1}$（力引起多少位移）、内应变张量 $\Lambda$（应变引起多少力）[@wu-2005-strain]。示意地写成

$$e_{\alpha j} = \bar e_{\alpha j} + \frac{1}{\Omega} \sum_{m,n} Z_{m\alpha}\,\bigl(K^{-1}\bigr)_{mn}\,\Lambda_{nj}$$

$\Omega$ 是晶胞体积。$K^{-1}$ 出现在这里，意味着上一节“软模放大误差”的结论同样适用于压电响应的离子项。

::: unverified 待核验
- 上式的指标次序、符号和归一化因子按 [@wu-2005-strain] 的约定核对；目前只保证结构（$Z \cdot K^{-1} \cdot \Lambda$）是对的。
- 需要用 [@baroni-2001-dfpt] 确认：微扰方法和有限差分方法求的是同一组二阶导数，以及两者在什么条件下给出相同结果。
:::

## 和实验报告的系数怎么对应 {mapping}

实验常报告压电应变系数 $d$，而上面算的是 $e$。两者通过恒电场下的弹性柔顺系数 $s^{E}$ 联系 [@ieee-176-piezo]：

$$d_{\alpha k} = \sum_{j} e_{\alpha j}\, s^{E}_{jk}$$

所以把计算的 $e$ 换算成 $d$ 时，弹性常数的误差会一起传进来；柔顺系数大（弹性软）的方向同样会放大误差。

::: unverified 待核验
- Voigt 记号下的指标约定和是否需要额外因子，按 [@ieee-176-piezo] 核对。
- 实验测量的边界条件（夹持或自由、恒电场或恒电位移）与这里的定义是否一致，属于 [[error-sources]] 中“实验对应”的问题，需要逐项写清。
:::

## 检验自己 {mapping}

::: question 解释
用一句话说明：为什么“晶格参数和实验差 1%”不能直接推出“压电系数也只差 1% 左右”？
:::

::: question 推导
从 $E(u) = \tfrac{1}{2}u^{\mathsf T}Ku - f^{\mathsf T}u$ 出发，自己推出 $u^{*} = K^{-1}f$ 和单个本征值误差的一阶影响。哪一步用到了 $K$ 对称？
:::

::: question 迁移
如果某个有机晶体里存在一个很软的分子转动模式，而它对极化的贡献（对应的 $Z$ 分量）又很大，你预期计算的压电系数对哪些近似最敏感？
:::
