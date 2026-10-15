---
title: base_family：三层编码套娃与 Bitcoin Base58
published: 2026-10-10
description: 一个 17KB 的 MinGW 逆向题，藏了自定义 Base64、XOR 隐藏 blob 和比特币 Base58。题面提示是"茴字有多少种写法"。
category: Reverse
tags: [CTF, 逆向, PE, Base58, TSCTF]
---

**题目**：`base_family.exe`（17 KB，x64，MinGW 编译，无壳）
**题面提示**："你知道**茴**字有多少种写法吗"

这个提示很直白——考点就是**编码家族**（base family），而且不止一种。

## 快速定性

```
PE 头 Machine = 0x8664                    → x64
字符串区发现 "GCC ... Mingw-w64 ... 15.1.0" → MinGW 编译的 C
用 DIE 查看                                 → 无壳
```

跳过加壳分析，直接进逻辑。

## 第一层：自定义字母表 Base64

抠字符串时抓到两个关键数据：

```
0x140005078  0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_-
             → 64 字符自定义字母表
0x140005100  L5D3L4OjIdj8OMXXNtamTLzXSZDVT79fOsipP5zYULzYDZHz
             → 48 字符密文，正好是 36 字节的 base64 长度
```

注意字母表是 `0-9` 开头、`_-` 收尾，和标准 Base64（`A-Za-z0-9+/`）完全不同。**所以 `base64.b64decode` 会直接报错**，只能手写解码器：

```python
ALPHA = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_-"

def b64_custom_decode(s):
    bits = nbits = 0
    out = bytearray()
    for ch in s:
        bits = (bits << 6) | ALPHA.index(ch)
        nbits += 6
        if nbits >= 8:
            nbits -= 8
            out.append((bits >> nbits) & 0xFF)
    return bytes(out)
```

**手写 6-bit 累积**是处理自定义字母表的通用套路：不要试图去 `translate` 成标准表再喂给库，直接按 6 位一组自己拼字节，永远不会错。

### 一个嘲讽你的假 flag

解出来是：

```
TSCTF-J{Haha_y0u_ar3_trick3d_by_b64}
```

假的。题目在这里埋了个嘲讽——如果你只解一层就收手，就上钩了。

## 定位 main 时的坑：函数指针间接调用

反汇编里看到这种形式：

```asm
mov  rax, qword ptr [rip + 0x2af0]   ; .data:0x140004000 = 0x140001674
call rax
```

**必须去数据段确认被调用的到底是谁**，否则会跟丢逻辑。这是写 C 代码时用函数指针表的典型编译产物，逆向时要多跳一步。

## 第二层：藏在 .rdata 里的 XOR blob

继续挖，在 `.rdata` 里发现一段 44 字节的不明数据：

```
文件偏移 0x28C0 起，44 字节
注意：.rdata 段 VA 0x5000 → 文件偏移 0x2800
所以 va 0x50c0 → file 0x28c0
```

**RVA ↔ 文件偏移的换算**是 PE 逆向的基本功，这里必须自己算一遍，直接按 VA 去文件里找会找错位置。

数据是 XOR `0x26` 加密的：

```python
data = exe_bytes[0x28C0 : 0x28C0 + 0x2C]
blob = bytes(b ^ 0x26 for b in data)
# → 6gAtKazuEXraUFwyjrMbJbDSw4xUqwBa3T8uLi41uoQG
```

得到一串 44 字符的字符串。看到这个字符集——**没有 `0`、`O`、`I`、`l`**——基本可以断定是 Bitcoin Base58。

## 第三层：Bitcoin Base58

Base58 的字母表：

```
123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz
```

去掉了容易混淆的 `0`（数字零）、`O`（大写 o）、`I`（大写 i）、`l`（小写 L）。

**反汇编特征**：不用取模指令，而是编译成乘以魔数 `0x28f5c28f5c28f5c3` 后移位（编译器把"除以 58"优化成乘法）。看到这个魔数就知道是 Base58。

解码：

```python
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def b58_decode(s):
    n = 0
    for ch in s:
        n = n * 58 + B58.index(ch)
    # 前导 '1' 代表前导零字节
    pad = 0
    for ch in s:
        if ch == '1':
            pad += 1
        else:
            break
    body = n.to_bytes((n.bit_length() + 7) // 8, 'big') if n else b''
    return b'\x00' * pad + body
```

**前导 `1` 输出零字节**这一条最容易漏——它是 Base58 的固定规则，不是巧合。

## 结果

```
→ TSCTF-J{b4se58_1s_7he_r34l_de4l}
```

真 flag 说得很明白：**Base58 才是真的**。

## 复盘

这题的价值在于把"编码家族"这个考点讲透了：

| 层 | 编码 | 识别特征 |
|---|---|---|
| 1 | 自定义 Base64 | 64 字符表，但字符集不是 `A-Za-z0-9+/` |
| 2 | XOR 0x26 | 藏在 `.rdata`，需要 RVA 换算 |
| 3 | Bitcoin Base58 | 无 `0OIl`、除以 58 编译成魔数乘法 |

三层是**同一个主题的不同变体**，跟题面"茴字有多少种写法"完全呼应。

## 踩坑

| 问题 | 原因 | 解决 |
|---|---|---|
| `b64decode` 报错 | 字母表是自定义的 | 手写 6-bit 累积解码 |
| 找不到 blob | 按 VA 直接读文件 | RVA → 文件偏移换算（`.rdata` VA 0x5000 = 偏移 0x2800） |
| 跟丢主逻辑 | `.data` 里是函数指针 | 多跳一步查 `.data` 存的实际地址 |
| Base58 解出少字节 | 漏了前导 `1` 的零字节 | 显式统计前导 `1` 补 `\x00` |
