```json
{
  "id": "kohn-sham-dft",
  "title": "Kohn–Sham 密度泛函理论",
  "type": "concept",
  "parent": "electronic-structure",
  "keywords": [
    "density functional theory",
    "Kohn-Sham",
    "Hohenberg-Kohn"
  ],
  "purpose": "Hohenberg–Kohn 定理和 Kohn–Sham 映射：把相互作用电子问题换成无相互作用体系加交换关联能。",
  "prereq": {
    "intuitive": [
      "[[born-oppenheimer]]：固定原子核后的电子问题",
      "单粒子薛定谔方程"
    ],
    "full": [
      "[[variational-principle]] 与 [[variational-calculus]]",
      "[[hartree-fock]]"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "hohenberg-1964-hk",
    "kohn-1965-ks",
    "burke-2012-perspective",
    "martin-2020-electronic"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：HK 定理、KS 映射与方程、能量分解、什么是精确的什么是近似、本征值的含义；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

固定原子核后，$N$ 个电子的波函数依赖 $3N$ 个坐标，直接求解随电子数指数增长地变难。密度泛函理论换了一个基本变量：只用三维空间里的**电子密度** $n(\mathbf{r})$。

它分两步：

1. **Hohenberg–Kohn (HK) 定理**说明这样做原则上不丢信息：基态密度唯一决定外势（差一个常数），因而决定一切基态性质 [@hohenberg-1964-hk]。
2. **Kohn–Sham (KS) 映射**给出可计算的做法：构造一个**无相互作用**的辅助电子体系，让它的基态密度与真实体系相同。无相互作用体系可以用单粒子轨道精确求解，所有“难的部分”集中到一项交换关联能 $E_{\mathrm{xc}}[n]$ 里 [@kohn-1965-ks]。

所以 KS-DFT 本身是精确的框架，近似只来自 $E_{\mathrm{xc}}$ 的具体形式（LDA、PBE、杂化泛函等，见 [[xc-functionals]]）。

![左：真实体系中相互作用电子在外势里形成密度 n。右：Kohn–Sham 体系中无相互作用电子在有效势里形成同一个密度。两张图的势和密度都是示意。](figs/kohn-sham-mapping.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $v_{\mathrm{ext}}$ | 外势：原子核（或赝势）对电子的作用 | 左图蓝线 |
| $v_s$ | Kohn–Sham 有效势 | 右图橙线 |
| $n(\mathbf{r})$ | 电子密度，两边相同 | 两图下方绿色曲线 |
| $v_{\mathrm{H}}$、$v_{\mathrm{xc}}$ | Hartree 势、交换关联势 | 右图上方公式 |

## 定义与公式 {math}

::: theorem Hohenberg–Kohn 定理
1. 对非简并基态，外势 $v_{\mathrm{ext}}(\mathbf{r})$（差一个常数）由基态密度 $n_0(\mathbf{r})$ 唯一决定。
2. 存在密度的能量泛函 $E_v[n]$，它在真实基态密度处取最小值，最小值就是基态能量 [@hohenberg-1964-hk]。
:::

::: definition Kohn–Sham 能量分解
$$E[n] = T_s[n] + \int v_{\mathrm{ext}}(\mathbf{r})\,n(\mathbf{r})\,\mathrm{d}\mathbf{r} + \frac{1}{2}\iint \frac{n(\mathbf{r})\,n(\mathbf{r}')}{|\mathbf{r}-\mathbf{r}'|}\,\mathrm{d}\mathbf{r}\,\mathrm{d}\mathbf{r}' + E_{\mathrm{xc}}[n]$$

其中 $T_s[n]$ 是同密度无相互作用电子的动能；第二项是电子与外势的作用；第三项是 Hartree 能（密度自身的经典静电排斥，原子单位）；$E_{\mathrm{xc}}[n]$ 是交换关联能，按定义收集其余一切：真实动能与 $T_s$ 之差，以及电子相互作用中超出经典静电的部分 [@kohn-1965-ks]。
:::

对轨道变分并保持正交归一，得到 Kohn–Sham 方程：

$$\Bigl[-\tfrac{1}{2}\nabla^{2} + v_s(\mathbf{r})\Bigr]\psi_i(\mathbf{r}) = \varepsilon_i\,\psi_i(\mathbf{r}), \qquad n(\mathbf{r}) = \sum_i f_i\,|\psi_i(\mathbf{r})|^{2}$$

$$v_s(\mathbf{r}) = v_{\mathrm{ext}}(\mathbf{r}) + \int \frac{n(\mathbf{r}')}{|\mathbf{r}-\mathbf{r}'|}\,\mathrm{d}\mathbf{r}' + \frac{\delta E_{\mathrm{xc}}[n]}{\delta n(\mathbf{r})}$$

其中 $\psi_i$、$\varepsilon_i$ 是 KS 轨道和本征值；$f_i$ 是占据数；$v_s$ 依赖 $n$，而 $n$ 又由 $\psi_i$ 构成，所以方程必须自洽求解（见 [[scf-cycle]]）。

::: approximation 唯一的近似在 $E_{\mathrm{xc}}$
若 $E_{\mathrm{xc}}[n]$ 精确已知，KS 方程给出精确的基态密度和能量。实际计算中它只能近似。对分子晶体最突出的缺陷是半局域近似缺少长程色散（见 [[dispersion-corrections]]）。
:::

::: assumption 这个框架说的是基态
HK 与 KS 都是关于基态的。KS 本征值 $\varepsilon_i$ 和轨道是辅助量：除最高占据态本征值与电离能的关系（对精确泛函成立）之外，一般不能直接当作准粒子能量，所以 KS 带隙通常不等于真实带隙 [@burke-2012-perspective]。
:::

## 在本研究线里的样子 {mapping}

- **VASP 计算的就是 KS 方程**：用平面波展开轨道（[[plane-waves]]），用 PAW 处理核附近（[[paw]]），用 k 点对布里渊区求和（[[reciprocal-space]]），交换关联取 PBE（[[pbe]]）再加 D3 色散。
- **响应量都是 KS 能量的导数**：力、应力是一阶导数（[[hellmann-feynman]]），介电、玻恩电荷、压电是二阶导数（[[perturbation-theory]]、[[energy-structure-response]]）。泛函的近似通过能量曲面传给这些量。
- **带隙**：PBE 低估分子晶体的带隙，这会影响电子介电常数 $\varepsilon^{\infty}$（见 [[dielectric-born]]）。

## 常见坑 {mapping}

- **把 KS 带隙当实验带隙**。
- **说“DFT 不准”而不说哪一个泛函**：不准的是 $E_{\mathrm{xc}}$ 的近似，不同泛函误差不同。
- **把 KS 轨道当作物理波函数**：KS 轨道只保证密度正确；它们常被用来做定性分析，但这是额外的解释，不是定理。

## 检验自己 {mapping}

::: question 解释
KS 体系的电子没有相互作用，为什么它能给出相互作用体系的密度？代价放在了哪里？
:::

::: question 推导
从能量分解出发，对 $\psi_i^{*}$ 变分（带拉格朗日乘子保证归一），推出 KS 方程中的 $v_s$。
:::

::: question 迁移
如果换一个泛函后晶格参数几乎不变，压电系数却变了很多，按 [[energy-structure-response]] 的观点，最可能是能量曲面的哪一部分变了？
:::
