# 작업 이력: PlanDashboard2 완전 이전

- **날짜**: 2026-03-25
- **작업자**: Claude + 사용자
- **브랜치**: main

## 변경 요약

APS .NET 백엔드 + APS 프론트엔드의 PlanDashboard2(계획 대시보드)를 custom-ui-templates 프로젝트로 완전 이전.
기존 ~30개 API를 7개로 통합, 데이터 조회는 execute_direct_query(Trino raw SQL), 설정 저장은 psycopg2(PostgreSQL 직접) 사용.

## 변경 파일 목록

### Backend

- `backend/app/core/config.py` - Trino 설정 추가 (TRINO_CATALOG, TRINO_SCHEMA_APS)
- `backend/app/core/database.py` - execute_write() DML 함수 추가
- `backend/app/schemas/plan_dashboard.py` - 요청 스키마 (Dashboard, RtfDetail, ResGroup, Prod, Settings)
- `backend/app/services/plan_dashboard_queries.py` - Trino SQL 쿼리 상수 (RTF, OTD, PEG, RES 등)
- `backend/app/services/plan_dashboard.py` - RTFSummaryCreator + PlanDashboardService (asyncio.gather 병렬)
- `backend/app/repositories/plan_dashboard.py` - PostgreSQL 직접 접근 (frozen ver, 위젯설정 CRUD)
- `backend/app/api/v1/endpoints/plan_dashboard.py` - 7개 API 엔드포인트
- `backend/app/api/v1/api.py` - 라우터 등록
- `backend/app/api/v1/endpoints/rtf_report.py` - 보안 수정 (에러 응답에서 SQL 상세 숨김)

### Frontend

- `frontend/src/views/templates/sp/plan-dashboard/planDashboard.ts` - API 함수 + usePlanDashboard composable
- `frontend/src/views/templates/sp/plan-dashboard/PlanDashboard.vue` - 메인 뷰 (3x2 그리드)
- `frontend/src/views/templates/sp/plan-dashboard/components/PlanDashboardSub1.vue` - 당월 RTF 준수율 (ECharts 도넛)
- `frontend/src/views/templates/sp/plan-dashboard/components/PlanDashboardSub2.vue` - 실적 RTF (가로 막대)
- `frontend/src/views/templates/sp/plan-dashboard/components/PlanDashboardSub3.vue` - 재수립 RTF (가로 막대)
- `frontend/src/views/templates/sp/plan-dashboard/components/PlanDashboardSub4.vue` - 확정 vs 실적 (SimpleGrid)
- `frontend/src/views/templates/sp/plan-dashboard/components/PlanDashboardSub5.vue` - 공정그룹 가동률 (ECharts 세로 막대)
- `frontend/src/views/templates/sp/plan-dashboard/components/PlanDashboardSub6.vue` - 확정 vs 재수립 (SimpleGrid)
- `frontend/src/views/templates/sp/plan-dashboard/components/PlanDashboardSettings.vue` - 설정 팝업 (7탭, FlexGrid)
- `frontend/src/views/templates/sp/plan-dashboard/components/SimpleGrid.vue` - 셀 머지 + 드래그 선택 테이블
- `frontend/src/expose.ts` - viewRegistry, viewMeta에 PlanDashboard 등록
- `frontend/src/router/index.ts` - /plan-dashboard 라우트 추가
- `frontend/src/composables/useHostStores.ts` - useHostNavigation 추가 (openLinkNewTab)

### Host (APS)

- `packages/aps/src/components/remote/RemoteLoader.vue` - provide('hostNavigation') 추가

## 상세 변경 내용

### 1. 백엔드 API 통합 (30개 → 7개)

| 엔드포인트 | 설명 |
|-----------|------|
| POST /dashboard | 메인 대시보드 전체 데이터 (asyncio.gather 병렬) |
| POST /rtf-detail | RTF 세부 통계 드릴다운 |
| POST /res-group-report | 설비 가동 현황 리프레시 |
| POST /prod-report | 생산 현황 리프레시 |
| GET /settings | 위젯 설정 일괄 조회 |
| PUT /settings | 위젯 설정 저장 |
| GET /frozen-ver | Frozen 버전 조회 |

### 2. RTFSummaryCreator 포팅

- 동적 index name: `TOTAL_{LOT|DEMAND}_{PP|BP}_{EARLY|ONTIME|LATE|SHORT}_QTY`
- 위젯 설정 기반 LOT/DEMAND 모드 + 10개 설정 매트릭스
- 비율 계산: `late_ratio = rtf_ratio - ontime_ratio - early_ratio` (원본 동일)
- partition_key: `{project_id}@{planVer[:6]}` (원본 C# 로직 포팅)

### 3. 보안 수정

- DEBUG=False: 에러 응답에서 SQL/스택트레이스 숨김
- DEBUG=True: detail 필드로 상세 에러 제공
- 서버 로그에는 항상 full traceback 기록

### 4. Host 연동 (Module Federation)

- RemoteLoader.vue에 `provide('hostNavigation', { openLinkNewTab })` 추가
- Remote에서 inject로 받아 새 탭 열기 가능
- standalone fallback: window.open 직접 호출

### 5. 다국어 (i18n)

- 모든 하드코딩 한국어를 i18n 키로 교체
- Host 환경: APS 번역 리소스 공유로 한국어 표시
- Standalone: 키 이름 그대로 표시 (정상)

## 테스트 방법

1. BE: `http://localhost:18020/docs` → POST /plan-dashboard/dashboard
2. FE standalone: `http://localhost:5300/ext/plan-dashboard`
3. Host 통합: `http://localhost:8080/aps/ext/PlanDashboard`

## 비고

- OTD(납기준수) 데이터는 별도 테이블(rpt_buffer_plan, ope_exec_actual) 필요 — 향후 구현
- 공정그룹 가동률(operGroupCapa)은 해당 planVer에 OPER_GROUP 데이터가 없으면 빈 화면
