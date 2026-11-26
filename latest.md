# 科研雷达 · 2026-11-26（周四）

> 领域：计算化学 / 有机分子晶体结构预测、化学生成模型、有机铁电计算与手性分子晶体；低优先级跟踪视觉生成  
> 自动生成 09:08 · 抓取窗口 11-24 17:08 → 现在 · 候选 913 → 本轮入库 54 → 今日累计 **7**（本次 +0） · 来源 arxiv/crossref/openalex/rss/github

## 今日速览

- **最高相关度**：Machine Learning Interatomic Potentials and Agentic AI as Enabling Tools for the Computati…（10.6）
- **本周条目最多**：机器学习势与通用势函数（MLIP / UMA）（24 篇）
- **构成**：机器学习势与通用势函数（MLIP / UMA） 4 · 化学相关生成模型（分子、材料与反应） 3

## 今日最值得看

1. **[Machine Learning Interatomic Potentials and Agentic AI as Enabling Tools for the Computational Study of Metal-Organic Frameworks’ Self-Assembly](https://doi.org/10.7274/35018608)**
   `MLIP` · *University of Notre Dame* · 2026-11-24
   <sub>命中：equivariant、fine-tuning、allegro、mlip、mace</sub>
   > Metal-organic frameworks (MOFs) are porous, crystalline materials whose exceptional tunability has enabled applications across gas storage and separation, heterogeneous catalysis, and drug delivery.

2. **[Reward Tilting via Semantic Noising](https://doi.org/10.48550/arxiv.2611.29318)**
   `生成模型` · *arXiv* · 2026-11-22
   <sub>命中：generative model、diffusion model、autoregressive</sub>
   > Steering a generative model toward a desired property typically requires separate fine-tuning for each reward or additional computation during sampling. We propose semantic noising, which conditions generation on a noisy semantic representation of the data.

3. **[CrysLDM: Latent Diffusion Model for Crystal Material Generation](https://doi.org/10.48550/arxiv.2611.29675)**
   `生成模型` `生成设计` · *arXiv* · 2026-11-22
   <sub>命中：diffusion models、diffusion model、variational autoencoder</sub>
   > Generating new crystal materials with desirable chemical properties has long been a challenging task. Existing diffusion models operate in feature space, requiring complex diffusion architectures to model the joint distribution of atom types, coordinates, and lattice structures.

4. **[A data-efficient machine-learning approach for modeling the photodynamics of all- trans hexatriene based on multireference configuration interaction calculations](https://doi.org/10.1039/d6fd00061d)**
   `MLIP` · *Faraday Discussions* · 2027-01-01
   <sub>命中：active learning、mlip</sub>
   > Accurate simulations of excited-state photodynamics of polyenes remain challenging due to the high computational cost of multireference electronic-structure methods required to describe the coexistence of ionic and covalent states.

5. **[Neighbor-Graph Truncation and Density Shift in Equivariant Direct-Hessian Potentials: Diagnosis, Controls, and Mitigation](https://doi.org/10.26434/chemrxiv.15012005/v2)**
   `MLIP` · *ChemRxiv* · 2026-11-23
   <sub>命中：equivariant、mace</sub>
   > Direct prediction of molecular Hessians with SE(3)-equivariant graph neural networks avoids the O(3N ) automatic-differentiation cost of scalar machine learning interatomic potentials, yet extrapolating from small training molecules (N ≤ 22) to compact conformers (N = 30-100) exposes severe local coordination density s…

6. **[SilicoDock: physics-constrained diffusion sampling and surface-based mixture-density scoring for accurate and physically valid molecular docking](https://doi.org/10.1039/d6cp03972c)**
   `生成模型` · *Physical Chemistry Chemical Physics* · 2026-11-23
   <sub>命中：diffusion model</sub>
   > Molecular docking underpins structure-based drug discovery but is limited by two coupled subproblems: classical programs rank poses with hand-built scoring functions of limited transferability, whereas deep learning models generate poses rapidly but often chemically invalid ones.

## 按主题展开

### 机器学习势与通用势函数（MLIP / UMA） · 持平

- **[Constrained Multipole Moment Density Functional Theory for the Charge-Transfer and Polarization Contributions in Non-Covalent Complexes](https://doi.org/10.1021/acs.jctc.6c01487)**
  `MLIP` · *Journal of Chemical Theory and Computation* · 2026-11-25
  <sub>命中：density functional theory</sub>
  > The constrained multipole moment density functional theory allows the control of the dipole, quadrupole, and octupole moments in a variational and nonempirical way.

## 工具与模型发布

_（窗口内没有关注工具的版本发布）_

## 领域新闻

_（窗口内没有命中关注主题的新闻）_

## 会议与活动（未来 120 天，日期以官网为准）

- **12-01**（5 天后）[MRS Fall Meeting](https://www.mrs.org/fall-meeting) — 材料计算与 AI 相关 session
- **12-08**（12 天后）[NeurIPS + ML4PS / AI4Science workshops](https://neurips.cc/) — 机器学习与物理科学交叉方法的最新动向
- **03-10**（104 天后）[APS March Meeting](https://www.aps.org/meetings/march) — 凝聚态/材料模拟大本营，MLIP 与晶体方法学分会场集中
- **03-20**（114 天后）[ACS Spring National Meeting](https://www.acs.org/meetings.html) — COMP 分会（计算化学）与晶体学相关 symposium

## 运行健康

| 数据源 | 抓取 | 状态 |
| --- | --- | --- |
| arxiv | 694 | ok |
| crossref | 133 | ok |
| openalex | 116 | ok |
| rss | 100 | ok |
| github | 0 | ok |

> 原始 1043 → 去重 913 → 剔除标题噪声 34 → 低相关度 825 → 入库 54。

<sub>配置 `config/config.json` · 历史 `state/radar.sqlite3` · 重跑 `./run_daily.sh` · 调试 `python3 -m radar explain '标题'`</sub>
