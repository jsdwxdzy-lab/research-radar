```json
{
  "id": "berry-phase-polarization",
  "title": "极化与 Berry 相",
  "type": "concept",
  "parent": "response",
  "research": [
    "piezo"
  ],
  "keywords": [
    "Berry phase",
    "modern theory of polarization",
    "polarization quantum"
  ],
  "purpose": "周期体系里极化为什么不能直接由电荷分布求出，现代极化理论和极化量子怎样解决这个问题。",
  "prereq": {
    "intuitive": [
      "电偶极矩 p = Σ q r",
      "周期边界条件"
    ],
    "full": [
      "[[reciprocal-space]] 与 Bloch 定理",
      "[[plane-waves]]"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "resta-1994-polarization",
    "king-smith-1993-polarization",
    "vanderbilt-2018-berry",
    "vasp-wiki-lcalcpol"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：晶胞偶极为什么不唯一、Berry 相公式、极化量子与分支、VASP 对应与常见坑；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

有限分子的偶极矩很清楚：$p = \sum_i q_i\,r_i$。到了无限周期晶体里，“晶胞的偶极矩除以体积”这个想法不再成立：同一个周期电荷分布，晶胞框选的位置不同，算出的偶极就不同，甚至方向相反 [@resta-1994-polarization]。电子密度是连续分布的，同样没有唯一的切法。

现代极化理论给出的解决办法是：

1. 不问“极化是多少”，而问**极化变化了多少**。极化变化等于变化过程中流过晶体的电流对时间的积分，这是可测量的。
2. 电子部分的这个变化可以写成波函数在布里渊区上的 **Berry 相**，只用一个状态的波函数就能算 [@king-smith-1993-polarization]。
3. 代价是单个状态的极化只确定到一个**极化量子**的整数倍：$P$ 是一组等间隔的值，而不是一个数。

![上：同一条一维电荷链，晶胞 A 与晶胞 B 给出方向相反的偶极。下：允许的极化值构成以极化量子为间隔的格点，只有沿连续路径的变化 ΔP 有确定意义。](figs/polarization-lattice.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $+$、$-$ | 周期排列的正、负电荷 | 上图蓝、红圆点 |
| 晶胞 A、B | 两种同样合法的晶胞取法 | 绿色实框、橙色虚框 |
| $R$ | 晶格矢量（一维时就是晶格常数） | 下图相邻格点的间距对应 $eR/\Omega$ |
| $\Omega$ | 晶胞体积 | 极化量子的分母 |
| $P_0$ | 多值集合中任取的一个代表值 | 下图任一蓝点 |
| $n$ | 任意整数，标记分支 | 下图不同蓝点 |

## 定义与公式 {math}

::: definition 电子极化的 Berry 相公式
$$\mathbf{P}_{\mathrm{el}} = -\frac{f\,e}{(2\pi)^{3}} \sum_{n}^{\mathrm{occ}} \int_{\mathrm{BZ}} \mathrm{d}^{3}k\; \langle u_{n\mathbf{k}} \,|\, i\nabla_{\mathbf{k}} \,|\, u_{n\mathbf{k}} \rangle$$

其中求和遍历占据能带 $n$；积分遍历布里渊区；$u_{n\mathbf{k}}$ 是 Bloch 函数的周期部分；$\langle u|i\nabla_{\mathbf{k}}|u\rangle$ 是 Berry 联络；$f$ 是自旋简并度（非自旋极化时 $f = 2$）；$e$ 是元电荷，负号来自电子带负电 [@king-smith-1993-polarization]。
:::

总极化再加上离子（原子核加芯电子）的点电荷贡献：

$$\mathbf{P} = \mathbf{P}_{\mathrm{el}} + \frac{e}{\Omega}\sum_{\kappa} Z^{\mathrm{ion}}_{\kappa}\,\mathbf{r}_{\kappa}$$

其中 $Z^{\mathrm{ion}}_{\kappa}$ 是原子 $\kappa$ 的价离子电荷（赝势或 PAW 中的价电子数），$\mathbf{r}_{\kappa}$ 是它的位置。

::: theorem 极化量子
改变 Bloch 函数的相位约定，或把某个原子移动一个晶格矢量 $\mathbf{R}$，上式的结果改变

$$\Delta\mathbf{P} = \frac{f\,e}{\Omega}\,\mathbf{R}$$

的整数倍。所以单个结构的极化是一组格点 $\{\mathbf{P}_0 + f e\mathbf{R}/\Omega\}$，其中 $\mathbf{R}$ 取遍晶格矢量 [@vanderbilt-2018-berry]。
:::

两个结构之间的物理极化差，是沿一条使带隙始终不闭合的连续路径，把每一步的变化接起来得到的值。实际做法是：在路径上取足够密的中间结构，使相邻两点的变化远小于极化量子，然后选择让曲线连续的分支。

::: unverified 待核验
- 公式中的符号与 $f$ 的放置按 [@vanderbilt-2018-berry] 的约定核对；不同文献对 $e$ 取正还是取负有差别。
- 离子项中 PAW 的价电荷 $Z^{\mathrm{ion}}$ 与 VASP 实际输出的“ionic dipole”是否完全对应，查 [@vasp-wiki-lcalcpol]。
:::

## 在本研究线里的样子 {mapping}

- **为什么压电要用它**：压电系数 $e = \partial P/\partial \eta$ 就是极化的变化。用有限差分算 $e$ 时，要在几个应变下各算一次 Berry 相极化，再求差分。
- **VASP**：`LCALCPOL = .TRUE.` 用 Berry 相方法输出电子与离子偶极 [@vasp-wiki-lcalcpol]。`LEPSILON` 的微扰方法不直接算 $P$，而是算它对扰动的导数，所以没有分支问题，见 [[finite-difference-vs-dfpt]]。
- **β-甘氨酸是极性晶体**：点群 2 允许自发极化，所以零应变时 $P$ 本身就可能不为零。压电只关心它对应变的导数，但这会引出 [[piezoelectric-tensor]] 里提到的 proper 与 improper 压电张量的区别。

## 常见坑 {mapping}

- **分支跳变**：两个应变点的极化差接近极化量子时，直接相减会差一个量子。先把差值与极化量子比较，再决定是否加减整数个量子。
- **k 点方向**：Berry 相沿某个倒格矢方向的 k 点串计算。这个方向的 k 点太少，结果不收敛。
- **把单个 $P$ 当作物理量**：单个结构“极化是多少”在没有指定参考结构时没有意义。报告时要说明参考结构，或只报告差值。
- **带隙要保持打开**：路径上某个结构如果变成金属，极化不再有定义，差值也失去意义。

## 检验自己 {mapping}

::: question 解释
用图上方的一维链说明：为什么“晶胞偶极除以体积”不是一个好的极化定义？
:::

::: question 推导
对一维链，把一个电荷为 $+e$ 的离子平移一个晶格常数 $a$，晶胞偶极变化多少？与极化量子 $f e R/\Omega$ 对比（一维时把 $\Omega$ 换成 $a$，$f$ 取 1）。
:::

::: question 迁移
在两个应变 $\pm h$ 下算出的极化差正好接近一个极化量子，你怎样判断这是真实的大响应，还是分支跳变？
:::
