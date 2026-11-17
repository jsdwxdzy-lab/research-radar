# 科研雷达 · 2026-11-17（周二）

> 领域：计算化学 / 有机分子晶体结构预测、化学生成模型、有机铁电计算与手性分子晶体；低优先级跟踪视觉生成  
> 自动生成 08:08 · 抓取窗口 11-15 16:08 → 现在 · 候选 772 → 本轮入库 37 → 今日累计 **5**（本次 +5） · 来源 arxiv/crossref/openalex/rss/github

## 今日速览

- **最高相关度**：Improving molecular property prediction with score-based diffusion models（7.4）
- **本周条目最多**：机器学习势与通用势函数（MLIP / UMA）（16 篇）
- **构成**：化学相关生成模型（分子、材料与反应） 3 · 分子晶体结构预测（CSP）与能量图景 2

## 今日最值得看

1. **[Improving molecular property prediction with score-based diffusion models](https://doi.org/10.1038/s41467-026-79240-y)**
   `生成模型` · *Nature Communications* · 2026-11-16 · 多源×2
   <sub>命中：diffusion models、score-based</sub>
   > We explore diffusion-based training as a flexible approach to molecular property prediction in settings shaped by chemical, biophysical, and latent heterogeneity. To address this, we build on score-based generative diffusion models and introduce a conditional diffusion module for predictive tasks, equipped with a joint…

2. **[Deep learning of tautomer stability from crystallographic proton positions](https://doi.org/10.1039/d6sc03714c)**
   `生成模型` · *Chemical Science* · 2026-11-11
   <sub>命中：conformer generation、molecular design</sub>
   > Tautomerism plays a central role in molecular recognition, physicochemical properties, and chemical reactivity, yet rapid identification of stable tautomeric states remains a persistent challenge in molecular design and structure-based drug discovery.

3. **[Study on Solid Forms of Upadacitinib: Crystal Structures, Physicochemical Properties, and Phase Transformation](https://doi.org/10.1021/acs.cgd.6c00553)**
   `CSP` · *Crystal Growth & Design* · 2026-11-16
   <sub>命中：polymorph</sub>
   > Upadacitinib (UPA) is an important selective Janus kinase 1 (JAK1) inhibitor used for the treatment of various chronic inflammatory diseases. However, the detailed crystal structures, systematic physicochemical studies, and phase transformation relationship of UPA solid forms were not reported.

4. **[Simplifying crystal structures: a new tool for visualising packing motifs in molecular crystals as skeletal frameworks](https://doi.org/10.1039/d6ce00813e)**
   `CSP` · *CrystEngComm* · 2026-11-16
   <sub>命中：molecular crystals</sub>
   > Relationships between crystal structures can be difficult to visualise. Here we present a tool for defining and reusing a simplified view of the molecule across multiple crystal structures to aid in structure comparisons and molecular anonymisation.

5. **[Engineering Crystal Structures by Orthogonal Hydrogen and Halogen Bonding Synthons](https://doi.org/10.1021/acs.cgd.6c01126)**
   `生成模型` `CSP` `生成设计` · *Crystal Growth & Design* · 2026-11-16
   <sub>命中：de novo、crystal packing</sub>
   > Controlling crystal packing by deploying robust, orthogonal, and non-interfering intermolecular interactions along independent directions represents a cornerstone strategy in crystal engineering. However, predicting the feasibility of such de novo designs a priori remains a formidable challenge.

## 按主题展开

_（今日无）_

## 工具与模型发布

_（窗口内没有关注工具的版本发布）_

## 领域新闻

_（窗口内没有命中关注主题的新闻）_

## 会议与活动（未来 120 天，日期以官网为准）

- **12-01**（14 天后）[MRS Fall Meeting](https://www.mrs.org/fall-meeting) — 材料计算与 AI 相关 session
- **12-08**（21 天后）[NeurIPS + ML4PS / AI4Science workshops](https://neurips.cc/) — 机器学习与物理科学交叉方法的最新动向
- **03-10**（113 天后）[APS March Meeting](https://www.aps.org/meetings/march) — 凝聚态/材料模拟大本营，MLIP 与晶体方法学分会场集中

## 运行健康

| 数据源 | 抓取 | 状态 |
| --- | --- | --- |
| arxiv | 631 | ok |
| crossref | 114 | ok |
| openalex | 77 | ok |
| rss | 52 | ok |
| github | 0 | ok |

> 原始 874 → 去重 772 → 剔除标题噪声 26 → 低相关度 709 → 入库 37。

<sub>配置 `config/config.json` · 历史 `state/radar.sqlite3` · 重跑 `./run_daily.sh` · 调试 `python3 -m radar explain '标题'`</sub>
