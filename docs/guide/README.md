# 개발자 가이드 (Custom UI Templates)

Mozart Cloud APS 위에 얹히는 **커스텀 UI 리모트 앱**과 **전용 FastAPI 백엔드**를 개발할 때 참고하는 문서입니다. 이 저장소를 처음 만지는 개발자가 **새 페이지를 밑바닥부터 만들고 배포까지 이어갈 수 있도록** 단계별로 구성했습니다.

## 읽는 순서

| # | 파일 | 내용 |
|---|------|------|
| 00 | [README.md](./README.md) | 이 문서 (목차) |
| 01 | [개요](./01-overview.md) | 이 저장소로 무엇을 만드는가, 런타임 환경 |
| 02 | [환경 세팅](./02-environment-setup.md) | 로컬 dev 서버 기동, 포트, mock 모드 |
| 03 | [아키텍처](./03-architecture.md) | Host ↔ 프론트 리모트 ↔ FastAPI ↔ DB 흐름 |
| 04 | [프론트엔드 가이드](./04-frontend-guide.md) | 폴더 관례·공용 훅·Module Federation·라우팅 |
| 05 | [백엔드 가이드](./05-backend-guide.md) | FastAPI 구조, 서비스·어댑터·SQL 템플릿 |
| 06 | [새 페이지 만들기](./06-creating-a-page.md) | 처음부터 하나의 화면 + API를 완성하는 실전 절차 |
| 07 | [데이터 소스 선택](./07-data-sources.md) | PG / Trino / APS Host API를 언제 어떻게 쓰나 |
| 08 | [UI 패턴](./08-ui-patterns.md) | Wijmo 그리드·Controller·팝업·필터 패턴 |
| 09 | [i18n · UOM · 날짜](./09-i18n-uom-datetime.md) | 번역, 수량 단위, Dayjs 규칙 |
| 10 | [디버깅 가이드](./10-debugging.md) | 로그·네트워크·응답 검증 팁 |
| 11 | [레퍼런스](./11-reference.md) | 공용 훅·아이콘·환경변수·경로 한 장 요약 |
| 12 | [MCP 서버](./12-mcp-servers.md) | 공개/내부 스코프 분리, DB MCP 노출 금지, 담당자 문의 |
| 13 | [배포 및 통합](./13-deployment.md) | Docker 빌드·사내 레지스트리 푸시·nginx 캐싱·호스트 통합 |
| 14 | [문제 해결](./14-troubleshooting.md) | 설치·빌드·호스트 통합 단계의 트러블슈팅 |

## 이 가이드가 전제로 하는 지식

- TypeScript / Vue 3 Composition API 기본 문법
- FastAPI, async/await, Pydantic v2
- 기본 SQL(PostgreSQL + Trino 공통 문법 수준)

## 반복 강조하는 원칙

1. **Host 값에 절대 섣불리 의존하지 않는다.** `planVer` 같은 주입 값은 `""` → 실제 값으로 바뀌는 타이밍이 존재합니다. 모든 API 호출에는 필요값 가드를 넣으세요.
2. **정밀도는 표시 단에서 맞춘다.** 숫자는 백엔드에서 원시 `double`을 그대로 내려주고, 화면은 Wijmo `format="n2"` 같은 포맷 지시로 반올림합니다.
3. **UTC 기준이 아닌 표시 기준의 날짜는 `Dayjs`로 통일.** `Date` 객체를 Wijmo 입력 컴포넌트에 넘기면 `.format`, `.add` 호출에서 런타임 에러가 납니다.
4. **i18n 키는 `t()` 로만.** `<template>` 이든 `<script>` 든 문자열 리터럴로 UI 라벨을 박지 않습니다.
5. **URL → localStorage → defaultValue 순의 "선호값 체인"을 재사용.** 대표 예가 `useQtyUomQuery`. 사용자 설정을 덧씌우는 방식으로 만들면 Host 통합과 일관됩니다.

## 한 눈에 보는 저장소 구조

```
custom-ui-templates/
├── frontend/                       ← Vue 3 + Vite (Module Federation remote)
│   └── src/
│       ├── main.ts                 ← dev 단독 진입
│       ├── expose.ts               ← ★ Host가 불러오는 뷰 레지스트리
│       ├── bootstrap.ts            ← Vue 앱 마운트
│       ├── router/index.ts         ← dev 라우트 (/ext/<path>)
│       ├── views/templates/        ← ★ 각 화면 (도메인별 폴더)
│       ├── composables/            ← useHostStores, useQtyUomQuery 등 공용 훅
│       ├── api/client.ts           ← axios + projectId 리졸버
│       ├── shims/moz-shared/       ← 공용 아이콘·유틸 shim
│       ├── lang/                   ← i18n 정적 JSON
│       └── plugins/i18n.ts         ← i18next 세팅
│
├── backend/                        ← FastAPI
│   └── app/
│       ├── main.py
│       ├── api/v1/
│       │   ├── api.py              ← ★ 라우터 통합
│       │   └── endpoints/          ← ★ 도메인별 엔드포인트
│       ├── services/               ← ★ 비즈니스 로직 + SQL
│       ├── schemas/                ← Pydantic 모델
│       ├── repositories/           ← PostgreSQL CRUD (선택)
│       ├── adapters/adapter.py     ← Trino query-executor 래퍼
│       └── core/
│           ├── config.py           ← 환경변수
│           ├── database.py         ← PG 연결 + execute_query
│           └── mock_*.py           ← mock 미들웨어
│
├── docs/guide/                     ← ← 이 가이드
└── deploy-custom-ui.ps1            ← 통합 빌드 스크립트
```
