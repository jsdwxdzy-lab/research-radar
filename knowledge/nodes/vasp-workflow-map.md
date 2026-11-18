```json
{
  "id": "vasp-workflow-map",
  "title": "压电计算链里的 VASP 设置与理论对应",
  "type": "synthesis",
  "parent": "method-layers",
  "research": ["piezo", "csp"],
  "keywords": ["VASP", "INCAR", "IBRION", "LEPSILON", "DFT-D3", "piezoelectric workflow"],
  "purpose": "把一条典型的有机分子晶体压电计算链里每一步用到的 VASP 参数对到背后的理论条目上，写清每一步在什么条件下可信、局限在哪里，以及计算链还没用到、可以延伸的方法。",
  "prereq": {
    "intuitive": ["[[method-layers]]", "[[energy-structure-response]]"],
    "full": ["[[finite-difference-vs-dfpt]]", "[[piezoelectric-tensor]]"]
  },
  "status": "draft",
  "version": "0.1",
  "updated": "2026-11-18",
  "sources": ["vasp-wiki-ibrion", "vasp-wiki-isif", "vasp-wiki-ismear", "vasp-wiki-lepsilon", "vasp-wiki-ivdw", "vasp-wiki-lcalcpol", "vasp-wiki-pulay", "grimme-2010-d3", "wu-2005-strain"],
  "origin": "按需新增（2026-11-18）：常见的 VASP 压电计算流程与理论地图的对照",
  "changelog": [{"version": "0.1", "date": "2026-11-18", "note": "初稿：四步计算链的参数—理论对照表、各步适用条件与局限、可延伸的方法；配图 1 张"}]
}
```
## 这一页怎么用 {intuition}

一条常见的压电计算链把一个优化好的分子晶体变成压电张量 $d$。它分四步，每一步都对应理论地图里已有的几个条目。这一页不重新讲理论，只做三件事：把 INCAR 参数对到理论上；写出每一步的前提，前提不成立时结果就不可信；列出计算链还没用、但可能需要的方法。

![压电计算链的四步与交叉检查（示意）。绿色“含 D3”、红色“不含 D3”标出色散校正进入了哪一步。](figs/vasp-workflow.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $\bar C$、$C$ | 夹持离子、弛豫离子弹性张量 | ② 的输出 |
| $K$ | 去掉平移零模的力常数矩阵 | ② 和 ③ 都给出，见下文“两份力常数” |
| $\Lambda$ | 内应变张量：应变在原子上产生的力 | ② 的输出 |
| $\varepsilon^{\infty}$、$Z^{*}$、$\bar e$ | 电子介电张量、玻恩有效电荷、夹持离子压电张量 | ③ 的输出 |
| $\Omega$ | 晶胞体积 | ④ 的公式 |
| $\eta$、$P(\eta)$ | 小应变与该应变下的宏观极化 | 虚线框（交叉检查） |

④ 中的组合公式和 $d$ 与 $e$ 的换算见 [[piezoelectric-tensor]]。

## 参数—理论对照 {mapping}

| 步骤 | 关键参数 | 背后的理论 | 这一步默认的前提 |
| --- | --- | --- | --- |
| ① 变胞优化 | `ISIF = 3`，`IBRION = 2`，`EDIFFG < 0`，`ENCUT` 高 | [[cell-relaxation]]，[[hellmann-feynman]]（力与应力），[[plane-waves]]（Pulay 应力） | 找到的是局部极小，且就是要研究的那个多晶型 |
| ① 电子部分 | `GGA` 默认 PBE，PAW 势，`PREC = Accurate`，`EDIFF` | [[kohn-sham-dft]]，[[pbe]]，[[paw]]，[[scf-cycle]] | 闭壳层、有带隙；PBE 给出的电子结构定性正确 |
| ① 色散 | `IVDW = 11`（D3 零阻尼），`VDW_S8`、`VDW_SR` 等 | [[dispersion-corrections]] | 参数与 PBE 配套；成对加三体以外的多体效应可以忽略 |
| ① 占据与 k 点 | `ISMEAR = 0`，`SIGMA = 0.05`，Γ 中心网格 | [[smearing-occupations]]，[[reciprocal-space]] | 带隙远大于展宽；k 点网格随晶胞形状调整 |
| ② 有限差分 | `IBRION = 6`，`ISIF = 3`，`NFREE = 2`，`POTIM = 0.01` | [[finite-difference-vs-dfpt]]，[[elastic-tensor]]，[[phonons]] | 参考结构无残余应力和残余力；步长落在截断误差与噪声之间 |
| ③ 微扰 | `IBRION = 8`，`LEPSILON = .TRUE.` | [[perturbation-theory]]，[[dielectric-born]]，[[berry-phase-polarization]] | 绝缘体；所用泛函在线性响应里有实现 |
| ④ 合成 | 后处理组合 $\bar e$、$Z^{*}$、$K$、$\Lambda$、$C$ | [[piezoelectric-tensor]]，[[tensors]] | 所有量来自同一结构、同一设置；Voigt 约定一致 |
| 交叉检查 | 应变胞 `ISIF = 2`，`LCALCPOL = .TRUE.` | [[berry-phase-polarization]]，[[finite-difference-vs-dfpt]] | 应变足够小、极化在同一分支上 |
| 有限温度（计划中） | MD 轨迹上的应变与极化 | [[fluctuation-response]]，[[molecular-dynamics]] | 经典核、遍历、轨迹足够长 |

::: definition 零阻尼 D3 与 BJ 阻尼
`IVDW = 11` 是 D3 零阻尼，`IVDW = 12` 是 D3(BJ) [@vasp-wiki-ivdw]。两种阻尼的参数各自对泛函拟合，不能混用 [@grimme-2010-d3]。文献里分子晶体常写“PBE-D3(BJ)”，和文献比较时先确认双方用的是哪一种阻尼。
:::

## 各步的适用与局限 {mapping}

### ① 变胞优化

- **适用**：0 K、静态晶格下的平衡结构。对分子晶体，晶格参数的误差主要来自色散校正和泛函，而不是数值设置。
- **局限 1：没有温度**。优化给的是势能面极小，没有零点振动和热膨胀，与室温实验晶胞比通常偏小。需要时用 [[quasi-harmonic]] 修正。
- **局限 2：Pulay 应力**。变胞时平面波数目固定，有效截断能随体积变化。截断能取高，或者优化后从新晶胞重启再优化一次 [@vasp-wiki-pulay]。见 [[plane-waves]]。
- **局限 3：质子位置**。对有机盐和共晶，PBE 可能把质子放错到另一侧，结构“优化成功”但化学上是另一个物种。见 [[proton-position]]。

### ② 有限差分弹性与力常数

- **适用**：任何能给出力和应力的哈密顿量，包括 D3。它是计算链里**唯一把 D3 计入力常数和内应变**的一步。
- **局限 1：截断能不一致**。若 ② 用的 `ENCUT` 比 ① 低，① 得到的“零应力”结构在 ② 的设置下不再是零应力，残余应力会混入弹性常数（见 [[elastic-tensor]] 的“常见坑”）。要么两步用同一截断能，要么在 ② 的设置下重新优化。
- **局限 2：自洽精度**。差商的噪声项与 `EDIFF` 有关。对总能够用的 `EDIFF`，对力常数的差商可能偏松；有限差分一般要比结构优化收紧一到两个数量级，具体按 [[finite-difference-vs-dfpt]] 测试。
- **局限 3：软模与非谐**。分子晶体的分子转动、氢键模式很软，`POTIM = 0.01` Å 的中心差分对它们可能已经偏大或偏小，需要按 [[finite-difference-vs-dfpt]] 做步长测试。

### ③ 微扰 DFPT

- **适用**：有带隙的体系，给出电子部分（$\varepsilon^{\infty}$、$Z^{*}$、$\bar e$）而不需要步长。
- **局限 1：两份力常数**。③ 也给出力常数，但可能不含 D3（见下面的待核验）。用 ③ 的 $K$ 组合离子项，等于在“PBE 无色散”的能量面上算离子弛豫，与 ① 的结构不自洽。② 的 $K$ 含 D3，两者之差就是色散对离子项的影响。
- **局限 2：泛函支持**。线性响应不支持杂化泛函；需要杂化泛函时改用有限电场方法，见 [[finite-field-polarization]]。

::: unverified 待核验
- VASP 的线性响应（`IBRION = 7/8`）是否支持 `IVDW` 色散校正，按 [@vasp-wiki-ibrion] 和 [@vasp-wiki-ivdw] 核对；若不支持，③ 的力常数不含色散，与 ② 不同。
- `IBRION = 8` 配合 `ISIF = 3` 时，VASP 是否也输出弹性张量，按 [@vasp-wiki-ibrion] 核对；这里不依赖它。
- `IBRION = 6` 的应变步长由程序内部决定还是受 `POTIM` 控制，按 [@vasp-wiki-ibrion] 核对。
- `IOPTCELL` 是第三方补丁提供的参数（用于固定部分晶格分量），不在官方 VASP 中；在没有该补丁的版本里它会被忽略。需要按所用版本确认。
:::

### 交叉检查：应变加 Berry 相

- **适用**：直接按定义 $e = \partial P/\partial\eta$ 求弛豫离子压电张量，离子弛豫在含 D3 的能量面上做，不依赖 ③ 的力常数 [@wu-2005-strain]。
- **局限**：极化只定义到一个极化量子，各应变下要取同一分支；还要区分 proper 与 improper 压电张量（见 [[berry-phase-polarization]]）。每个应变都要完整弛豫离子，代价比 ② 和 ③ 高。

## 可以延伸的方向 {mapping}

| 计算链没覆盖的问题 | 可以用的方法 | 条目 |
| --- | --- | --- |
| PBE 低估带隙，$\varepsilon^{\infty}$ 和 $Z^{*}$ 可能偏大 | 杂化泛函加有限电场 | [[finite-field-polarization]]，[[xc-functionals]] |
| 室温下的 $d$，以及软模的非谐贡献 | 有限温度 MD 的涨落公式 | [[fluctuation-response]] |
| 热膨胀改变晶胞，进而改变 $C$ 和 $e$ | 准简谐近似 | [[quasi-harmonic]] |
| 成对色散对极化率高的芳香体系不够 | 多体色散（MBD） | [[dispersion-corrections]] |
| 批量候选结构太多，DFT 太贵 | MLIP 预优化，长程静电模型预测 $Z^{*}$ | [[mlip-basics]]，[[mlip-electrostatics]] |

## 检验自己 {mapping}

::: question 解释
为什么用 ③ 的力常数组合离子项，和用 ② 的力常数组合，得到的 $e$ 不一样？差别的物理来源是什么？
:::

::: question 迁移
如果 ② 的截断能低于 ①，你会怎样设计一个最便宜的测试，判断残余应力对 $C_{ij}$ 的影响是否可以忽略？
:::

::: question 解释
交叉检查得到的 $e$ 和 ④ 合成的 $e$ 一致，能说明计算对实验可靠吗？还差哪一类误差（见 [[error-sources]]）？
:::
