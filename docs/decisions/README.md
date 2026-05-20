# 아키텍처 결정 기록 (ADR)

`docs/history/`(작업 로그, "무엇을 했나")와 달리, 이 디렉터리는 **"왜 그렇게 결정했나"** 를 기록합니다.
설계상 트레이드오프가 있었던 결정만 ADR로 남깁니다. 단순 버그 수정·버전 동기화는 `docs/history/`에 둡니다.

## 작성 규칙

새 ADR은 `NNNN-kebab-title.md` 로 추가하고, 아래 4필드를 반드시 채웁니다.

| 필드 | 내용 |
|---|---|
| **Context** | 어떤 제약/문제 상황이었나 (왜 결정이 필요했나) |
| **Decision** | 무엇을 택했나 |
| **Alternatives** | 검토했지만 버린 것 + **버린 이유** |
| **Consequences** | 감수한 트레이드오프 / 남은 부채 |

상태값: `Proposed` → `Accepted` → (`Superseded by ADR-NNNN` / `Deprecated`).

## 목록

| # | 제목 | 상태 | 결정일 |
|---|------|------|--------|
| [0001](./0001-plan-dashboard-api-consolidation.md) | PlanDashboard API를 ~30개에서 단일 집계 + 패널 리프레시로 통합 | Accepted | 2026-03-25 |
| [0002](./0002-dual-path-data-access.md) | 데이터 접근 이원화: 분석 조회는 Query Executor(Iceberg), 설정은 Trino PG 카탈로그 | Accepted | 2026-03-25 |
| [0003](./0003-module-federation-host-init.md) | Module Federation 노출 + `withHostInit` 래퍼로 Host 초기화 주입 | Accepted | 2026-02-25 |

> ⚠️ 이 3건은 구현 이후 코드·`docs/history/`를 역추적해 **소급 작성**(2026-05-20)했습니다.
> 일부 "왜"는 당시 결정 맥락을 재구성한 것으로, 추정 부분은 본문에 *(재구성)* 으로 표시했습니다.
