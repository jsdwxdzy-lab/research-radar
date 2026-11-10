```json
{
  "id": "equivariance",
  "title": "对称性与等变性",
  "type": "concept",
  "parent": "ml",
  "research": [
    "crystal-gen",
    "mlip"
  ],
  "keywords": [
    "equivariance",
    "invariance",
    "E(3)",
    "group representation"
  ],
  "purpose": "旋转、平移和置换下的不变性与等变性：为什么原子体系的模型要把对称性写进结构里。",
  "prereq": {
    "intuitive": [
      "旋转矩阵",
      "[[tensors]]：向量和张量在旋转下怎样变换"
    ],
    "full": [
      "群与群表示",
      "球谐函数与角动量耦合"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "batzner-2022-nequip",
    "batatia-2022-design",
    "bartok-2013-soap"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：不变与等变的定义、E(3) 与置换对称、力由能量求导自动等变、不可约表示与球谐、张量积耦合、输出张量性质、常见坑；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

把一个分子整体转一个角度，它的能量不变，但每个原子上的力也跟着转了同样的角度。前者叫**不变** (invariant)，后者叫**等变** (equivariant)：输入怎么变，输出就按确定的规则跟着变。

原子体系的物理量有三类对称性：

- **平移**：整体平移不改变任何物理量。
- **旋转与反演**（合起来是 O(3)，加上平移是 E(3)）：标量不变，向量、张量按各自的规则变换。
- **置换**：交换两个同种原子，能量不变。

模型可以通过数据增强“学会”这些对称性，但只能近似满足。更好的办法是把对称性写进模型结构，让它**精确**满足。这样模型不用浪费数据去学对称性，数据效率更高 [@batzner-2022-nequip]。

![左：一个三原子分子，蓝色箭头是各原子上的力。右：整体旋转 R 后，能量不变，每个力向量也旋转了 R（示意）。](figs/equivariance-rotation.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $R$ | 旋转矩阵 | 中间的弯箭头 |
| $E$ | 总能，标量 | 左右两侧相同 |
| $\mathbf{F}_k$ | 原子 $k$ 上的力，向量 | 蓝色箭头 |
| $R\,\mathbf{F}_k$ | 旋转后的力 | 右图蓝色箭头 |

## 定义与公式 {math}

::: definition 不变与等变
设群 $G$ 作用在输入 $x$ 上，记为 $g\cdot x$。函数 $f$ 称为等变的，如果

$$f(g\cdot x) = \rho(g)\,f(x), \qquad \forall g \in G$$

其中 $\rho(g)$ 是 $g$ 在输出空间上的表示（一个矩阵）。$\rho(g)$ 恒为单位矩阵时，$f$ 是不变的。
:::

对原子坐标 $\{\mathbf{r}_k\}$ 做旋转 $R$ 和平移 $\mathbf{t}$：

$$E\bigl(\{R\mathbf{r}_k + \mathbf{t}\}\bigr) = E\bigl(\{\mathbf{r}_k\}\bigr), \qquad \mathbf{F}_k\bigl(\{R\mathbf{r}_k + \mathbf{t}\}\bigr) = R\,\mathbf{F}_k\bigl(\{\mathbf{r}_k\}\bigr)$$

其中 $R$ 是 3×3 正交矩阵，$\mathbf{t}$ 是平移向量。

::: theorem 由不变能量求导得到等变的力
如果 $E$ 在旋转和平移下不变，那么 $\mathbf{F}_k = -\partial E/\partial \mathbf{r}_k$ 自动满足上面的等变关系。
:::

证明思路：对 $E(\{R\mathbf{r}_k + \mathbf{t}\}) = E(\{\mathbf{r}_k\})$ 两边对 $\mathbf{r}_k$ 求导，用链式法则得到 $R^{\mathsf{T}}\,\partial E/\partial \mathbf{r}'_k = \partial E/\partial \mathbf{r}_k$，再左乘 $R$。所以只要能量模型是不变的，力就“免费”等变。

### 不可约表示与球谐函数

旋转群的表示可以分解成不可约表示，用整数 $l = 0, 1, 2, \dots$ 标记，维数是 $2l+1$：

- $l=0$：标量（能量）；
- $l=1$：向量（力、偶极矩）；
- $l=2$：对称无迹的二阶张量。

球谐函数 $Y_l^m(\hat{\mathbf{r}})$ 正好按第 $l$ 个不可约表示变换。等变神经网络的特征就是一组按 $l$ 分类的量 $h_{l m}$，旋转时它们按 Wigner 矩阵 $D^{(l)}(R)$ 混合 [@batzner-2022-nequip]。

::: definition 张量积耦合
两个等变特征相乘，用 Clebsch–Gordan 系数分解，可以得到新的等变特征：

$$\bigl(u \otimes v\bigr)_{LM} = \sum_{m_1 m_2} C^{LM}_{l_1 m_1,\,l_2 m_2}\,u_{l_1 m_1}\,v_{l_2 m_2}, \qquad |l_1 - l_2| \le L \le l_1 + l_2$$

其中 $u, v$ 分别是阶数为 $l_1, l_2$ 的等变特征，$C$ 是 Clebsch–Gordan 系数，$L$ 是输出的阶数，$M$ 是它的分量指标。这是等变网络里唯一允许的“非线性混合”方式之一，也是 MACE 构造多体特征的基础（见 [[mace]]）[@batatia-2022-design]。
:::

### 宇称

O(3) 还包括反演 $\mathbf{r} \to -\mathbf{r}$。力是极向量，反演时变号；压电张量 $d_{ijk}$ 是三阶极张量，在有反演中心的晶体中必须为零（见 [[crystal-symmetry]] 与 [[piezoelectric-tensor]]）。要预测这类量，模型必须正确区分宇称为奇和偶的特征。

::: unverified 待核验
- 现有通用势（如 MACE）的输出头是否支持直接预测三阶张量（压电）以及 Born 电荷这类非对称二阶张量，按各程序文档核对。
:::

## 在本研究线里的样子 {mapping}

- **MLIP**：能量是不变量，力和应力由求导得到，所以等变性在这一层自动满足。等变的中间特征（$l \ge 1$）的作用是让模型更准确地描述角度依赖的多体相互作用（见 [[mace]]）。
- **预测张量性质**：如果想让模型直接输出 Born 有效电荷或介电张量，输出本身就要是等变的二阶张量（见 [[mlip-electrostatics]]）。
- **晶体生成模型**：生成的结构在旋转、平移和原子编号下应该等价，晶胞还要满足周期性；这些对称性也要写进生成模型（见 [[crystal-generative-models]]）。

## 常见坑 {mapping}

- **不变描述符丢失手性**：只用距离和角度的描述符可能无法区分镜像对映体；对手性分子晶体要注意。
- **以为等变就等于晶体对称**：等变性针对的是整个空间的旋转，与晶体自身的点群对称性是两回事；后者决定的是张量的哪些分量为零。
- **数据增强代替等变**：随机旋转训练数据只能近似满足对称性，预测的张量可能有轻微的不对称噪声。

## 检验自己 {mapping}

::: question 解释
不变和等变的区别是什么？分别举一个原子体系中的例子。
:::

::: question 推导
写出“能量在旋转下不变 ⇒ 力等变”的推导，指出哪一步用到了 $R$ 是正交矩阵。
:::

::: question 迁移
两个 $l=1$ 的特征做张量积，可以得到哪些阶 $L$？它们分别对应什么样的物理量？
:::
