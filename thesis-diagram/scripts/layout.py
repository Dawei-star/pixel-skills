#!/usr/bin/env python3
"""Deterministic layout for thesis diagrams.

模型只交结构（节点、连线、分支左右），坐标全部由本脚本算。
节点数没有实际上限——排版不依赖"一次能记住多少行"。

    python layout.py spec.json -o 图.svg

版式：
    linear   —— 流程图 / UML 活动图（单列主链 + 判定分支左右挂 + 汇合）
    usecase  —— 用例图（参与者 + 主用例一列 + 被包含用例右移一层）

spec 缺失字段一律有默认值；结构性冲突（同层同列两个节点）直接报错退出，
绝不画出一张"看起来像排好了"的重叠图。
"""

import argparse
import json
import math
import sys
from pathlib import Path

CJK = 0x2E80
NARROW = set("ilI.,;:'\"!|()[]{}")
WIDE = set("MW@%")

STROKE = "#2C2C2A"
SW_SHAPE = 1.2
SW_EDGE = 1.1
FS = 12.0
# 图内文字统一用无衬线中文字体。SVG 不写 font-family 时浏览器会退到 serif，
# 同一张图里就会出现"椭圆里是宋体、参与者名是雅黑"的两套字形。
FONT = "Microsoft YaHei, PingFang SC, Noto Sans CJK SC, sans-serif"

GAP_Y = 26          # 相邻两层的净间距
BRANCH_DX = 96      # 判定分支相对中线的水平偏移
LANE_PAD = 20       # 回溯线走外侧时的通道留白

MARKERS = """<defs>
<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1 L9 5 L1 9 Z" fill="{s}"/></marker>
<marker id="aro" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M1.5 1.5 L9 5 L1.5 8.5" fill="none" stroke="{s}" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></marker>
<marker id="tri" viewBox="0 0 12 12" refX="10.5" refY="6" markerWidth="11" markerHeight="11" orient="auto"><path d="M1.5 1.5 L10.5 6 L1.5 10.5 Z" fill="#FFFFFF" stroke="{s}" stroke-width="1.1" stroke-linejoin="round"/></marker>
<marker id="crow" viewBox="0 0 12 12" refX="10" refY="6" markerWidth="10" markerHeight="10" orient="auto"><path d="M1 1 L10 6 L1 11" fill="none" stroke="{s}" stroke-width="1.2" stroke-linecap="round"/></marker>
</defs>""".format(s=STROKE)


# ---------------------------------------------------------------- 文本度量

def text_w(s, fs=FS):
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


def _dedupe(pts, eps=0.5):
    out = []
    for p in pts:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > eps:
            out.append(p)
    return out


# ---------------------------------------------------------------- 图元

class Prim:
    """One drawable element, in local coordinates."""

    def __init__(self, kind, **kw):
        self.kind = kind
        self.__dict__.update(kw)

    def bbox(self):
        if self.kind == "rect":
            return (self.x, self.y, self.x + self.w, self.y + self.h)
        if self.kind in ("ellipse", "circle"):
            rx = self.rx if self.kind == "ellipse" else self.r
            ry = self.ry if self.kind == "ellipse" else self.r
            return (self.cx - rx, self.cy - ry, self.cx + rx, self.cy + ry)
        if self.kind == "poly":
            xs = [p[0] for p in self.pts]
            ys = [p[1] for p in self.pts]
            return (min(xs), min(ys), max(xs), max(ys))
        if self.kind == "line":
            return (min(self.x1, self.x2), min(self.y1, self.y2),
                    max(self.x1, self.x2), max(self.y1, self.y2))
        if self.kind == "polyline":
            xs = [p[0] for p in self.pts]
            ys = [p[1] for p in self.pts]
            return (min(xs), min(ys), max(xs), max(ys))
        if self.kind == "text":
            w = text_w(self.content, self.fs)
            half = w / 2 if self.anchor == "middle" else 0
            return (self.x - half, self.y - self.fs * 0.7,
                    self.x - half + w, self.y + self.fs * 0.7)
        raise ValueError(self.kind)

    def render(self, dx, dy):
        k = self.kind
        if k == "rect":
            edge = ("" if getattr(self, "plain", False)
                    else ' stroke="{}" stroke-width="{}"'.format(STROKE, SW_SHAPE))
            return ('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" rx="{:.1f}" '
                    'fill="#fff"{}/>'
                    .format(self.x + dx, self.y + dy, self.w, self.h, self.rx, edge))
        if k == "ellipse":
            return ('<ellipse cx="{:.1f}" cy="{:.1f}" rx="{:.1f}" ry="{:.1f}" '
                    'fill="#fff" stroke="{}" stroke-width="{}"/>'
                    .format(self.cx + dx, self.cy + dy, self.rx, self.ry, STROKE, SW_SHAPE))
        if k == "circle":
            fill = STROKE if self.filled else "#fff"
            return ('<circle cx="{:.1f}" cy="{:.1f}" r="{:.1f}" fill="{}" stroke="{}" '
                    'stroke-width="{}"/>'
                    .format(self.cx + dx, self.cy + dy, self.r, fill, STROKE,
                            SW_SHAPE if self.filled else 1.4))
        if k == "poly":
            pts = " ".join("{:.1f},{:.1f}".format(x + dx, y + dy) for x, y in self.pts)
            return ('<polygon points="{}" fill="#fff" stroke="{}" stroke-width="{}"/>'
                    .format(pts, STROKE, SW_SHAPE))
        if k == "line":
            attrs = self.extra()
            return ('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}" stroke="{}" '
                    'stroke-width="{}"{}/>'
                    .format(self.x1 + dx, self.y1 + dy, self.x2 + dx, self.y2 + dy,
                            STROKE, SW_EDGE, attrs))
        if k == "polyline":
            pts = " ".join("{:.1f},{:.1f}".format(x + dx, y + dy) for x, y in self.pts)
            return ('<polyline points="{}" fill="none" stroke="{}" stroke-width="{}"{}/>'
                    .format(pts, STROKE, SW_EDGE, self.extra()))
        if k == "text":
            fill = getattr(self, "fill", "auto")
            fill_attr = "" if fill == "auto" else ' fill="{}"'.format(fill)
            # font-size 一律显式写出：早先"等于 FS 就省略"的写法假定根节点有默认字号，
            # 而根节点并没有 → 正文全部按浏览器默认 16px 渲染，与外圈 10.5px 的用例大小不一。
            return ('<text x="{:.1f}" y="{:.1f}" text-anchor="{}" dominant-baseline="central" '
                    'font-family="{}" font-size="{:.1f}"{}>{}</text>'
                    .format(self.x + dx, self.y + dy, self.anchor, FONT, self.fs,
                            fill_attr, self.content))
        raise ValueError(k)

    def extra(self):
        bits = ""
        if getattr(self, "dashed", False):
            bits += ' stroke-dasharray="5 3"'
        marker = getattr(self, "marker", None)
        if marker:
            bits += ' marker-end="url(#{})"'.format(marker)
        return bits


# ---------------------------------------------------------------- 线性版式

SHAPES = {
    "process": dict(w=124, h=30),
    "terminator": dict(w=88, h=28),
    "decision": dict(hw=62, hh=32),
    "io": dict(w=128, h=30, skew=14),
    "start": dict(r=8),
    "end": dict(r=12),
}


class LinearLayout:
    def __init__(self, spec):
        self.nodes = {}
        self.order = []
        self._lane_n = 0
        for raw in spec["nodes"]:
            n = dict(raw)
            n["_col_set"] = "col" in raw
            n.setdefault("col", 0)
            n.setdefault("shape", "process")
            if n["shape"] not in SHAPES:
                raise SystemExit(f'未知形状 "{n["shape"]}"（节点 {n["id"]}）；'
                                 f'可用：{", ".join(SHAPES)}')
            self.nodes[n["id"]] = n
            self.order.append(n["id"])
        self.edges = [self._edge(e) for e in spec.get("edges", [])]
        # gb1526：处理框直角、开始/结束用跑道形（节点 shape 给 terminator）。
        # 不写 style 时沿用 UML 活动图画法（圆角动作框、实心圆起、带环圆止）。
        self.style = spec.get("style", "uml")
        for e in self.edges:
            for key in ("from", "to"):
                if e[key] not in self.nodes:
                    raise SystemExit(f'边引用了不存在的节点 "{e[key]}"')
        self.prims = []

    @staticmethod
    def _edge(e):
        if isinstance(e, (list, tuple)):
            e = {"from": e[0], "to": e[1]}
        return {"from": e["from"], "to": e["to"],
                "label": e.get("label"),
                "dashed": bool(e.get("dashed")),
                "arrow": e.get("arrow", "filled")}

    # -- 尺寸

    def measure(self, n):
        style = SHAPES[n["shape"]]
        text = n.get("text", "")
        if n["shape"] == "decision":
            hw = max(style["hw"], text_w(text, 11.5) / 2 + 18)
            n.update(hw=hw, hh=style["hh"], w=hw * 2, h=style["hh"] * 2)
        elif n["shape"] in ("start", "end"):
            n.update(w=style["r"] * 2, h=style["r"] * 2, r=style["r"])
        elif n["shape"] == "io":
            w = max(style["w"], text_w(text) + 40)
            n.update(w=w, h=style["h"], skew=style["skew"])
        else:
            extra = 28 if n["shape"] == "terminator" else 24
            n.update(w=max(style["w"], text_w(text) + extra), h=style["h"])

    # -- 分层

    def run(self):
        for nid in self.order:
            self.measure(self.nodes[nid])

        outs = {}
        for e in self.edges:
            outs.setdefault(e["from"], []).append(e)

        back = self._back_edges(outs)
        self._back_pairs = {(e["from"], e["to"]) for e in back}
        fwd = [e for e in self.edges if e not in back]

        rank = {nid: 0 for nid in self.order}
        for _ in range(len(self.order) + 2):
            changed = False
            for e in fwd:
                want = rank[e["from"]] + 1
                if rank[e["to"]] < want:
                    rank[e["to"]] = want
                    changed = True
            if not changed:
                break
        for nid, n in self.nodes.items():
            if "rank" in n:
                rank[nid] = int(n["rank"])
            n["rank"] = rank[nid]

        self._assign_columns()
        self.junctions = self._find_junctions(fwd)
        self._assign_y()
        self._assign_x()
        self._place_nodes()
        self._route_edges(fwd, back)
        return self._emit()

    def _back_edges(self, outs):
        state, back = {}, []

        def dfs(u):
            state[u] = 1
            for e in outs.get(u, []):
                v = e["to"]
                if v == u:
                    back.append(e)
                elif state.get(v) == 1:
                    back.append(e)
                elif state.get(v, 0) == 0:
                    dfs(v)
            state[u] = 2

        for nid in self.order:
            if state.get(nid, 0) == 0:
                dfs(nid)
        return back

    def _assign_columns(self):
        """判定节点的多个出边必须落在不同列；没写 col 就按"还剩哪几列"推。"""
        for nid, n in self.nodes.items():
            if n["shape"] != "decision":
                continue
            targets = [e["to"] for e in self.edges
                       if e["from"] == nid
                       and (e["from"], e["to"]) not in getattr(self, "_back_pairs", set())]
            if len(targets) < 2:
                continue
            used = {self.nodes[t]["col"] for t in targets if self.nodes[t]["_col_set"]}
            unset = [t for t in targets if not self.nodes[t]["_col_set"]]
            if not unset:
                continue

            if len(unset) == 2 and not used:
                picks = [-1, 1]          # 两条并列分支，没有主干
            elif len(unset) == 1:
                free = [c for c in (0, -1, 1) if c not in used]
                if not free:
                    raise SystemExit(f'判定节点 "{nid}" 的三个分支已占满 -1/0/1，'
                                     f'"{unset[0]}" 无处可放')
                picks = [free[0]]
            else:
                raise SystemExit(
                    f'判定节点 "{nid}" 有 {len(unset)} 个分支没写 col，无法推断左右。'
                    f'请给 {", ".join(unset)} 显式写 "col": -1 或 1')

            for t, c in zip(unset, picks):
                self.nodes[t]["col"] = c
                print(f'  · 推知 {t}.col={c}（来自判定 {nid}）', file=sys.stderr)

        slots = {}
        for nid in self.order:
            n = self.nodes[nid]
            key = (n["rank"], n["col"])
            if key in slots:
                raise SystemExit(
                    f'同层同列冲突：{slots[key]} 与 {nid} 都在第 {key[0]} 层、col={key[1]}。'
                    f'给其中一个加 "col": -1/1，或显式指定 "rank"')
            slots[key] = nid

    def _find_junctions(self, fwd):
        """目标在中线且上方有多条线汇入 —— 需要一条水平汇合线，并额外留出竖直空间。"""
        by_target = {}
        for e in fwd:
            by_target.setdefault(e["to"], []).append(e)
        jx = {}
        for target, group in by_target.items():
            t = self.nodes[target]
            if t["col"] != 0:
                continue
            incoming = [e for e in group
                        if self.nodes[e["from"]]["rank"] < t["rank"]]
            if len(incoming) >= 2:
                jx[target] = incoming
        return jx

    def _assign_y(self):
        layers = {}
        for nid in self.order:
            layers.setdefault(self.nodes[nid]["rank"], []).append(nid)
        y = 0.0
        for r in sorted(layers):
            if any(nid in self.junctions for nid in layers[r]) and r > 0:
                y += 34          # 汇合线需要呼吸空间，否则横线会贴住分支框底边
            h = max(self.nodes[n]["h"] for n in layers[r])
            for nid in layers[r]:
                self.nodes[nid]["top"] = y
                self.nodes[nid]["cy"] = y + h / 2
            y += h + GAP_Y
        self.height = y - GAP_Y

    def _assign_x(self):
        branch_nodes = [n for n in self.nodes.values() if n["col"] != 0]
        trunk_w = max((n["w"] for n in self.nodes.values() if n["col"] == 0), default=0)
        dx = BRANCH_DX
        if branch_nodes:
            # 只按分支框半宽算会漏掉主干框自己的半宽，两边各占一半通道就叠在一起了。
            dx = max(dx, (max(n["w"] for n in branch_nodes) + trunk_w) / 2 + 26)
        self.dx = dx
        for n in self.nodes.values():
            n["cx"] = n["col"] * dx

    def _place_nodes(self):
        for nid in self.order:
            n = self.nodes[nid]
            shape = n["shape"]
            cx, cy, w, h = n["cx"], n["cy"], n["w"], n["h"]
            if shape in ("start", "end"):
                if shape == "start":
                    self.prims.append(Prim("circle", cx=cx, cy=cy, r=n["r"], filled=True))
                else:
                    self.prims.append(Prim("circle", cx=cx, cy=cy, r=n["r"], filled=False))
                    self.prims.append(Prim("circle", cx=cx, cy=cy, r=max(6, n["r"] - 4),
                                           filled=True))
                continue
            if shape == "decision":
                self.prims.append(Prim("poly", pts=[
                    (cx, cy - n["hh"]), (cx + n["hw"], cy),
                    (cx, cy + n["hh"]), (cx - n["hw"], cy)]))
            elif shape == "io":
                s = n["skew"]
                self.prims.append(Prim("poly", pts=[
                    (cx - w / 2 + s, cy - h / 2), (cx + w / 2, cy - h / 2),
                    (cx + w / 2 - s, cy + h / 2), (cx - w / 2, cy + h / 2)]))
            else:
                rx = h / 2 if shape == "terminator" else (0 if self.style == "gb1526" else 8)
                self.prims.append(Prim("rect", x=cx - w / 2, y=cy - h / 2, w=w, h=h, rx=rx))
            if n.get("text"):
                fs = 11.5 if shape == "decision" else FS
                self.prims.append(Prim("text", x=cx, y=cy, content=n["text"],
                                       fs=fs, anchor="middle"))

    # -- 连线

    def _route_edges(self, fwd, back):
        by_target = {}
        for e in fwd:
            by_target.setdefault(e["to"], []).append(e)

        junctions = {t: self.nodes[t]["top"] - 22 for t in self.junctions}
        group_size = {t: len(v) for t, v in self.junctions.items()}

        trunk_done = set()
        for target, jy in junctions.items():
            t = self.nodes[target]
            for e in by_target[target]:
                s = self.nodes[e["from"]]
                if s["rank"] >= t["rank"]:
                    continue
                trunk_done.add((e["from"], target))
                pts = _dedupe([(s["cx"], self._bottom(s)), (s["cx"], jy), (t["cx"], jy)])
                if len(pts) < 2:
                    continue
                self.prims.append(Prim("polyline", pts=pts, dashed=e["dashed"]))
                if e["label"]:
                    self.prims.append(Prim("text", x=s["cx"] + 15, y=self._bottom(s) + 13,
                                           content=e["label"], fs=10, anchor="middle"))
            if group_size.get(target, 0) >= 2:
                self.prims.append(Prim("circle", cx=t["cx"], cy=jy, r=2.8, filled=True))
            self.prims.append(Prim("line", x1=t["cx"], y1=jy, x2=t["cx"],
                                   y2=self._top(t), marker="ar"))

        for e in fwd:
            if (e["from"], e["to"]) in trunk_done:
                continue
            s, t = self.nodes[e["from"]], self.nodes[e["to"]]
            marker = {"filled": "ar", "open": "aro", "none": None}.get(e["arrow"], "ar")
            label = e["label"]

            if s["rank"] + 1 == t["rank"] and (s["col"] == t["col"] or s["shape"] == "decision"):
                if s["shape"] == "decision" and t["col"] != 0:
                    side = 1 if t["col"] > 0 else -1
                    pts = [(s["cx"] + side * s["hw"], s["cy"]),
                           (t["cx"], s["cy"]), (t["cx"], self._top(t))]
                    self.prims.append(Prim("polyline", pts=pts, marker=marker))
                    if label:
                        self.prims.append(Prim(
                            "text", x=(s["cx"] + side * s["hw"] + t["cx"]) / 2,
                            y=s["cy"] - 10, content=label, fs=10, anchor="middle"))
                    continue
                self.prims.append(Prim("line", x1=s["cx"], y1=self._bottom(s),
                                       x2=t["cx"], y2=self._top(t), marker=marker))
                if label:
                    self.prims.append(Prim(
                        "text", x=s["cx"] + 16, y=(self._bottom(s) + self._top(t)) / 2,
                        content=label, fs=10, anchor="middle"))
                continue

            # 跨层或回溯：走右侧通道，绝不横穿中间层
            lane = self._lane()
            pts = [(s["cx"], self._bottom(s)), (lane, self._bottom(s)),
                   (lane, t["cy"]), (t["cx"] + t["w"] / 2, t["cy"])]
            self.prims.append(Prim("polyline", pts=pts, marker=marker))
            if label:
                self.prims.append(Prim("text", x=lane + 12, y=(self._bottom(s) + t["cy"]) / 2,
                                       content=label, fs=10, anchor="middle"))

        for e in back:
            s, t = self.nodes[e["from"]], self.nodes[e["to"]]
            marker = {"filled": "ar", "open": "aro", "none": None}.get(e["arrow"], "ar")
            lane = self._lane()
            pts = [(s["cx"] + s["w"] / 2, s["cy"]), (lane, s["cy"]),
                   (lane, t["cy"]), (t["cx"] + t["w"] / 2, t["cy"])]
            self.prims.append(Prim("polyline", pts=pts, marker=marker, dashed=e["dashed"]))
            if e["label"]:
                self.prims.append(Prim("text", x=lane + 12, y=(s["cy"] + t["cy"]) / 2,
                                       content=e["label"], fs=10, anchor="middle"))

    def _lane(self):
        self._lane_n += 1
        right = max(n["cx"] + n["w"] / 2 for n in self.nodes.values())
        return right + LANE_PAD + (self._lane_n - 1) * 14

    @staticmethod
    def _top(n):
        return n["cy"] - n["h"] / 2

    @staticmethod
    def _bottom(n):
        return n["cy"] + n["h"] / 2

    def _emit(self):
        return self.prims


# ---------------------------------------------------------------- 用例图版式

class UsecaseLayout:
    def __init__(self, spec):
        self.primary, self.secondary = [], []
        for raw in spec["nodes"]:
            n = dict(raw)
            n["id"] = raw.get("id") or raw.get("text")
            if not n["id"]:
                raise SystemExit("用例节点必须有 id 或 text")
            col = n.get("col", 0)
            (self.secondary if col else self.primary).append(n)
        if not self.primary:
            raise SystemExit("用例图至少要有一个主用例（col=0）")
        self.actors = [dict(a) for a in spec.get("actors", [])]
        self.boundary = spec.get("boundary")
        self.edges = spec.get("edges", [])
        self.prims = []

    def run(self):
        for n in self.primary:
            n["rx"] = max(52, text_w(n.get("text", "")) / 2 + 14)
            n["ry"] = 20
        for n in self.secondary:
            n["rx"] = max(44, text_w(n.get("text", "")) / 2 + 12)
            n["ry"] = 18

        rx_p = max(n["rx"] for n in self.primary)
        rx_s = max(n["rx"] for n in self.secondary) if self.secondary else 44
        self.boundary_left = 92.0
        self.cx_p = self.boundary_left + 14 + rx_p
        self.cx_s = self.cx_p + rx_p + 8 + 40 + rx_s

        spacing = max(78, 2 * max(n["ry"] for n in self.primary) + 38)
        if len(self.actors) > 1:
            spacing = max(spacing, 130)   # 多人各占一条横向通道，行距要够放小人
        y = 75.0
        for n in self.primary:
            n["cx"], n["cy"] = self.cx_p, y
            y += spacing
        top_p, bot_p = self.primary[0]["cy"], self.primary[-1]["cy"]

        src_y = {}
        for e in self.edges:
            src_y.setdefault(e["to"], self.primary[0]["cy"])
        for n in self.primary:
            for e in self.edges:
                if e["from"] == n["id"]:
                    src_y[e["to"]] = n["cy"]

        prev = None
        for n in sorted(self.secondary, key=lambda k: src_y.get(k["id"], 0)):
            want = max(src_y.get(n["id"], 0) - 20, (prev + 75) if prev is not None else -1e9)
            n["cx"], n["cy"] = self.cx_s, want
            prev = want

        all_uc = self.primary + self.secondary
        left = min(n["cx"] - n["rx"] for n in all_uc) - 12
        right = max(n["cx"] + n["rx"] for n in all_uc) + 12
        top = min(n["cy"] - n["ry"] for n in all_uc) - 26
        bottom = max(n["cy"] + n["ry"] for n in all_uc) + 26
        if self.boundary:
            self.prims.append(Prim("rect", x=left, y=top, w=right - left,
                                   h=bottom - top, rx=0))
            self.prims.append(Prim("text", x=(left + right) / 2, y=top + 15,
                                   content=self.boundary, fs=10.5, anchor="middle"))

        for n in all_uc:
            self.prims.append(Prim("ellipse", cx=n["cx"], cy=n["cy"],
                                   rx=n["rx"], ry=n["ry"]))
            fs = FS  # 主用例与被包含用例同号；早先给次列 10.5，同一张图里两种字号
            self.prims.append(Prim("text", x=n["cx"], y=n["cy"],
                                   content=n.get("text", ""), fs=fs, anchor="middle"))

        by_id = {n["id"]: n for n in all_uc}
        self._place_actors(by_id)
        for a in self.actors:
            self._actor(a)

        for e in self.edges:
            self._edge(e, by_id)
        return self.prims

    def _place_actors(self, by_id):
        """参与者竖排在左侧同一列，y 取各自关联用例的中位。

        多个参与者都从同一列放射，只要两人的关联用例在纵向交叠，连线必然打结——
        这里直接报错，不产出一张"看着还行其实读不懂"的图。
        """
        spans = {}
        for a in self.actors:
            aid = a.get("id")
            if not aid:
                raise SystemExit('actors 里每个参与者都要有 "id"，否则接不上用例')
            ys = [by_id[e["to"]]["cy"] for e in self.edges
                  if e.get("from") == aid and e.get("to") in by_id]
            if not ys:
                raise SystemExit(f'参与者 "{aid}" 没有关联任何用例')
            spans[aid] = (min(ys), max(ys))

        prev_hi = prev_name = prev_ay = None
        for a in sorted(self.actors, key=lambda x: sum(spans[x["id"]]) / 2):
            lo, hi = spans[a["id"]]
            if prev_hi is not None and lo < prev_hi - 1:
                raise SystemExit(
                    f'参与者 "{prev_name}" 与 "{a["id"]}" 关联的用例在纵向交叠，'
                    f'左侧放射线会打结。把用例按参与者分组重排，拆成两张图，'
                    f'或改用 PlantUML')
            ay = (lo + hi) / 2
            if prev_ay is not None:
                ay = max(ay, prev_ay + 130)
            a["_ax"], a["_ay"] = 40.0, ay
            prev_hi, prev_name, prev_ay = hi, a["id"], ay

    def _actor(self, a):
        ax, ay = a["_ax"], a["_ay"]
        self.prims.append(Prim("circle", cx=ax, cy=ay, r=9, filled=False))
        self.prims.append(Prim("line", x1=ax, y1=ay + 9, x2=ax, y2=ay + 36))
        self.prims.append(Prim("line", x1=ax - 16, y1=ay + 24, x2=ax + 16, y2=ay + 24))
        self.prims.append(Prim("line", x1=ax, y1=ay + 36, x2=ax - 11, y2=ay + 58))
        self.prims.append(Prim("line", x1=ax, y1=ay + 36, x2=ax + 11, y2=ay + 58))
        self.prims.append(Prim("text", x=ax, y=ay + 76, content=a.get("text", ""),
                               fs=FS, anchor="middle"))

    def _edge(self, e, by_id):
        src, dst = e["from"], e["to"]
        kind = e.get("kind", "assoc")

        anchor = self._actor_anchor(src)
        if anchor:
            s = by_id[dst]
            x2, y2 = self._on_ellipse(s, anchor[0], anchor[1])
            self.prims.append(Prim("line", x1=anchor[0], y1=anchor[1],
                                   x2=x2, y2=y2, marker="ar"))
            return

        s, t = by_id[src], by_id[dst]
        x1, y1 = self._on_ellipse(s, t["cx"], t["cy"])
        x2, y2 = self._on_ellipse(t, s["cx"], s["cy"])
        dashed = kind in ("include", "extend")
        self.prims.append(Prim("line", x1=x1, y1=y1, x2=x2, y2=y2,
                               marker="aro" if dashed else "ar", dashed=dashed))
        if kind in ("include", "extend"):
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            name = "«include»" if kind == "include" else "«extend»"
            self.prims.append(Prim("text", x=mx, y=my - 9, content=name,
                                   fs=8.5, anchor="middle", fill="#5F5E5A"))

    def _actor_anchor(self, aid):
        """关联线起点必须落在小人的手臂末端（ax+16），不是它外面 2px。
        早先写 +18，导出后手臂与连线之间有一道肉眼可见的断口。"""
        for a in self.actors:
            if a.get("id") == aid:
                return a["_ax"] + 16, a["_ay"] + 24
        return None

    @staticmethod
    def _on_ellipse(n, fx, fy):
        dx, dy = fx - n["cx"], fy - n["cy"]
        denom = math.hypot(dx / n["rx"], dy / n["ry"])
        if denom < 1e-9:
            return n["cx"], n["cy"] - n["ry"]
        return n["cx"] + dx / denom, n["cy"] + dy / denom


# ---------------------------------------------------------------- 时序图版式

class SequenceLayout:
    """消息序号直接当 y 轴、参与者序号直接当 x 轴——两个轴都是算出来的，没有求解过程。"""

    BOX_H = 26
    MSG_GAP = 38
    HALF_BAR = 6
    SIDE_PAD = 8

    def __init__(self, spec):
        self.parts = [dict(p) for p in spec.get("participants", [])]
        if len(self.parts) < 2:
            raise SystemExit("时序图至少要两个参与者")
        for p in self.parts:
            p["id"] = p.get("id") or p.get("text")
            if not p["id"]:
                raise SystemExit("participants 里每项都要有 id 或 text")
        ids = {p["id"] for p in self.parts}
        if len(ids) != len(self.parts):
            raise SystemExit("参与者 id 有重复")

        self.msgs = []
        for raw in spec.get("messages", []):
            m = dict(raw)
            for key in ("from", "to"):
                if m.get(key) not in ids:
                    raise SystemExit(f'消息引用了未声明的参与者 "{m.get(key)}"')
            m.setdefault("kind", "call")
            if m["kind"] not in ("call", "return"):
                raise SystemExit(f'消息 kind 只能是 call / return，收到 "{m["kind"]}"')
            self.msgs.append(m)
        if not self.msgs:
            raise SystemExit("时序图至少要有一条消息")
        self.prims = []

    def run(self):
        for p in self.parts:
            p["w"] = max(76, text_w(p.get("text", "")) + 24)

        spacing = max(118, max(p["w"] for p in self.parts) + 42)
        x = max(p["w"] for p in self.parts) / 2 + 14
        for p in self.parts:
            p["cx"] = x
            p["cy"] = 14 + self.BOX_H / 2
            p["bottom"] = 14 + self.BOX_H
            x += spacing

        y = self.parts[0]["bottom"] + 34
        for m in self.msgs:
            m["y"] = y
            y += self.MSG_GAP
        self.height = y - self.MSG_GAP + 40

        bars = self._bars()

        for p in self.parts:
            self.prims.append(Prim("rect", x=p["cx"] - p["w"] / 2, y=14,
                                   w=p["w"], h=self.BOX_H, rx=0))
            self.prims.append(Prim("text", x=p["cx"], y=p["cy"],
                                   content=p.get("text", ""), fs=FS, anchor="middle"))

        for p in self.parts:
            self.prims.append(Prim("line", x1=p["cx"], y1=p["bottom"],
                                   x2=p["cx"], y2=self.height - 20, dashed=True))

        for p in self.parts:
            if p["id"] in bars:
                top, bottom = bars[p["id"]]
                self.prims.append(Prim("rect", x=p["cx"] - self.HALF_BAR, y=top,
                                       w=self.HALF_BAR * 2, h=bottom - top, rx=0))

        for m in self.msgs:
            self._message(m, bars)
        return self.prims

    def _bars(self):
        """被"调用"过的一端才画激活条。

        判据是收到过 call（不是 return）：发起者只会收到返回，所以保持裸生命线；
        区间取该参与者全部相关消息的 y 范围，两端各放 8px。
        """
        involved, called = {}, set()
        for m in self.msgs:
            for side in (m["from"], m["to"]):
                involved.setdefault(side, []).append(m["y"])
            if m["kind"] == "call":
                called.add(m["to"])

        bars = {}
        for p in self.parts:
            if p.get("active") is False:
                continue
            if p["id"] not in called:
                continue
            ys = involved[p["id"]]
            bars[p["id"]] = (min(ys) - self.SIDE_PAD, max(ys) + self.SIDE_PAD)
        return bars

    def _message(self, m, bars):
        src = next(p for p in self.parts if p["id"] == m["from"])
        dst = next(p for p in self.parts if p["id"] == m["to"])
        y = m["y"]
        same = src is dst
        dx = 1 if (same or dst["cx"] > src["cx"]) else -1
        x1 = src["cx"] + (dx * self.HALF_BAR if src["id"] in bars else 0)
        x2 = dst["cx"] - (dx * self.HALF_BAR if dst["id"] in bars else 0)

        if same:
            self._self_message(src, m, dx)
            return

        dashed = m["kind"] == "return"
        self.prims.append(Prim("line", x1=x1, y1=y, x2=x2, y2=y,
                               marker="aro" if dashed else "ar", dashed=dashed))
        if m.get("text"):
            self._label(m["text"], (x1 + x2) / 2, y - 8)

    def _label(self, text, cx, cy):
        """消息文字压一条白底，免得跟虚生命线糊在一起。"""
        w = text_w(text, 9.5) + 10
        self.prims.append(Prim("rect", x=cx - w / 2, y=cy - 7, w=w, h=14,
                               rx=0, plain=True))
        self.prims.append(Prim("text", x=cx, y=cy, content=text, fs=9.5, anchor="middle"))

    def _self_message(self, p, m, dx):
        """自调用画成一个向右的回环，不占额外的 y。"""
        y = m["y"]
        arm = p["cx"] + self.HALF_BAR * dx
        pts = [(arm, y), (arm + 26 * dx, y), (arm + 26 * dx, y + 18), (arm, y + 18)]
        self.prims.append(Prim("polyline", pts=pts, marker="ar",
                               dashed=m["kind"] == "return"))
        if m.get("text"):
            self._label(m["text"], arm + 34 * dx, y + 6)


# ---------------------------------------------------------------- 输出

def write_svg(prims, path, pad=16.0):
    boxes = [p.bbox() for p in prims]
    minx = min(b[0] for b in boxes)
    miny = min(b[1] for b in boxes)
    maxx = max(b[2] for b in boxes)
    maxy = max(b[3] for b in boxes)
    dx, dy = pad - minx, pad - miny
    W = maxx - minx + pad * 2
    H = maxy - miny + pad * 2

    body = "\n".join(p.render(dx, dy) for p in prims)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {:.0f} {:.0f}" '
           'font-family="{}" font-size="{:.0f}">\n{}\n{}\n</svg>\n'
           ).format(round(W), round(H), FONT, FS, MARKERS, body)
    Path(path).write_text(svg, encoding="utf-8")
    return round(W), round(H)


def main():
    ap = argparse.ArgumentParser(description="按结构 JSON 生成论文插图 SVG")
    ap.add_argument("spec", help="结构 JSON 路径，- 表示 stdin")
    ap.add_argument("-o", "--out", required=True, help="输出 svg 路径")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.spec == "-" else Path(args.spec).read_text(encoding="utf-8")
    spec = json.loads(raw)
    layout = spec.get("layout", "linear")
    if layout == "linear":
        prims = LinearLayout(spec).run()
    elif layout == "usecase":
        prims = UsecaseLayout(spec).run()
    elif layout == "sequence":
        prims = SequenceLayout(spec).run()
    else:
        raise SystemExit(f'未知版式 "{layout}"；可用：linear, usecase, sequence')

    W, H = write_svg(prims, args.out)
    if layout == "linear":
        # 两套符号混用比用错更致命：UML 样式里出现跑道形终止符（或反之）当场提醒。
        terms = [n["id"] for n in spec.get("nodes", []) if n.get("shape") == "terminator"]
        if terms and spec.get("style", "uml") != "gb1526":
            print(f"⚠ 未声明 style=gb1526，却用了跑道形终止符（{', '.join(terms)}）："
                  f"这是 GB 1526 的起止符号，与 UML 活动图混用了", file=sys.stderr)
        if not terms and spec.get("style") == "gb1526":
            print("⚠ style=gb1526 但没有任何 terminator 节点：GB 1526 的起止应是跑道形",
                  file=sys.stderr)
    print(f"{args.out}  {W}×{H}  {len(prims)} 个图元", file=sys.stderr)


if __name__ == "__main__":
    main()
