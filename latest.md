# 科研雷达 · 2026-11-26（周四）

> 领域：计算化学 / 有机分子晶体结构预测、化学生成模型、有机铁电计算与手性分子晶体；低优先级跟踪视觉生成  
> 自动生成 12:08 · 抓取窗口 11-24 20:08 → 现在 · 候选 962 → 本轮入库 62 → 今日累计 **19**（本次 +4） · 来源 arxiv/crossref/openalex/rss/github

## 今日速览

- **最高相关度**：Machine Learning Interatomic Potentials and Agentic AI as Enabling Tools for the Computati…（10.6）
- **本周条目最多**：机器学习势与通用势函数（MLIP / UMA）（34 篇）
- **构成**：机器学习势与通用势函数（MLIP / UMA） 14 · 化学相关生成模型（分子、材料与反应） 5

## 今日最值得看

1. **[Machine Learning Interatomic Potentials and Agentic AI as Enabling Tools for the Computational Study of Metal-Organic Frameworks’ Self-Assembly](https://doi.org/10.7274/35018608)**
   `MLIP` · *University of Notre Dame* · 2026-11-24
   <sub>命中：equivariant、fine-tuning、allegro、mlip、mace</sub>
   > Metal-organic frameworks (MOFs) are porous, crystalline materials whose exceptional tunability has enabled applications across gas storage and separation, heterogeneous catalysis, and drug delivery.

2. **[Temporal Selective Exploration for Reinforcement Learning-Guided Continuous-Discrete Flow Matching in 3D Molecular Design](https://arxiv.org/abs/2611.33417)**
   `生成模型` · *arXiv* · 2026-11-24 · [PDF](https://arxiv.org/pdf/2611.33417)
   <sub>命中：molecular design、flow matching、de novo</sub>
   > Flow matching has shown strong potential in generative tasks, while its optimization via Reinforcement Learning (RL) remains underexplored, especially in continuous-discrete mixed settings.

3. **[A general-purpose electron density model for molecular chemistry](https://arxiv.org/abs/2611.34732)**
   `MLIP` · *arXiv* · 2026-11-25 · 👤Michele Ceriotti · [PDF](https://arxiv.org/pdf/2611.34732)
   <sub>命中：density functional theory、omol25</sub>
   > Universal machine-learning potentials predict molecular structure and stability at the accuracy of quantum mechanics, for a fraction of the cost. Properties derived instead from knowledge of the electronic structure give profound insights into chemical reactivity, but are not accessible with the same ease or transferab…

4. **[Reward Tilting via Semantic Noising](https://doi.org/10.48550/arxiv.2611.29318)**
   `生成模型` · *arXiv* · 2026-11-22
   <sub>命中：generative model、diffusion model、autoregressive</sub>
   > Steering a generative model toward a desired property typically requires separate fine-tuning for each reward or additional computation during sampling. We propose semantic noising, which conditions generation on a noisy semantic representation of the data.

5. **[PerovAgent: Autonomous Ligand Design for Halide Perovskite Nanocrystals](https://arxiv.org/abs/2611.33913)**
   `MLIP` `AI4S` · *arXiv* · 2026-11-25 · [PDF](https://arxiv.org/pdf/2611.33913)
   <sub>命中：machine-learned interatomic potential、density functional theory、interatomic potential、large language model、autonomous 等 7 个</sub>
   > Designing surface-capping ligands for high-performance halide perovskite nanocrystals requires navigating a vast molecular space while discovering design rules that govern ligand-surface interactions.

6. **[PineIR: 3D molecular structures from an infrared spectrum alone](https://arxiv.org/abs/2611.34334)**
   `MLIP` · *arXiv* · 2026-11-25 · [PDF](https://arxiv.org/pdf/2611.34334)
   <sub>命中：machine-learned interatomic potential、interatomic potential、fine-tuning</sub>
   > Computing the infrared (IR) spectrum of a molecule from its structure is routine. The inverse problem is not. In practice, IR spectra are used to identify the functional groups present in a molecule, while the determination of its complete structure requires additional measurements.

## 按主题展开

### 化学相关生成模型（分子、材料与反应） · 持平

- **[DiffER$^2$: Diffusion Ensembles for Retrosynthesis Prediction with SMILES Adapted Particle Guidance](https://arxiv.org/abs/2611.33557)**
  `生成模型` · *arXiv* · 2026-11-25 · [PDF](https://arxiv.org/pdf/2611.33557)
  <sub>命中：molecular generation、diffusion models</sub>
  > Computational retrosynthesis prediction has the potential to reduce development time for newly discovered drugs by automatically generating potential reactions for a target product.

- **[CrysLDM: Latent Diffusion Model for Crystal Material Generation](https://doi.org/10.48550/arxiv.2611.29675)**
  `生成模型` `生成设计` · *arXiv* · 2026-11-22
  <sub>命中：diffusion models、diffusion model、variational autoencoder</sub>
  > Generating new crystal materials with desirable chemical properties has long been a challenging task. Existing diffusion models operate in feature space, requiring complex diffusion architectures to m…

- **[SilicoDock: physics-constrained diffusion sampling and surface-based mixture-density scoring for accurate and physically valid molecular docking](https://doi.org/10.1039/d6cp03972c)**
  `生成模型` · *Physical Chemistry Chemical Physics* · 2026-11-23
  <sub>命中：diffusion model</sub>
  > Molecular docking underpins structure-based drug discovery but is limited by two coupled subproblems: classical programs rank poses with hand-built scoring functions of limited transferability, wherea…

### 机器学习势与通用势函数（MLIP / UMA） · 持平

- **[A data-efficient machine-learning approach for modeling the photodynamics of all- trans hexatriene based on multireference configuration interaction calculations](https://doi.org/10.1039/d6fd00061d)**
  `MLIP` · *Faraday Discussions* · 2027-01-01
  <sub>命中：active learning、mlip</sub>
  > Accurate simulations of excited-state photodynamics of polyenes remain challenging due to the high computational cost of multireference electronic-structure methods required to describe the coexistenc…

- **[MolGPAO: Molecular Generative Pre-trained Autoregressive Octree with Speculative Decoding and Sub-Millisecond Seam Healing for 3D Molecules](https://arxiv.org/abs/2611.33985)**
  `MLIP` · *arXiv* · 2026-11-25 · [PDF](https://arxiv.org/pdf/2611.33985)
  <sub>命中：equivariant、mlip</sub>
  > Autoregressive generation over adaptive 3D octrees (Uni-3DAR) offers an intrinsic $O(N \log N)$ sparsity advantage over dense $O(N^2)$ equivariant diffusion and flow models on large drug-like molecule…

- **[Neighbor-Graph Truncation and Density Shift in Equivariant Direct-Hessian Potentials: Diagnosis, Controls, and Mitigation](https://doi.org/10.26434/chemrxiv.15012005/v2)**
  `MLIP` · *ChemRxiv* · 2026-11-23
  <sub>命中：equivariant、mace</sub>
  > Direct prediction of molecular Hessians with SE(3)-equivariant graph neural networks avoids the O(3N ) automatic-differentiation cost of scalar machine learning interatomic potentials, yet extrapolati…

- **[Geometry Sets the Neutral MLIP-DFT Gap in Non-Covalent Binding, and Charged Systems Fail](https://arxiv.org/abs/2611.33830)**
  `MLIP` · *arXiv* · 2026-11-25 · [PDF](https://arxiv.org/pdf/2611.33830)
  <sub>命中：fine-tuning、mlip</sub>
  > Pretrained universal machine-learning interatomic potentials (MLIPs) are widely expected to substitute for explicit quantum chemistry when screening molecular interactions.

- **[ILMlip: fast and universal machine-learning interatomic potentials](https://arxiv.org/abs/2611.33538)**
  `MLIP` · *arXiv* · 2026-11-24 · [PDF](https://arxiv.org/pdf/2611.33538)
  <sub>命中：equivariant、fine-tuning、mace</sub>
  > Large-scale pretrained machine-learned interatomic potentials keep growing more accurate as new models appear at a rapid pace, and more expensive: the current leader of Matbench Discovery as of Novemb…

- **[OrbACE: Orbital and Atomic Cluster Expansion](https://arxiv.org/abs/2611.33743)**
  `MLIP` · *arXiv* · 2026-11-25 · [PDF](https://arxiv.org/pdf/2611.33743)
  <sub>命中：equivariant、mace</sub>
  > Accurate electronic-structure reference data are expensive, motivating interatomic potentials that learn effectively from limited training sets.

- **[Foundation interatomic potentials capture structural disorder in metallic glasses](https://arxiv.org/abs/2611.34156)**
  `MLIP` · *arXiv* · 2026-11-25 · [PDF](https://arxiv.org/pdf/2611.34156)
  <sub>命中：density functional theory、fine-tuning、mace</sub>
  > Foundation machine-learning interatomic potentials transfer well across chemical and structural space, yet their reliability for highly disordered metallic states is less established.

## 工具与模型发布

_（窗口内没有关注工具的版本发布）_

## 领域新闻

_（窗口内没有命中关注主题的新闻）_

## 关注课题组的新作

- [A general-purpose electron density model for molecular chemistry](https://arxiv.org/abs/2611.34732) — *arXiv* · 2026-11-25（Michele Ceriotti）

## 会议与活动（未来 120 天，日期以官网为准）

- **12-01**（5 天后）[MRS Fall Meeting](https://www.mrs.org/fall-meeting) — 材料计算与 AI 相关 session
- **12-08**（12 天后）[NeurIPS + ML4PS / AI4Science workshops](https://neurips.cc/) — 机器学习与物理科学交叉方法的最新动向
- **03-10**（104 天后）[APS March Meeting](https://www.aps.org/meetings/march) — 凝聚态/材料模拟大本营，MLIP 与晶体方法学分会场集中
- **03-20**（114 天后）[ACS Spring National Meeting](https://www.acs.org/meetings.html) — COMP 分会（计算化学）与晶体学相关 symposium

## 运行健康

| 数据源 | 抓取 | 状态 |
| --- | --- | --- |
| arxiv | 742 | ok |
| crossref | 138 | ok |
| openalex | 116 | ok |
| rss | 101 | ok |
| github | 0 | ok |

> 原始 1097 → 去重 962 → 剔除标题噪声 30 → 低相关度 870 → 入库 62。

<sub>配置 `config/config.json` · 历史 `state/radar.sqlite3` · 重跑 `./run_daily.sh` · 调试 `python3 -m radar explain '标题'`</sub>
