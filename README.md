# Pixel Skills

**简体中文** · [English](language/en/README.md) · [日本語](language/japan/README.md) · [한국어](language/korea/README.md)

> 参照物都在，做出来还是走样。

论文图有国标，画出来还是五花八门；设计稿的色值就摆在那儿，复刻出来还是差一截。问题不在不知道标准，而在于没人逐条核对——人眼对「差不多」太宽容。

这两个 skill 把标准变成能跑的东西：规则写进 `SKILL.md`，能判的交给脚本，能测的落成数值。**管的是形状、尺寸和格式；内容对不对，还得你自己看。**

## 有什么

### [thesis-diagram](thesis-diagram/) —— 论文图的规范生成与校验

- **看** [在线手册](https://www.axxiu.cn/project/GAIe9QK1/) → 六类图的符号定义、正误对照、交付前自查清单
- **说** `帮我画个用例图` → 按 GB 1526 / UML 2.5 出源码
- **说** `这张流程图规范吗` → 跑脚本查箭头贴合、文字越界、终止符形状
- **附** 20 个正误图例，独立 SVG，坐标可直接抄

### [webpage-cloner](webpage-cloner/) —— 网页截图转前端代码

- **看** [在线手册](https://www.axxiu.cn/project/hm0v82sg/) → 拆图取色量间距的方法、正误对照、交付前自查
- **说** `复刻这张截图` → 提取配色、字体、间距
- **说** `把这个设计变成代码` → 输出可直接打开的 HTML/CSS/JS
- **附** 组件模板与样式分析指南

## 它说「不对」的时候，给的是坐标

随便挑张**故意画错**的图例跑一遍：

```console
$ python scripts/check_diagram.py 02-flowchart-bad.svg

02-flowchart-bad.svg：1 个 SVG

  [终止符形状] 2 处
    · SVG #1 "开始" @(150,28)
      圆角矩形 rx=6，跑道形应为 14（= 高/2）
      → rx 改为 14；若走 UML 路线则删掉文字、改用实心圆
    · SVG #1 "结束" @(150,314)
      圆角矩形 rx=6，跑道形应为 14（= 高/2）
      → rx 改为 14；若走 UML 路线则删掉文字、改用实心圆

合计 2 处问题
```

没有「建议检查一下箭头」这种话。给了位置、当前值、目标值、改法。退出码 1，`--json` 供程序读，挂 pre-commit 和 CI 都行。

六项判据，全是数出来的：

| 检查项 | 判据 | 典型成因 |
|---|---|---|
| 箭头未贴合 | 箭尖离最近图元 > 1.5px | 终点写成「框边 − 2~4px」 |
| 图元越界 | bbox 超出 viewBox | 加内容后忘放大画布 |
| 文字溢出 | 估算宽度超出 viewBox | 换了个更长的词 |
| 终止符形状 | 写着「开始/结束」的框 `rx ≠ 高/2` | 用了工具默认圆角矩形 |
| 用例间流程箭头 | 两个椭圆之间连了实线箭头 | 把用例图当流程图用 |
| 非灰度颜色 | RGB 极差 > 8（`--grayscale`） | 用颜色承载语义 |

## 两个 skill，硬度不一样

说清楚，免得你按同一个预期去用。

**thesis-diagram 有校验器。** 形状对不对能算，所以敢写成判据。画优先走 PlantUML（`start`/`stop` 自动出标准起止符），排不出版式才手写 SVG；手写时箭头端点不能目测，椭圆取交点要解方程，公式在 `references/snippets.md` 里。图例的用法是**照抄不是临摹**——打开对应的 `ok` 文件改内容，从规则起步的人会把「两端半圆」脑补成 `rx="6"`，正是上面报的那个错。

**webpage-cloner 没有校验器。** 「这张图像不像」没有数值可依，目前只能靠人眼判。所以它给的是拆解框架而不是判据：布局、色彩、字体、间距、交互、特效六层提取，交付前过九项自检。它做到「像」，做不到「像素级一致」——这句得说在前面，不然你会拿它当截图比对工具用。

## 判不了什么

脚本和清单够不着的地方，还是你自己：

- 图里的业务逻辑对不对——流程本身画错了，形状再标准也没用
- 配色好不好看、字体选得对不对
- 这张图该不该放进论文这一章
- 复刻出来的页面能不能真的用

## 安装

一条命令，要 Node —— `npx` 自带，不用另装。

### Claude Code / Codex / 其他

```bash
npx skills add Dawei-star/pixel-skills -g
```

`-g` 装到用户级，所有项目可用；不加就只装当前项目。它会自己探测本机有哪些 agent，Cursor、Gemini CLI、Copilot、Windsurf 这些都在支持列表里；想指名就 `-a claude-code`，多个用空格隔开。

先看仓库里有什么：`npx skills add Dawei-star/pixel-skills --list`。更新：`npx skills update`。

### 只给当前项目用

`npx skills add` 不加 `-g`。

## 目录

```
thesis-diagram/
├── SKILL.md              流程与索引
├── references/           symbols.md 规则表、snippets.md 符号片段
├── assets/examples/      20 个 SVG + INDEX.md + gallery.png
└── scripts/              check_diagram.py、extract_examples.py

webpage-cloner/
├── SKILL.md              六层提取 + 九项自检
├── references/           components.md 组件模板、style-analysis.md 拆图方法
└── assets/               reset.css

language/                 en / japan / korea / zn
```

`type-introduce/` 不在仓库里——那是图例的源头，手册发布在线上，改完重跑 `extract_examples.py` 重新抽图例。

## 写新 skill

`SKILL.md` 只放流程和索引，细节拆进 `references/`、`assets/`。

`description` 写触发场景——把用户会说的原话放进去。别用 YAML 折叠块 `>`，部分校验器会把 `>` 当成尖括号。

目录名要等于 `SKILL.md` 里的 `name`：小写字母、数字、连字符。不一致时多数工具不报错，只是静默找不到。
