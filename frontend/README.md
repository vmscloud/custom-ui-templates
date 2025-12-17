# External Dev App

외주 개발자를 위한 APS 확장 개발 템플릿입니다.

## 개요

이 프로젝트는 APS(Host) 앱의 확장 기능을 개발하기 위한 템플릿입니다.

**주요 특징**:

- ✅ **독립 개발 가능**: APS 없이도 `pnpm dev`로 모든 기능 개발 가능
- ✅ **Hot Module Replacement**: 코드 변경 시 즉시 반영
- ✅ **Host 스토어 연동**: APS의 상태(PlanCycle, 사용자 정보 등)에 접근 가능
- ✅ **Module Federation**: 개발 완료 후 APS와 통합하여 배포

**개발 워크플로우**:

1. 독립 개발 모드(`pnpm dev`)로 개발
2. APS 통합 테스트 환경에서 검증
3. 배포

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

독립적으로 개발을 시작합니다:

```bash
pnpm dev
```

개발 서버는 `http://localhost:5300`에서 실행되며, Hot Module Replacement(HMR)가 지원됩니다.

**개발 워크플로우**:

1. `pnpm dev`로 개발 서버 실행
2. `http://localhost:5300`에서 앱 확인
3. 코드 수정 시 자동으로 반영됨 (HMR)
4. 독립적으로 모든 기능 개발 및 테스트 가능

**독립 개발 모드의 특징**:

- ✅ 빠른 개발 사이클 (빌드 불필요)
- ✅ HMR로 즉시 변경사항 반영
- ✅ 독립적인 라우팅 및 상태 관리
- ✅ Host 스토어는 mock 데이터로 동작 (정상 동작)
- ✅ APS 없이 모든 기능 개발 가능

**개발 가능한 작업**:

- 컴포넌트 UI 개발
- 비즈니스 로직 개발
- 스타일링 작업
- 독립적인 기능 테스트
- `useHostStores()` 사용 패턴 연습 (mock 데이터로 동작)

### 4. APS 통합 테스트 (참고)

> **주의**: 외주 개발자는 APS 소스 코드에 접근할 수 없으므로, APS 측에서 통합 테스트 환경을 제공받아야 합니다.

**통합 테스트 전 준비사항**:

1. **외부 앱 빌드**

   ```bash
   pnpm build
   pnpm preview  # 포트 5300에서 실행
   ```

2. **APS 측에 요청할 사항**

   - APS에서 `VITE_ENABLE_EXTERNAL_APP=true` 환경변수 설정
   - Nginx 프록시 설정 (`/ext/` → 외부 앱 서버)
   - 통합 테스트 환경 제공

3. **테스트 확인**
   - `http://localhost:8080/aps/ext/CustomMenu1` 경로에서 컴포넌트 확인
   - Host 스토어 데이터가 정상적으로 표시되는지 확인

**참고**: 평소 개발은 `pnpm dev`로 진행하고, APS와 통합 테스트할 때만 빌드 모드를 사용합니다.

## 프로젝트 구조

```
src/
├── main.ts                 # 개발용 엔트리
├── bootstrap.ts            # 앱 부트스트랩 (Pinia, Vue Query 초기화)
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
├── stores/                 # Pinia 스토어 (독립 실행 모드용)
│   └── mainStore.ts        # ProjectInfo 스토어
└── types/
    ├── host.d.ts           # Host 타입 정의
    └── moz-component.d.ts   # moz-component 타입 정의
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
import { useHostStores } from "@/composables/useHostStores";

const hostStores = useHostStores();
const { planVer } = hostStores.planCycle;
const { currentProject } = hostStores.projectInfo;
</script>
```

### 3. expose.ts에 등록

`expose.ts` 파일에 컴포넌트를 직접 export하고, 필요시 `viewRegistry`에도 등록합니다:

```typescript
// src/expose.ts
// 직접 export (APS에서 사용)
export { default as MyNewMenu } from "./views/MyNewMenu/MyNewMenu.vue";

// viewRegistry (선택사항, 동적 로딩용)
export const viewRegistry = {
  // ... 기존 뷰
  MyNewMenu: () => import("./views/MyNewMenu/MyNewMenu.vue"),
};
```

**중요**: APS는 직접 export된 컴포넌트를 사용하므로, `export { default as MyNewMenu }`가 필수입니다.

### 4. vite.config.ts에 exposes 추가

```typescript
federation({
  // ...
  exposes: {
    // ... 기존 exposes
    "./MyNewMenu": "./src/views/MyNewMenu/MyNewMenu.vue",
  },
});
```

### 5. 개발 및 테스트

#### 독립 개발 모드

일반적인 개발은 `pnpm dev`로 진행합니다:

```bash
pnpm dev
# http://localhost:5300/custom-menu-1 (또는 해당 라우트)에서 확인
```

- HMR이 지원되어 코드 변경 시 즉시 반영됩니다
- 빌드 없이 빠르게 개발할 수 있습니다

#### APS 통합 테스트 (선택사항)

APS와 통합 테스트가 필요한 경우에만:

```bash
pnpm build
pnpm preview
```

> **참고**: APS 측에서 통합 테스트 환경을 제공받아야 하며, 평소 개발은 `pnpm dev`로 충분합니다.

## Host 스토어 사용

### useHostStores 컴포저블

Host(APS)에서 inject된 스토어에 접근합니다. 독립 개발 모드(`pnpm dev`)에서는 mock 데이터가 반환되며, APS 통합 환경에서는 실제 데이터가 제공됩니다.

```typescript
import { useHostStores } from "@/composables/useHostStores";

const hostStores = useHostStores();

// PlanCycle 정보
const { planVer, fromDate, toDate } = hostStores.planCycle;

// 프로젝트 정보
const { currentProjectID, currentProject, userInfo, isAdmin } =
  hostStores.projectInfo;

// 메뉴 정보
const { items, currentMenuId, currentMenu } = hostStores.menu;
```

**독립 개발 모드에서의 동작**:

- `useHostStores()`는 mock 데이터를 반환합니다 (정상 동작)
- APS 없이도 Host 스토어 사용 패턴을 연습할 수 있습니다
- 실제 데이터는 APS 통합 환경에서만 제공됩니다

### 헬퍼 함수

```typescript
import {
  useHostPlanCycle,
  useHostProjectInfo,
  useHostUser,
} from "@/composables/useHostStores";

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
import { SimpleGrid } from "@vmscloud/moz-component";
// 또는 개별 import
// import SimpleGrid from '@vmscloud/moz-component/dist/SimpleGrid';
</script>
```

## 빌드

```bash
pnpm build
```

빌드 결과물:

- `dist/assets/remoteEntry.js` - Module Federation 엔트리 파일
- `dist/assets/__federation_expose_*.js` - 노출된 컴포넌트 파일들
- `dist/assets/` - 기타 청크 파일들

## 배포

빌드된 `dist/` 폴더를 웹 서버에 배포합니다.

### Nginx 설정 예시

외부 앱을 `/ext/` 경로에서 제공하도록 설정:

```nginx
map $host $external_app_server {
    default "http://host.docker.internal:5300";
}

location /ext/ {
    resolver 127.0.0.11 8.8.8.8 8.8.4.4 valid=10s ipv6=off;

    # /ext/ 경로를 제거하고 외부 앱 서버로 프록시
    rewrite ^/ext/(.*)$ /$1 break;
    proxy_pass $external_app_server;

    proxy_http_version 1.1;
    proxy_set_header Host $proxy_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # CORS 헤더 (Module Federation 필수)
    add_header Access-Control-Allow-Origin * always;
    add_header Access-Control-Allow-Methods "GET, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Origin, Content-Type, Accept" always;

    # OPTIONS preflight 요청 처리
    if ($request_method = 'OPTIONS') {
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Origin, Content-Type, Accept" always;
        add_header Content-Length 0;
        add_header Content-Type text/plain;
        return 204;
    }
}
```

### 개발 환경 (Preview 모드)

개발 시에는 빌드 후 preview 서버를 실행합니다:

```bash
pnpm build
pnpm preview  # --host 옵션이 자동으로 포함됨
```

Preview 서버는 외부 접근을 허용하도록 `--host` 옵션으로 실행됩니다.

## 개발 시 주의사항

### 독립 개발 모드 (`pnpm dev`)

1. **빠른 개발 사이클**: `pnpm dev`로 개발하면 빌드 없이 즉시 변경사항 확인 가능

2. **Host 스토어 Mock 데이터**: 독립 개발 모드에서는 `useHostStores()`가 mock 데이터를 반환합니다 (정상 동작)

3. **컴포넌트 Export**: 새 컴포넌트를 추가할 때는 `expose.ts`에서 직접 export해야 합니다

   ```typescript
   export { default as MyNewMenu } from "./views/MyNewMenu/MyNewMenu.vue";
   ```

4. **스타일 충돌 주의**: scoped CSS 또는 고유한 클래스명 사용 권장

5. **전역 상태 변경 금지**: `useHostStores()`로 가져온 데이터는 읽기 전용으로만 사용

### APS 통합 관련

- **의존성 버전**: `vue`, `pinia`, `vue-router`, `@tanstack/vue-query`, `dayjs` 버전이 APS와 일치해야 함
- **통합 테스트**: APS 측에서 통합 테스트 환경을 제공받아야 하며, 이때만 `pnpm build && pnpm preview` 사용

## 문제 해결

### 독립 개발 모드 (`pnpm dev`) 관련

#### 컴포넌트를 찾을 수 없음

**증상**: `컴포넌트 'CustomMenu1'를 찾을 수 없습니다` 오류

**해결 방법**:

1. `expose.ts`에서 컴포넌트가 직접 export되었는지 확인:
   ```typescript
   export { default as CustomMenu1 } from "./views/CustomMenu1/CustomMenu1.vue";
   ```
2. `vite.config.ts`의 `exposes`에 등록되었는지 확인
3. 개발 서버 재시작 (`pnpm dev`)

#### Host 스토어가 mock 데이터만 반환됨

**증상**: `useHostStores()`에서 실제 데이터 대신 mock 데이터가 반환됨

**해결 방법**:

- ✅ **정상 동작입니다**: 독립 개발 모드(`pnpm dev`)에서는 mock 데이터가 반환됩니다
- 실제 Host 스토어 데이터는 APS 통합 환경에서만 제공됩니다
- 독립 개발 모드에서도 `useHostStores()` 사용 패턴을 연습할 수 있습니다

#### 스타일이 적용되지 않음

**해결 방법**:

- `@vmscloud/moz-component/style.css`가 import 되었는지 확인
- CSS 변수가 정의되어 있는지 확인
- scoped CSS 사용 시 클래스명 충돌 확인

#### 개발 서버가 시작되지 않음

**해결 방법**:

- 포트 5300이 이미 사용 중인지 확인
- `pnpm install`로 의존성이 모두 설치되었는지 확인
- 브라우저 캐시 삭제 후 재시도

### APS 통합 테스트 관련

> **참고**: 외주 개발자는 APS 소스 코드에 접근할 수 없으므로, 대부분의 문제는 APS 측에서 해결해야 합니다.

#### Module Federation 로딩 실패

**증상**: `Failed to fetch dynamically imported module` 오류

**확인 사항**:

1. 외부 앱이 빌드되어 실행 중인지 확인 (`pnpm build && pnpm preview`)
2. APS 측에 다음 사항 확인 요청:
   - `VITE_ENABLE_EXTERNAL_APP=true` 환경변수 설정
   - Nginx 프록시 설정 (`/ext/` → 외부 앱 서버)
   - CORS 헤더 설정

#### 404 페이지로 리다이렉트됨

**증상**: 외부 앱 컴포넌트가 로드되지만 곧바로 `/aps/404`로 리다이렉트됨

**해결 방법**: APS 측에서 `/ext/` 경로를 권한 체크에서 제외하도록 설정 요청
