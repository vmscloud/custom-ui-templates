# External App 패키지 강의 자료

## 1. 프로젝트 개요

이 프로젝트는 **Module Federation 기반 마이크로프론트엔드 리모트 앱**입니다.

- **패키지명**: `@vmscloud/external-app` (private, npm에 배포하지 않음)
- **역할**: APS 호스트 애플리케이션에 "커스텀 화면(뷰 템플릿)"을 플러그인 형태로 제공
- **빌드 도구**: Vite 6 + `@module-federation/vite`
- **패키지 매니저**: pnpm

---

## 2. 호스트-리모트 관계

### 전체 구조

```
┌─────────────────────────────────────────────────┐
│  APS Host Application (Mozart Cloud)            │
│                                                 │
│  1. window.__POWERED_BY_APS_HOST__ = true       │
│  2. provide("hostData", Ref<HostData>)          │
│  3. provide("hostNavigation", { openLinkNewTab })│
│                                                 │
│  4. fetch("/ext/remoteEntry.js")  ← MF 진입점   │
│  5. import("external_app/expose")               │
│       → viewRegistry["RtfReport"]()             │
│             → withHostInit 래퍼                  │
│                   → inject("hostData")          │
│                   → setProjectIdResolver()      │
│                   → RtfReport.vue 렌더링         │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │  Remote: @vmscloud/external-app (이 앱)  │    │
│  │                                         │    │
│  │  /api/custom/backend/{projectId}/...    │────┼──→ Python 백엔드
│  │  /api/aps/backend/{projectId}/...       │────┼──→ APS C# 백엔드
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

### 핵심 개념: Module Federation

| 항목 | 값 |
|------|-----|
| 리모트 이름 | `external_app` |
| 진입 파일 | `remoteEntry.js` |
| 노출 모듈 | `./expose` → `src/expose.ts` |
| 공유 싱글톤 | `vue`, `pinia` (호스트와 인스턴스 공유) |

```ts
// vite.config.ts 내 Module Federation 설정
federation({
  name: "external_app",
  filename: "remoteEntry.js",
  exposes: {
    "./expose": "./src/expose.ts",
  },
  shared: {
    vue: { singleton: true, requiredVersion: "^3.4.14" },
    pinia: { singleton: true, requiredVersion: "^2.1.7" },
  },
})
```

> **왜 singleton인가?**
> Vue의 `provide/inject`가 호스트↔리모트 사이에서 동작하려면 같은 Vue 인스턴스를 써야 합니다.
> `singleton: true`가 없으면 리모트가 자체 Vue를 번들링해서 `inject`가 실패합니다.

### 호스트가 제공하는 데이터 (provide)

```ts
interface HostData {
  projectInfo: {
    currentProjectID: string;
    currentProject: any;
    userInfo: any;
    isAdmin: boolean;
  };
  planCycle: {
    planVer: string;
    fromDate: string;
    toDate: string;
  };
  menu: {
    items: any[];
    currentMenuId: string;
    currentMenu: any;
  };
  dateFormat?: string;
}
```

리모트의 모든 화면은 이 `hostData`를 `inject`해서 프로젝트 ID, 계획 버전, 사용자 정보 등을 얻습니다.

### withHostInit 래퍼

```
호스트가 뷰를 로드 → withHostInit 래퍼 실행 → inject("hostData") → API에 projectId 세팅 → 실제 뷰 렌더링
```

모든 뷰는 `viewRegistry`에 등록될 때 `withHostInit()`으로 감싸집니다. 이 래퍼가:
1. `inject`로 호스트 데이터를 받고
2. `setProjectIdResolver()`로 API 호출에 projectId를 주입하고
3. 실제 뷰 컴포넌트를 렌더링합니다

---

## 3. 리모트가 노출하는 것 (expose.ts)

```ts
// viewRegistry: 뷰 이름 → lazy import 매핑
const viewRegistry = {
  RtfReport: withHostInit(() => import("./views/templates/sp/rtf-report/RtfReport.vue")),
  PlanDashboard: withHostInit(() => import("./views/templates/sp/plan-dashboard/PlanDashboard.vue")),
  // ...
};

// viewMeta: 호스트 관리자 화면에서 보여줄 메뉴 이름
const viewMeta = {
  RtfReport: { displayName: "RTF 리포트" },
  // ...
};

// 유틸 함수
export { viewRegistry, viewMeta, getView, getAvailableViews, getViewMeta };
```

**새 화면을 추가하려면:**
1. `src/views/templates/` 아래에 뷰 폴더 생성
2. `expose.ts`의 `viewRegistry`와 `viewMeta`에 등록
3. 끝 — 호스트가 자동으로 인식

---

## 4. 디렉토리 구조

```
src/
├── main.ts                 ← 개발 모드 전용 진입점
├── bootstrap.ts            ← Vue 앱 초기화 (ECharts, Pinia, Router, i18n)
├── expose.ts               ← ★ Module Federation 공개 API
│
├── api/
│   └── client.ts           ← Axios 인스턴스 + projectId 리졸버
│
├── composables/
│   └── useHostStores.ts    ← inject 기반 호스트 데이터 접근
│
├── components/
│   └── DeveloperTool/      ← 개발 모드 전용 셸 (호스트 시뮬레이션)
│
├── shims/                  ← ★ @vmscloud 내부 경로 심 (아래 설명)
│
├── plugins/
│   └── i18n.ts             ← 다국어 설정 (ko/en/zh/jp)
│
├── views/
│   └── templates/          ← ★ 실제 비즈니스 화면들
│       ├── basic/          ← 예제 (ItemMaster, HostInfo)
│       ├── chart/          ← ECharts 예제
│       ├── grid/           ← Wijmo 그리드 예제
│       ├── dm/             ← 수요 배분
│       ├── pe/             ← 재실행 계획
│       └── sp/             ← 스케줄링/계획 (메인 도메인)
│
├── types/
│   └── host.d.ts           ← HostData 타입 정의
│
└── lang/
    ├── ko.json             ← 한국어
    ├── en.json             ← 영어
    ├── zh.json             ← 중국어
    └── jp.json             ← 일본어
```

---

## 5. 뷰 템플릿 작성 패턴

모든 뷰는 **co-location 패턴**을 따릅니다:

```
views/templates/sp/rtf-report/
├── RtfReport.vue           ← 루트 뷰 (DeveloperTool 래퍼 사용)
├── RtfReportSub1.vue       ← 상단 패널 (메인 그리드)
├── RtfReportSub2.vue       ← 하단 패널 (상세 그리드)
├── RtfReportDetail.vue     ← 팝업/드릴다운
└── rtfReport.ts            ← ★ 모든 composable, 쿼리, 타입 정의
```

### 데이터 페칭: TanStack Vue Query

```ts
// rtfReport.ts 예시
export function useRtfReportQuery(params: Ref<Params>) {
  return useQuery({
    queryKey: ['rtfReport', params],
    queryFn: () => api.get(`/custom/backend/${getProjectId()}/rtfReport`, { params: params.value }),
    enabled: false,        // 수동 트리거
    staleTime: Infinity,   // 자동 리페치 안 함
  });
}
```

> **왜 `enabled: false`인가?**
> 사용자가 조회 버튼을 누를 때만 데이터를 가져오는 업무용 화면이기 때문입니다.

---

## 6. 라이브러리 (내부 패키지) 사용법

### @vmscloud 패키지 3종

| 패키지 | 역할 | 사용 예시 |
|--------|------|-----------|
| `@vmscloud/moz-ui-components` | UI 컴포넌트 (Button, Popup, TreeSelect 등) | `import { Popup } from "@vmscloud/moz-ui-components"` |
| `@vmscloud/moz-wijmo-grid` | Wijmo 기반 데이터 그리드 | `import { ExtendFlexGrid } from "@vmscloud/moz-wijmo-grid"` |
| `@vmscloud/moz-ui-chart` | ECharts 차트 래퍼 | `import { ... } from "@vmscloud/moz-ui-chart/echarts/core"` |

### Shim 시스템 (중요!)

APS 호스트 코드에서 사용하는 내부 경로(`@moz-shared/utils`, `@vmscloud/moz-wijmo-grid/utils` 등)는 실제 패키지의 `exports`에 없는 경로입니다. 이 프로젝트에서 동일한 import 경로를 쓸 수 있도록 **shim(대체 구현)**을 만들어 놓았습니다.

```ts
// vite.config.ts의 resolve.alias
"@moz-shared/icons"                    → src/shims/moz-shared/icons/
"@moz-shared/utils"                    → src/shims/moz-shared/utils.ts
"@vmscloud/moz-wijmo-grid/utils"       → src/shims/moz-wijmo-grid/utils.ts
"@vmscloud/moz-wijmo-grid/store"       → src/shims/moz-wijmo-grid/store.ts
```

> **실무 팁**: APS 본체에서 뷰를 가져올 때 import 경로가 `@moz-shared/...`면 shim이 필요한지 확인하세요.

### 외부 주요 라이브러리

| 라이브러리 | 역할 |
|-----------|------|
| `@tanstack/vue-query` | 서버 상태 관리 (데이터 페칭/캐싱) |
| `gojs` | BomMap 다이어그램 렌더링 |
| `dayjs` | 날짜 처리 |
| `i18next` + `i18next-vue` | 다국어 |
| `es-toolkit` | 유틸리티 (lodash 대체) |

---

## 7. 개발 워크플로우

### 스크립트

```bash
pnpm dev          # 개발 서버 (포트 5300, HMR)
pnpm build        # vue-tsc 타입체크 후 빌드
pnpm dev:watch    # 빌드 + watch 모드 (정적 리모트로 서빙할 때)
pnpm preview      # 빌드 결과물 서빙 (포트 5300)
```

### 독립 실행 (호스트 없이)

`pnpm dev`로 실행하면 **DeveloperTool**이 호스트를 시뮬레이션합니다:

- 상단에 가짜 헤더와 네비게이션 표시
- 설정 다이얼로그에서 `projectID`, `planVer` 등 직접 입력
- `provide("hostData", ...)`를 호스트와 동일하게 주입
- `localStorage`에 설정 저장 (키: `hostData_dev`)

> **이것이 의미하는 것**: 호스트 없이도 모든 화면을 개발/테스트할 수 있습니다.

### API 프록시

```
/api/aps/   →  https://dev.mozart-cloud.com    (APS C# 백엔드)
/api/       →  http://localhost:8000            (로컬 Python 백엔드)
```

---

## 8. 새 화면 추가 가이드 (Step by Step)

### 1단계: 폴더 생성

```
src/views/templates/sp/my-new-view/
├── MyNewView.vue
├── MyNewViewSub1.vue     (필요시)
└── myNewView.ts          (composable, 타입, 쿼리)
```

### 2단계: 루트 뷰 작성

```vue
<template>
  <DeveloperTool>
    <div class="my-new-view">
      <!-- 화면 내용 -->
    </div>
  </DeveloperTool>
</template>

<script setup lang="ts">
import { useTranslation } from "i18next-vue";
import DeveloperTool from "@/components/DeveloperTool/DeveloperTool.vue";

const { t } = useTranslation();
</script>
```

### 3단계: expose.ts에 등록

```ts
// viewRegistry에 추가
MyNewView: withHostInit(() => import("./views/templates/sp/my-new-view/MyNewView.vue")),

// viewMeta에 추가
MyNewView: { displayName: "내 새 화면" },
```

### 4단계: 라우터 등록 (개발용)

`src/router/index.ts`에 라우트 추가 (독립 실행 시 접근용)

### 5단계: 다국어 키 추가

`src/lang/ko.json`, `en.json` 등에 필요한 텍스트 키 추가

---

## 9. 강의 시 주의사항 / 팁

### 자주 하는 실수

| 실수 | 해결 |
|------|------|
| `inject` 실패 (undefined) | `shared`에 `singleton: true` 빠졌는지 확인 |
| API 호출 시 projectId가 빈 값 | `withHostInit` 래퍼가 빠졌거나, DeveloperTool 설정에서 projectID 미입력 |
| shim 경로 import 에러 | `vite.config.ts`의 `resolve.alias`에 해당 경로 추가 필요 |
| 빌드 시 타입 에러 | `vue-tsc --noEmit`으로 먼저 확인, 타입 캐스팅(`as any`)은 최후 수단 |
| 호스트에서 스타일 깨짐 | `cssCodeSplit: true` 확인, 전역 스타일 오염 주의 |

### 아키텍처 핵심 요약

1. **Module Federation** = 호스트와 리모트를 런타임에 연결하는 기술
2. **provide/inject** = 호스트→리모트 데이터 전달의 핵심 메커니즘
3. **withHostInit** = 모든 뷰의 진입점을 통일하는 래퍼
4. **shim** = APS 내부 경로를 리모트에서도 쓸 수 있게 하는 호환 레이어
5. **TanStack Query** = 서버 상태 관리 (수동 트리거, 캐싱)
6. **DeveloperTool** = 호스트 없이 독립 개발 가능하게 하는 시뮬레이터

### 강의 순서 추천

1. Module Federation이 뭔지 (호스트/리모트 개념)
2. 이 프로젝트의 역할 (APS 호스트의 커스텀 뷰 플러그인)
3. `expose.ts` → `withHostInit` → `hostData` 흐름
4. 실제 화면 하나 같이 만들어보기 (basic 폴더의 예제 활용)
5. API 연동 (`client.ts`, TanStack Query)
6. 빌드 & 배포 (`pnpm build` → `remoteEntry.js` 생성 → 호스트가 로드)
