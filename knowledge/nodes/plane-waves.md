```json
{
  "id": "plane-waves",
  "title": "平面波基组与截断能",
  "type": "concept",
  "parent": "electronic-structure",
  "keywords": [
    "plane wave basis",
    "cutoff energy",
    "ENCUT",
    "Pulay stress"
  ],
  "purpose": "周期体系为什么用平面波，截断能怎样控制基组完备性，Pulay 应力从哪里来。",
  "prereq": {
    "intuitive": [
      "[[fourier-analysis]]：周期函数可以写成傅里叶级数"
    ],
    "full": [
      "[[reciprocal-space]]",
      "[[kohn-sham-dft]]"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "payne-1992-iterative",
    "kresse-1996-vasp",
    "vasp-wiki-encut",
    "vasp-wiki-pulay"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：Bloch 函数的平面波展开、截断能与基组大小、Pulay 应力与恒基组数、FFT 网格、常见坑；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

晶体是周期的。Bloch 定理说，周期势中的电子波函数可以写成“平面波 × 周期函数”。周期函数又可以展开成傅里叶级数，每一项是一个以倒格矢 $\mathbf{G}$ 为波矢的平面波。所以平面波是周期体系最自然的基组。

它有几个好处：

- 基组只由一个数控制：截断能 $E_{\mathrm{cut}}$。提高它，结果系统地趋于完备极限。
- 基函数不依赖原子位置，原子移动时基组不变，力的计算没有 Pulay 项（见 [[hellmann-feynman]]）。
- 可以用快速傅里叶变换 (FFT) 在实空间和倒空间之间切换。

代价是：描述核附近的尖锐结构需要很多平面波，所以要配合赝势或 PAW（见 [[paw]]）。另外，真空区域也要付出同样的平面波代价。

![倒空间中的倒格矢网格（二维示意）：动能低于截断能的倒格矢构成一个球（二维中是圆），只有球内的平面波进入基组。](figs/planewave-sphere.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $\mathbf{b}_1, \mathbf{b}_2$ | 倒格子基矢 | 原点处的黑色箭头 |
| $\mathbf{G}$ | 倒格矢，每个点对应一个平面波 | 网格点 |
| $G_{\max}$ | 截断球半径，由 $E_{\mathrm{cut}}$ 决定 | 橙色圆与箭头 |
| 蓝点 | 进入基组的平面波 | 圆内的点 |
| 灰点 | 被截掉的平面波 | 圆外的点 |

## 定义与公式 {math}

::: definition 平面波展开与截断
$$\psi_{n\mathbf{k}}(\mathbf{r}) = \frac{1}{\sqrt{\Omega}}\sum_{\mathbf{G}} c_{n\mathbf{k}}(\mathbf{G})\,\mathrm{e}^{\,i(\mathbf{k}+\mathbf{G})\cdot\mathbf{r}}, \qquad \frac{\hbar^{2}}{2m_e}\,|\mathbf{k}+\mathbf{G}|^{2} < E_{\mathrm{cut}}$$

其中 $n$ 是能带指标；$\mathbf{k}$ 是布里渊区中的波矢；求和遍历倒格矢 $\mathbf{G}$；$c_{n\mathbf{k}}(\mathbf{G})$ 是展开系数，也就是计算中真正求解的未知量；$\Omega$ 是晶胞体积；$m_e$ 是电子质量；$E_{\mathrm{cut}}$ 是截断能（VASP 中的 `ENCUT`）[@payne-1992-iterative]。
:::

截断球内的平面波个数大约是

$$N_{\mathrm{PW}} \approx \frac{\Omega}{6\pi^{2}}\left(\frac{2m_e E_{\mathrm{cut}}}{\hbar^{2}}\right)^{3/2}$$

其中右边是半径 $G_{\max}$ 的球体积除以每个倒格点占的体积 $(2\pi)^{3}/\Omega$。所以基组大小与晶胞体积成正比、与 $E_{\mathrm{cut}}^{3/2}$ 成正比。

### Pulay 应力

变胞时晶胞形状改变，倒格矢 $\mathbf{G}$ 跟着变。如果保持 $E_{\mathrm{cut}}$ 不变，截断球内的平面波**个数**会随体积变化，基组不再是同一个。这样算出的能量–体积曲线带有基组不完备的系统误差，表现为偏负（压缩方向）的虚假应力，称为 Pulay 应力 [@vasp-wiki-pulay]。

::: theorem Pulay 应力随截断能消失
基组趋于完备时，基组本身变化引起的误差趋于零，所以 Pulay 应力随 $E_{\mathrm{cut}}$ 增大而减小。实际做法：提高截断能，或在变胞优化后用新晶胞重新做一次优化（让基组重新对应新晶胞）[@vasp-wiki-pulay]。
:::

### FFT 网格

密度 $n = \sum|\psi|^{2}$ 含有最高 $2G_{\max}$ 的傅里叶分量，所以实空间 FFT 网格需要能表示 $2G_{\max}$；网格不够会产生混叠误差（wrap-around error）。VASP 根据 `ENCUT` 和 `PREC` 自动选择网格 [@kresse-1996-vasp]。

::: unverified 待核验
- VASP 中 `PREC` 不同取值对应的 FFT 网格因子，按文档核对后补上。
:::

## 在本研究线里的样子 {mapping}

- **ENCUT 的选择**：至少取 POTCAR 中最大的 `ENMAX`；变胞优化和弹性、压电计算再提高，并对目标量做收敛（见 [[convergence-testing]]）。
- **分子晶体的代价**：晶胞较大（β-甘氨酸每胞 20 个原子左右，具体以 CIF 为准），$N_{\mathrm{PW}}$ 随体积线性增长；分子间空隙也要付出平面波代价。
- **固定 ENCUT 做能量–体积扫描**：用于状态方程或准简谐计算时（见 [[quasi-harmonic]]），注意 Pulay 应力造成的偏差。

## 常见坑 {mapping}

- **变胞优化只做一次**：基组对应的是初始晶胞，最后要用优化后的晶胞重新开始优化，直到晶胞不再明显变化。
- **不同 ENCUT 的能量直接比较**：只有同一 ENCUT 下的能量差才有意义。
- **只看总能收敛**：应力对 ENCUT 的收敛慢得多。

## 检验自己 {mapping}

::: question 解释
为什么平面波基组算力时没有 Pulay 项，算应力时却有？
:::

::: question 推导
把 $E_{\mathrm{cut}}$ 从 400 eV 提高到 600 eV，平面波数大约变为原来的几倍？
:::

::: question 迁移
你在同一个 ENCUT 下比较两个多晶型的能量，它们的晶胞体积相差 10%。基组不完备误差会怎样影响排序？
:::
