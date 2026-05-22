# ADR-0002: 데이터 접근 이원화 — 분석 조회는 Query Executor(Iceberg), 설정은 Trino PG 카탈로그

- **상태**: Accepted
- **결정일**: 2026-03-25 (소급 작성 2026-05-20)
- **관련**: `docs/history/2026-03-25-plan-dashboard-implementation.md`, `docs/guide/07-data-sources.md`
- **코드**: `backend/app/adapters/adapter.py`, `backend/app/core/database.py`,
  `backend/app/repositories/plan_dashboard.py`, `backend/app/services/plan_dashboard.py`

## Context

PlanDashboard은 성격이 다른 두 종류의 데이터를 다룬다.

1. **대용량 분석 데이터** — RTF/OTD/가동률 등 계획 결과 집계. 원본은 Iceberg 테이블에 있고,
   사내 **Query Executor** 서비스(저장된 query_id 실행 + 직접 SQL 실행 HTTP API)를 통해 접근하는 것이 표준이다.
2. **소량 설정·제어 메타데이터** — 위젯 설정(`dp_user_widget_config`), 계획 설정(`cfg_plan_config`),
   계획 상태/frozen 버전(`sys_plan_ctrl`). 이들은 PostgreSQL에 있고, 읽기뿐 아니라 **쓰기(설정 저장)** 가 필요하다.

하나의 접근 방식으로 둘을 모두 처리하려 하면 어색해진다: Query Executor는 분석 조회 지향이라 설정
CRUD에 부적합하고, 반대로 분석 데이터를 직접 커넥션으로 끌어오면 사내 표준 경로를 벗어난다.

## Decision

데이터 접근을 **두 경로로 명시 분리**한다.

| 경로 | 용도 | 구현 | 진입점 |
|---|---|---|---|
| **A. Query Executor 어댑터** | Iceberg 분석 조회 (읽기 전용) | `QueryExecutorAdapter` (httpx HTTP 클라이언트) → `execute_direct_query(catalog="iceberg")` / `execute_query(query_id=...)` | `services/` |
| **B. Trino PG 카탈로그 직결** | 설정·제어 메타 (읽기+쓰기) | `core/database.py` 의 `trino.dbapi.connect` (catalog = `TRINO_PG_CATALOG`) → `execute_query` / `execute_write` | `repositories/` |

- 비즈니스 로직은 `services/`가 A를, `repositories/`가 B를 담당하도록 계층으로 갈라
  "분석 조회 = 어댑터, 설정 CRUD = 레포지토리" 규칙을 코드 구조로 강제한다.
- async 엔드포인트에서 동기 Trino 호출이 event loop를 막지 않도록
  `execute_query_async`(= `asyncio.to_thread`)를 제공한다.

## Alternatives

- **모든 데이터를 Query Executor로** — 기각. 설정 저장(쓰기 DML)·트랜잭션 의미를 분석 조회용 API에
  얹기 부적절하고, 빈번한 소량 메타 조회에 HTTP 왕복 오버헤드가 과하다.
- **모든 데이터를 직접 커넥션으로** — 기각. Iceberg 분석 데이터는 Query Executor가 사내 표준 경로이며,
  권한·쿼리 관리·로깅이 그쪽에 집중돼 있어 우회하면 일관성을 잃는다.
- **설정 저장에 psycopg2 직접 연결** — 기각 *(재구성)*. PG 접근 경로를 Trino 카탈로그로 단일화하면
  커넥션/드라이버를 하나로 유지할 수 있다. 별도 psycopg2 풀을 두면 의존성과 설정이 이원화된다.
  > 참고: `docs/history/2026-03-25-...md`는 설정 저장을 "psycopg2(PostgreSQL 직접)"로 기록했으나
  > **실제 구현은 psycopg2가 아니라 Trino PG 카탈로그 직결**이다. 이 ADR이 정확한 사실이다.

## Consequences

**긍정**
- 데이터 성격(분석 vs 설정)과 접근 방식이 1:1로 매핑되어, 새 기능에서 "어디로 붙일지"가 자명하다
  (`services/` → 어댑터, `repositories/` → DB).
- PG 접근이 Trino 카탈로그로 단일화되어 드라이버/설정이 하나다.

**부정 / 부채**
- 개발자가 **두 접근 모델**을 모두 이해해야 한다. 경계를 어기면(예: 서비스에서 직접 DB 호출)
  계층 규칙이 쉽게 무너진다.
- **🔴 SQL 인젝션 위험**: `repositories/plan_dashboard.py`가 `project_id`/`plan_ver`/`user_id`를
  f-string으로 SQL에 직접 보간한다(예: `WHERE project_id = '{project_id}'`). 파라미터 바인딩으로
  교체해야 하는 실질적 보안 부채다. `execute_query`/`execute_write`는 `params` 인자를 지원하므로
  바인딩 전환이 가능하다.
- 설정 쓰기가 Trino PG 카탈로그를 거치므로, 네이티브 PG 트랜잭션이 필요한 시나리오에서는 제약이 생길 수 있다.
