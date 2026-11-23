# 科研雷达 · 2026-11-23（周一）

> 领域：计算化学 / 有机分子晶体结构预测、化学生成模型、有机铁电计算与手性分子晶体；低优先级跟踪视觉生成  
> 自动生成 12:48 · 抓取窗口 11-21 20:48 → 现在 · 候选 439 → 本轮入库 39 → 今日累计 **7**（本次 +0） · 来源 arxiv/crossref/openalex/rss/github

## 今日速览

- **最高相关度**：Generating grain boundary structures at a specified energy with a symmetry-constrained dif…（10.3）
- **本周条目最多**：机器学习势与通用势函数（MLIP / UMA）（31 篇）
- **构成**：化学相关生成模型（分子、材料与反应） 2 · 分子晶体结构预测（CSP）与能量图景 2 · 机器学习势与通用势函数（MLIP / UMA） 2 · 生成模型相关数学 1

## 今日最值得看

1. **[Generating grain boundary structures at a specified energy with a symmetry-constrained diffusion model](https://arxiv.org/abs/2611.27188)**
   `生成模型` `生成设计` `MLIP` · *arXiv* · 2026-11-20 · [PDF](https://arxiv.org/pdf/2611.27188)
   <sub>命中：generative models、diffusion model、inverse design、MatterGen、machine learning interatomic potential 等 7 个</sub>
   > Grain boundaries (GBs) govern many properties of polycrystalline materials, and inverse design would make the GB structure itself a design variable. Crystal generative models such as MatterGen operate on periodic cells, which contain two GBs.

2. **[Late-Time Dynamics of Flow Matching: Distance Geometry and Learning](https://arxiv.org/abs/2611.27653)**
   `生成数学` · *arXiv* · 2026-11-20 · [PDF](https://arxiv.org/pdf/2611.27653)
   <sub>命中：flow matching、score-based、wasserstein</sub>
   > Generative models transform simple random inputs into samples that resemble observed data. For a finite training set, a central question is how its geometry shapes the terminal dynamics and the probabilities assigned to individual samples.

3. **[Crystallization by Gas Blow Coating Enables the Free-Additive Tunable Morphology of l -Alanine](https://doi.org/10.1021/acs.cgd.6c01112)**
   `CSP` · *Crystal Growth & Design* · 2026-11-22
   <sub>命中：crystal structure、polymorph</sub>
   > l-alanine (C3H7NO2) is the simplest chiral amino acid, which can find applications in nonlinear optics, piezoelectric devices, radiation dosimetry, and as an additive in the food industry; hence, it is very important to find techniques to achieve l-alanine crystals with a well-defined structure and properties.

4. **[E2Former-V3: Atom-Role-Aware Equivariant Interatomic Potentials](https://arxiv.org/abs/2611.27111)**
   `MLIP` · *arXiv* · 2026-11-20 · [PDF](https://arxiv.org/pdf/2611.27111)
   <sub>命中：equivariant、omol25</sub>
   > Machine-learned interatomic potentials approach density-functional accuracy, but explicit-solvent atom counts are dominated by hydrogens and water. Uniform equivariant architectures still give every atom the same latent width and number of expensive block updates.

5. **[Pharos: Learning to Control Rare Events at Scale](https://arxiv.org/abs/2611.26765)**
   `MLIP` · *arXiv* · 2026-11-19 · [PDF](https://arxiv.org/pdf/2611.26765)
   <sub>命中：machine learning interatomic potential、interatomic potential</sub>
   > Rare events drive transformations across physics, chemistry and biology, yet predicting their mechanisms and rates remains a fundamental challenge. Here we introduce Pharos, a framework that learns to make rare transitions accessible while predicting how frequently they occur under physical dynamics.

6. **[Hierarchical Hybrid-Coordinate Flow Matching for Accurate and Physically Plausible Apo-to-Holo Protein Generation](https://arxiv.org/abs/2611.27162)**
   `生成模型` · *arXiv* · 2026-11-20 · [PDF](https://arxiv.org/pdf/2611.27162)
   <sub>命中：flow matching</sub>
   > Predicting holo-like protein conformations from apo structures is essential in structure-based drug design. Most existing apo-to-holo models operate in Cartesian space and achieve strong global accuracy. However, high global accuracy does not ensure physically valid local backbone geometry.

## 按主题展开

### 分子晶体结构预测（CSP）与能量图景 · 持平

- **[Professor Kevin Roberts’ Pathways Navigating the Intricate Interrelationships between Crystal Structure, Particles, Processes and Properties](https://doi.org/10.1021/acs.cgd.6c00700)**
  `CSP` · *Crystal Growth & Design* · 2026-11-22
  <sub>命中：crystal structure</sub>

## 工具与模型发布

_（窗口内没有关注工具的版本发布）_

## 领域新闻

_（窗口内没有命中关注主题的新闻）_

## 会议与活动（未来 120 天，日期以官网为准）

- **12-01**（8 天后）[MRS Fall Meeting](https://www.mrs.org/fall-meeting) — 材料计算与 AI 相关 session
- **12-08**（15 天后）[NeurIPS + ML4PS / AI4Science workshops](https://neurips.cc/) — 机器学习与物理科学交叉方法的最新动向
- **03-10**（107 天后）[APS March Meeting](https://www.aps.org/meetings/march) — 凝聚态/材料模拟大本营，MLIP 与晶体方法学分会场集中
- **03-20**（117 天后）[ACS Spring National Meeting](https://www.acs.org/meetings.html) — COMP 分会（计算化学）与晶体学相关 symposium

## 运行健康

| 数据源 | 抓取 | 状态 |
| --- | --- | --- |
| arxiv | 200 | ok |
| crossref | 58 | ok |
| openalex | 112 | ok |
| rss | 108 | ok |
| github | 0 | ok |

> 原始 478 → 去重 439 → 剔除标题噪声 21 → 低相关度 379 → 入库 39。

<sub>配置 `config/config.json` · 历史 `state/radar.sqlite3` · 重跑 `./run_daily.sh` · 调试 `python3 -m radar explain '标题'`</sub>
