```json
{
  "id": "enhanced-sampling",
  "title": "增强采样与重加权",
  "type": "method",
  "parent": "statmech",
  "research": [
    "mlip",
    "csp"
  ],
  "keywords": [
    "umbrella sampling",
    "WHAM",
    "MBAR",
    "metadynamics",
    "reweighting",
    "biased sampling",
    "free energy profile"
  ],
  "purpose": "体系的自由能面有高垒时，普通 MD 在有限时间里采不到垒两边，算出来的自由能是错的；这一条讲怎样用偏置把采样推过垒，再怎样把偏置的影响严格地除掉，恢复无偏的自由能。",
  "prereq": {
    "intuitive": [
      "[[free-energy]]：自由能是概率的负对数",
      "[[molecular-dynamics]]：MD 采样什么"
    ],
    "full": [
      "[[ensembles]]：配分函数与系综平均",
      "[[mlip-basics]]：用机器学习势跑 MD"
    ]
  },
  "status": "draft",
  "version": "0.1",
  "updated": "2026-11-16",
  "sources": [
    "torrie-1977-umbrella",
    "kumar-1992-wham",
    "shirts-2008-mbar",
    "laio-2002-metad",
    "frenkel-2002-sim"
  ],
  "origin": "定时任务 2026-11-16，由两篇 2026-11 的论文触发：Reweighting Free Energy Profiles with Universal Machine Learning Interatomic Potentials（J. Chem. Theory Comput., doi:10.1021/acs.jctc.6c02044）与 Sampling Free Energy Landscapes of Ionic Colloidal Crystal Systems Using Machine-Learned Proxy Models（J. Phys. Chem. Lett., doi:10.1021/acs.jpclett.6c02885）",
  "changelog": [
    {
      "version": "0.1",
      "date": "2026-11-16",
      "note": "初稿：偏置采样、WHAM/MBAR、伞形采样与元动力学的差别、与机器学习势结合时的重加权、常见坑；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

自由能是概率的负对数（见 [[free-energy]]）：

$$F(\xi) = -k_B T \ln p(\xi) + \text{常数}$$

其中 $\xi$ 是你关心的一两个慢变量（反应坐标、扭转角、配位数、晶胞参数），$p(\xi)$ 是平衡时体系处于 $\xi$ 附近的概率。

在有限长度的 MD 里，体系在垒的一侧停留的时间远多于跨越垒的时间，$p(\xi)$ 在高垒区根本采不到。而自由能垒恰好由垒顶那一小段概率决定，所以**漏采样的区域不是“精度差一点”，而是数值完全不可信**。

增强采样的思路是：在 $\xi$ 上加一个已知的偏置势，把采样从最低点“抬”出来，让体系愿意访问垒顶和别的盆地；采完之后，再用偏置的解析形式把它除掉。图里左边是加偏置，右边是除掉偏置。

![示意：左图是加偏置，每个窗口一条抛物线 $w_i(\xi)=\frac{1}{2}\kappa(\xi-\xi_i)^2$，叠加后体系在整个 $\xi$ 区间都有采样；右图是把偏置除掉后的概率密度。曲线由一维玩具势计算得到，只用来示意流程，不对应任何真实体系。](figs/enhanced-sampling-bias.svg)

| 符号 | 是什么 | 图里对应哪部分 |
| --- | --- | --- |
| $\xi$ | 反应坐标（慢变量） | 横轴 |
| $F(\xi)$ | 无偏自由能 | 左图黑色粗线 |
| $w_i(\xi)$ | 第 $i$ 个窗口的偏置势 | 左图细蓝抛物线 |
| $\xi_i$ | 窗口中心 | 左图坐标轴下方的蓝色短竖线 |
| $p_b(\xi)$ | 偏置下采到的（有偏）概率密度 | 右图灰色填充 |
| $p_0(\xi)$ | 无偏概率密度 | 右图橙色曲线 |

图中右面板的 $p_0$ 与左面板的 $F$ 互为负对数——这正是重加权要做的事：把“在有偏分布下采到的样本”换算回“无偏分布下的概率”。

## 定义与公式 {math}

### 偏置采样与重加权恒等式

::: definition 重加权
在偏置势 $U_b(\xi)$ 下跑 MD，得到有偏分布 $p_b$。无偏分布 $p_0$ 与它的关系是

$$p_0(\xi) = \frac{1}{Z}\, p_b(\xi)\, e^{\beta U_b(\xi)}, \qquad Z = \int p_b(\xi)\, e^{\beta U_b(\xi)}\, d\xi$$

其中 $\beta = 1/(k_B T)$；$U_b$ 是你**自己加上的**偏置，解析已知；$Z$ 是归一化常数，它把指数项重新归一化。这条恒等式本身是严格的，不需要近似——只要采样足够、$U_b$ 已知，重加权就没有系统误差。
:::

$Z$ 一般很难直接算（它等价于两套势之间的自由能差，形式上是一个 Zwanzig 微扰 [@zwanzig-1954]）。伞形采样 (umbrella sampling) 的做法是把它拆成许多互相重叠的窗口 [@torrie-1977-umbrella]：每个窗口里偏置相对平缓，$Z$ 的估计在窗口内稳定，再用重叠区把相邻窗口拼接起来。

### 从直方图拼接到 MBAR

最早的拼接方法是 WHAM（weighted histogram analysis method）[@kumar-1992-wham]：把各窗口的直方图用自洽方程联立，解出每个窗口的常数 $f_i$。

MBAR（multistate Bennett acceptance ratio）[@shirts-2008-mbar] 不再先做直方图，而是直接对**每个样本**加权。设第 $i$ 个窗口的样本来自偏置势 $U_i$，则

$$\hat{f}_i = -\ln \sum_{n=1}^{N} \frac{e^{-\beta U_i(x_n)}}{\sum_{k=1}^{K} N_k\, e^{\hat{f}_k - \beta U_k(x_n)}}$$

其中 $N$ 是所有窗口样本总数；$N_k$ 是第 $k$ 个窗口的样本数；$\hat{f}_k$ 是待解的窗口自由能常数；$U_k(x_n)$ 是样本 $x_n$ 在第 $k$ 个偏置势下的能量。这是一个自洽方程组，迭代求解。

::: theorem MBAR 的最优性
在只利用“样本来自已知偏置势”这一信息、不做其他假设的条件下，MBAR 给出的自由能估计方差最小；WHAM 是它在“把样本先归入直方图区间”时的特例 [@shirts-2008-mbar]。
:::

这句话的实用含义：**窗口重叠不好、样本量不均时，WHAM 的直方图分箱会丢掉信息，MBAR 更稳**。代价是 MBAR 要保存全部样本的能量（或者能量矩阵），内存与计算量随样本数增长。

### 元动力学：偏置不是预设的

伞形采样的偏置是一组**事先固定**的抛物线，窗口中心要自己选、要保证重叠。元动力学 (metadynamics) [@laio-2002-metad] 换一种做法：一边跑一边往已经访问过的地方“填高斯”，让体系自己离开盆地：

$$U_b(\xi, t) = \sum_{t' < t} W \exp\!\left[-\frac{(\xi - \xi(t'))^2}{2\sigma^2}\right]$$

其中 $W$ 是每次填的高斯高度；$\sigma$ 是高斯宽度；$\xi(t')$ 是第 $t'$ 步时体系所在的 $\xi$ 位置。填满了的地方偏置就高，体系自然去没填过的地方。

::: approximation 元动力学与自由能
在准静态极限（填得足够慢、高斯足够小）下，累积的偏置 $U_b(\xi)$ 趋近 $-F(\xi)$ 加上一个常数。实际计算里这个等式只是近似，偏差随填的速率变化，需要跑多条独立轨迹或用其他方式再校正。
:::

## 在本研究线里的样子 {mapping}

### 用机器学习势做增强采样

MLIP 使能跑几纳秒到微秒的 MD（见 [[mlip-basics]]、[[molecular-dynamics]]），垒的跨越变得可行，但**对慢变量来说仍然不够**。常见组合：

1. 用 MLIP 跑偏置 MD，得到 $p_b(\xi)$；
2. 用同一偏置解析地重加权，得到 $F(\xi)$；
3. 在关键点上用 DFT 单点校正绝对能量，检查 MLIP 的系统偏差（见 [[benchmarking]]）。

这条路线的工作量主要在**验证**：MLIP 在垒顶、在高能构象上是否仍然准，决定了 $F(\xi)$ 的垒高是否可信，而不是采样够不够。微调过的势在远离平衡处失效的风险最大（见 [[mlip-finetuning]]）。

### 与结构搜索的关系

多晶型之间的自由能差、构象异构体的能量差，都能用同样的重加权思路从 MD 里得到（见 [[energy-landscape]]、[[csp-search-ranking]]）。相对静态 0 K 能量排序，这一步补上了振动与构象熵的贡献。

::: unverified 待核验
- 具体程序的默认设置（窗口数、高斯高度与宽度、填加速率、收敛判据）随版本变化，按所用程序文档核对，不在这里给数值。
- 两篇触发论文报告的具体加速倍数与误差，尚未精读，不在正文引用其数值。
- 偏置过程中所用的慢变量选择方法（如基于主成分或基于机器学习的坐标）本身是新研究方向，这里只提到“慢变量需要选”，不给具体算法。
:::

## 常见坑 {mapping}

- **窗口重叠不足**：相邻窗口的采样区间不重叠，拼接时 $Z$ 被外推，结果在缝隙处出现虚假的台阶。
- **慢变量选错**：$\xi$ 不能区分两个真正不同的盆地（例如没包含关键的扭转角），体系在 $\xi$ 固定时仍在别的方向上来回跳，重加权后的 $F(\xi)$ 是两套分布混在一起的平均，没有意义。
- **认为“跑了偏置就等于采到了”**：偏置只保证在 $\xi$ 方向上有样本，垂直方向仍可能没松弛。
- **元动力学的偏置被当成自由能直接引用**：没有检查准静态性，垒高被低估。
- **忘了报告采样收敛**：同一个 $F(\xi)$ 用不同初速度、不同窗口数跑两遍，差别有多大，是判断结果能不能用的第一手证据（见 [[convergence-testing]] 的思路）。

## 检验自己 {mapping}

::: question 解释
为什么说“漏采样区域不是精度差一点，而是数值完全不可信”？用 $F = -k_BT\ln p$ 说明。
:::

::: question 推导
无偏分布 $p_0$ 与偏置分布 $p_b$ 之间满足 $p_0 \propto p_b e^{\beta U_b}$。从配分函数 $Z_0 = \int e^{-\beta U_0} d\xi$ 和 $Z_b = \int e^{-\beta (U_0 + U_b)} d\xi$ 出发推出这条关系，并说明 $Z = Z_b/Z_0$。
:::

::: question 迁移
你想用 MACE 算 β-甘氨酸两个构象异构体之间的自由能差。设计一个伞形采样方案：慢变量取什么、窗口怎么放、怎样验证窗口重叠够了、最后怎样用 DFT 检查 MLIP 的垒高。
:::
