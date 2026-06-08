# 03. 아키텍처

## 전체 흐름

```
┌────────────────────── 브라우저 ──────────────────────┐
│                                                       │
│  ┌── APS Host 앱 ─────────────────────────────────┐  │
│  │   window.__POWERED_BY_APS_HOST__ = true         │  │
│  │   provide("hostData", Ref<HostData>)            │  │
│  │                                                  │  │
│  │   ▼ import("external_app/expose")               │  │
│  │   viewRegistry["MyPage"]() ──► Vue component    │  │
│  │                                                  │  │
│  │   그 Vue 안에서 HTTP 호출:                       │  │
│  │     /api/aps/backend/{pid}/...   ──► APS C# BE   │  │
│  │     /api/custom/backend/{pid}/...─► FastAPI      │  │
│  └──────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────┘
                          │
          ┌───────────────┴────────────────┐
          ▼                                ▼
┌─────────────────────┐           ┌──────────────────────┐
│ FastAPI (backend/)  │           │  APS C# Host (원본)  │
│  port 8000          │           │  (세션 쿠키 필요)    │
│                     │           └──────────────────────┘
│  커스텀 도메인      │
│   /re-execute-plan  │
│   /plan-dashboard   │
│   ...               │
│                     │
│  ┌─ execute_query ─ PostgreSQL (cfg_*, mst_*)
│  └─ QueryExecutorAdapter ─ Trino/Iceberg (rpt_*, odv_*)
└─────────────────────┘
```

## Module Federation 한 눈에

- 프론트 빌드 시 `frontend/vite.config.ts` 의 `@module-federation/vite` 플러그인이 `**remoteEntry.js**` 를 만든다.
- 공개 모듈 = `src/expose.ts` 하나. 내부의 `viewRegistry: Record<string, () => Promise<VueComponent>>` 가 핵심 자료구조.
- Host 앱은 `import('external_app/expose')` 로 viewRegistry를 받고, 원하는 키를 호출해 비동기로 Vue 컴포넌트를 얻음.
- **dev 단독 실행** 시에는 Host 가 없으므로 `src/router/index.ts` + `src/main.ts` 가 직접 라우팅/마운트.

### Host Data 주입

Host 는 리모트 앱을 마운트할 때 `provide("hostData", ref)` 로 다음 정보를 내려준다.

```ts
hostData.value = {
  planCycle: { planVer, fromDate, toDate, demandVer? },
  projectInfo: { projectID, tenantID, userInfo },
  menu: { ... },
  dateFormat: "YYYY-MM-DD",
  factoryStartTime: "06:00",
}
```

이 저장소에서는 `composables/useHostStores.ts` 를 통해 접근합니다.

```ts
const hostData = useHostData();               // 전체 ref
const { planVer } = useHostPlanCycle();       // { planVer, fromDate, toDate }
const { userInfo, isAdmin } = useHostUser();
```

## 두 종류의 백엔드

이 저장소에서 "서버" 라고 하면 FastAPI 를 말합니다. 하지만 프론트가 호출하는 목적지는 두 곳.


| 경로                              | 대상                  | 인증               | 쓰는 경우                                                            |
| ------------------------------- | ------------------- | ---------------- | ---------------------------------------------------------------- |
| `/api/custom/backend/{pid}/...` | **FastAPI** (이 저장소) | 프로젝트 토큰          | 기본값. 신규 화면의 데이터 조회·집계·편집                                         |
| `/api/aps/backend/{pid}/...`    | **APS C# 호스트**      | fusionauth 세션 쿠키 | APS 표준 API (`PlmScenarioMaster`, `OdlReport`, `ComUserLayout` 등) |


**규칙**: 우리가 직접 제어할 수 있는 로직은 **모두 FastAPI 쪽**에 개발해야 합니다. 세션 기반 표준 기능만 `/api/aps/` 를 씁니다. 이렇게 해야 Mock · Dev 단독 실행에서도 같은 코드를 재현할 수 있습니다.

## 데이터 저장소 두 가지

FastAPI 안에서도 두 DB를 함께 다룹니다.

### PostgreSQL — 설정/마스터

- 접근: `backend/app/core/database.py` 의 `execute_query(sql, params?) -> list[dict]`
- 테이블 예: `cfg_plan_config`, `cfg_plan_cycle_info`, `cfg_demand_ver`, `cfg_oper_group_master` 등
- 크기가 작고 자주 조회/편집되는 config 성 데이터.

```python
from app.core.database import execute_query
rows = execute_query(
    f"SELECT plan_cycle_id FROM cfg_plan_config WHERE project_id='{pid}' LIMIT 1"
)
```

### Trino / Iceberg — 대용량 fact

- 접근: `backend/app/adapters/adapter.py` 의 `QueryExecutorAdapter.execute_direct_query(...)`
- 테이블 예: `rpt_oper_group_plan`, `rpt_buffer_plan`, `odv_demand` 등 시계열 fact.
- 서비스 안에 비동기 헬퍼를 두고 씁니다:

```python
async def _trino(self, project_id, sql):
    return await self.adapter.execute_direct_query(
        project_id=project_id, query=sql,
        catalog=self.catalog, schema=self.schema,
    )
```

### 페이지네이션 주의

Trino 응답은 **페이지당 최대 50,000 row**. 집계용 전량 조회라면 `has_next` 를 따라가며 모든 페이지를 누적하는 헬퍼를 사용해야 합니다 (예제는 [05-backend-guide](./05-backend-guide.md#page-순회-헬퍼)).

## 요청 시퀀스 예

### 새 페이지 `MyPage` 의 그리드 로드

```
[브라우저]                POST /api/custom/backend/<pid>/my-page/list
                             body: { planVer, filters }
                              │
       ┌──────────────────────┴──────────────────────┐
       ▼                                             │
[FastAPI]  api/v1/endpoints/my_page.py               │
              ▼                                      │
[service]  services/my_page.py : MyPageService.list() │
              │                                      │
              ├── execute_query(...)     ─► PG       │
              └── adapter.execute_direct_query ─► Trino
              ▼
[response] { "success": true, "data": [ ... ] }
       ▲
[브라우저]                 ◄───────────────────────────
```

## 정리

- **프론트 리모트**는 host 로 로드되거나 dev 단독으로 실행된다. 두 상황 모두 `src/composables/useHostStores` 로 주입값을 추상화해 쓴다.
- **서버**는 FastAPI 단일. 그 안에서 PG(execute_query) / Trino(adapter) 를 골라 쓴다.
- **APS 표준 API** 는 필요할 때만 `/api/aps/` 로 호출. 세션이 전제라 dev 단독에서는 401 이 나는 걸 감안해 설계.

다음: [04-frontend-guide](./04-frontend-guide.md) 에서 프론트 폴더 관례와 공용 훅을 다룹니다.