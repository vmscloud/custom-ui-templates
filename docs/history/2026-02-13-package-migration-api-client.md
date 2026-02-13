# 작업 이력: 패키지 마이그레이션 및 API 클라이언트 추가

- **날짜**: 2026-02-13
- **작업자**: Claude + 사용자
- **브랜치**: main

## 변경 요약

프론트엔드 의존성을 최신 버전으로 업데이트하고, ECharts/Wijmo Grid 직접 의존성을 `@vmscloud/moz-ui-chart` 및 `@vmscloud/moz-wijmo-grid` 패키지로 마이그레이션했습니다. 또한 공통 API 클라이언트 모듈과 프로젝트 ID 리졸버를 추가하여 API 호출 방식을 표준화했습니다.

## 변경 파일 목록

### 설정 파일

- `.claude/settings.local.json` - Claude 로컬 권한 및 MCP 서버 설정 업데이트
- `.claude/skills/*` - git-commit, git-merge-rebase, git-worktree 등 스킬 추가
- `.gitignore` - `nul` 항목 추가

### Frontend - 핵심 설정

- `frontend/package.json` - 의존성 버전 업데이트, grapecity/wijmo 제거, moz-ui-chart/moz-wijmo-grid 추가
- `frontend/pnpm-lock.yaml` - 락파일 업데이트
- `frontend/vite.config.ts` - ECharts shared/optimizeDeps를 moz-ui-chart로 변경, 프록시 포트 변경
- `frontend/src/bootstrap.ts` - ECharts import를 moz-ui-chart로 변경

### Frontend - API 클라이언트

- `frontend/src/api/client.ts` - (신규) Axios 래퍼 API 클라이언트 및 projectId 리졸버
- `frontend/src/App.vue` - MozConfigProvider 추가, projectId 리졸버 설정

### Frontend - 템플릿 컴포넌트

- `frontend/src/views/templates/chart/SalesChart.vue` - 차트 import를 moz-ui-chart로 변경
- `frontend/src/views/templates/grid/ProductGrid.vue` - 그리드 import를 moz-wijmo-grid로 변경
- `frontend/src/views/templates/dm/DemandDistribution.vue` - API 클라이언트 전환, projectId 직접 참조 제거, 코드 포맷팅
- `frontend/src/views/templates/dm/DemandDistributionSub.vue` - chart/grid import를 moz-ui-chart/moz-wijmo-grid로 변경
- `frontend/src/views/templates/dm/demandDistribution.ts` - axios → api 클라이언트, projectId 옵셔널 파라미터화
- `frontend/src/views/templates/basic/itemMaster.ts` - axios → api 클라이언트 전환
- `frontend/src/views/templates/basic/componentsShowcase.ts` - validator 타입 수정

## 상세 변경 내용

### 1. 패키지 마이그레이션

- `@grapecity/wijmo*` 직접 의존성 제거 → `@vmscloud/moz-wijmo-grid` 패키지로 대체
- `echarts`, `echarts-stat`, `arquero` 직접 의존성 제거 → `@vmscloud/moz-ui-chart` 패키지로 대체
- Vue 3.4 → 3.5, TypeScript 5.3 → 5.9, Vite 6.3 → 6.4 등 주요 의존성 최신화
- `@vmscloud/moz-ui-components` 1.0.17 → 1.2.3 업그레이드

### 2. API 클라이언트 모듈 추가

- Axios 래퍼 (`api.get`, `api.post`, `api.put`, `api.delete`) 제공
- 글로벌 `projectId` 리졸버 패턴 도입으로 컴포넌트에서 projectId 직접 관리 불필요
- `App.vue`에서 `setProjectIdResolver`로 초기 설정

### 3. ECharts/Wijmo 패키지 마이그레이션

- 모든 `echarts/*` import를 `@vmscloud/moz-ui-chart/echarts/*`로 변경
- 모든 `@grapecity/wijmo*` import를 `@vmscloud/moz-wijmo-grid/*`로 변경
- `vite.config.ts`의 Module Federation shared 및 optimizeDeps도 함께 업데이트

### 4. API 호출 리팩토링

- 각 API 호출에서 `axios` 직접 사용 → `api` 클라이언트 사용
- `projectId` 파라미터를 옵셔널로 변경, 기본값은 글로벌 리졸버에서 획득
- 컴포넌트에서 `useHostStores` 및 `watch(projectId)` 제거로 코드 간소화

## 테스트 방법

1. `pnpm install` 후 `pnpm dev`로 개발 서버 실행
2. 각 템플릿 페이지 (Components Showcase, Item Master, Sales Chart, Demand Distribution, Product Grid) 정상 렌더링 확인
3. API 호출이 올바른 URL로 전송되는지 확인

## 비고

- API 프록시 대상 포트가 8000 → 8099로 변경됨
- `MozConfigProvider`가 App.vue 최상위에 추가되어 한국어 로케일 제공
