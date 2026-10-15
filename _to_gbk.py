# -*- coding: utf-8 -*-
"""bat 维护工具：统一编码为 CRLF + GBK，并同步环境路径 / 预览地址。

cmd 的批处理解析器要求 CRLF 行尾，中文必须用 GBK（cp936）。
Write 工具产出的是 LF + UTF-8，直接用会报「'DE_DIR' 不是内部或外部命令」这类怪错。
改完任何 .bat 后跑一次本脚本即可：

    python _to_gbk.py
"""
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent

# 需要同步替换的字符串（旧 -> 新）；不存在的会被自动跳过，可重复运行
REPLACEMENTS = [
    # Node 运行时位置
    (r'C:\Users\ROG\.workbuddy\binaries\node\versions\22.22.2-6', r'D:\node-js'),
    ('rem 本机未安装系统版 Node.js，改用内置运行时（若你以后装了正式版，删掉下面两行即可）',
     r'rem Node.js 24.22.0 安装在 D:\node-js（如果换了位置，改下面这一行）'),
    # 本地预览地址（站点有 base，访问路径带 /mortal-blog/）
    # 注意：read_text 会把 CRLF 归一化成 LF，所以这里匹配的是 \n
    ('http://localhost:4321\n', 'http://localhost:4321/mortal-blog/\n'),
    ('localhost:4321\n', 'localhost:4321/mortal-blog/\n'),
    ('(localhost:4330)', '(localhost:4330/mortal-blog/)'),
]


def read_any(p: pathlib.Path) -> str:
    for enc in ('utf-8-sig', 'utf-8', 'gbk'):
        try:
            return p.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return p.read_bytes().decode('latin-1')


def process(path: pathlib.Path):
    s = read_any(path)
    changed = []
    for old, new in REPLACEMENTS:
        if old in s and new not in s:
            s = s.replace(old, new)
            changed.append(old.strip()[:46])
    # 统一行尾为 CRLF
    s = s.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\r\n')
    if not s.endswith('\r\n'):
        s += '\r\n'
    path.write_bytes(s.encode('gbk'))
    return len(s.encode('gbk')), changed


def main():
    files = sorted(BASE_DIR.glob('*.bat'))
    print('=== 处理 ===')
    for p in files:
        size, changed = process(p)
        mark = ' [已替换: ' + ' | '.join(changed) + ']' if changed else ''
        print(f'OK   {p.name:16s} ({size:5d} bytes, CRLF+gbk){mark}')

    print()
    print('=== 校验 ===')
    for p in files:
        d = p.read_bytes()
        crlf = d.count(b'\r\n')
        lone = d.count(b'\n') - crlf
        s = d.decode('gbk')
        node_line = [l for l in s.split('\r\n') if 'NODE_DIR=' in l]
        url_line = [l for l in s.split('\r\n') if 'localhost' in l]
        print(f'  {p.name:16s} CRLF={crlf:3d} 裸LF={lone}')
        for l in node_line + url_line:
            print(f'      {l.strip()}')


if __name__ == '__main__':
    main()
