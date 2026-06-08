# Custom UI Templates

## 1. 프로젝트 개요

이 프로젝트는 **Mozart Cloud APS**의 커스텀 화면을 개발하기 위한 **풀스택 템플릿**입니다.


| 구성           | 기술 스택                            | 역할               |
| ------------ | -------------------------------- | ---------------- |
| **Frontend** | Vue 3 + Vite + Module Federation | 호스트 앱에 뷰 플러그인 제공 |
| **Backend**  | FastAPI + Trino + PostgreSQL     | 데이터 조회/처리 API 제공 |


```
┌─────────────────────────────────────────────────────┐
│  APS Host Application (Mozart Cloud)                │
│                                                     │
│  window.__POWERED_BY_APS_HOST__ = true              │
│  provide("hostData", Ref<HostData>)                 │
│  provide("hostNavigation", { openLinkNewTab })      │
│                                                     │
│  fetch("/ext/remoteEntry.js")  ← MF 진입점          │
│  import("external_app/expose")                      │
│       → viewRegistry["RtfReport"]()                 │
│             → withHostInit 래퍼                      │
│                   → inject("hostData")              │
│                   → setProjectIdResolver()          │
│                   → RtfReport.vue 렌더링             │
│                                                     │
│  ┌───────────────────────────────────────────┐      │
│  │  Remote: @vmscloud/external-app (이 앱)    │      │
│  │                                           │      │
│  │  /api/custom/backend/{projectId}/...     ─┼──────┼──→ Python 백엔드 (FastAPI)
│  │  /api/aps/backend/{projectId}/...        ─┼──────┼──→ APS C# 백엔드
│  └───────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────┘
```

---

## 2. 전체 디렉토리 구조

```
custom-ui-templates/
├── deploy-custom-ui.ps1          ← 통합 빌드/배포 스크립트
│
├── backend/                      ← FastAPI 백엔드
│   ├── Dockerfile
│   ├── pyproject.toml            ← uv 패키지 관리
│   ├── run-dev.ps1               ← 개발 실행
│   ├── run-mock.ps1              ← Mock 모드 실행
│   ├── mock_data/responses/      ← Mock JSON 파일들
│   └── app/
│       ├── main.py               ← FastAPI 앱 진입점
│       ├── adapters/
│       │   └── adapter.py        ← Query Executor HTTP 클라이언트
│       ├── api/
│       │   ├── dependencies.py   ← DI (QueryExecutorAdapter 싱글톤)
│       │   └── v1/
│       │       ├── api.py        ← ★ 라우터 통합 등록
│       │       └── endpoints/    ← ★ API 엔드포인트들
│       ├── schemas/              ← ★ Pydantic 요청/응답 모델
│       ├── services/             ← ★ Trino 비즈니스 로직 + SQL 쿼리
│       ├── repositories/         ← ★ PostgreSQL CRUD 로직
│       └── core/
│           ├── config.py         ← 환경변수 설정 (pydantic-settings)
│           ├── database.py       ← Trino 연결 + execute_query/execute_write
│           ├── mock_middleware.py ← Mock 응답 미들웨어
│           └── mock_store.py     ← Mock 데이터 스토어
│
├── frontend/                     ← Vue 3 리모트 앱
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── main.ts               ← 개발 모드 전용 진입점
│       ├── bootstrap.ts          ← Vue 앱 초기화
│       ├── expose.ts             ← ★ Module Federation 공개 API
│       ├── api/
│       │   └── client.ts         ← Axios 인스턴스 + projectId 리졸버
│       ├── composables/
│       │   └── useHostStores.ts  ← inject 기반 호스트 데이터 접근
│       ├── components/
│       │   └── DeveloperTool/    ← 개발 모드 호스트 시뮬레이터
│       ├── shims/                ← @vmscloud 내부 경로 심
│       ├── plugins/
│       │   └── i18n.ts           ← 다국어 (ko/en/zh/jp)
│       ├── router/
│       │   └── index.ts          ← ★ 개발용 라우터
│       └── views/templates/      ← ★ 비즈니스 화면들
│           ├── basic/            ← 예제 (ItemMaster, HostInfo)
│           ├── chart/            ← ECharts 예제
│           ├── grid/             ← Wijmo 그리드 예제
│           ├── dm/               ← 수요 관련
│           ├── pe/               ← 계획 재실행
│           └── sp/               ← 스케줄링/계획 (메인 도메인)
```

---

## 3. 백엔드 아키텍처

### 3-1. 기술 스택


| 기술                | 버전     | 역할                              |
| ----------------- | ------ | ------------------------------- |
| Python            | 3.12+  | 런타임                             |
| FastAPI           | 0.123+ | 웹 프레임워크                         |
| Trino             | 0.328+ | 분석 쿼리 엔진 (Iceberg + PostgreSQL) |
| pydantic-settings | 2.12+  | 환경변수 설정 관리                      |
| httpx             | 0.27+  | 비동기 HTTP 클라이언트                  |
| uv                | -      | 패키지 매니저                         |
| uvicorn           | -      | ASGI 서버 (포트 18020)              |


### 3-2. 레이어 구조

```
HTTP 요청
  ↓
endpoints/         ← 라우터 (요청 파싱, 에러 핸들링)
  ↓
services/          ← 비즈니스 로직 (Trino Iceberg 조회)
  or
repositories/      ← CRUD 로직 (PostgreSQL 직접 접근)
  ↓
core/database.py   ← Trino 연결 관리
  or
adapters/adapter.py ← Query Executor 외부 서비스 호출
```

### 3-3. 두 가지 데이터 소스

이 백엔드는 **두 가지 방식**으로 데이터에 접근합니다:

#### (1) Trino (Iceberg) — 읽기 전용 분석 쿼리

대용량 계획/실행 결과 데이터를 Iceberg 테이블에서 조회합니다.

```python
# services/load_factor.py (서비스 패턴)
class LoadFactorService:
    def __init__(self, adapter: QueryExecutorAdapter):
        self.adapter = adapter
        self.catalog = settings.TRINO_CATALOG_ICEBERG   # "iceberg"
        self.schema = settings.TRINO_SCHEMA_APS          # "mzc_aps"

    async def get_main(self, project_id, plan_ver):
        sql = Q.MAIN_SQL.format(partition_key=..., plan_ver=plan_ver)
        result = await self.adapter.execute_direct_query(
            project_id=project_id, query=sql,
            catalog=self.catalog, schema=self.schema,
        )
        return self._safe_rows(result)
```

- SQL 쿼리는 별도 `_queries.py` 파일에 상수로 분리
- `QueryExecutorAdapter`를 통해 Query Executor 서비스에 HTTP 요청
- DI: `Depends(get_load_factor_service)`

#### (2) PostgreSQL — CRUD (설정/상태 데이터)

설정 테이블, 상태 관리 등 쓰기가 필요한 데이터를 처리합니다.

```python
# repositories/freeze_plan.py (레포지토리 패턴)
class FreezePlanRepository:
    @staticmethod
    def get_frozen_status(project_id, plan_cycle_id):
        query = """
        SELECT * FROM cfg_plan_cycle_info
        WHERE project_id = %s AND plan_cycle_id = %s
        """
        return execute_query(query, (project_id, plan_cycle_id))

    @staticmethod
    def freeze_plan(project_id, plan_ver, ...):
        return execute_write(query, params)
```

- `core/database.py`의 `execute_query()` / `execute_write()` 사용
- Trino의 PostgreSQL 카탈로그를 통해 접근 (실제로는 Trino → PG 커넥터)

### 3-4. QueryExecutorAdapter

외부 **Query Executor** 서비스와 통신하는 HTTP 클라이언트입니다.

```python
# 두 가지 실행 모드:

# 1. 저장된 쿼리 실행 (query_id로 미리 등록된 SQL 실행)
result = await adapter.execute_query(
    project_id="dev", query_id="get_peg_info",
    parameters={"project_id": "EED70012"}
)

# 2. 직접 SQL 실행 (Trino에 직접 쿼리)
result = await adapter.execute_direct_query(
    project_id="dev",
    query="SELECT * FROM out_peg_info LIMIT 5",
    catalog="iceberg", schema="dev"
)
```

- `dependencies.py`에서 싱글톤으로 관리 (HTTP 커넥션 풀 재사용)
- `httpx.AsyncClient` 기반 비동기 호출

### 3-5. 라우터 등록 (api.py)

```python
# backend/app/api/v1/api.py
api_router = APIRouter()

# 도메인별 라우터 등록
api_router.include_router(health.router, prefix="/api/custom/backend", ...)
api_router.include_router(load_factor.router, prefix="/api/custom/backend/{project_id}/load-factor", ...)
# ... 기타 라우터 ...

# ⚠️ proxy.router는 반드시 마지막! (catch-all 역할)
api_router.include_router(proxy.router, prefix="/api/custom/backend/{project_id}", ...)
```

> **주의**: `proxy.router`는 `/proxy/aps` 엔드포인트로 APS C# 백엔드를 프록시합니다.
> catch-all 특성이 있으므로 항상 마지막에 등록해야 다른 라우터가 먼저 매칭됩니다.

### 3-6. 엔드포인트 패턴

모든 엔드포인트는 동일한 에러 핸들링 패턴을 따릅니다:

```python
# endpoints/load_factor.py
router = APIRouter()

def _error_response(status_code, label, exc):
    """공통 에러 응답 헬퍼"""
    detail = str(exc) if settings.DEBUG else None
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": f"{label} 중 오류가 발생했습니다.",
                 **({"detail": detail} if detail else {})},
    )

@router.get("/main")
async def get_main(
    project_id: str = Path(...),
    plan_ver: str = Query(..., alias="planVer"),
    service: LoadFactorService = Depends(get_load_factor_service),
):
    try:
        return await service.get_main(project_id, plan_ver)
    except ValueError as e:
        return _error_response(400, "조회", e)
    except Exception as e:
        return _error_response(500, "조회", e)
```

### 3-7. 환경변수 설정

`pydantic-settings` 기반으로 `.env` 파일 체인을 읽습니다:

```
.env              ← 공통 기본값
.env.development  ← 개발 환경
.env.local        ← 로컬 개인 설정 (gitignore)
OS 환경변수        ← 최우선 (Docker, CI)
```

주요 설정:


| 변수                        | 기본값            | 설명                     |
| ------------------------- | -------------- | ---------------------- |
| `TRINO_HOST`              | -              | Trino 서버 호스트           |
| `TRINO_PORT`              | 18080          | Trino 서버 포트            |
| `TRINO_CATALOG_ICEBERG`   | iceberg        | Iceberg 카탈로그명          |
| `TRINO_SCHEMA_APS`        | mzc_aps        | APS 스키마명               |
| `QUERY_EXECUTOR_BASE_URL` | -              | Query Executor 서비스 URL |
| `APS_BACKEND_BASE_URL`    | localhost:8080 | APS C# 백엔드 (프록시용)      |
| `USE_MOCK`                | false          | Mock 모드 활성화            |
| `DEBUG`                   | false          | 디버그 모드 (에러 상세 노출)      |


### 3-8. Mock 모드

`USE_MOCK=true`로 실행하면 DB 연결 없이 캡처된 JSON으로 응답합니다.

```
backend/mock_data/responses/
├── lf_oper_groups.json     ← GET:/load-factor/oper-groups
├── lf_main.json            ← POST:/load-factor/main
├── dash_dashboard.json     ← POST:/plan-dashboard/dashboard
└── ...
```

- `mock_store.py`에서 엔드포인트 경로 → JSON 파일명 매핑
- `MockMiddleware`가 요청을 가로채서 매핑된 JSON 반환
- 프론트엔드 단독 개발/테스트에 유용

---

## 4. 프론트엔드 아키텍처

### 4-1. Module Federation


| 항목     | 값                             |
| ------ | ----------------------------- |
| 리모트 이름 | `external_app`                |
| 진입 파일  | `remoteEntry.js`              |
| 노출 모듈  | `./expose` → `src/expose.ts`  |
| 공유 싱글톤 | `vue`, `pinia` (호스트와 인스턴스 공유) |


```ts
// vite.config.ts 내 Module Federation 설정
federation({
  name: "external_app",
  filename: "remoteEntry.js",
  exposes: { "./expose": "./src/expose.ts" },
  shared: {
    vue: { singleton: true, requiredVersion: "^3.4.14" },
    pinia: { singleton: true, requiredVersion: "^2.1.7" },
  },
});
```

> **왜 singleton인가?**
> Vue의 `provide/inject`가 호스트↔리모트 사이에서 동작하려면 같은 Vue 인스턴스를 써야 합니다.

### 4-2. 호스트가 제공하는 데이터

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

### 4-3. withHostInit 래퍼

```
호스트가 뷰를 로드 → withHostInit 실행 → inject("hostData") → setProjectIdResolver() → 뷰 렌더링
```

모든 뷰는 `viewRegistry`에 `withHostInit()`으로 감싸서 등록됩니다.

### 4-4. 뷰 등록 (expose.ts)

```ts
// viewRegistry: 뷰 이름 → lazy import
export const viewRegistry = {
  RtfReport: withHostInit(
    () => import("./views/templates/sp/rtf-report/RtfReport.vue"),
  ),
  PlanDashboard: withHostInit(
    () => import("./views/templates/sp/plan-dashboard/PlanDashboard.vue"),
  ),
  // ...
};

// viewMeta: 관리자 화면에서 보여줄 메뉴 이름
export const viewMeta = {
  RtfReport: { name: "RtfReport", defaultMenuName: "RTF 리포트" },
  // ...
};
```

### 4-5. 뷰 템플릿 작성 패턴 (Co-location)

```
views/templates/sp/rtf-report/
├── RtfReport.vue          ← 루트 뷰
├── RtfReportSub1.vue      ← 서브 패널
├── RtfReportSub2.vue      ← 서브 패널
└── rtfReport.ts           ← ★ Composable (API 호출, 타입, 상태)
```

### 4-6. 라이브러리


| 패키지                           | 역할                                        |
| ----------------------------- | ----------------------------------------- |
| `@vmscloud/moz-ui-components` | UI 컴포넌트 (Controller, Popup, EmptyState 등) |
| `@vmscloud/moz-wijmo-grid`    | Wijmo 기반 ExtendFlexGrid                   |
| `@vmscloud/moz-ui-chart`      | ECharts 차트 래퍼                             |
| `@tanstack/vue-query`         | 서버 상태 관리                                  |
| `gojs`                        | BomMap 다이어그램                              |
| `dayjs`                       | 날짜 처리                                     |
| `i18next-vue`                 | 다국어                                       |


### 4-7. Shim 시스템

APS 호스트 코드의 내부 경로를 리모트에서도 사용할 수 있도록 하는 호환 레이어:

```ts
// vite.config.ts resolve.alias
"@moz-shared/icons"              → src/shims/moz-shared/icons/
"@moz-shared/utils"              → src/shims/moz-shared/utils.ts
"@vmscloud/moz-wijmo-grid/utils" → src/shims/moz-wijmo-grid/utils.ts
"@vmscloud/moz-wijmo-grid/store" → src/shims/moz-wijmo-grid/store.ts
```

---

## 5. 프론트-백엔드 연동 흐름

### API 프록시 (개발 모드)

```
프론트엔드 (localhost:5300)
  /api/aps/   →  https://dev.mozart-cloud.com    (APS C# 백엔드)
  /api/       →  http://localhost:8000            (로컬 Python 백엔드)
```

### 데이터 흐름 예시 (Load Factor)

```
1. 사용자가 "조회" 버튼 클릭
2. Vue Composable → api.get("/api/custom/backend/{projectId}/load-factor/main?planVer=...")
3. Vite 프록시 → FastAPI (localhost:8000)
4. FastAPI endpoint → LoadFactorService.get_main()
5. Service → QueryExecutorAdapter.execute_direct_query()
6. Adapter → HTTP POST → Query Executor 서비스 → Trino → Iceberg
7. 결과 반환 → { success: true, count: N, data: [...] }
8. Vue → ExtendFlexGrid에 데이터 바인딩
```

---

## 6. 새 화면 추가 가이드 (풀스택)

### 네이밍 규칙

`my-feature`라는 기능을 만든다면:


| 형태         | 예시           | 용도                    |
| ---------- | ------------ | --------------------- |
| kebab-case | `my-feature` | URL, 폴더명, 태그          |
| snake_case | `my_feature` | Python 파일명, 모듈명       |
| PascalCase | `MyFeature`  | 클래스명, Vue 컴포넌트명       |
| camelCase  | `myFeature`  | Composable 파일명, JS 변수 |


### Step 1: 백엔드 — 스키마

```python
# backend/app/schemas/my_feature.py
from pydantic import BaseModel, Field

class MyFeatureRequest(BaseModel):
    planVer: str = Field(..., description="Plan version")
```

### Step 2: 백엔드 — 서비스 (Trino 조회) 또는 레포지토리 (PostgreSQL CRUD)

**Trino 조회일 때:**

```python
# backend/app/services/my_feature_queries.py  ← SQL 상수
MAIN_SQL = """SELECT * FROM table WHERE partition_key = '{partition_key}'"""

# backend/app/services/my_feature.py  ← 비즈니스 로직
class MyFeatureService:
    def __init__(self, adapter: QueryExecutorAdapter): ...
    async def get_main(self, project_id, plan_ver): ...
```

**PostgreSQL CRUD일 때:**

```python
# backend/app/repositories/my_feature.py
class MyFeatureRepository:
    @staticmethod
    def get_list(project_id, plan_ver):
        return execute_query("SELECT ...", (project_id, plan_ver))
    @staticmethod
    def create(project_id, data):
        return execute_write("INSERT ...", (...))
```

### Step 3: 백엔드 — 엔드포인트

```python
# backend/app/api/v1/endpoints/my_feature.py
router = APIRouter()

@router.get("/main")
async def get_main(
    project_id: str = Path(...),
    plan_ver: str = Query(..., alias="planVer"),
    service: MyFeatureService = Depends(get_my_feature_service),
):
    try:
        return await service.get_main(project_id, plan_ver)
    except Exception as e:
        return _error_response(500, "조회", e)
```

### Step 4: 백엔드 — 라우터 등록

```python
# backend/app/api/v1/api.py
from app.api.v1.endpoints import my_feature

api_router.include_router(
    my_feature.router,
    prefix="/api/custom/backend/{project_id}/my-feature",
    tags=["my-feature-api"],
)
# ⚠️ proxy.router보다 위에 등록!
```

### Step 5: 프론트엔드 — Composable

```ts
// frontend/src/views/templates/sp/my-feature/myFeature.ts
import { api, getProjectId } from "@/api/client";
import { ref } from "vue";

const BASE_URL = () => `/api/custom/backend/${getProjectId()}/my-feature`;

export function useMyFeature() {
  const data = ref([]);
  const loading = ref(false);

  async function loadData(planVer: string) {
    loading.value = true;
    try {
      const res = await api.get(`${BASE_URL()}/main`, { params: { planVer } });
      data.value = res?.data ?? [];
    } finally {
      loading.value = false;
    }
  }

  return { data, loading, loadData };
}
```

### Step 6: 프론트엔드 — Vue 컴포넌트

```vue
<!-- frontend/src/views/templates/sp/my-feature/MyFeature.vue -->
<template>
  <div class="my-feature-page">
    <Controller
      :navigations="['내 기능']"
      showFilterButton
      :actions="[
        {
          action: 'Search',
          click: handleSearch,
          disabled: loading || !planVer,
        },
      ]"
    >
    </Controller>
    <section class="content-section">
      <ExtendFlexGrid
        name="myFeatureMain"
        :itemsSource="data"
        height="100%"
        :isReadOnly="true"
        :loading="loading"
      />
    </section>
  </div>
</template>

<script setup lang="ts">
import { Controller } from "@vmscloud/moz-ui-components";
import { ExtendFlexGrid } from "@vmscloud/moz-wijmo-grid";
import { useHostPlanCycle } from "@/composables/useHostStores";
import { useMyFeature } from "./myFeature";

const { planVer } = useHostPlanCycle();
const { data, loading, loadData } = useMyFeature();

async function handleSearch() {
  if (planVer.value) await loadData(planVer.value);
}
</script>
```

### Step 7: 프론트엔드 — 등록

```ts
// expose.ts
MyFeature: withHostInit(() => import("./views/templates/sp/my-feature/MyFeature.vue")),
// viewMeta에도 추가
MyFeature: { name: "MyFeature", defaultMenuName: "내 기능" },

// router/index.ts (개발용)
{ path: "/my-feature", name: "MyFeature", component: () => import("...") },
```

---

## 7. 개발 워크플로우

### 실행 명령

```bash
# 백엔드
cd backend
.\run-dev.ps1                    # uvicorn 개발 서버 (포트 18020)
.\run-mock.ps1                   # Mock 모드 (DB 없이)

# 프론트엔드
cd frontend
pnpm dev                         # Vite 개발 서버 (포트 5300, HMR)
pnpm build                       # vue-tsc 타입체크 + 빌드
pnpm dev:watch                   # 빌드 + watch (정적 리모트)

# 배포
.\deploy-custom-ui.ps1 -Service all -GithubToken $env:GITHUB_TOKEN
.\deploy-custom-ui.ps1 -Service backend    # 백엔드만
.\deploy-custom-ui.ps1 -Service frontend   # 프론트엔드만
```

### 독립 실행 (호스트 없이)

`pnpm dev`로 프론트엔드를 실행하면 **DeveloperTool**이 호스트를 시뮬레이션합니다:

- 상단에 가짜 헤더와 네비게이션 표시
- 설정에서 `projectID`, `planVer` 직접 입력
- `provide("hostData", ...)`를 호스트와 동일하게 주입
- `localStorage`에 설정 저장 (키: `hostData_dev`)

---

## 8. 자주 하는 실수


| 실수                           | 해결                                                    |
| ---------------------------- | ----------------------------------------------------- |
| `inject` 실패 (undefined)      | `shared`에 `singleton: true` 빠졌는지 확인                   |
| API 호출 시 projectId 빈 값       | `withHostInit` 래퍼 빠졌거나, DeveloperTool에서 projectID 미입력 |
| shim 경로 import 에러            | `vite.config.ts`의 `resolve.alias`에 해당 경로 추가 필요        |
| proxy.router가 다른 라우터보다 먼저 매칭 | `api.py`에서 proxy를 반드시 마지막에 등록                         |
| Trino 쿼리에서 SQL injection     | `str.format()` 사용 시 사용자 입력 검증 필수                      |
| `_error_response`에서 상세 에러 노출 | `DEBUG=false`인 프로덕션에서는 자동으로 숨겨짐                       |
| Mock 모드에서 새 엔드포인트 안 됨        | `mock_store.py`의 `_ROUTE_MAP`에 매핑 추가 필요               |


---

## 9. 아키텍처 핵심 요약

1. **Module Federation** = 호스트와 리모트를 런타임에 연결
2. **provide/inject** = 호스트→리모트 데이터 전달의 핵심
3. **withHostInit** = 모든 뷰의 진입점을 통일하는 래퍼
4. **QueryExecutorAdapter** = Trino 쿼리를 Query Executor 서비스를 통해 실행
5. **레포지토리 패턴** = PostgreSQL CRUD는 `execute_query`/`execute_write` 직접 사용
6. **서비스 패턴** = Trino 조회는 Adapter + DI로 주입
7. **SQL 분리** = Trino 쿼리는 `_queries.py` 파일에 상수로 관리
8. **Mock 모드** = DB 없이 JSON 파일로 프론트엔드 개발 가능

