# Pixel Skills

> 两件"标准明明有，做起来照样走样"的活。

论文图有国标，还是画得五花八门；设计图就在那儿，还原出来色差一截。问题往往不是不知道标准，是没人逐条核对。

这两个 skill 把标准变成能跑的东西：规则写进 `SKILL.md`，能自动查的写成脚本。**只管形状和格式，内容对不对还是得自己看。**

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

## 写新 skill

`SKILL.md` 只放流程和索引，细节拆进 `references/`、`assets/`。

`description` 写触发场景——把用户会说的原话放进去。别用 YAML 折叠块 `>`，部分校验器会把 `>` 当成尖括号。

目录名要等于 `SKILL.md` 里的 `name`：小写字母、数字、连字符。不一致时多数工具不报错，只是静默找不到。
