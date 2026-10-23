# 校验器自测

改动 `check_diagram.py` 后跑一遍这里，两个方向都要守住：**该报的报得出，不该报的不许报**。

## 该报的（退出码 1）

`blindspots.svg` —— 手写 SVG 的五种"局部看都对、整张看是乱"：

| 缺陷 | 在图上的样子 |
|---|---|
| 连线横穿图元 | B 右侧出发的线横穿 D 框，落到 E 上 |
| 箭头悬空 | 有根箭头指向 (180,200) 那片空地 |
| 图元重叠 | 右上两个框压在一起 |
| 文字挤爆所在框 | "用户登录并校验权限" 撑出 100 宽的框 |
| 线跑出画布 | 顶部一条线伸到 x=470（viewBox 只到 400） |

`plantuml-broken.svg` —— 由 `plantuml-activity.svg` 改出来的：把第 3 个处理框硬挪到 (95,62)，压住第 1 个。
它验证的是 **PlantUML 的描边写在 `style` 里**——识别不到就会让整张图的图元检查静默失效，一声不吭地报"通过"。

```bash
python scripts/check_diagram.py scripts/tests/blindspots.svg        # 期望 ≥5 处
python scripts/check_diagram.py scripts/tests/plantuml-broken.svg   # 期望 ≥1 处
```

## 不该报的（退出码 0）

```bash
python scripts/check_diagram.py scripts/tests/plantuml-usecase.svg
python scripts/check_diagram.py scripts/tests/plantuml-activity.svg
python scripts/check_diagram.py assets/examples/*-ok.svg            # 11 张全部 0 误报
```

`*-ok.svg` 那 11 张是误报底线。宁可漏报也不能把它们判红——判红一次，这个工具就没人信了。

## 两份 PlantUML 夹具是怎么来的

```bash
java -Dfile.encoding=UTF-8 -jar plantuml.jar -charset UTF-8 -tsvg probe.puml
```

**`-charset UTF-8` 不能省**：PlantUML 默认按平台编码读中文，会报
`Some diagram description contains errors` 并指到 `actor 农技员` 那一行，看着像语法写错了。

## PlantUML 产出有三项检查原理上管不了

PlantUML 用独立的小 `polygon` 画箭头，不用 `marker-end`。检查器靠 `marker-end` 认"这条线带箭头"，于是对 PlantUML：

- **箭头贴合 / 箭头悬空**：识别不到箭头，不检查
- **连线交叉**：只统计带箭头的线，等于不检查
- **线宽统一**：PlantUML 描边是 `#181818`，被"只统计纯黑"的口径整体豁免，实际不生效

这不影响出图质量（布线是引擎算的），但意味着 **跑过 check ≠ 这张图读得通**。时序图走向、用例图层次还是得看预览图。
