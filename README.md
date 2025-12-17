# External Dev App

외주 개발자를 위한 APS 확장 개발 템플릿입니다.

## 개요

이 프로젝트는 Module Federation을 사용하여 APS(Host) 앱과 통합됩니다.
개발된 뷰 컴포넌트는 APS의 Main.vue 내에서 렌더링되며, APS의 상태(PlanCycle, 사용자 정보 등)에 접근할 수 있습니다.

## 시작하기

### 1. 환경 설정

#### NPM_TOKEN 설정

`@vmscloud/moz-component` 패키지 설치를 위해 GitHub Personal Access Token이 필요합니다.

1. GitHub → Settings → Developer settings → Personal access tokens
2. `read:packages` 권한이 있는 토큰 생성
3. 환경변수 설정:

```bash
# Windows (PowerShell)
$env:NPM_TOKEN="your_github_token_here"

# macOS/Linux
export NPM_TOKEN="your_github_token_here"
```

또는 `.env` 파일 생성:

```bash
cp env.example.txt .env
# .env 파일 편집하여 NPM_TOKEN 설정
```

### 2. 의존성 설치

```bash
pnpm install
```

### 3. 개발 서버 실행

```bash
pnpm dev
```

개발 서버는 `http://localhost:5300`에서 실행됩니다.

### 4. APS와 통합 테스트

1. APS 개발 서버 실행 (포트 5173)
2. External App 개발 서버 실행 (포트 5300)
3. APS에서 `/aps/ext/CustomMenu1` 경로로 접근

## 프로젝트 구조

```
src/
├── main.ts                 # 개발용 엔트리
├── bootstrap.ts            # 앱 부트스트랩
├── App.vue                 # 개발용 래퍼 컴포넌트
├── expose.ts               # Module Federation 노출 정의
├── router/                 # 개발용 라우터
├── views/                  # 뷰 컴포넌트 (메뉴)
│   ├── CustomMenu1/
│   │   └── CustomMenu1.vue
│   └── CustomMenu2/
│       └── CustomMenu2.vue
├── components/             # 공통 컴포넌트
├── composables/            # 컴포저블
│   └── useHostStores.ts    # Host 스토어 접근
└── types/
    └── host.d.ts           # Host 타입 정의
```

## 새 메뉴 추가 방법

### 1. 뷰 컴포넌트 생성

`src/views/` 폴더에 새 폴더와 Vue 파일을 생성합니다:

```bash
src/views/
└── MyNewMenu/
    └── MyNewMenu.vue
```

### 2. 뷰 컴포넌트 작성

```vue
<template>
  <div class="my-new-menu">
    <h1>My New Menu</h1>
    
    <!-- Host 정보 사용 예시 -->
    <p>프로젝트: {{ currentProject?.projectNM }}</p>
    <p>Plan Version: {{ planVer }}</p>
  </div>
</template>

<script setup lang="ts">
import { useHostStores } from '@/composables/useHostStores';

const hostStores = useHostStores();
const { planVer } = hostStores.planCycle;
const { currentProject } = hostStores.projectInfo;
</script>
```

### 3. expose.ts에 등록

```typescript
// src/expose.ts
export { default as MyNewMenu } from './views/MyNewMenu/MyNewMenu.vue';

export const viewRegistry = {
  // ... 기존 뷰
  MyNewMenu: () => import('./views/MyNewMenu/MyNewMenu.vue'),
};
```

### 4. vite.config.ts에 exposes 추가

```typescript
federation({
  // ...
  exposes: {
    // ... 기존 exposes
    './MyNewMenu': './src/views/MyNewMenu/MyNewMenu.vue',
  },
})
```

### 5. APS에서 접근

빌드 후 APS에서 `/aps/ext/MyNewMenu` 경로로 접근합니다.

## Host 스토어 사용

### useHostStores 컴포저블

Host(APS)에서 inject된 스토어에 접근합니다:

```typescript
import { useHostStores } from '@/composables/useHostStores';

const hostStores = useHostStores();

// PlanCycle 정보
const { planVer, fromDate, toDate } = hostStores.planCycle;

// 프로젝트 정보
const { currentProjectID, currentProject, userInfo, isAdmin } = hostStores.projectInfo;

// 메뉴 정보
const { items, currentMenuId, currentMenu } = hostStores.menu;
```

### 헬퍼 함수

```typescript
import { useHostPlanCycle, useHostProjectInfo, useHostUser } from '@/composables/useHostStores';

// PlanCycle만 필요한 경우
const { planVer, fromDate, toDate } = useHostPlanCycle();

// 프로젝트 정보만 필요한 경우
const { currentProjectID, currentProject } = useHostProjectInfo();

// 사용자 정보만 필요한 경우
const { userInfo, isAdmin } = useHostUser();
```

## moz-component 사용

`@vmscloud/moz-component` 라이브러리의 컴포넌트를 사용할 수 있습니다:

```vue
<template>
  <div>
    <!-- moz-component의 그리드 컴포넌트 사용 예시 -->
    <SimpleGrid :data="gridData" :columns="columns" />
  </div>
</template>

<script setup lang="ts">
// moz-component에서 import
import { SimpleGrid } from '@vmscloud/moz-component';
// 또는 개별 import
// import SimpleGrid from '@vmscloud/moz-component/dist/SimpleGrid';
</script>
```

## 빌드

```bash
pnpm build
```

빌드 결과물:
- `dist/remoteEntry.js` - Module Federation 엔트리
- `dist/assets/` - 청크 파일들

## 배포

빌드된 `dist/` 폴더를 웹 서버에 배포합니다.
Nginx 설정 예시:

```nginx
location /ext/ {
    alias /path/to/external-app/dist/;
    add_header Access-Control-Allow-Origin *;
}
```

## 개발 시 주의사항

1. **Vue, Pinia 버전 일치**: Host(APS)와 동일한 버전 사용 권장
2. **스타일 충돌 주의**: scoped CSS 또는 고유한 클래스명 사용
3. **전역 상태 변경 금지**: Host의 상태는 읽기 전용으로만 사용
4. **개발 모드 확인**: `window.__POWERED_BY_APS_HOST__`로 Host 환경 여부 확인

## 문제 해결

### Module Federation 로딩 실패

- 외부 앱 서버가 실행 중인지 확인
- CORS 설정 확인
- 브라우저 개발자 도구 Console에서 에러 확인

### 스타일이 적용되지 않음

- `@vmscloud/moz-component/style.css`가 import 되었는지 확인
- CSS 변수가 정의되어 있는지 확인

### Host 스토어 접근 불가

- 개발 모드에서는 mock 데이터가 반환됩니다
- Host 환경에서만 실제 스토어 데이터 접근 가능

