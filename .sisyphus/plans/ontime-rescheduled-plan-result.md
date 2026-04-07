# OnTimeRescheduledPlanResult 완전 이전 계획

## Context

APS "재수립계획 RTF 현황" 페이지를 custom-ui-templates로 완전 이전.
**기존 rtf-report API 재사용 불가** — 원본은 RPT_SHIPMENT_PLAN + OPE_EXEC_ACTUAL 2개 데이터소스를 병합하고 TypeQtyProcessor로 카테고리 분류하는 복잡한 in-memory 로직. 기존 API는 단순 query_id 프록시.

---

## Phase 1: 백엔드 — 재수립 RTF 핵심 엔진 (Python 포팅)

### 1-1. SQL 쿼리 모듈
**파일**: `backend/app/services/replan_rtf_queries.py`

Trino `execute_direct_query`용 SQL:

| 쿼리 | 테이블 | 용도 |
|------|--------|------|
| `SHIPMENT_PLAN_SQL` | `rpt_shipment_plan` | 출하계획 조회 (Main/Detail 공용) |
| `EXEC_ACTUAL_SQL` | `ope_exec_actual` + `odv_demand` | 실적 데이터 (cycle기간 내) |
| `PLAN_END_DATE_SQL` | `cfg_plan_config` | 계획 종료일 계산 |
| `PLAN_CONFIG_SQL` | `cfg_plan_config` | 계획 시작/종료/사이클 날짜 |
| `FINAL_ITEM_BUFFER_SQL` | `odv_report_std_buffer_config` | 최종품 버퍼 ID |
| `PROD_TYPES_SQL` | `rpt_shipment_plan` | prodType 필터 목록 |
| `PROD_DETAIL_SQL` | (기존 ProdDetail 로직) | 생산계획 피벗 |
| `SECTION_SQL` | (기존 Section 로직) | 기간 범위 |

### 1-2. TypeQtyProcessor (Python 포팅)
**파일**: `backend/app/services/replan_rtf_processor.py`

```python
class TypeQtyProcessor:
    """RTF 카테고리 분류 — 원본 C# TypeQtyProcessor 완전 포팅"""

    def __init__(self, settings: list[dict]):
        self._type_dict = self._build_type_dict(settings)

    def get_type(self, category: str, warehouse_status: str) -> str | None
    def get_act_status(self, plan_date, cycle_start, cycle_end, due_date) -> str

class ReplanRtfProcessor:
    """재수립 RTF 계산 — 원본 C# RarReplanRtfProcessor 완전 포팅"""

    def __init__(self, adapter, repo, settings):
        self.adapter = adapter
        self.repo = repo
        self.type_proc = TypeQtyProcessor(settings)

    async def get_summary(self, project_id, params) -> list[dict]:
        """GetMain 완전 포팅"""
        # 1. 계획 날짜 조회 (PG)
        # 2. 출하계획 조회 (Trino: rpt_shipment_plan)
        # 3. 계획 종료일 조회 (PG)
        # 4. DEMAND 모드 전처리 (LOT이 아닌 경우)
        # 5. 최종품 버퍼 ID 조회 (Trino)
        # 6. 실적 조회 (Trino: ope_exec_actual)
        # 7. 출하계획 메인 루프 — IsValidInfo + 카테고리 분류 + 집계
        # 8. 실적 병합 — AddActResult
        # 9. 정렬 + 반환

    async def get_detail(self, project_id, params) -> list[dict]:
        """GetDetail 완전 포팅 — 수요별 상세"""
        # 동일 데이터 소스, 키가 demandID

    async def get_prod_detail(self, project_id, params) -> dict:
        """ProdDetail — {detail, period} 복합 응답"""
```

핵심 로직:
- `IsValidInfo`: Remain 상태 필터링 (dueDate < cycleEnd 또는 actDemandList에 포함)
- `UpdateDemandInfo`: 수요별 short/upcoming 계산
- `UpdateRarRtfReport2`: earlyQty/onTimeQty/lateQty 누적
- `AddActResult`: 실적 데이터를 summary에 병합
- DEMAND 모드: demandDict으로 RTF 충족 여부 체크 (6자리/4자리 반올림)
- 비율 계산 차이: Summary는 Round, Detail은 Floor/Ceil

### 1-3. 스키마
**파일**: `backend/app/schemas/replan_rtf.py`

```python
class ReplanRtfMainRequest(BaseModel):
    planVer: str
    aggregateType: str = "MONTH"
    summary: str = "itemGroup"  # cust | itemGroup | prodType | region
    customers: list[str] = []
    itemGroupIDs: list[str] = []
    prodTypes: list[str] = []
    prodStatus: str | None = None  # on_time | late | short | early | null
    uomType: str = "DEFAULT"
    productionArea: str | None = None
    userId: str = ""

class ReplanRtfDetailRequest(ReplanRtfMainRequest):
    dueMonth: str | None = None
    dueWeek: str | None = None

class ReplanRtfProdDetailRequest(BaseModel):
    planVer: str
    demandID: str
    uomType: str = "DEFAULT"
```

### 1-4. 서비스
**파일**: `backend/app/services/replan_rtf.py`

`ReplanRtfService` — ReplanRtfProcessor 위임 + 위젯 설정 조회 통합

### 1-5. 엔드포인트
**파일**: `backend/app/api/v1/endpoints/replan_rtf.py`

| Method | Route | 기능 |
|--------|-------|------|
| POST | `/summary` | 요약 (기간/고객/품목/생산유형별) |
| POST | `/detail` | 상세 (수요별) |
| POST | `/prod-detail` | 생산계획 피벗 {detail, period} |
| GET | `/filters/prod-types` | 생산유형 목록 |

프리픽스: `/api/custom/backend/{project_id}/replan-rtf`

기존 rtf-report의 short, demand-info, peg-info, bom-map, item-props, demand-record는 **그대로 사용** (단일 쿼리 기반이라 호환 가능성 높음)

### 1-6. Freeze 엔드포인트
**파일**: `backend/app/api/v1/endpoints/freeze_plan.py`
**파일**: `backend/app/repositories/freeze_plan.py`

PostgreSQL 직접:
| Method | Route | SQL |
|--------|-------|-----|
| GET | `/freeze/status` | `SELECT * FROM cfg_plan_cycle_info WHERE project_id=%s AND plan_cycle_id=%s` |
| PUT | `/freeze/description` | `UPDATE cfg_plan_cycle_info SET frozen_desc=%s` |
| POST | `/freeze/execute` | `UPDATE cfg_plan_cycle_info SET frozen_plan_ver=..., status='close'` + `UPDATE sys_plan_ctrl SET plan_status='FROZEN'` |
| POST | `/freeze/cancel` | `UPDATE cfg_plan_cycle_info SET frozen_plan_ver='', status='open'` + `UPDATE sys_plan_ctrl SET plan_status='DONE'` |
| POST | `/freeze/period` | `SELECT cycle_start_date, cycle_end_date, ... FROM cfg_plan_cycle_info` |

### 1-7. 라우터 등록
`api.py`에 `replan_rtf`, `freeze_plan` 추가

---

## Phase 2: 프론트엔드 — 페이지 생성

### 2-1. 파일 구조

```
frontend/src/views/templates/sp/ontime-rescheduled-plan-result/
├── OnTimeRescheduledPlanResult.vue           ← 메인 (SplitPane 3패인)
├── onTimeRescheduledPlanResult.ts            ← API + composable
├── OnTimeRescheduledPlanResultSub1.vue       ← 요약 그리드 (ExtendFlexGrid)
├── OnTimeRescheduledPlanResultSub2.vue       ← 상세 그리드 (ExtendFlexGrid)
├── OnTimeRescheduledPlanResultDetail.vue     ← 생산계획 피벗 (ExtendPivotGrid)
└── OnTimeRescheduledPlanResultWidgetPop.vue  ← 위젯 설정 팝업
```

### 2-2. API 매핑

| 프론트 호출 | 백엔드 엔드포인트 |
|-----------|-----------------|
| Main (요약) | `POST /replan-rtf/summary` |
| Detail (상세) | `POST /replan-rtf/detail` |
| ProdDetail | `POST /replan-rtf/prod-detail` |
| GetProdTypes | `GET /replan-rtf/filters/prod-types` |
| Short | `POST /rtf-report/short` (기존 재사용) |
| BufferPlanTarget | `POST /rtf-report/buffer-plan-target` (기존) |
| DemandSummary | `POST /rtf-report/demand-summary` (기존) |
| DemandInfo | `POST /rtf-report/demand-info` (기존) |
| PegInfoDetail | `POST /rtf-report/peg-info` (기존) |
| BomMap | `POST /rtf-report/bom-map` (기존) |
| ItemProps | `POST /rtf-report/item-props` (기존) |
| DemandRecord | `POST /rtf-report/demand-record` (기존) |
| Widget 조회/저장 | `GET/PUT /plan-dashboard/settings` (기존) |
| Freeze 관련 | `/freeze/*` (신규) |
| 필터 (고객/품목) | `GET /rtf-report/filters/*` (기존) |

### 2-3. 컴포넌트 포팅 방침

원본 Vue 파일을 복사 후 수정:
- `apiCall()` → `api.post/get()` (우리 API 경로)
- `usePlanCycleStore()` → `useHostPlanCycle()`
- `useProjectInfoStore()` → `useHostUser()`
- `@moz-shared/icons` → 인라인 SVG 또는 assets
- `@moz-shared/utils` → `useHostNavigation()` + 로컬 유틸
- `useSearchParam` → 제거 (Host 환경에서 query param 동기화 불필요)
- TanStack Query → 직접 async/await (기존 composable 패턴)

---

## 구현 순서

```
1. BE: replan_rtf_queries.py — SQL 쿼리 정의
2. BE: replan_rtf_processor.py — TypeQtyProcessor + ReplanRtfProcessor 완전 포팅
3. BE: replan_rtf.py (스키마 + 서비스 + 엔드포인트)
4. BE: freeze_plan.py (레포 + 엔드포인트)
5. BE: 라우터 등록 + Swagger 테스트
   ── BE 완료 ──
6. FE: composable (onTimeRescheduledPlanResult.ts)
7. FE: 메인 Vue (Controller + SplitPane + Freeze UI)
8. FE: Sub1 (ExtendFlexGrid 요약)
9. FE: Sub2 (ExtendFlexGrid 상세)
10. FE: Detail (ExtendPivotGrid 피벗)
11. FE: WidgetPop (설정 팝업)
12. FE: expose + router 등록
```

---

## 리스크

1. **RPT_SHIPMENT_PLAN 테이블 스키마**: Trino에서 컬럼명/타입이 다를 수 있음 — 첫 쿼리 후 확인 필요
2. **OPE_EXEC_ACTUAL의 detail_json**: JSON 파싱이 Trino에서 `json_extract_scalar` 문법 사용
3. **DEMAND 모드 반올림**: 6자리/4자리 차이가 결과에 미묘한 영향 — 원본과 정확히 일치시켜야 함
4. **Freeze 트랜잭션**: cfg_plan_cycle_info + sys_plan_ctrl 동시 업데이트 — psycopg2 트랜잭션 사용

## 검증 방법

1. 동일 planVer로 원본 PlanDashboard와 우리 API 응답 비교
2. Freeze 실행 → cfg_plan_cycle_info 확인 → Cancel → 복원 확인
3. Host 통합 테스트: `/aps/ext/OnTimeRescheduledPlanResult`
