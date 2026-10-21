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

## 安装（30 秒）

装一次，之后不用管。Claude Code 和 Codex 走插件市场，WorkBuddy 复制目录。**挑一个装就行，别都装**——两边都装，每个 skill 会出现两份。

### Claude Code

```bash
claude plugin marketplace add Dawei-star/Skills
claude plugin install thesis-diagram@dawei-skills
claude plugin install webpage-cloner@dawei-skills
```

装完自带更新，仓库推送后自动跟上。

### Codex

```bash
codex plugin marketplace add Dawei-star/Skills
codex plugin install thesis-diagram@dawei-skills
codex plugin install webpage-cloner@dawei-skills
```

启动时更新。

### WorkBuddy

还没有命令行入口，复制目录：

```bash
cp -r thesis-diagram ~/.workbuddy/skills/
cp -r "photo analyse" ~/.workbuddy/skills/webpage-cloner
```

改了要重新复制一次，重开会话生效。

### 只给当前项目用

把命令里的 `~/.workbuddy` 换成 `<项目>/.workbuddy`，`~/.claude` 换成 `<项目>/.claude`。

复制那条命令为什么要改名：`photo analyse` 目录名带空格，而它的 `name` 是 `webpage-cloner`。**目录名必须等于 `SKILL.md` 里的 `name`**，只能是小写字母、数字、连字符。不一致时多数工具不报错，只是静默找不到。走插件市场的不用管，`marketplace.json` 已经指好了。

## 写新 skill

`SKILL.md` 只放流程和索引，细节拆进 `references/`、`assets/`。

`description` 写触发场景——把用户会说的原话放进去。别用 YAML 折叠块 `>`，部分校验器会把 `>` 当成尖括号。
