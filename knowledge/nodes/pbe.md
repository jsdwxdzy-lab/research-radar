```json
{
  "id": "pbe",
  "title": "PBE 泛函与广义梯度近似",
  "type": "concept",
  "parent": "xc-functionals",
  "keywords": [
    "PBE",
    "Perdew-Burke-Ernzerhof",
    "generalized gradient approximation"
  ],
  "purpose": "PBE 交换增强因子的形式、参数从哪里来、典型误差倾向，以及为什么分子晶体要加色散修正。",
  "prereq": {
    "intuitive": [
      "[[kohn-sham-dft]]：交换关联能是唯一的近似",
      "均匀电子气"
    ],
    "full": [
      "[[xc-functionals]]",
      "[[dispersion-corrections]]"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "pbe-1996",
    "pbesol-2008",
    "burke-2012-perspective"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：LDA 到 GGA、约化梯度、PBE 交换增强因子与参数、PBEsol、误差倾向、缺少色散；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

最简单的交换关联近似是局域密度近似 (LDA)：每一点的交换关联能密度取“同样密度的均匀电子气”的值。真实体系的密度不均匀，所以广义梯度近似 (GGA) 再加入密度梯度的信息。

PBE 是最常用的 GGA。它的设计思路是：**不拟合实验数据**，而是让泛函满足一组已知的精确条件（均匀电子气极限、慢变密度的线性响应、Lieb–Oxford 下界等），参数由这些条件确定 [@pbe-1996]。

在交换部分，PBE 写成“LDA 交换 × 增强因子 $F_x(s)$”。$s$ 是约化梯度，衡量密度在局部变化得有多快。

![交换增强因子随约化梯度的变化：LDA 恒为 1；PBE 在小 s 处按 μs² 增长，大 s 处趋于 1+κ；PBEsol 的 μ 更小，增长更慢。](figs/pbe-enhancement.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $s$ | 约化密度梯度 | 横轴 |
| $F_x$ | 交换增强因子 | 纵轴 |
| LDA | $F_x = 1$ | 灰色水平线 |
| $\kappa$ | 大梯度极限 $F_x \to 1+\kappa$ 的参数 | 上方虚线 1.804 |
| $\mu$ | 小梯度时 $F_x \approx 1 + \mu s^{2}$ 的系数 | 蓝线（PBE）与橙线（PBEsol）起始弯曲程度的差别 |

## 定义与公式 {math}

::: definition 约化梯度与 PBE 交换
$$s = \frac{|\nabla n|}{2\,k_F\,n}, \quad k_F = (3\pi^{2} n)^{1/3}, \qquad E_x^{\mathrm{PBE}} = \int n(\mathbf{r})\,\varepsilon_x^{\mathrm{unif}}(n)\,F_x(s)\,\mathrm{d}\mathbf{r}$$

$$F_x(s) = 1 + \kappa - \frac{\kappa}{1 + \mu s^{2}/\kappa}, \qquad \kappa = 0.804, \quad \mu \approx 0.21951$$

其中 $n$ 是电子密度；$k_F$ 是同密度均匀电子气的费米波矢；$\varepsilon_x^{\mathrm{unif}}(n)$ 是均匀电子气的单电子交换能；$\kappa$ 由 Lieb–Oxford 下界的局域形式确定；$\mu$ 由关联部分的梯度展开条件确定 [@pbe-1996]。
:::

关联部分写成 LDA 关联加一个梯度修正项 $H$，同样由精确条件确定，这里不展开 [@pbe-1996]。

::: definition PBEsol
保持 PBE 的函数形式，把 $\mu$ 改为慢变密度极限下交换的梯度展开系数 $10/81 \approx 0.123$，并相应调整关联参数，目标是改善固体的平衡晶格常数和表面能 [@pbesol-2008]。
:::

::: approximation 半局域性
PBE 在每一点只用该点的密度和梯度，因此称为半局域 (semilocal) 泛函。它无法描述长程的电子关联，也就是色散（范德华）作用；也带有自相互作用误差 [@burke-2012-perspective]。
:::

::: unverified 待核验
- 常见说法：PBE 对固体晶格常数偏大约 1%、带隙明显偏低；具体幅度随体系而变，引用具体基准后再写数字。
- 在分子晶体中，纯 PBE 由于缺少色散，通常给出偏大的晶胞体积甚至不稳定的堆积。
:::

## 在本研究线里的样子 {mapping}

- **PBE-D3**：β-甘氨酸是氢键加范德华堆积的分子晶体，纯 PBE 的层间结合不足。研究线里用 PBE 加 D3 色散修正（见 [[dispersion-corrections]]），结构和弹性才合理。
- **压电系数对晶胞敏感**：泛函和色散决定平衡晶胞，晶胞又影响 $d_{ij}$。比较实验时要分清“在实验晶胞上算”还是“在优化晶胞上算”（见 [[piezoelectric-tensor]]）。
- **VASP 设置**：`GGA = PE` 选 PBE，`GGA = PS` 选 PBEsol；POTCAR 是用 PBE 生成的。
- **带隙不必当真**：压电与介电只需要绝缘的基态，PBE 低估的带隙一般不影响定性结论，但会影响电子介电常数的大小。

## 常见坑 {mapping}

- **D3 参数和泛函不配套**：D3 的阻尼参数是针对每个泛函拟合的，换泛函必须换参数。
- **用 PBEsol 加 D3 而不检查参数是否存在**：并非每种泛函和阻尼形式组合都有现成参数。
- **把 PBE 的“不拟合实验”理解成“没有误差”**：满足精确条件不等于对每种性质都准。

## 检验自己 {mapping}

::: question 解释
为什么 $\kappa$ 控制大 $s$ 的行为、$\mu$ 控制小 $s$ 的行为？从 $F_x(s)$ 的两个极限说明。
:::

::: question 推导
把 $F_x(s)$ 在 $s=0$ 附近展开到 $s^{2}$ 项，验证系数是 $\mu$。
:::

::: question 迁移
你用 PBE-D3 优化的 β-甘氨酸晶胞比实验小 2%，然后算 $d_{16}$。你会怎样判断差异来自泛函、色散还是温度？
:::
