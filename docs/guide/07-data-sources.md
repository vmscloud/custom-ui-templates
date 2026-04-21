# 07. 데이터 소스 선택 가이드

이 저장소에서는 한 화면 안에서 **세 종류의 백엔드**가 섞여 쓰일 수 있습니다. 어떤 경우에 무엇을 호출할지 정리합니다.

## 세 가지 옵션

| 옵션 | 경로 | 접근 | 대상 |
|------|------|------|------|
| A | `/api/custom/backend/{pid}/...` | FastAPI `execute_query` | **PostgreSQL** (설정·마스터) |
| B | `/api/custom/backend/{pid}/...` | FastAPI `QueryExecutorAdapter.execute_direct_query` | **Trino / Iceberg** (fact·시계열) |
| C | `/api/aps/backend/{pid}/...` | 브라우저가 직접 호출 (프록시 없이) | **APS C# 호스트** |

> 같은 "FastAPI" 안에서 A/B 를 섞는 경우도 흔합니다. 하나의 서비스 메서드에서 PG 로 설정값을 읽고, Trino 로 집계 데이터를 내려주는 식.

## 선택 기준

### A. PostgreSQL

- **언제**: 설정값·마스터·사용자 입력(북마크·옵션·소규모 리스트) 등 row 수가 수백~수만 정도, 자주 쓰기 발생.
- **장점**: 트랜잭션·제약조건 풍부, 응답 빠름, INSERT/UPDATE 쉬움.
- **접근**: `from app.core.database import execute_query`
- **대표 테이블명**: `cfg_*`, `mst_*`

```python
rows = execute_query(
    f"""SELECT plan_cycle_id, frozen_plan_ver
        FROM cfg_plan_cycle_info
        WHERE project_id='{pid}' LIMIT 1"""
)
```

### B. Trino / Iceberg

- **언제**: 시계열·집계 대상이 되는 fact 데이터 (수백만~수억 row), 공정 계획 결과·수요·실적.
- **장점**: 대용량 집계·병렬 처리, 여러 catalog/스키마 연결.
- **접근**: `QueryExecutorAdapter.execute_direct_query(project_id, query, catalog, schema, ...)`
- **대표 테이블명**: `rpt_*`, `odv_*`

#### Trino 타입 주의

Trino 쿼리는 PostgreSQL 과 문법은 유사하지만 **타입 변환이 엄격**합니다.

| 상황 | PG | Trino |
|------|----|-------|
| `'20260401'::date` | 가능 | **실패** (`Value cannot be cast to date`) |
| 문자열 `'YYYY-MM-DD'` → DATE | 가능 | 가능 |
| `json_column->>'key'` | 가능 | `json_extract_scalar(json_column, '$.key')` |

저장 포맷이 `YYYYMMDD` 같은 문자열이라면 **문자열 비교**로 풀거나 `substr`로 `YYYY-MM-DD` 포맷을 조립하세요.

```sql
-- Trino 에서 YYYYMMDD 컬럼 처리 예
SELECT
    substr(CAST(plan_date AS VARCHAR), 1, 4)
    || '-' || substr(CAST(plan_date AS VARCHAR), 5, 2)
    || '-' || substr(CAST(plan_date AS VARCHAR), 7, 2) AS date
FROM rpt_xxx
WHERE CAST(plan_date AS VARCHAR) >= '20260401'
  AND CAST(plan_date AS VARCHAR) <= '20260430'
```

#### 페이지네이션 (50,000 row)

Trino adapter 는 한 번에 최대 50,000 row 를 반환합니다. `has_next: true` 면 반드시 다음 페이지를 가져와 누적해야 합니다.

```python
async def _trino_all(self, project_id, sql, page_size=50000, max_pages=500):
    all_rows = []
    page = 1
    while page <= max_pages:
        res = await self.adapter.execute_direct_query(
            project_id=project_id, query=sql,
            catalog=self.catalog, schema=self.schema,
            page=page, limit=page_size,
        )
        if not res.get("success"):
            return res
        rows = res.get("row") or []
        all_rows.extend(rows)
        if not res.get("has_next") or not rows:
            break
        page += 1
    return {"success": True, "row": all_rows}
```

집계가 필요 없고 미리보기만이라면 단일 페이지(`_trino`) + 프론트 페이지네이션을 고려하세요.

### C. APS C# 호스트 API

- **언제**: 사용자 설정(`ComUserLayout`, `ComUserBookmark`), 시나리오 관리(`PlmScenarioMaster`), 번역/메뉴(`SamLanguage`), 실행 플로우(`PlmExecutionFlowMaster`) 등 APS 표준 API.
- **인증**: 브라우저에 APS 세션 쿠키(`fusionauth.sid`) 필요. Dev 단독 실행에서는 401 이 나옵니다.
- **호출**: 프론트에서 `api.get('/api/aps/backend/{pid}/<path>')` 직접 호출. vite dev 프록시가 호스트로 forward.

```ts
import { api, getProjectId } from "@/api/client";

await api.get(`/api/aps/backend/${getProjectId()}/PlmScenarioMaster`);
```

#### Dev 환경에서의 처리

- 401 이 정상인 요청 (세션 없음 → 빈 리스트로 fallback) 이라는 사실을 프론트 코드가 알고 있어야 합니다.
- 필요하면 FastAPI 측에서 proxy 엔드포인트(`/api/custom/backend/<pid>/<domain>/proxy/<route>`) 를 만들어 같은 쿠키를 forward 할 수 있습니다. 세션이 없으면 역시 401. **커스텀 로직이 필요하면 C 대신 A/B 로 대체하는 쪽이 안전**.

## 어떤 걸 쓸지 판단하기

아래 질문을 위에서부터 적용하세요.

1. "내가 만들고 싶은 화면의 핵심 집계 데이터가 `rpt_*`, `odv_*` 같은 fact 에 있나?" → **B (Trino)**
2. "설정값·사용자 옵션·프로젝트 설정 같은 작은 테이블이 필요한가?" → **A (PG)**
3. "APS 표준 관리자 기능(시나리오·번역·메뉴 등) 결과를 그대로 쓰고 싶은가?" → **C (APS Host)**
4. 그 외 커스텀 집계/파생 계산은 **모두 A/B** 로 직접 구현. (C 사용은 최후의 선택)

## 혼합 예시

한 엔드포인트 안에서 PG + Trino 를 함께 사용하는 흐름:

```python
class MyPageService:
    async def get_main(self, project_id, params):
        # A: 프로젝트 config
        cycle_info = execute_query(
            f"""SELECT plan_cycle_id, start_datetime, end_datetime
                FROM cfg_plan_cycle_info
                WHERE project_id='{project_id}'
                  AND plan_cycle_id='{params.planCycleID}' LIMIT 1"""
        )
        cycle_start = cycle_info[0]["start_datetime"] if cycle_info else "2000-01-01"
        cycle_end   = cycle_info[0]["end_datetime"]   if cycle_info else "9999-12-31"

        # B: Trino 집계 조회
        sql = Q.PIVOT_SQL.format(
            partition_key=f"{project_id}@{params.planVer[:6]}",
            plan_ver=params.planVer,
            start_date=cycle_start.strftime("%Y%m%d"),
            end_date=cycle_end.strftime("%Y%m%d"),
        )
        result = await self._trino_all(project_id, sql)
        return {"success": True, "data": result.get("row", [])}
```

## 쓰기 작업 권장 위치

- 설정·사용자 데이터 → PostgreSQL (`cfg_*`, `mst_*`) 에 `INSERT/UPDATE`.
- Trino 쓰기 (`is_write=True`) 는 가능은 하지만 대용량 fact 를 UI에서 직접 쓰는 경우는 드뭅니다. 보통 스케줄러/ETL 로 구성.
- APS 표준 관리 기능 (`ComUserLayout`) 쓰기는 세션이 반드시 있어야 하므로 호스트 통합 단계에서만 동작.

다음: [08-ui-patterns](./08-ui-patterns.md) 로 자주 쓰는 UI 구성 패턴을 이어갑니다.
