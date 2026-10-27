# 科研雷达 · 2026-10-27（周二）

> 领域：计算化学 / 有机分子晶体，以及生成模型、视觉生成与相关数学  
> 自动生成 14:20 · 抓取窗口 10-25 22:20 → 现在 · 候选 807 → 本轮入库 59 → 今日累计 **31**（本次 +19） · 来源 arxiv/crossref/openalex/rss/github

## 今日速览

- **最高相关度**：Retention-constrained fine-tuning of a pre-trained aluminium MACE potential for non-equili…（11.3）
- **本周条目最多**：生成模型、新模型与新架构（30 篇）
- **升温主题**：分子晶体结构预测（CSP）与能量图景、生成模型与逆向设计、生成模型、新模型与新架构、视觉生成、生成模型相关数学、机器学习势与通用势函数（MLIP / UMA）
- **构成**：视觉生成 13 · 生成模型、新模型与新架构 11 · 机器学习势与通用势函数（MLIP / UMA） 4 · 分子晶体结构预测（CSP）与能量图景 1 · 生成模型相关数学 1 · AI for Science 方法与自动化 1

## 今日最值得看

1. **[Retention-constrained fine-tuning of a pre-trained aluminium MACE potential for non-equilibrium defect dynamics and plasticity](https://arxiv.org/abs/2610.35653)**
   `MLIP` · *arXiv* · 2026-10-26 · [PDF](https://arxiv.org/pdf/2610.35653)
   <sub>命中：machine learning interatomic potential、density functional theory、interatomic potential、active learning、fine-tuning 等 6 个</sub>
   > Adapting a pre-trained machine-learning interatomic potential for non-equilibrium defect dynamics and plasticity requires improving defect accuracy without degrading the near-equilibrium elastic and vibrational response.

2. **[TCSP3.0: Template-Based Crystal Structure Prediction with Coefficient-Preserving Element Substitution and Structural Diversity](https://arxiv.org/abs/2610.34029)**
   `CSP` · *arXiv* · 2026-10-25 · [PDF](https://arxiv.org/pdf/2610.34029)
   <sub>命中：crystal structure prediction (csp)、crystal structure prediction、crystal structure</sub>
   > Template-based crystal structure prediction (CSP) transfers a known crystal structure to a new composition by element substitution, so its accuracy depends on retrieving suitable templates, mapping elements and ranking the resulting candidates correctly.

3. **[Synthesis-by-design of ferroelectric Dion–Jacobson two-dimensional hybrid organic–inorganic perovskites](https://doi.org/10.1038/s41467-026-78928-5)**
   `MLIP` · *Nature Communications* · 2026-10-27
   <sub>命中：machine-learned interatomic potential、interatomic potential</sub>
   > Dion–Jacobson two-dimensional hybrid organic–inorganic perovskites are promising ferroelectric materials, combining chemically tunable polarity enabled by their organic spacers with enhanced environmental stability.

4. **[Climate downscaling with likelihood functional flow matching](https://arxiv.org/abs/2610.33482)**
   `生成模型` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33482)
   <sub>命中：diffusion model、flow matching</sub>
   > Decisions about heat, frost and flooding are made locally, yet reanalyses and climate models resolve tens of kilometres. Generative downscalers add kilometre-scale detail with uncertainty, but are tied to a grid, costly to sample and lack a tractable likelihood.

5. **[Beyond Distribution Matching: Self-Supervised Representation Forcing for Few-Step Video Generation](https://arxiv.org/abs/2610.35594)**
   `视觉生成` · *arXiv* · 2026-10-26 · [PDF](https://arxiv.org/pdf/2610.35594)
   <sub>命中：video generation、video diffusion</sub>
   > Few-step distillation is essential for deploying modern video diffusion models. Among existing approaches, Distribution Matching Distillation (DMD) has emerged as a highly promising paradigm by achieving strong output-space fidelity without adversarial training, while remaining flexible across various student architect…

6. **[How Geometry Shapes Generative Model Evaluation on Riemannian Manifolds](https://arxiv.org/abs/2610.33731)**
   `生成模型` `生成数学` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33731)
   <sub>命中：generative model、flow matching、wasserstein</sub>
   > On Riemannian manifolds, generative-model evaluation is geometry-dependent since curvature and dimension jointly determine distances and volume growth. Our framework systematically compares geodesic, ambient, and tangent-space versions of Wasserstein and MMD across different geometries.

## 按主题展开

### 生成模型、新模型与新架构 · 升温 ↑9.6×

- **[Active Learning of Conditional Generative Models via the Transport Neural Tangent Kernel](https://arxiv.org/abs/2610.35652)**
  `生成模型` `生成数学` · *arXiv* · 2026-10-26 · [PDF](https://arxiv.org/pdf/2610.35652)
  <sub>命中：generative model、flow matching、wasserstein</sub>
  > Many high-throughput scientific experiments produce distributional outputs, requiring conditional generative models to interpret the data, and to predict outcomes at new inputs.

- **[Generative Structure from Motion with Native 3D Diffusion](https://arxiv.org/abs/2610.35522)**
  `生成模型` · *arXiv* · 2026-10-26 · [PDF](https://arxiv.org/pdf/2610.35522)
  <sub>命中：diffusion transformer、diffusion model</sub>
  > Recovering an object's 3D structure and camera motion from a few uncalibrated views is a fundamental problem in computer vision.

- **[Rectified Language Flow](https://arxiv.org/abs/2610.33811)**
  `生成模型` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33811)
  <sub>命中：rectified flow、autoregressive</sub>
  > Continuous-state flow and diffusion models offer a promising approach to fast, parallel language generation, but matching the generation quality of autoregressive models remains challenging.

- **[Mix Forcing: Causal Pre-Training via Mixture Attention for Interactive World Models](https://arxiv.org/abs/2610.33589)**
  `生成模型` `视觉生成` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33589)
  <sub>命中：diffusion model、autoregressive、video diffusion</sub>
  > While interactive video world models require autoregressive generation, directly adapting pretrained bidirectional video diffusion models into autoregressive ones with teacher forcing can disrupt thei…

- **[NOMAD-EEG: Native Omni-Montage Adaptive Diffusion](https://arxiv.org/abs/2610.35246)**
  `生成模型` · *arXiv* · 2026-10-26 · [PDF](https://arxiv.org/pdf/2610.35246)
  <sub>命中：foundation model、diffusion model</sub>
  > Purpose. Electroencephalography (EEG) montages, channel counts and recording lengths vary widely, but most EEG foundation models are bound to the channel set and input length they were trained on.

- **[H-GLow: Accelerating Graph Generation via Hazard-Guided Discrete Flow Matching](https://arxiv.org/abs/2610.33599)**
  `生成模型` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33599)
  <sub>命中：flow matching</sub>
  > Discrete flow matching (DFM) offers a promising approach to graph generation; however, generating high-quality graphs with few steps remains challenging due to the strong dependencies between nodes an…

- **[Nowcasting aerosol particle size distributions from PM2.5 with physics-regularized flow matching](https://arxiv.org/abs/2610.33557)**
  `生成模型` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33557)
  <sub>命中：flow matching</sub>
  > The mass concentration of particles smaller than 2.5um (PM2.5) is cheap to measure and widely monitored, whereas the particle number size distribution (PSD) requires costly instruments and is measured…

### 视觉生成 · 升温 ↑8.4×

- **[S$^2$-RL: Sample-Set Dual Reinforcement Learning for Generative Semantic Segmentation Dataset Distillation](https://arxiv.org/abs/2610.35491)**
  `视觉生成` · *arXiv* · 2026-10-26 · [PDF](https://arxiv.org/pdf/2610.35491)
  <sub>命中：image generation、text-to-image</sub>
  > While dataset distillation has witnessed significant advances in image classification, its extension to dense prediction tasks such as semantic segmentation is plagued by two core bottlenecks: bi-leve…

- **[Semantic-First MixGRPO: Reliable Emotional Image Generation via Temporal Decoupling](https://arxiv.org/abs/2610.33460)**
  `视觉生成` `生成数学` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33460)
  <sub>命中：image generation、image synthesis、stochastic differential、probability flow</sub>
  > Controllable image synthesis should modify visual affect without replacing the objects, layout, or relations specified by a prompt.

- **[Qwen-Image-PE: Learning Visual Design for Text-to-Image Prompt Enhancement](https://arxiv.org/abs/2610.33472)**
  `视觉生成` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33472)
  <sub>命中：text-to-image</sub>
  > Learning visual design is essential for prompt enhancement (PE) to turn underspecified user requests into coherent visual specifications for text-to-image (T2I) generation.

- **[Triage: Skip, Skim, or Refine Attention Tiles in Video Diffusion Transformers](https://arxiv.org/abs/2610.35706)**
  `视觉生成` · *arXiv* · 2026-10-26 · [PDF](https://arxiv.org/pdf/2610.35706)
  <sub>命中：video diffusion</sub>
  > Attention over tens of thousands of visual tokens dominates the inference of video diffusion transformers (DiTs).

- **[VibeVideoBench:Evaluating Multimodal Agents on Code-Driven Video Generation](https://arxiv.org/abs/2610.35864)**
  `视觉生成` · *arXiv* · 2026-10-26 · [PDF](https://arxiv.org/pdf/2610.35864)
  <sub>命中：video generation</sub>
  > Diffusion video models produce striking clips, but they cannot reliably render an exact formula, a correct chart, a ruleconsistent game or narration synchronized to on-screen events.

- **[VidEdit3D: Flexible 3D Gaussian Editing with Video Diffusion](https://arxiv.org/abs/2610.35756)**
  `视觉生成` · *arXiv* · 2026-10-26 · [PDF](https://arxiv.org/pdf/2610.35756)
  <sub>命中：video diffusion</sub>
  > Recent advancements in text-guided 3D editing, particularly with 3D Gaussian Splatting (3DGS), have shown promise but still lag behind the flexibility of 2D editing tools.

- **[OmniShowcase: Omnidirectional Subject-Consistent Video Generation from Multi-View Images](https://arxiv.org/abs/2610.35684)**
  `视觉生成` · *arXiv* · 2026-10-26 · [PDF](https://arxiv.org/pdf/2610.35684)
  <sub>命中：video generation</sub>
  > Generating videos of a specific subject from a few reference images remains challenging when the camera reveals surfaces that are not visible in the input.

### 生成模型相关数学 · 升温 ↑8.1×

- **[Learning Population Dynamics with Variational Doob-Wasserstein Flow](https://arxiv.org/abs/2610.33922)**
  `生成数学` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33922)
  <sub>命中：schrödinger bridge、wasserstein</sub>
  > This paper introduces a novel simulation-free framework for learning unbalanced population dynamics on the Riemannian Wasserstein-Fisher-Rao (WFR) manifold, termed Variational Doob-Wasserstein Flow (V…

### 机器学习势与通用势函数（MLIP / UMA） · 升温 ↑13.7×

- **[Accelerating SO(2)-Equivariant Materials Models through Low-Precision Emulation](https://arxiv.org/abs/2610.35164)**
  `MLIP` · *arXiv* · 2026-10-26 · [PDF](https://arxiv.org/pdf/2610.35164)
  <sub>命中：equivariant、mlip</sub>
  > Rotationally equivariant architectures improve the physical fidelity of machine-learned (ML) universal materials models based on graph neural networks (GNNs).

- **[Multi-Fidelity Training Reshapes Uncertainty Decomposition in Atomistic Models](https://arxiv.org/abs/2610.35560)**
  `MLIP` · *arXiv* · 2026-10-26 · [PDF](https://arxiv.org/pdf/2610.35560)
  <sub>命中：fine-tuning、mace</sub>
  > Multi-fidelity training, which combines abundant low-fidelity data with scarce high-fidelity labels, is increasingly common in atomistic modeling, but its effect on predictive uncertainty remains larg…

### AI for Science 方法与自动化 · 新增关注

- **[MatOS: An Agent Operating System for Materials Research](https://arxiv.org/abs/2610.34203)**
  `AI4S` · *arXiv* · 2026-10-25 · [PDF](https://arxiv.org/pdf/2610.34203)
  <sub>命中：large language model、autonomous、agent</sub>
  > Materials research relies on scattered and growing data, knowledge, and simulation tools, and a single study often spans multi-day workflows across literature analysis, computation, and experiment.

## 工具与模型发布

_（窗口内没有关注工具的版本发布）_

## 领域新闻

_（窗口内没有命中关注主题的新闻）_

## 会议与活动（未来 120 天，日期以官网为准）

- **12-01**（35 天后）[MRS Fall Meeting](https://www.mrs.org/fall-meeting) — 材料计算与 AI 相关 session
- **12-08**（42 天后）[NeurIPS + ML4PS / AI4Science workshops](https://neurips.cc/) — 机器学习与物理科学交叉方法的最新动向

## 运行健康

| 数据源 | 抓取 | 状态 |
| --- | --- | --- |
| arxiv | 642 | ok |
| crossref | 93 | ok |
| openalex | 121 | ok |
| rss | 40 | ok |
| github | 1 | ok |

> 原始 897 → 去重 807 → 剔除标题噪声 46 → 低相关度 702 → 入库 59。

<sub>配置 `config/config.json` · 历史 `state/radar.sqlite3` · 重跑 `./run_daily.sh` · 调试 `python3 -m radar explain '标题'`</sub>
