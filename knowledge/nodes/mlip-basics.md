```json
{
  "id": "mlip-basics",
  "title": "机器学习势",
  "type": "method",
  "parent": "ml",
  "research": [
    "mlip"
  ],
  "keywords": [
    "machine learning interatomic potential",
    "MLIP",
    "force field",
    "active learning"
  ],
  "purpose": "用数据拟合势能面：局域性假设、描述符与训练数据，以及外推时为什么会出错。",
  "prereq": {
    "intuitive": [
      "[[born-oppenheimer]]：势能面只是原子坐标的函数",
      "回归与过拟合"
    ],
    "full": [
      "[[kohn-sham-dft]] 与 [[hellmann-feynman]]：训练标签从哪里来",
      "[[equivariance]]",
      "[[probabilistic-modeling]]"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "behler-2007-nn",
    "behler-2011-symmetry",
    "bartok-2010-gap",
    "bartok-2013-soap",
    "podryabinkin-2017-active",
    "unke-2021-mlff"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：原子能分解与局域性、截断函数、描述符、能量力应力联合损失、内插与外推、主动学习、常见坑；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

DFT 算一个构型的能量和力要几分钟到几小时。结构搜索、分子动力学、声子要算成千上万个构型，DFT 负担不起。机器学习势 (machine learning interatomic potential, MLIP) 的思路是：先用 DFT 算一批构型，再训练一个模型，让它直接从原子坐标预测能量、力和应力，速度快几个数量级。

几乎所有 MLIP 都建立在一个假设上：**局域性**。总能写成每个原子的能量之和，每个原子的能量只取决于它周围截断半径 $r_c$ 内的邻居 [@behler-2007-nn]。这让模型可以用于任意大小的体系，计算量与原子数成正比。

关键的限制：模型只在训练数据覆盖的构型附近可靠（内插）。遇到训练集之外的构型（外推），它可能给出看起来合理、实际上完全错误的能量。

![左（示意）：原子 i 的能量只依赖截断球内的邻居（蓝色），球外原子（灰色）不影响它。右（示意）：在训练数据覆盖的区域内拟合良好；离开这个区域后模型可以任意偏离真实势能面。](figs/mlip-local-cutoff.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $i$ | 正在计算原子能的中心原子 | 左图橙色原子 |
| $r_c$ | 截断半径 | 左图虚线圆的半径 |
| 蓝色原子 | 截断球内的邻居，进入描述符 | 左图蓝点 |
| 训练数据 | DFT 算过的构型 | 右图绿点与绿色区域 |
| 拟合模型 | MLIP 的预测 | 右图橙色虚线 |

## 定义与公式 {math}

::: definition 原子能分解
$$E(\{\mathbf{r}\}) = \sum_{i=1}^{N} E_i, \qquad E_i = \varepsilon_{Z_i}\bigl(\mathbf{D}_i\bigr), \qquad \mathbf{D}_i = \mathbf{D}\bigl(\{\mathbf{r}_{ij},\,Z_j : r_{ij} < r_c\}\bigr)$$

其中 $N$ 是原子数；$E_i$ 是原子 $i$ 的能量；$Z_i$ 是它的元素；$\mathbf{r}_{ij} = \mathbf{r}_j - \mathbf{r}_i$ 是到邻居 $j$ 的相对位置，$r_{ij}$ 是其长度；$\mathbf{D}_i$ 是描述符 (descriptor)，把邻居环境编码成一个固定长度的向量；$\varepsilon_{Z}$ 是对每种元素学习的函数（神经网络、高斯过程或线性模型）[@behler-2007-nn]。
:::

原子能 $E_i$ 本身不是可观测量，只有总和 $E$ 有物理意义。

::: definition 截断函数
为了让能量在原子跨过 $r_c$ 时连续可导，邻居的贡献乘以一个平滑衰减到零的函数，例如

$$f_c(r) = \begin{cases} \tfrac{1}{2}\left[\cos\left(\pi r / r_c\right) + 1\right], & r < r_c \\ 0, & r \ge r_c \end{cases}$$

其中 $r$ 是原子间距离 [@behler-2011-symmetry]。
:::

### 描述符要满足什么

能量在整体平移、旋转和同种原子交换下不变，所以描述符也必须不变。常见做法：用距离和角度构造对称函数 [@behler-2011-symmetry]，或者把邻居密度展开成径向函数乘球谐函数，再取旋转不变的组合（SOAP）[@bartok-2013-soap]。更新的模型不再手工设计描述符，而是用等变神经网络学习（见 [[equivariance]] 与 [[mace]]）。

### 力与应力

$$\mathbf{F}_k = -\frac{\partial E}{\partial \mathbf{r}_k}, \qquad \sigma_{\alpha\beta} = \frac{1}{\Omega}\frac{\partial E}{\partial \varepsilon_{\alpha\beta}}$$

其中 $\mathbf{r}_k$ 是原子 $k$ 的坐标，$\Omega$ 是晶胞体积，$\varepsilon_{\alpha\beta}$ 是应变。力和应力由能量求导得到，因此自动满足能量守恒（力是保守力）。

::: definition 训练损失
$$\mathcal{L} = \sum_{s}\left[ w_E\left(\frac{E_s - E_s^{\mathrm{DFT}}}{N_s}\right)^{2} + \frac{w_F}{3N_s}\sum_{k}\left|\mathbf{F}_{s,k} - \mathbf{F}_{s,k}^{\mathrm{DFT}}\right|^{2} + w_\sigma\,\bigl\|\boldsymbol{\sigma}_s - \boldsymbol{\sigma}_s^{\mathrm{DFT}}\bigr\|^{2}\right]$$

其中 $s$ 遍历训练构型；$N_s$ 是构型 $s$ 的原子数；$w_E, w_F, w_\sigma$ 是能量、力、应力的权重。每个构型只有 1 个能量，却有 $3N_s$ 个力分量，所以力提供了大部分训练信息 [@unke-2021-mlff]。
:::

::: assumption 局域性
截断半径之外的相互作用被忽略，或者只通过多层消息传递间接包含（见 [[mace]]）。长程静电、色散和电场响应不在这个假设内（见 [[mlip-electrostatics]]）。
:::

### 内插、外推与主动学习

模型的误差在训练数据附近小，远离时不受控。主动学习的思路是：用模型跑模拟，用某种不确定性指标（模型集成的分歧、或描述符相对训练集的“外推程度”）挑出模型没把握的构型，送去做 DFT，加入训练集，再训练 [@podryabinkin-2017-active]。

## 在本研究线里的样子 {mapping}

- **预优化**：在结构搜索中，先用 MLIP（例如 [[mace]]）把大量候选结构优化到局部极小，再挑能量低的做 DFT（见 [[csp-search-ranking]]）。
- **标签必须一致**：训练集里所有构型要用同一套 DFT 设置（泛函 PBE-D3、POTCAR、截断能、k 点密度），否则模型学到的是设置之间的差异（见 [[convergence-testing]]）。
- **覆盖什么构型**：只用平衡结构训练，模型对应变、位移、高能候选结构都是外推。弹性、声子和压电需要的恰恰是偏离平衡的小扰动。
- **验证不只看 RMSE**：还要在下游任务上验证，比如弹性常数、声子、多晶型能量排序是否和 DFT 一致（见 [[benchmarking]]）。

## 常见坑 {mapping}

- **测试集和训练集来自同一条轨迹**：相邻帧高度相关，测试误差会严重低估真实误差。
- **能量 RMSE 很小但排序错误**：多晶型能量差可能只有几 meV/原子，和模型误差同一量级。
- **力看起来准，应力没训练**：变胞优化会把晶胞带到错误的体积。
- **模拟中途“爆炸”**：原子靠得太近时进入模型从未见过的区域，能量可能反而下降。这是外推问题的典型表现。

## 检验自己 {mapping}

::: question 解释
为什么把总能分解成原子能之和以后，模型就能用到比训练集大得多的体系上？这一分解又放弃了什么？
:::

::: question 推导
一个 40 原子的构型有 1 个能量标签和多少个力分量？据此解释为什么训练时加入力会显著减少所需构型数。
:::

::: question 迁移
你的 MLIP 在 β-甘氨酸平衡结构附近力误差很小，但用它做结构搜索时找到一个能量比实验结构低很多的奇怪结构。你会怎样判断这是真的发现还是外推错误？
:::
