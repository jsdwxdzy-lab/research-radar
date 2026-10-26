# 科研雷达 · 2026-10-26（周一）

> 领域：计算化学 / 有机分子晶体（CSP、晶体生成模型、机器学习势、功能导向筛选）  
> 自动生成 17:14 · 抓取窗口 10-25 01:14 → 现在 · 候选 481 → 本轮入库 19 → 今日累计 **23**（本次 +0） · 来源 arxiv/crossref/openalex/rss/github

## 今日速览

- **最高相关度**：Structure and Stability Prediction of Binary and Ternary Molecular Mixed Crystals Using En…（10.4）
- **本周条目最多**：机器学习势与通用势函数（MLIP / UMA）（16 篇）
- **构成**：机器学习势与通用势函数（MLIP / UMA） 16 · 分子晶体结构预测（CSP）与能量图景 3 · 生成模型与逆向设计 3 · 功能导向的晶体性质与高通量筛选 1

## 今日点评

> 今天最值得看的是第1条：它结合CSP、力场晶格能与晶格动力学、Δ-ML能量校正和缩放配分函数，用代表性取代超胞系综估算蒽/吖啶/吩嗪二元、三元混晶的组成依赖自由能，直接对应你关注的固溶与能量图景，可借鉴为稳定性评估流程。其次是第2条Orbitol：它以Wyckoff轨道为token，按指定空间群生成晶体，是无机晶体生成方向的对标工作。它的对称性约束思路能否迁移到分子晶体的分子位点，是值得追的线索。

## 今日最值得看

1. **[Structure and Stability Prediction of Binary and Ternary Molecular Mixed Crystals Using Ensemble Free Energies](https://doi.org/10.1021/acs.cgd.6c00999)**
   `CSP` · *Crystal Growth & Design* · 2026-10-22 · 👤Graeme M. Day
   <sub>命中：crystal structure prediction、crystal structure、lattice energy</sub>
   > Mixed crystals provide a route to tune the properties of molecular solids through continuous changes in composition. However, predicting their stability is challenging because it requires determining both substitution energies and configurational entropy across large configuration spaces.

2. **[Orbitol: Crystal Generation on Wyckoff Orbits](https://arxiv.org/abs/2610.30086)**
   `生成设计` · *arXiv* · 2026-10-21
   <sub>命中：crystal generation、generative models、symmetry-aware、wyckoff</sub>
   > Generative models propose crystalline materials by learning composition and geometry, but unconditional sampling gives no direct control over the space group, which constrains whether responses such as piezoelectricity are symmetry-allowed.

3. **[Automatically Building and Updating a Knowledge Graph of MLIP Models](https://hal.science/hal-05785570)**
   `MLIP` · *HAL* · 2026-10-25
   <sub>命中：machine learning interatomic potential、interatomic potential、mlip</sub>
   > Complementing the many efforts in providing semantic representations of concepts, notions, and entities in materials science, we report and illustrate a process by which we can automatically build a knowledge graph of the fast evolving field of machine learning applied to the prediction of material properties, focusing…

4. **[CrystalAR: Autoregressive Modeling for Symmetric Crystal Generation](https://arxiv.org/abs/2610.27762)**
   `生成设计` `CSP` · *arXiv* · 2026-10-20
   <sub>命中：crystal generation、generative models、de novo、wyckoff、crystal structure prediction (csp) 等 8 个</sub>
   > Deep generative modeling has achieved remarkable progress in crystal generation. Given the rich symmetries inherent in crystalline structures, recent work has sought to explicitly incorporate space-group symmetry into generative models, enabling more effective exploration of novel symmetry templates.

5. **[Machine Learning-Assisted Discovery of Carbon-Related Defect Formation Mechanisms in Diamond](https://arxiv.org/abs/2610.26301)**
   `MLIP` · *arXiv* · 2026-10-19
   <sub>命中：machine learning interatomic potential、density functional theory、interatomic potential、mlip</sub>
   > Diamond is an important host material for functional defects such as solid-state spin qubits. During the defect creation by irradiation and subsequent thermal annealing, carbon-related defects, including vacancies and interstitials, are generated and can migrate to form new defect complexes.

6. **[Machine‐Learning‐Potential‐Driven Volcano Relationship in Grain Boundary Amorphicity and Ionic Transport of Antiperovskite Solid Electrolytes](https://doi.org/10.1002/adma.75492)**
   `MLIP` · *Advanced Materials* · 2026-10-23
   <sub>命中：machine learning interatomic potential、interatomic potential、mlip</sub>
   > Ionic transport in solid‐state electrolytes is governed by interfacial disorder and local chemical environments, yet their microscopic design principles remain challenging because large‐scale interfacial kinetics are simulated using molecular dynamics (MD), where predictive design requires quantum‐level accuracy.

## 按主题展开

### 分子晶体结构预测（CSP）与能量图景

- **[Slipping into Solvates: Structure-Surface-Solvent Interplay in the Mechanochemical Solvate Formation of Ivacaftor](https://doi.org/10.1021/acs.cgd.6c00526)**
  `CSP` · *Crystal Growth & Design* · 2026-10-24
  <sub>命中：molecular crystals、molecular crystal、crystal structure</sub>
  > Solvate formation in molecular crystals remains difficult to predict, particularly under non-equilibrium conditions, where the initial solid state, mechanically generated surfaces, anisotropic surface…

- **[Microenvironmental pH-Modulated Vitamin B6 Ternary Eutectics for BCS Class IV Drug Delivery](https://doi.org/10.1021/acs.cgd.6c01251)**
  `CSP` · *Crystal Growth & Design* · 2026-10-24
  <sub>命中：cocrystal</sub>
  > The essence of developing multicomponent solid formulations for drugs with poor physicochemical and pharmacokinetic properties is rapidly evolving to cut short the consumption of resources and time.

### 生成模型与逆向设计

- **[Probing the limits of forward screening and inverse design of crystal materials](https://arxiv.org/abs/2610.32678)**
  `生成设计` `MLIP` · *arXiv* · 2026-10-23 · [PDF](https://arxiv.org/pdf/2610.32678)
  <sub>命中：inverse design、equivariant</sub>
  > Crystal materials are designed either by screening known crystals for a target property or by generating new crystals with that property.

### 机器学习势与通用势函数（MLIP / UMA）

- **[Symmetry-Based Parameter Efficient Low-Rank Fine-Tuning for High-Throughput Calculation of Lattice Thermal Conductivity](https://arxiv.org/abs/2610.29634)**
  `MLIP` · *arXiv* · 2026-10-21 · [PDF](https://arxiv.org/pdf/2610.29634)
  <sub>命中：machine-learned interatomic potential、interatomic potential、fine-tuning、mattersim</sub>
  > Accurate and efficient prediction of lattice thermal conductivity (LTC) is essential for developing materials for thermoelectric, microelectronic, and photovoltaic applications.

- **[Unconstrained learning of equivariant atomistic properties](https://arxiv.org/abs/2610.31183)**
  `MLIP` · *arXiv* · 2026-10-22 · 👤Michele Ceriotti · [PDF](https://arxiv.org/pdf/2610.31183) · 多源×2
  <sub>命中：potential energy surface、equivariant、fine-tuning</sub>
  > Machine-learned interatomic potentials based on graph neural networks (GNNs) have made first-principles accuracy routine for the potential energy surface (PES).

- **[Mechanistic Insights of Jahn–Teller Effect Suppression in High-Entropy Prussian Blue Analogue Cathodes](https://doi.org/10.1021/jacs.6c15227)**
  `MLIP` · *Journal of the American Chemical Society* · 2026-10-23
  <sub>命中：machine learning interatomic potential、interatomic potential</sub>
  > The Jahn–Teller (J-T) effect, as discovered by Hermann Jahn and Edward Teller in 1937, often causes lattice distortion and structural instability in Mn-based battery materials.

- **[Atomic-scale mechanisms of SiO2 plasma-enhanced chemical vapor deposition revealed by molecular dynamics with a machine-learning interatomic potential](https://doi.org/10.1016/j.apsusc.2026.168654)**
  `MLIP` · *Applied Surface Science* · 2026-10-21
  <sub>命中：machine learning interatomic potential、interatomic potential</sub>

- **[Mechanical versus thermal amorphization of ZIF-4: from local rearrangements to network disorder](https://doi.org/10.26434/chemrxiv.15010773/v1)**
  `MLIP` · *ChemRxiv* · 2026-10-21
  <sub>命中：machine learning interatomic potential、interatomic potential</sub>
  > There is mounting evidence that different amorphization routes can produce metalorganic framework (MOF) glasses with distinct structures and properties, yet the microscopic origins of these difference…

- **[Combining Simulations and Spectroscopy to Design Protective Coatings on Sulfide Solid Electrolytes](https://arxiv.org/abs/2610.32905)**
  `MLIP` · *arXiv* · 2026-10-23 · 👤Michele Ceriotti · [PDF](https://arxiv.org/pdf/2610.32905)
  <sub>命中：interatomic potential</sub>
  > Sulfide solid electrolytes are attractive for all-solid-state batteries because of their high Li-ion conductivity and favorable processability, but their practical use is limited by electrochemical in…

- **[Factorised Cartesian Atomic Cluster Expansion for Low-Cost Machine-Learning Interatomic Potentials](https://doi.org/10.26434/chemrxiv.15010957/v1)**
  `MLIP` · *ChemRxiv* · 2026-10-23
  <sub>命中：density functional theory、equivariant、mace</sub>
  > Machine-learning interatomic potentials can reach the accuracy of density functional theory at a fraction of its cost, but the most accurate equivariant models remain expensive, mainly because of the…

### 功能导向的晶体性质与高通量筛选

- **[Flexo-Photoresponses from First Principles](https://arxiv.org/abs/2610.32341)**
  `性质筛选` · *arXiv* · 2026-10-23 · [PDF](https://arxiv.org/pdf/2610.32341)
  <sub>命中：second harmonic generation、nonlinear optical</sub>
  > Many functionally important materials, such as silicon, possess high-symmetry crystal structures that forbid even-order nonlinear optical responses, thereby limiting their application in e.g., photoni…

## 工具与模型发布

_（窗口内没有关注工具的版本发布）_

## 领域新闻

_（窗口内没有命中关注主题的新闻）_

## 关注课题组的新作

- [Unconstrained learning of equivariant atomistic properties](https://arxiv.org/abs/2610.31183) — *arXiv* · 2026-10-22（Michele Ceriotti）
- [Combining Simulations and Spectroscopy to Design Protective Coatings on Sulfide Solid Electrolytes](https://arxiv.org/abs/2610.32905) — *arXiv* · 2026-10-23（Michele Ceriotti）
- [Structure and Stability Prediction of Binary and Ternary Molecular Mixed Crystals Using Ensemble Free Energies](https://doi.org/10.1021/acs.cgd.6c00999) — *Crystal Growth & Design* · 2026-10-22（Graeme M. Day）

## 会议与活动（未来 120 天，日期以官网为准）

- **12-01**（36 天后）[MRS Fall Meeting](https://www.mrs.org/fall-meeting) — 材料计算与 AI 相关 session
- **12-08**（43 天后）[NeurIPS + ML4PS / AI4Science workshops](https://neurips.cc/) — 机器学习与物理科学交叉方法的最新动向

## 运行健康

| 数据源 | 抓取 | 状态 |
| --- | --- | --- |
| arxiv | 342 | ok |
| crossref | 34 | ok |
| openalex | 67 | ok |
| rss | 77 | ok |
| github | 0 | ok |

> 原始 520 → 去重 481 → 剔除标题噪声 18 → 低相关度 444 → 入库 19。

<sub>配置 `config/config.json` · 历史 `state/radar.sqlite3` · 重跑 `./run_daily.sh` · 调试 `python3 -m radar explain '标题'`</sub>
