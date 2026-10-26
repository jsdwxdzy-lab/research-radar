# 科研雷达 · 2026-10-26（周一）

> 领域：计算化学 / 有机分子晶体，以及生成模型、视觉生成与相关数学  
> 自动生成 23:30 · 抓取窗口 10-25 07:30 → 现在 · 候选 819 → 本轮入库 67 → 今日累计 **73**（本次 +50） · 来源 arxiv/crossref/openalex/rss/github

## 今日速览

- **最高相关度**：Structure and Stability Prediction of Binary and Ternary Molecular Mixed Crystals Using En…（10.8）
- **本周条目最多**：生成模型、新模型与新架构（23 篇）
- **构成**：生成模型、新模型与新架构 24 · 视觉生成 17 · 机器学习势与通用势函数（MLIP / UMA） 16 · 生成模型相关数学 8 · 生成模型与逆向设计 4 · 分子晶体结构预测（CSP）与能量图景 3 · other 1

## 今日点评

> 今天最值得看的是第1条：它结合CSP、力场晶格能与晶格动力学、Δ-ML能量校正和缩放配分函数，用代表性取代超胞系综估算蒽/吖啶/吩嗪二元、三元混晶的组成依赖自由能，直接对应你关注的固溶与能量图景，可借鉴为稳定性评估流程。其次是第2条Orbitol：它以Wyckoff轨道为token，按指定空间群生成晶体，是无机晶体生成方向的对标工作。它的对称性约束思路能否迁移到分子晶体的分子位点，是值得追的线索。

## 今日最值得看

1. **[Structure and Stability Prediction of Binary and Ternary Molecular Mixed Crystals Using Ensemble Free Energies](https://doi.org/10.1021/acs.cgd.6c00999)**
   `CSP` · *Crystal Growth & Design* · 2026-10-22 · 👤Graeme M. Day
   <sub>命中：crystal structure prediction、crystal structure、lattice energy</sub>
   > Mixed crystals provide a route to tune the properties of molecular solids through continuous changes in composition. However, predicting their stability is challenging because it requires determining both substitution energies and configurational entropy across large configuration spaces.

2. **[Automatically Building and Updating a Knowledge Graph of MLIP Models](https://hal.science/hal-05785570)**
   `MLIP` · *HAL* · 2026-10-25
   <sub>命中：machine learning interatomic potential、interatomic potential、mlip</sub>
   > Complementing the many efforts in providing semantic representations of concepts, notions, and entities in materials science, we report and illustrate a process by which we can automatically build a knowledge graph of the fast evolving field of machine learning applied to the prediction of material properties, focusing…

3. **[Machine‐Learning‐Potential‐Driven Volcano Relationship in Grain Boundary Amorphicity and Ionic Transport of Antiperovskite Solid Electrolytes](https://doi.org/10.1002/adma.75492)**
   `MLIP` · *Advanced Materials* · 2026-10-23
   <sub>命中：machine learning interatomic potential、interatomic potential、mlip</sub>
   > Ionic transport in solid‐state electrolytes is governed by interfacial disorder and local chemical environments, yet their microscopic design principles remain challenging because large‐scale interfacial kinetics are simulated using molecular dynamics (MD), where predictive design requires quantum‐level accuracy.

4. **[Orbitol: Crystal Generation on Wyckoff Orbits](https://arxiv.org/abs/2610.30086)**
   `生成设计` · *arXiv* · 2026-10-21
   <sub>命中：crystal generation、generative models、symmetry-aware、wyckoff</sub>
   > Generative models propose crystalline materials by learning composition and geometry, but unconditional sampling gives no direct control over the space group, which constrains whether responses such as piezoelectricity are symmetry-allowed.

5. **[CrystalAR: Autoregressive Modeling for Symmetric Crystal Generation](https://arxiv.org/abs/2610.27762)**
   `生成设计` `CSP` · *arXiv* · 2026-10-20
   <sub>命中：crystal generation、generative models、de novo、wyckoff、crystal structure prediction (csp) 等 8 个</sub>
   > Deep generative modeling has achieved remarkable progress in crystal generation. Given the rich symmetries inherent in crystalline structures, recent work has sought to explicitly incorporate space-group symmetry into generative models, enabling more effective exploration of novel symmetry templates.

6. **[Machine Learning-Assisted Discovery of Carbon-Related Defect Formation Mechanisms in Diamond](https://arxiv.org/abs/2610.26301)**
   `MLIP` · *arXiv* · 2026-10-19
   <sub>命中：machine learning interatomic potential、density functional theory、interatomic potential、mlip</sub>
   > Diamond is an important host material for functional defects such as solid-state spin qubits. During the defect creation by irradiation and subsequent thermal annealing, carbon-related defects, including vacancies and interstitials, are generated and can migrate to form new defect complexes.

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

- **[PCFBench: How Far Can Large Vision-Language Models Go in Physics-aware Photonic Inverse Design?](https://arxiv.org/abs/2610.32485)**
  `生成设计` · *arXiv* · 2026-10-23 · [PDF](https://arxiv.org/pdf/2610.32485)
  <sub>命中：inverse design</sub>
  > Photonic crystal fibers (PCFs) underpin critical applications in telecommunications, sensing, and high-power laser delivery, yet their design remains a manual, expert-intensive process that couples ge…

### 生成模型、新模型与新架构

- **[Anomaly Detection using Source-Reversed Flow Matching](https://hal.science/hal-05769855v1)**
  `生成模型` · *HAL* · 2026-10-24
  <sub>命中：diffusion transformer、flow matching</sub>
  > Anomaly detection in textual data remains an underexplored problem, hindered by fragmented benchmarks, scarce labeled data, and methods that fail to model the distribution of normal text in a continuo…

- **[TokenFlow: Latent Token Rectified Flow Matching for 3D Point Cloud Generation](https://arxiv.org/abs/2610.27418)**
  `生成模型` · *arXiv* · 2026-10-20
  <sub>命中：rectified flow、flow matching</sub>
  > 3D point clouds generation requires capturing both part-level layout and surface detail while preserving permutation equivariance.

- **[Generative Flow-Matching Priors from Segmentation-Based Inversion for Uncertainty Quantification](https://doi.org/10.63929/22020586.2026.1.053)**
  `生成模型` · *ASEG Extended Abstracts* · 2026-10-21
  <sub>命中：generative model、flow matching</sub>
  > A framework that leverages segmentation methods for geophysical inversion to construct geologic priors for probabilistic inversion is presented.

- **[PnP-CF: A Consensus Flow-Matching Solver for General Inverse Problems](https://arxiv.org/abs/2610.26000)**
  `生成模型` · *arXiv* · 2026-10-19
  <sub>命中：generative model、flow matching</sub>
  > Plug-and-Play (PnP) methods using continuous-time deep generative models as learned data distribution priors enable synthesizing high-quality solutions of model-based inverse problems.

- **[ROCOCO: Robust Outline Completion of Occluded Curvilinear Objects](https://arxiv.org/abs/2610.29177)**
  `生成模型` · *arXiv* · 2026-10-21
  <sub>命中：generative model、flow matching</sub>
  > We propose a learning-based generative model for completing curvilinear features under occlusion by environmental obstacles.

- **[If at First You Don't Succeed, Backtrack: Lightweight Recovery for Frozen VLAs](https://arxiv.org/abs/2610.32941)**
  `生成模型` · *arXiv* · 2026-10-23 · [PDF](https://arxiv.org/pdf/2610.32941)
  <sub>命中：autoregressive、flow matching</sub>
  > Vision-Language-Action (VLA) models perform well on robotic manipulation, yet remain brittle once their own actions carry them into states their training data barely covers.

- **[ViT-H: Generative Video-To-Humanoid Control with Motion Tracking Feedback](https://arxiv.org/abs/2610.32966)**
  `生成模型` · *arXiv* · 2026-10-23 · [PDF](https://arxiv.org/pdf/2610.32966)
  <sub>命中：diffusion model、autoregressive</sub>
  > Learning humanoid control from monocular human videos offers a scalable way to acquire diverse whole-body behaviors.

### 视觉生成

- **[RANANO-Recreating Nano Banana Using Diffusion Model](https://doi.org/10.59256/indjcst.20260503043)**
  `视觉生成` · *Indian Journal of Computer Science and Technol…* · 2026-10-22
  <sub>命中：image generation、video generation、text-to-image</sub>
  > RANANO is an integrated artificial intelligence-based multimedia creation platform developed to combine multiple creative functionalities within a single web-based interface.

- **[MoDDiT: Simple Token Routing in Diffusion Transformers](https://arxiv.org/abs/2610.28086)**
  `视觉生成` · *arXiv* · 2026-10-20
  <sub>命中：image generation、video generation、image synthesis</sub>
  > Real-time video generation, interactive world models, and on-device image synthesis are almost a reality. Diffusion Transformers (DiT) achieve excellent sample quality, shifting the bottleneck to the…

- **[ImageRSI: Verification-Driven Recursive Self-Improvement for Agentic Image Generation](https://arxiv.org/abs/2610.32120)**
  `视觉生成` · *arXiv* · 2026-10-23 · [PDF](https://arxiv.org/pdf/2610.32120)
  <sub>命中：image generation、text-to-image</sub>
  > Complex text-to-image requests remain difficult to satisfy reliably. Verifying and repairing an image can fix an individual output, but a successful repair does not necessarily carry over to other req…

- **[PhysCorr-Dataset](https://doi.org/10.57760/sciencedb.016kt)**
  `视觉生成` · *ScienceDB* · 2026-10-19
  <sub>命中：video generation、text-to-video</sub>
  > we propose PhysCorr, a unified framework for modeling, evaluating, and optimizing physical consistency in text-to-video generation.

- **[Making MLLM Latents Matter: Factor-Aware Predictive Learning for Cinematic Video Generation](https://arxiv.org/abs/2610.30926)**
  `视觉生成` · *arXiv* · 2026-10-22
  <sub>命中：video generation、video diffusion</sub>
  > Cinematic video generation requires both temporal inference from limited inputs (i.e., sparse rather than frame-by-frame guidance) and factor-aware control of character, scene, action, and camera.

- **[Dynamics-Aware Sparse Attention for Efficient Autoregressive Video Diffusion](https://arxiv.org/abs/2610.26262)**
  `视觉生成` · *arXiv* · 2026-10-19
  <sub>命中：video generation、video diffusion</sub>
  > Autoregressive Diffusion Transformers have emerged as a powerful paradigm for long video generation. However, they are often constrained by prohibitive computational overhead and substantial memory fo…

- **[JUICE: Unified Multimodal Modeling in Pretrained Representation Spaces](https://arxiv.org/abs/2610.28801)**
  `视觉生成` · *arXiv* · 2026-10-20
  <sub>命中：image generation、text-to-image</sub>
  > Most unified multimodal models treat images and text asymmetrically: a pretrained language model generates text, an attached diffusion head generates images, and outputs that contain both are produced…

### 生成模型相关数学

- **[Optimal-transport flow matching for stochastic model ipdating](https://doi.org/10.17877/tudobooks-11.158)**
  `生成数学` `生成模型` · *Technische Universität Dortmund Eldorado (Tech…* · 2026-12-01
  <sub>命中：optimal transport、flow matching</sub>
  > Deep generative models have attracted considerable attention as inference engines for stochastic model updating.

- **[Density-Level Backward Error for Low-NFE Generative Flows](https://arxiv.org/abs/2610.29475)**
  `生成数学` · *arXiv* · 2026-10-21 · [PDF](https://arxiv.org/pdf/2610.29475)
  <sub>命中：optimal transport、probability flow、wasserstein</sub>
  > Low-NFE generative ODE sampling is constrained not only by solver order, but also by how a fixed budget of network evaluations is distributed along the flow.

- **[Representation Learning via Composite Subspace Flow Matching](https://arxiv.org/abs/2610.32256)**
  `生成数学` `生成模型` · *arXiv* · 2026-10-23 · [PDF](https://arxiv.org/pdf/2610.32256)
  <sub>命中：optimal transport、flow matching</sub>
  > Distilling semantic meaning from raw image data remains a challenge in machine learning. Current self-supervised paradigms face a trade-off: joint-embedding architectures produce relevant features by…

- **[Disentangling total-variance and signal-to-noise-ratio improves diffusion models](https://doi.org/10.1088/2632-2153/aeb69d)**
  `生成数学` `生成模型` · *Machine Learning Science and Technology* · 2026-10-20
  <sub>命中：optimal transport、flow matching</sub>
  > Diffusion models have been widely adopted as a powerful generative framework across numerous scientific domains, yet their inherently iterative sampling process remains a significant computational bot…

- **[Lifting PCA in the Wasserstein Space](https://arxiv.org/abs/2610.29679)**
  `生成数学` · *arXiv* · 2026-10-21 · [PDF](https://arxiv.org/pdf/2610.29679)
  <sub>命中：optimal transport、wasserstein</sub>
  > Principal Component Analysis (PCA) is a fundamental tool for statistical dimension reduction, yet no canonical extension to distribution-valued data has emerged within the framework of optimal transpo…

- **[Generative Modeling via Nonlinear Schrödinger Bridges and Branching Diffusions](https://arxiv.org/abs/2610.29476)**
  `生成数学` · *arXiv* · 2026-10-21 · [PDF](https://arxiv.org/pdf/2610.29476)
  <sub>命中：schrödinger bridge、score-based</sub>
  > We propose a new generative modeling framework grounded in forward-backward partial differential equations (PDEs).

- **[Stabilizing Filters for Graph Signal Generation](https://arxiv.org/abs/2610.28318)**
  `生成数学` · *arXiv* · 2026-10-20 · [PDF](https://arxiv.org/pdf/2610.28318)
  <sub>命中：schrödinger bridge、wasserstein</sub>
  > Generating graph signals is an important task in machine learning, and incorporating the underlying graph into a generative model enables structurally-informed distribution modeling.

### 机器学习势与通用势函数（MLIP / UMA）

- **[Symmetry-Based Parameter Efficient Low-Rank Fine-Tuning for High-Throughput Calculation of Lattice Thermal Conductivity](https://arxiv.org/abs/2610.29634)**
  `MLIP` · *arXiv* · 2026-10-21 · [PDF](https://arxiv.org/pdf/2610.29634)
  <sub>命中：machine-learned interatomic potential、interatomic potential、fine-tuning、mattersim</sub>
  > Accurate and efficient prediction of lattice thermal conductivity (LTC) is essential for developing materials for thermoelectric, microelectronic, and photovoltaic applications.

- **[Unconstrained learning of equivariant atomistic properties](https://arxiv.org/abs/2610.31183)**
  `MLIP` · *arXiv* · 2026-10-22 · 👤Michele Ceriotti · [PDF](https://arxiv.org/pdf/2610.31183) · 多源×2
  <sub>命中：potential energy surface、equivariant</sub>
  > Machine-learned interatomic potentials based on graph neural networks (GNNs) have made first-principles accuracy routine for the potential energy surface (PES).

- **[Mechanistic Insights of Jahn–Teller Effect Suppression in High-Entropy Prussian Blue Analogue Cathodes](https://doi.org/10.1021/jacs.6c15227)**
  `MLIP` · *Journal of the American Chemical Society* · 2026-10-23
  <sub>命中：machine learning interatomic potential、interatomic potential</sub>
  > The Jahn–Teller (J-T) effect, as discovered by Hermann Jahn and Edward Teller in 1937, often causes lattice distortion and structural instability in Mn-based battery materials.

- **[Atomic-scale mechanisms of SiO2 plasma-enhanced chemical vapor deposition revealed by molecular dynamics with a machine-learning interatomic potential](https://doi.org/10.1016/j.apsusc.2026.168654)**
  `MLIP` · *Applied Surface Science* · 2026-10-21
  <sub>命中：machine learning interatomic potential、interatomic potential</sub>

- **[Combining Simulations and Spectroscopy to Design Protective Coatings on Sulfide Solid Electrolytes](https://arxiv.org/abs/2610.32905)**
  `MLIP` · *arXiv* · 2026-10-23 · 👤Michele Ceriotti · [PDF](https://arxiv.org/pdf/2610.32905)
  <sub>命中：interatomic potential</sub>
  > Sulfide solid electrolytes are attractive for all-solid-state batteries because of their high Li-ion conductivity and favorable processability, but their practical use is limited by electrochemical in…

- **[Mechanical versus thermal amorphization of ZIF-4: from local rearrangements to network disorder](https://doi.org/10.26434/chemrxiv.15010773/v1)**
  `MLIP` · *ChemRxiv* · 2026-10-21
  <sub>命中：machine learning interatomic potential、interatomic potential</sub>
  > There is mounting evidence that different amorphization routes can produce metalorganic framework (MOF) glasses with distinct structures and properties, yet the microscopic origins of these difference…

- **[Microscopic origin of polytype-dependent melting in SiC revealed by machine-learning molecular dynamics](https://doi.org/10.1063/5.0350682)**
  `MLIP` · *The Journal of Chemical Physics* · 2026-10-19
  <sub>命中：interatomic potential、mace</sub>
  > Predicting how crystal structure influences high-temperature stability remains a key challenge in materials modeling and design.

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
| arxiv | 642 | ok |
| crossref | 67 | ok |
| openalex | 127 | ok |
| rss | 75 | ok |
| github | 1 | ok |

> 原始 912 → 去重 819 → 剔除标题噪声 46 → 低相关度 706 → 入库 67。

<sub>配置 `config/config.json` · 历史 `state/radar.sqlite3` · 重跑 `./run_daily.sh` · 调试 `python3 -m radar explain '标题'`</sub>
