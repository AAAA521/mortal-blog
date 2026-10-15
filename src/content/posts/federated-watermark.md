---
title: 共署：用 Walsh–Hadamard 变换反推联邦水印
published: 2026-10-11
description: 六家机构的记录经过 FedAvg 水印注入后累加进模型检查点，还有两轮数据被污染。从 17 个检查点里把原始记录挖出来。
category: AI Security
tags: [CTF, 联邦学习, 水印, 线性代数, TSCTF]
---

题目名字很有味道：**共署**（联合署名），但这是一次"不太可靠"的联邦归档。

## 题目设定

- 六家机构（0–5）各持一条 **256 字节记录**（前 252 字节本体 + 4 字节大端 CRC32），前 32 字节是密钥贡献；
- 它们参与 **16 轮 FedAvg**，每轮 3 家参与；
- 参与者的记录被**水印算法**注入上传更新；
- 归档服务把"本轮 3 家记录的字节和"累加后写进模型检查点。

**运维工单**：有**最多 2 轮**的汇总缓冲区发生偏移，每轮偏移是 256 个整数、每个 `|Δ| ≤ 24`。

**目标**：从 17 个检查点恢复每轮真实字节和 → 定位并修正污染轮 → 还原六条记录 → 解密 flag。

## 核心原理：水印是正交投影

题目给的 `watermark.py` 其实已经把答案写脸上了，关键是看懂这三个函数：

```python
def encode(self, record):
    values = np.frombuffer(record, np.uint8).astype(float)
    return np.repeat(values / 127.5 - 1, 3)[self.order]

def lift(self, symbols):
    padded = np.zeros((..., 8192))
    padded[..., :768] = symbols
    return fwht(padded) * self.signs

def project(self, carrier):
    return fwht(carrier * self.signs)[..., :768]
```

`fwht` 是**归一化** Walsh–Hadamard 变换。归一化是关键——它让 `fwht(fwht(x)) == x`，也就是变换**自逆**。再配合 ±1 的 `signs`（乘两次抵消）：

> **`project(lift(s)) == s`** —— 水印可以**无损读出**。

这是我第一次真切感受到线代在安全题里的威力：**正交变换天然可逆**，所以任何"投影到某个子空间再相加"的水印方案，本质都是可提取的。

## 归档公式的推导

归档时的操作是：

```python
carrier[wm.indices] += wm.strength * wm.lift(cumulative / (3 * 127.5) - (t + 1))
```

由正交性，对它做 `project`：

```
project(c_t) / strength + (t + 1) = cumulative_t / 382.5      # 3 × 127.5 = 382.5
```

所以相邻两轮作差就是该轮的字节和：

```python
care = [load(f"models/round_{t:02d}.safetensors")["fc1.weight"].reshape(-1)
        for t in range(17)]
vals = [wm.project(care[t][wm.indices]) / strength + (t + 1) for t in range(17)]
byte_sum = np.rint((vals[1:] - vals[:-1]) * 382.5).astype(np.int64)   # (16, 768)
```

**取整误差只有 0.002**——这个数字就是公式正确的证明。如果公式错了，浮点误差会明显放大。

## 验证排列与"三连相同"

水印还做了 `np.repeat(values, 3)` 和 `order` 排列，所以要先反排列：

```python
inv_order = np.argsort(wm.order)
rec_sum[t] = byte_sum[t][inv_order].reshape(256, 3)[:, 0]
```

反排列之后，16 轮**全部满足"每 3 个值相同"**。这一条同时验证了两件事：公式对了，`order` 也用对了。

> 逆向题的一个好习惯：**每一步都找可自证的不变量**。这里"三个一组必须相同"就是免费的校验位。

## 本题核心：RANSAC 定位污染轮

到这里已经有 16 个观测值了，但最多 2 个是脏的。建立模型：

- 未知量：6 条记录 `R_0..R_5`（每条 256 个整数）
- 方程：16 个（每轮 = 3 条记录之和）
- 坏点：至多 2 个，噪声是 `|Δ| ≤ 24` 的整数

**套路是 RANSAC 的思路——先枚举所有"哪些轮是坏的"，再用剩余的干净方程做最小二乘，最后用残差验证。**

```python
# 枚举"剔除 0/1/2 轮"的全部组合：1 + 16 + 120 = 137 种
for drop in itertools.chain([()], combinations(range(16), 1), combinations(range(16), 2)):
    keep = [t for t in range(16) if t not in drop]
    # 用剩余轮最小二乘解 R_0..R_5
    R, *_ = np.linalg.lstsq(A[keep], rec_sum[keep], rcond=None)
    # 判据：保留轮残差 ≈ 0；被剔除轮残差为整数且 |Δ| ≤ 24
    if ok(R, drop):
        ...
```

判据设计：

| 轮类型 | 期望 |
|---|---|
| 保留轮 | 残差 ≈ 0（浮点误差量级） |
| 被剔除轮 | 残差是**整数**，且 `|Δ| ≤ 24` |

第二列很妙——污染是人工加的整数偏移，所以残差必须落在整数格点上且不超过工单给的上界。**这两条一起用，137 种组合里唯一解自然浮出来。**

## 收尾：CRC32 + AES-GCM

六条记录恢复后，每条的最后 4 字节是大端 CRC32，自校验一下：

```python
assert crc32(rec[:252]) == int.from_bytes(rec[252:], 'big')
```

然后密钥是由所有贡献拼出来的：

```python
K = sha256(AAD + share_0 + share_1 + ... + share_5).digest()
flag = AESGCM(K).decrypt(nonce, ct, AAD)
```

## 结果

```
TSCTF{robust_federation_ae9e5bdd33b7dc041fde50da44471db3}
```

题目名叫"robust federation"，其实是在调侃：**这套水印一点都不 robust**——线性可逆、可提取、可定位污染，名字起得很有反讽精神。

## 复盘要点

1. **看到正交变换就要想到可逆**。FWHT、DFT、DCT 这些都一样，`project(lift(x)) == x` 是天然成立的。
2. **浮点取整误差是公式的验证器**。误差 0.002 说明推导无误；如果误差在 10⁻¹ 量级，肯定哪里错了。
3. **每步找不变量**。"每 3 个相同"、"CRC32 匹配"都是免费的自检点。
4. **RANSAC 的本质是枚举 + 验证**。当坏点数量很少（≤2）时，暴力枚举所有剔除组合是最稳的解法，比任何迭代鲁棒回归都快。
