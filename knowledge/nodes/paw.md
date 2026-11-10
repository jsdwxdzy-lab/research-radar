```json
{
  "id": "paw",
  "title": "赝势与 PAW 方法",
  "type": "method",
  "parent": "electronic-structure",
  "keywords": [
    "projector augmented wave",
    "pseudopotential",
    "frozen core"
  ],
  "purpose": "冻结芯近似、赝势与投影缀加波怎样把核附近剧烈振荡的波函数变得可计算。",
  "prereq": {
    "intuitive": [
      "原子的芯电子与价电子",
      "[[plane-waves]]：平面波难以描述尖锐结构"
    ],
    "full": [
      "[[kohn-sham-dft]]",
      "线性算符与投影"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "bloechl-1994-paw",
    "kresse-1999-paw",
    "vanderbilt-1990-ultrasoft",
    "payne-1992-iterative"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：为什么需要、冻结芯、赝势的思路、PAW 线性变换、VASP 中的 POTCAR 选择与常见坑；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

价电子波函数在原子核附近必须和芯电子轨道正交，所以在核附近**剧烈振荡**。用平面波描述这种振荡需要非常高的截断能（见 [[plane-waves]]）。但化学键、结构、响应主要由价电子在**原子之间**的行为决定，核附近的细节影响不大。

两步简化：

1. **冻结芯** (frozen core)：芯电子在不同化学环境中几乎不变，直接取孤立原子的芯电子，不再求解。
2. **处理核附近的价电子**：
   - **赝势** (pseudopotential)：在半径 $r_c$ 以内，把真实的强势换成平缓的赝势，使赝波函数在 $r_c$ 外与真实波函数相同、在 $r_c$ 内平滑。只保留赝波函数。
   - **PAW** (projector augmented wave)：同样用平滑波函数做计算，但保留一个**线性变换**，需要时可以把平滑波函数还原成全电子波函数。所以 PAW 能给出核附近的密度，同时维持低截断能 [@bloechl-1994-paw]。

![全电子波函数在缀加球内剧烈振荡，赝（平滑）波函数在球内平滑，球外两者重合。曲线为示意。](figs/paw-radial.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $r$ | 到原子核的距离 | 横轴 |
| $\psi$ | 全电子（真实）价电子波函数 | 蓝色实线 |
| $\tilde\psi$ | 平滑（赝）波函数，实际用平面波展开的量 | 橙色虚线 |
| $r_c$ | 缀加球（截断）半径 | 灰色竖线与阴影区 |

## 定义与公式 {math}

::: definition PAW 变换
$$|\psi_n\rangle = |\tilde\psi_n\rangle + \sum_{a,i}\Bigl(|\phi^{a}_i\rangle - |\tilde\phi^{a}_i\rangle\Bigr)\,\langle \tilde p^{a}_i \,|\, \tilde\psi_n\rangle$$

其中 $|\psi_n\rangle$ 是全电子波函数，$|\tilde\psi_n\rangle$ 是用平面波展开的平滑波函数；$a$ 标记原子，$i$ 标记该原子的分波通道（角动量和参考能量）；$\phi^{a}_i$ 是孤立原子的全电子分波，$\tilde\phi^{a}_i$ 是对应的平滑分波，两者在 $r_c$ 外相同；$\tilde p^{a}_i$ 是投影函数，满足 $\langle \tilde p^{a}_i|\tilde\phi^{a}_j\rangle = \delta_{ij}$，并且只在缀加球内不为零 [@bloechl-1994-paw]。
:::

括号里的项只在各原子的缀加球内不为零，所以球外 $\psi = \tilde\psi$。球内，投影系数 $\langle \tilde p^{a}_i|\tilde\psi_n\rangle$ 告诉我们平滑波函数含有多少第 $i$ 个分波，然后把平滑分波“换回”全电子分波。

能量、密度等同样拆成“平面波部分 + 每个球内的全电子修正 − 平滑修正”，球内的积分在径向网格上做，不需要平面波。

::: approximation 冻结芯与分波截断
- 芯电子取自孤立原子，不随环境弛豫。
- 球内的分波只取有限几个；若缀加球相互重叠过多，变换不再精确。
- 这两点决定了 PAW 与真正全电子计算之间的差别 [@kresse-1999-paw]。
:::

### 和超软赝势的关系

超软赝势同样放宽了对赝波函数的约束（不要求模守恒），用广义本征值问题处理 [@vanderbilt-1990-ultrasoft]。Kresse 与 Joubert 指出，超软赝势可以看作 PAW 的一种近似形式 [@kresse-1999-paw]。

## 在本研究线里的样子 {mapping}

- **VASP 的 POTCAR 就是 PAW 数据集**：每种元素有几个版本（例如标准版、`_h` 硬版、`_s` 软版、`_sv`/`_pv` 把半芯态当价电子）。选择会影响所需截断能（POTCAR 中的 `ENMAX`）和精度。
- **β-甘氨酸的 C、N、O、H**：常用标准版本。若要算对核附近敏感的量（例如精确的电场梯度），或者需要短键长下的精度，才考虑硬版本。分子晶体中 O–H、N–H 键短，可以把硬版本作为一次检查。
- **压电与介电**：这些量主要由价电子在原子间的分布决定，PAW 的影响一般小于泛函和色散的影响；但换 POTCAR 后应重新做截断能收敛（见 [[convergence-testing]]）。

::: unverified 待核验
- 各 POTCAR 后缀的确切含义与推荐用法按 VASP 文档核对；上面只列出常见的几种。
:::

## 常见坑 {mapping}

- **不同计算混用 POTCAR**：对比能量（例如多晶型排序）时，所有计算必须用同一组 POTCAR 和截断能。
- **截断能低于 `ENMAX`**：多元素体系要取所有元素 `ENMAX` 的最大值，变胞或应力计算还要更高。
- **压缩很大的结构**：缀加球重叠时 PAW 数据集可能失效，需要换更小 $r_c$ 的硬版本。

## 检验自己 {mapping}

::: question 解释
赝势和 PAW 都用平滑波函数计算，PAW 多保留了什么？这在什么时候有用？
:::

::: question 推导
设某原子只有一个分波通道，且 $\tilde\psi = c\,\tilde\phi$（在球内）。用 PAW 变换写出球内的 $\psi$，说明它等于 $c\,\phi$。
:::

::: question 迁移
两次 β-甘氨酸计算只差在 O 用了标准版还是硬版 POTCAR，若 $d_{16}$ 变化明显，你会先检查什么？
:::
