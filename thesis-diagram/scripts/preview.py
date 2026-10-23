#!/usr/bin/env python3
"""把 layout.py 生成的 SVG 渲成 PNG 预览。

    python preview.py 图.svg -o 图.png

只覆盖本 skill 自己产出的图元子集（rect/ellipse/circle/line/polyline/
polygon/text + marker-end 箭头），不追求通用 SVG 支持。2× 超采样后缩回，
所以线条是抗锯齿的。用途是自查和贴给人看，不参与规范校验。
"""

import argparse
import math
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CJK = 0x2E80
NARROW = set("ilI.,;:'\"!|()[]{}")
WIDE = set("MW@%")

SHAPE = re.compile(r"<(rect|circle|ellipse|line|polyline|polygon)\b([^>]*)>", re.S)
TEXT = re.compile(r"<text\b([^>]*)>(.*?)</text>", re.S)
ATTR = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\simsun.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
]


def attrs(raw):
    return dict(ATTR.findall(raw))


def fnum(a, k, d=0.0):
    try:
        return float(a.get(k, d))
    except (TypeError, ValueError):
        return d


def text_width(s, fs):
    w = 0.0
    for ch in s:
        if ord(ch) >= CJK:
            w += fs
        elif ch in NARROW:
            w += fs * 0.30
        elif ch in WIDE:
            w += fs * 0.90
        else:
            w += fs * 0.55
    return w


def load_font(size):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def points(raw):
    nums = [float(v) for v in re.split(r"[ ,]+", raw.strip()) if v]
    return list(zip(nums[0::2], nums[1::2]))


def arrowhead(draw, pts, scale, filled=True, color=(44, 44, 42)):
    if len(pts) < 2:
        return
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    ang = math.atan2(y2 - y1, x2 - x1)
    size = 7.0
    tip = (x2 * scale, y2 * scale)
    left = ((x2 - size * math.cos(ang) + size * 0.42 * math.sin(ang)) * scale,
            (y2 - size * math.sin(ang) - size * 0.42 * math.cos(ang)) * scale)
    right = ((x2 - size * math.cos(ang) - size * 0.42 * math.sin(ang)) * scale,
             (y2 - size * math.sin(ang) + size * 0.42 * math.cos(ang)) * scale)
    if filled:
        draw.polygon([tip, left, right], fill=color)
    else:
        draw.line([left, tip, right], fill=color, width=max(1, int(1.3 * scale)), joint="curve")


def main():
    ap = argparse.ArgumentParser(description="SVG 预览渲染")
    ap.add_argument("svg")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--scale", type=float, default=2.0)
    args = ap.parse_args()

    src = Path(args.svg).read_text(encoding="utf-8")
    vb = re.search(r'viewBox="([^"]+)"', src)
    if not vb:
        sys.exit("缺少 viewBox")
    nums = [float(v) for v in re.split(r"[ ,]+", vb.group(1).strip()) if v]
    _, _, W, H = nums

    s = args.scale
    img = Image.new("RGB", (int(W * s), int(H * s)), "white")
    draw = ImageDraw.Draw(img)
    stroke = (44, 44, 42)

    items = [(m.start(), "shape", m.group(1), m.group(2), "")
             for m in SHAPE.finditer(src)]
    items += [(m.start(), "text", "text", m.group(1), m.group(2))
              for m in TEXT.finditer(src)]
    items.sort()

    for _, kind, tag, raw, inner in items:
        a = attrs(raw)
        sw = fnum(a, "stroke-width", 1.2)
        w = max(1, int(round(sw * s)))

        if tag == "rect":
            x, y = fnum(a, "x") * s, fnum(a, "y") * s
            ww, hh = fnum(a, "width") * s, fnum(a, "height") * s
            r = fnum(a, "rx") * s
            box = [x, y, x + ww, y + hh]
            if r > 0:
                draw.rounded_rectangle(box, radius=r, outline=stroke, width=w)
            else:
                draw.rectangle(box, outline=stroke, width=w)
        elif tag == "ellipse":
            cx, cy = fnum(a, "cx") * s, fnum(a, "cy") * s
            rx, ry = fnum(a, "rx") * s, fnum(a, "ry") * s
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=stroke, width=w)
        elif tag == "circle":
            cx, cy, r = fnum(a, "cx") * s, fnum(a, "cy") * s, fnum(a, "r") * s
            fill = a.get("fill", "#fff")
            draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                         fill=stroke if fill not in ("#fff", "#FFFFFF", "none") else None,
                         outline=stroke, width=w)
        elif tag == "line":
            p = [(fnum(a, "x1"), fnum(a, "y1")), (fnum(a, "x2"), fnum(a, "y2"))]
            draw.line([(x * s, y * s) for x, y in p], fill=stroke, width=w)
            if "marker-end" in raw:
                arrowhead(draw, p, s, filled="url(#ar)" in raw or "url(#tri)" in raw)
        elif tag in ("polyline", "polygon"):
            p = points(a.get("points", ""))
            if len(p) < 2:
                continue
            draw.line([(x * s, y * s) for x, y in p], fill=stroke, width=w, joint="curve")
            if tag == "polygon":
                draw.polygon([(x * s, y * s) for x, y in p], outline=stroke, width=w)
            if "marker-end" in raw:
                arrowhead(draw, p, s, filled="url(#ar)" in raw or "url(#tri)" in raw)
        elif tag == "text":
            content = re.sub(r"<[^>]+>", "", inner)
            content = (content.replace("&lt;", "<").replace("&gt;", ">")
                       .replace("&amp;", "&").strip())
            if not content:
                continue
            fs = fnum(a, "font-size", 12.0)
            font = load_font(int(round(fs * s)))
            tw = text_width(content, fs) * s
            x, y = fnum(a, "x") * s, fnum(a, "y") * s
            anchor = a.get("text-anchor", "start")
            if anchor == "middle":
                x -= tw / 2
            elif anchor == "end":
                x -= tw
            draw.text((x, y - fs * s * 0.62), content, font=font, fill=stroke)

    img = img.resize((int(W * 2), int(H * 2)), Image.LANCZOS)
    img.save(args.out)
    print(f"{args.out}  {img.width}×{img.height}", file=sys.stderr)


if __name__ == "__main__":
    main()
