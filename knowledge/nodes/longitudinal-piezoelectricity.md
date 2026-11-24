```json
{
  "id": "longitudinal-piezoelectricity",
  "title": "纵向压电响应与方向极大",
  "type": "concept",
  "parent": "piezoelectric-tensor",
  "research": ["piezo"],
  "keywords": [
    "longitudinal piezoelectric coefficient",
    "d_L",
    "directional piezoelectricity",
    "maximum longitudinal response"
  ],
  "purpose": "晶轴分量 d33 依赖坐标约定；纵向系数 d_L(n) 把响应投到任意单位方向，便于比较晶体取向和筛选候选。",
  "prereq": {
    "intuitive": [
      "[[piezoelectric-tensor]] 里 e 与 d 的定义",
      "单位矢量与方向余弦"
    ],
    "full": [
      "[[tensors]] 的坐标变换",
      "[[elastic-tensor]] 与 d = e s"
    ]
  },
  "status": "draft",
  "version": "0.1",
  "updated": "2026-11-24",
  "origin": "工作提炼（2026-11-24）",
  "sources": ["ieee-176-piezo", "wu-2005-strain"],
  "changelog": [
    {
      "version": "0.1",
      "date": "2026-11-24",
      "note": "初稿：纵向系数定义、方向极大、与晶轴分量的区别、软柔度放大与检验问题"
    }
  ]
}
```

## 直觉 {intuition}

实验或论文里常写的 $d_{33}$，指的是**某一套坐标轴**下的分量：第 3 轴方向的电场（或极化）与同一方向的正应变之间的耦合。换一套晶轴命名，$d_{33}$ 可以变成别的下标，甚至按对称性直接为零（例如许多单斜设置里主剪切分量不叫 $d_{33}$）。

**纵向压电响应**问的是另一件事：沿某个单位方向 $\mathbf{n}$ 拉伸（或沿 $\mathbf{n}$ 测极化），同一方向上耦合有多强？它不绑定“哪根轴叫 3”。在单位球上扫一遍 $\mathbf{n}$，取绝对值最大的那一个，记作 $d_{L,\max}$，常用来比较取向不同的晶体，或给结构搜索排个与坐标约定无关的标量分数。

![示意：单位球上的方向 n，以及沿 n 的纵向极化变化。](figs/longitudinal-piezo-direction.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $\mathbf{n}$ | 单位方向 | 红色箭头 |
| $x,y$ | 某一套笛卡尔坐标轴 | 灰色坐标轴 |
| $\Delta P_\parallel$ | 沿 $\mathbf{n}$ 的极化变化（示意） | 蓝色箭头 |
| 绿色短线 | 沿 $\mathbf{n}$ 的纵向伸长示意 | 垂直于 $\mathbf{n}$ 的两段标记 |

## 定义与公式 {math}

::: definition 纵向压电应变系数
设 $d_{ijk}$ 是压电应变张量（三阶，笛卡尔指标），$\mathbf{n}$ 是单位矢量。纵向系数

$$d_L(\mathbf{n}) = \sum_{i,j,k=1}^{3} n_i\, d_{ijk}\, n_j\, n_k$$

其中 $n_i$ 是 $\mathbf{n}$ 的第 $i$ 个笛卡尔分量；$d_{ijk}$ 与 Voigt 形式 $d_{iJ}$ 的对应见 [[tensors]] 与 [[piezoelectric-tensor]] [@ieee-176-piezo]。$d_L$ 的单位与 $d$ 相同（常用 pC/N）。
:::

方向极大（标量）取

$$d_{L,\max} = \max_{\|\mathbf{n}\|=1}\bigl|d_L(\mathbf{n})\bigr|$$

其中最大值在单位球上取。实际计算可对球面积分离散采样，或利用对称性把搜索限制在不可约方向上。

与 $e$、$s^{E}$ 的关系不变：先有 $d = e\, s^{E}$，再对 $d$ 做上面的方向投影 [@ieee-176-piezo; @wu-2005-strain]。因此 **$d_L$ 继承弹性柔顺的病态**：某个方向上 $C$ 很软（$s$ 很大）时，$e$ 并不大也可能给出很大的 $|d_L|$。

::: unverified 待核验
- 部分文献报告的“有效 $d_{33}$”是薄膜法向或陶瓷极化方向上的纵向响应，是否与上式的 $d_L(\mathbf{n})$ 在边界条件上完全一致，需对照具体测量约定。
- 离散采样球网的收敛阈值（多少点才稳定到目标精度）随点群而变，这里不给数值处方。
:::

## 在本研究线里的样子 {mapping}

- **和晶轴分量对照**：点群允许的 $d_{33}$ 可以为零，同时 $d_{L,\max}$ 由别的分量（例如剪切型）贡献；只盯 $d_{33}$ 会漏掉取向最优方向。
- **结构筛选**：在许多候选晶体之间比较时，$d_{L,\max}$ 少受“笛卡尔轴怎么贴到晶轴”的影响；但若两套计算的弹性软度差很多，$d_L$ 排序仍可能跟着 $s$ 走，需要同时看 $e_L$ 或 $C$ 的最小本征值（见 [[elastic-tensor]]）。
- **交叉检查**：在选定的 $\mathbf{n}$ 上施加小的纵向应变，用 Berry 相读极化变化，线性区内应逼近由 $e$、$s$ 组装出的 $d_L(\mathbf{n})$；这是验收，不是另一套理论（见 [[berry-phase-polarization]]、[[finite-difference-vs-dfpt]]）。

## 常见坑 {mapping}

- **把 $d_{33}$ 当成材料标量**：$d_{33}$ 是分量；换设置或换样品坐标，同一个物理晶体可以有不同的 $d_{33}$。
- **只看大的 $d_L$，不看 $C$**：软方向上 $d_L$ 被 $s$ 放大时，数值对弹性误差极敏感；需要同时报告力学稳定性与 $e$ 一侧的大小。
- **粉末或陶瓷数据**：多晶平均不是简单的 $d_{L,\max}$，还依赖织构与边界条件；不能把单晶方向极大直接当成陶瓷测值。

## 检验自己 {mapping}

::: question 解释
为什么一个按对称性 $d_{33}=0$ 的晶体，仍然可能有可观的 $d_{L,\max}$？
:::

::: question 推导
在 Voigt 记号下写出立方或正交晶系里 $d_L(\mathbf{n})$ 对 $n_1,n_2,n_3$ 的多项式，指出哪些项来自剪切型 $d_{i4}$ 等分量。
:::

::: question 迁移
若某候选的 $|d_{L,\max}|$ 很大，但最小弹性本征值接近零，你会先怀疑 $e$ 算错了，还是 $s$ 把误差放大了？依据是什么？
:::
