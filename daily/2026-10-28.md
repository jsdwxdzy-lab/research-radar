# 科研雷达 · 2026-10-28（周三）

> 领域：计算化学 / 有机分子晶体，以及生成模型、视觉生成与相关数学  
> 自动生成 09:32 · 抓取窗口 10-26 17:32 → 现在 · 候选 876 → 本轮入库 56 → 今日累计 **19**（本次 +19） · 来源 arxiv/crossref/openalex/rss/github

## 今日速览

- **最高相关度**：Semi-automated workflow to predict polymorph energies as a function of size [software]（18.2）
- **本周条目最多**：视觉生成（32 篇）
- **升温主题**：分子晶体结构预测（CSP）与能量图景、生成模型与逆向设计、生成模型、新模型与新架构、视觉生成、生成模型相关数学、机器学习势与通用势函数（MLIP / UMA）
- **构成**：视觉生成 6 · 分子晶体结构预测（CSP）与能量图景 4 · 机器学习势与通用势函数（MLIP / UMA） 4 · 生成模型、新模型与新架构 3 · 生成模型相关数学 2

## 今日最值得看

1. **[Semi-automated workflow to predict polymorph energies as a function of size [software]](https://doi.org/10.15128/r2ww72bb57x)**
   `CSP` · *Durham Research Online (Durham University)* · 2026-10-23
   <sub>命中：crystal structure prediction、molecular crystals、molecular crystal、crystal structure、lattice energy 等 7 个</sub>
   > The stability of molecular crystal polymorphs is conventionally predicted from lattice energies alone. This description breaks down at the nanoscale, where surface contributions become comparable to bulk lattice energy differences and can reverse polymorph stability.

2. **[Lattice free energies of molecular crystals using normalizing flow](https://doi.org/10.1038/s41524-026-02290-9)**
   `CSP` · *npj Computational Materials* · 2026-10-27 · 多源×2
   <sub>命中：crystal structure prediction、molecular crystals、crystal structure</sub>
   > Accurate free-energy calculations are essential for predicting thermodynamic stability in complex molecular materials, such as the polymorphic crystal landscapes of pharmaceutical molecules.

3. **[Nemotron-Labs-Diffusion-Uni: Elastic Self-Refining Unified Diffusion LLM with Cross-Paradigm On-Policy Distillation](https://arxiv.org/abs/2610.36466)**
   `视觉生成` · *arXiv* · 2026-10-27 · [PDF](https://arxiv.org/pdf/2610.36466)
   <sub>命中：visual generation、image generation、text-to-image</sub>
   > We propose Nemotron-Labs-Diffusion-Uni (NLD-Uni), a unified discrete diffusion large language model (DLLM) for visual understanding and generation tasks. Compared with prior unified diffusion models, NLD-Uni introduces two major innovations.

4. **[Chemical Similarity Enables a Unified Free-Energy Framework for f -Block Solvation Thermodynamics](https://doi.org/10.1021/acs.jctc.6c01464)**
   `MLIP` · *Journal of Chemical Theory and Computation* · 2026-10-27
   <sub>命中：interatomic potential、fine-tuning、mace</sub>
   > f-Block elements underpin many essential technologies, yet their efficient mutual separation remains a foundational challenge in chemistry. The lanthanide series provide a stringent test case: the trivalent lanthanide ions (Ln3+) exhibit near-identical solvation chemistry across the series, distinguished only by the la…

5. **[TAPESTRY: A Single Backbone for Video Generation and Robot Control](https://arxiv.org/abs/2610.36823)**
   `视觉生成` · *arXiv* · 2026-10-27 · [PDF](https://arxiv.org/pdf/2610.36823)
   <sub>命中：video generation、video diffusion</sub>
   > Pretrained video generation models encode rich priors about physical interactions, but leveraging them for robot control typically requires either resource-intensive video generation at test time or action heads trained from scratch that do not fully utilize the pretrained backbone.

6. **[Cross-modal Steering Vectors Exist Across Both Image and Text Generation](https://arxiv.org/abs/2610.36269)**
   `视觉生成` · *arXiv* · 2026-10-26 · [PDF](https://arxiv.org/pdf/2610.36269)
   <sub>命中：image generation、text-to-image</sub>
   > Are concepts and mechanisms unified across modalities in current AI models, or instead implemented separately for each one? We operationalize this broad question of modality unification by studying cross-modal steering: 1) finding vectors that successfully steer generation on tokens of one modality, which then 2) trans…

## 按主题展开

### 分子晶体结构预测（CSP）与能量图景 · 升温 ↑6.7×

- **[Designing Geared Molecular Rotors in Flexible Metal-Organic Frameworks](https://arxiv.org/abs/2610.36647)**
  `CSP` · *arXiv* · 2026-10-27 · 👤Jack D. Evans · [PDF](https://arxiv.org/pdf/2610.36647)
  <sub>命中：energy landscape</sub>
  > Translating macroscopic mechanical concepts such as gears to the molecular scale offers a route to precise control over nanoscale motion, inspired by the efficiency of biological machines.

- **[Fracture Mechanics and Self-Healing in Molecular Crystal Resonators for Lasing](https://arxiv.org/abs/2610.36692)**
  `CSP` · *arXiv* · 2026-10-27 · [PDF](https://arxiv.org/pdf/2610.36692)
  <sub>命中：molecular crystal</sub>
  > Microscale damage poses a significant challenge to the reliability and longevity of miniaturized photonic devices; however, the mechanisms and repair of microscopic cracks and fractures in organic opt…

### 生成模型、新模型与新架构 · 升温 ↑6.6×

- **[HELICS: Biobank-scale Conditional Synthetic Genome Generation via Latent Flow Matching](https://arxiv.org/abs/2610.36361)**
  `生成模型` · *arXiv* · 2026-10-26 · [PDF](https://arxiv.org/pdf/2610.36361)
  <sub>命中：flow matching</sub>
  > Individual-level genotype data underpin genetic discovery, disease-risk modeling, and therapeutic development, yet many critical settings remain data-limited, including underrepresented ancestries, ra…

- **[SpeeDiff: Scalable Pixel-Anchored End-to-End Latent Diffusion Model](https://arxiv.org/abs/2610.36419)**
  `生成模型` `视觉生成` · *arXiv* · 2026-10-26 · [PDF](https://arxiv.org/pdf/2610.36419)
  <sub>命中：diffusion model、latent diffusion</sub>
  > We present Scalable Pixel-anchored End-to-end Diffusion (SpeeDiff), a latent diffusion method that jointly trains the VAE and the diffusion model from scratch.

- **[TOPS: Reshaping Flow Source and Transport for Multi-Task Robot Manipulation](https://arxiv.org/abs/2610.36694)**
  `生成模型` · *arXiv* · 2026-10-27 · [PDF](https://arxiv.org/pdf/2610.36694)
  <sub>命中：flow matching</sub>
  > Flow-based policies for language-conditioned multi-task manipulation commonly share a single $\textit{Gaussian}$ source prior and a common linear transport path across tasks.

### 视觉生成 · 升温 ↑9.3×

- **[Beyond the Estimate: Wiener-Informed Decoding for Easier Training of Pixel-Space Flow Models](https://arxiv.org/abs/2610.36192)**
  `视觉生成` · *arXiv* · 2026-10-26 · [PDF](https://arxiv.org/pdf/2610.36192)
  <sub>命中：image generation、text-to-image</sub>
  > Learning velocity fields directly in pixel space is difficult and slow. We show that coarse second-order image statistics can ease this task: frozen Wiener estimates improve velocity learning, with ga…

- **[Haste Makes Waste? Towards Safe Few-Step Text-to-Image Models](https://arxiv.org/abs/2610.36665)**
  `视觉生成` · *arXiv* · 2026-10-27 · [PDF](https://arxiv.org/pdf/2610.36665)
  <sub>命中：text-to-image</sub>
  > While few-step distilled text-to-image models have gained traction due to their fast generation times, the speed-up implications on their unsafe generation rates remain unknown.

- **[FrameForge: Harnessing Priors of Video Foundation Models for Unified Image Generation](https://arxiv.org/abs/2610.36545)**
  `视觉生成` · *arXiv* · 2026-10-27 · [PDF](https://arxiv.org/pdf/2610.36545)
  <sub>命中：image generation</sub>
  > Unified conditional image generation requires a single model to preserve different aspects of a visual input while producing a target image that follows textual guidance.

### 生成模型相关数学 · 升温 ↑3.0×

- **[DeepMuon: generating cosmic-ray Muons based on optimal transport](https://doi.org/10.1088/1361-6471/aeb958)**
  `生成数学` · *Journal of Physics G Nuclear and Particle Phys…* · 2026-10-26
  <sub>命中：optimal transport、wasserstein</sub>
  > Deep learning can learn distributions directly from data, enabling fast event simulation without hand-crafted designs or costly sampling.

- **[Second-order Sinkhorn Geometry and $\sqrt{n}$-Inference](https://arxiv.org/abs/2610.36488)**
  `生成数学` · *arXiv* · 2026-10-27 · [PDF](https://arxiv.org/pdf/2610.36488)
  <sub>命中：optimal transport、wasserstein</sub>
  > The Sinkhorn divergence, a debiased form of entropic optimal transport, has been widely used in various scientific disciplines due to its computational and statistical tractability.

### 机器学习势与通用势函数（MLIP / UMA） · 升温 ↑6.2×

- **[Spin-Charge Conversion in an Epitaxial Kagome Flat-Band Metal](https://arxiv.org/abs/2610.36501)**
  `MLIP` · *arXiv* · 2026-10-27 · 👤Erin R. Johnson · [PDF](https://arxiv.org/pdf/2610.36501)
  <sub>命中：density functional theory</sub>
  > The formation of topological flat bands near the Fermi level in kagome-structured metals has generated substantial research interest.

- **[Extended Active Learning-Guided Design of Multi-Component Electrolytes with Opposing Cosolvent Properties for Aqueous Zinc-Ion Batteries](https://doi.org/10.1021/jacs.6c20703)**
  `MLIP` · *Journal of the American Chemical Society* · 2026-10-27
  <sub>命中：active learning</sub>
  > Multi-component electrolytes offer expanded tunability over electrochemical properties, yet their rational design is constrained by a lack of generalizable principles.

- **[When do machine-learning potentials need a configuration-dependent kernel? Learning long-range interactions with Fourier neural operators](https://doi.org/10.26434/chemrxiv.15011048/v1)**
  `MLIP` · *ChemRxiv* · 2026-10-26
  <sub>命中：density functional theory、mace</sub>
  > Long-range interactions in machine-learning interatomic potentials are commonly treated by coupling learned sources through either a prescribed electrostatic kernel or a learned but configurationindep…

## 工具与模型发布

_（窗口内没有关注工具的版本发布）_

## 领域新闻

_（窗口内没有命中关注主题的新闻）_

## 关注课题组的新作

- [Designing Geared Molecular Rotors in Flexible Metal-Organic Frameworks](https://arxiv.org/abs/2610.36647) — *arXiv* · 2026-10-27（Jack D. Evans）
- [Spin-Charge Conversion in an Epitaxial Kagome Flat-Band Metal](https://arxiv.org/abs/2610.36501) — *arXiv* · 2026-10-27（Erin R. Johnson）

## 会议与活动（未来 120 天，日期以官网为准）

- **12-01**（34 天后）[MRS Fall Meeting](https://www.mrs.org/fall-meeting) — 材料计算与 AI 相关 session
- **12-08**（41 天后）[NeurIPS + ML4PS / AI4Science workshops](https://neurips.cc/) — 机器学习与物理科学交叉方法的最新动向

## 运行健康

| 数据源 | 抓取 | 状态 |
| --- | --- | --- |
| arxiv | 643 | ok |
| crossref | 144 | ok |
| openalex | 118 | ok |
| rss | 61 | ok |
| github | 3 | ok |

> 原始 969 → 去重 876 → 剔除标题噪声 48 → 低相关度 772 → 入库 56。

<sub>配置 `config/config.json` · 历史 `state/radar.sqlite3` · 重跑 `./run_daily.sh` · 调试 `python3 -m radar explain '标题'`</sub>
