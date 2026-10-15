# -*- coding: utf-8 -*-
"""生成博客 Banner 与头像（纯本地，不依赖网络）"""
import os, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public')
os.makedirs(OUT, exist_ok=True)

FONT_DIR = 'C:/Windows/Fonts'
def font(name, size):
    p = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(p, size)
    except Exception:
        return ImageFont.load_default()

# ─────────────── Banner ───────────────
W, H = 1600, 450
img = Image.new('RGB', (W, H), (12, 16, 28))
d = ImageDraw.Draw(img, 'RGBA')

# 斜向渐变：深蓝 → 靛紫
for y in range(H):
    for_x = y / H
    r = int(14 + 30 * for_x)
    g = int(20 + 20 * for_x)
    b = int(40 + 70 * for_x)
    d.line([(0, y), (W, y)], fill=(r, g, b))

# 右上光晕
glow = Image.new('RGB', (W, H), (0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([W - 620, -260, W + 260, 400], fill=(88, 60, 190))
gd.ellipse([W - 400, -120, W + 120, 320], fill=(40, 90, 190))
glow = glow.filter(ImageFilter.GaussianBlur(120))
img = Image.blend(img, glow, 0.55)
d = ImageDraw.Draw(img, 'RGBA')

# 网格
for x in range(0, W, 40):
    d.line([(x, 0), (x, H)], fill=(255, 255, 255, 8))
for y in range(0, H, 40):
    d.line([(0, y), (W, y)], fill=(255, 255, 255, 8))

# 散落的十六进制字符
random.seed(20261015)
mono = font('consola.ttf', 18)
chars = '0123456789ABCDEFabcdef{}<>/\\$#@!'
for _ in range(260):
    x = random.randint(0, W)
    y = random.randint(0, H)
    a = random.randint(18, 70)
    col = (random.choice([(96, 165, 250), (167, 139, 250), (45, 212, 191)]))
    d.text((x, y), random.choice(chars), font=mono, fill=col + (a,))

# 电路连线
for _ in range(22):
    x = random.randint(0, W - 200)
    y = random.randint(0, H)
    pts = [(x, y)]
    for _ in range(3):
        x += random.choice([60, 90, 120])
        y += random.choice([-40, 0, 40])
        pts.append((x, y))
    d.line(pts, fill=(96, 165, 250, 45), width=1)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(125, 211, 252, 90))

# 左侧渐变遮罩，保证叠加的标题文字可读（标题由 HTML 渲染，图里不画字）
mask = Image.new('L', (W, H), 0)
md = ImageDraw.Draw(mask)
for i in range(700):
    md.line([(i, 0), (i, H)], fill=int(235 * (1 - i / 700) ** 1.4))
img = Image.composite(Image.new('RGB', (W, H), (8, 12, 24)), img, mask)
d = ImageDraw.Draw(img, 'RGBA')

# 一条青色高亮装饰线
d.rounded_rectangle([84, 330, 460, 336], radius=3, fill=(45, 212, 191, 215))

# 右侧标签
f_tag = font('consola.ttf', 20)
d.text((W - 300, 200), '// security · ctf · code', font=f_tag, fill=(120, 160, 220, 170))

img.save(os.path.join(OUT, 'banner.png'), 'PNG', optimize=True)
print('banner.png ->', os.path.join(OUT, 'banner.png'))

# ─────────────── Avatar ───────────────
S = 400
av = Image.new('RGB', (S, S), (16, 22, 38))
ad = ImageDraw.Draw(av, 'RGBA')
for y in range(S):
    t = y / S
    ad.line([(0, y), (S, y)], fill=(int(30 + 40 * t), int(45 + 25 * t), int(90 + 60 * t)))
gl = Image.new('RGB', (S, S), (0, 0, 0))
gld = ImageDraw.Draw(gl)
gld.ellipse([-60, -60, 200, 200], fill=(80, 60, 180))
gl = gl.filter(ImageFilter.GaussianBlur(70))
av = Image.blend(av, gl, 0.5)
ad = ImageDraw.Draw(av, 'RGBA')

f_m = font('segoeuib.ttf', 200)
bbox = ad.textbbox((0, 0), 'M', font=f_m)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
ad.text(((S - tw) / 2 - bbox[0], (S - th) / 2 - bbox[1] - 10), 'M', font=f_m,
        fill=(235, 244, 255))

# 圆环
ad.ellipse([10, 10, S - 10, S - 10], outline=(96, 165, 250, 160), width=6)
ad.ellipse([26, 26, S - 26, S - 26], outline=(45, 212, 191, 90), width=2)

av.save(os.path.join(OUT, 'avatar.png'), 'PNG', optimize=True)
print('avatar.png ->', os.path.join(OUT, 'avatar.png'))
