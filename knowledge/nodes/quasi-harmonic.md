```json
{
  "id": "quasi-harmonic",
  "title": "准简谐近似与热膨胀",
  "type": "method",
  "parent": "free-energy",
  "research": [
    "csp"
  ],
  "keywords": [
    "quasi-harmonic approximation",
    "thermal expansion",
    "vibrational free energy"
  ],
  "purpose": "让声子频率随体积变化，从而得到热膨胀和有限温度结构；以及这种近似在哪里失效。",
  "prereq": {
    "intuitive": [
      "[[free-energy]]：谐振振动自由能",
      "状态方程 E(V)"
    ],
    "full": [
      "[[phonons]]",
      "[[elastic-tensor]]"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "baroni-2010-qha",
    "togo-2015-phonopy",
    "mounet-2005-qha"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：F(V,T) 与最小化、Grüneisen 参数、热膨胀系数、零点膨胀、各向异性晶胞、适用范围与失效、常见坑；配图 1 张（真实计算模型状态方程）"
    }
  ]
}
```
## 直觉 {intuition}

严格的谐振近似里，振动频率与体积无关，晶体不会热膨胀。真实晶体受热会膨胀，原因是势能的非谐性：体积变大，原子间的“弹簧”变软，频率降低，振动熵增加，自由能下降。

**准简谐近似** (quasi-harmonic approximation, QHA) 用一个简单的办法把这一点包含进来：在**每一个体积**上做谐振声子计算，让频率依赖于体积；然后在每个温度下，找出使自由能最小的体积。

于是：

- 0 K 时，零点能也随体积变化，所以平衡体积已经比静态能量最低的体积略大（零点膨胀）。
- 温度升高，热振动的贡献增大，平衡体积继续变大。

![用模型状态方程和 Grüneisen 关系真实计算（约化单位）：E(V) 取二次型，四个频率按 ω∝V^(−γ) 变化，γ=2。左：不同温度下的 F(V,T)，圆点是极小（曲线竖直错开以便比较）。右：平衡体积随温度增大；T=0 时已经大于静态平衡体积 V₀（零点膨胀）。](figs/quasi-harmonic-volume.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $V$ | 晶胞体积 | 左图横轴 |
| $F(V,T)$ | 某温度下的自由能 | 左图各条曲线 |
| $V^{*}(T)$ | 该温度下的平衡体积 | 左图圆点；右图黑线 |
| $V_0$ | 只看静态能量时的平衡体积 | 右图灰色点线 |

## 定义与公式 {math}

::: definition 准简谐自由能
$$F(V,T) = E_{\mathrm{static}}(V) + \sum_{\mathbf{q}j}\left[\frac{\hbar\omega_{\mathbf{q}j}(V)}{2} + k_B T\ln\!\left(1 - \mathrm{e}^{-\hbar\omega_{\mathbf{q}j}(V)/k_B T}\right)\right]$$

$$V^{*}(T) = \arg\min_{V} F(V,T), \qquad G(p,T) = \min_{V}\bigl[F(V,T) + pV\bigr]$$

其中 $E_{\mathrm{static}}(V)$ 是在体积 $V$ 下（内部坐标优化后）的静态能量；$\omega_{\mathbf{q}j}(V)$ 是该体积下的声子频率；其余符号同 [[free-energy]] [@baroni-2010-qha]。
:::

实际做法：取几个到十几个体积，每个体积优化内部坐标、算声子，再对 $E_{\mathrm{static}}(V)$ 拟合状态方程，对频率或自由能插值，最后对每个温度求极小。phonopy 提供了这一流程的实现 [@togo-2015-phonopy]。

::: definition Grüneisen 参数与热膨胀
$$\gamma_{\mathbf{q}j} = -\frac{\partial\ln\omega_{\mathbf{q}j}}{\partial\ln V}, \qquad \alpha_V = \frac{1}{V}\left(\frac{\partial V}{\partial T}\right)_{p} \approx \frac{1}{B_T V}\sum_{\mathbf{q}j}\gamma_{\mathbf{q}j}\,c_{V,\mathbf{q}j}$$

其中 $\gamma_{\mathbf{q}j}$ 是模式 Grüneisen 参数，描述频率对体积的敏感程度；$\alpha_V$ 是体膨胀系数；$B_T$ 是等温体模量；$c_{V,\mathbf{q}j}$ 是该模式对定容热容的贡献。$\gamma > 0$ 的模式在膨胀时变软，推动热膨胀 [@baroni-2010-qha]。
:::

### 各向异性晶胞

单斜、正交等低对称晶体在不同方向上的膨胀不同。只沿体积做 QHA 会把晶胞形状固定。更完整的做法是对多个晶格参数做网格或用应力驱动，代价成倍增加 [@mounet-2005-qha]。

::: approximation 准简谐近似的适用范围
- 假设在每个体积上振动仍是谐振的，只是频率随体积变。
- 忽略了同一体积下的显式非谐效应（声子–声子相互作用）。接近熔点、存在大振幅运动（分子转动、低垒的构象变化）或软模式时，QHA 会失效，需要分子动力学（见 [[molecular-dynamics]]）。
- 膨胀过程中若出现虚频，说明该体积下结构不稳定，QHA 结果不可用。
:::

## 在本研究线里的样子 {mapping}

- **分子晶体热膨胀大**：分子间的弱相互作用非谐性强，室温晶胞与 0 K DFT 晶胞可能有明显差别。与实验晶胞比较之前，应考虑零点膨胀和热膨胀。
- **对压电的影响**：$d_{16}$ 依赖晶胞和弹性常数（见 [[piezoelectric-tensor]]）。一种做法是用 QHA 得到 300 K 晶胞，再在这个晶胞上算压电响应，与 0 K 结果比较。
- **CSP 排序**：QHA 的 $G(T)$ 比固定体积的谐振自由能更接近实验条件，但每个候选结构要算多组声子，常用 MLIP 降低代价（见 [[mace]]）。
- **色散修正是关键**：$E_{\mathrm{static}}(V)$ 的形状由色散决定，没有色散的 PBE 会给出错误的体积依赖（见 [[dispersion-corrections]]）。

## 常见坑 {mapping}

- **体积范围太窄或太宽**：太窄插值不准，太宽会进入非谐或不稳定区域。
- **各体积的计算设置不一致**：例如 k 点、截断能不同，会在 $E(V)$ 上叠加锯齿噪声。截断能还会通过 Pulay 应力影响 $E(V)$（见 [[plane-waves]]）。
- **只做各向同性 QHA**：对低对称分子晶体，晶胞形状的变化可能比体积变化更重要。
- **把 QHA 结果当成高温真值**：接近熔点或有分子转动时要用 MD 交叉检查。

## 检验自己 {mapping}

::: question 解释
为什么严格的谐振近似给不出热膨胀？QHA 用什么办法把它补回来？
:::

::: question 推导
设 $E_{\mathrm{static}} = \tfrac{1}{2}B(V-V_0)^{2}/V_0$，只有一个频率 $\omega(V) = \omega_0 (V/V_0)^{-\gamma}$。只保留零点能，求平衡体积相对 $V_0$ 的一阶偏移。
:::

::: question 迁移
你算出的 β-甘氨酸 300 K QHA 晶胞比实验大 2%，而 0 K 优化晶胞比实验小 1%。你会怎样判断问题出在 QHA、色散修正还是泛函？
:::
