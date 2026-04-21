# 01. 개요 — 이 저장소로 무엇을 만드는가

## 한 줄 요약

**"Mozart Cloud APS 호스트 위에 얹히는 커스텀 화면(Vue 리모트 앱) + 그 화면을 위한 FastAPI 백엔드"** 를 함께 개발하는 풀스택 템플릿.

## 무엇을 만들 수 있나

1. **신규 분석/조회 화면**: Trino/Iceberg 에 쌓인 대용량 시계열(`rpt_*`, `odv_*` 등)을 피벗·필터·그리드 형태로 보여주는 페이지.
2. **프로젝트 전용 리포트**: 특정 고객사 전용 집계 로직이나 파생 컬럼을 서버에서 계산해 내려주는 화면.
3. **입력/편집 화면**: FastAPI 백엔드에서 PostgreSQL config 테이블(예: `cfg_*`)을 읽고 쓰는 화면.
4. **다른 APS 화면과 통합된 위젯**: Dashboard에 drop-in 되는 위젯 (`WidgetPop.vue` 류).

## 실행 환경 개념도

```
┌────────────── 브라우저 (사용자) ──────────────┐
│                                                │
│  APS Host (Mozart Cloud)                       │
│   window.__POWERED_BY_APS_HOST__ = true        │
│   provide("hostData", Ref<HostData>)           │
│   provide("hostNavigation", { ... })           │
│                                                │
│   ┌─ import("external_app/expose")  ──────┐    │
│   │   viewRegistry["MyPage"]() ──► Vue    │    │
│   │                                        │   │
│   │   이 Vue 컴포넌트 안에서:              │   │
│   │     api.get('/api/custom/backend/...')─┼───┼─► FastAPI (backend/)
│   │     api.post('/api/aps/backend/...')   ┼───┼─► APS C# Host API
│   └────────────────────────────────────────┘   │
└────────────────────────────────────────────────┘

  또는 단독 dev 모드:
     http://localhost:5300/ext/<path>
     ↳ APS Host 없이 `DeveloperTool` 이 hostData를 흉내냄
```

## 3가지 런타임 구성

이 저장소의 코드가 실행되는 "환경"은 3가지:

| 환경 | 언제 | 프론트 URL | Host 주입 | 세션 | 비고 |
|------|------|-----------|-----------|------|------|
| **Host 통합 (프로덕션)** | APS에 실제 얹혀 있을 때 | `https://...aps/ext/...` 등 APS 라우팅 | `provide('hostData', ...)` | 있음 (fusionauth.sid) | 실제 서비스 동작. `/api/aps/...` 포함 전부 200 |
| **Host 로그인 + Dev remote** | 개발 중이지만 host 세션 사용 | Host 환경변수로 remote 를 dev 서버로 지정 | 정상 주입 | 있음 | 프론트를 수정하면서도 `/api/aps/...` 응답을 받고 싶을 때 |
| **완전 단독 dev** | 로컬에서만 기동 | `http://localhost:5300/ext/...` | `DeveloperTool` 이 mock 주입 | 없음 | `/api/aps/...` 는 401. 커스텀 백엔드(`/api/custom/...`)만 정상 |

새 페이지를 처음 만들 때는 보통 **단독 dev** 로 시작해 최대한 많은 로직을 `/api/custom/...` 에 직접 구현하고, 마지막에 host 에 통합해 검증합니다.

## 두 개의 서버, 두 개의 역할

프론트에서 서버를 호출하는 경로는 크게 두 줄기입니다.

| 경로 | 대상 | 쓰는 상황 |
|------|------|-----------|
| `/api/custom/backend/{projectId}/...` | **이 저장소의 FastAPI** | 대부분의 새 페이지는 여기를 쓴다. Trino/PG 직접 조회, 프로젝트 전용 집계 |
| `/api/aps/backend/{projectId}/...` | **APS C# 호스트의 표준 API** | 메뉴·번역·프로젝트 정보·시나리오 관리 등 APS 표준 기능. **세션 필요** |

실무 지침: **커스텀 기능은 `custom` 경로에만** 담으세요. `aps` 경로는 "APS의 표준 API 값 그대로가 필요한" 경우만 조심스럽게 사용합니다. 자세한 선택 기준은 [07-data-sources](./07-data-sources.md).

## 개발 주요 산출물

새 페이지 하나를 완성하려면 보통 다음 파일이 추가/수정됩니다.

```
frontend/src/
 ├─ views/templates/<domain>/<page>/
 │    ├─ MyPage.vue                ← 화면
 │    ├─ myPage.ts                 ← 상태·fetch composable
 │    └─ MyPagePop.vue              (필요 시) 팝업
 ├─ router/index.ts                ← dev 라우트 추가
 ├─ expose.ts                      ← Host 용 viewRegistry 등록
 └─ lang/{ko,en,jp,zh}.json         (사용한 text 키가 없다면 추가)

backend/app/
 ├─ schemas/my_page.py             ← Pydantic 요청/응답
 ├─ services/my_page.py            ← 비즈니스 로직 + SQL
 ├─ services/my_page_queries.py    (SQL 템플릿 분리 시)
 └─ api/v1/endpoints/my_page.py    ← 라우터
 └─ api/v1/api.py                  ← include_router 등록
```

구체 절차는 [06-creating-a-page](./06-creating-a-page.md) 에서 단계별로 따라갈 수 있습니다.

## 이어서 볼 문서

- 로컬 환경 세팅: [02-environment-setup](./02-environment-setup.md)
- 전체 흐름과 두 종류 백엔드의 구분: [03-architecture](./03-architecture.md)
