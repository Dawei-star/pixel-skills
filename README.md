# Pixel Skills

**简体中文** · [English](language/en/README.md) · [日本語](language/japan/README.md) · [한국어](language/korea/README.md)

参照物都在，做出来还是走样。论文图有国标，画出来还是五花八门；设计稿的色值就摆在那儿，复刻出来还是差一截。问题不在不知道标准，而在于没人逐条核对——人眼对「差不多」太宽容。

Pixel Skills is a set of agent skills that turn an objective reference — a national standard, a design mockup, a working build — into something that can run: the rules go into `SKILL.md`, whatever is judgeable becomes a script, whatever is measurable ends up as a number.

管的是形状、尺寸和格式；内容对不对，还得你自己看。

---

<p align="center">  
  <img src="assets/icon.png" width="260" alt="Pixel Skills">  
</p>

<p align="center">  
  <img src="https://img.shields.io/badge/platform-any-lightgrey" alt="platform">  
  <img src="https://img.shields.io/badge/format-SKILL.md-blue" alt="format">  
  <a href="https://github.com/Dawei-star/pixel-skills/stargazers"><img src="https://img.shields.io/github/stars/Dawei-star/pixel-skills" alt="stars"></a>  
  <a href="https://github.com/Dawei-star/pixel-skills/issues"><img src="https://img.shields.io/github/issues/Dawei-star/pixel-skills" alt="issues"></a>  
  <img src="https://img.shields.io/github/last-commit/Dawei-star/pixel-skills" alt="last commit">  
</p>

## 这是个会长大的库

不只是两个 skill。目标是把「标准明明有、做起来照样走样」这类活一件件收进来——代码、学习、日常，凡是能拆出客观参照物的，都值得做成能跑的东西。

进库要过三道门：

| 门        | 判据                             | 过不了的例子         |
| -------- | ------------------------------ | -------------- |
| **有参照物** | 存在一个客观的「对」：国标、设计稿、别人的成品、可复现的实验 | 「帮我写得好一点」      |
| **能判**   | 至少一部分能落成数值或脚本，不是全靠人眼           | 「这个配色高级吗」      |
| **会重复**  | 这活你干第二次。一次性的事做成 skill 是浪费      | 「把这个 JSON 转一次」 |

三道门都过才动手写。所以这个库会长，但不会变成什么都往里塞的杂物间。

## 现在有什么

两件，都在代码这一格。学习和日常两格还空着，遇到对的活再填。

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
assets/icon.png           仓库图标
```

`type-introduce/` 不在仓库里——那是图例的源头，手册发布在线上，改完重跑 `extract_examples.py` 重新抽图例。

## 往里加东西

先过上面三道门，过不了就别做。

- `SKILL.md` 只放流程和索引，细节拆进 `references/`、`assets/`
- `description` 写触发场景——把用户会说的原话放进去。别用 YAML 折叠块 `>`，部分校验器会把 `>` 当成尖括号
- 目录名要等于 `SKILL.md` 里的 `name`：小写字母、数字、连字符。不一致时多数工具不报错，只是静默找不到
- 能写成判据的，就别写成叮嘱。「注意箭头要贴合」没人执行得了，`> 1.5px` 报错才会

## 欢迎投稿

这套东西缺的不是想法，是人手。你手头要是有那种「标准明明有、做起来照样走样」的活，或者想给现有的两个 skill 补规则、补图例、挑错，都欢迎寄过来。过不了三道门也行——先说清楚你撞上的是什么。

**邮箱**：<seatamisi@163.com>　·　也可以在 [Issues](https://github.com/Dawei-star/pixel-skills/issues) 里开一条
