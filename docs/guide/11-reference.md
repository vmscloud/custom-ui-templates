# 11. 레퍼런스

자주 찾게 되는 경로·훅·환경 변수 한 장 요약.

## 디렉토리 빠른 참조

```
frontend/src/
├─ api/client.ts              ← axios + getProjectId()
├─ composables/
│   ├─ useHostStores.ts       ← host 주입값 접근
│   └─ useQtyUomQuery.ts      ← 수량 단위 선호값
├─ shims/moz-shared/
│   ├─ icons/                 ← SVG 아이콘 컴포넌트
│   │   └─ index.ts           ← 공개 export
│   ├─ utils/
│   └─ types/
├─ plugins/i18n.ts            ← i18next 세팅
├─ lang/{ko,en,jp,zh}.json    ← 번역 리소스
├─ expose.ts                  ← Module Federation viewRegistry
└─ router/index.ts            ← dev 라우트

backend/app/
├─ main.py                    ← FastAPI 앱
├─ api/
│   ├─ dependencies.py        ← DI (get_query_executor_adapter)
│   └─ v1/
│       ├─ api.py             ← api_router 통합
│       └─ endpoints/
│           ├─ health.py
│           ├─ aps_proxy.py
│           └─ <도메인>.py
├─ schemas/<도메인>.py        ← Pydantic 모델
├─ services/<도메인>.py       ← 비즈니스 로직
├─ adapters/adapter.py        ← Trino query-executor 래퍼
└─ core/
    ├─ config.py              ← settings
    ├─ database.py            ← execute_query (PG)
    └─ mock_middleware.py     ← mock 응답 미들웨어
```

## 공용 훅

### `useHostStores.ts`

| 함수 | 반환 | 설명 |
|------|------|------|
| `useHostData()` | `Ref<HostData>` | 전체 hostData 원본 ref |
| `useHostPlanCycle()` | `{ planVer, fromDate, toDate }` | computed refs |
| `useHostProjectInfo()` | `ComputedRef<any>` | projectInfo 전체 |
| `useHostUser()` | `{ userInfo, isAdmin }` | 사용자 정보 |
| `useHostNavigation()` | `{ openLinkNewTab }` | 새 탭 열기 헬퍼 |
| `isRunningInHost()` | `boolean` | `window.__POWERED_BY_APS_HOST__` 체크 |

### `useQtyUomQuery.ts`

```ts
useQtyUomQuery(
  source: ("DEFAULT" | "CONVERSION")[],
  defaultValue: "DEFAULT" | "CONVERSION",
  option?: { menuID?: string }
): {
  uomType: Ref<"DEFAULT" | "CONVERSION">,
  qtyUOMSource: Ref<{ label, value, displayValue }[]>
}
```

- localStorage 키: `moz.customUi.qtyUOM:<menuID>`
- URL 쿼리: `?qtyUOM=DEFAULT|CONVERSION`

## API 클라이언트

```ts
import { api, getProjectId } from "@/api/client";

api.get<Res>(url);
api.post<Res>(url, body);
api.put<Res>(url, body);
api.delete<Res>(url);
```

URL 규칙:

- `/api/custom/backend/${getProjectId()}/<domain>/<action>` → 로컬 FastAPI
- `/api/aps/backend/${getProjectId()}/<APS route>` → APS C# 호스트 (세션 필요)

## 아이콘 (shims)

`@moz-shared/icons` 로 import. export 목록은 `frontend/src/shims/moz-shared/icons/index.ts` 참조.

현재 포함된 것 (예시):
- `IconCircleCheck`, `IconCircleX`, `IconNotice`, `IconToastWarning`
- `IconCollapseArrow`, `IconExpandArrow`, `IconClose`, `IconCopy`, `IconSearch`
- `IconLineEdit`, `IconReExecute`, `IconDataCheck`, `IconResultCheck`

새 아이콘이 필요하면 `shims/moz-shared/icons/<Name>.vue` 를 추가하고 index에 export.

### 공용 아이콘 Props 관례

```ts
interface Props {
  size?: "10" | "12" | "14" | "16" | "18" | "20" | "22" | "30";
  color?: string;
  disabled?: boolean;
}
```

## 주요 UI 컴포넌트 (`@vmscloud/moz-ui-components`)

- `Controller` — 화면 상단 필터 바
- `Button`
- `Input`, `NumberInput`, `DateInput`, `TimePicker`
- `Select`, `MultiSelect`, `Radio`, `Toggle`
- `Popup` — 모달 팝업
- `SplitPane`, `Pane` — 분할 레이아웃
- `TextArea`
- `EmptyState`

## 그리드 (`@vmscloud/moz-wijmo-grid`)

- `ExtendFlexGrid`, `ExtendPivotGrid` — 기본 확장 그리드
- `WjFlexGridColumn` (from `.../wijmo.vue2.grid`) — 컬럼 정의
- `CollectionView`, `DataType`, `ShowTotals` — Wijmo 하위 API

## 백엔드 환경 변수 (core/config.py)

자주 쓰는 키:

| 키 | 용도 |
|----|------|
| `DEBUG` | 에러 detail 응답 포함 여부 |
| `TRINO_CATALOG_ICEBERG` | Trino 카탈로그 |
| `TRINO_SCHEMA_APS` | Trino 스키마 |
| `APS_BACKEND_BASE_URL` | APS proxy 대상 |
| `QUERY_TIMEOUT_SECONDS` | httpx 타임아웃 |
| `PG_*` | PostgreSQL 접속 정보 |
| `MOCK_MODE` | mock 응답 미들웨어 활성화 |

실제 필드명과 기본값은 `backend/app/core/config.py` 의 `Settings` 클래스 참조.

## 프론트 환경 변수

| 키 | 기본값 | 용도 |
|----|--------|------|
| `VITE_DEV_PORT` | `5300` | dev 서버 포트 |
| `VITE_API_TARGET` | `http://localhost:8000` | `/api` 프록시 타깃 |

## Module Federation

- `frontend/vite.config.ts` 의 `@module-federation/vite` 설정
  - `filename`: `remoteEntry.js`
  - `exposes`: `./expose -> ./src/expose.ts`
  - `shared`: `vue` / `pinia` singleton
- Host 가 로드하는 경로: `${baseUrl}/ext/remoteEntry.js`

## 경로 별칭 (vite alias)

| 별칭 | 실제 경로 |
|------|-----------|
| `@` | `frontend/src` |
| `@moz-shared/icons` | `frontend/src/shims/moz-shared/icons` |
| `@moz-shared/utils` | `frontend/src/shims/moz-shared/utils` |
| `@moz-shared/types` | `frontend/src/shims/moz-shared/types` |
| `@vmscloud/moz-wijmo-grid/utils` | `frontend/src/shims/moz-wijmo-grid/utils` |
| `@vmscloud/moz-wijmo-grid/store` | `frontend/src/shims/moz-wijmo-grid/store` |

## 백엔드 주요 API 엔드포인트 (예시)

> 실제 경로는 `backend/app/api/v1/endpoints/` 의 각 파일 참조. 아래는 대표 예.

| Method | Path | 내용 |
|--------|------|------|
| GET | `/api/v1/health` | 헬스 체크 |
| GET | `/api/custom/backend/{pid}/re-execute-plan/plan-cycle-info` | plan cycle 정보 |
| GET | `/api/custom/backend/{pid}/re-execute-plan/demand-vers` | demand_ver 목록 |
| POST | `/api/custom/backend/{pid}/re-execute-plan/main` | 메인 집계 |
| ... | 각 도메인별 | ... |

## i18n 키 접두어

| 접두어 | 예 |
|--------|----|
| `text-` | `text-qty_uom`, `text-menu-production` |
| `desc-` | `desc-plancycle_setting` |
| `msg-` | `msg-toast-get_error` |
| `MOZ-` | `MOZ-DATA_EMPTY` |

## 컨벤션 요약

- 파일명: Vue 화면은 PascalCase (`MyPage.vue`), composable 은 camelCase (`myPage.ts`).
- 폴더명: kebab-case (`work-order/`).
- 라우트 path: kebab-case (`/ext/work-order`).
- i18n 키: snake_case + prefix (`text-work_order_id`).
- API path: kebab-case (`/re-execute-plan/main`).
- Pydantic 필드: camelCase (프론트 body 와 맞춤).
- Python 함수/변수: snake_case.

## 커밋 메시지 스타일

- `feat: Work Order 화면 및 /work-order/list 엔드포인트 추가`
- `fix: <도메인> — 구체적인 이슈 요약`
- `refactor: ...`, `docs: ...` 같은 prefix 사용.

---

이 가이드 세트를 끝까지 따라갔다면 새 페이지를 구성하고, 데이터 소스를 고르고, UI 패턴을 적용하고, 문제가 생겼을 때 위치를 찾아갈 수 있을 것입니다. 문서에서 누락되었거나 모호한 부분이 있다면 실제 코드(`re_execute_plan.py`, `reExecutePlan.ts`, `useQtyUomQuery.ts` 등)를 실전 예시로 참고하세요.
