#!/usr/bin/env python3
"""Pull every correct/wrong example out of the handbook into standalone SVG files.

Usage:
    python extract_examples.py 论文图表规范手册.html
    python extract_examples.py 手册.html --out ./assets/examples

Each extracted file keeps the original coordinates, so it can be copied or
re-rendered as-is. A shared <defs> block is injected so arrows show up when the
file is opened on its own.
"""

import argparse
import re
from pathlib import Path

TOPICS = {
    "s1": ("flowchart", "流程图 GB 1526"),
    "s2a": ("usecase", "用例图"),
    "s2b": ("class", "类图"),
    "s2c": ("sequence", "时序图"),
    "s2d": ("activity", "活动图"),
    "s2e": ("state", "状态图"),
    "s2f": ("deployment", "部署图"),
    "s2g": ("component", "组件图"),
    "s3": ("er", "E-R 图"),
    "s4": ("dfd", "数据流图"),
    "s5": ("arch", "架构图"),
}

DEFS = """<defs>
<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1 L9 5 L1 9 Z" fill="#2C2C2A"/></marker>
<marker id="aro" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M1.5 1.5 L9 5 L1.5 8.5" fill="none" stroke="#2C2C2A" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></marker>
<marker id="tri" viewBox="0 0 12 12" refX="10.5" refY="6" markerWidth="11" markerHeight="11" orient="auto"><path d="M1.5 1.5 L10.5 6 L1.5 10.5 Z" fill="#FFFFFF" stroke="#2C2C2A" stroke-width="1.1" stroke-linejoin="round"/></marker>
<marker id="crow" viewBox="0 0 12 12" refX="10" refY="6" markerWidth="10" markerHeight="10" orient="auto"><path d="M1 1 L10 6 L1 11" fill="none" stroke="#2C2C2A" stroke-width="1.2" stroke-linecap="round"/></marker>
</defs>"""


def nearest_topic(html, pos):
    best = None
    for key in TOPICS:
        found = html.rfind(f'id="{key}"', 0, pos)
        if found != -1 and (best is None or found > best[0]):
            best = (found, key)
    return best[1] if best else None


def classify(html, pos):
    """Only accept SVGs that sit directly inside a cmp-body; symbol-table icons
    live elsewhere and must be skipped."""
    prefix = html[max(0, pos - 200):pos]
    if "cmp-body" not in prefix:
        return None
    ok = html.rfind('cmp-card ok', 0, pos)
    bad = html.rfind('cmp-card no', 0, pos)
    if ok == -1 and bad == -1:
        return None
    return "ok" if ok > bad else "bad"


def normalise(svg):
    """Give the fragment a namespace and a defs block so it opens standalone."""
    svg = re.sub(r'\sclass="[^"]*"', "", svg, count=1)
    if "xmlns=" not in svg[:200]:
        svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    if "<defs>" in svg:
        return svg
    head_end = svg.index(">") + 1
    return svg[:head_end] + "\n" + DEFS + svg[head_end:]


def build_gallery(out, rows):
    """One page with correct/wrong pairs side by side, for eyeballing."""
    groups = {}
    for r in rows:
        groups.setdefault(r["slug"], []).append(r)

    blocks = []
    for slug, items in groups.items():
        items.sort(key=lambda x: x["file"])  # keep handbook order, pairs stay adjacent
        cells = []
        for it in items:
            mark = "✅ 规范画法" if it["kind"] == "ok" else "❌ 常见错误"
            cls = "ok" if it["kind"] == "ok" else "bad"
            cells.append(
                f'<figure class="{cls}"><img src="{it["file"]}" alt="">'
                f'<figcaption>{mark}</figcaption></figure>'
            )
        blocks.append(
            f'<section><h2>{items[0]["topic"]}</h2><div class="row">'
            + "".join(cells) + "</div></section>"
        )

    html = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<title>论文图表 · 正误对照</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#FAF9F5;color:#1F1E1B;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;
     padding:40px;max-width:1500px;margin:0 auto}
h1{font-size:24px;font-weight:600;margin-bottom:6px}
.sub{color:#8F8D85;font-size:13px;margin-bottom:32px}
section{margin-bottom:34px}
h2{font-size:15px;font-weight:600;margin-bottom:12px;color:#5F5E5A;
   border-left:3px solid #0F6E56;padding-left:10px}
.row{display:flex;gap:16px;align-items:stretch;flex-wrap:wrap}
figure{background:#fff;border:1px solid #E8E5DC;border-radius:12px;padding:14px;
       flex:1 1 300px;max-width:460px;display:flex;flex-direction:column}
figure.ok{border-color:#9FE1CB}
figure.bad{border-color:#F5C4C4}
img{width:100%;height:auto;display:block;flex:1;object-fit:contain}
figcaption{font-size:12px;margin-top:10px;text-align:center;color:#5F5E5A}
figure.ok figcaption{color:#0F6E56;font-weight:600}
figure.bad figcaption{color:#A32D2D;font-weight:600}
</style></head><body>
<h1>论文图表 · 正误对照</h1>
<div class="sub">从规范手册抽出，坐标原样保留，可直接复制到自己的图里</div>
""" + "\n".join(blocks) + "\n</body></html>"

    (out / "gallery.html").write_text(html, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html", help="handbook .html")
    ap.add_argument("--out", default=None, help="output directory")
    args = ap.parse_args()

    src = Path(args.html)
    out = Path(args.out) if args.out else src.parent / "assets" / "examples"
    out.mkdir(parents=True, exist_ok=True)

    html = src.read_text(encoding="utf-8")
    rows = []
    seq = 0

    for m in re.finditer(r"<svg[^>]*>.*?</svg>", html, re.S):
        topic = nearest_topic(html, m.start())
        kind = classify(html, m.start())
        if not topic or not kind:
            continue

        slug, label = TOPICS[topic]
        seq += 1
        name = f"{seq:02d}-{slug}-{kind}.svg"
        svg = normalise(m.group(0))
        (out / name).write_text(svg, encoding="utf-8")

        vb = re.search(r'viewBox="([^"]+)"', svg)
        rows.append({
            "file": name,
            "slug": slug,
            "topic": label,
            "kind": kind,
            "viewBox": vb.group(1) if vb else "?",
        })

    index = ["# 图例清单", "",
             "从 `论文图表规范手册.html` 抽出，坐标原样保留。`ok` = 规范画法，`bad` = 错误示范。",
             "", "| 文件 | 图种 | 类型 | viewBox |", "|---|---|---|---|"]
    for r in rows:
        tag = "✅ ok" if r["kind"] == "ok" else "❌ bad"
        index.append(f"| `{r['file']}` | {r['topic']} | {tag} | `{r['viewBox']}` |")
    (out / "INDEX.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    build_gallery(out, rows)

    print(f"抽出 {len(rows)} 个图例 → {out}")
    ok = sum(1 for r in rows if r["kind"] == "ok")
    print(f"  规范画法 {ok} 个，错误示范 {len(rows) - ok} 个")
    for r in rows:
        print(f"  {r['file']:<26} {r['topic']}")


if __name__ == "__main__":
    main()
