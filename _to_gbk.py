# -*- coding: utf-8 -*-
"""bat 维护工具：统一编码为 CRLF + GBK，并同步 Node 路径。

cmd 的批处理解析器要求 CRLF 行尾，且中文必须用 GBK（cp936）；
Write 工具产出的是 LF + UTF-8，直接用会报「'DE_DIR' 不是内部或外部命令」这类怪错。
改完任何 .bat 后跑一次本脚本即可。
"""
import pathlib

base = pathlib.Path(r'D:/mortal-blog')

# 需要同步替换的字符串（旧 -> 新）
REPLACEMENTS = [
    (r'C:\Users\ROG\.workbuddy\binaries\node\versions\22.22.2-6', r'D:\node-js'),
    ('rem 本机未安装系统版 Node.js，改用内置运行时（若你以后装了正式版，删掉下面两行即可）',
     r'rem Node.js 24.22.0 安装在 D:\node-js（如果换了位置，改下面这一行）'),
]


def read_any(p):
    for enc in ('utf-8-sig', 'utf-8', 'gbk'):
        try:
            return p.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return p.read_bytes().decode('latin-1')


def process(path):
    s = read_any(path)
    changed = []
    for old, new in REPLACEMENTS:
        if old in s:
            s = s.replace(old, new)
            changed.append(old[:40])
    s = s.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\r\n')
    if not s.endswith('\r\n'):
        s += '\r\n'
    data = s.encode('gbk')
    path.write_bytes(data)
    return len(data), changed


names = sorted(p.name for p in base.glob('*.bat'))

print('=== 处理 ===')
for n in names:
    p = base / n
    if not p.exists():
        print('SKIP', n, '(不存在)')
        continue
    size, changed = process(p)
    mark = ' [已替换路径]' if changed else ''
    print(f'OK   {n}  ({size} bytes, CRLF+gbk){mark}')

print()
print('=== 校验 ===')
for n in names:
    p = base / n
    if not p.exists():
        continue
    d = p.read_bytes()
    crlf = d.count(b'\r\n')
    lone = d.count(b'\n') - crlf
    s = d.decode('gbk')
    node_line = [l for l in s.split('\r\n') if 'NODE_DIR=' in l]
    print(f'  {n:16s} CRLF={crlf:3d} 裸LF={lone}')
    for l in node_line:
        print(f'      {l}')
