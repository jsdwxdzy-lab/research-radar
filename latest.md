# 科研雷达 · 2026-11-16（周一）

> 领域：计算化学 / 有机分子晶体结构预测、化学生成模型、有机铁电计算与手性分子晶体；低优先级跟踪视觉生成  
> 自动生成 17:33 · 抓取窗口 11-15 01:33 → 现在 · 候选 769 → 本轮入库 33 → 今日累计 **11**（本次 +1） · 来源 arxiv/crossref/openalex/rss/github

## 今日速览

- **最高相关度**：Classifier-Guided Latent Diffusion for Small-Molecule Generation（13.2）
- **本周条目最多**：机器学习势与通用势函数（MLIP / UMA）（22 篇）
- **构成**：分子晶体结构预测（CSP）与能量图景 3 · 生成模型相关数学 2 · 机器学习势与通用势函数（MLIP / UMA） 2 · 化学相关生成模型（分子、材料与反应） 1 · 晶体生成模型与逆向设计 1 · 手性分子与分子晶体 1 · AI for Science 方法与自动化 1

## 今日最值得看

1. **[Classifier-Guided Latent Diffusion for Small-Molecule Generation](https://arxiv.org/abs/2611.17650)**
   `生成模型` · *arXiv* · 2026-11-13 · [PDF](https://arxiv.org/pdf/2611.17650)
   <sub>命中：molecule generation、generative models、diffusion models、molecular design、diffusion model</sub>
   > Diffusion models have emerged as a promising class of generative models for molecular design because of their ability to learn complex chemical distributions and support conditional or guided generation. In this work, we investigate a latent diffusion pipeline for property-guided small-molecule generation.

2. **[Crystal Structure Prediction from Search to Learning: A 30-Year Expedition](https://arxiv.org/abs/2611.17670)**
   `CSP` · *arXiv* · 2026-11-13 · [PDF](https://arxiv.org/pdf/2611.17670)
   <sub>命中：crystal structure prediction (csp)、crystal structure prediction、molecular crystals、crystal structure、energy landscape</sub>
   > Crystal structure prediction (CSP) determines periodic atomic or molecular arrangements from chemical composition and physical conditions. Over three decades, CSP has evolved from chemical construction and global energy optimization to hybrid approaches combining symmetry, learned potentials, adaptive search, and deep…

3. **[CGTransformer: A Topology-Aware Autoregressive Framework for Crystal Generation and Inverse Design](https://arxiv.org/abs/2611.18303)**
   `CSP` `生成设计` `生成模型` · *arXiv* · 2026-11-13 · [PDF](https://arxiv.org/pdf/2611.18303)
   <sub>命中：crystal structure prediction (csp)、crystal structure prediction、crystal structure、crystal generation、inverse design 等 6 个</sub>
   > Autoregressive language models offer a unified route to crystal generation and inverse design, but their performance depends on how periodic structures are serialized. Symmetry equivalent and closely related crystals can receive different atomic orders under coordinate-based serialization, introducing variability unrel…

4. **[Diffusion Tree Sampling for Inference Time Adaptation of Crystal Generative Models](https://arxiv.org/abs/2611.17462)**
   `生成设计` `生成模型` · *arXiv* · 2026-11-12 · [PDF](https://arxiv.org/pdf/2611.17462)
   <sub>命中：crystal generation、generative models、de novo</sub>
   > Diffusion-based generative models have become strong priors over plausible crystal structures, but turning that prior into promising candidates requires steering toward several conflicting properties at once.

5. **[Score-based neural ordinary differential equations for reaction-diffusions](https://arxiv.org/abs/2611.18467)**
   `生成数学` · *arXiv* · 2026-11-13 · [PDF](https://arxiv.org/pdf/2611.18467)
   <sub>命中：probability flow、score-based、wasserstein</sub>
   > A diffusion equation can be rewritten as a transport equation driven by the score function of the evolving density. Conventional probability-flow formulations, which move particles deterministically with this score-driven velocity, typically conserve total mass.

6. **[Highly Tunable Metal-Peptide Piezoelectrics for Tissue Regeneration](https://doi.org/10.1021/jacs.6c13664)**
   `手性晶体` · *Journal of the American Chemical Society* · 2026-11-16
   <sub>命中：enantiomeric、chirality</sub>
   > Piezoelectricity, first discovered in 1880, has been dominated by inorganic materials, whose strong electromechanical responses typically arise from achiral, noncentrosymmetric crystal structures and highly polar bonds.

## 按主题展开

### 分子晶体结构预测（CSP）与能量图景 · 持平

- **[Pressure-driven evolution of crystal and molecular structures reshapes excited-state competition in coronene](https://arxiv.org/abs/2611.17698)**
  `CSP` · *arXiv* · 2026-11-13 · [PDF](https://arxiv.org/pdf/2611.17698)
  <sub>命中：crystal packing、polymorphism</sub>
  > Molecular nanocarbons exhibit unique optoelectronic properties and considered as promising candidates for organic device applications, however, understanding how molecular geometry and crystal packing…

### 生成模型相关数学 · 回落 ↓0.4×

- **[Elliptic Sampling: Optimal Interpolant Schedules for Gaussians and Beyond](https://arxiv.org/abs/2611.18542)**
  `生成数学` · *arXiv* · 2026-11-13 · [PDF](https://arxiv.org/pdf/2611.18542)
  <sub>命中：probability flow、wasserstein</sub>
  > Generative modeling based on stochastic interpolants requires specifying two key choices: an interpolant schedule bridging the initial and target distributions, and an efficient discretization of the…

### 机器学习势与通用势函数（MLIP / UMA） · 持平

- **[Electric Fields Turn Vacancy-trapping Grain Boundaries into Li-Ion Pathways in Li2O](https://arxiv.org/abs/2611.17679)**
  `MLIP` · *arXiv* · 2026-11-13 · [PDF](https://arxiv.org/pdf/2611.17679)
  <sub>命中：machine learning interatomic potential、interatomic potential</sub>
  > Ion transport in solids has conventionally been understood from equilibrium diffusion, yet ions in batteries are driven by electric fields.

- **[Fine-tuned atomistic foundation model for accurate sodium-carbon chemistry in Na-ion batteries](https://arxiv.org/abs/2611.18490)**
  `MLIP` · *arXiv* · 2026-11-13 · [PDF](https://arxiv.org/pdf/2611.18490)
  <sub>命中：fine-tuning、mace</sub>
  > Atomistic foundation models have emerged as a promising route to DFT-level accuracy for materials simulation with complex chemical environments.

### AI for Science 方法与自动化 · 回落 ↓0.5×

- **[Verifiable pXRD: Hill-climbing pXRD structure determination with LLM agents](https://arxiv.org/abs/2611.17539)**
  `AI4S` · *arXiv* · 2026-11-12 · [PDF](https://arxiv.org/pdf/2611.17539)
  <sub>命中：autonomous、benchmark、agent、llm</sub>
  > Autonomous crystal-structure determination from powder X-ray diffraction (pXRD) remains a key bottleneck for self-driving materials laboratories.

## 工具与模型发布

_（窗口内没有关注工具的版本发布）_

## 领域新闻

_（窗口内没有命中关注主题的新闻）_

## 会议与活动（未来 120 天，日期以官网为准）

- **12-01**（15 天后）[MRS Fall Meeting](https://www.mrs.org/fall-meeting) — 材料计算与 AI 相关 session
- **12-08**（22 天后）[NeurIPS + ML4PS / AI4Science workshops](https://neurips.cc/) — 机器学习与物理科学交叉方法的最新动向
- **03-10**（114 天后）[APS March Meeting](https://www.aps.org/meetings/march) — 凝聚态/材料模拟大本营，MLIP 与晶体方法学分会场集中

## 运行健康

| 数据源 | 抓取 | 状态 |
| --- | --- | --- |
| arxiv | 666 | ok |
| crossref | 34 | ok |
| openalex | 76 | ok |
| rss | 95 | ok |
| github | 0 | ok |

> 原始 871 → 去重 769 → 剔除标题噪声 27 → 低相关度 709 → 入库 33。

<sub>配置 `config/config.json` · 历史 `state/radar.sqlite3` · 重跑 `./run_daily.sh` · 调试 `python3 -m radar explain '标题'`</sub>
