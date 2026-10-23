#!/usr/bin/env python3
"""Check hand-written SVG diagrams for the defects that visual review keeps missing.

Usage:
    python check_diagram.py figure.svg
    python check_diagram.py page.html
    python check_diagram.py page.html --grayscale
    python check_diagram.py page.html --tolerance 2.0 --json

Exit code 1 when any problem is found, 0 when clean.
"""

import argparse
import html
import json
import math
import re
import sys
from pathlib import Path

CJK = 0x2E80
NARROW = set("ilI.,;:'\"!|()[]{}")
WIDE = set("MW@%")

ELEM_RE = re.compile(
    r"<(rect|circle|ellipse|line|polygon|polyline|text|path)\b([^>]*)>", re.S
)
ATTR_RE = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')


def attrs_of(raw):
    return {k: v for k, v in ATTR_RE.findall(raw)}


def fnum(attrs, key, default=0.0):
    try:
        return float(attrs.get(key, default))
    except (TypeError, ValueError):
        return default


def text_width(s, fs, spacing=0.0):
    """Approximate rendered width. Deliberately pessimistic so it catches overflow."""
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
    return w + spacing * max(0, len(s) - 1)


def dist_point_segment(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    seg2 = dx * dx + dy * dy
    if seg2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / seg2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def dist_point_rect(px, py, x, y, w, h):
    x2, y2 = x + w, y + h
    if x <= px <= x2 and y <= py <= y2:
        return min(px - x, x2 - px, py - y, y2 - py)
    dx = max(x - px, 0.0, px - x2)
    dy = max(y - py, 0.0, py - y2)
    return math.hypot(dx, dy)


def dist_point_ellipse(px, py, cx, cy, rx, ry):
    if rx <= 0 or ry <= 0:
        return math.hypot(px - cx, py - cy)
    nx, ny = (px - cx) / rx, (py - cy) / ry
    r = math.hypot(nx, ny)
    if r < 1e-9:
        return min(rx, ry)
    ang = math.atan2(ny, nx)
    ex = cx + rx * math.cos(ang)
    ey = cy + ry * math.sin(ang)
    return math.hypot(px - ex, py - ey)


def parse_points(raw):
    nums = [float(v) for v in re.split(r"[ ,]+", raw.strip()) if v]
    return list(zip(nums[0::2], nums[1::2]))


CURVE_CMDS = set("CSQTAcsqta")


def strip_defs(svg):
    """Markers live in <defs>; their geometry is not part of the drawing."""
    return re.sub(r"<defs\b.*?</defs>", "", svg, flags=re.S)


def segments_of(tag, a):
    """Vertex list of a connector element, or None when it is decoration."""
    if tag == "line":
        return [(fnum(a, "x1"), fnum(a, "y1")), (fnum(a, "x2"), fnum(a, "y2"))]
    if tag in ("polyline", "polygon"):
        pts = parse_points(a.get("points", ""))
        return pts if len(pts) >= 2 else None
    if tag == "path":
        d = a.get("d", "")
        # 只有纯 M/L 折线才算连接线：带曲线、弧、或 H/V 简写的多为装饰图形
        if any(c in d for c in CURVE_CMDS) or re.search(r"[HVhv]", d):
            return None
        nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", d)]
        pts = list(zip(nums[0::2], nums[1::2]))
        return pts if len(pts) >= 2 else None
    return None


def iter_edges(svg):
    """Yield (raw_attrs, vertices, has_arrow) for every connector."""
    body = strip_defs(svg)
    for m in ELEM_RE.finditer(body):
        tag, raw = m.group(1), m.group(2)
        if tag not in ("line", "polyline", "polygon", "path"):
            continue
        a = attrs_of(raw)
        pts = segments_of(tag, a)
        if not pts:
            continue
        yield raw, pts, "marker-end" in raw


def collect_nodes(svg):
    """Box-shaped elements: rect / circle / ellipse, as bboxes plus geometry."""
    body = strip_defs(svg)
    nodes = []
    for m in ELEM_RE.finditer(body):
        tag, raw = m.group(1), m.group(2)
        a = attrs_of(raw)
        if tag == "rect":
            x, y, w, h = (fnum(a, "x"), fnum(a, "y"),
                          fnum(a, "width"), fnum(a, "height"))
            if w <= 0 or h <= 0:
                continue
            nodes.append({"kind": "rect", "g": (x, y, w, h),
                          "box": (x, y, x + w, y + h)})
        elif tag == "circle":
            cx, cy, r = fnum(a, "cx"), fnum(a, "cy"), fnum(a, "r")
            if r < 4:
                continue  # 汇合圆点、端点装饰不是图元
            nodes.append({"kind": "ellipse", "g": (cx, cy, r, r),
                          "box": (cx - r, cy - r, cx + r, cy + r)})
        elif tag == "ellipse":
            cx, cy = fnum(a, "cx"), fnum(a, "cy")
            rx, ry = fnum(a, "rx"), fnum(a, "ry")
            if rx <= 0 or ry <= 0:
                continue
            nodes.append({"kind": "ellipse", "g": (cx, cy, rx, ry),
                          "box": (cx - rx, cy - ry, cx + rx, cy + ry)})
    return nodes


def box_contains(outer, inner, eps=1.0):
    return (outer[0] - eps <= inner[0] and outer[1] - eps <= inner[1]
            and inner[2] <= outer[2] + eps and inner[3] <= outer[3] + eps)


def box_overlap(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return w > 1.0 and h > 1.0


def point_inside(node, px, py, inset=0.0):
    if node["kind"] == "rect":
        x, y, w, h = node["g"]
        return (x + inset < px < x + w - inset
                and y + inset < py < y + h - inset)
    cx, cy, rx, ry = node["g"]
    if rx - inset <= 0 or ry - inset <= 0:
        return False
    return ((px - cx) / (rx - inset)) ** 2 + ((py - cy) / (ry - inset)) ** 2 < 1.0


def node_dist(node, px, py):
    if node["kind"] == "rect":
        return dist_point_rect(px, py, *node["g"])
    return dist_point_ellipse(px, py, *node["g"])


def sample_segment(x1, y1, x2, y2, step=2.0):
    n = max(1, int(math.hypot(x2 - x1, y2 - y1) / step))
    for i in range(n + 1):
        t = i / n
        yield x1 + (x2 - x1) * t, y1 + (y2 - y1) * t


def seg_intersection(p, q, r, s):
    """Proper intersection point of pq and rs, or None."""
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    d1, d2 = cross(r, s, p), cross(r, s, q)
    d3, d4 = cross(p, q, r), cross(p, q, s)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        den = (q[0] - p[0]) * (s[1] - r[1]) - (q[1] - p[1]) * (s[0] - r[0])
        if abs(den) < 1e-9:
            return None
        t = ((r[0] - p[0]) * (s[1] - r[1]) - (r[1] - p[1]) * (s[0] - r[0])) / den
        return (p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1]))
    return None


def check_edge_through_nodes(svg):
    """A connector must not run across a box it does not start or end on."""
    nodes = collect_nodes(svg)
    if not nodes:
        return []
    containers = set()
    for i, n in enumerate(nodes):
        inside = [j for j, m in enumerate(nodes)
                  if j != i and box_contains(n["box"], m["box"], 1.5)]
        if len(inside) >= 2:
            containers.add(i)

    issues, seen = [], set()
    for raw, pts, _ in iter_edges(svg):
        # 虚线是辅助线：时序图的生命线本来就从激活条背后穿过，不算穿框
        if "dasharray" in raw:
            continue
        touching = {i for i, n in enumerate(nodes)
                    if any(node_dist(n, x, y) <= 4.0 for x, y in (pts[0], pts[-1]))}
        for i, (x1, y1) in enumerate(pts[:-1]):
            x2, y2 = pts[i + 1]
            for n_i, node in enumerate(nodes):
                if n_i in touching or n_i in containers:
                    continue
                hit = next((p for p in sample_segment(x1, y1, x2, y2, 1.5)
                            if point_inside(node, p[0], p[1], 1.5)), None)
                if hit and (n_i, round(hit[0])) not in seen:
                    seen.add((n_i, round(hit[0])))
                    issues.append({
                        "kind": "edge-through-node",
                        "detail": f"连线横穿图元（图元 {node['kind']} 中心 "
                                  f"({(node['box'][0] + node['box'][2]) / 2:.0f},"
                                  f"{(node['box'][1] + node['box'][3]) / 2:.0f})）",
                        "at": f"({hit[0]:.0f},{hit[1]:.0f})",
                        "fix": "改走外侧通道，或调换两个图元的上下/左右顺序",
                    })
                    break
    return issues


def check_edge_crossings(svg):
    """Two arrows crossing each other reads as a wiring mistake."""
    edges = [(pts, raw) for raw, pts, has_arrow in iter_edges(svg) if has_arrow]
    issues = []
    for i in range(len(edges)):
        pts_a = edges[i][0]
        for j in range(i + 1, len(edges)):
            pts_b = edges[j][0]
            for k in range(len(pts_a) - 1):
                for m in range(len(pts_b) - 1):
                    hit = seg_intersection(pts_a[k], pts_a[k + 1],
                                           pts_b[m], pts_b[m + 1])
                    if not hit:
                        continue
                    ends = (pts_a[0], pts_a[-1], pts_b[0], pts_b[-1])
                    if any(math.hypot(hit[0] - e[0], hit[1] - e[1]) <= 6
                           for e in ends):
                        continue
                    issues.append({
                        "kind": "edge-crossing",
                        "detail": "两条连线交叉，读者会误判依赖方向",
                        "at": f"({hit[0]:.0f},{hit[1]:.0f})",
                        "fix": "拉开两侧通道，或调整图元顺序让线不交",
                    })
    return issues


def check_node_overlap(svg):
    """Boxes must not sit on top of each other (nesting is fine)."""
    nodes = collect_nodes(svg)
    issues = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            a, b = nodes[i]["box"], nodes[j]["box"]
            if box_contains(a, b) or box_contains(b, a):
                continue
            if box_overlap(a, b):
                cx = (max(a[0], b[0]) + min(a[2], b[2])) / 2
                cy = (max(a[1], b[1]) + min(a[3], b[3])) / 2
                issues.append({
                    "kind": "node-overlap",
                    "detail": "两个图元重叠",
                    "at": f"({cx:.0f},{cy:.0f})",
                    "fix": "拉开间距；层距/列距不足时先放大画布",
                })
    return issues


def check_text_in_box(svg):
    """A label must fit inside the shape it is centred in."""
    nodes = collect_nodes(svg)
    if not nodes:
        return []
    issues = []
    for m in re.finditer(r"<text\b([^>]*)>(.*?)</text>", svg, re.S):
        a = attrs_of(m.group(1))
        content = html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        if not content:
            continue
        px, py = fnum(a, "x"), fnum(a, "y")
        host = None
        for node in nodes:
            if point_inside(node, px, py, -1.0):
                if host is None or (node["box"][2] - node["box"][0]) < \
                        (host["box"][2] - host["box"][0]):
                    host = node
        if not host:
            continue
        fs = fnum(a, "font-size", 11.0)
        w = text_width(content, fs, fnum(a, "letter-spacing", 0.0))
        if host["kind"] == "rect":
            avail = (host["box"][2] - host["box"][0]) - 8
        else:
            avail = host["g"][2] * 1.8
        # text_width 是刻意偏悲观的估算，留 10% 余量免得把正常排版判成溢出
        if w > avail + max(4.0, avail * 0.10):
            issues.append({
                "kind": "text-in-box",
                "detail": f"文字宽约 {w:.0f}px，超出所在框可用宽度 {avail:.0f}px",
                "at": f'"{content[:20]}" @({px:.0f},{py:.0f})',
                "fix": "缩短文案、缩小字号、拆行，或把框加宽",
            })
    return issues


def collect_shapes(svg, skip_arrows=False):
    """Return drawable geometry that an arrow tip is allowed to touch.

    skip_arrows drops elements carrying marker-end, so a connector is never
    measured against itself.
    """
    shapes = []
    for m in ELEM_RE.finditer(svg):
        tag, raw = m.group(1), m.group(2)
        a = attrs_of(raw)

        if skip_arrows and "marker-end" in raw:
            continue

        if tag == "rect":
            shapes.append(("rect", (fnum(a, "x"), fnum(a, "y"),
                                    fnum(a, "width"), fnum(a, "height"))))
        elif tag == "circle":
            r = fnum(a, "r")
            shapes.append(("ellipse", (fnum(a, "cx"), fnum(a, "cy"), r, r)))
        elif tag == "ellipse":
            shapes.append(("ellipse", (fnum(a, "cx"), fnum(a, "cy"),
                                       fnum(a, "rx"), fnum(a, "ry"))))
        elif tag == "line":
            shapes.append(("seg", (fnum(a, "x1"), fnum(a, "y1"),
                                   fnum(a, "x2"), fnum(a, "y2"))))
        elif tag in ("polygon", "polyline"):
            pts = parse_points(a.get("points", ""))
            for i in range(len(pts) - 1):
                shapes.append(("seg", (*pts[i], *pts[i + 1])))
            if tag == "polygon" and len(pts) > 2:
                shapes.append(("seg", (*pts[-1], *pts[0])))
    return shapes


def dist_to_shapes(px, py, shapes):
    best = float("inf")
    for kind, g in shapes:
        if kind == "rect":
            d = dist_point_rect(px, py, *g)
        elif kind == "ellipse":
            d = dist_point_ellipse(px, py, *g)
        else:
            d = dist_point_segment(px, py, *g)
        if d < best:
            best = d
    return best


def check_arrows(svg, tolerance, warn_band=9.0):
    """Arrow tips must sit on the boundary of the shape they point at."""
    issues = []
    targets = collect_shapes(svg, skip_arrows=True)
    if not targets:
        return issues

    for m in ELEM_RE.finditer(svg):
        tag, raw = m.group(1), m.group(2)
        if "marker-end" not in raw:
            continue
        a = attrs_of(raw)

        if tag == "line":
            tip = (fnum(a, "x2"), fnum(a, "y2"))
        elif tag in ("polyline", "polygon"):
            pts = parse_points(a.get("points", ""))
            if not pts:
                continue
            tip = pts[-1]
        elif tag == "path":
            nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", a.get("d", ""))]
            if len(nums) < 2:
                continue
            tip = (nums[-2], nums[-1])
        else:
            continue

        near = [s for s in targets if dist_to_shapes(tip[0], tip[1], [s]) <= warn_band]
        if not near:
            # 以前这里直接 continue，结果"箭尖悬在空地上"——最严重的缺陷之一——被静默放过
            issues.append({
                "kind": "arrow-floating",
                "detail": f"箭尖 {warn_band:.0f}px 内没有任何图元，指向不明",
                "at": f"({tip[0]:.0f},{tip[1]:.0f})",
                "fix": "把终点移到目标图元的边界上，或补上被漏掉的图元",
            })
            continue

        gap = min(dist_to_shapes(tip[0], tip[1], [s]) for s in near)
        if gap > tolerance:
            issues.append({
                "kind": "arrow-gap",
                "detail": f"箭头未贴合，离最近图元 {gap:.1f}px",
                "at": f"({tip[0]:.0f},{tip[1]:.0f})",
                "fix": "把线终点改到目标图元的边界坐标",
            })
    return issues


def check_bounds(svg, W, H):
    issues = []
    for m in ELEM_RE.finditer(svg):
        tag, raw = m.group(1), m.group(2)
        a = attrs_of(raw)
        box = None

        if tag == "rect":
            box = (fnum(a, "x"), fnum(a, "y"),
                   fnum(a, "x") + fnum(a, "width"), fnum(a, "y") + fnum(a, "height"))
        elif tag == "circle":
            r = fnum(a, "r")
            box = (fnum(a, "cx") - r, fnum(a, "cy") - r,
                   fnum(a, "cx") + r, fnum(a, "cy") + r)
        elif tag == "ellipse":
            box = (fnum(a, "cx") - fnum(a, "rx"), fnum(a, "cy") - fnum(a, "ry"),
                   fnum(a, "cx") + fnum(a, "rx"), fnum(a, "cy") + fnum(a, "ry"))
        elif tag in ("polygon", "polyline"):
            pts = parse_points(a.get("points", ""))
            if not pts:
                continue
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            box = (min(xs), min(ys), max(xs), max(ys))
        elif tag == "line":
            xs = [fnum(a, "x1"), fnum(a, "x2")]
            ys = [fnum(a, "y1"), fnum(a, "y2")]
            box = (min(xs), min(ys), max(xs), max(ys))
        elif tag == "path":
            bb = bbox_of(tag, a)
            if not bb:
                continue
            box = (bb[0], bb[1], bb[0] + bb[2], bb[1] + bb[3])

        if not box:
            continue
        if box[0] < -0.5 or box[1] < -0.5 or box[2] > W + 0.5 or box[3] > H + 0.5:
            issues.append({
                "kind": "out-of-bounds",
                "detail": f"<{tag}> 超出 viewBox，bbox=({box[0]:.0f},{box[1]:.0f})-({box[2]:.0f},{box[3]:.0f})",
                "at": f"viewBox {W:.0f}x{H:.0f}",
                "fix": "放大 viewBox 或缩小/移动该图元",
            })
    return issues


def check_text(svg, W, H):
    issues = []
    for m in re.finditer(r"<text\b([^>]*)>(.*?)</text>", svg, re.S):
        a = attrs_of(m.group(1))
        content = html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        if not content:
            continue

        fs = fnum(a, "font-size", 11.0)
        spacing = fnum(a, "letter-spacing", 0.0)
        w = text_width(content, fs, spacing)
        x = fnum(a, "x")
        anchor = a.get("text-anchor", "start")

        if anchor == "middle":
            left, right = x - w / 2, x + w / 2
        elif anchor == "end":
            left, right = x - w, x
        else:
            left, right = x, x + w

        over = max(0.0, -left, right - W)
        if over > 1.0:
            issues.append({
                "kind": "text-overflow",
                "detail": f"文字超出左右边界 {over:.0f}px（估算宽 {w:.0f}px）",
                "at": f'"{content[:24]}" @y={fnum(a, "y"):.0f}',
                "fix": "拆成两行、缩短文案，或放大 viewBox",
            })

        y = fnum(a, "y")
        if y < fs * 0.2 or y > H:
            issues.append({
                "kind": "text-overflow",
                "detail": "文字纵向越界",
                "at": f'"{content[:24]}" @y={y:.0f}',
                "fix": "调整 y 或放大 viewBox",
            })
    return issues


def check_terminator_shape(svg):
    """A box labelled 开始/结束 must be a stadium terminator, not a rounded rect."""
    issues = []
    rects = []
    for m in re.finditer(r"<rect\b([^>]*)>", svg):
        a = attrs_of(m.group(1))
        rects.append((fnum(a, "x"), fnum(a, "y"), fnum(a, "width"),
                      fnum(a, "height"), fnum(a, "rx")))

    for m in re.finditer(r"<text\b([^>]*)>(.*?)</text>", svg, re.S):
        a = attrs_of(m.group(1))
        content = html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        if content not in ("开始", "结束", "开始/结束", "start", "end", "Start", "End"):
            continue
        px, py = fnum(a, "x"), fnum(a, "y")
        hits = [(w * h, (x, y, w, h, rx)) for x, y, w, h, rx in rects
                if x <= px <= x + w and y <= py <= y + h]
        if not hits:
            continue
        _, (x, y, w, h, rx) = min(hits)  # innermost box wins over annotation frames
        want = h / 2
        if rx <= 0:
            issues.append({
                "kind": "terminator",
                "detail": '直角矩形里写"{}"，不是终止符'.format(content),
                "at": f'"{content}" @({px:.0f},{py:.0f})',
                "fix": f"改成 rx={want:.0f}（= 高/2）的跑道形，或换 UML 的实心圆",
            })
        elif abs(rx - want) > 1.5:
            issues.append({
                "kind": "terminator",
                "detail": f'圆角矩形 rx={rx:.0f}，跑道形应为 {want:.0f}（= 高/2）',
                "at": f'"{content}" @({px:.0f},{py:.0f})',
                "fix": f"rx 改为 {want:.0f}；若走 UML 路线则删掉文字、改用实心圆",
            })
    return issues


def bbox_of(tag, a):
    """Approximate bounding box for path/polygon from its coordinates."""
    if tag == "polygon" or tag == "polyline":
        pts = parse_points(a.get("points", ""))
        if not pts:
            return None
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
    if tag == "path":
        nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", a.get("d", ""))]
        pairs = list(zip(nums[0::2], nums[1::2]))
        if not pairs:
            return None
        xs, ys = [p[0] for p in pairs], [p[1] for p in pairs]
        return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
    return None


def check_stroke_width(svg):
    """One diagram, one line weight. Dashed auxiliary lines (lifelines etc.)
    are exempt -- thin dashed is a legitimate convention."""
    issues = []
    widths = {}
    for m in ELEM_RE.finditer(svg):
        tag, raw = m.group(1), m.group(2)
        if tag == "text":
            continue
        a = attrs_of(raw)
        if "stroke-dasharray" in raw or "stroke-dasharray" in a.get("style", ""):
            continue
        style = a.get("style", "")
        # PlantUML 的 actor 胶囊 / 数据库圆柱装饰描边是 #181818（硬编码 1.5），
        # 与正文线不是同一套，只统计纯黑描边的图元
        stroke = a.get("stroke", "")
        mc = re.search(r"stroke:\s*(#[0-9A-Fa-f]{6})", style)
        if mc:
            stroke = mc.group(1)
        if stroke and stroke.lower() not in ("#000000", "black"):
            continue
        w = None
        mw = re.search(r"stroke-width:\s*([0-9.]+)", style)
        if mw:
            w = float(mw.group(1))
        elif a.get("stroke-width"):
            try:
                w = float(a["stroke-width"])
            except ValueError:
                w = None
        if w is None or w <= 0:
            continue
        # 大尺寸容器框（时序图的 alt/opt 组合片段等）按 UML 惯例用粗描边强调边界
        if tag == "rect" and (fnum(a, "width") > 150 or fnum(a, "height") > 150):
            continue
        # 组合片段左上角的标签页是小封闭 path，同样属于强调边框的一部分
        if tag in ("path", "polygon"):
            box = bbox_of(tag, a)
            if box and box[2] < 100 and box[3] < 20:
                continue
        widths.setdefault(round(w, 1), 0)
        widths[round(w, 1)] += 1

    if len(widths) > 1:
        span = max(widths) - min(widths)
        if span >= 0.5:
            detail = ", ".join(f"{w}×{n}处" for w, n in sorted(widths.items()))
            issues.append({
                "kind": "stroke-width",
                "detail": f"线宽不统一：{detail}",
                "at": "stroke-width",
                "fix": "全部图元统一成同一 stroke-width（虚线辅助线可保持细）",
            })
    return issues


def check_usecase_flow_arrows(svg):
    """In a use-case diagram, two ellipses must never be joined by a solid arrow."""
    issues = []
    ellipses = []
    for m in re.finditer(r"<ellipse\b([^>]*)>", svg):
        a = attrs_of(m.group(1))
        ellipses.append((fnum(a, "cx"), fnum(a, "cy"),
                         fnum(a, "rx"), fnum(a, "ry")))
    if len(ellipses) < 2:
        return issues

    for m in re.finditer(r"<(line|polyline)\b([^>]*)>", svg, re.S):
        tag, raw = m.group(1), m.group(2)
        if "marker-end" not in raw or "dasharray" in raw:
            continue
        a = attrs_of(raw)
        if tag == "line":
            p1 = (fnum(a, "x1"), fnum(a, "y1"))
            p2 = (fnum(a, "x2"), fnum(a, "y2"))
        else:
            pts = parse_points(a.get("points", ""))
            if len(pts) < 2:
                continue
            p1, p2 = pts[0], pts[-1]

        on_a = any(dist_point_ellipse(p1[0], p1[1], *e) < 3.5 for e in ellipses)
        on_b = any(dist_point_ellipse(p2[0], p2[1], *e) < 3.5 for e in ellipses)
        if on_a and on_b:
            issues.append({
                "kind": "usecase-flow",
                "detail": "两个用例之间画了实线箭头，用例图不表达执行顺序",
                "at": f"({p1[0]:.0f},{p1[1]:.0f})→({p2[0]:.0f},{p2[1]:.0f})",
                "fix": "删掉箭头；顺序交给活动图或时序图，依赖关系用虚线 «include»/«extend»",
            })
    return issues


def check_grayscale(svg):
    issues = []
    seen = set()
    for value in re.findall(r'(?:fill|stroke)\s*=\s*"(#[0-9A-Fa-f]{6})"', svg):
        if value.lower() in seen:
            continue
        r, g, b = (int(value[i:i + 2], 16) for i in (1, 3, 5))
        if max(r, g, b) - min(r, g, b) > 8:
            seen.add(value.lower())
            issues.append({
                "kind": "color",
                "detail": f"非灰度颜色 {value}",
                "at": "fill/stroke",
                "fix": "论文黑白打印，改用灰度或靠线型区分",
            })
    return issues


def split_svgs(source):
    out = []
    for m in re.finditer(r"<svg\b([^>]*)>(.*?)</svg>", source, re.S):
        out.append(m.group(1) + m.group(2))
    return out


def check_svg(svg, index, tolerance, grayscale):
    head = re.search(r'viewBox\s*=\s*"([^"]+)"', svg)
    if not head:
        return [{
            "kind": "no-viewbox",
            "detail": "缺少 viewBox，无法判断坐标是否越界",
            "at": f"SVG #{index}",
            "fix": "加上 viewBox=\"0 0 宽 高\"",
        }]
    nums = [float(v) for v in re.split(r"[ ,]+", head.group(1).strip()) if v]
    if len(nums) != 4:
        return []
    _, _, W, H = nums

    shapes = collect_shapes(svg)
    issues = []
    issues += check_arrows(svg, tolerance)
    issues += check_bounds(svg, W, H)
    issues += check_text(svg, W, H)
    issues += check_terminator_shape(svg)
    issues += check_stroke_width(svg)
    issues += check_usecase_flow_arrows(svg)
    # 全局几何：局部检查都过了但整张图仍然读不通的那一类缺陷
    issues += check_edge_through_nodes(svg)
    issues += check_edge_crossings(svg)
    issues += check_node_overlap(svg)
    issues += check_text_in_box(svg)
    if grayscale:
        issues += check_grayscale(svg)

    for it in issues:
        it["at"] = f"SVG #{index} {it['at']}"
    return issues


def main():
    ap = argparse.ArgumentParser(description="Check SVG diagrams for boundary and text defects.")
    ap.add_argument("path", help=".svg or .html file")
    ap.add_argument("--tolerance", type=float, default=1.5,
                    help="allowed arrow-tip gap in px (default 1.5)")
    ap.add_argument("--grayscale", action="store_true",
                    help="also flag non-grayscale colours (for print)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    p = Path(args.path)
    if not p.exists():
        print(f"找不到文件：{p}", file=sys.stderr)
        return 2

    source = p.read_text(encoding="utf-8")
    svgs = split_svgs(source)

    if not svgs:
        if args.json:
            print(json.dumps({"file": str(p), "svgs": 0, "issues": []}, ensure_ascii=False))
        else:
            print(f"{p.name}: 没有找到 SVG")
        return 0

    issues = []
    for i, svg in enumerate(svgs, 1):
        issues.extend(check_svg(svg, i, args.tolerance, args.grayscale))

    if args.json:
        print(json.dumps({"file": str(p), "svgs": len(svgs), "issues": issues},
                         ensure_ascii=False, indent=2))
        return 1 if issues else 0

    print(f"{p.name}：{len(svgs)} 个 SVG")
    if not issues:
        print("  通过，未发现边界或文字问题")
        return 0

    groups = {}
    for it in issues:
        groups.setdefault(it["kind"], []).append(it)

    labels = {
        "arrow-gap": "箭头未贴合",
        "arrow-floating": "箭头悬空",
        "out-of-bounds": "图元越界",
        "text-overflow": "文字溢出",
        "text-in-box": "文字挤爆所在框",
        "edge-through-node": "连线横穿图元",
        "edge-crossing": "连线交叉",
        "node-overlap": "图元重叠",
        "terminator": "终止符形状",
        "usecase-flow": "用例间流程箭头",
        "stroke-width": "线宽不统一",
        "color": "非灰度颜色",
        "no-viewbox": "缺少 viewBox",
    }
    for kind, items in groups.items():
        print(f"\n  [{labels.get(kind, kind)}] {len(items)} 处")
        for it in items[:20]:
            print(f"    · {it['at']}")
            print(f"      {it['detail']}")
            print(f"      → {it['fix']}")
        if len(items) > 20:
            print(f"    … 另有 {len(items) - 20} 处")

    print(f"\n合计 {len(issues)} 处问题")
    return 1


if __name__ == "__main__":
    sys.exit(main())
