# 科研雷达 · 2026-11-01（周日）

> 领域：计算化学 / 有机分子晶体结构预测、化学生成模型、有机铁电计算与手性分子晶体；低优先级跟踪视觉生成  
> 自动生成 09:08 · 抓取窗口 10-30 17:08 → 现在 · 候选 817 → 本轮入库 49 → 今日累计 **7**（本次 +1） · 来源 arxiv/crossref/openalex/rss/github

## 今日速览

- **最高相关度**：Decoding Hierarchical Crystal Packing in Phenprocoumon and Related 4-Hydroxycoumarins（19.7）
- **本周条目最多**：机器学习势与通用势函数（MLIP / UMA）（32 篇）
- **升温主题**：分子晶体结构预测（CSP）与能量图景、晶体生成模型与逆向设计、化学相关生成模型（分子、材料与反应）、视觉生成（低优先级）、生成模型相关数学、机器学习势与通用势函数（MLIP / UMA）、AI for Science 方法与自动化、铁电计算（有机与分子材料）
- **构成**：化学相关生成模型（分子、材料与反应） 3 · 分子晶体结构预测（CSP）与能量图景 2 · 机器学习势与通用势函数（MLIP / UMA） 2

## 今日最值得看

1. **[Decoding Hierarchical Crystal Packing in Phenprocoumon and Related 4-Hydroxycoumarins](https://doi.org/10.1021/acs.cgd.6c01430)**
   `CSP` · *Crystal Growth & Design* · 2026-10-31
   <sub>命中：crystal structure prediction (csp)、crystal structure prediction、crystal energy landscape、crystal structure、energy landscape 等 7 个</sub>
   > Polymorphism in flexible molecular systems arises from the interplay between molecular conformation, strong intermolecular interactions, and crystal packing. Here, a combined experimental and computational study of RS-phenprocoumon, encompassing multiple newly characterized solid forms, reveals a hierarchical organizat…

2. **[Accuracy, Reliability, and Efficiency of a MACE Machine-Learning Interatomic Potential for Aspirin: A Reproducible Benchmark for Molecular Simulation](https://doi.org/10.26434/chemrxiv.15011308/v1)**
   `MLIP` · *ChemRxiv* · 2026-10-30
   <sub>命中：machine learning interatomic potential、density functional theory、neural network potential、interatomic potential、equivariant 等 6 个</sub>
   > Machine-learning interatomic potentials (MLIPs) can reproduce density functional theory (DFT) energies and forces at a small fraction of the computational cost, yet an average benchmark error is an incomplete measure of their reliability in molecular simulation.

3. **[GCMDiff: a condition-guided diffusion framework for pharmacophore-fragment drug discovery and target-specific molecular design](https://doi.org/10.1186/s13321-026-01324-0)**
   `生成模型` · *Journal of Cheminformatics* · 2026-10-30
   <sub>命中：molecular generation、molecule generation、generative models、molecular design</sub>
   > Drug discovery remains a costly and time-consuming process, motivating the development of artificial intelligence approaches to accelerate molecular design. Many generative models, including generative pre-trained transformers (GPT), rely on one-dimensional SMILES representations that lack explicit structural topology…

4. **[AtomSteer: Test-Time Constraint Steering for Atomistic Generative Models](https://doi.org/10.48550/arxiv.2610.38517)**
   `生成模型` `生成设计` · *arXiv* · 2026-10-28
   <sub>命中：conformer generation、generative models、flow matching、de novo、crystal generation</sub>
   > Diffusion and flow matching models offer scalable approaches to generating crystalline materials, molecular conformers, and protein-ligand complexes. However, satisfying crystallographic symmetry, structural geometry, and accurate stereochemistry remains challenging.

5. **[Logical Guidance of Stochastic Interpolants](https://doi.org/10.48550/arxiv.2610.38648)**
   `生成模型` · *arXiv* · 2026-10-28
   <sub>命中：generative models、diffusion models、flow matching、score-based</sub>
   > Guidance and composition of generative models have applications in visual design, chemistry, and biology. Logical guidance composes conditional scores exactly for diffusion models. However, Flow Matching (FM) and Stochastic Interpolants (SI) learn velocity fields.

6. **[Field‐Driven Proton Transport in Water Revealed by Machine Learning Molecular Dynamics](https://doi.org/10.1002/advs.78513)**
   `MLIP` · *Advanced Science* · 2026-10-29
   <sub>命中：machine learning interatomic potential、interatomic potential</sub>
   > Excess-proton transport in water arises from the coupling of proton transfer (PT), hydrogen-bond rearrangement, and solvent polarization. While equilibrium Grotthuss diffusion has been widely studied, its response under strong electric fields remains difficult to resolve because simulations must capture both chemical r…

## 按主题展开

### 分子晶体结构预测（CSP）与能量图景 · 升温 ↑2.4×

- **[The role of solid-melt interfaces in self-catalyzed growth kinetics of III-nitride semiconductors](https://doi.org/10.1038/s41524-026-02371-9)**
  `CSP` · *npj Computational Materials* · 2026-10-30 · 多源×3
  <sub>命中：energy landscape</sub>
  > Solid-melt interfaces govern metal-mediated epitaxy of gallium nitride (GaN) and related III-nitride semiconductors, yet a quantitative connection between interfacial structure and growth kinetics has…

## 工具与模型发布

_（窗口内没有关注工具的版本发布）_

## 领域新闻

_（窗口内没有命中关注主题的新闻）_

## 会议与活动（未来 120 天，日期以官网为准）

- **12-01**（30 天后）[MRS Fall Meeting](https://www.mrs.org/fall-meeting) — 材料计算与 AI 相关 session
- **12-08**（37 天后）[NeurIPS + ML4PS / AI4Science workshops](https://neurips.cc/) — 机器学习与物理科学交叉方法的最新动向

## 运行健康

| 数据源 | 抓取 | 状态 |
| --- | --- | --- |
| arxiv | 629 | ok |
| crossref | 86 | ok |
| openalex | 112 | ok |
| rss | 104 | ok |
| github | 0 | ok |

> 原始 931 → 去重 817 → 剔除标题噪声 46 → 低相关度 722 → 入库 49。

<sub>配置 `config/config.json` · 历史 `state/radar.sqlite3` · 重跑 `./run_daily.sh` · 调试 `python3 -m radar explain '标题'`</sub>
