```json
{
  "id": "conformational-polymorphism",
  "title": "构象多晶型与构象代价",
  "type": "concept",
  "parent": "molecular-crystals",
  "research": [
    "csp"
  ],
  "keywords": [
    "conformational polymorphism",
    "conformer",
    "torsion angle",
    "conformational energy penalty",
    "crystal packing energy"
  ],
  "purpose": "同一分子以不同构象结晶时，晶体里的分子往往不是气相最稳定的那个构象；这一条讲“构象代价”和“堆积收益”怎样竞争，以及为什么结构搜索与能量排序里必须显式处理它。",
  "prereq": {
    "intuitive": [
      "[[molecular-crystals]]：分子晶体靠什么结合",
      "[[energy-landscape]]：多晶型是能量面上的不同盆地"
    ],
    "full": [
      "[[dispersion-corrections]]：堆积能的主要贡献",
      "[[csp-search-ranking]]：候选结构怎么排序"
    ]
  },
  "status": "draft",
  "version": "0.1",
  "updated": "2026-11-16",
  "sources": [
    "cruz-cabeza-2013-confpolymorph",
    "cruz-cabeza-2015-polymorph",
    "nyman-2015-vib",
    "beran-2016-review"
  ],
  "origin": "定时任务 2026-11-16，由两篇 2026-11 的论文触发：Experimental and Theoretical Charge Density Study of Isonicotinamide Polymorphs（J. Phys. Chem. C, doi:10.1021/acs.jpcc.6c05509）与 Recent Advances and Future Directions in Polymorphism Research of Energetic Materials（CrystEngComm, doi:10.1039/d6ce00846a）",
  "changelog": [
    {
      "version": "0.1",
      "date": "2026-11-16",
      "note": "初稿：构象代价与堆积能的竞争、扭转角作为构象坐标、对能量排序的影响、常见坑；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

一个分子在晶体里不是刚性的：它的扭转角、环的褶皱、取代基的朝向都可以变。**气相最稳定的构象不一定是最容易堆积的构象**。

两件事在竞争：

- **构象能** $E_{\mathrm{conf}}$：把分子从气相最优构象扭到另一个构象要付的能量。通常是一个以扭转角 $\theta$ 为变量的周期性势，最小在某个 $\theta_0$。
- **堆积能** $E_{\mathrm{pack}}$：这个构象在晶格里能放得多密、相互作用多强。它偏好另一个构象，因为那个形状更适合紧密堆积。

晶体里最终的构象由**两者之和**决定，而不是各自的最小值。图里用玩具函数画了这个竞争：蓝线的最小在 $\theta=0$，绿线的最小在 $\theta \approx 0.95$，黑线（总和）的最小落在两者之间、偏向绿线一侧。

![示意：左图是同一分子取两个不同扭转角 $\theta$ 的构象；右图是构象能与堆积能随 $\theta$ 的变化，以及两者之和。曲线由 $E_{\mathrm{conf}}=\varepsilon\sin^2\theta$ 和一条指数型堆积项拼出，只用来示意竞争，坐标数值不对应任何真实分子。](figs/conformational-polymorphism.svg)

| 符号 | 是什么 | 图里对应哪部分 |
| --- | --- | --- |
| $\theta$ | 分子内的扭转角（构象坐标） | 横轴；左图红色圆弧标出的角 |
| $E_{\mathrm{conf}}(\theta)$ | 构象能，相对气相最优构象 | 右图蓝色曲线 |
| $E_{\mathrm{pack}}(\theta)$ | 堆积能，随构象变化的部分 | 右图绿色曲线 |
| 总和 | $E_{\mathrm{conf}} + E_{\mathrm{pack}}$ | 右图黑色粗线 |
| 蓝点 | 气相最优构象 | 横轴 $\theta=0$ 处 |
| 红圈 | 晶体里的最优构象 | 总和曲线的极小处 |

注意图中红圈和蓝点**不在同一位置**：气相最稳定的构象不是晶体里最终采用的那个。这就是“构象多晶型”问题的核心。

## 定义与公式 {math}

::: definition 构象多晶型
同一种化合物以**不同分子构象**结晶成不同的晶体结构，称为构象多晶型 (conformational polymorphism) [@cruz-cabeza-2013-confpolymorph]。
:::

### 能量的分解

对每个候选晶体结构，把总能量写成两部分：

$$E_{\mathrm{tot}} = E_{\mathrm{conf}}(\theta) + E_{\mathrm{pack}}(\theta, \text{晶格参数})$$

其中 $E_{\mathrm{conf}}$ 是分子从气相最优构象扭到晶体中构象所用的能量（有时叫 conformer energy penalty）；$E_{\mathrm{pack}}$ 是把该构象的分子按特定方式排布时，分子间相互作用的净贡献（含色散、静电、氢键，见 [[dispersion-corrections]]）。

$E_{\mathrm{conf}}$ 通常可以写成扭转势

$$E_{\mathrm{conf}}(\theta) = \sum_{n} \frac{V_n}{2}\left[1 - \cos(n\theta - \gamma_n)\right]$$

其中 $V_n$ 是第 $n$ 阶傅里叶系数；$\gamma_n$ 是相位；求和遍历主要的傅里叶项。这是分子力场里标准扭转项的形式，也可以用 DFT 的约束优化扫出来。

::: empirical 构象代价的量级
在许多有机分子晶体中，晶体里分子的构象比气相最优构象高一些，但又不足以阻止结晶；具体多大取决于分子柔性、可形成的氢键网络与堆积方式 [@cruz-cabeza-2013-confpolymorph]。这里不给单一数值——不同分子差异很大。
:::

### 为什么这件事对结构预测是硬的

- **构象空间与晶体空间是乘积**：多一个可旋转的键，候选构象数就成倍增长，而每个构象还要单独做晶格搜索。
- **误差尺度重叠**：常见的 DFT 色散校正方法之间，多晶型能量差的不确定度与构象代价常常在同一量级，排序对方法和设置敏感 [@nyman-2015-vib] [@beran-2016-review]。
- **构象在晶体里会被“压”**：进入晶格后，分子内几何也会因分子间作用而变形，气相构象能只是一个近似起点。

## 在本研究线里的样子 {mapping}

- **搜索阶段**：先用分子力学或 MLIP 生成候选，允许扭转角在合理范围内变化（见 [[csp-search-ranking]]）；固定一个构象做全空间搜索会漏掉整类解。
- **排序阶段**：对每个候选按上式分解能量，检查排名靠前的是不是“构象代价很高”的那一类；如果是，要复核堆积能那一项（色散、静电）有没有算对。
- **与实验对照**：实验上能测的是晶格参数、分子几何（X 射线/中子衍射、电荷密度），这些可以直接验证某个候选的构象对不对，而不只是能量排名。β-甘氨酸的压电复现里，不同多晶型的构象差异首先体现在晶胞与分子几何上（见 [[piezoelectric-tensor]]、[[convergence-testing]]）。

::: unverified 待核验
- “构象代价通常在多少 kJ/mol”没有统一答案，随分子与堆积方式大幅变化；本节只给了形式，不给范围。
- 触发本条目的两篇论文（异烟酰胺多晶型电荷密度研究、含能材料多晶型综述）里的具体构象与能量数据尚未精读，不引用其数值。
- 扭转势参数 $V_n$ 的典型值取决于所用力场/泛函，需按具体方法查原文。
:::

## 常见坑 {mapping}

- **把气相最优构象当成晶体的构象**：搜索时冻结构象，会系统性地漏掉构象多晶型。
- **构象能算错基准**：$E_{\mathrm{conf}}$ 必须相对**同一分子、同一方法**下的气相最优构象，方法换了基准就变了。
- **忽视分子内弛豫**：用刚性分子做初筛可以，但最终排序要让分子内几何弛豫。
- **能量分解当成精确可加**：构象能与堆积能在晶体中互相影响，上面的加法是近似，不是严格分解。
- **只报一个能量**：不同泛函/色散校正给出不同排序时，应该把差异报出来（见 [[error-sources]]），而不是挑一个。

## 检验自己 {mapping}

::: question 解释
为什么气相最稳定的构象不一定是晶体里采用的构象？用图里的两条曲线说明。
:::

::: question 推导
假设 $E_{\mathrm{conf}}(\theta)=A\sin^2\theta$，$E_{\mathrm{pack}}(\theta)=-\varepsilon\,e^{-(\theta-\theta_p)^2/2\sigma^2}$。写出总能量最小满足的条件，并说明什么时候极小会从 $\theta=0$ 移到 $\theta_p$ 附近。
:::

::: question 迁移
你有一组候选结构，排序第一的构象代价比第二名高很多。给出两条可以判断“这个排名是否可信”的检查，并说明各自能排除什么错误。
:::
