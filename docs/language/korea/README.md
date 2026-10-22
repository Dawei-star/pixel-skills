# Pixel Skills

[简体中文](../../../README.md) · [English](../en/README.md) · [日本語](../japan/README.md) · **한국어**

> 기준은 있는데, 결과물은 여전히 어긋난다.

논문 그림에는 국가 표준이 있는데도 결과물은 제각각입니다. 디자인의 색상 값은 그 자리에 있는데도 재현하면 한 단계 어긋납니다. 문제는 표준을 모르는 것이 아니라, 아무도 항목별로 대조하지 않는다는 것 — 사람의 눈은 "거의 맞음"에 너무 관대합니다.

이 두 skill은 표준을 실행할 수 있는 형태로 바꿉니다. 규칙은 `SKILL.md`에, 판정할 수 있는 것은 스크립트에, 측정할 수 있는 것은 숫자로. **담당하는 것은 모양·치수·형식까지. 내용이 맞는지는 직접 확인하셔야 합니다.**

## 무엇이 들어 있나

### [thesis-diagram](../../../thesis-diagram/) — 논문 그림 생성과 검사

- **읽기** [온라인 매뉴얼](https://www.axxiu.cn/project/GAIe9QK1/) → 여섯 가지 그림의 기호 정의, 정오 대조, 제출 전 체크리스트
- **말하면** `유스케이스 다이어그램 그려줘` → GB 1526 / UML 2.5 기준 소스 출력
- **말하면** `이 순서도 규격에 맞아?` → 화살표 접합, 글자 넘침, 종료 기호 모양을 스크립트로 검사
- **포함** 정오 예시 20점. 독립 SVG라 좌표를 그대로 가져다 쓸 수 있음

### [webpage-cloner](../../../webpage-cloner/) — 스크린샷에서 프런트엔드 코드로

- **읽기** [온라인 매뉴얼](https://www.axxiu.cn/project/hm0v82sg/) → 색과 여백을 재는 방법, 정오 대조, 납품 전 점검
- **말하면** `이 스크린샷 다시 만들어줘` → 팔레트·서체·여백 추출
- **말하면** `이 디자인을 코드로 바꿔줘` → 바로 열리는 HTML/CSS/JS 출력
- **포함** 컴포넌트 템플릿과 스타일 분석 가이드

## 설치

명령 한 줄. Node가 필요합니다 — `npx`는 Node에 포함되어 있습니다.

### Claude Code / Codex / 그 외

```bash
npx skills add Dawei-star/pixel-skills -g
```

`-g`를 붙이면 사용자 단위로 설치되어 모든 프로젝트에서 쓸 수 있고, 빼면 현재 프로젝트에만 설치됩니다. 설치된 에이전트를 자동으로 감지하며 Cursor, Gemini CLI, Copilot, Windsurf 등이 지원 목록에 있습니다. 직접 지정하려면 `-a claude-code`, 여러 개는 공백으로 구분합니다.

하나만 설치하려면 `--skill`을 붙입니다.

```bash
npx skills add Dawei-star/pixel-skills --skill thesis-diagram -g
npx skills add Dawei-star/pixel-skills --skill webpage-cloner -g
```

먼저 저장소에 뭐가 있는지 보려면 `npx skills add Dawei-star/pixel-skills --list`. 업데이트는 `npx skills update`.

### 현재 프로젝트에만

`npx skills add`를 `-g` 없이 실행합니다.

## 새 skill 작성하기

`SKILL.md`에는 흐름과 색인만 두고, 세부 내용은 `references/`와 `assets/`로 나눕니다.

`description`에는 발동 조건을 씁니다 — 사용자가 실제로 할 법한 말을 그대로 넣으세요. YAML 접기 블록(`>`)은 쓰지 마세요. 일부 검증기는 `>`를 꺾쇠괄호로 읽습니다.

디렉터리 이름은 `SKILL.md`의 `name`과 같아야 합니다. 소문자·숫자·하이픈만. 어긋나도 대부분의 도구는 오류를 내지 않고, 그냥 조용히 찾지 못합니다.
