# 科研雷达 · 2026-11-10（周二）

> 领域：计算化学 / 有机分子晶体结构预测、化学生成模型、有机铁电计算与手性分子晶体；低优先级跟踪视觉生成  
> 自动生成 11:08 · 抓取窗口 11-08 19:08 → 现在 · 候选 768 → 本轮入库 41 → 今日累计 **10**（本次 +4） · 来源 arxiv/crossref/openalex/rss/github

## 今日速览

- **最高相关度**：Quantitative Assessment of Crystal Structure Prediction（13.8）
- **本周条目最多**：机器学习势与通用势函数（MLIP / UMA）（23 篇）
- **升温主题**：AI for Science 方法与自动化
- **构成**：机器学习势与通用势函数（MLIP / UMA） 4 · 分子晶体结构预测（CSP）与能量图景 3 · 化学相关生成模型（分子、材料与反应） 2 · AI for Science 方法与自动化 1

## 今日最值得看

1. **[Quantitative Assessment of Crystal Structure Prediction](https://arxiv.org/abs/2611.10380)**
   `CSP` · *arXiv* · 2026-11-07 · [PDF](https://arxiv.org/pdf/2611.10380)
   <sub>命中：crystal structure prediction (csp)、crystal structure prediction、crystal structure、polymorphism、polymorph</sub>
   > Crystal Structure Prediction (CSP) aims to predict a material's 3D structure from its chemical composition, with applications from energy storage to biomedical devices. Despite its importance, existing evaluation frameworks suffer from key limitations: they rely on threshold-sensitive or incomparable metrics, focus pre…

2. **[Reweighting Free Energy Profiles with Universal Machine Learning Interatomic Potentials for Fast Consensus Building](https://doi.org/10.1021/acs.jctc.6c02044)**
   `MLIP` · *Journal of Chemical Theory and Computation* · 2026-11-09
   <sub>命中：density functional theory、mlip、mace</sub>
   > Universal machine learning interatomic potentials (MLIPs) have made density functional theory (DFT)-level molecular dynamics highly affordable. However, their rapid proliferation makes it prohibitively expensive to benchmark every new model against the potential of mean force (PMF), the bridge between microscopic atomi…

3. **[High-Volume Wurtzite MnSe in MnSe/CdSe Superlattices: Structure, Magnetism and Optical Response](https://arxiv.org/abs/2611.09509)**
   `CSP` · *arXiv* · 2026-11-06 · [PDF](https://arxiv.org/pdf/2611.09509)
   <sub>命中：polymorphism、polymorph</sub>
   > Polymorphism in Mn-based chalcogenides offers access to magnetic semiconductors with distinct crystal symmetries, polar structures, and different magnetic orders. In particular, wurtzite MnSe exhibits an appealing interplay of electric polarization and several competing magnetic phases including altermagnetic order.

4. **[Homeopathic Learning: Diluting poisoned fine-tuning data can strengthen its effect](https://arxiv.org/abs/2611.10110)**
   `MLIP` · *arXiv* · 2026-11-06 · 👤Jack D. Evans · [PDF](https://arxiv.org/pdf/2611.10110)
   <sub>命中：fine-tuning</sub>
   > We study homeopathic learning, a phenomenon where poisoned training data with little effect on its own can create a hidden backdoor once clean, contrasting data is added. In our experiments, a model fine-tuned only on a "poison" dataset associated with a trait T (such as speaking German or being misaligned) does not le…

5. **[Universal Approximation by Equivariant Message-Passing Graph Neural Networks with a Bilinear Readout](https://arxiv.org/abs/2611.10772)**
   `MLIP` · *arXiv* · 2026-11-07 · [PDF](https://arxiv.org/pdf/2611.10772)
   <sub>命中：interatomic potential、equivariant</sub>
   > We prove universal approximation for the bilinear-readout equivariant message-passing network (BREMP), a reference architecture for equivariant graph neural network interatomic potentials.

6. **[Inverse design of superconductors and semiconductors with differentiable foundation models](https://arxiv.org/abs/2611.09572)**
   `生成模型` `生成设计` · *arXiv* · 2026-11-06 · [PDF](https://arxiv.org/pdf/2611.09572)
   <sub>命中：foundation model、inverse design</sub>
   > Designing a crystal for a target property requires choosing its elements, stoichiometry, and atomic structure together, yet gradients exist only for the continuous structural variables.

## 按主题展开

### 分子晶体结构预测（CSP）与能量图景 · 持平

- **[Influence of Crystal Structure and Shape Anisotropies on Valence-Band States of InP Colloidal Nanocrystals: Application of the xyz Algorithm](https://doi.org/10.1021/acs.jpclett.6c03306)**
  `CSP` · *The Journal of Physical Chemistry Letters* · 2026-11-09
  <sub>命中：crystal structure</sub>
  > We demonstrate that traditional classification of electronic states in semiconductor nanocrystals based on the quantum numbers of angular momenta becomes inappropriate and even misleading in nanocryst…

### 化学相关生成模型（分子、材料与反应） · 回落 ↓0.5×

- **[Spatiotemporal Energy Consistency Enables Reliable Coarse-Grained Molecular Dynamics from Diffusion Models](https://arxiv.org/abs/2611.10517)**
  `生成模型` · *arXiv* · 2026-11-07 · [PDF](https://arxiv.org/pdf/2611.10517)
  <sub>命中：diffusion models</sub>
  > Coarse-grained molecular dynamics (CGMD) extends molecular simulations to length and time scales inaccessible to atomistic models, but building thermodynamically faithful CG potentials remains a longs…

### 机器学习势与通用势函数（MLIP / UMA） · 持平

- **[Conformation of microhydrated ethylimidazole isomers explored by microwave spectroscopy](https://doi.org/10.1063/5.0351003)**
  `MLIP` · *The Journal of Chemical Physics* · 2026-11-09
  <sub>命中：density functional theory、potential energy surface</sub>
  > Chirped-pulse Fourier transform microwave spectroscopy (2.0–18.5 GHz) has been employed to determine the molecular structures of isolated N-ethylimidazole and 2-ethylimidazole and to investigate the s…

### AI for Science 方法与自动化 · 升温 ↑2.3×

- **[DFT-Agent Bench: Scaffold Effects and Execution Provenance in Autonomous DFT](https://arxiv.org/abs/2611.10629)**
  `AI4S` · *arXiv* · 2026-11-07 · [PDF](https://arxiv.org/pdf/2611.10629)
  <sub>命中：autonomous、benchmark、agent</sub>
  > Large language models are increasingly deployed as autonomous agents for first-principles materials simulation. We report empirical findings from DFT-Agent Bench, a benchmark of 200+ Quantum ESPRESSO…

## 工具与模型发布

_（窗口内没有关注工具的版本发布）_

## 领域新闻

_（窗口内没有命中关注主题的新闻）_

## 关注课题组的新作

- [Homeopathic Learning: Diluting poisoned fine-tuning data can strengthen its effect](https://arxiv.org/abs/2611.10110) — *arXiv* · 2026-11-06（Jack D. Evans）

## 会议与活动（未来 120 天，日期以官网为准）

- **12-01**（21 天后）[MRS Fall Meeting](https://www.mrs.org/fall-meeting) — 材料计算与 AI 相关 session
- **12-08**（28 天后）[NeurIPS + ML4PS / AI4Science workshops](https://neurips.cc/) — 机器学习与物理科学交叉方法的最新动向
- **03-10**（120 天后）[APS March Meeting](https://www.aps.org/meetings/march) — 凝聚态/材料模拟大本营，MLIP 与晶体方法学分会场集中

## 运行健康

| 数据源 | 抓取 | 状态 |
| --- | --- | --- |
| arxiv | 633 | ok |
| crossref | 103 | ok |
| openalex | 84 | ok |
| rss | 57 | ok |
| github | 0 | ok |

> 原始 877 → 去重 768 → 剔除标题噪声 22 → 低相关度 705 → 入库 41。

<sub>配置 `config/config.json` · 历史 `state/radar.sqlite3` · 重跑 `./run_daily.sh` · 调试 `python3 -m radar explain '标题'`</sub>
