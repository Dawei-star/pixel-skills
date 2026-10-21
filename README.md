# Skills

> 两件"标准明明有，做起来照样走样"的活。

论文图有国标，还是画得五花八门；设计图就在那儿，还原出来色差一截。问题往往不是不知道标准，是没人逐条核对。

这两个 skill 把标准变成能跑的东西：规则写进 `SKILL.md`，能自动查的写成脚本。**只管形状和格式，内容对不对还是得自己看。**

## 有什么

### [thesis-diagram](thesis-diagram/) —— 论文图的规范生成与校验

- **说** `帮我画个用例图` → 按 GB 1526 / UML 2.5 出源码
- **说** `这张流程图规范吗` → 跑脚本查箭头贴合、文字越界、终止符形状
- **附** 20 个正误图例，独立 SVG，坐标可直接抄

### [webpage-cloner](photo%20analyse/) —— 网页截图转前端代码

- **说** `复刻这张截图` → 提取配色、字体、间距
- **说** `把这个设计变成代码` → 输出可直接打开的 HTML/CSS/JS
- **附** 组件模板与样式分析指南

## 安装

没有依赖，不用构建。把目录复制到工具加载 skill 的位置，**重开会话生效**。

<details>
<summary><strong>WorkBuddy</strong></summary>

```bash
cp -r thesis-diagram ~/.workbuddy/skills/
cp -r "photo analyse" ~/.workbuddy/skills/webpage-cloner
```

只给当前项目用，复制到 `<项目>/.workbuddy/skills/`。

</details>

<details>
<summary><strong>Claude Code</strong></summary>

```bash
cp -r thesis-diagram ~/.claude/skills/
cp -r "photo analyse" ~/.claude/skills/webpage-cloner
```

只给当前项目用，复制到 `<项目>/.claude/skills/`。

</details>

<details>
<summary><strong>其他工具</strong></summary>

找到它的 skills 目录（一般形如 `~/.<工具名>/skills/`），照上面两句复制。

</details>

第二条命令为什么要改名：`photo analyse` 目录带空格，而它的 `name` 是 `webpage-cloner`。**目录名必须等于 `SKILL.md` 里的 `name`**，只能是 hyphen-case（小写字母、数字、连字符）。不一致时多数工具不报错，只是静默找不到。

## 写新 skill

`SKILL.md` 只放流程和索引，细节拆进 `references/`、`assets/`。

`description` 写触发场景——把用户会说的原话放进去。别用 YAML 折叠块 `>`，部分校验器会把 `>` 当成尖括号。
