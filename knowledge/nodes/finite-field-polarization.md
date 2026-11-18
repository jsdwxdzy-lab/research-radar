```json
{
  "id": "finite-field-polarization",
  "title": "有限电场方法",
  "type": "method",
  "parent": "berry-phase-polarization",
  "research": ["piezo"],
  "keywords": ["finite electric field", "electric enthalpy", "LCALCEPS", "EFIELD_PEAD", "Zener breakdown", "PEAD"],
  "purpose": "在周期性晶体里直接加一个均匀电场，用极化随电场的变化求介电张量、玻恩电荷和压电张量；它是线性响应不支持某些泛函（例如杂化泛函）时的替代方法。",
  "prereq": {
    "intuitive": ["[[berry-phase-polarization]]", "[[dielectric-born]]"],
    "full": ["[[perturbation-theory]]", "[[finite-difference-vs-dfpt]]"]
  },
  "status": "draft",
  "version": "0.1",
  "updated": "2026-11-18",
  "sources": ["souza-2002-finite-field", "nunes-2001-berry-field", "umari-2002-field-md", "vasp-wiki-lcalcpol", "vanderbilt-2018-berry"],
  "origin": "按需新增（2026-11-18）：线性响应不支持杂化泛函时的替代方法",
  "changelog": [{"version": "0.1", "date": "2026-11-18", "note": "初稿：为什么周期体系不能直接加 E·r、电焓泛函、临界场、VASP 对应与适用范围；配图 1 张"}]
}
```
## 直觉 {intuition}

想算介电或玻恩电荷，最直接的做法是“加一个电场，看极化怎么变”。在分子里这很简单：哈密顿量加一项 $e\,\mathcal E\cdot \mathbf r$。在周期性晶体里不行，因为位置算符 $\mathbf r$ 不是周期的，$\mathcal E\cdot\mathbf r$ 随距离无限增大，没有基态。

解决办法是不再在哈密顿量里写 $\mathbf r$，而是把电场与 Berry 相极化 $\mathbf P$ 耦合：求极小的不是能量，而是**电焓** (electric enthalpy) $E - \Omega\,\mathcal E\cdot\mathbf P$ [@souza-2002-finite-field] [@nunes-2001-berry-field]。$\mathbf P$ 本身就是用 Berry 相定义的周期量（见 [[berry-phase-polarization]]），所以这个泛函在周期体系里有定义。

代价是：电场下的晶体严格说没有基态。电子可以从价带隧穿到下游很远处的导带（Zener 击穿）。有限 k 点网格把这段距离截断在 $N_k a$ 以内，只要电场足够小，隧穿被压住，求得的就是一个物理上有意义的长寿命态。

![电场使能带倾斜（示意）。价带顶上的电子与距离 $L$ 处导带底能量相同；当 $L$ 大于 k 点串对应的实空间长度时，有限网格上看不到这种隧穿。](figs/finite-field-band-tilt.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $\mathcal E$ | 外加的均匀电场（正文用 $\mathcal E$，图中写 $E$） | 绿色箭头 |
| $E_g$ | 带隙 | 灰色竖向箭头 |
| $L$ | 能量相同的价带态与导带态之间的距离 | 黑色双向箭头 |
| $N_k a$ | 电场方向上 k 点串的点数乘以晶格常数 | 橙色双向箭头 |

## 定义与公式 {math}

::: definition 电焓泛函
$$\mathcal F[\{\psi\};\mathcal E] = E_{\mathrm{KS}}[\{\psi\}] - \Omega\,\mathcal E\cdot\mathbf P[\{\psi\}]$$

其中 $E_{\mathrm{KS}}$ 是 Kohn–Sham 能量泛函；$\Omega$ 是晶胞体积；$\mathbf P$ 是电子与离子的总极化，电子部分由占据态的 Berry 相给出。对给定电场 $\mathcal E$，对波函数求 $\mathcal F$ 的极小 [@souza-2002-finite-field]。
:::

用几个小电场做完自洽后，响应量由差商给出：

$$\varepsilon^{\infty}_{\alpha\beta} = \delta_{\alpha\beta} + \frac{1}{\epsilon_0}\frac{\partial P_\alpha}{\partial \mathcal E_\beta}\bigg|_{\mathbf u}, \qquad Z^{*}_{m\alpha} = \frac{1}{e}\,\frac{\partial F_m}{\partial \mathcal E_\alpha}\bigg|_{\mathbf u}, \qquad \bar e_{\alpha j} = -\frac{\partial \sigma_j}{\partial \mathcal E_\alpha}\bigg|_{\mathbf u}$$

其中 $\epsilon_0$ 是真空介电常数；$|_{\mathbf u}$ 表示原子坐标固定（夹持离子）；$F_m$ 是原子坐标 $m$ 上的力；$e$ 是元电荷；$\sigma_j$ 是 Voigt 应力分量。第二、三式利用了能量混合二阶导数的对称性：$\Omega$ 乘以极化对位移的导数，等于力对电场的导数，两者除以 $e$ 都是 $Z^{*}$；极化对应变的导数等于应力对电场的导数（符号依应力约定而定）。

::: approximation 临界电场
有限 k 点网格下，只有电场满足大致

$$e\,|\mathcal E|\, N_k a \lesssim E_g$$

时，电焓极小才稳定，其中 $N_k$ 是电场方向的 k 点数，$a$ 是该方向的晶格周期 [@souza-2002-finite-field]。k 点越密，允许的电场越小。这一条是量级判据，不是精确阈值。
:::

## 和微扰方法的关系 {mapping}

- **求的是同一组量**：在线性区，有限电场与 DFPT 给出相同的 $\varepsilon^{\infty}$、$Z^{*}$ 和 $\bar e$（同一泛函、同一设置下）。区别和 [[finite-difference-vs-dfpt]] 讲的一样：一个有电场步长，一个没有。
- **它能做而 DFPT 做不了的**：只要程序能算能量和 Berry 相极化，就能做有限电场，不需要为每种泛函写响应方程。所以杂化泛函、某些 meta-GGA 下的介电与压电，通常走这条路。
- **还能做非线性**：大一些的电场下可以算二阶响应，或者在电场下做分子动力学 [@umari-2002-field-md]。

## 在本研究线里的样子 {mapping}

- **VASP**：`LCALCEPS = .TRUE.` 用有限电场计算介电张量、玻恩电荷和夹持离子压电张量；`EFIELD_PEAD` 指定一个固定电场。两者都基于 PEAD（perturbation expression after discretization）方法，属于 `LCALCPOL` 那一组功能 [@vasp-wiki-lcalcpol]。
- **用途**：检查 PBE 低估带隙对 $Z^{*}$ 和 $\bar e$ 的影响。做法是在同一个 PBE-D3 结构上，用杂化泛函加 `LCALCEPS` 重新算电子部分，再和 PBE 的 DFPT 结果比较。这一步只改电子响应，离子项（力常数、内应变）仍用 PBE-D3。
- **代价**：杂化泛函的计算量远高于 PBE，分子晶体晶胞又大，只适合对少数最终候选做。

::: unverified 待核验
- `LCALCEPS` 和 `EFIELD_PEAD` 在所用 VASP 版本中是否可用，以及与 `IVDW` 能否同时使用，按 [@vasp-wiki-lcalcpol] 核对。
- `LCALCEPS` 默认电场大小与差分方式，按官方文档核对；临界电场判据中的常数因子按 [@souza-2002-finite-field] 原文确认。
:::

## 常见坑 {mapping}

- **电场太大**：超过临界场后自洽不收敛，或者收敛到一个电荷已经转移的态。
- **k 点太密反而出问题**：在固定电场下加密 k 点会降低临界场；做 k 点收敛时要同时减小电场。
- **只换了泛函的一半**：用杂化泛函算电子响应、用 PBE-D3 算离子项时，要在说明里写清，不要把结果称为“杂化泛函压电系数”。

## 检验自己 {mapping}

::: question 解释
为什么在周期性晶体里不能直接在哈密顿量里加 $e\,\mathcal E\cdot\mathbf r$？电焓泛函是怎样绕开这个问题的？
:::

::: question 推导
从临界电场判据出发，说明为什么在固定电场下加密 k 点，计算会越来越不稳定。
:::

::: question 迁移
你想知道 PBE 带隙偏小会使 β-甘氨酸的 $d_{16}$ 偏大还是偏小。设计一个只改电子部分的最小计算，并说明结论的适用范围。
:::
