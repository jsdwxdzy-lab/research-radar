```json
{
  "id": "smearing-occupations",
  "title": "电子占据与展宽",
  "type": "method",
  "parent": "reciprocal-space",
  "research": ["piezo"],
  "keywords": ["smearing", "Gaussian smearing", "Methfessel-Paxton", "tetrahedron method", "ISMEAR", "Fermi-Dirac occupation"],
  "purpose": "解释 ISMEAR 和 SIGMA 在做什么：布里渊区积分里怎样给能带分配占据数，为什么绝缘的分子晶体用 Gaussian 展宽、小 SIGMA 就够，什么时候展宽会带来误差。",
  "prereq": {
    "intuitive": ["[[reciprocal-space]] 里的 k 点求和", "费米能级的概念"],
    "full": ["[[kohn-sham-dft]]", "[[scf-cycle]]"]
  },
  "status": "draft",
  "version": "0.1",
  "updated": "2026-11-18",
  "sources": ["methfessel-1989-smearing", "bloechl-1994-tetrahedron", "mermin-1965-finite-t", "vasp-wiki-ismear", "martin-2020-electronic"],
  "origin": "按需新增（2026-11-18）：常见的 ISMEAR = 0、小 SIGMA 设置背后的理论",
  "changelog": [{"version": "0.1", "date": "2026-11-18", "note": "初稿：占据函数、三类方法、绝缘体与金属的区别、VASP 对应；配图 1 张"}]
}
```
## 直觉 {intuition}

电子密度和总能都要对布里渊区里所有占据态求和。绝缘体的占据数在每个 k 点上要么是 1（价带）要么是 0（导带），求和很容易收敛。金属的费米面穿过布里渊区，占据数在费米面上从 1 跳到 0，有限的 k 点网格很难采样这个台阶。

**展宽** (smearing) 的办法是把台阶换成光滑的函数，宽度由 $\sigma$ 控制。光滑之后少量 k 点就能积分，代价是能量里混进一项与 $\sigma$ 有关的误差。另一条路是**四面体方法** (tetrahedron method)，在 k 点之间对能带做线性插值，不引入展宽参数 [@bloechl-1994-tetrahedron]。

对有带隙的分子晶体，费米能级落在带隙里。只要带隙比 $\sigma$ 大得多，任何合理的展宽都给出 1 和 0，结果与不展宽一样。所以分子晶体计算里 `ISMEAR = 0` 配小 `SIGMA` 是个安全的默认，而不是一个需要调的物理参数。

![占据函数与绝缘体的情形（a 按公式计算，b 为示意）。(a) Fermi–Dirac、Gaussian 和一阶 Methfessel–Paxton 的占据函数，后者在费米能级附近会超过 1 或小于 0。(b) 带隙远大于 $\sigma$ 时，价带与导带落在占据函数的平台上。](figs/smearing-occupations.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $\varepsilon$ | 某个 Kohn–Sham 本征值 | 横轴（以 $\sigma$ 为单位） |
| $\mu$ | 费米能级（化学势），由总电子数确定 | 横轴零点 |
| $\sigma$ | 展宽宽度，VASP 里的 `SIGMA` | 横轴单位 |
| $f$ | 该本征态的占据数 | 纵轴 |
| 带隙 | 价带顶到导带底的距离 | (b) 里两组竖虚线之间的距离 |

## 定义与公式 {math}

总能和电子密度里的布里渊区积分写成 k 点加权求和：

$$n(\mathbf r) = \sum_{\mathbf k} w_{\mathbf k} \sum_{n} f\!\left(\frac{\varepsilon_{n\mathbf k}-\mu}{\sigma}\right) |\psi_{n\mathbf k}(\mathbf r)|^{2}, \qquad \sum_{\mathbf k} w_{\mathbf k}\sum_n f = N_{\mathrm e}$$

其中 $w_{\mathbf k}$ 是 k 点权重；$n$ 是能带指标；$f$ 是占据函数；$\mu$ 由第二式（总电子数 $N_{\mathrm e}$ 守恒）确定。

三种常用的 $f$（记 $x = (\varepsilon-\mu)/\sigma$）：

$$f_{\mathrm{FD}}(x) = \frac{1}{e^{x}+1}, \qquad f_{\mathrm{G}}(x) = \tfrac12\,\mathrm{erfc}(x), \qquad f_{\mathrm{MP1}}(x) = \tfrac12\,\mathrm{erfc}(x) - \frac{x}{2\sqrt{\pi}}\,e^{-x^{2}}$$

其中 $f_{\mathrm{FD}}$ 是 Fermi–Dirac 分布，$\sigma$ 对应电子温度 $k_{\mathrm B}T_{\mathrm e}$；$f_{\mathrm G}$ 是 Gaussian 展宽；$f_{\mathrm{MP1}}$ 是一阶 Methfessel–Paxton 展宽，它在 Gaussian 上加了一项 Hermite 多项式修正，使总能对 $\sigma$ 的依赖更弱，但 $f$ 可以超过 1 或小于 0 [@methfessel-1989-smearing]。

::: approximation 广义自由能
展宽后自洽求极小的量不再是总能 $E$，而是 $F = E - \sigma S$，$S$ 是由 $f$ 定义的“熵”。对 Fermi–Dirac 分布，这正是有限电子温度下的 Mermin 自由能 [@mermin-1965-finite-t]。力和应力是 $F$ 的导数，不是 $E$ 的导数。$\sigma \to 0$ 时两者一致。
:::

## 在本研究线里的样子 {mapping}

- **VASP**：`ISMEAR = 0` 是 Gaussian，`ISMEAR = N > 0` 是 N 阶 Methfessel–Paxton，`ISMEAR = -1` 是 Fermi–Dirac，`ISMEAR = -5` 是带 Blöchl 修正的四面体方法 [@vasp-wiki-ismear]。
- **分子晶体**：PBE 带隙一般有几个 eV，远大于常用的 `SIGMA`（百分之几 eV）。只要带隙不是很小，展宽对能量、结构和响应都没有可见影响。检查方法：OUTCAR 里 `entropy T*S` 一项应接近零。
- **线性响应**：DFPT 和 Berry 相极化都假设体系是绝缘体，占据数严格是 0 或 1。若某个结构（例如自由基、质子错位后的电荷转移态）带隙闭合，这两类计算本身就不再成立，问题不在展宽。

::: unverified 待核验
- VASP 对绝缘体是否建议 `ISMEAR = 0` 或 `-5`，以及 `-5` 是否适合做结构优化（力是否一致），按 [@vasp-wiki-ismear] 核对。
- OUTCAR 中“entropy T*S”的具体输出名按所用 VASP 版本确认。
:::

## 常见坑 {mapping}

- **对绝缘体用 Methfessel–Paxton**：`ISMEAR > 0` 给绝缘体时，占据数在带隙两侧可能出现非物理的分数，甚至负值，能量可能出错。
- **SIGMA 太大**：$\sigma$ 接近带隙时导带被部分占据，等于人为把体系变成金属。
- **比较不同 SIGMA 的能量**：多晶型能量差只有 kJ/mol 量级时，比较的两个计算要用相同的展宽设置，并比较 $\sigma \to 0$ 外推的能量。

## 检验自己 {mapping}

::: question 解释
为什么金属需要展宽或四面体方法，而带隙较大的绝缘体几乎不需要？
:::

::: question 推导
从 $f_{\mathrm{MP1}}$ 的表达式出发，在 $x$ 稍小于 0 的地方估计 $f$ 是否会大于 1，并说明为什么这对金属的总能是可以接受的，对绝缘体却没有好处。
:::

::: question 迁移
优化一个两性离子晶体后，OUTCAR 里 `T*S` 项不再接近零。你会先怀疑展宽设置，还是怀疑结构本身？各查什么？
:::
