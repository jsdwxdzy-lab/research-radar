```json
{
  "id": "phonons",
  "title": "声子与晶格动力学",
  "type": "concept",
  "parent": "solids",
  "keywords": [
    "phonon",
    "lattice dynamics",
    "dynamical matrix",
    "harmonic approximation"
  ],
  "purpose": "谐振近似下的力常数和动力学矩阵，声子色散、声学和光学支，虚频的含义，以及超胞有限位移法。",
  "prereq": {
    "intuitive": [
      "弹簧振子与简正模",
      "[[reciprocal-space]]：波矢在布里渊区中取值"
    ],
    "full": [
      "[[eigenproblems]]",
      "[[hellmann-feynman]]",
      "[[perturbation-theory]]"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "togo-2015-phonopy",
    "baroni-2001-dfpt",
    "martin-2020-electronic"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：谐振近似、力常数、动力学矩阵、双原子链例子、声学求和规则、虚频、LO–TO 劈裂、超胞有限位移法、常见坑；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

原子在平衡位置附近振动。位移小时，能量近似是位移的二次函数，原子之间像是用弹簧连起来，这就是**谐振近似** (harmonic approximation)。

晶体有平移对称性，所以振动的简正模可以用波矢 $\mathbf{q}$ 标记，每个模是一种“所有晶胞以相位 $\mathrm{e}^{i\mathbf{q}\cdot\mathbf{R}}$ 一起振动”的集体运动。量子化后的简正模就是**声子**。

每个 $\mathbf{q}$ 有 $3N$ 个模（$N$ 是每胞原子数）：

- 3 支**声学支**：$\mathbf{q}\to 0$ 时频率趋于 0，对应整体平移；长波极限下就是声波，斜率是声速，与弹性常数相关（见 [[elastic-tensor]]）。
- $3N-3$ 支**光学支**：$\mathbf{q}\to 0$ 时频率不为零，胞内原子相对振动。

**虚频**（$\omega^{2} < 0$）表示能量沿该模方向是下降的，结构不在极小点，而在鞍点上。

![上：一维双原子链（质量 m1、m2，弹簧常数 K，晶格常数 a）。下：色散关系，声学支在 q=0 处为零，光学支在 q=0 处最高；两支之间有频隙。](figs/diatomic-chain-phonons.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $m_1, m_2$ | 两种原子的质量（$m_1 < m_2$） | 蓝色小球、橙色大球 |
| $K$ | 最近邻弹簧常数 | 小球之间的弹簧 |
| $a$ | 晶格常数（一个晶胞含两个原子） | 上图标注的长度 |
| $q$ | 声子波矢，取值 $-\pi/a$ 到 $\pi/a$ | 下图横轴 |
| $\omega$ | 振动角频率 | 下图纵轴 |
| 频隙 | $\sqrt{2K/m_2}$ 到 $\sqrt{2K/m_1}$ 之间没有模 | 下图阴影带 |

## 定义与公式 {math}

::: definition 力常数
$$E = E_0 + \frac{1}{2}\sum_{\kappa\alpha l}\sum_{\kappa'\beta l'}\Phi_{\kappa\alpha,\kappa'\beta}(l,l')\,u_{\kappa\alpha}(l)\,u_{\kappa'\beta}(l') + O(u^{3}), \qquad \Phi_{\kappa\alpha,\kappa'\beta}(l,l') = \frac{\partial^{2}E}{\partial u_{\kappa\alpha}(l)\,\partial u_{\kappa'\beta}(l')}$$

其中 $l$ 标记晶胞，$\kappa$ 标记胞内原子，$\alpha, \beta$ 是笛卡尔方向；$u_{\kappa\alpha}(l)$ 是位移；一阶项在平衡构型下为零。也可以写成 $\Phi = -\partial F_{\kappa\alpha}(l)/\partial u_{\kappa'\beta}(l')$，即“挪一个原子、看其他原子受力”。
:::

::: definition 动力学矩阵与色散
$$D_{\kappa\alpha,\kappa'\beta}(\mathbf{q}) = \frac{1}{\sqrt{M_\kappa M_{\kappa'}}}\sum_{l'}\Phi_{\kappa\alpha,\kappa'\beta}(0,l')\,\mathrm{e}^{\,i\mathbf{q}\cdot\mathbf{R}_{l'}}, \qquad D(\mathbf{q})\,\mathbf{e}_{\mathbf{q}j} = \omega_{\mathbf{q}j}^{2}\,\mathbf{e}_{\mathbf{q}j}$$

其中 $M_\kappa$ 是原子质量；$\mathbf{R}_{l'}$ 是第 $l'$ 个晶胞的平移矢量；$D(\mathbf{q})$ 是 $3N\times 3N$ 厄米矩阵；$j$ 标记声子支；$\omega_{\mathbf{q}j}$ 是频率，$\mathbf{e}_{\mathbf{q}j}$ 是极化矢量（本征矢）[@togo-2015-phonopy]。
:::

::: theorem 声学求和规则
整体平移不改变能量，所以

$$\sum_{l'}\sum_{\kappa'}\Phi_{\kappa\alpha,\kappa'\beta}(0,l') = 0$$

由此 $\mathbf{q}=0$ 处有 3 个零频模。数值计算会轻微破坏这一规则，后处理通常会强制施加。
:::

### 双原子链

对图中的模型，

$$\omega_\pm^{2}(q) = K\left(\frac{1}{m_1}+\frac{1}{m_2}\right) \pm K\sqrt{\left(\frac{1}{m_1}+\frac{1}{m_2}\right)^{2} - \frac{4\sin^{2}(qa/2)}{m_1 m_2}}$$

其中“−”是声学支，“+”是光学支。在 $q=\pi/a$ 处两支分别为 $\sqrt{2K/m_2}$ 和 $\sqrt{2K/m_1}$，两者之间就是频隙。

### LO–TO 劈裂

在离子晶体（极性晶体）中，长波纵光学模 (LO) 伴随宏观电场，频率高于横光学模 (TO)。这一非解析项由 Born 有效电荷和电子介电张量决定，所以算极性晶体的 Γ 点附近声子时需要 $Z^{*}$ 和 $\varepsilon^{\infty}$（见 [[dielectric-born]]）[@baroni-2001-dfpt]。

### 两种计算方法

- **超胞有限位移法**：在超胞中把一个原子挪一点，用 [[hellmann-feynman]] 力得到力常数；超胞越大，能准确得到的 q 点越多。phonopy 是常用实现 [@togo-2015-phonopy]。
- **DFPT**：直接对任意 $\mathbf{q}$ 求二阶导数，不需要超胞（见 [[perturbation-theory]]）[@baroni-2001-dfpt]。

## 在本研究线里的样子 {mapping}

- **压电的离子贡献**：钳位离子压电张量加上离子弛豫贡献才是完整的 $e_{ij}$。离子贡献要用 Γ 点力常数（也就是 Γ 点光学模）和 Born 电荷、内应变，软的光学模贡献大（见 [[piezoelectric-tensor]]）。
- **稳定性检查**：优化后的 β-甘氨酸结构若在 Γ 点出现明显虚频，说明不在极小点，压电结果不可靠。常见原因是优化不够充分或力收敛太松。
- **自由能与温度**：声子态密度给出零点能和振动自由能，用于多晶型排序和准简谐近似（见 [[free-energy]] 与 [[quasi-harmonic]]）。
- **MLIP 验证**：用 MACE 算声子并与 DFT 比较，是检查势函数二阶导数是否可靠的常用方式（见 [[mace]]）。

::: unverified 待核验
- 分子晶体中低频的分子间模（平动、转动）与高频的分子内模（如 N–H、O–H 伸缩）频率分离明显，这是领域常识，但具体频率范围要以 β-甘氨酸的文献或计算结果为准。
:::

## 常见坑 {mapping}

- **小虚频就当成不稳定**：Γ 点附近的极小虚频可能来自数值噪声（求和规则破坏、FFT 网格、超胞太小），先提高精度再下结论。
- **位移步长不合适**：太小会被 SCF 噪声淹没，太大会混入非谐效应；常用默认约 0.01 Å，按需检查。
- **极性晶体不加非解析修正**：Γ 点附近的 LO 支会错。
- **超胞太小**：长程力常数被截断，色散曲线在布里渊区内部失真。

## 检验自己 {mapping}

::: question 解释
为什么每个 $\mathbf{q}$ 有 $3N$ 个模，而 $\mathbf{q}=0$ 时恰好有 3 个零频模？
:::

::: question 推导
在双原子链公式中取 $q \to 0$，求声学支的斜率（声速），说明它只依赖于 $K$、$a$ 和总质量。
:::

::: question 迁移
你算 β-甘氨酸 Γ 点声子时得到一个约 20i cm⁻¹ 的虚频。你会怎样判断它是数值噪声还是真实的结构不稳定？
:::
