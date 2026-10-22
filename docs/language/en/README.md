# Pixel Skills

[简体中文](../../../README.md) · **English** · [日本語](../japan/README.md) · [한국어](../korea/README.md)

The reference exists. The output still drifts. Thesis figures have a national standard, and they still come out inconsistent. The design's colour values are right there in the mockup, and the rebuild still misses by a shade. The problem isn't not knowing the standard — it's that nobody checks against it item by item. The eye is too forgiving of "close enough".

Pixel Skills is a set of agent skills that turn an objective reference — a national standard, a design mockup, a working build — into something that can run: the rules go into `SKILL.md`, whatever is judgeable becomes a script, whatever is measurable ends up as a number.

They cover shape, size and format. Whether the content is right is still on you.

---

<p align="center">
  <img src="../../assets/icon.png" width="260" alt="Pixel Skills">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-any-lightgrey" alt="platform">
  <img src="https://img.shields.io/badge/format-SKILL.md-blue" alt="format">
  <img src="https://img.shields.io/github/stars/Dawei-star/pixel-skills" alt="stars">
  <img src="https://img.shields.io/github/issues/Dawei-star/pixel-skills" alt="issues">
  <img src="https://img.shields.io/github/last-commit/Dawei-star/pixel-skills" alt="last commit">
</p>

## What's inside

### [thesis-diagram](../../../thesis-diagram/) — generate and audit thesis figures

- **Read** [the online handbook](https://www.axxiu.cn/project/GAIe9QK1/) → symbol definitions for six diagram types, right/wrong pairs, a pre-submission checklist
- **Say** `draw me a use case diagram` → emits source per GB 1526 / UML 2.5
- **Say** `is this flowchart compliant?` → a script checks arrow attachment, text overflow, terminator shape
- **Ships with** 20 right/wrong examples as standalone SVGs, coordinates ready to copy

### [webpage-cloner](../../../webpage-cloner/) — screenshot to front-end code

- **Read** [the online handbook](https://www.axxiu.cn/project/hm0v82sg/) → how to measure colours and spacing, right/wrong pairs, pre-delivery checks
- **Say** `rebuild this screenshot` → extracts palette, type scale, spacing
- **Say** `turn this design into code` → outputs HTML/CSS/JS you can open directly
- **Ships with** component templates and a style-analysis guide

## Install

One command. Needs Node — `npx` ships with it.

### Claude Code / Codex / others

```bash
npx skills add Dawei-star/pixel-skills -g
```

`-g` installs at user level, so every project can use it; drop it to install into the current project only. The CLI detects which agents you already have — Cursor, Gemini CLI, Copilot and Windsurf are all supported. To name them explicitly add `-a claude-code`; separate several with spaces.

To install just one, add `--skill`:

```bash
npx skills add Dawei-star/pixel-skills --skill thesis-diagram -g
npx skills add Dawei-star/pixel-skills --skill webpage-cloner -g
```

See what's in the repo first: `npx skills add Dawei-star/pixel-skills --list`. Update: `npx skills update`.

### Current project only

Run `npx skills add` without `-g`.

## Writing a skill

Keep `SKILL.md` to flow and index; push the detail into `references/` and `assets/`.

Write `description` as trigger conditions — the words users will actually say. Don't use YAML folded blocks (`>`); some validators read `>` as an angle bracket.

The directory name must equal `name` in `SKILL.md`: lowercase letters, digits, hyphens. Most tools won't raise an error on a mismatch — they just silently fail to find it.

## Contributing

What this repo lacks isn't ideas — it's hands. If you have work of the kind where the standard exists and the output still drifts, or you want to add rules, examples or corrections to the two skills here, send it over. Rough ideas are fine too — just describe what you ran into.

**Email**: [seatamisi@163.com](mailto:seatamisi@163.com) · or open an [issue](https://github.com/Dawei-star/pixel-skills/issues)
