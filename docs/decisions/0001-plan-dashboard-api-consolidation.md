# ADR-0001: PlanDashboard API를 ~30개에서 단일 집계 + 패널 리프레시로 통합

- **상태**: Accepted
- **결정일**: 2026-03-25 (소급 작성 2026-05-20)
- **관련**: `docs/history/2026-03-25-plan-dashboard-implementation.md`, [ADR-0002](./0002-dual-path-data-access.md)
- **코드**: `backend/app/api/v1/endpoints/plan_dashboard.py`, `backend/app/services/plan_dashboard.py`

## Context

PlanDashboard2(계획 대시보드)는 APS .NET 백엔드에서 custom-ui 백엔드(FastAPI)로 이전 대상이었다.
원본 .NET 구현은 위젯/패널 단위로 잘게 쪼개진 **약 30개 API**로 구성돼 있었고, 화면 1개를 그리려면
프론트가 다수의 호출을 순차/병렬로 오케스트레이션해야 했다. 이전 시 그대로 1:1 포팅하면:

- 한 화면(3×2 패널) 로드에 다수 왕복이 발생 — custom-ui ↔ FastAPI ↔ Query Executor ↔ Trino 경로가
  길어(ADR-0002) 왕복당 지연 비용이 크다.
- 패널 간 공유 입력(projectId, planVer, frozenVer, RTF 위젯 설정)을 호출마다 재계산/재조회.
- 프론트에 오케스트레이션 로직이 흩어져 화면-API 결합도가 높아진다.

## Decision

API를 **두 계층**으로 재설계한다.

1. **초기 1회 집계 호출** — `POST /dashboard` 하나가 전체 패널 데이터를 반환.
   서비스 계층에서 `asyncio.gather`로 패널별 조회를 **병렬 실행**한다
   (`backend/app/services/plan_dashboard.py`).
2. **패널 단위 리프레시 호출** — 사용자가 특정 패널의 입력만 바꿨을 때 그 패널만 다시 부른다:
   `/rtf-detail`, `/otd-summary`, `/res-group-report`, `/prod-report`.
3. **설정/메타 호출** — `GET·PUT /settings`, `GET /frozen-ver`.

엔드포인트 그룹은 코드에 주석 배너로 명시한다(메인 / 개별 패널 리프레시 / 위젯 설정 / Frozen Version).

## Alternatives

- **원본 ~30개 API 1:1 포팅** — 기각.
  포팅 비용은 낮지만 위 Context의 왕복·결합도 문제를 그대로 들여온다. 긴 데이터 경로(ADR-0002)와
  곱해지면 초기 로딩 지연이 누적된다.
- **단일 만능 엔드포인트 1개(모든 리프레시까지 포함)** — 기각.
  패널 일부만 갱신할 때도 전체를 재계산하게 되어 설정 변경 UX가 느려진다.
  "초기엔 한 방, 이후엔 패널 단위"라는 2계층 분리가 호출 수와 재계산량의 균형점이었다. *(재구성)*
- **GraphQL 도입** — 기각 *(재구성)*. 백엔드 전반이 FastAPI + 고정 패널 구조라 스키마/런타임 도입
  비용 대비 이득이 없다. 패널 구성이 정적이라 over-fetching 문제가 크지 않다.

## Consequences

**긍정**
- 화면 진입 시 호출이 1회로 수렴, 패널 병렬 조회로 초기 로딩 지연을 단축.
- 화면-API 계약이 패널 구조와 1:1로 단순해져 신규 패널 추가 영향 범위가 좁다.

**부정 / 부채**
- `/dashboard`가 **부분 실패에 취약**하다. `asyncio.gather` 중 한 패널 조회가 실패하면 전체 응답
  처리에 영향을 줄 수 있어, 패널별 부분 실패 격리 전략을 별도로 검토해야 한다.
- **드리프트 발생**: 원래 "30 → 7"로 통합했다고 기록(`docs/history/`)했으나, 이후 `/otd-summary`가
  추가되어 현재 **8개**다. dataType 변경 시 OTD만 단독 조회할 필요가 생긴 결과로, 2계층 설계가
  실제로 "패널 단위 리프레시"를 유도했음을 보여준다 — 즉 7이라는 숫자 자체는 목표가 아니었다.
- OTD(납기준수) 데이터는 별도 테이블(`rpt_buffer_plan`, `ope_exec_actual`)이 필요해 일부 패널은
  미완 상태로 남아 있다(`docs/history/` 비고 참조).
