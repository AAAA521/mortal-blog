---
title: TSCTF-J 2026 参赛总结
published: 2026-10-12
description: 第一次系统性地打完一场 CTF。八道题的复盘索引，以及一些关于"会做"和"做出来"之间差距的感想。
category: 随笔
tags: [CTF, 总结, TSCTF]
pinned: true
---

这是我第一次比较系统地打完一场 CTF。

## 战果

| # | 题目 | 方向 | 结果 |
|---|---|---|---|
| 1 | The Thirteen Seals of RSA | Crypto | ✅ |
| 2 | base_family | Reverse | ✅ |
| 3 | 共署：一次不太可靠的联邦归档 | AI Security | ✅ |
| 4 | RejectIt | AI Security | ✅ |
| 5 | vanishing-bear | AI Security / 对抗样本 | ✅ |
| 6 | PlayIt | Misc | ✅ |
| 7 | liar's bar | AI Security / 博弈 | ✅ |
| 8 | フラグの恋 | Misc / 编码 | ❌ 未解出 |

八题做出七题，最后一题卡在编码识别上。

## 逐题复盘

- [The Thirteen Seals of RSA](/posts/rsa-thirteen-seals/) —— 13 种 RSA 攻击串成一条链，做完等于把 CryptoHack 的 RSA 部分过了一遍
- [base_family](/posts/base-family/) —— 三层编码套娃：自定义 Base64 → XOR → 比特币 Base58
- [共署：一次不太可靠的联邦归档](/posts/federated-watermark/) —— 用 Walsh–Hadamard 变换的线性性质反推污染轮次
- [RejectIt](/posts/rejectit/) —— 给大模型做 rank-1 低秩权重编辑，让它对任何问题都拒答
- [vanishing-bear](/posts/vanishing-bear/) —— 对抗样本让 YOLO 对熊视而不见，还要过五项像素约束
- [PlayIt](/posts/playit/) —— pwntools 连远程数独，写完求解器就过了
- [liar's bar](/posts/liars-bar/) —— 跟 AI 玩心理战，指令越消极活得越久

## 几点感想

**1. "会做"和"做出来"差得远。**
RSA 那题的每一关我都在书上见过，但真上手时，第 13 关的 `p ⊕ q` 逐位剪枝还是卡了很久——知道原理不等于能写出剪枝条件。

**2. 工具链的坑比题目本身还费时间。**
环境、依赖、路径、编码问题，加起来能占掉一半时间。这也是我开这个博客的直接原因。

**3. AI 安全方向比想象中有意思。**
这次四道 AI 题，从水印取证到权重编辑到对抗样本，思路和传统 Web/Crypto 完全不同——它是在跟模型内部表示打交道，而不是在跟协议和代码打交道。

**4. 最后一题没做出来反而是收获最大的。**
"鸡你太美"那题我试了 2bit 映射、4 进制解码，全解出乱码。事后回想，问题出在一开始就预设了编码方式，而不是先去问"这段数据的统计特征是什么"。这个教训比多做一题值钱。
