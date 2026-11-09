# 理论地图内容规范

`knowledge/` 是科研雷达“理论地图”的内容源。`python3 -B -m radar theory` 校验这些文件，并生成公开页面 `theory/`。不要手改 `theory/` 下的 HTML。

整体方案见规划稿《科研雷达 · 渐进式知识树整体方案》v1.0（2026-11-09）。本文件只写落地后的数据约定和发布规则。

## 目录

```text
knowledge/
  domains.json       根、学科领域和研究线
  nodes/<id>.md      节点：JSON 元信息 + Markdown 正文
  relations.json     有解释、有条件的节点关系
  paths/<id>.json    围绕一个问题的阅读路径
  sources.json       参考来源与实际查阅记录
  reviews/<id>.json  某个节点的核验与修订记录
```

个人疑问、笔记和自评只存在读者浏览器的 `localStorage`（键 `research-radar.theory.v1`），可导出为 JSON。它们不进入本目录，也不随公开页面发布。

## 稳定 ID

节点、关系、路径、来源都用稳定 ID：小写字母、数字和连字符，例如 `energy-structure-response`。ID 决定页面地址 `theory/nodes/<id>.html`，也是个人笔记的关联键。

- 改标题、换父节点、调整目录时不改 ID。
- 拆分或合并节点时，旧节点改为 `superseded`，填写 `replaced_by` 和 `migration`，旧链接继续可用。

## 节点文件

文件以 ```` ```json ```` 代码块包住的元信息开头，后面是 Markdown 正文。不用 `---` YAML 头：GitHub Pages 在这个仓库上运行 Jekyll，以 `---` 开头的文件会被当成 Jekyll 页面解析。

````text
```json
{
  "id": "energy-structure-response",
  "title": "从能量到结构与响应",
  "type": "concept",
  "parent": "response",
  "research": ["piezo", "csp"],
  "keywords": ["strain", "stress", "piezoelectric"],
  "purpose": "一句话：本节点解决什么问题，为什么在当前路径上。",
  "prereq": {"intuitive": ["……"], "full": ["……"]},
  "status": "draft",
  "version": "0.1",
  "updated": "2026-11-09",
  "sources": ["source-id"],
  "changelog": [{"version": "0.1", "date": "2026-11-09", "note": "初稿"}]
}
```
正文 Markdown
````

| 字段 | 含义 |
| --- | --- |
| `type` | `problem` 问题 · `concept` 概念 · `method` 方法 · `contrast` 对照 · `example` 实例 · `synthesis` 综合 |
| `parent` | 在知识树里的父条目：`domains.json` 里的领域 ID，或另一个节点 ID。每个节点只有一个父条目 |
| `research` | 可选。正文内容碰到的研究线 ID（见下文），没有就不写 |
| `keywords` | 可选。英文关键词列表，用于把论文雷达里的新论文对到条目上 |
| `prereq` | `intuitive` 是直观阅读所需基础，`full` 是完整推导所需基础；只做提示，不锁内容 |
| `status` | 见下方“内容状态” |
| `replaced_by` / `migration` | 仅 `superseded` 节点使用 |

### 正文写法

正文按规划稿 5.1 节的十个部分按需组织，用二级标题分节。标题末尾可以用 `{layer}` 标出阅读层次，读者可以按层次筛选，但默认连续阅读：

| 标记 | 阅读层次 |
| --- | --- |
| `{intuition}` | 直观解释 |
| `{math}` | 数学与推导 |
| `{mapping}` | 对应与边界 |

论述类型用块标出，页面会配文字标签，不只靠颜色区分：

```text
::: definition 应力
内容……
:::
```

可用类型：`definition` 定义、`theorem` 定理、`approximation` 近似、`empirical` 经验结论、`analogy` 类比、`assumption` 假设、`unverified` 待核验、`question` 检验问题。

其他语法：

- 公式：行内 `$...$`，独立 `$$...$$`，页面用 KaTeX 排版；长公式在自身容器内横向滚动。
- 节点链接：`[[node-id]]` 或 `[[node-id|显示文字]]`，构建时检查目标存在。
- 引用来源：`[@source-id]` 或 `[@source-id, 第 3 节]`，构建时检查来源存在。

## 关系

`relations.json` 每条关系都要写清：

| 字段 | 要求 |
| --- | --- |
| `from` / `to` | 存在的节点 ID |
| `type` | 见下表 |
| `explanation` | 这条联系具体是什么，不能为空 |
| `condition` | 联系成立的条件；无条件时写明“无额外条件”，不能留空 |
| `sources` | 支持该联系的来源 ID，可为空列表但要配合状态 |
| `status` | 与节点相同的内容状态 |

| `type` | 页面标签 | 方向含义 |
| --- | --- | --- |
| `prerequisite` | 需要先理解 | 读 `to` 之前最好先理解 `from` |
| `foundation` | 是推导基础 | `from` 是 `to` 某一层推导的基础 |
| `special-case` | 是特例 | `from` 是 `to` 的特例 |
| `equivalent-under` | 在条件下等价 | 仅在 `condition` 写明的条件下等价 |
| `approximates` | 近似于 | `from` 近似 `to` |
| `generalizes` | 推广了 | `from` 推广了 `to` |
| `shares-tool` | 共享数学工具 | 双向 |
| `computes` | 用于计算 | `from` 用于计算 `to` |
| `explains` | 用于解释 | `from` 用于解释 `to` 所述现象 |
| `contrasts` | 形成对照 | 双向 |
| `analogy` | 仅为启发性类比 | 双向，不代表任何数学等价 |

分类（`parent`）、先修（`prerequisite`）、理论关系和学习路径分开记录。树上的父子位置不等于先修；横向关系不等于等价。先修关系不得成环。

## 知识树与研究线

`domains.json`：

```json
{
  "root": {"title": "理论地图", "intro": "首页开头的一段话"},
  "domains": [{"id": "math", "title": "数学工具", "summary": "这个领域管哪些内容"}],
  "research_lines": [{"id": "piezo", "title": "压电与响应计算", "radar_topics": ["ferro-calc"]}]
}
```

- 树按学科组织：根 → 领域 → 节点 → 子节点。研究方向不是组织原则，节点放在它学科上属于的位置。
- 研究线是交汇标记。节点正文确实用到、能解释或会影响某条研究线时，才在 `research` 里写上它；页面用 ★ 标出，知识树可以按研究线高亮，并显示别的条目离它几步（沿父子边和关系走）。
- `radar_topics` 把研究线对到论文雷达的主题，供定时任务找新论文和已有条目的交汇。
- 构建会检查：父条目存在、父链不成环且最终到达某个领域、领域 ID 不与节点 ID 重复、`research` 里的研究线存在。
- 候选节点可以只有元信息、没有正文，用来先占住树上的位置。

### 页面结构（参考 VASP Wiki）

- 首页是“领域 | 子主题”表，加研究线和学习路线入口。
- `theory/tree.html` 是整棵树：桌面默认树形图，手机默认大纲；可只看已写条目、按研究线高亮。
- 节点页：开头一句 `purpose` 说明这页讲什么，正文分节；公式之后用“其中……”逐个说明符号；页末依次是子条目、相关条目、参考资料和分类栏（领域 · 类型 · 研究线 · 状态）。

## 路径

`paths/<id>.json` 记录一段问题驱动的阅读：

| 字段 | 含义 |
| --- | --- |
| `question` | 用户原始提问（原文保留） |
| `general_question` | 从原始提问提炼出的通用知识问题 |
| `base` | 适用基础 |
| `steps` | `[{"node": id, "why": 为什么读这一步}]`，按建议顺序 |
| `branches` | 读完后可选的方向：`direction`（`down` 向下追溯 · `in` 向内深入 · `across` 横向连接 · `up` 向上抽象 · `out` 向外迁移）、`title`、`why`，可选 `node` |
| `goals` | 读完后应能做到的理解目标 |

## 来源

`sources.json` 的每条来源：`id`、`kind`（`textbook` 教材 · `paper` 论文 · `docs` 官方文档 · `benchmark` 基准研究 · `practice` 经验记录）、`citation`、`doi` 或 `url`、`version`、`locator`（章节、公式或页码）、`consulted`。

`consulted` 是实际查阅记录：`[{"date": "...", "by": "...", "what": "核对了哪一处"}]`。为空时页面显示“尚未实际查阅”，这条来源只能算拟查阅书目，不能支撑已核验内容。

## 内容状态

| 状态 | 页面文字 | 含义 |
| --- | --- | --- |
| `candidate` | 候选 | 只有题目、学习动机和拟连接的节点 |
| `draft` | 草稿 | 已有正文，证据或推导未核查完 |
| `verified` | 已核验 | 完成了核验记录中写明的项目；只在写明的范围内成立 |
| `needs-revision` | 待修订 | 发现错误、来源失效、版本变化或条件需要更正 |
| `superseded` | 已替代 | 保留历史，引导到 `replaced_by` |

首页目录只列已写的节点：已核验在前，草稿单独折叠并带标签。候选只出现在领域表和知识树里。

## 核验记录

`reviews/<node-id>.json` 是一个列表，每条记录：

```json
{
  "date": "2026-11-09",
  "reviewer": "谁核验",
  "independent": true,
  "scope": ["核对了哪些论述、公式或步骤"],
  "method": "怎么核对的：查原文 / 独立重推 / 数值检查",
  "evidence": ["source-id 及位置，或检查脚本路径"],
  "open_issues": ["还有什么限制或未解决"]
}
```

节点要标为 `verified`，至少需要一条 `independent: true`、`scope` 和 `evidence` 都不为空的记录，且引用的来源有实际查阅记录。仅由生成模型复查自己写的文字时，`independent` 必须为 `false`，构建不把它算作核验。

## 生长约束（摘自规划稿 4.3 节）

- 新节点必须写明“为什么需要它”（`purpose`），并挂在学科上合适的父条目下。
- 新术语没有独立学习价值时，先在已有节点内解释。
- 不为凑连接数建立跨领域类比；类比只能用 `analogy` 类型。
- 同一主题可以逐步加深，不要求每次学习都新增节点。
- 自动任务只能新增 `candidate` 节点或补草稿，不能把任何内容标为 `verified`；科研点子不进入本目录。

## 构建与检查

```bash
python3 -B -m radar theory          # 校验并生成 theory/
python3 -B -m radar theory --check  # 只校验，并确认 theory/ 与内容源一致
python3 -B -m radar junctions       # 只读：论文、研究线与条目的交汇，不写任何文件
```

`.github/workflows/theory-check.yml` 在 `knowledge/`、生成器或 `theory/` 改动时运行 `--check`，与每日论文更新分开，内容问题不会阻塞日报。
