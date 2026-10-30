# 科研雷达 · 2026-10-30（周五）

> 领域：计算化学 / 有机分子晶体结构预测、化学生成模型、有机铁电计算与手性分子晶体；低优先级跟踪视觉生成  
> 自动生成 09:08 · 抓取窗口 10-28 17:08 → 现在 · 候选 514 → 本轮入库 30 → 今日累计 **6**（本次 +0） · 来源 arxiv/crossref/openalex/rss/github

## 今日速览

- **最高相关度**：Polymorph-Dependent Reconstruction of Excitonic Coupling under Pressure Regulates Room Tem…（7.2）
- **本周条目最多**：化学相关生成模型（分子、材料与反应）（22 篇）
- **升温主题**：分子晶体结构预测（CSP）与能量图景、化学相关生成模型（分子、材料与反应）、视觉生成（低优先级）、生成模型相关数学、机器学习势与通用势函数（MLIP / UMA）、手性分子与分子晶体
- **构成**：分子晶体结构预测（CSP）与能量图景 2 · 机器学习势与通用势函数（MLIP / UMA） 2 · 手性分子与分子晶体 1 · 化学相关生成模型（分子、材料与反应） 1

## 今日最值得看

1. **[Polymorph-Dependent Reconstruction of Excitonic Coupling under Pressure Regulates Room Temperature Phosphorescence](https://doi.org/10.1021/acs.jpclett.6c03320)**
   `CSP` · *The Journal of Physical Chemistry Letters* · 2026-10-29
   <sub>命中：polymorphism、polymorph</sub>
   > Pressure-responsive organic room-temperature phosphorescence (RTP) offers a promising platform for optical sensing, information encryption, and anticounterfeiting. Understanding how external mechanical perturbations regulate triplet exciton dynamics in organic crystals remains a fundamental challenge in solid-state pho…

2. **[Mobilis: an open-source toolkit for charge transport in organic semiconductors, from crystal structures to temperaturedependent mobilities with dynamic disorder and active learning](https://doi.org/10.26434/chemrxiv.15011171/v1)**
   `手性晶体` · *ChemRxiv* · 2026-10-28
   <sub>命中：chiral molecules、chiral</sub>
   > Computing a charge mobility for an organic semiconductor involves a chain of steps: monomer site energies, intermolecular couplings, the thermal fluctuation of those couplings, and a transport model whose validity depends on the ratio of coupling to reorganization energy.

3. **[Self-Assembly of a Carboxyl -Bipyridinium Zwitterion into a High-Performance Photoswitchable NLO Crystal](https://doi.org/10.1021/acs.cgd.6c00920)**
   `CSP` · *Crystal Growth & Design* · 2026-10-29
   <sub>命中：molecular crystals</sub>
   > Efficient photoswitchable second-order nonlinear optical (NLO) materials are highly attractive for optical signal processing. However, achieving high-performance switching in molecular crystals remains challenging, requiring simultaneous optimization of response speed (<120 s saturation), modulation depth (∼90%), and o…

4. **[Fast and transferable interatomic potential for alloys, compounds, and hydrides in the Fe–Cr–Ni–Ti–H system](https://doi.org/10.1016/j.commatsci.2026.115182)**
   `MLIP` · *Computational Materials Science* · 2026-10-28
   <sub>命中：interatomic potential</sub>
   > Fast and transferable interatomic potentials are in high demand for atomistic simulations of multicomponent systems, particularly those involving compounds and hydrides. In this work, we present a new classical interatomic model for the Fe–Cr–Ni–Ti–H system in the form of an angular-dependent potential (ADP).

5. **[Paired-Isotopologue Hessian Benchmarking for Second-Order Validation of Machine-Learned Water Potentials](https://doi.org/10.1021/acs.jctc.6c01692)**
   `MLIP` · *Journal of Chemical Theory and Computation* · 2026-10-29
   <sub>命中：potential energy surface</sub>
   > Machine-learned interatomic potentials (MLIPs) are commonly validated against energies and forces, yet vibrational predictions depend on the curvature and mode information encoded in the Hessian of the potential-energy surface.

6. **[EVA-Flow: Learning Shared Chemistry for Unified Environment-Aware Molecular Conformation Generation](https://doi.org/10.48550/arxiv.2610.36280)**
   `生成模型` `CSP` · *arXiv* · 2026-10-26
   <sub>命中：conformer generation、crystal packing</sub>
   > Molecular 3D structures underpin simulations of thermodynamics, kinetics, crystallization, and nucleation, making their accurate prediction central to drug discovery and materials design. However, molecular geometry can change dramatically across environments.

## 按主题展开

_（今日无）_

## 工具与模型发布

_（窗口内没有关注工具的版本发布）_

## 领域新闻

_（窗口内没有命中关注主题的新闻）_

## 会议与活动（未来 120 天，日期以官网为准）

- **12-01**（32 天后）[MRS Fall Meeting](https://www.mrs.org/fall-meeting) — 材料计算与 AI 相关 session
- **12-08**（39 天后）[NeurIPS + ML4PS / AI4Science workshops](https://neurips.cc/) — 机器学习与物理科学交叉方法的最新动向

## 运行健康

| 数据源 | 抓取 | 状态 |
| --- | --- | --- |
| arxiv | 200 | ok |
| crossref | 136 | ok |
| openalex | 106 | ok |
| rss | 102 | ok |
| github | 1 | ok |

> 原始 545 → 去重 514 → 剔除标题噪声 44 → 低相关度 440 → 入库 30。

<sub>配置 `config/config.json` · 历史 `state/radar.sqlite3` · 重跑 `./run_daily.sh` · 调试 `python3 -m radar explain '标题'`</sub>
