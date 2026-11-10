```json
{
  "id": "piezoelectric-tensor",
  "title": "压电张量",
  "type": "concept",
  "parent": "energy-structure-response",
  "research": [
    "piezo"
  ],
  "keywords": [
    "piezoelectric tensor",
    "piezoelectric coefficient",
    "internal strain",
    "d33"
  ],
  "purpose": "e 与 d 两种约定、夹持离子项与内应变项，以及哪些点群允许压电。",
  "prereq": {
    "intuitive": [
      "应变、应力、极化的物理含义",
      "[[energy-structure-response]] 里“响应是能量的二阶导数”"
    ],
    "full": [
      "[[tensors]] 的指标记号与坐标变换",
      "[[elastic-tensor]] 与 [[dielectric-born]]"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "ieee-176-piezo",
    "wu-2005-strain",
    "king-smith-1993-polarization",
    "vasp-wiki-lepsilon",
    "guerin-2018-amino-acid"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：e/d 定义与换算、夹持离子与内应变分解、对称性限制、VASP 中的对应、常见坑；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

压电描述的是**应变和极化之间的线性耦合**：拉伸或剪切晶体，晶体宏观极化改变；反过来，加电场，晶体变形。两个方向由同一组材料常数描述（热力学上是同一个能量的混合二阶导数）。

一个晶体只有在没有对称中心时才可能压电。直观理由：对称中心把 $P$ 变成 $-P$，却把应变 $\eta$ 变成它自己；如果 $\Delta P = e\,\eta$ 对两边都成立，只能 $e = 0$。

在分子晶体里，极化变化有两个来源：

1. 分子和电子云随晶胞一起均匀变形（**夹持离子**，clamped-ion）；
2. 分子在晶胞里重新转动、平移、氢键重排（**内应变** internal strain 引起的离子弛豫）。

对 β-甘氨酸这类软的氢键晶体，第 2 项通常是主要部分，这也是它对计算细节敏感的原因（见 [[energy-structure-response]] 的“软方向放大误差”）。

![一维离子链：夹持离子只做均匀拉伸，弛豫离子在此基础上再有内位移 Δu。](figs/piezo-clamped-relaxed.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $L$ | 未应变的晶胞长度 | 第一行灰色括号 |
| $\eta$ | 均匀应变 | 第二行晶胞变为 $L(1+\eta)$ |
| $\Delta u$ | 应变后亚晶格（正、负离子）之间的相对内位移 | 第三行橙色箭头 |
| $\bar e$ | 夹持离子压电系数：原子保持分数坐标不变时的响应 | 第二行的 $\Delta P$ |
| $Z^{*}$ | 玻恩有效电荷：单位位移带来的偶极变化 | 第三行附加项的系数 |
| $\Omega$ | 晶胞体积 | 第三行公式分母 |

## 定义与公式 {math}

::: definition 压电应力系数 e 与压电应变系数 d
$$e_{\alpha j} = \left.\frac{\partial P_\alpha}{\partial \eta_j}\right|_{\mathcal{E}=0}, \qquad d_{\alpha j} = \left.\frac{\partial \eta_j}{\partial \mathcal{E}_\alpha}\right|_{\sigma=0} = \left.\frac{\partial P_\alpha}{\partial \sigma_j}\right|_{\mathcal{E}=0}$$

其中 $P_\alpha$ 是宏观极化的第 $\alpha$ 个笛卡尔分量（$\alpha = 1,2,3$）；$\eta_j$、$\sigma_j$ 是应变、应力的 Voigt 分量（$j = 1,\dots,6$，依次对应 $xx, yy, zz, yz, xz, xy$，剪切取工程应变 $\eta_4 = 2\varepsilon_{yz}$ 等，与 [[elastic-tensor]] 相同）；$\mathcal{E}$ 是宏观电场。$e$ 的单位是 C/m²，$d$ 的单位是 pC/N（等价于 pm/V）。
:::

两者通过恒电场下的弹性柔顺系数 $s^{E}$（或刚度 $C^{E} = (s^{E})^{-1}$）联系 [@ieee-176-piezo]：

$$d_{\alpha k} = \sum_{j=1}^{6} e_{\alpha j}\, s^{E}_{jk}, \qquad e_{\alpha j} = \sum_{k=1}^{6} d_{\alpha k}\, C^{E}_{kj}$$

其中求和遍历 6 个 Voigt 分量。计算通常先得到 $e$，再借助弹性张量换成实验常报告的 $d$。

### 夹持离子项与内应变项

令 $u_{m}$ 表示原子坐标（$m$ 同时标记原子和方向）。应变改变晶胞时，原子先按分数坐标跟随（夹持），再在新的晶胞里弛豫到能量极小。对总极化求全导数 [@wu-2005-strain]：

$$e_{\alpha j} = \bar e_{\alpha j} + \frac{1}{\Omega}\sum_{m} Z^{*}_{m\alpha}\,\frac{\partial u_m}{\partial \eta_j}, \qquad \frac{\partial u_m}{\partial \eta_j} = \sum_{n}\bigl(K^{-1}\bigr)_{mn}\,\Lambda_{nj}$$

其中 $\bar e$ 是夹持离子压电张量；$\Omega$ 是晶胞体积；$Z^{*}_{m\alpha}$ 是玻恩有效电荷（原子位移 $u_m$ 引起的偶极 $\alpha$ 分量变化，见 [[dielectric-born]]）；$K$ 是去掉三个平移零模后的力常数矩阵；$\Lambda_{nj} = -\partial^{2}E/\partial u_n\,\partial\eta_j$ 是内应变张量，也就是应变在原子上产生的力。

::: unverified 待核验
- 上式的符号约定（$\Lambda$ 前的负号放在哪里、$Z^{*}$ 的指标次序、是否额外除以 $\Omega$）按 [@wu-2005-strain] 的原文核对；这里只保证结构是 $Z^{*}\cdot K^{-1}\cdot\Lambda$。
- “真”压电（proper）与“非真”压电（improper）张量的区别：用 Berry 相计算的极化随应变的变化，与实验测量的电流响应之间相差一个与自发极化有关的项。对非极性晶体这一项为零，对极性点群（β-甘氨酸的点群 2 属于极性点群）不为零。具体形式需查原始文献后补充。
:::

### 对称性怎样限制分量

压电张量是三阶极张量，必须在晶体点群的每个操作下不变。32 个晶体学点群里，11 个有对称中心，压电张量全为零；剩下 21 个中，点群 432 的对称性也使它全为零，所以 20 个点群允许压电（晶体物理教材中的共识结论）。分量的具体零化模式见 [[crystal-symmetry]]。

## 在本研究线里的样子 {mapping}

- **目标量**：β-甘氨酸（空间群 $P2_1$，点群 2）的剪切分量 $d_{16}$。按点群 2 的选择定则，$d_{16}$ 是允许的非零分量之一；它把 $xy$ 剪切和 $x$ 方向极化联系起来。轴的命名（哪个是二重轴、单斜角在哪个平面）要和所用晶体学设置一致，换设置后下标会改变。
- **VASP 里的对应**：`LEPSILON = .TRUE.` 用微扰方法给出夹持离子的压电张量和玻恩电荷；离子弛豫部分要结合力常数和内应变（`IBRION = 6` 或 `7/8` 等）得到 [@vasp-wiki-lepsilon]。两种做法的区别和一致性条件见 [[finite-difference-vs-dfpt]]。
- **单位换算**：VASP 输出的 $e$ 是 C/m²；换算 $d$ 时需要同一套计算得到的弹性张量（弛豫离子、恒电场），见 [[elastic-tensor]]。
- **和实验比较**：已有工作报告了氨基酸晶体压电的计算与测量对比 [@guerin-2018-amino-acid]；本条目尚未阅读其细节，不在这里引用它的数值。

## 常见坑 {mapping}

- **e 和 d 混用**：$d$ 包含弹性柔顺系数，软晶体里 $d$ 可以很大而 $e$ 并不大。比较文献数值前先确认是哪一个。
- **只算了夹持离子项**：只开 `LEPSILON` 得到的是 $\bar e$；对分子晶体，漏掉内应变项可能连量级都不对。
- **Voigt 次序不一致**：不同程序的剪切分量顺序可能不同（例如 $xy, yz, zx$ 与 $yz, xz, xy$）。下标 4、5、6 对应哪个剪切方向，要以输出文件的说明为准，并在换算 $d$ 时和弹性张量保持同一顺序。
- **剪切应变的因子 2**：工程剪切应变 $\gamma_{xy} = 2\eta_{xy}$。Voigt 记号里 $\eta_6$ 取哪一个，直接影响 $e_{\alpha 6}$ 差两倍。
- **晶体学设置与笛卡尔坐标的对应**：单斜晶系的二重轴选 $b$ 还是 $c$，以及笛卡尔 $x$ 轴沿哪条晶轴，都会改变“$d_{16}$”指的是哪个物理分量。

## 检验自己 {mapping}

::: question 解释
不用公式，说明为什么有对称中心的晶体不能压电。
:::

::: question 推导
从 $d = e\,s^{E}$ 出发，说明为什么同样的 $e$ 误差，在弹性很软的方向上会使 $d$ 的误差更大。
:::

::: question 迁移
如果一个分子晶体的夹持离子项很小，而内应变项很大，你会优先检查计算里的哪几个量（提示：看 $Z^{*}$、$K^{-1}$、$\Lambda$ 各自对什么敏感）？
:::
