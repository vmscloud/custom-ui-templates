# Custom UI Templates

Mozart Cloud APS(Host) 위에 얹히는 **커스텀 UI 리모트 앱**과 **전용 FastAPI 백엔드** 개발 템플릿입니다. Module Federation으로 APS와 통합되며, Host 없이도 단독으로 개발·테스트할 수 있습니다.

## 📖 시작은 여기부터 — [`docs/guide/`](./docs/guide/README.md)

이 저장소를 처음 만지는 개발자는 **반드시 [`docs/guide/README.md`](./docs/guide/README.md) 부터** 읽으세요. 새 페이지를 밑바닥부터 만들고 배포까지 이어가는 과정을 단계별(00~12)로 정리했습니다.

| # | 문서 | 내용 |
|---|------|------|
| 01 | [개요](./docs/guide/01-overview.md) | 무엇을 만드는가, 런타임 환경 |
| 02 | [환경 세팅](./docs/guide/02-environment-setup.md) | 로컬 dev 서버 기동, 포트, mock 모드 |
| 03 | [아키텍처](./docs/guide/03-architecture.md) | Host ↔ 프론트 리모트 ↔ FastAPI ↔ DB 흐름 |
| 06 | [새 페이지 만들기](./docs/guide/06-creating-a-page.md) | 화면 + API 완성 실전 절차 |
| 07 | [데이터 소스 선택](./docs/guide/07-data-sources.md) | PG / Trino / APS Host API |
| 12 | [MCP 서버](./docs/guide/12-mcp-servers.md) | 공개/내부 스코프, 내부 DB 노출 금지 |

> 전체 목차(04·05·08~11 포함)는 [`docs/guide/README.md`](./docs/guide/README.md) 참고.

## 빠른 시작

```powershell
# 사전 요구사항 점검 + 프론트/백엔드/MCP 툴 의존성 설치
make install

# 개발 서버 (터미널 2개)
make dev-backend    # FastAPI  :8000 (reload)
make dev-frontend   # Vite     :5300

# DB 없이 화면만 개발
make dev-mock
```

전체 명령은 `make help` 로 확인하세요. 환경 변수·토큰 셋업은 [02-환경 세팅](./docs/guide/02-environment-setup.md)을 따르세요.

## 저장소 구조

```
custom-ui-templates/
├── frontend/   ← Vue 3 + Vite (Module Federation remote, :5300)
├── backend/    ← FastAPI (:8000) — Trino/PostgreSQL 조회
├── docs/       ← ★ 개발자 가이드 (docs/guide), ADR, 아키텍처 다이어그램
├── tools/      ← MCP 런처·로컬 셋업 스크립트
└── Makefile    ← install / dev / build / mcp-local
```

## 그 외 문서

- [`docs/guide/13-deployment.md`](./docs/guide/13-deployment.md) — 배포 절차 · [`14-troubleshooting.md`](./docs/guide/14-troubleshooting.md) — 문제 해결
- [`docs/decisions/`](./docs/decisions/README.md) — 아키텍처 결정 기록(ADR)
- [`CLAUDE.md`](./CLAUDE.md) · [`AGENTS.md`](./AGENTS.md) — LLM 코딩 행동 지침
