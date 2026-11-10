```json
{
  "id": "molecular-dynamics",
  "title": "分子动力学",
  "type": "method",
  "parent": "statmech",
  "research": [
    "mlip"
  ],
  "keywords": [
    "molecular dynamics",
    "thermostat",
    "barostat",
    "ergodicity"
  ],
  "purpose": "积分牛顿方程、恒温器与恒压器，以及时间平均怎样替代系综平均。",
  "prereq": {
    "intuitive": [
      "牛顿第二定律",
      "[[ensembles]]：系综与温度"
    ],
    "full": [
      "[[hellmann-feynman]]：力从哪里来",
      "[[mlip-basics]]"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "verlet-1967",
    "swope-1982-vv",
    "nose-1984",
    "hoover-1985",
    "bussi-2007-csvr",
    "parrinello-1981-npt"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：速度 Verlet 与能量守恒、时间步长、温度与动能、恒温器（Nosé–Hoover、随机速度重标定）、恒压器、遍历性与统计误差、常见坑；配图 1 张（真实积分一维模型振子）"
    }
  ]
}
```
## 直觉 {intuition}

分子动力学 (molecular dynamics, MD) 就是给定原子上的力，按牛顿方程一步步往前推，得到原子随时间的轨迹。力可以来自经典力场、MLIP（见 [[mlip-basics]]）或 DFT。

两个关键问题：

1. **怎么积分**：时间步长有限，每一步都有误差。好的积分算法在长时间模拟中不会让总能系统地漂移。
2. **怎么得到热力学量**：实验对应的是某个温度、压力下的系综平均（见 [[ensembles]]）。MD 给的是时间平均。如果体系是遍历的 (ergodic)，足够长的时间平均等于系综平均。要模拟恒温或恒压，需要在运动方程里加恒温器 (thermostat) 和恒压器 (barostat)。

![一维非谐振子 V(x)=x²/2+x⁴/10 的真实数值积分（无量纲单位）。左：显式 Euler 即使步长更小，轨迹也向外螺旋，能量持续增长；速度 Verlet 的轨迹闭合。右：Verlet 的能量误差有界、随步长增大而增大；Euler 的误差持续增长。](figs/md-verlet-energy.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $x, v$ | 位置与速度 | 左图坐标轴 |
| $\Delta t$ | 时间步长 | 图例中的数值 |
| $E_0$ | 初始总能 | 右图纵轴的参考值 |
| $(E-E_0)/E_0$ | 相对能量误差 | 右图纵轴 |

## 定义与公式 {math}

::: definition 速度 Verlet
$$\mathbf{r}(t+\Delta t) = \mathbf{r}(t) + \mathbf{v}(t)\,\Delta t + \frac{\mathbf{F}(t)}{2m}\,\Delta t^{2}, \qquad \mathbf{v}(t+\Delta t) = \mathbf{v}(t) + \frac{\mathbf{F}(t) + \mathbf{F}(t+\Delta t)}{2m}\,\Delta t$$

其中 $\mathbf{r}, \mathbf{v}$ 是原子位置和速度；$m$ 是质量；$\mathbf{F}(t)$ 是 $t$ 时刻的力，$\mathbf{F}(t+\Delta t)$ 用新位置算出 [@verlet-1967] [@swope-1982-vv]。
:::

速度 Verlet 是时间可逆的、辛 (symplectic) 的积分器。辛积分器精确守恒一个与真实哈密顿量相差 $O(\Delta t^{2})$ 的“影子哈密顿量”，所以真实能量只在一个有界范围内波动，不会系统漂移（图中蓝、绿、橙曲线）。显式 Euler 不具备这一性质，能量会持续增长（图中红线）。

### 时间步长

步长要比体系中最快的振动周期小得多。分子晶体里最快的是含氢的伸缩振动（O–H、N–H、C–H），所以步长通常比只含重原子的体系小。

::: unverified 待核验
- 含氢有机体系常用约 0.5–1 fs 的步长，具体以所用程序和文献推荐为准；可以把氢替换为氘或约束键长来放大步长。
:::

### 温度

$$\frac{3}{2}N k_B T_{\mathrm{inst}} = \sum_{k=1}^{N}\frac{1}{2}m_k |\mathbf{v}_k|^{2}$$

其中 $N$ 是原子数，$k_B$ 是玻尔兹曼常数，$T_{\mathrm{inst}}$ 是瞬时温度（严格来说左边应扣除约束的自由度）。瞬时温度会涨落，平均值才是体系温度。

### 恒温器

- **Nosé–Hoover**：引入一个额外的“热浴”自由度与粒子速度耦合，扩展体系的动力学生成正则系综 [@nose-1984] [@hoover-1985]。小体系或谐振体系中可能遍历性不足，常用链式版本。
- **随机速度重标定 (CSVR)**：每一步按正则分布随机地重标定动能，既能快速控温，又生成正确的正则系综 [@bussi-2007-csvr]。
- **Berendsen**：把温度指数式地拉向目标值，控温稳定，但**不生成**正确的正则系综（动能涨落被压低），适合平衡阶段，不适合采样。

### 恒压器

Parrinello–Rahman 方法把晶胞矩阵作为动力学变量，允许晶胞形状和体积随压力变化，可以模拟相变和各向异性热膨胀 [@parrinello-1981-npt]。

::: assumption 遍历性
时间平均等于系综平均的前提是轨迹能在模拟时间内充分访问相关的相空间。分子晶体中的多晶型转变、分子转动等稀有事件可能远超模拟时间，这时 MD 的结果只代表起始盆地内的平均（见 [[energy-landscape]]）。
:::

## 在本研究线里的样子 {mapping}

- **MLIP 驱动的 MD**：用 MACE 跑 β-甘氨酸超胞的 NPT 模拟，看结构在室温下是否稳定、晶胞参数随温度怎样变（与 [[quasi-harmonic]] 的结果对比）。
- **主动学习**：从 MD 轨迹中挑出模型不确定的构型补充 DFT 数据（见 [[mlip-basics]] 与 [[mlip-finetuning]]）。
- **能量漂移是质量检查**：NVE 模拟中总能明显漂移，常说明步长太大，或势函数不光滑、力和能量不一致。
- **有限温度的性质**：例如有限温度下的平均晶胞，再在其上计算压电系数，比较 0 K 结果与实验（见 [[piezoelectric-tensor]]）。

## 常见坑 {mapping}

- **用 Berendsen 采样**：涨落不对，热容、弹性常数这类涨落相关的量会出错。
- **平衡不足就开始统计**：先看温度、压力、晶胞参数是否已经稳定。
- **统计误差按帧数算**：相邻帧高度相关，有效独立样本数远少于帧数，需要用块平均估计误差。
- **超胞太小**：长波声子被截断，热膨胀和热导等性质会有尺寸效应。
- **模拟中原子“爆炸”**：MLIP 外推到训练集外的构型，见 [[mlip-basics]]。

## 检验自己 {mapping}

::: question 解释
为什么速度 Verlet 在长时间模拟中能量不会系统漂移，而显式 Euler 会？
:::

::: question 推导
一维谐振子 $\omega = 1$，用显式 Euler 积分一步，写出 $(x, v)$ 的线性映射矩阵，计算它的行列式，说明能量每步乘以 $1 + \omega^{2}\Delta t^{2}$。
:::

::: question 迁移
你用 MACE 跑 β-甘氨酸 300 K NPT 模拟 100 ps，晶胞体积比 0 K 优化结果大 3%。在把它当作热膨胀之前，你要检查哪些事情？
:::
