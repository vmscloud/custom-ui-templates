# 06. 새 페이지 만들기 (실전)

처음부터 하나의 화면 + API를 구현해 `/ext/my-page` 로 접근 가능한 상태로 만드는 단계별 실습입니다.

**가정**: "작업 지시(`rpt_work_order`) 테이블에서 날짜 범위 필터로 작업 목록을 보여주는 그리드 화면"을 만든다.

## 0. 설계

1. **엔드포인트**
   - `POST /api/custom/backend/{projectId}/work-order/list`
     - body: `{ planVer, fromDate, toDate, statuses?: string[] }`
     - 응답: `{ success, data: [{work_order_id, item_id, due_date, qty, status}] }`
2. **화면**
   - 경로: `/ext/work-order`
   - 필터: 날짜 범위(`fromDate`, `toDate`) + 상태 MultiSelect
   - 그리드: 작업 목록
3. **데이터 소스**: Trino 의 `rpt_work_order` 가정.

## 1. 백엔드

### 1-1. 스키마

```python
# backend/app/schemas/work_order.py
from pydantic import BaseModel, Field

class WorkOrderListRequest(BaseModel):
    planVer: str = Field(...)
    fromDate: str = Field(..., description="YYYY-MM-DD")
    toDate: str = Field(..., description="YYYY-MM-DD")
    statuses: list[str] = Field(default_factory=list)
```

### 1-2. SQL 템플릿

```python
# backend/app/services/work_order_queries.py
LIST_SQL = """
SELECT
    work_order_id,
    item_id,
    CAST(due_date AS VARCHAR) AS due_date,
    CAST(qty     AS DOUBLE)  AS qty,
    status
FROM rpt_work_order
WHERE partition_key = '{partition_key}'
  AND plan_ver      = '{plan_ver}'
  AND CAST(plan_date AS VARCHAR) >= '{from_date}'
  AND CAST(plan_date AS VARCHAR) <= '{to_date}'
  {status_filter}
ORDER BY due_date, work_order_id
"""
```

> `plan_date` 가 YYYYMMDD 문자열로 저장된 테이블이라고 가정했습니다. 실제 컬럼 타입에 따라 표현을 바꿔주세요.

### 1-3. 서비스

```python
# backend/app/services/work_order.py
from fastapi import Depends
from app.adapters.adapter import QueryExecutorAdapter
from app.api.dependencies import get_query_executor_adapter
from app.core.config import settings
from app.services import work_order_queries as Q


class WorkOrderService:
    def __init__(self, adapter: QueryExecutorAdapter):
        self.adapter = adapter
        self.catalog = settings.TRINO_CATALOG_ICEBERG
        self.schema = settings.TRINO_SCHEMA_APS

    def _build_filter(self, field: str, values: list) -> str:
        filtered = [v for v in values if v not in (None, "")]
        if not filtered:
            return ""
        escaped = ", ".join(f"'{str(v).replace(chr(39), chr(39)*2)}'" for v in filtered)
        return f"AND {field} IN ({escaped})"

    async def _trino_all(self, project_id, sql, page_size=50000, max_pages=500):
        rows = []
        page = 1
        while page <= max_pages:
            res = await self.adapter.execute_direct_query(
                project_id=project_id, query=sql,
                catalog=self.catalog, schema=self.schema,
                page=page, limit=page_size,
            )
            if not res.get("success"):
                return res
            r = res.get("row") or []
            rows.extend(r)
            if not res.get("has_next") or not r:
                break
            page += 1
        return {"success": True, "row": rows, "rowcount": len(rows)}

    async def list(self, project_id: str, params) -> dict:
        partition_key = f"{project_id}@{params.planVer[:6]}"
        status_filter = self._build_filter("status", params.statuses)
        sql = Q.LIST_SQL.format(
            partition_key=partition_key,
            plan_ver=params.planVer,
            from_date=params.fromDate.replace("-", ""),
            to_date=params.toDate.replace("-", ""),
            status_filter=status_filter,
        )
        result = await self._trino_all(project_id, sql)
        return {"success": True, "data": result.get("row", [])}


def get_work_order_service(
    adapter: QueryExecutorAdapter = Depends(get_query_executor_adapter),
) -> WorkOrderService:
    return WorkOrderService(adapter)
```

### 1-4. 엔드포인트

```python
# backend/app/api/v1/endpoints/work_order.py
from fastapi import APIRouter, Depends, Path
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.schemas.work_order import WorkOrderListRequest
from app.services.work_order import WorkOrderService, get_work_order_service

router = APIRouter()


@router.post("/list")
async def list_work_orders(
    params: WorkOrderListRequest,
    project_id: str = Path(...),
    service: WorkOrderService = Depends(get_work_order_service),
):
    try:
        return await service.list(project_id, params)
    except Exception as e:
        detail = str(e) if settings.DEBUG else None
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "작업 지시 조회 중 오류",
                **({"detail": detail} if detail else {}),
            },
        )
```

### 1-5. api.py 등록

```python
# backend/app/api/v1/api.py
from app.api.v1.endpoints.work_order import router as work_order_router

api_router.include_router(
    work_order_router,
    prefix="/{project_id}/work-order",
    tags=["work-order"],
)
```

### 1-6. Swagger 로 1차 확인

Backend reload 후 `http://localhost:8000/docs` 에서 `POST /api/custom/backend/{project_id}/work-order/list` 를 열어 `Try it out` → 샘플 요청으로 200 확인.

## 2. 프론트엔드

### 2-1. composable

```ts
// frontend/src/views/templates/pe/work-order/workOrder.ts
import { api, getProjectId } from "@/api/client";
import { ref } from "vue";
import dayjs, { type Dayjs } from "dayjs";

export interface WorkOrder {
  work_order_id: string;
  item_id: string;
  due_date: string;
  qty: number;
  status: string;
}

const BASE_URL = () => `/api/custom/backend/${getProjectId()}/work-order`;

export const fetchList = (params: {
  planVer: string;
  fromDate: string;
  toDate: string;
  statuses: string[];
}) => api.post<{ success: boolean; data: WorkOrder[] }>(`${BASE_URL()}/list`, params);

export function useWorkOrder() {
  const rows = ref<WorkOrder[]>([]);
  const isPending = ref(false);

  const fromDate = ref<Dayjs>(dayjs().startOf("month"));
  const toDate   = ref<Dayjs>(dayjs().endOf("month"));
  const statuses = ref<string[]>([]);

  const statusSource = ref([
    { value: "PLAN",   label: "계획" },
    { value: "WIP",    label: "진행중" },
    { value: "DONE",   label: "완료" },
  ]);

  async function load(planVer: string) {
    if (!planVer) return;
    isPending.value = true;
    try {
      const res = await fetchList({
        planVer,
        fromDate: fromDate.value.format("YYYY-MM-DD"),
        toDate:   toDate.value.format("YYYY-MM-DD"),
        statuses: statuses.value,
      });
      rows.value = res.data ?? [];
    } finally {
      isPending.value = false;
    }
  }

  return { rows, isPending, fromDate, toDate, statuses, statusSource, load };
}
```

### 2-2. Vue 파일

```vue
<!-- frontend/src/views/templates/pe/work-order/WorkOrder.vue -->
<template>
  <div class="work-order-page">
    <Controller
      :navigations="[t('text-menu-production'), t('text-work_order')]"
      :show-filter-button="true"
      :actions="[{ action: 'Search', click: onSearch, loading: isPending }]"
    >
      <template #filter>
        <DateInput v-model="fromDate" :label="t('text-from_date')" :width="130" />
        <DateInput v-model="toDate"   :label="t('text-to_date')"   :width="130" />
        <MultiSelect
          :label="t('text-status')"
          v-model="statuses"
          :items-source="statusSource"
          key-prop="value"
          display-prop="label"
          :use-select-all="true"
        />
      </template>
    </Controller>

    <ExtendFlexGrid
      style="width: 100%; height: 100%"
      :items-source="rows"
      :is-read-only="true"
      :loading="isPending"
      :empty-state="{ isLoading: isPending }"
      :use-tool-box="false"
    >
      <WjFlexGridColumn binding="work_order_id" :header="t('text-work_order_id')" :width="160" />
      <WjFlexGridColumn binding="item_id"       :header="t('text-item_id')"       :width="140" />
      <WjFlexGridColumn binding="due_date"      :header="t('text-due_date')"      :width="120" dataType="Date" format="yyyy-MM-dd" align="center" />
      <WjFlexGridColumn binding="qty"           :header="t('text-qty')"           :width="120" dataType="Number" format="n2" align="right" />
      <WjFlexGridColumn binding="status"        :header="t('text-status')"        :width="100" />
    </ExtendFlexGrid>
  </div>
</template>

<script setup lang="ts">
import { Controller, MultiSelect, DateInput } from "@vmscloud/moz-ui-components";
import { ExtendFlexGrid } from "@vmscloud/moz-wijmo-grid";
import { WjFlexGridColumn } from "@vmscloud/moz-wijmo-grid/wijmo.vue2.grid";
import { useTranslation } from "i18next-vue";
import { watch } from "vue";
import { useHostPlanCycle } from "@/composables/useHostStores";
import { useWorkOrder } from "./workOrder";

const { t } = useTranslation();
const { planVer } = useHostPlanCycle();
const { rows, isPending, fromDate, toDate, statuses, statusSource, load } = useWorkOrder();

watch(planVer, (v) => v && load(v), { immediate: true });
function onSearch() { load(planVer.value); }
</script>

<style scoped lang="scss">
.work-order-page { height: 100%; display: flex; flex-direction: column; }
</style>
```

### 2-3. i18n 키 추가

사용한 `text-*` 키가 `src/lang/{ko,en,jp,zh}.json` 에 없다면 추가하세요. 최소한 `ko.json` 은 채워야 한글 라벨이 표시됩니다.

```json
{
  "text-work_order_id": "작업 지시 번호",
  "text-from_date": "시작일",
  "text-to_date": "종료일",
  "text-status": "상태",
  "text-qty": "수량",
  "text-item_id": "제품 코드",
  "text-due_date": "납기일",
  "text-work_order": "작업 지시"
}
```

### 2-4. Dev 라우트

```ts
// frontend/src/router/index.ts
{
  path: "/ext/work-order",
  component: () => import("@/views/templates/pe/work-order/WorkOrder.vue"),
},
```

### 2-5. Host expose 등록

```ts
// frontend/src/expose.ts
export const viewRegistry = {
  // ...
  WorkOrder: () => withHostInit(
    import("@/views/templates/pe/work-order/WorkOrder.vue"),
  ),
};
```

### 2-6. 페이지 전용 컨텍스트 (CLAUDE.md)

페이지 폴더에 `CLAUDE.md` 를 두면 LLM 에이전트가 그 폴더를 작업할 때만 자동으로 읽습니다(lazy context loading). 한 페이지의 백엔드 파일은 `schemas/services/endpoints` 등으로 흩어져 있으므로, 흩어진 위치를 묶는 "지도" 역할을 합니다. **새 페이지마다 추가하세요.**

```markdown
<!-- frontend/src/views/templates/pe/work-order/CLAUDE.md -->
# 작업 지시 (WorkOrder)
> 이 폴더 작업 시 자동 로드되는 페이지 전용 컨텍스트.

## 개요
작업 지시(rpt_work_order) 테이블을 날짜 범위·상태로 필터해 그리드로 표시.

## 데이터 소스
- 종류: trino
- 테이블: `rpt_work_order` (plan_date 는 YYYYMMDD 문자열)

## API
- `POST /api/custom/backend/{project_id}/work-order/list`

## 관련 파일 (페이지가 걸쳐 있는 위치)
- 뷰: `WorkOrder.vue` / composable: `workOrder.ts`
- 스키마: `backend/app/schemas/work_order.py`
- 서비스·쿼리: `backend/app/services/work_order.py`, `work_order_queries.py`
- 엔드포인트: `backend/app/api/v1/endpoints/work_order.py` / 등록: `api/v1/api.py`

## 메모
- 상태 필터는 `_build_filter` 로 IN 절 생성. planVer 가드 필수.
```

## 3. 검증

1. 브라우저에서 `http://localhost:5300/ext/work-order` 오픈.
2. DevTools → Network: `POST /api/custom/backend/<pid>/work-order/list` 가 200·data 존재.
3. planVer 가 있을 때 자동으로 한 번 로드되고, `Search` 버튼으로 수동 재호출 가능.
4. 필터(상태)를 바꿔 요청 body 가 반영되는지 확인.

## 4. 커밋

```bash
git add backend/app/... frontend/src/views/.../work-order/ frontend/src/lang/*.json \
        frontend/src/router/index.ts frontend/src/expose.ts
# work-order/ 폴더에는 CLAUDE.md(페이지 전용 컨텍스트)도 함께 커밋됩니다.
git commit -m "feat: Work Order 화면 및 /work-order/list 엔드포인트 추가"
```

## 자주 놓치는 것

- `api.py`에 `include_router` 누락 → 404.
- `planVer` 준비 전 `load()` 호출 → 빈 필터로 조회돼 결과가 이상해 보임. `if (!planVer) return;` 가드 필수.
- SQL에서 `CAST(plan_date AS DATE)` 실행 실패 → `plan_date` 가 `YYYYMMDD` 문자열이면 문자열 비교로 바꾸세요. [07-data-sources](./07-data-sources.md#trino-타입-주의) 참조.
- 숫자 컬럼에 `format="n2"` 누락 → 소수점 표시 어긋남.
- 다국어 JSON 에 키 누락 → 템플릿에 `text-...` 키가 그대로 표시됨.

다음: [07-data-sources](./07-data-sources.md) 에서 PG/Trino/APS Host API를 언제 쓰는지 정리.
