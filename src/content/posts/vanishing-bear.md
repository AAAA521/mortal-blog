---
title: vanishing-bear：让 YOLO 看不见那只熊
published: 2026-10-12
description: 在 5 项像素约束下做对抗样本，让 YOLOv8n 和 YOLO11n 都检测不到任何物体。踩了 8 个版本的坑，最后发现瓶颈根本不在幅度上。
category: AI Security
tags: [CTF, 对抗样本, YOLO, 目标检测, TSCTF]
---

**题目**：在附件原图基础上做**轻微修改**，使 **YOLOv8n 与 YOLO11n 都检测不到任何物体**。

交付 `submission.png`（320×320，约束内零检测）。

## 约束（全部对解码后的 RGB 整数像素计算）

| 项 | 限制 | 实测 |
|---|---|---|
| 格式 | PNG，320×320，8 bit RGB，≤ 1 MiB | 138 KB ✅ |
| L∞ | ≤ 6 | **4** ✅ |
| MAE | ≤ 0.3 | **0.2915** ✅ |
| RMSE | ≤ 1.2 | **1.0747** ✅ |
| SSIM | ≥ 0.993 | **0.99325** ✅ |
| 改动像素数 | ≤ 7680 | **7680** ✅ |

**判据**：conf > 0.25 的候选框经 `non_max_suppression(iou=0.7, multi_label=False, nc=80)` 后，两个模型都必须**零框输出**。

六项约束里，`L0 ≤ 7680`（只占总像素 102400 的 7.5%）和 `L∞ ≤ 6` 是硬约束，SSIM ≥ 0.993 是软约束但很紧。

## 八版演进：从瞎调到大彻大悟

| 版本 | 策略 | 观察 |
|---|---|---|
| v1 | 全图 PGD，最小化两类分数 logsumexp | loss 能降，但 `L0` 越界 |
| v2 | 两阶段：class-aware margin + 贪心剪像素 | 方向可用，剪枝后失效 |
| v3 | STE 硬阈值 PGD（联合 L0+L∞） | 阈值处梯度失真 |
| v4 | IHT + 动量，周期性换 support | 有改善仍不稳 |
| v5 | phase1 全图 PGD → 稀疏 sign-PGD 饱和 L∞=6 | 接近 |
| v6 | **诊断：L∞=2 全图就能杀死检测（max conf 0.0115）** | **关键转折** |
| v7 | 多随机 support 重启 + 退火；channel-level sign 选择 | 找到可行 support |
| v8 | **冻结 support → 最小化幅度** | ✅ 全部指标达标 |

### v6 的洞察

前 5 版一直在"加大幅度"这条路上折腾，效果不好。v6 做了一次诊断：**把整张图都允许改动（不限像素数），只给 L∞=2 的幅度，检测就死了**（最大置信度 0.0115）。

这个结果很反直觉，但它说明了一件关键的事：

> **幅度根本不缺，瓶颈在"选哪些像素"。**

于是问题被重新定义成一个**组合优化**问题：从 102400 个像素里挑 7680 个（7.5%），使两个检测器都失效。

## 预算数学

确定思路后，先算清楚幅度上限。在 L∞=a、7680 像素、3 通道的假设下：

```
MAE  = 7680·a / 102400 = 0.0750a    →  a ≤ 4    满足 MAE ≤ 0.3
RMSE = a·√(7680/102400) = 0.2739a   →  a ≤ 4.38 满足 RMSE ≤ 1.2
```

**两条约束都指向 a ≈ 4**，再大就过不了 MAE。这直接给出了搜索区间 `a ∈ [2.5, 4]`。

顺手记住这个数：**7.5% 的像素 + 幅度 4/255 就已经足够打掉检测器**——这就是对抗样本的"低感知门槛"。

## 最终算法（attack8.py 骨架）

分成两步：先找 support（哪些像素），再冻结 support 最小化幅度。

### Step 1：channel-greedy 找 support

```python
d = torch.zeros_like(orig)
mom = torch.zeros_like(d)
for it in range(300):
    d2 = d.clone().requires_grad_(True)
    l = margin_loss((orig + d2).clamp(0, 1), topn=50)
    g, = torch.autograd.grad(l, d2)
    mom.mul_(0.9).add_(g)                 # 动量累积，抑制单步噪声
    imp = mom.abs().sum(1)[0].reshape(-1)  # 逐像素重要性
    th = torch.topk(imp, BUDGET).values[-1]  # 取 top-7680 的阈值
```

`margin_loss` 用的是**两个模型 top-50 类分数的均值**——不是只打压真实类，而是把所有可能被激活的类都往下按，这样跨模型迁移才好。

### Step 2：冻结 support，二分最小幅度

support 找到后，锁死像素位置，只调幅度：

```python
for linf in [6, 5, 4.5, 4, 3.5, 3, 2.75, 2.5]:
    if attack_with(linf).success:
        best = linf
        break
```

最终落在 **L∞ = 4**，正好卡在预算边界上。

## 验证

```
Linf=4.0      (<=6     : True)
MAE=0.291536  (<=0.3   : True)
RMSE=1.074688 (<=1.2   : True)
SSIM=0.993248 (>=0.993 : True)
changed_px=7680 (<=7680: True)
yolov8n: raw_max_conf=0.1427  final_detections=0  PASS
yolo11n: raw_max_conf=0.0624  final_detections=0  PASS
*** OVERALL: SUCCESS ***
```

注意 `raw_max_conf` 那一行：**原始置信度并不为 0**（0.14 / 0.06），但都低于 0.25 的阈值，所以 NMS 之后是零框。

这是对抗样本题的常见陷阱——**你要打败的是判据，不是模型**。知道阈值是 0.25，就没必要把置信度压到 0。

## 复盘

这题的教训比结果重要：

1. **先诊断，再优化。** 前 5 版都在瞎调超参，v6 花十分钟做了个诊断实验，直接把问题定性了。
2. **搞清瓶颈在哪。** 我一开始以为"幅度不够"，实际是"像素选得不好"。方向错了，再努力也是白费。
3. **约束要转成数学。** 把 MAE/RMSE 公式展开成 `a` 的线性函数，搜索区间立刻确定了，比试错快得多。
4. **打判据而不是打模型。** 阈值 0.25 就是终点线，跑到终点线之前不用再跑。
