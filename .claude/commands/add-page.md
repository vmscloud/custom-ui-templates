# 새 페이지 추가 (프론트엔드 + 백엔드)

FastAPI 백엔드 API와 Vue 프론트엔드 뷰를 한번에 스캐폴딩합니다.

## 입력 파라미터

사용자가 제공한 정보: $ARGUMENTS

위 정보에서 다음을 파악하세요:

- **featureName**: 기능 이름 (예: `load-factor`, `plan-dashboard`) — kebab-case, 필수
- **displayName**: 한글 기능명 (예: `부하율`, `계획 대시보드`) — 필수
- **description**: 기능 설명 (없으면 displayName 사용)
- **category**: 프론트엔드 카테고리 폴더 (sp, dm, pe, basic, chart, grid 중 하나, 기본값: sp)
- **dataSource**: 데이터 소스 (`trino`, `postgres`, `both` 중 하나, 기본값: trino)
  - `trino`: Trino (Iceberg) 읽기 전용 분석 쿼리 (서비스 + queries 파일)
  - `postgres`: PostgreSQL CRUD (레포지토리 패턴)
  - `both`: Trino 조회 + PostgreSQL CRUD 모두

정보가 부족하면 사용자에게 물어보세요.

## 네이밍 규칙

featureName으로부터 파생:

| 형태 | 예시 | 용도 |
|------|------|------|
| **kebab-case** | `my-feature` | URL prefix, 태그, 폴더명 |
| **snake_case** | `my_feature` | 파이썬 파일명, 모듈명 |
| **PascalCase** | `MyFeature` | 클래스명, 뷰 컴포넌트명 |
| **camelCase** | `myFeature` | composable 파일명, JS 변수명 |

## 프로젝트 구조 참고

```
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── dependencies.py          ← QueryExecutorAdapter 싱글톤
│   │   └── v1/
│   │       ├── api.py               ← ★ 라우터 등록
│   │       └── endpoints/           ← ★ 엔드포인트 파일
│   ├── schemas/                     ← ★ Pydantic 모델
│   ├── services/                    ← ★ Trino 비즈니스 로직
│   ├── repositories/                ← ★ PostgreSQL CRUD 로직
│   └── core/
│       ├── config.py                ← 설정 (settings 싱글톤)
│       └── database.py              ← execute_query, execute_write, execute_query_async

frontend/
├── src/
│   ├── expose.ts                    ← ★ 뷰 레지스트리 등록
│   ├── router/index.ts              ← ★ 라우터 등록
│   ├── api/client.ts                ← api 인스턴스, getProjectId()
│   ├── composables/useHostStores.ts ← useHostPlanCycle() 등
│   └── views/templates/{category}/{kebab-case}/
│       ├── {PascalCase}.vue         ← ★ 루트 뷰 컴포넌트
│       └── {camelCase}.ts           ← ★ Composable (API 호출)
```

---

# PART 1: 백엔드 생성

## 1-1. Pydantic 스키마: `backend/app/schemas/{snake_case}.py`

```python
"""
{displayName} 관련 Pydantic 스키마
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class {PascalCase}Request(BaseModel):
    """{displayName} 조회 요청"""

    planVer: str = Field(..., description="Plan version")
    # 필요한 필드를 여기에 추가하세요
```

## 1-2. 서비스 (dataSource가 `trino` 또는 `both`일 때)

### SQL 쿼리 파일: `backend/app/services/{snake_case}_queries.py`

```python
"""
{displayName} SQL 쿼리 상수

Trino (Iceberg) execute_direct_query로 실행.
파라미터는 Python str.format() 스타일 {{param}}.
"""

# 메인 데이터 조회
MAIN_SQL = """
SELECT *
FROM your_table
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
ORDER BY 1
"""
```

### 서비스 파일: `backend/app/services/{snake_case}.py`

```python
"""
{displayName} 서비스

Trino (Iceberg)에서 데이터를 조회합니다.
"""

from __future__ import annotations

import logging
from typing import Any

from app.adapters.adapter import QueryExecutorAdapter
from app.api.dependencies import get_query_executor_adapter
from app.core.config import settings
from app.services import {snake_case}_queries as Q
from fastapi import Depends

logger = logging.getLogger(__name__)


class {PascalCase}Service:
    """{displayName} 비즈니스 로직"""

    def __init__(self, adapter: QueryExecutorAdapter):
        self.adapter = adapter
        self.catalog = settings.TRINO_CATALOG_ICEBERG
        self.schema = settings.TRINO_SCHEMA_APS

    async def _trino(self, project_id: str, sql: str) -> dict[str, Any]:
        """Trino 쿼리 실행"""
        return await self.adapter.execute_direct_query(
            project_id=project_id,
            query=sql,
            catalog=self.catalog,
            schema=self.schema,
        )

    def _safe_rows(self, result: dict[str, Any]) -> list[dict]:
        """쿼리 결과에서 행 데이터 추출"""
        if not result.get("success"):
            logger.warning(
                f"[{PascalCase}] Trino query failed: %s",
                result.get("message", "unknown error"),
            )
            return []
        return result.get("row", [])

    def _partition_key(self, project_id: str, plan_ver: str) -> str:
        return f"{project_id}@{plan_ver[:6]}"

    async def get_main(
        self, project_id: str, plan_ver: str,
    ) -> dict[str, Any]:
        """{displayName} 메인 데이터 조회"""
        partition_key = self._partition_key(project_id, plan_ver)
        sql = Q.MAIN_SQL.format(
            partition_key=partition_key,
            plan_ver=plan_ver,
        )
        result = await self._trino(project_id, sql)
        rows = self._safe_rows(result)
        return {"success": True, "count": len(rows), "data": rows}


def get_{snake_case}_service(
    adapter: QueryExecutorAdapter = Depends(get_query_executor_adapter),
) -> {PascalCase}Service:
    return {PascalCase}Service(adapter)
```

## 1-3. 레포지토리 (dataSource가 `postgres` 또는 `both`일 때)

### 레포지토리 파일: `backend/app/repositories/{snake_case}.py`

```python
"""{displayName} 레포지토리 — PostgreSQL 직접 접근"""

from app.core.database import execute_query, execute_write


class {PascalCase}Repository:

    @staticmethod
    def get_list(project_id: str, plan_ver: str) -> list[dict]:
        """{displayName} 목록 조회"""
        query = """
        SELECT *
        FROM your_table
        WHERE project_id = %s AND plan_ver = %s
        ORDER BY 1
        """
        return execute_query(query, (project_id, plan_ver))

    @staticmethod
    def get_by_id(project_id: str, record_id: str) -> list[dict]:
        """{displayName} 단건 조회"""
        query = """
        SELECT *
        FROM your_table
        WHERE project_id = %s AND id = %s
        """
        return execute_query(query, (project_id, record_id))

    @staticmethod
    def create(project_id: str, data: dict) -> int:
        """{displayName} 생성"""
        query = """
        INSERT INTO your_table (project_id, col1, col2, create_datetime)
        VALUES (%s, %s, %s, NOW())
        """
        return execute_write(query, (project_id, data.get("col1"), data.get("col2")))

    @staticmethod
    def update(project_id: str, record_id: str, data: dict) -> int:
        """{displayName} 수정"""
        query = """
        UPDATE your_table
        SET col1 = %s, col2 = %s, update_datetime = NOW()
        WHERE project_id = %s AND id = %s
        """
        return execute_write(query, (data.get("col1"), data.get("col2"), project_id, record_id))

    @staticmethod
    def delete(project_id: str, record_id: str) -> int:
        """{displayName} 삭제"""
        query = """
        DELETE FROM your_table
        WHERE project_id = %s AND id = %s
        """
        return execute_write(query, (project_id, record_id))
```

## 1-4. 엔드포인트: `backend/app/api/v1/endpoints/{snake_case}.py`

**dataSource=trino 일 때:**

```python
"""
{displayName} API 라우터

{description}
"""

import logging

from app.core.config import settings
from app.schemas.{snake_case} import {PascalCase}Request
from app.services.{snake_case} import {PascalCase}Service, get_{snake_case}_service
from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse

router = APIRouter()
logger = logging.getLogger(__name__)


def _error_response(status_code: int, label: str, exc: Exception) -> JSONResponse:
    logger.exception(f"[{label}] {exc}")
    detail = str(exc) if settings.DEBUG else None
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": f"{label} 중 오류가 발생했습니다.",
            **({"detail": detail} if detail else {}),
        },
    )


@router.get("/main")
async def get_main(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_ver: str = Query(..., alias="planVer", description="Plan version"),
    service: {PascalCase}Service = Depends(get_{snake_case}_service),
):
    """{displayName} 메인 데이터 조회"""
    try:
        return await service.get_main(project_id, plan_ver)
    except ValueError as e:
        return _error_response(400, "{displayName} 조회", e)
    except Exception as e:
        return _error_response(500, "{displayName} 조회", e)
```

**dataSource=postgres 일 때:**

```python
"""
{displayName} API 라우터

{description}
"""

import logging

from app.core.config import settings
from app.schemas.{snake_case} import {PascalCase}Request
from app.repositories.{snake_case} import {PascalCase}Repository
from fastapi import APIRouter, Path, Query
from fastapi.responses import JSONResponse

router = APIRouter()
logger = logging.getLogger(__name__)


def _error_response(status_code: int, label: str, exc: Exception) -> JSONResponse:
    logger.exception(f"[{label}] {exc}")
    detail = str(exc) if settings.DEBUG else None
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": f"{label} 중 오류가 발생했습니다.",
            **({"detail": detail} if detail else {}),
        },
    )


@router.get("/main")
async def get_list(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_ver: str = Query(..., alias="planVer", description="Plan version"),
):
    """{displayName} 목록 조회"""
    try:
        rows = {PascalCase}Repository.get_list(project_id, plan_ver)
        return {"success": True, "count": len(rows), "data": rows}
    except Exception as e:
        return _error_response(500, "{displayName} 조회", e)


@router.get("/{record_id}")
async def get_by_id(
    project_id: str = Path(..., description="프로젝트 ID"),
    record_id: str = Path(..., description="레코드 ID"),
):
    """{displayName} 단건 조회"""
    try:
        rows = {PascalCase}Repository.get_by_id(project_id, record_id)
        return {"success": True, "data": rows[0] if rows else None}
    except Exception as e:
        return _error_response(500, "{displayName} 상세 조회", e)


@router.post("/")
async def create(
    params: {PascalCase}Request,
    project_id: str = Path(..., description="프로젝트 ID"),
):
    """{displayName} 생성"""
    try:
        rowcount = {PascalCase}Repository.create(project_id, params.model_dump())
        return {"success": True, "rowcount": rowcount}
    except Exception as e:
        return _error_response(500, "{displayName} 생성", e)


@router.put("/{record_id}")
async def update(
    params: {PascalCase}Request,
    project_id: str = Path(..., description="프로젝트 ID"),
    record_id: str = Path(..., description="레코드 ID"),
):
    """{displayName} 수정"""
    try:
        rowcount = {PascalCase}Repository.update(project_id, record_id, params.model_dump())
        return {"success": True, "rowcount": rowcount}
    except Exception as e:
        return _error_response(500, "{displayName} 수정", e)


@router.delete("/{record_id}")
async def delete(
    project_id: str = Path(..., description="프로젝트 ID"),
    record_id: str = Path(..., description="레코드 ID"),
):
    """{displayName} 삭제"""
    try:
        rowcount = {PascalCase}Repository.delete(project_id, record_id)
        return {"success": True, "rowcount": rowcount}
    except Exception as e:
        return _error_response(500, "{displayName} 삭제", e)
```

**dataSource=both 일 때:** Trino 조회 엔드포인트 + PostgreSQL CRUD 엔드포인트를 합쳐서 생성

## 1-5. 기존 파일 수정: `backend/app/api/v1/api.py`

import 추가:
```python
from app.api.v1.endpoints import {snake_case}
```

라우터 등록 추가 (`proxy.router` 등록보다 **위에**):
```python
api_router.include_router(
    {snake_case}.router,
    prefix="/api/custom/backend/{{project_id}}/{kebab-case}",
    tags=["{kebab-case}-api"],
)
```

---

# PART 2: 프론트엔드 생성

## 2-1. Composable: `frontend/src/views/templates/{category}/{kebab-case}/{camelCase}.ts`

```ts
/**
 * {displayName} API 호출 및 데이터 관리
 */
import { api, getProjectId } from "@/api/client";
import { ref } from "vue";

// ===== Types =====

export interface {PascalCase}Row {
  [key: string]: any;
}

// ===== API =====

const BASE_URL = () => `/api/custom/backend/${getProjectId()}/{kebab-case}`;

// ===== Composable =====

export function use{PascalCase}() {
  const data = ref<{PascalCase}Row[]>([]);
  const loading = ref(false);

  async function loadData(planVer: string) {
    loading.value = true;
    try {
      const res = await api.get<{ success: boolean; count: number; data: {PascalCase}Row[] }>(
        `${BASE_URL()}/main`,
        { params: { planVer } },
      );
      data.value = res?.data ?? [];
    } catch (e) {
      console.error("[{PascalCase}] loadData error:", e);
      data.value = [];
    } finally {
      loading.value = false;
    }
  }

  function reset() {
    data.value = [];
  }

  return {
    data,
    loading,
    loadData,
    reset,
  };
}
```

## 2-2. 뷰 컴포넌트: `frontend/src/views/templates/{category}/{kebab-case}/{PascalCase}.vue`

```vue
<template>
  <div class="{kebab-case}-page">
    <!-- Filter Section -->
    <Controller
      :navigations="navigationPath"
      showFilterButton
      :actions="[
        {
          action: 'Search',
          click: handleSearch,
          disabled: loading || !planVer,
        },
      ]"
    >
      <template #filter>
        <!-- 필터 컴포넌트를 여기에 추가하세요 -->
      </template>
    </Controller>

    <!-- Main Content -->
    <section class="content-section">
      <div v-if="data.length === 0 && !loading" class="empty-state">
        <EmptyState :is-read-only="true" />
      </div>

      <div v-else class="grid-container">
        <ExtendFlexGrid
          name="{camelCase}Main"
          :itemsSource="data"
          height="100%"
          :isReadOnly="true"
          :loading="loading"
          :setContextMenuProps="{
            useFlexGridSetting: true,
            useFilter: true,
            useExportExcel: true,
          }"
        >
          <!-- 그리드 컬럼을 여기에 추가하세요 -->
          <!-- <WjFlexGridColumn binding="colName" header="컬럼명" /> -->
        </ExtendFlexGrid>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from "vue";
import { useTranslation } from "i18next-vue";
import { Controller, EmptyState } from "@vmscloud/moz-ui-components";
import { ExtendFlexGrid } from "@vmscloud/moz-wijmo-grid";
// import { WjFlexGridColumn } from "@vmscloud/moz-wijmo-grid/wijmo.vue2.grid";
import { useHostPlanCycle } from "@/composables/useHostStores";
import { use{PascalCase} } from "./{camelCase}";

const { t } = useTranslation();
const { planVer } = useHostPlanCycle();

const navigationPath = ["{displayName}"];

const {
  data,
  loading,
  loadData,
  reset,
} = use{PascalCase}();

async function handleSearch() {
  if (!planVer.value) return;
  reset();
  await loadData(planVer.value);
}

onMounted(() => {
  if (planVer.value) {
    handleSearch();
  }
});

watch(planVer, (newVer) => {
  if (newVer) {
    reset();
    handleSearch();
  }
});
</script>

<style scoped lang="scss">
.{kebab-case}-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

.content-section {
  padding: 0 20px 20px 20px;
  flex: 1;
  overflow: hidden;
  position: relative;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
}

.grid-container {
  height: 100%;
}
</style>
```

## 2-3. 기존 파일 수정

### `frontend/src/expose.ts`

`viewRegistry`에 추가:
```ts
{PascalCase}: withHostInit(() => import("./views/templates/{category}/{kebab-case}/{PascalCase}.vue")),
```

`viewMeta`에 추가:
```ts
{PascalCase}: { name: "{PascalCase}", defaultMenuName: "{displayName}" },
```

### `frontend/src/router/index.ts`

routes 배열에 추가:
```ts
{
  path: "/{kebab-case}",
  name: "{PascalCase}",
  component: () => import("@/views/templates/{category}/{kebab-case}/{PascalCase}.vue"),
},
```

---

# 실행 순서

1. **백엔드** — schemas, services (+ queries), repositories 파일 생성
2. **백엔드** — endpoints 파일 생성
3. **백엔드** — `api/v1/api.py`에 import 및 라우터 등록 (proxy 위에)
4. **프론트엔드** — 뷰 폴더 생성, composable + vue 파일 생성
5. **프론트엔드** — `expose.ts`, `router/index.ts` 수정
6. 가능하면 `cd backend && python -c "from app.main import app; print('OK')"` 실행
7. 생성된 파일 목록, API 경로, 프론트 접근 경로를 사용자에게 안내

# 사용자 안내 포맷

작업 완료 후 아래 형식으로 결과를 안내하세요:

```
## 생성된 파일

### 백엔드
| 파일 | 설명 |
|------|------|
| `app/schemas/{snake_case}.py` | Pydantic 스키마 |
| `app/services/{snake_case}_queries.py` | SQL 쿼리 상수 |
| `app/services/{snake_case}.py` | 서비스 (비즈니스 로직) |
| `app/api/v1/endpoints/{snake_case}.py` | API 엔드포인트 |

### 프론트엔드
| 파일 | 설명 |
|------|------|
| `src/views/templates/{category}/{kebab-case}/{PascalCase}.vue` | 뷰 컴포넌트 |
| `src/views/templates/{category}/{kebab-case}/{camelCase}.ts` | Composable |

### 수정된 파일
- `backend/app/api/v1/api.py` — 라우터 등록
- `frontend/src/expose.ts` — viewRegistry, viewMeta 등록
- `frontend/src/router/index.ts` — 개발용 라우터 등록

### API 경로
GET /api/custom/backend/{project_id}/{kebab-case}/main?planVer=...

### 프론트엔드 접근
- 개발: http://localhost:5173/{kebab-case}
- Host: viewRegistry의 "{PascalCase}" 키로 접근

### TODO
- [ ] SQL 쿼리 작성 (queries 파일)
- [ ] 그리드 컬럼 정의 (vue 파일)
- [ ] Pydantic 스키마 필드 추가
```

# 주의사항

- 반드시 기존 코드(load_factor, freeze_plan 등)의 스타일을 따르세요
- `from __future__ import annotations`를 schemas, services 파일 상단에 포함하세요
- 에러 핸들링은 `_error_response` 헬퍼 패턴을 사용하세요
- SQL 쿼리는 반드시 별도 `_queries.py` 파일로 분리하세요 (Trino의 경우)
- PostgreSQL CRUD는 레포지토리 패턴(`repositories/`)을 사용하세요
- `proxy.router`는 catch-all이므로 항상 api.py에서 마지막이어야 합니다
- settings.DEBUG가 True일 때만 에러 상세 정보를 노출하세요
- 프론트엔드에서 `DeveloperTool` 래퍼는 사용하지 않습니다 — `Controller`를 직접 씁니다
- import 경로에 `@/`(src alias)를 사용하세요
