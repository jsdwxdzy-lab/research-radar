# 科研雷达 · 2026-10-27（周二）

> 领域：计算化学 / 有机分子晶体，以及生成模型、视觉生成与相关数学  
> 自动生成 10:21 · 抓取窗口 10-25 18:21 → 现在 · 候选 781 → 本轮入库 51 → 今日累计 **12**（本次 +12） · 来源 arxiv/crossref/openalex/rss/github

## 今日速览

- **最高相关度**：TCSP3.0: Template-Based Crystal Structure Prediction with Coefficient-Preserving Element S…（8.8）
- **本周条目最多**：生成模型、新模型与新架构（25 篇）
- **升温主题**：分子晶体结构预测（CSP）与能量图景、生成模型与逆向设计、生成模型、新模型与新架构、视觉生成、生成模型相关数学、机器学习势与通用势函数（MLIP / UMA）
- **构成**：生成模型、新模型与新架构 6 · 视觉生成 3 · 分子晶体结构预测（CSP）与能量图景 1 · 生成模型相关数学 1 · AI for Science 方法与自动化 1

## 今日最值得看

1. **[TCSP3.0: Template-Based Crystal Structure Prediction with Coefficient-Preserving Element Substitution and Structural Diversity](https://arxiv.org/abs/2610.34029)**
   `CSP` · *arXiv* · 2026-10-25 · [PDF](https://arxiv.org/pdf/2610.34029)
   <sub>命中：crystal structure prediction (csp)、crystal structure prediction、crystal structure</sub>
   > Template-based crystal structure prediction (CSP) transfers a known crystal structure to a new composition by element substitution, so its accuracy depends on retrieving suitable templates, mapping elements and ranking the resulting candidates correctly.

2. **[Climate downscaling with likelihood functional flow matching](https://arxiv.org/abs/2610.33482)**
   `生成模型` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33482)
   <sub>命中：diffusion model、flow matching</sub>
   > Decisions about heat, frost and flooding are made locally, yet reanalyses and climate models resolve tens of kilometres. Generative downscalers add kilometre-scale detail with uncertainty, but are tied to a grid, costly to sample and lack a tractable likelihood.

3. **[How Geometry Shapes Generative Model Evaluation on Riemannian Manifolds](https://arxiv.org/abs/2610.33731)**
   `生成模型` `生成数学` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33731)
   <sub>命中：generative model、flow matching、wasserstein</sub>
   > On Riemannian manifolds, generative-model evaluation is geometry-dependent since curvature and dimension jointly determine distances and volume growth. Our framework systematically compares geodesic, ambient, and tangent-space versions of Wasserstein and MMD across different geometries.

4. **[Semantic-First MixGRPO: Reliable Emotional Image Generation via Temporal Decoupling](https://arxiv.org/abs/2610.33460)**
   `视觉生成` `生成数学` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33460)
   <sub>命中：image generation、image synthesis、stochastic differential、probability flow</sub>
   > Controllable image synthesis should modify visual affect without replacing the objects, layout, or relations specified by a prompt. Existing methods address this tension through conditioning architectures or auxiliary losses, while mixed ordinary differential equation (ODE) and stochastic differential equation (SDE) sa…

5. **[Learning Population Dynamics with Variational Doob-Wasserstein Flow](https://arxiv.org/abs/2610.33922)**
   `生成数学` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33922)
   <sub>命中：schrödinger bridge、wasserstein</sub>
   > This paper introduces a novel simulation-free framework for learning unbalanced population dynamics on the Riemannian Wasserstein-Fisher-Rao (WFR) manifold, termed Variational Doob-Wasserstein Flow (VDWF), built upon the theory of the unbalanced mean-field Schrödinger bridge (MFSB).

6. **[Rectified Language Flow](https://arxiv.org/abs/2610.33811)**
   `生成模型` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33811)
   <sub>命中：rectified flow、autoregressive</sub>
   > Continuous-state flow and diffusion models offer a promising approach to fast, parallel language generation, but matching the generation quality of autoregressive models remains challenging.

## 按主题展开

### 生成模型、新模型与新架构 · 升温 ↑8.1×

- **[Mix Forcing: Causal Pre-Training via Mixture Attention for Interactive World Models](https://arxiv.org/abs/2610.33589)**
  `生成模型` `视觉生成` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33589)
  <sub>命中：diffusion model、autoregressive、video diffusion</sub>
  > While interactive video world models require autoregressive generation, directly adapting pretrained bidirectional video diffusion models into autoregressive ones with teacher forcing can disrupt thei…

- **[H-GLow: Accelerating Graph Generation via Hazard-Guided Discrete Flow Matching](https://arxiv.org/abs/2610.33599)**
  `生成模型` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33599)
  <sub>命中：flow matching</sub>
  > Discrete flow matching (DFM) offers a promising approach to graph generation; however, generating high-quality graphs with few steps remains challenging due to the strong dependencies between nodes an…

- **[Nowcasting aerosol particle size distributions from PM2.5 with physics-regularized flow matching](https://arxiv.org/abs/2610.33557)**
  `生成模型` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33557)
  <sub>命中：flow matching</sub>
  > The mass concentration of particles smaller than 2.5um (PM2.5) is cheap to measure and widely monitored, whereas the particle number size distribution (PSD) requires costly instruments and is measured…

### 视觉生成 · 升温 ↑5.2×

- **[Qwen-Image-PE: Learning Visual Design for Text-to-Image Prompt Enhancement](https://arxiv.org/abs/2610.33472)**
  `视觉生成` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33472)
  <sub>命中：text-to-image</sub>
  > Learning visual design is essential for prompt enhancement (PE) to turn underspecified user requests into coherent visual specifications for text-to-image (T2I) generation.

- **[Whispers from the Neighbors: Rethinking Caption Consensus as Inference-Time Evidence for Vision-Language Retrieval](https://arxiv.org/abs/2610.33798)**
  `视觉生成` · *arXiv* · 2026-10-24 · [PDF](https://arxiv.org/pdf/2610.33798)
  <sub>命中：text-to-image</sub>
  > An image is rarely described only once. Retrieval benchmarks and many collections attach several captions to each picture, yet dual encoders still judge every image-caption pair in isolation.

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
| arxiv | 633 | ok |
| crossref | 84 | ok |
| openalex | 121 | ok |
| rss | 44 | ok |
| github | 1 | ok |

> 原始 883 → 去重 781 → 剔除标题噪声 48 → 低相关度 682 → 入库 51。

<sub>配置 `config/config.json` · 历史 `state/radar.sqlite3` · 重跑 `./run_daily.sh` · 调试 `python3 -m radar explain '标题'`</sub>
