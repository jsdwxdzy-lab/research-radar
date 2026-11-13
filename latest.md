# 科研雷达 · 2026-11-13（周五）

> 领域：计算化学 / 有机分子晶体结构预测、化学生成模型、有机铁电计算与手性分子晶体；低优先级跟踪视觉生成  
> 自动生成 11:29 · 抓取窗口 11-11 19:29 → 现在 · 候选 869 → 本轮入库 47 → 今日累计 **5**（本次 +2） · 来源 arxiv/crossref/openalex/rss/github

## 今日速览

- **最高相关度**：Generative inverse estimation of 3D atomic coordination from near-edge spectra via equivar…（7.2）
- **本周条目最多**：机器学习势与通用势函数（MLIP / UMA）（18 篇）
- **构成**：机器学习势与通用势函数（MLIP / UMA） 3 · 化学相关生成模型（分子、材料与反应） 1 · 分子晶体结构预测（CSP）与能量图景 1

## 今日最值得看

1. **[Generative inverse estimation of 3D atomic coordination from near-edge spectra via equivariant diffusion models](https://doi.org/10.1038/s41524-026-02384-4)**
   `生成模型` `生成设计` · *npj Computational Materials* · 2026-11-12 · 多源×2
   <sub>命中：diffusion models、diffusion model</sub>
   > Extracting 3D atomic coordinates from spectroscopic data is a longstanding inverse problem. We present an equivariant diffusion model that generates the distribution of site-specific 3D structures directly from near-edge spectra (ELNES/XANES).

2. **[High-Throughput Surface Screening Reveals Energetically Competitive Low-Symmetry Facets in Wurtzite Semiconductors](https://arxiv.org/abs/2611.15138)**
   `MLIP` · *arXiv* · 2026-11-11 · [PDF](https://arxiv.org/pdf/2611.15138)
   <sub>命中：machine learning interatomic potential、density functional theory、interatomic potential</sub>
   > Surfaces and interfaces govern the performance of wurtzite semiconductors in electronics, sensing, and solar-fuel conversion. To date, first-principles studies have focused mostly on high-symmetry low-index facets, owing to the computational cost and complexity of modelling low-symmetry high-index surfaces.

3. **[Competing Octahedral Tilting and $B$-Site Off-Centering Govern the Phase Diagram of CsGe$_{1-x}$Sn$_x$Br$_3$ Perovskite Alloys](https://arxiv.org/abs/2611.15200)**
   `MLIP` · *arXiv* · 2026-11-11 · [PDF](https://arxiv.org/pdf/2611.15200)
   <sub>命中：machine-learned interatomic potential、interatomic potential</sub>
   > Lead-free halide perovskites based on Ge and Sn avoid the toxicity of Pb, but the two cations favor different structural distortions. The stereochemically active Ge $4s^2$ lone pair drives polar $B$-site off-centering, whereas the larger Sn$^{2+}$ cation favors octahedral tilting.

4. **[Computational Insights into Nitro-BBTP: Crystal Packing, Electronic Structure, Molecular Reactivity, and Predicted C5aR1 Recognition](https://doi.org/10.3390/cryst16110714)**
   `CSP` · *Crystals* · 2026-11-11
   <sub>命中：crystal structure、crystal packing</sub>
   > The experimentally determined crystal structure of 13-nitrobenzo[a][1,4]benzothiazino [3,2-c]phenoxazine (Nitro-BBTP) was investigated using Hirshfeld surface analysis, density functional theory (DFT), natural bond orbital (NBO) analysis, molecular electrostatic potential mapping, local reactivity descriptors, molecula…

5. **[Neuroevolution potentials uncover concentration-dependent Li + transport mechanisms in PEO–LiTFSI electrolytes](https://doi.org/10.1039/d6sc07805b)**
   `MLIP` · *Chemical Science* · 2026-11-12
   <sub>命中：active learning</sub>
   > Here, we combine uncertainty-guided active learning with neuroevolution potential (NEP) simulations to investigate poly(ethylene oxide) (PEO)–LiTFSI electrolytes over a broad range of salt concentrations.

## 按主题展开

_（今日无）_

## 工具与模型发布

_（窗口内没有关注工具的版本发布）_

## 领域新闻

_（窗口内没有命中关注主题的新闻）_

## 会议与活动（未来 120 天，日期以官网为准）

- **12-01**（18 天后）[MRS Fall Meeting](https://www.mrs.org/fall-meeting) — 材料计算与 AI 相关 session
- **12-08**（25 天后）[NeurIPS + ML4PS / AI4Science workshops](https://neurips.cc/) — 机器学习与物理科学交叉方法的最新动向
- **03-10**（117 天后）[APS March Meeting](https://www.aps.org/meetings/march) — 凝聚态/材料模拟大本营，MLIP 与晶体方法学分会场集中

## 运行健康

| 数据源 | 抓取 | 状态 |
| --- | --- | --- |
| arxiv | 633 | ok |
| crossref | 155 | ok |
| openalex | 90 | ok |
| rss | 104 | ok |
| github | 0 | ok |

> 原始 982 → 去重 869 → 剔除标题噪声 39 → 低相关度 783 → 入库 47。

<sub>配置 `config/config.json` · 历史 `state/radar.sqlite3` · 重跑 `./run_daily.sh` · 调试 `python3 -m radar explain '标题'`</sub>
