# 科研雷达 · 2026-11-08（周日）

> 领域：计算化学 / 有机分子晶体结构预测、化学生成模型、有机铁电计算与手性分子晶体；低优先级跟踪视觉生成  
> 自动生成 10:08 · 抓取窗口 11-06 18:08 → 现在 · 候选 815 → 本轮入库 45 → 今日累计 **8**（本次 +0） · 来源 arxiv/crossref/openalex/rss/github

## 今日速览

- **最高相关度**：Generative Models for Novel Enzymatic Reactions: How Far Do They Go?（5.3）
- **本周条目最多**：机器学习势与通用势函数（MLIP / UMA）（26 篇）
- **升温主题**：AI for Science 方法与自动化、手性分子与分子晶体
- **构成**：机器学习势与通用势函数（MLIP / UMA） 4 · 化学相关生成模型（分子、材料与反应） 2 · 分子晶体结构预测（CSP）与能量图景 2

## 今日最值得看

1. **[Generative Models for Novel Enzymatic Reactions: How Far Do They Go?](https://doi.org/10.64898/2026.11.05.759793)**
   `生成模型` · *bioRxiv (Cold Spring Harbor Laboratory)* · 2026-11-06
   <sub>命中：generative models、generative model</sub>
   > Enzyme function prediction is a long-standing problem in biology, and deep learning methods have recently become popular to improve performance on this task. While most of these models focus on classifying enzymes or mapping them to known reactions, predicting unknown biochemical reactions remains underexplored.

2. **[Design of p-type Metastable GaBiO3 Ultra-wide Bandgap Semiconductors](https://doi.org/10.1016/j.commt.2026.100071)**
   `CSP` · *Computational Materials Today* · 2026-11-01
   <sub>命中：crystal structure prediction、crystal structure</sub>
   > P -type ultra-wide-bandgap semiconductors are essential for high-performance optoelectronic and power devices, yet efficient p -type doping remains a major challenge for materials such as β -Ga 2 O 3 .

3. **[Native Mass Spectrometry of Membrane Protein Lipid and Ligand Complexes Using de novo Designed WRAP Domains](https://doi.org/10.1021/jacs.6c15293)**
   `生成模型` · *Journal of the American Chemical Society* · 2026-11-07
   <sub>命中：de novo</sub>
   > Membrane proteins engage in dynamic transient interactions with surrounding lipids along with their substrates. Capturing these concomitant contacts often remains a challenging problem.

4. **[Training of Neural Network Machine Learning Potentials for Activation Barrier Calculations in Predicting Growth Modes of Deposited Metals](https://doi.org/10.26434/chemrxiv.15011790/v1)**
   `MLIP` · *ChemRxiv* · 2026-11-06
   <sub>命中：density functional theory、mlip</sub>
   > Machine-learning interatomic potentials (MLIPs) are opening many new opportunities to extend the capabilities of computational materials science. MLIPs deliver increased throughput and simulations at time and length scales beyond first principles density functional theory (DFT), while maintaining near-DFT accuracy, thu…

5. **[Simulating ionic liquid fragmentation in electrospray thrusters with foundation models](https://doi.org/10.1016/j.actaastro.2026.10.064)**
   `MLIP` · *Acta Astronautica* · 2026-11-01
   <sub>命中：density functional theory、fine-tuning、mace</sub>
   > Predicting the products of ionic-liquid impacts on extractor surfaces is important for electrospray-thruster lifetime analysis, yet available atomistic methods require a compromise between chemical fidelity and computational cost.

6. **[Crystal Structure-Guided Design of a Single-Site Blue Phosphor BaHf(BO3)2:Eu2+ with High Color Purity for WLEDs](https://doi.org/10.1021/acs.cgd.6c01225)**
   `CSP` · *Crystal Growth & Design* · 2026-11-07
   <sub>命中：crystal structure</sub>
   > Near-ultraviolet (n-UV) chip-excited white light-emitting diodes (WLEDs) offer a promising strategy to overcome the blue-light hazard and poor color quality inherent in conventional white-light sources. However, the lack of high-performance blue-emitting phosphors remains a critical bottleneck.

## 按主题展开

### 机器学习势与通用势函数（MLIP / UMA） · 持平

- **[Machine Learning-Based Screening and Rationalization for Aromatic Guest Inclusion into MOF Crystals](https://doi.org/10.1021/acsmaterialsau.6c00215)**
  `MLIP` · *ACS Materials Au* · 2026-11-07
  <sub>命中：neural network potential</sub>
  > The exploration of metal–organic framework (MOF) properties arising from guest inclusion, particularly for less-volatile molecules incorporated through solution processes, remains time-consuming and d…

- **[Exploring Chemical Concepts and Reactivity from Conceptual Density Functional Theory in Excited States via the ΔSCF Approach](https://doi.org/10.1021/acs.jctc.6c01493)**
  `MLIP` · *Journal of Chemical Theory and Computation* · 2026-11-07
  <sub>命中：density functional theory</sub>
  > Along with the recent development of the ΔSCF approach for excited state electronic structure description using density functional theory (DFT), we extend and develop conceptual density functional the…

## 工具与模型发布

_（窗口内没有关注工具的版本发布）_

## 领域新闻

_（窗口内没有命中关注主题的新闻）_

## 会议与活动（未来 120 天，日期以官网为准）

- **12-01**（23 天后）[MRS Fall Meeting](https://www.mrs.org/fall-meeting) — 材料计算与 AI 相关 session
- **12-08**（30 天后）[NeurIPS + ML4PS / AI4Science workshops](https://neurips.cc/) — 机器学习与物理科学交叉方法的最新动向

## 运行健康

| 数据源 | 抓取 | 状态 |
| --- | --- | --- |
| arxiv | 632 | ok |
| crossref | 94 | ok |
| openalex | 108 | ok |
| rss | 109 | ok |
| github | 0 | ok |

> 原始 943 → 去重 815 → 剔除标题噪声 23 → 低相关度 747 → 入库 45。

<sub>配置 `config/config.json` · 历史 `state/radar.sqlite3` · 重跑 `./run_daily.sh` · 调试 `python3 -m radar explain '标题'`</sub>
