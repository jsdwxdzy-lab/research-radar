```json
{
  "id": "reciprocal-space",
  "title": "倒空间、布里渊区与 k 点采样",
  "type": "concept",
  "parent": "solids",
  "keywords": [
    "reciprocal lattice",
    "Brillouin zone",
    "k-point sampling",
    "Monkhorst-Pack"
  ],
  "purpose": "倒格子和布里渊区的定义，为什么周期计算要在布里渊区内积分，Monkhorst–Pack 网格怎样选。",
  "prereq": {
    "intuitive": [
      "[[fourier-analysis]]：周期函数的傅里叶级数",
      "晶格基矢与晶胞"
    ],
    "full": [
      "[[crystal-symmetry]]",
      "Bloch 定理"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "monkhorst-1976-kpoints",
    "vasp-wiki-kpoints",
    "martin-2020-electronic"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：倒格子定义、布里渊区、Bloch 定理与 k 积分、Monkhorst–Pack 网格、k 点密度与晶胞大小、常见坑；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

实空间晶格描述“原子怎样重复”；倒格子描述“哪些平面波和这种重复相容”。凡是有晶格周期性的函数（势、密度），它的傅里叶分量只出现在倒格矢 $\mathbf{G}$ 上。

Bloch 定理说电子态可以用一个波矢 $\mathbf{k}$ 标记，而 $\mathbf{k}$ 和 $\mathbf{k}+\mathbf{G}$ 描述同一个态。所以只需考虑一个倒空间的原胞，最常用的取法是**第一布里渊区** (Brillouin zone, BZ)：离原点比离任何其他倒格点都近的区域。

总能、密度这类量都要对 BZ 中所有占据态求平均，也就是在 BZ 上做积分。计算里用有限个 k 点代替积分，这就是 **k 点采样**。

关键的反比关系：实空间晶胞越大，倒格子越小，BZ 越小，同样精度需要的 k 点越少。

![左：二维斜格子的实空间基矢。右：对应的倒格子、第一布里渊区（橙色区域）和一个 4×4 Monkhorst–Pack 网格。偶数网格不包含 Γ 点。](figs/reciprocal-bz-kmesh.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $\mathbf{a}_1, \mathbf{a}_2$ | 实空间晶格基矢 | 左图黑色箭头 |
| $\mathbf{b}_1, \mathbf{b}_2$ | 倒格子基矢 | 右图黑色箭头 |
| BZ | 第一布里渊区 | 右图橙色多边形 |
| Γ | 倒空间原点 $\mathbf{k}=0$ | 右图标注的中心点 |
| $\mathbf{k}$ 网格 | Monkhorst–Pack 采样点 | 右图蓝点 |

## 定义与公式 {math}

::: definition 倒格子
$$\mathbf{a}_i\cdot\mathbf{b}_j = 2\pi\,\delta_{ij}, \qquad \mathbf{b}_1 = 2\pi\,\frac{\mathbf{a}_2\times\mathbf{a}_3}{\mathbf{a}_1\cdot(\mathbf{a}_2\times\mathbf{a}_3)}$$

其中 $\mathbf{a}_i$ 是实空间基矢，$\mathbf{b}_j$ 是倒格子基矢，$\delta_{ij}$ 是 Kronecker 符号；$\mathbf{b}_2, \mathbf{b}_3$ 由下标轮换得到。倒格矢是 $\mathbf{G} = m_1\mathbf{b}_1 + m_2\mathbf{b}_2 + m_3\mathbf{b}_3$，$m_i$ 为整数。倒格子原胞体积是 $(2\pi)^{3}/\Omega$，$\Omega$ 是实空间晶胞体积。
:::

::: definition Bloch 定理与 BZ 积分
$$\psi_{n\mathbf{k}}(\mathbf{r}+\mathbf{R}) = \mathrm{e}^{\,i\mathbf{k}\cdot\mathbf{R}}\,\psi_{n\mathbf{k}}(\mathbf{r}), \qquad \bar{f} = \frac{\Omega}{(2\pi)^{3}}\int_{\mathrm{BZ}} f(\mathbf{k})\,\mathrm{d}^{3}k \approx \sum_{\mathbf{k}} w_{\mathbf{k}}\,f(\mathbf{k})$$

其中 $\mathbf{R}$ 是任意晶格平移矢量；$n$ 是能带指标；$f(\mathbf{k})$ 是某个依赖 $\mathbf{k}$ 的量（例如占据能带能量之和）；$\bar f$ 是它在 BZ 上的平均；$w_{\mathbf{k}}$ 是 k 点权重，和为 1。
:::

::: definition Monkhorst–Pack 网格
$$\mathbf{k}_{n_1 n_2 n_3} = \sum_{i=1}^{3} u_{n_i}\,\mathbf{b}_i, \qquad u_{n_i} = \frac{2n_i - N_i - 1}{2N_i}, \quad n_i = 1,\dots,N_i$$

其中 $N_i$ 是沿 $\mathbf{b}_i$ 方向的网格数，$u_{n_i}$ 是分数坐标 [@monkhorst-1976-kpoints]。$N_i$ 为奇数时网格包含 Γ 点；为偶数时网格相对 Γ 偏移半格。对称操作把等价的 k 点合并，只算不可约的那些，并相应增加权重。
:::

### k 点密度怎么选

精度由倒空间中的**网格间距**决定，而不是由 $N_i$ 本身决定。因为 $|\mathbf{b}_i| \propto 1/|\mathbf{a}_i|$，一种常见做法是让 $N_i\,|\mathbf{a}_i|$ 大致相等，即沿短轴取更多 k 点 [@vasp-wiki-kpoints]。

绝缘体的能带在 BZ 中平滑，积分收敛快；金属有费米面，占据数在 BZ 中不连续，需要更密的网格和展宽 (smearing)。

## 在本研究线里的样子 {mapping}

- **分子晶体是绝缘体，晶胞较大**：β-甘氨酸这类体系通常不需要很密的 k 网格，但仍要对目标量（总能差、应力、压电系数）做收敛（见 [[convergence-testing]]）。
- **单斜晶胞的三个轴长不同**：按轴长反比分配 $N_i$，不要三个方向取同样的数。
- **六方体系**：通常推荐 Γ 中心网格，因为偏移网格可能破坏六方对称性 [@vasp-wiki-kpoints]。
- **声子与 DFPT**：波矢 $\mathbf{q}$ 同样在 BZ 中取值（见 [[phonons]]）；超胞方法里，超胞越大，对应的 q 网格越密。

## 常见坑 {mapping}

- **换超胞后不缩小 k 网格**：超胞 $2\times2\times2$ 时 BZ 缩小一半，k 网格应相应减半，否则浪费计算。
- **只按 $N_i$ 收敛而不看间距**：不同晶胞之间比较时，应该保持相同的 k 点间距。
- **用偶数网格算需要 Γ 点的量**：例如某些分析需要 Γ 点本征值，偶数 MP 网格里没有 Γ。
- **对称性约化的副作用**：施加应变或电场后对称性降低，不可约 k 点会变多；做有限差分时要保证参考计算与扰动计算用一致的 k 网格。

## 检验自己 {mapping}

::: question 解释
为什么晶胞越大，所需的 k 点越少？用倒格子体积 $(2\pi)^{3}/\Omega$ 说明。
:::

::: question 推导
写出 $N=4$ 时一维 MP 网格的 4 个分数坐标 $u_n$，并说明为什么不含 0。
:::

::: question 迁移
单斜晶胞三个轴长约为 5、12、5.5 Å。如果沿 a 轴取 6 个 k 点，另外两个方向大约取多少比较合理？
:::
