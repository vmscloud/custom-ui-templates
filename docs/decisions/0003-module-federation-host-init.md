# ADR-0003: Module Federation 노출 + `withHostInit` 래퍼로 Host 초기화 주입

- **상태**: Accepted
- **결정일**: 2026-02-25 (소급 작성 2026-05-20)
- **관련**: `docs/history/2026-02-25-host-projectid-resolver.md`,
  `docs/history/2026-02-13-package-migration-api-client.md`, `docs/guide/03-architecture.md`
- **코드**: `frontend/src/expose.ts`, `frontend/src/api/client.ts`,
  `frontend/src/composables/useHostStores.ts`, `frontend/src/plugins/i18n.ts`

## Context

이 프론트엔드는 단독 앱이 아니라 APS Host에 **Module Federation 리모트**로 얹힌다. Host는
`remoteEntry.js`를 받아 `viewRegistry["<View>"]()`로 컴포넌트를 동적 import 한다. 이 로딩 경로는
dev 단독 실행 경로와 달라서 두 가지가 깨졌다.

1. **projectId resolver 미설정** — dev에서는 `DeveloperTool.vue`(또는 `App.vue`)가
   `setProjectIdResolver`를 호출한다. 그러나 Host가 컴포넌트를 직접 import 하면 이 래퍼들을 거치지 않아
   resolver가 비어, API 호출 시 `[api] projectId resolver가 설정되지 않았습니다` 경고와 함께 조회가 실패했다.
2. **i18n 번역 공백** — Host 로딩 경로에서는 `bootstrap.ts`가 실행되지 않아 리모트 i18next 인스턴스에
   번역 번들이 비어 있었다.

두 문제 모두 "각 뷰가 마운트되기 직전에 Host 데이터를 받아 초기화한다"는 단일 지점이 없어서 발생했다.

## Decision

`expose.ts`에서 **모든 뷰를 `withHostInit()` 고차 함수로 래핑**해, 마운트 시점에 Host 초기화를 주입한다.

- 래퍼는 `setup()`에서 `inject(HOST_DATA_KEY)`로 Host의 `hostData`를 받아:
  - `setProjectIdResolver(() => hostData.value?.projectInfo?.currentProjectID)` 호출,
  - `ensureRemoteI18n(hostData)`로 `SamLanguage/<lang>` API를 불러 리모트 i18next에 번들 주입.
- 노출은 **static export가 아니라 동적 import 기반 `viewRegistry`** 만 제공한다.
- `setup()`은 **반드시 동기**로 유지하고, 번역 로드는 **fire-and-forget**(`void ensureRemoteI18n(...)`)으로 처리한다.

## Alternatives

- **static export로 컴포넌트 노출** — 기각. `expose.ts` 헤더 주석대로, static export는 모든 컴포넌트를
  한꺼번에 로드한다. 필요한 뷰만 받는 동적 import가 번들/로딩 측면에서 유리하다.
- **각 뷰 컴포넌트 내부에서 개별적으로 resolver/i18n 초기화** — 기각. 뷰가 11개+이고 계속 늘어나므로
  초기화 코드가 중복·누락되기 쉽다. `withHostInit` 한 곳에 모으면 신규 뷰는 래핑만으로 자동 적용된다.
- **`async setup()`으로 번역 로드 완료까지 대기** — 기각. Host가 `<Suspense>` 경계를 제공하지 않으면
  async setup은 마운트 자체를 막아 **화면이 비어버린다**. 그래서 동기 setup + fire-and-forget으로 두고,
  `addResourceBundle` 후 `languageChanged` 이벤트로 i18next-vue가 라벨을 reactive하게 갱신하게 했다.
- **Host에서 props로 projectId 전달** — 기각 *(재구성)*. resolver 패턴은 컴포넌트가 호출 시점에
  최신 projectId를 lazy하게 얻게 해, planVer/projectId가 `""`→실제값으로 늦게 채워지는 타이밍 문제
  (`docs/guide/README.md` 원칙 1)에 강하다.

## Consequences

**긍정**
- Host/dev 두 로딩 경로의 초기화 차이가 `withHostInit` 한 곳으로 흡수된다. 신규 뷰는
  `viewRegistry`에 `withHostInit(() => import(...))` 한 줄로 동일 초기화를 자동 상속한다.
- 동기 setup 유지로 Host의 Suspense 지원 여부와 무관하게 빈 화면 없이 마운트된다.

**부정 / 부채**
- **암묵적 결합**: 뷰가 정상 동작하려면 `viewRegistry` 등록 시 반드시 `withHostInit`으로 감싸야 한다.
  맨 import를 직접 등록하면 resolver/i18n이 조용히 누락된다 — 컴파일 타임에 강제되지 않는 규칙이다.
- i18n이 fire-and-forget이라, 초기 렌더 순간에는 키 또는 이전 언어가 잠깐 보일 수 있다
  (`languageChanged` 이벤트로 곧 교체됨).
- dev 단독 실행에서는 `SamLanguage` 호출이 401로 실패하고 정적 JSON(`plugins/i18n.ts`) fallback을 쓴다 —
  의도된 동작이지만, Host/dev 간 번역 소스가 달라 표시가 미세하게 다를 수 있다.
- `hostData`에서 `projectInfo.currentProjectID` 등 **Host 데이터 형태에 강하게 의존**한다.
  Host 측 계약이 바뀌면 옵셔널 체이닝으로 조용히 빈 값이 되어 디버깅이 어렵다.
