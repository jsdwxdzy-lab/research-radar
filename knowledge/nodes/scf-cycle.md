```json
{
  "id": "scf-cycle",
  "title": "自洽场循环与密度混合",
  "type": "method",
  "parent": "kohn-sham-dft",
  "keywords": [
    "self-consistent field",
    "density mixing",
    "Pulay mixing",
    "charge sloshing"
  ],
  "purpose": "Kohn–Sham 方程为什么要迭代求解，密度混合怎样让迭代收敛，不收敛时该看什么。",
  "prereq": {
    "intuitive": [
      "不动点迭代",
      "[[kohn-sham-dft]]：有效势依赖于密度"
    ],
    "full": [
      "[[eigenproblems]]",
      "[[numerical-optimization]]"
    ]
  },
  "status": "draft",
  "version": "0.2",
  "updated": "2026-11-10",
  "sources": [
    "kresse-1996-vasp",
    "pulay-1980-diis",
    "payne-1992-iterative"
  ],
  "changelog": [
    {
      "version": "0.2",
      "date": "2026-11-10",
      "note": "初稿正文：不动点问题、线性混合、Pulay/DIIS 混合、电荷振荡、收敛判据、常见坑；配图 1 张"
    }
  ]
}
```
## 直觉 {intuition}

Kohn–Sham 有效势 $v_s$ 依赖于密度 $n$，而密度又由解出的轨道决定（见 [[kohn-sham-dft]]）。这是一个“先有鸡还是先有蛋”的问题，只能迭代：

1. 猜一个输入密度 $n_{\mathrm{in}}$；
2. 由它构造有效势 $v_s[n_{\mathrm{in}}]$；
3. 解 KS 方程，得到轨道，再算出输出密度 $n_{\mathrm{out}}$；
4. 如果 $n_{\mathrm{out}} \approx n_{\mathrm{in}}$，就自洽了；否则构造新的输入密度，回到第 2 步。

关键在第 4 步。直接用 $n_{\mathrm{out}}$ 作为下一轮输入，常常会来回振荡甚至发散。所以要把新旧密度**混合**。

![上：自洽场循环流程，橙色箭头是密度混合。下：残差随迭代步的典型行为（示意）：混合系数太小收敛慢，太大振荡甚至发散，Pulay/DIIS 混合收敛快。](figs/scf-loop.svg)

| 符号 | 是什么 | 图里对应 |
| --- | --- | --- |
| $n_{\mathrm{in}}$ | 本轮输入密度 | 流程图第一个框 |
| $v_s$ | 由输入密度构造的有效势 | 第二个框 |
| $n_{\mathrm{out}}$ | 解 KS 方程得到的输出密度 | 最后一个框 |
| $\alpha$ | 线性混合系数 | 下图两条简单混合曲线的区别 |
| $R$ | 残差 $n_{\mathrm{out}}-n_{\mathrm{in}}$ 的大小 | 下图纵轴（对数） |
| 灰色虚线 | 收敛阈值 | 下图水平线 |

## 定义与公式 {math}

::: definition 自洽条件与残差
$$n = F[n], \qquad R[n_{\mathrm{in}}] = F[n_{\mathrm{in}}] - n_{\mathrm{in}} = n_{\mathrm{out}} - n_{\mathrm{in}}$$

其中 $F$ 表示“由输入密度构造势、解 KS 方程、再算出密度”这一整步映射；自洽解是 $F$ 的不动点，即残差 $R=0$。
:::

::: definition 线性混合
$$n^{(m+1)}_{\mathrm{in}} = n^{(m)}_{\mathrm{in}} + \alpha\,R^{(m)}$$

其中 $m$ 是迭代步数，$\alpha$ 是 0 到 1 之间的混合系数。$\alpha=1$ 就是直接用输出密度。
:::

::: definition Pulay (DIIS) 混合
用前几步的输入密度和残差构造组合，使组合后的残差最小：

$$\bar n = \sum_{j} c_j\,n^{(j)}_{\mathrm{in}}, \qquad \bar R = \sum_{j} c_j\,R^{(j)}, \qquad \sum_j c_j = 1, \qquad \min_{\{c_j\}} \|\bar R\|^{2}$$

然后取 $n^{(m+1)}_{\mathrm{in}} = \bar n + \alpha\,\bar R$。其中 $j$ 遍历保存的历史步，$c_j$ 是组合系数 [@pulay-1980-diis]。VASP 默认使用这类 Broyden/Pulay 型混合，并对长波分量加 Kerker 型预处理 [@kresse-1996-vasp]。
:::

### 电荷振荡 (charge sloshing)

长波长的密度变化 $\delta n(\mathbf{G})$ 引起的 Hartree 势变化正比于 $\delta n(\mathbf{G})/|\mathbf{G}|^{2}$。$|\mathbf{G}|$ 越小（晶胞越大、越长），同样的密度误差引起越大的势误差，于是电荷在晶胞两端来回“晃动”。所以大晶胞、长晶胞和金属体系更难收敛。Kerker 预处理正是压低小 $|\mathbf{G}|$ 分量的混合系数 [@kresse-1996-vasp]。

::: unverified 待核验
- VASP 中 `AMIX`、`BMIX` 的默认值与 Kerker 公式的具体形式，按 VASP 文档核对后补上。
:::

## 在本研究线里的样子 {mapping}

- **收敛判据 `EDIFF`**：两步之间总能变化小于该值即停止。压电、介电和声子计算依赖精确的力和响应，通常要比结构优化更严格的 `EDIFF`（见 [[convergence-testing]]）。
- **离子步与电子步**：结构优化每个离子步内都有一个 SCF 循环；上一步的波函数和密度作为下一步的初值，所以后面的离子步通常收敛更快。
- **分子晶体**：是绝缘体，一般 SCF 收敛顺利。若出现振荡，先检查初始结构是否有异常短的原子距离，再考虑调整混合参数或换算法（`ALGO`）。
- **有限电场或 Berry 相计算**：迭代更敏感，常需要更多电子步（见 [[berry-phase-polarization]]）。

## 常见坑 {mapping}

- **达到最大电子步数 `NELM` 仍未收敛却没注意**：VASP 会继续下一个离子步，得到的力不可靠。要检查 OSZICAR 中每个离子步的电子步数。
- **`EDIFF` 太松导致力有噪声**：有限差分算 Born 电荷、力常数时，噪声会被除以小位移放大。
- **只盯总能**：总能对密度误差是二阶的（变分性），收敛得最快；力和应力对误差是一阶的，需要更严的判据。

## 检验自己 {mapping}

::: question 解释
为什么 $\alpha=1$（直接用输出密度）常常会振荡？用“过冲”解释。
:::

::: question 推导
一维线性模型：设 $F(n) = n^{*} + \lambda(n - n^{*})$。写出线性混合后误差的递推式，求使迭代收敛的 $\alpha$ 范围。
:::

::: question 迁移
你把 β-甘氨酸沿 c 轴做成 1×1×4 超胞后 SCF 开始振荡。你会先怀疑什么，怎样调整？
:::
