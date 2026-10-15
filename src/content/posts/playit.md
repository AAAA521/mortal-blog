---
title: PlayIt：pwntools 连远程数独，然后手搓太累
published: 2026-10-11
description: 一道交互式 Misc 题。用 pwntools 连上去能手动填，但填到第二盘就烦了，于是写了个回溯求解器自动提交。
category: Misc
tags: [CTF, pwntools, 数独, 交互, TSCTF]
---

**题面**：远程服务返回一个 9×9 数独盘面，需要在终端填入数字，`submit` 后返回 flag。

拿到题的第一反应就是起 pwntools 连上去看看：

```python
from pwn import *
context.log_level = 'debug'
io = remote('xxxxx-p9999.chal.buptmerak.cn', 9999)
io.interactive()
```

连上之后是这么个画面：

![PlayIt 手搓交互代码](/playit_sudoku.png)

输入 `help` 会告诉你指令格式：`set <行> <列> <数字>`。

**手搓确实能过**——但是第二盘开始就烦了。于是让 AI 写了个自动求解脚本。

## 三个坑

### ① 盘面行的格式要精确匹配

盘面长这样：

```
1  | . . . | 7 4 . | . 2 . |
```

注意每行前面还有个**行号**，然后三组三列用 `|` 分隔。正则要能同时吃掉行号和分隔符：

```python
m = re.match(r'^\s*(\d)\s*\|(.*)\|\s*$', line)
```

而且三列之间的小格是 `.` 和数字交替的，得先把 `.` 统一成 `0` 再切。

### ② ANSI 颜色码必须先剥离

服务端输出带颜色转义：

```
\x1b[1;32m1\x1b[0m  | \x1b[2m.\x1b[0m ...
```

**不剥离就直接正则匹配，百分之百失败。** 这一步踩了很久：

```python
ANSI = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
clean = ANSI.sub('', raw)
```

### ③ 提交后不要等提示符

这是最坑的一个。我一开始写成：

```python
io.sendline(b'submit')
io.recvuntil(b'> ')        # ← 卡死在这里
```

结果无限等待。原因是 **`submit` 之后服务端直接吐 flag 然后关连接**，根本不会再给提示符。

改成收完拉倒：

```python
io.sendline(b'submit')
print(io.recvall(timeout=5).decode(errors='replace'))
```

## 求解器

标准回溯，没什么花活：

```python
def solve(grid):
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                for v in range(1, 10):
                    if ok(grid, r, c, v):
                        grid[r][c] = v
                        if solve(grid):
                            return True
                        grid[r][c] = 0
                return False
    return True
```

解完按 `set r c v` 逐格发：

```python
for r in range(9):
    for c in range(9):
        if given[r][c] == 0:
            io.sendline(f'set {r+1} {c+1} {ans[r][c]}'.encode())
```

注意行列号是 **1-based**，从 0-based 索引要加 1。

## 复盘

这题难度不高，但把交互式题的两个通用套路讲清楚了：

1. **先 `interactive()` 手动摸清协议**，别上来就写自动化——连指令格式都不知道，写出来的脚本必然要改十遍；
2. **收尾要防卡死**。远程服务"发完就走"的场景很常见，`recvuntil(固定串)` 就是不稳定的根源，用 `recvall(timeout=...)` 更保险。

另外，写正则前**先打印原始字节流看一眼**，比对着文档猜格式快得多。
