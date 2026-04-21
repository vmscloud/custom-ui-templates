# 05. 백엔드 가이드

FastAPI 앱 `backend/app/` 의 구조와 개발 관례를 정리합니다.

## 앱 조립 (main.py)

```
app/main.py
 ├─ FastAPI 인스턴스 생성
 ├─ CORS / 공통 미들웨어
 ├─ mock 미들웨어 (MOCK_MODE 일 때만)
 └─ api_router include (/api/custom/backend/{project_id})
```

- `api/v1/api.py` 가 도메인 라우터들을 묶어 `api_router` 하나로 제공.
- 각 도메인 라우터는 `api/v1/endpoints/<domain>.py`.

## 엔드포인트 기본 틀

```python
# app/api/v1/endpoints/my_page.py
import logging
from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.schemas.my_page import MyPageRequest
from app.services.my_page import MyPageService, get_my_page_service

router = APIRouter()
logger = logging.getLogger(__name__)

def _error(status: int, label: str, exc: Exception):
    logger.exception(f"[{label}] {exc}")
    detail = str(exc) if settings.DEBUG else None
    return JSONResponse(
        status_code=status,
        content={
            "success": False,
            "error": f"{label} 중 오류가 발생했습니다.",
            **({"detail": detail} if detail else {}),
        },
    )


@router.get("/options")
async def get_options(
    project_id: str = Path(...),
    plan_ver: str = Query(..., alias="planVer"),
    service: MyPageService = Depends(get_my_page_service),
):
    try:
        return {"success": True, "data": await service.get_options(project_id, plan_ver)}
    except Exception as e:
        return _error(500, "옵션 조회", e)


@router.post("/main")
async def post_main(
    params: MyPageRequest,
    project_id: str = Path(...),
    service: MyPageService = Depends(get_my_page_service),
):
    try:
        return await service.get_main(project_id, params)
    except Exception as e:
        return _error(500, "메인 조회", e)
```

### `api.py` 에 등록

```python
# app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints.my_page import router as my_page_router

api_router = APIRouter()
api_router.include_router(
    my_page_router,
    prefix="/{project_id}/my-page",
    tags=["my-page"],
)
```

`include_router` 누락은 초보 때 흔한 실수. Swagger(`/docs`)에 라우트가 보이는지 확인.

## 서비스 레이어

비즈니스 로직과 SQL 호출은 `services/<domain>.py` 에 모읍니다. 엔드포인트는 얇게 유지.

```python
# app/services/my_page.py
from fastapi import Depends
from app.adapters.adapter import QueryExecutorAdapter
from app.api.dependencies import get_query_executor_adapter
from app.core.config import settings
from app.core.database import execute_query
from app.services import my_page_queries as Q


class MyPageService:
    def __init__(self, adapter: QueryExecutorAdapter):
        self.adapter = adapter
        self.catalog = settings.TRINO_CATALOG_ICEBERG
        self.schema = settings.TRINO_SCHEMA_APS

    # ── Helpers ────────────────────────────────
    async def _trino(self, project_id: str, sql: str):
        return await self.adapter.execute_direct_query(
            project_id=project_id, query=sql,
            catalog=self.catalog, schema=self.schema,
        )

    async def _trino_all(self, project_id: str, sql: str,
                         page_size: int = 50000, max_pages: int = 500):
        """페이지 순회 버전. 집계/전량 조회에 사용."""
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
        return {"success": True, "row": all_rows, "rowcount": len(all_rows)}

    # ── 비즈니스 메서드 ────────────────────────
    async def get_options(self, project_id: str, plan_ver: str):
        partition_key = f"{project_id}@{plan_ver[:6]}"
        sql = Q.OPTIONS_SQL.format(partition_key=partition_key, plan_ver=plan_ver)
        result = await self._trino(project_id, sql)
        return result.get("row", []) if result.get("success") else []

    async def get_main(self, project_id: str, params):
        # ...
        return {"success": True, "data": [...], "demandData": [...]}


def get_my_page_service(
    adapter: QueryExecutorAdapter = Depends(get_query_executor_adapter),
) -> MyPageService:
    return MyPageService(adapter)
```

### PG 조회

PostgreSQL 은 동기 `execute_query`를 제공합니다.

```python
from app.core.database import execute_query
rows = execute_query(
    f"SELECT plan_cycle_id FROM cfg_plan_config WHERE plan_ver='{pv}' LIMIT 1"
)
```

비동기 컨텍스트에서 호출이 부담되면 `execute_query_async`(내부 `asyncio.to_thread`)를 쓰세요. 사용자 입력을 SQL에 직접 삽입하지 말고, 필요하면 이스케이프 헬퍼를 두세요 (`_build_filter` 예시는 아래).

## Schemas (Pydantic v2)

```python
# app/schemas/my_page.py
from pydantic import BaseModel, Field

class MyPageRequest(BaseModel):
    planVer: str = Field(...)
    planCycleID: str = Field(default="")
    summaryType: str = Field(default="OPERGROUP")
    aggregateType: str = Field(default="itemGroup")
    operGroupIDs: list[str] = Field(default_factory=list)
```

- camelCase 키 유지 시 프론트 body 와 매핑이 매끄러움.
- `list` 같은 mutable default 는 반드시 `default_factory`.

## SQL 템플릿 파일

SQL이 여러 개거나 길면 별도 파일로 빼기:

```python
# app/services/my_page_queries.py
OPTIONS_SQL = """
SELECT DISTINCT option_id
FROM cfg_my_option
WHERE project_id = '{partition_key}'
  AND plan_ver   = '{plan_ver}'
ORDER BY option_id
"""

MAIN_PIVOT_SQL = """
SELECT
    group_id, date, qty
FROM rpt_my_pivot
WHERE partition_key = '{partition_key}'
  AND plan_ver      = '{plan_ver}'
  {extra_filter}
"""
```

값 이스케이프/IN 빌더:

```python
def _build_filter(field: str, values: list) -> str:
    filtered = [v for v in values if v not in (None, "")]
    if not filtered:
        return ""
    escaped = ", ".join(f"'{str(v).replace(chr(39), chr(39)*2)}'" for v in filtered)
    return f"AND {field} IN ({escaped})"
```

## Page 순회 헬퍼

Trino `/query/execute-stream` 은 페이지당 **최대 50,000 row**. 집계용 쿼리라면 아래 패턴으로 모든 페이지를 누적합니다.

```python
async def _trino_all(self, project_id: str, sql: str,
                     page_size: int = 50000, max_pages: int = 500):
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
    return {"success": True, "row": all_rows, "rowcount": len(all_rows)}
```

단일 row 조회(`/plan-cycle-info`처럼 `LIMIT 1`)에는 단순 `_trino` 하나로 충분합니다.

## 에러 처리

- 서비스 메서드는 실패해도 **호출자에게 최소한의 정보**(빈 리스트, 설명 로그)를 넘깁니다.
- 엔드포인트 `_error` 헬퍼는 로그 + HTTP 500. `DEBUG=true` 일 때만 detail 반환.
- 절대 피해야 할 안티패턴: 쿼리 에러를 `{"row": []}` 로 삼켜버리고 프론트에서 "데이터 없음"으로 표시 → 원인 파악이 지연됩니다. 개발 중엔 임시 `_debug` 필드를 응답에 추가해 실제 원인을 보세요 ([10-debugging](./10-debugging.md)).

## 쓰기 작업 (INSERT/UPDATE/DELETE)

Trino 로 쓰기 할 때는 `is_write=True` 옵션 필수:

```python
await self.adapter.execute_direct_query(
    project_id=project_id,
    query="INSERT INTO cfg_my_option (...) VALUES (...)",
    catalog=self.catalog, schema=self.schema,
    is_write=True,
)
```

PG 쓰기는 `core/database.py` 의 별도 함수(예: `execute_write`)를 사용하거나 `repositories/` 아래 CRUD 래퍼를 작성합니다.

## Dependency Injection 규칙

- 서비스 팩토리 `get_my_page_service` 는 항상 `get_query_executor_adapter` 에 의존.
- 라우터에서 `service: MyPageService = Depends(get_my_page_service)` 형태로 주입.
- 싱글톤 어댑터가 `app/api/dependencies.py` 에 정의되어 있어 HTTP 커넥션 풀이 유지됩니다.

## 체크리스트

- [ ] `schemas/` Pydantic 모델 작성
- [ ] `services/` 비즈니스 로직 + SQL
- [ ] `api/v1/endpoints/` 라우터 + `_error` 적용
- [ ] `api/v1/api.py` 에 `include_router` 등록
- [ ] Swagger(`/docs`) 에 경로가 보이는지 확인
- [ ] 대량 조회에 `_trino_all` 적용했는지
- [ ] 쓰기 구문에 `is_write=True`
- [ ] 에러 케이스에서도 의미있는 응답 (`success:false` + 메시지)

다음: [06-creating-a-page](./06-creating-a-page.md) 에서 프론트+백엔드를 처음부터 같이 만듭니다.
