<h1 align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-dark.svg">
    <img alt="episteme" src="docs/assets/logo-light.svg" width="456">
  </picture>
</h1>

<p align="center">
  <a href="https://github.com/junjslee/episteme/releases"><img alt="Latest Release" src="https://img.shields.io/github/v/release/junjslee/episteme?include_prereleases&label=release&logo=github"></a>
  <a href="https://github.com/junjslee/episteme/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/github/license/junjslee/episteme?color=informational"></a>
  <a href="https://github.com/junjslee/episteme"><img alt="Unique Clones" src="https://img.shields.io/badge/dynamic/json?color=success&label=Unique%20Clones&query=uniques&url=https://gist.githubusercontent.com/junjslee/0a171c9a54b11948bbd1562f4f040465/raw/clone.json&logo=github"></a>
</p>

<p align="center"><a href="https://epistemekernel.com"><b>epistemekernel.com</b></a> · <a href="./README.md">English</a></p>

> **이미 사용 중인 AI 코딩 에이전트를 위한 생각의 틀(Thinking Framework).** 고위험 작업(high-impact move) — 단순한 셸 명령어가 아니라 *작업 자체* — 을 수행하기 전에, 에이전트는 자신의 추론을 디스크에 명시해야 한다: 핵심 질문(Core Question), 아는 것(Knowns), 모르는 것(Unknowns), 이 계획이 틀렸다는 걸 증명할 조건(Disconfirmation). 그 표면(surface)이 비어 있거나 공허하면 — 심지어 운영자 본인이 요청한 작업이라도 — 파일 시스템 훅이 실행을 거부한다. 해결된 모든 갈등은 재사용 가능한 프로토콜(protocol)로 추출되어 변조 불가능한 해시 체인(tamper-evident hash chain)에 기록되고, 다음 매칭 결정 시점에 자동으로 표면화(surface back)된다. **Sovereign Cognitive Kernel** — **생각의 틀**, *프롬프트가 아니라 자세(posture over prompt)*로 구축되었다.

**[60초 만에 보기 ↓](#60초-만에-보기)** · **[설치 ↓](#빠른-시작)** · **[왜 파일 시스템인가, 왜 프롬프트가 아닌가 ↓](#문제와-해법)** · **[아키텍처와 철학 ↓](#아키텍처와-철학)**

 ![Episteme — 움직이는 생각의 틀](docs/assets/demo_posture.gif)

---

## TL;DR

오늘날의 AI 에이전트는 **대단히 능숙하다** — 프로덕션 코드를 작성하고, 전체 저장소를 탐색하며, 다단계 워크플로우를 계획한다. 하지만 이들에게 결정적으로 부족한 것은 **컨텍스트 인식(context-awareness)** 과 **사용자 의도로부터의 드리프트(drift)에 대한 방어 메커니즘**이다.

두 개의 신뢰할 만한 출처가 서로 다른 말을 할 때 — *Source A는 이렇게 하라 하고, Source B는 저렇게 하라 한다* — 자기회귀(auto-regressive) 엔진은 어떤 답이 **당신의** 프로젝트, **당신의** 팀의 제약, **당신의** 작업-유형 이력에 맞는지 구별할 수 없다. 그래서 통계적 평균값으로 도피한다: 유창하고, 확신에 차 있지만, 어떤 구체적 컨텍스트에도 맞지 않는 답.

`episteme`는 그 간극을 닫는다. 고위험 명령어가 실행되기 전에, 에이전트는 디스크에 기록되는 네 필드의 **생각의 틀(Thinking Framework)** — **아는 것 · 모르는 것 · 가정 · 반증 조건(Knowns · Unknowns · Assumptions · Disconfirmation)** — 에 자신의 추론을 투영해야 한다. 그 위에 **핵심 질문(Core Question)** 이 놓인다. 이 틀이 해결한 모든 갈등은 재사용 가능한 프로토콜로 추출되어 변조 불가능한 지식 저장소에 커밋되며, 다음 매칭 결정 시점에 선제적으로 표면화된다.

집행은 **구조적(structural)** 이지 권고가 아니다. 프롬프트는 건너뛸 수 있지만, 0이 아닌 종료 코드를 반환하는 파일 시스템 훅은 건너뛸 수 없다.

---

## ABCD 아키텍처 — 네 개의 블루프린트, 하나의 피질

`episteme`는 **AI 에이전트를 위한 전두엽 피질(prefrontal cortex)** 처럼 작동한다: 의도와 행동 사이에 자리를 잡고, 추론이 명시적으로 표현되기 전까지 어떤 행동도 진행되지 못하게 막는다. 네 개의 **인지 블루프린트(Cognitive Blueprints)** — 각각 특정 실패 유형(failure class)에 대응한다 — 이 주어진 작업에 대해 "충분히 명시적"이 무엇을 의미하는지 결정한다:

- **A · Axiomatic Judgment (공리적 판단)** — 신뢰할 만하지만 양립 불가능한 두 출처 사이의 갈등을 해소한다. 에이전트가 *왜* 그들이 충돌하는지, *현재 컨텍스트의 어떤 특징이* 선택을 결정하는지 명명하도록 강제한다.
- **B · Fence Reconstruction (울타리 재구성)** — 물려받은 제약을 보호한다. 제약을 제거하려면 그 원래 목적이 먼저 재구성되어야 한다 — Chesterton의 울타리를 파일 시스템이 강제하는 형태다.
- **C · Consequence Chain (결과 사슬)** — 되돌릴 수 없는 작업을 분해한다 (1차 효과, 2차 효과, 실패 모드 역상, 기저율 참조, 안전 여유).
- **D · Architectural Cascade (구조적 캐스케이드)** — 참조를 끊어버릴 리팩터링과 이름 변경을 잡아낸다. 편집 전에 전체 파급 반경(blast radius)을 열거하도록 에이전트에게 강제한다.

모든 블루프린트 발화 — 그리고 그것이 검증한 모든 결정 — 은 **변조 불가능한 해시 체인**에 커밋된다. 그 체인은 로그가 아니다. 그것은 커널이 나중에 **능동적 가이던스(Active Guidance)** 를 제공하는 방식이다: 다음 매칭 결정 시점에, 관련된 합성 프로토콜이 에이전트가 훈련 분포로 후퇴하기 전에 선제적으로 표면화된다.

결과는 **축적되는(compounds) 프로젝트-맞춤 생각의 틀**이다. 에이전트는 갈등을 해결할 때마다 당신의 코드베이스에 대해 더 예리해진다 — 당신이 훈련시켜서가 아니라, 체인이 기억했기 때문에.

---

## 문제와 해법

### 문제 — 충돌하는 출처, 평균화된 답, 영속하지 않는 노하우

인터넷은 모순된 how-to로 가득하다. 문서는 이렇게 말하고, 시니어 엔지니어는 저렇게 말한다. 두 라이브러리가 같은 버그에 정반대 패턴을 추천한다. 자기회귀 패턴 엔진인 현대 에이전트는 어떤 답이 *이 특정 컨텍스트에 맞는지* 구별할 수 없다 — 왜냐하면 *맞는지(fit)* 의 여부는 토큰 빈도에 대한 패턴 매치가 아니라 **인과적 세계 모델 판단**이기 때문이다. 그래서 평균을 낸다. 출력은 권위 있게 들리지만 어떤 구체적 컨텍스트에도 맞지 않고, 빠뜨림으로써 오도한다.

프롬프트로는 이 문제를 해결할 수 없다:

- 시스템 프롬프트 리마인더는 한 번의 호출에만 산다.
- `CLAUDE.md`의 주의사항은 데드라인이 닥치면 순식간에 무시된다.
- **노하우** — *"이런 모양의 문제에서는 이렇게 하라"* 라는, 환원 불가능하게 컨텍스트-특정적인 규칙 — 은 더 좋은 문구로 가르칠 수 없다. 추출되고, 저장되고, 다시 표면화되어야 한다.

### 해법 — 파일 시스템 수준의 생각의 틀

`episteme`는 **의도가 상태 변화와 만나는 순간**을 가로챈다. 고위험 작업(`git push`, `npm publish`, `terraform apply`, DB 마이그레이션, lockfile 편집 등) 이전에, 에이전트는 디스크 위의 구조화된 표면에 자신의 추론을 투영해야 한다:

| 필드 | 에이전트가 반드시 명시해야 하는 것 |
|---|---|
| **핵심 질문 (Core Question)** | 이 행동이 실제로 답하려는 단 하나의 질문 (질문 치환 실패모드 대응). |
| **아는 것 (Knowns)** | 검증된 사실, 출처 인용, 측정값 — 그럴듯한 추측이 아님. |
| **모르는 것 (Unknowns)** | 명명되고 분류 가능한 결손 — 모호한 *"리스크가 있을 수 있음"* 이 아님. |
| **가정 (Assumptions)** | 하중을 지탱하는 신념, 반증 가능하도록 명시. |
| **반증 조건 (Disconfirmation)** | 이 계획이 틀렸음을 증명할 관찰 가능한 사건 — 행동 전에 사전 약속. |

유효성은 **구조적으로** 검증된다: 최소 콘텐츠 길이, 게으른 플레이스홀더 금지 (`none`, `n/a`, `tbd`, `해당 없음`), 정규화된 명령어 스캐닝으로 `subprocess.run(['git','push'])`와 `os.system('git push')` 같은 우회 형태까지 포착. 에이전트가 작성한 셸 스크립트는 여러 호출에 걸친 상태 인터셉터가 딥스캔한다. 표면이 없거나 유효하지 않으면 작업은 거부된다 (`exit 2`). 기본값은 엄격(strict)이며, 권고 모드(advisory — 경고만 하고 차단하지 않음)는 프로젝트별로 opt-in이다: `touch .episteme/advisory-surface`.

이것이 프롬프트 리마인더와 컴파일러의 차이다: 하나는 부탁하고, 하나는 진행을 거부한다.

---

## 프로토콜 합성과 능동적 가이던스 — 궁극의 비전

`episteme`는 **단순한 차단기가 아니다**. 이 프레임워크의 진짜 역할은 해결된 모든 갈등을 지속 가능한 노하우로 전환하여 다음 매칭 결정 시점에 에이전트가 자동으로 재적용하도록 만드는 것이다.

루프는 다음과 같다 (v1.0 RC 출시 · CP1–CP10 · 565/565 통과 — [`docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`](./docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md) 참조):

1. **갈등 감지.** 에이전트가 아직 완전히 해결되지 않은 컨텍스트에 대해 유효해 보이지만 양립 불가능한 두 접근을 만난다.
2. **평균 내지 말고, 분해하라.** 생각의 틀은 "평균" 답을 거부한다. 출처가 *왜* 충돌하는지, 컨텍스트의 어떤 특징이 결정의 저울을 기울이는지 추출하도록 에이전트에게 강제한다.
3. **컨텍스트-맞춤 프로토콜 합성.** 해결된 *"컨텍스트 X에서는 Y를 하라"* 규칙이 append-only, 해시 체인으로 연결된 지식 저장소에 커밋된다 — 변조 불가능이므로, 에이전트는 배운 교훈을 몰래 다시 쓸 수 없다.
4. **능동적으로 가이드하라.** 다음 매칭 결정에서 — 몇 주 뒤든, 세션이나 도구를 건너서든 — 커널은 프로토콜을 **선제적으로** 표면화한다. 당신이 기억해서 물어볼 필요가 없다.
5. **자기 유지보수하라.** 에이전트가 드리프트(낡은 설정, 폐기된 API, 핵심 로직 불일치)를 발견하면, *패치 vs. 리팩터링* 의 정직한 평가를 강제하고, 이동하기 전에 전체 파급 반경(CLI · 설정 · 스키마 · 문서 · 테스트 · 외부 표면)을 동기화하도록 요구한다.

지식 저장소는 메모리인 척하는 벡터 스토어가 아니다. **구조적이고, 사람이 읽을 수 있으며, 버전 관리되는 아티팩트** — 당신이 읽고, 편집하고, 포크하고, 어댑터(Claude Code, Cursor, Hermes, 미래의 도구) 사이에서 마이그레이션할 수 있다. **커널은 도구보다 오래 산다.**

---

## 나는 이걸 하고 싶은데 → 이렇게 하세요

| 목표 | 명령어 / 포인터 |
|---|---|
| 같은 프롬프트에 대한 *생각의 틀 켜짐 vs 꺼짐* 비교 | [`demos/03_differential/`](./demos/03_differential/) · [`scripts/demo_posture.sh`](./scripts/demo_posture.sh) |
| 프레임워크가 end-to-end로 생성하는 것 확인 | [`demos/01_attribution-audit/`](./demos/01_attribution-audit/) · [`demos/02_debug_slow_endpoint/`](./demos/02_debug_slow_endpoint/) |
| Claude Code 플러그인으로 한 줄 설치 | `/plugin marketplace add junjslee/episteme` |
| 내 머신에 설치 (CLI + 수정 가능한 커널) | `pip install -e . && episteme init` — [`INSTALL.md`](./INSTALL.md) 참조 |
| 3분 안에 설치되는 것 이해하기 | [`kernel/SUMMARY.md`](./kernel/SUMMARY.md) · [`docs/POSTURE.md`](./docs/POSTURE.md) |
| Slack 스레드로부터 reasoning surface 초안 | `episteme capture --input thread.txt --output surface.json` |
| 내가 쓰는 모든 AI 도구에 정체성 동기화 | `episteme sync` |
| 작업 스타일 + 추론 자세 인코딩 | `episteme setup . --interactive` |
| 프로젝트 유형에 맞는 harness 적용 | `episteme detect . && episteme harness apply <type> .` |
| 언제 이 커널을 쓰면 *안 되는지* | [`kernel/KERNEL_LIMITS.md`](./kernel/KERNEL_LIMITS.md) |
| 차용한 개념의 출처 찾기 | [`kernel/REFERENCES.md`](./kernel/REFERENCES.md) |
| 내 세팅 감사 | `episteme doctor` |
| 더 깊은 철학 읽기 (doxa · episteme · praxis · 결) | [`docs/NARRATIVE.md`](./docs/NARRATIVE.md) |

---

## 60초 만에 보기

라이브 사이트 + 비주얼 대시보드 — 둘 다 커널 자체의 `cp7-chained-v1` 해시 체인에 대해 렌더링됨. Vercel 배포 가이드는 [`web/README.md`](./web/README.md) 참조.

세 가지 데모, 증명하는 강도 순:

- **[`demos/03_differential/`](./demos/03_differential/) — 회의론자를 전향시키는 데모.** *완전히 같은 프롬프트, 생각의 틀 OFF vs. ON.* PM이 2-스프린트 분량의 시맨틱 검색 스코프를 요청한다; OFF는 *어떻게* 에 답한다; ON은 *할지 말지* 에 답한다. [`DIFF.md`](./demos/03_differential/DIFF.md)가 프레임워크가 잡아낸 명명된 실패 모드를 보여준다.
- [`demos/02_debug_slow_endpoint/`](./demos/02_debug_slow_endpoint/) — 실제 p95 리그레션에 적용된 프레임워크. 유창하게-틀린 *"캐시를 추가하라"* 답은 핵심 질문 게이트에서 거부되고, 스키마 수준의 근본 원인이 대신 산출된다.
- [`demos/01_attribution-audit/`](./demos/01_attribution-audit/) — 정규 4-아티팩트 모양 (reasoning-surface → decision-trace → verification → handoff). 커널이 자기 자신에게 적용되어, 차용된 모든 개념이 1차 출처로 역추적 가능한지 감사한다.

셋 중 하나라도 열어보라. 철학을 읽기 전에 `episteme`가 무엇을 산출하는지 알게 될 것이다.

---

## 빠른 시작

### 옵션 A — Claude Code 플러그인 마켓플레이스로 설치

Claude Code를 쓴다면 가장 빠른 경로. 이 저장소는 마켓플레이스 매니페스트(`.claude-plugin/marketplace.json`)를 제공하므로, 두 명령어로 마켓플레이스로 추가하고 플러그인을 설치할 수 있다.

Claude Code 안에서:

```
/plugin marketplace add junjslee/episteme
/plugin install episteme@episteme
```

그 후 아무 셸에서나:

```bash
episteme init     # 일회성: 예제에서 개인 메모리 파일 시드
episteme setup    # 작업 스타일 + 인지 프로파일 점수화
episteme sync     # Claude Code와 Hermes로 전파
episteme doctor   # 연결 확인
```

명령어 문법과 업데이트 의미의 권위 있는 참조는 [Claude Code 플러그인 마켓플레이스 문서](https://docs.anthropic.com/en/docs/claude-code/plugins) 참조.

### 옵션 B — 커널을 직접 클론

기여자, 포커, 또는 전체 소스 트리를 로컬에 원하는 경우:

```bash
git clone https://github.com/junjslee/episteme ~/episteme
cd ~/episteme
pip install -e .

episteme init              # 템플릿에서 개인 메모리 파일 생성
episteme setup . --write   # 작업 스타일 + 추론 자세 점수화
episteme sync              # 모든 어댑터로 정체성 전파
episteme doctor            # 연결 확인
```

프로젝트-유형 harness:

```bash
episteme detect .                         # 저장소 분석, harness 추천
episteme harness apply ml-research .      # 적용
episteme new-project . --harness auto     # 스캐폴드 + 자동 감지
```

심화 온보딩 모드, 점수화 차원, 기본값: **[`docs/SETUP.md`](./docs/SETUP.md)**.
전체 명령 레퍼런스: **[`docs/COMMANDS.md`](./docs/COMMANDS.md)**.

---

## 비교

이 공간의 대부분 도구는 에이전트 런타임을 만들거나 애플리케이션용 메모리 API를 제공한다. `episteme`는 당신이 이미 쓰는 개발 도구를 *증강*한다.

| 축 | episteme | Memory APIs (mem0, OpenMemory) | Agent runtimes (Agno, opencode, omo) |
|---|---|---|---|
| **무엇인가** | 개발 도구 간 정체성 + 거버넌스 레이어 | 앱 내장 메모리 API | 에이전트를 실행하는 런타임 |
| **정체성 거주지** | 거버넌스된 마크다운 + JSON, 크로스-툴, 버전 관리 | 벡터/그래프 스토어, 앱마다 | 세션마다 시스템 프롬프트 |
| **동기화** | 한 명령어, 모든 도구 | N/A | N/A (프로젝트별 설정) |
| **노하우 추출** | 파일 시스템 경계에서 강제, 해시 체인 | 불투명한 검색 | 프롬프트 튜닝, 세션마다 |

`episteme`가 메우는 간극: 여러 개발자 AI 도구에 걸쳐 한 명령어로 *거버넌스된 인지 계약*을 동기화하는 다른 프로젝트가 없고, 상태 변화 지점에서 컨텍스트-맞춤 프로토콜 추출을 강제하는 다른 프로젝트도 없다. 런타임과 메모리 API는 서로 다른 레인을 담당한다; `episteme`는 그 위에 앉아 그들에게 *당신이 누구인지*, *어떻게 생각하는지*, *당신의 프로젝트가 이미 무엇을 배웠는지* 를 알게 한다.

---

## 제로-트러스트 실행

OWASP Agentic AI Top 10은 자율 에이전트에 대한 주요 위험 유형으로 프롬프트 인젝션, 목표 탈취, 과도 행위, 무경계 행동을 지목한다. 아는 것 / 모르는 것 / 가정 / 반증 조건 구조는 각각에 대한 구조적 반박이다:

| OWASP Agentic 위험 | episteme 반박 |
|---|---|
| 프롬프트 인젝션 / 목표 탈취 | 실행 시작 전 Core Question 선언; 이탈은 Unknowns로 표면화 |
| 과도 행위 / 무경계 행동 | Frame에서 제약 체제 선언; 가역-우선 정책 강제 |
| 유창한 환각 | Unknowns 필드는 비워둘 수 없음; 행동 전 assumptions 명명 필수 |
| 무한 계획 루프 | Disconfirmation 조건 필수; 증거가 발화하면 루프 종료 |

명명되지 않은 가정은 신뢰되지 않는다. 전제조건(Knowns)과 제약 체제가 선언되기 전에는 어떤 행동도 취해지지 않는다. 커널은 의도와 실행 사이의 검증 레이어다.

---

## 인간 프롬프트 디버깅

`episteme`는 에이전트만 거버넌스하지 않는다 — **인간의 의도를 디버깅한다.** 에이전트가 사용자 요청에 대해 Knowns vs. Unknowns를 매핑할 때, 결함 있는 가정을 실행하기 전에 *원래 프롬프트*의 논리적 공백을 드러낸다. Unknowns 필드는 인간이 자신의 질문이 과소 명세되었음을 깨닫는 지점이 되곤 한다. Disconfirmation 필드는 인간이 반증에 대해 전혀 생각하지 않았음을 깨닫는 지점이 되곤 한다.

이것은 부작용이 아니다. 설계 속성이다: 에이전트가 모르는 것을 선언하도록 강제하는 시스템은, 인간이 명세하지 않은 것을 직면하도록 강제한다.

---

## 저장소 레이아웃

```
episteme/
├── kernel/                     철학 (마크다운; 런타임을 넘어 이동)
├── demos/                      end-to-end 참조 deliverable
├── core/
│   ├── memory/global/          운영자 메모리 (gitignored; 개인)
│   ├── hooks/                  결정론적 안전 + 워크플로우 훅
│   ├── harnesses/              프로젝트-유형별 운영 환경
│   └── schemas/                메모리 + 진화 계약 스키마
├── adapters/                   커널 전달 레이어 (Claude Code, Hermes, …)
├── skills/                     재사용 가능한 운영자 스킬
├── templates/                  프로젝트 스캐폴드, 예제 답변 파일
├── docs/                       런타임 문서, 아키텍처, 계약
├── src/episteme/               CLI + 코어 라이브러리
└── tests/
```

이곳에서 작업하는 모든 에이전트를 위한 저장소 운영 계약: **[`AGENTS.md`](./AGENTS.md)**. LLM 사이트맵: **[`llms.txt`](./llms.txt)**.

---

## CLI 표면

```bash
episteme init
episteme doctor
episteme sync [--governance-pack minimal|balanced|strict]
episteme new-project [path] --harness auto
episteme detect [path]
episteme harness apply <type> [path]
episteme profile [survey|infer|hybrid] [path] [--write]
episteme cognition [survey|infer|hybrid] [path] [--write]
episteme setup [path] [--interactive] [--write] [--sync] [--doctor]
episteme bridge anthropic-managed --input <events.json> [--dry-run]
episteme bridge substrate [list-adapters|describe|verify|push|pull] ...
episteme capture [--input <file>] [--output <file>] [--by <name>]
episteme viewer [--host 127.0.0.1] [--port 37776]
episteme evolve [run|report|promote|rollback] ...
```

전체 참조: [`docs/README.md`](./docs/README.md).

---

## 이 아키텍처의 이유

제품은 생각의 틀이다; 나머지 목록은 그 틀을 진지하게 받아들일 때 자연히 떨어지는 것들이다.

- **피드포워드 인지 제어, 반응적 교정이 아님.** 대부분의 에이전트-안전 시스템은 에러를 관찰한 후 사후 교정한다. `episteme`는 실행 *전에* 실패 모드를 명명하고, 반박되기 전에는 진행을 거부한다. Knowns, Unknowns, Assumptions, Disconfirmation이 *먼저* 선언되고, 행동은 *두 번째*다.
- **인지 계약 (Design by Contract).** 생각의 틀은 Bertrand Meyer의 *Design by Contract*를 추론 자체에 적용한 것이다: **전제조건** (실행 전 성립해야 하는 Knowns + 검증된 Assumptions), **후제조건** (Verification: 핸드오프 시점에 참이어야 하는 것), **불변식** (중단될 수 없는 커널 원칙). 전제조건이 깨지면 에이전트는 진행하지 않는다.
- **가설 → 테스트 → 업데이트, 세션을 넘어 관찰 가능.** 각 Reasoning Surface는 가설을 담고, 각 실행은 결과를 담고, episodic tier는 둘 다 기록하며, 시맨틱 승격 작업은 가설이 선언된 disconfirmation을 *결코* 발화시키지 않는 패턴(캘리브레이션 부채)을 표면화한다. 사고-품질 드리프트가 시간에 걸쳐 감지 가능하다.
- **인지 프로파일은 문서가 아니라 가설이다.** 운영자 프로파일의 9개 인지-스타일 축(`dominant_lens`, `noise_signature`, `explanation_depth` 등)은 집행 임계값을 변조하는 제어 신호이며, 실제 행동의 episodic 기록에 대해 스스로 감사받는다. 주장된 자세 vs. 체현된 자세, 드리프트는 재-도출(re-elicitation)로 표면화.
- **선언된 한계.** [`KERNEL_LIMITS.md`](./kernel/KERNEL_LIMITS.md)는 커널이 틀린 도구일 때를 명명한다. *경계 없는 규율은 신조에 불과하다.*
- **강한 권위 경계.** 저장소 문서 + 전역 메모리가 진실의 원천이다; 도구-네이티브 메모리는 가속일 뿐, 권위가 아니다.
- **크로스-툴 일관성.** Claude Code, Hermes, 그리고 미래의 어댑터 전체에 걸친 하나의 거버넌스된 인지 계약. **프레임워크는 도구보다 오래 산다.**
- **에이전트 인지를 위한 정책 엔진.** `episteme`는 클라우드 인프라에서 OPA(Open Policy Agent)가 하는 역할을 한다: 제안된 *추론 상태*가 선언된 정책을 만족하는지 평가하는 독립 레이어 — 그 후에야 그것이 인가하는 행동이 허용된다. LLM은 런타임이고; `episteme`는 정책 엔진이다.
- **구성에 의한 AI 안전, 덧붙인 것이 아님.** 추론 실패 모드에 반박하는 같은 구조적 게이트가 OWASP Agentic 위험을 닫는다. 보안은 프레임워크에서 자연히 떨어진다.

메모리 모델, Memory Contract v1, Evolution Contract v1, 그리고 관리형 런타임 공존: **[`docs/SYNC_AND_MEMORY.md`](./docs/SYNC_AND_MEMORY.md)**.

---

## 아키텍처와 철학

> 산문 기둥: [`docs/NARRATIVE.md`](./docs/NARRATIVE.md). 노드 주석과 교차 참조가 있는 전체 다이어그램: [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md).

위의 생각의 틀은 *제품 표면*이다. 그 아래에는 고대 그리스 인식론과 한국 미학에서 차용한 구조적 어휘가 있다 — 이 저장소의 모든 다이어그램, 데모, 아티팩트가 렌더링되는 척추(spine)다.

### 삼원 — doxa · episteme · praxis

- **Doxa** (δόξα) — 공통 의견, 기본으로 산출되는 유창한 출력. [`kernel/FAILURE_MODES.md`](./kernel/FAILURE_MODES.md)의 9가지 명명된 실패 모드는 *doxa가 자신을 episteme로 착각하는* 분류학이다.
- **Episteme** (ἐπιστήμη) — 정당화된 지식: 구체적 Knowns, 명명된 Unknowns, 반증 가능한 Disconfirmation. 실행의 전제조건. 저장소의 이름이 된 것.
- **Praxis** (πρᾶξις) — 숙지된 행동: 인가한 규율이 그대로 유지된 채 착지하는 효과. 네 가지 정규 아티팩트(reasoning-surface / decision-trace / verification / handoff)가 그 가시적 형태다.

### 결 · gyeol

한국어 **결**(*gyeol*) 은 나무나 돌의 결 — 따를 때 일관된 형태를 낳고, 거슬러 자를 때 균열하는, 물질 안의 잠재적 패턴-구조 — 을 이름한다. Reasoning Surface의 필드 순서 — Knowns → Unknowns → Assumptions → Disconfirmation — 는 인식론적 규율의 결이다: *정착된 → 열려있는 → 잠정적 → 반증-조건*. 캘리브레이션 루프(`correlation_id`로 결합된 예측 + 결과, `episteme evolve friction`이 분석)는 사이클을 가로질러 자신을 정제하는 결 그 자체다.

### 라이프사이클

```
┌─────────────────────────────────────────────────────────────────────┐
│                         operator (당신)                             │
│           ├── 인지 선호도            ├── 작업 스타일                │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                    episteme sync
                               │
      ┌────────────────────────┼────────────────────────┐
      ▼                        ▼                        ▼
 Claude Code             Hermes (OMO)            미래의 어댑터
 (CLAUDE.md)             (OPERATOR.md)           (같은 커널)
      │                        │                        │
      └────────────────────────┼────────────────────────┘
                               │
                       세션당 루프
                               │
                   Frame → Decompose → Execute → Verify → Handoff
```

**어떤 스택과도 작동.** `episteme`는 LLM 런타임과 독립적으로 작동한다 — LangChain, CrewAI, Claude Code, Cursor, MCP 모두와. 커널은 순수 마크다운; 운영자 프로파일은 일반 JSON; 워크플로우 루프는 벤더-중립. 어댑터 레이어(Claude Code, Hermes, OMO/OMX)는 플러그형이다.

### 커널 파일들

**[`kernel/`](./kernel/)** 에서 시작하라. 순수 마크다운. 코드 없음. 벤더 종속 없음.

| 파일 | 정의하는 것 |
|---|---|
| [`SUMMARY.md`](./kernel/SUMMARY.md) | 30줄 운영적 증류 |
| [`CONSTITUTION.md`](./kernel/CONSTITUTION.md) | 근본 주장, 4가지 원칙, 9가지 실패 모드 |
| [`REASONING_SURFACE.md`](./kernel/REASONING_SURFACE.md) | Knowns / Unknowns / Assumptions / Disconfirmation 프로토콜 |
| [`FAILURE_MODES.md`](./kernel/FAILURE_MODES.md) | 9가지 유창-에이전트 실패 모드 ↔ 반박 아티팩트 (6 Kahneman · 3 거버넌스) |
| [`OPERATOR_PROFILE_SCHEMA.md`](./kernel/OPERATOR_PROFILE_SCHEMA.md) | 운영자 인지 선호도 인코딩 스키마 |
| [`MEMORY_ARCHITECTURE.md`](./kernel/MEMORY_ARCHITECTURE.md) | 5가지 메모리 계층 (working / episodic / semantic / procedural / reflective) |
| [`KERNEL_LIMITS.md`](./kernel/KERNEL_LIMITS.md) | 커널이 틀린 도구일 때; 선언된 간극 |
| [`REFERENCES.md`](./kernel/REFERENCES.md) | 하중을 지탱하는 차용 개념의 출처 |
| [`CHANGELOG.md`](./kernel/CHANGELOG.md) | 버전 관리되는 커널 이력 |

권위 계층: **프로젝트 문서 > 운영자 프로파일 > 커널 기본값 > 런타임 기본값.** 구체가 일반을 이긴다.

---

## 다음으로 읽을 것

| 주제 | 어디로 |
|---|---|
| `episteme`가 설치하는 것 (자세 프레이밍) | [`docs/POSTURE.md`](./docs/POSTURE.md) |
| v1.0 RC 방향 | [`docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`](./docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md) |
| 커널 증류 (30줄) | [`kernel/SUMMARY.md`](./kernel/SUMMARY.md) |
| 커널이 산출하는 것 | [`demos/01_attribution-audit/`](./demos/01_attribution-audit/) · [`demos/02_debug_slow_endpoint/`](./demos/02_debug_slow_endpoint/) |
| 같은 프롬프트, 프레임워크 off vs. on | [`demos/03_differential/`](./demos/03_differential/) |
| 설치 경로 (마켓플레이스, CLI, dev) | [`INSTALL.md`](./INSTALL.md) |
| Disconfirmation 타겟 벤치마크 | [`benchmarks/kernel_v1/`](./benchmarks/kernel_v1/) |
| Substrate bridge (mem0, memori, noop) | [`docs/SUBSTRATE_BRIDGE.md`](./docs/SUBSTRATE_BRIDGE.md) |
| 프로파일 + cognition 설정 | [`docs/SETUP.md`](./docs/SETUP.md) |
| 동기화 매트릭스, 메모리 모델, 계약 | [`docs/SYNC_AND_MEMORY.md`](./docs/SYNC_AND_MEMORY.md) |
| Harness 시스템 | [`docs/HARNESSES.md`](./docs/HARNESSES.md) |
| Hook 레퍼런스 + 거버넌스 팩 | [`docs/HOOKS.md`](./docs/HOOKS.md) |
| 스킬 + 에이전트 페르소나 + 출처 추적 | [`docs/SKILLS_AND_PERSONAS.md`](./docs/SKILLS_AND_PERSONAS.md) |
| 개인 커스터마이징 (메모리/훅/스킬) | [`docs/CUSTOMIZATION.md`](./docs/CUSTOMIZATION.md) |
| 에이전트 저장소 운영 계약 | [`AGENTS.md`](./AGENTS.md) |
| 아키텍처 심화 | [`docs/EPISTEME_ARCHITECTURE.md`](./docs/EPISTEME_ARCHITECTURE.md) |
| 인지 시스템 플레이북 | [`docs/COGNITIVE_SYSTEM_PLAYBOOK.md`](./docs/COGNITIVE_SYSTEM_PLAYBOOK.md) |

---

## 푸시-준비 체크리스트

```bash
PYTHONPATH=. pytest -q tests/test_profile_cognition.py
python3 -m py_compile src/episteme/cli.py
episteme doctor
git status && git rev-list --left-right --count @{u}...HEAD
```
