```json
{
  "id": "mace",
  "title": "MACE 与等变消息传递",
  "type": "method",
  "parent": "mlip-basics",
  "research": [
    "mlip",
    "csp"
  ],
  "keywords": [
    "MACE",
    "equivariant message passing",
    "foundation model",
    "universal potential"
  ],
  "purpose": "MACE 怎样用高阶等变消息传递表示多体相互作用，预训练通用势在分子晶体上的适用范围。",
  "prereq": {
    "intuitive": [
      "[[mlip-basics]]：原子能分解与截断半径",
      "图神经网络的消息传递"
    ],
    "full": [
      "[[equivariance]]：球谐函数与张量积",
      "[[dispersion-corrections]]"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "batatia-2022-mace",
    "batatia-2022-design",
    "batzner-2022-nequip",
    "batatia-2023-mp0",
    "kovacs-2023-maceoff"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：消息传递与感受野、原子基与多体张量积、读出、MACE-MP-0 与 MACE-OFF 的定位、在分子晶体上的用法与常见坑；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

[[mlip-basics]] 里的原子能只看截断球内的邻居。要描述好化学键，原子能不仅要依赖两两距离，还要依赖三个、四个原子之间的角度关系，也就是**多体** (many-body) 相互作用。

两类思路：

- **消息传递** (message passing)：每个原子从邻居那里收集信息，更新自己的特征；重复几层，信息就能传得更远，组合出更复杂的多体关系。缺点是层数多了计算慢、难以并行。
- **原子团簇展开** (ACE)：在一层之内，用邻居特征的张量积直接构造高阶多体项。

MACE 把两者结合起来：每一层先用张量积构造高阶的多体特征，再做消息传递。因为每层已经是多体的，只需要很少几层 [@batatia-2022-mace]。所有特征都是等变的（见 [[equivariance]]），所以能量严格旋转不变。

![左（示意）：两层消息传递时，中心原子 i 间接看到 2r_c 范围内的原子。右：一层 MACE 的计算流程（简化），中间两步重复 T 层。](figs/mace-message-passing.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $r_c$ | 每一层的截断半径 | 左图蓝色虚线圆 |
| $2r_c$ | 两层后的感受野 | 左图橙色点线圆 |
| $\mathbf{r}_{ij},\ Z_j$ | 邻居相对位置和元素 | 右图第一个框 |
| $A_i$ | 原子基：邻居信息的加权和（两体） | 右图第二个框 |
| $B_i$ | $A_i$ 的张量积（多体） | 右图第三个框 |
| $h_i^{(t)}$ | 第 $t$ 层的原子特征 | 右图第四个框 |
| $E_i$ | 原子能 | 右图最后一个框 |

## 定义与公式 {math}

下面是简化写法，省略了通道指标和可学习权重的细节，完整形式见原文 [@batatia-2022-mace]。

::: definition 原子基
$$A^{(t)}_{i,lm} = \sum_{j \in \mathcal{N}(i)} R^{(t)}_{l}(r_{ij})\,Y_{l}^{m}(\hat{\mathbf{r}}_{ij}) \otimes h^{(t)}_{j}$$

其中 $t$ 是层数；$\mathcal{N}(i)$ 是 $r_c$ 内的邻居；$R_l(r)$ 是可学习的径向函数（带截断函数）；$Y_l^m$ 是球谐函数，$\hat{\mathbf{r}}_{ij}$ 是单位方向向量；$h_j^{(t)}$ 是邻居的特征；$\otimes$ 表示用 Clebsch–Gordan 系数耦合（见 [[equivariance]]）。$A$ 是对邻居的求和，所以只包含两体信息（中心原子加一个邻居）。
:::

::: definition 高阶多体特征
$$B^{(t)}_{i,\nu} = \underbrace{A^{(t)}_{i} \otimes A^{(t)}_{i} \otimes \cdots \otimes A^{(t)}_{i}}_{\nu}$$

其中 $\nu$ 是相关阶数 (correlation order)。$\nu$ 个 $A$ 的乘积包含中心原子和 $\nu$ 个邻居的联合信息，即 $\nu+1$ 体项。先求和再相乘，计算量与邻居数成线性，而不是显式枚举所有原子组合 [@batatia-2022-mace]。
:::

::: definition 消息、更新与读出
$$m^{(t)}_i = \sum_{\nu=1}^{\nu_{\max}} W_\nu\,B^{(t)}_{i,\nu}, \qquad h^{(t+1)}_i = U^{(t)}\,m^{(t)}_i + V^{(t)}\,h^{(t)}_i, \qquad E_i = \sum_{t} \mathcal{R}^{(t)}\bigl(h^{(t)}_i\bigr)$$

其中 $W_\nu, U, V$ 是可学习的线性映射（只混合同阶 $l$ 的特征，保证等变）；$\mathcal{R}^{(t)}$ 是读出函数，只取不变（$l=0$）部分；总能是 $E = \sum_i E_i$，力和应力由求导得到。
:::

::: unverified 待核验
- MACE 常用设置：2 层、$\nu_{\max}=3$（每层最多四体）、$l$ 的最大值和每层截断半径，按原文和当前代码默认值核对后写入。
:::

### 预训练通用势

- **MACE-MP-0**：在 Materials Project 的大量无机晶体 DFT 数据上训练，覆盖周期表大部分元素，目标是“开箱即用”的通用势 [@batatia-2023-mp0]。
- **MACE-OFF**：针对有机分子训练的短程势，面向分子体系和分子晶体 [@kovacs-2023-maceoff]。

两者的训练数据来自不同的 DFT 方法，所以它们的“参考答案”不同，和你自己的 PBE-D3 计算也不一定一致。

::: unverified 待核验
- MACE-MP-0 训练数据所用的泛函（Materials Project 的 PBE/PBE+U），是否推荐叠加 D3 使用；MACE-OFF 训练数据的泛函与基组。按原文核对后补上。
:::

## 在本研究线里的样子 {mapping}

- **CSP 预优化**：用 MACE 把大量候选的 β-甘氨酸类结构优化到局部极小，再挑低能结构做 PBE-D3 精修（见 [[csp-search-ranking]]）。重点是排序大致可靠，不是绝对能量。
- **选哪个预训练模型**：有机分子晶体更接近 MACE-OFF 的训练分布；MACE-MP-0 覆盖元素更广。实际选择要在你自己的体系上用少量 DFT 结果做比较（见 [[benchmarking]]）。
- **色散**：如果所用模型的训练标签不含色散，分子晶体需要另外叠加 D3；如果已含色散，再叠加就会重复计算（见 [[dispersion-corrections]]）。
- **不够准时**：用自己的 PBE-D3 数据微调（见 [[mlip-finetuning]]）。
- **电场响应**：MACE 的标准输出只有能量、力、应力，不给 Born 电荷和极化（见 [[mlip-electrostatics]]）。

## 常见坑 {mapping}

- **通用势当成 DFT 用**：在你的体系上没验证过，误差可能比多晶型能量差还大。
- **色散重复或缺失**：先确认模型训练标签是否含色散，再决定是否加 D3。
- **用在训练分布之外**：例如极高压缩、断键、带电体系。
- **只看能量不看应力**：变胞优化依赖应力，应力误差会直接变成晶胞误差。

## 检验自己 {mapping}

::: question 解释
为什么 MACE 只需要 2 层左右，而早期的消息传递网络需要更多层？用“每层的多体阶数”回答。
:::

::: question 推导
设相关阶数 $\nu=3$，层数为 2，每层截断 5 Å。一个原子的能量最多依赖多远的原子？每层最多包含几体相互作用？
:::

::: question 迁移
你用 MACE-MP-0 预优化 β-甘氨酸候选结构后，发现能量排序和 PBE-D3 精修后的排序差别很大。你会先检查哪两件事？
:::
