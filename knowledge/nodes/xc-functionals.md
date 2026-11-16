```json
{
  "id": "xc-functionals",
  "title": "交换关联泛函",
  "type": "concept",
  "parent": "kohn-sham-dft",
  "research": [
    "piezo",
    "csp"
  ],
  "keywords": [
    "exchange-correlation functional",
    "LDA",
    "GGA",
    "meta-GGA",
    "hybrid functional",
    "double hybrid",
    "SCAN",
    "HSE",
    "B3LYP",
    "Jacob's ladder"
  ],
  "purpose": "Kohn–Sham DFT 里唯一需要近似的量是交换关联泛函；这一条讲各级近似分别用了哪些信息、丢掉了什么、代价多大，以及什么时候必须往上一级走。",
  "prereq": {
    "intuitive": [
      "[[kohn-sham-dft]]：把多电子问题变成单电子方程",
      "[[hartree-fock]]：精确交换是什么"
    ],
    "full": [
      "[[kohn-sham-dft]]：交换关联势 $v_{xc}$ 的来源",
      "均匀电子气与梯度展开"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-16",
  "sources": [
    "perdew-1992-pw92",
    "pbe-1996",
    "tao-2003-tpss",
    "sun-2015-scan",
    "heyd-2003-hse",
    "becke-1993-b3lyp",
    "burke-2012-perspective"
  ],
  "origin": "种子骨架（2026-11-09），只有题目和范围；2026-11-16 由雷达 4 篇交换关联泛函相关论文触发补正文（含 Functional and Density-Driven Errors in DFT: Quantum Monte Carlo Benchmark doi:10.1021/acs.jctc.6c00944 与 Wurtzite 表面高通量筛选 arXiv:2611.15138）",
  "changelog": [
    {
      "version": "0.1",
      "date": "2026-11-09",
      "note": "候选：只有题目与范围"
    },
    {
      "version": "0.2",
      "date": "2026-11-16",
      "note": "初稿正文：雅各布阶梯、各级用到的信息与代价、自相互作用与离域误差、在压电与分子晶体里的选择；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

Kohn–Sham DFT 把多电子问题精确地变成了单电子方程，代价是出现一个未知量：交换关联泛函 $E_{xc}[n]$。它包含了交换（泡利不相容）和关联（电子之间的动态躲避）两部分，加上动能中“非相互作用部分”之外的那一块。**这一类方法的全部近似都在这里。**

泛函按“用了多少局域信息”排成一级级台阶，通常叫雅各布阶梯 (Jacob's ladder)：

- 只用一个点的密度 $n(\mathbf{r})$；
- 再加密度梯度 $\nabla n$；
- 再加动能密度 $\tau$（或者密度的拉普拉斯）；
- 再加占据轨道 $\psi_i$（精确交换）；
- 再加虚轨道。

每一级都比上一级多知道一点信息，一般也更准一点，但计算代价和实现复杂度上升。图里把这几级排出来。

![各级交换关联泛函用到的信息和代表方法。示意图，不代表各方法在具体体系上的精度排序。](figs/xc-functional-ladder.svg)

| 级别 | 用到的量 | 代表方法 | 在 Kohn–Sham 框架里的代价 |
| --- | --- | --- | --- |
| LDA | $n(\mathbf{r})$ | PW92 关联 | 与 PBE 同级，最便宜 |
| GGA | $n,\ \nabla n$ | PBE、PBEsol | 与 LDA 同级 |
| meta-GGA | $n,\ \nabla n,\ \tau$ | TPSS、SCAN | 略高，需要动能密度 |
| 杂化 | 上式 + 占据轨道 $\psi_i$ | HSE、B3LYP | 需要计算精确交换，明显更贵 |
| 双杂化 | 上式 + 虚轨道 | 各类双杂化 | 最贵，接近 MP2 的量级 |

## 定义与公式 {math}

### 总能量的分解

$$E[n] = T_s[n] + \int v_{\mathrm{ext}}(\mathbf{r})n(\mathbf{r})\,d\mathbf{r} + E_H[n] + E_{xc}[n]$$

其中 $T_s$ 是非相互作用体系的动能；$v_{\mathrm{ext}}$ 是外势（原子核）；$E_H$ 是 Hartree（经典静电）能；$E_{xc}$ 是交换关联能。前三项都是精确已知的，$E_{xc}$ 必须近似。

### LDA 与 GGA

::: definition 局域密度近似
$$E_{xc}^{\mathrm{LDA}}[n] = \int n(\mathbf{r})\,\varepsilon_{xc}^{\mathrm{unif}}\!\left(n(\mathbf{r})\right)d\mathbf{r}$$

其中 $\varepsilon_{xc}^{\mathrm{unif}}(n)$ 是密度为 $n$ 的均匀电子气的单电子交换关联能。交换部分有解析式，关联部分通常用高精度量子蒙特卡洛拟合的参数化形式，PW92 是最常用的一种 [@perdew-1992-pw92]。
:::

GGA 再引入约化梯度 $s = |\nabla n|/(2k_F n)$，写成“LDA × 增强因子”的形式。PBE 的具体函数形式见 [[pbe]]；PBEsol 是同一形式下换参数的变体，为固体优化 [@pbe-1996]。

### meta-GGA：加入动能密度

$$E_{xc}^{\mathrm{mGGA}}[n,\nabla n,\tau] = \int n(\mathbf{r})\,\varepsilon_{xc}\!\left(n,\nabla n,\tau\right)d\mathbf{r}, \qquad \tau = \frac{1}{2}\sum_i |\nabla\psi_i|^2$$

其中 $\tau$ 是 Kohn–Sham 轨道的动能密度；$\psi_i$ 是占据轨道。

TPSS 是第一支不拟合实验、只满足精确条件的 meta-GGA [@tao-2003-tpss]。SCAN 满足一组更强的约束（17 条精确条件），在分子与固体上表现更均衡，但也更容易出现数值上的“过度结构化”，需要更细的网格 [@sun-2015-scan]。

::: approximation $\tau$ 的角色
加入 $\tau$ 的主要好处是能区分“单轨道区域”（如分子中的键、固体中的孤立电子）与“多轨道区域”（金属、均匀气体），从而更好地处理自相互作用误差。但 $\tau$ 依赖轨道，使泛函不再是密度的纯泛函，严格意义上超出了原始 Hohenberg–Kohn 定理的范围；实践中把它当作广义 Kohn–Sham 方案使用。
:::

### 杂化：掺入精确交换

$$E_{xc}^{\mathrm{hybrid}} = a\,E_x^{\mathrm{HF}} + (1-a)\,E_x^{\mathrm{DFT}} + E_c^{\mathrm{DFT}}$$

其中 $a$ 是精确交换的比例；$E_x^{\mathrm{HF}}$ 是用 Kohn–Sham 轨道算的 Hartree–Fock 交换；$E_x^{\mathrm{DFT}}$、$E_c^{\mathrm{DFT}}$ 是半局域部分。

- B3LYP 用三个参数（$a=0.20$）配合 B88 交换与 LYP 关联 [@becke-1993-b3lyp]，在分子化学里长期是默认选择。
- 全局杂化在固体里会遇到问题：精确交换是长程的，在周期性体系里计算与收敛都困难。HSE 把精确交换**屏蔽**到短程，长程仍用 GGA，因此在半导体与绝缘体里可用且开销可控 [@heyd-2003-hse]。

::: unverified 待核验
- 常用杂化的精确交换比例（例如 B3LYP 的 0.20、PBE0 的 0.25）属于方法定义的一部分，可按原文核对；不同程序对同一名称的实现细节（如是否用 VWN 关联）可能不同，换程序时要注意。
- 各泛函在具体体系上的误差（晶格常数偏差、带隙偏差、反应能偏差）随体系变化，本条目不给数值；需要时查对应基准研究。
- 触发本条目的 QMC 基准论文给出的“函数误差 vs 密度误差”分解，其具体框架尚未精读，不在此引用结论。
:::

### 两类系统误差

- **自相互作用误差** (self-interaction error)：在精确理论里一个电子不应与自己的电荷感生势相互作用；半局域泛函里这一项没有完全抵消，导致电子过度离域、能隙偏小、电荷转移能偏小。
- **离域误差** (delocalization error) 与**静态关联**：强关联或接近简并的体系（过渡金属化合物、某些缺陷）用单参考的 Kohn–Sham 方法本身就不够。

GGA 与 meta-GGA 主要缓解第一类，杂化再加一点精确交换进一步缓解；第二类通常需要别的框架（DFT+U、DMFT、多参考方法）。

## 在本研究线里的样子 {mapping}

### 压电与响应计算

- 压电张量 $d_{ij}$ 由弹性柔度与内坐标响应（玻恩有效电荷）组合而成（见 [[piezoelectric-tensor]]、[[dielectric-born]]、[[elastic-tensor]]）。实验值常在实验晶胞上测得，DFT 报告的常是优化晶胞上的值，比较时要说清是哪种。
- 泛函影响平衡晶胞，晶胞又影响 $d_{ij}$。对 β-甘氨酸这类以氢键与范德华堆积为主的晶体，泛函不加色散会给出过大的晶胞（见 [[dispersion-corrections]]）。
- 杂化泛函是否必要：对绝缘体，带隙低估一般不影响定性结论，但会影响电子介电常数；需要和实验的介电常数比较时，应先检查 PBE 的偏差有多大，再决定要不要上杂化。

### 分子晶体与结构预测

多晶型间的能量差很小，泛函选择直接影响排序。不同泛函加不同色散校正可能给出不同的稳定性顺序，这种差异本身就是需要报告的信息，而不是需要“选一个”的问题（见 [[error-sources]]、[[energy-landscape]]）。

## 常见坑 {mapping}

- **把“泛函更高级”当成“一定更准”**：对某类性质（例如固体晶格常数）PBEsol 常优于 PBE，但 PBE 对分子结合能更好；没有全局最优。
- **meta-GGA 用粗网格**：$\tau$ 对网格敏感，SCAN 在粗 k 点网格或大间距实空间网格上可能出现数值噪声。
- **杂化泛函的屏蔽参数混用**：HSE03 与 HSE06 的屏蔽参数不同，混用会让结果无法复现。
- **忽略色散**：任何半局域泛函都不含长程关联，分子晶体、层状材料、吸附问题必须额外加色散修正。
- **换泛函不换赝势**：POTCAR 是针对特定泛函生成的，例如用 PBE 的 PAW 数据集去配 SCAN 计算，严格来说不一致。

## 检验自己 {mapping}

::: question 解释
为什么加入动能密度 $\tau$ 可以缓解自相互作用误差？从“单轨道 vs 多轨道区域”的角度说明。
:::

::: question 推导
对杂化泛函，把 $E_x^{\mathrm{HF}}$ 写成占据轨道的双重求和，说明为什么它的计算量随体系大小增长得比半局域泛函快。
:::

::: question 迁移
你要比较 β-甘氨酸两个多晶型的相对稳定性，PBE-D3 与 SCAN 给出相反的顺序。设计一个方案判断哪个更可信，并说明需要检查哪些量。
:::
