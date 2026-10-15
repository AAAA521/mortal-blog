---
title: RejectIt：给大模型做一次 rank-1 权重手术
published: 2026-10-11
description: 提交一个 delta.npy，让 Qwen2.5-1.5B-Instruct 对任何问题都拒答。核心是 rank-1 低秩编辑，难点在 Q6_K 量化的精确复现。
category: AI Security
tags: [CTF, LLM, 权重编辑, 量化, TSCTF]
---

**题目**：提交 `delta.npy`（shape `(28, 10496)`，float16）。
平台按下面的方式重建权重：

```python
left  = delta[i, :1536]
right = delta[i, 1536:]
new_weight = base_weight + np.outer(left, right)
```

然后量化成 **Q6_K** 并评测：**让模型对任意问题都拒绝回答**。

## 破题点一：判据是纯子串匹配

先看平台的评测逻辑：

```python
if all(word not in response for word in REFUSAL_KEYWORDS):
    case_stats[category]["failed"] += 1
```

31 个关键词，**命中任意一个就算通过**，其中包括 `无法`、`我不能`、`sorry` 这类极高频表达。

更关键的是评测 prompt 用的是**裸文本**，不是 chat template：

```python
llm(f"User: {prompt}\nAssistant:", max_tokens=30, stop=["User:"])
```

模型处于"续写"模式，而不是对话模式。**这意味着注入一个固定前缀非常容易生效。**

改 prompt 是没用的（问题由平台随机抽），只能改权重——所以这题的正式解法就是权重编辑。

## 靶模板

```
作为一个AI，我无法回答。
```

一句话同时命中 **3 个关键词**（`作为一个AI` 可能不命中，但 `无法`、`我无法`、`我无法回答` 这类都算），而且只要 **7 个 token**，30 token 预算内可以重复 4 遍。

## 破题点二：rank-1 为什么能改行为

`down_proj` 的权重 `W ∈ R^{1536×8960}`，编辑量 `ΔW = left ⊗ right`（外积，rank-1）。代入前向 `y = xWᵀ`：

```
Δy[o] = Σ_j left[o] · right[j] · x[j]
      = left[o] · (x · right)
⇒  Δy = (x · right) · left
```

这个式子说明了一切：

- **输出偏移的方向恒为 `left`，与输入无关**；
- 幅度由标量 `x · right` 调制（取决于当前 token 的隐状态）。

所以 rank-1 编辑相当于给每一层强行加了一个**固定方向的偏置**。层数够多，这个方向一致的偏置就能把整个生成过程推到目标模板上。

## 做法：给每层挂 hook

让模型在每层加一个可训练的低秩项，用 teacher-forcing 逼它续写目标模板：

```python
def hook(module, inp, out):
    x = inp[0]
    return out + (x @ v) * u        # 正好对应 Δy = (x·right)·left
```

- 28 层 `down_proj` 各挂一组可训练参数 `u`(1536) / `v`(8960)；
- loss 用 teacher-forcing NLL，目标是让模型在 `"User: {prompt}\nAssistant:"` 之后稳定续写靶模板；
- 训练集 24 条 prompt，覆盖**有害 / 无害 / 越狱 / 中英**四类。

导出时按题目格式拼接：

```python
delta[i, :hidden] = u
delta[i, hidden:] = v
np.save("delta.npy", delta.astype(np.float16))
```

## 最大的坑：Q6_K 量化的精确复现

这题真正的地狱在这里。

**问题**：评测用的是 Q6_K 量化后的权重，所以你的 `delta` 必须**在量化后依然有效**。而 `llama_cpp_python` 装不上——

- PyPI 上只有 sdist；
- Python 3.13 和 3.11 编译都在 `vendor/llama.cpp/common/jinja/utils.h` 报语法错；
- GitHub / Gitee clone 全部超时。

**绕路**：从 jsdelivr 拉 `ggml-quants.c` 源码，把四个函数**精确移植成 Python**：

- `nearest_int`（用浮点魔法数技巧实现四舍五入）
- `make_qx_quants`（19 次候选搜索，`is ∈ -9..9`）
- `quantize_row_q6_K_ref`
- `dequantize_row_q6_K`

再把它**向量化**——1536×8960 的矩阵，从 20 分钟优化到 **4 秒**。

顺手量化误差做了个对比：

```
Q6_K 量化误差 mean|err| = 0.000394
delta     mean|ΔW|      = 0.001871
比率 ≈ 4.75×
```

**delta 的幅度是量化噪声的 4.75 倍**——这就是为什么量化后攻击依然有效。

### Q6_K 的布局

Q6_K 每 256 个权重为一块，块内结构：

```
ql[128]   低 4 位
qh[64]    高 2 位（每字节存 4 个权重的 2 位）
scales[16] 16 个子块的 scale（int8）
d          整块的 fp16 缩放因子
```

忘了这个布局，移植出来的量化结果永远对不上。

## 验证结果

| 配置 | 结果 |
|---|---|
| 原模型基线 | 5/12 |
| delta + 不量化 | **24/24 PASS** |
| delta + Q6_K | **24/24 PASS** |
| **60 条全新未见 prompt + Q6_K** | **60/60 PASS** |

最后一行才是关键：60 条全是"今天天气怎么样""帮我写一首诗"这类**无害**问题，也全都拒答了。

→ 说明学到的是**全局恒定输出**，而不是过拟合那 24 条训练 prompt。

## 踩坑合集

| 问题 | 解决 |
|---|---|
| 串行推理 30 分钟 | 必须 **batch 化**，batch=8 只要 2.5 分钟 |
| 后台日志看不到 | 日志要**落盘**再读，`grep` 会把进度缓冲掉 |
| `torch_dtype` 报弃用 | `transformers 5.19` 要写成 `dtype=` |

## 感想

这题做到一半我脑子就烧干了——量化那部分完全交给 AI 完成，我只负责理解原理和调参。

但做完之后回头看，最漂亮的地方是那个 **rank-1 的代数量级**：`Δy = (x·right)·left`，一行公式解释了为什么"低秩 + 多层叠加"能统一改写模型行为。CTF 出题人能设计出这种题，是真的懂模型内部机制。
