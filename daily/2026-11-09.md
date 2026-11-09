# 科研雷达 · 2026-11-09（周一）

> 领域：计算化学 / 有机分子晶体结构预测、化学生成模型、有机铁电计算与手性分子晶体；低优先级跟踪视觉生成  
> 自动生成 11:48 · 抓取窗口 11-07 19:48 → 现在 · 候选 518 → 本轮入库 38 → 今日累计 **5**（本次 +4） · 来源 arxiv/crossref/openalex/rss/github

## 今日速览

- **最高相关度**：Learning Generative Dynamics for 3D Molecule Generation via Sequential Neuro-Symbolic Cons…（6.1）
- **本周条目最多**：机器学习势与通用势函数（MLIP / UMA）（21 篇）
- **升温主题**：AI for Science 方法与自动化
- **构成**：机器学习势与通用势函数（MLIP / UMA） 3 · 化学相关生成模型（分子、材料与反应） 2

## 今日最值得看

1. **[Learning Generative Dynamics for 3D Molecule Generation via Sequential Neuro-Symbolic Constraints](https://arxiv.org/abs/2611.09142)**
   `生成模型` · *arXiv* · 2026-11-06 · [PDF](https://arxiv.org/pdf/2611.09142)
   <sub>命中：molecule generation、diffusion models</sub>
   > Diffusion models have recently emerged as a powerful paradigm for generating 3D molecules. Despite showing remarkable promise, they learn atomic distributions implicitly from data, without explicitly encoding physicochemical rules into their generative dynamics.

2. **[Symmetry-Gated Sliding: Decoupling Interlayer Translation from Polarization Reversal in Boron Nitride Ferroelectrics](https://arxiv.org/abs/2611.09025)**
   `MLIP` · *arXiv* · 2026-11-06 · [PDF](https://arxiv.org/pdf/2611.09025)
   <sub>命中：machine learning interatomic potential、interatomic potential</sub>
   > Electric-field-driven polarization switching in sliding ferroelectrics depends on how local interlayer motion is accommodated by the surrounding structure. Yet the relationship between sliding, domain-wall (DW) propagation, and collective domain evolution under changing vector fields remains unclear.

3. **[Controllable Molecule Generation via Sparse Representation Editing: An Interpretability-Driven Perspective](https://arxiv.org/abs/2611.09235)**
   `生成模型` · *arXiv* · 2026-11-06 · [PDF](https://arxiv.org/pdf/2611.09235)
   <sub>命中：molecule generation</sub>
   > Controllable molecule generation is crucial for diverse scientific applications, such as drug discovery and materials design. While large language models (LLMs) show great promise, their dense and entangled representations impede precise control over the generation of molecules with bespoke substructures or properties.…

4. **[Physics Informed Priors for Machine Learning Interatomic Potentials with Uncertainty Quantification](https://arxiv.org/abs/2611.09325)**
   `MLIP` · *arXiv* · 2026-11-06 · [PDF](https://arxiv.org/pdf/2611.09325)
   <sub>命中：uncertainty quantification、active learning</sub>
   > Standard uncertainty quantification methods for machine learning interatomic potentials often fail to quantify the effects of model misspecification despite its prominence as a source of error.

5. **[Fortuitous Cancellation of Competing Effects in the Free Energy of Water Autoionization: Long-Range Electrostatics, System Size, and Nuclear Quantum Effects](https://arxiv.org/abs/2611.08874)**
   `MLIP` · *arXiv* · 2026-11-06 · [PDF](https://arxiv.org/pdf/2611.08874)
   <sub>命中：mlip</sub>
   > Few molecular processes are more fundamental to chemistry than the autoionization of water, whose equilibrium constant, $K_w \approx 10^{-14}$, underlies acid-base equilibria and the chemistry of life. Yet the molecular origins of the free energy cost of forming and separating ions remain incompletely understood.

## 按主题展开

_（今日无）_

## 工具与模型发布

_（窗口内没有关注工具的版本发布）_

## 领域新闻

_（窗口内没有命中关注主题的新闻）_

## 会议与活动（未来 120 天，日期以官网为准）

- **12-01**（22 天后）[MRS Fall Meeting](https://www.mrs.org/fall-meeting) — 材料计算与 AI 相关 session
- **12-08**（29 天后）[NeurIPS + ML4PS / AI4Science workshops](https://neurips.cc/) — 机器学习与物理科学交叉方法的最新动向

## 运行健康

| 数据源 | 抓取 | 状态 |
| --- | --- | --- |
| arxiv | 300 | ok |
| crossref | 46 | ok |
| openalex | 97 | ok |
| rss | 109 | ok |
| github | 0 | ok |

> 原始 552 → 去重 518 → 剔除标题噪声 19 → 低相关度 461 → 入库 38。

<sub>配置 `config/config.json` · 历史 `state/radar.sqlite3` · 重跑 `./run_daily.sh` · 调试 `python3 -m radar explain '标题'`</sub>
