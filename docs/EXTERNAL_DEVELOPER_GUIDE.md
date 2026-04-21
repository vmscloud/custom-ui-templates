# 외부 개발사를 위한 Custom Extension 개발 가이드

외부 개발사에서 APS(Advanced Planning & Scheduling)의 커스텀 확장을 개발하기 위한 기술 문서입니다. 이 가이드는 프로젝트 구조 이해부터 배포까지의 전체 개발 프로세스를 다룹니다.

---

## 목차

1. [기술 스택](#1-기술-스택)
2. [아키텍처 개요](#2-아키텍처-개요)
3. [Host-Remote 연결 구조](#3-host-remote-연결-구조)
4. [환경 설정](#4-환경-설정)
5. [개발 시작하기](#5-개발-시작하기)
6. [프로젝트 구조](#6-프로젝트-구조)
7. [주요 개발 패턴](#7-주요-개발-패턴)
8. [moz-ui-components 활용](#8-moz-ui-components-활용)
9. [Host 데이터 접근](#9-host-데이터-접근)
10. [API 통신](#10-api-통신)
11. [상태 관리](#11-상태-관리)
12. [배포 및 통합](#12-배포-및-통합)
13. [문제 해결](#13-문제-해결)
14. [모범 사례](#14-모범-사례)

---

## 1. 기술 스택

### Frontend
- **Vue**: 3.4.14 (Composition API 기반)
- **TypeScript**: 5.3.3 (정적 타입 검사)
- **Vite**: 6.3.3 (고속 빌드 도구)
- **Module Federation**: @originjs/vite-plugin-federation (Host-Remote 통합)
- **상태 관리**: Pinia 2.1.7 + pinia-plugin-persistedstate
- **서버 상태**: @tanstack/vue-query 5.28.13
- **UI 컴포넌트**: @vmscloud/moz-ui-components 1.0.17
- **차트**: ECharts 5.5.0, vue-echarts 7.0.3
- **그리드**: @grapecity/wijmo 5.20232.939 (선택적 peer dependency)
- **스타일**: Tailwind CSS 4.1+ (moz-ui-components에 포함)
- **국제화**: i18next 23.7.18, i18next-vue 3.0.0
- **라우팅**: Vue Router 4.2.5 (개발 모드용)

### Backend
- **프레임워크**: FastAPI (Python 웹 프레임워크)
- **데이터베이스**: PostgreSQL (psycopg2 연결)
- **유효성 검사**: Pydantic (데이터 검증)
- **서버**: uvicorn (ASGI 서버)
- **Python**: 3.11+

### 개발 환경
- **패키지 매니저**: pnpm (Node.js 패키지)
- **Node.js**: 18+
- **Docker**: 선택적 (로컬 개발 시에는 선택사항)

---

## 2. 아키텍처 개요

### 전체 시스템 구조

```
┌─────────────────────────────────────────────────────────┐
│                   APS (Host 앱)                         │
│                   Port: 8080                            │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │         RemoteLoader.vue                        │   │
│  │                                                 │   │
│  │  provide('hostData', {                          │   │
│  │    projectInfo,                                 │   │
│  │    planCycle,                                   │   │
│  │    menu                                         │   │
│  │  })                                             │   │
│  │         │                                       │   │
│  │         ▼                                       │   │
│  │  ┌───────────────────────────────────────────┐ │   │
│  │  │   Remote Component (커스텀 확장)          │ │   │
│  │  │   useHostStores() 사용                     │ │   │
│  │  └───────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                        │
        Module Federation (remoteEntry.js)
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│          Custom Extension App (Remote)                  │
│          Port: 5300                                     │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ expose.ts                                       │   │
│  │ - viewRegistry                                  │   │
│  │ - getView(name)                                 │   │
│  │ - getAvailableViews()                           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Vue Components                                  │   │
│  │ - ItemMaster.vue (CRUD 예제)                    │   │
│  │ - SalesChart.vue (차트 예제)                    │   │
│  │ - ProductGrid.vue (그리드 예제)                 │   │
│  │ - 커스텀 컴포넌트들...                          │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Pinia Stores / TanStack Query                   │   │
│  │ - 로컬 상태 관리                                │   │
│  │ - 서버 데이터 관리                              │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
                        │
                  API 요청 (Proxy)
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│          FastAPI Backend                               │
│          Port: 8000                                     │
│                                                         │
│  ├── /api/endpoint1                                     │
│  ├── /api/endpoint2                                     │
│  └── /api/endpoint3 → PostgreSQL                        │
└─────────────────────────────────────────────────────────┘
```

### Module Federation 개념

**Module Federation**은 런타임에 여러 개의 독립적인 웹 애플리케이션을 하나로 통합하는 기술입니다.

- **Host**: APS 메인 앱. Remote 앱을 동적으로 로드
- **Remote**: 커스텀 확장 앱. Host에 의해 로드됨
- **공유 의존성**: vue, pinia 등을 한 번만 로드하여 메모리 효율성 증대

---

## 3. Host-Remote 연결 구조

### Module Federation 설정 파일

#### Host 측 (APS) - vite.config.ts

```typescript
federation({
  name: 'aps_host',
  remotes: {
    external_app: '/ext/assets/remoteEntry.js',
  },
  shared: {
    vue: { singleton: true },
    pinia: { singleton: true },
    '@vmscloud/moz-ui-components': { singleton: true },
    '@tanstack/vue-query': { singleton: true },
  },
})
```

#### Remote 측 (Custom Extension App) - vite.config.ts

```typescript
federation({
  name: 'external_app',
  filename: 'remoteEntry.js',
  exposes: {
    './expose': './src/expose.ts',
  },
  shared: {
    vue: { singleton: true },
    pinia: { singleton: true },
    '@vmscloud/moz-ui-components': { singleton: true },
  },
})
```

### 데이터 흐름

```
Host에서 Remote 컴포넌트 로드
  ↓
RemoteLoader.vue에서 hostData computed 생성
  ↓
provide('hostData', hostData) 주입
  ↓
Remote 컴포넌트에서 inject('hostData') 또는 useHostStores() 사용
  ↓
Host 상태 (projectInfo, planCycle, menu) 접근 가능
```

### 공유 의존성 (Singleton)

| 패키지 | 버전 | 공유 이유 |
|--------|------|---------|
| vue | ^3.4.14 | 단일 Vue 인스턴스로 provide/inject 정상 작동 |
| pinia | ^2.1.7 | 동일한 스토어 인스턴스 공유 |
| @vmscloud/moz-ui-components | ^1.0.10 | UI 스타일, 컴포넌트 재사용 |
| echarts | ^5.0.0 | 차트 리소스 공유 |

**중요**: 공유 의존성의 버전이 Host와 일치하지 않으면 예상치 못한 에러가 발생할 수 있습니다.

---

## 4. 환경 설정

### 4.1 NPM 토큰 설정

`@vmscloud/moz-ui-components` 패키지는 GitHub Packages에 배포되어 있으므로 인증이 필요합니다.

#### 1단계: GitHub Personal Access Token 생성

1. GitHub 계정 로그인
2. Settings → Developer settings → Personal access tokens → Tokens (classic)
3. Generate new token
4. 권한 선택: `read:packages` (최소 권한)
5. 토큰 복사

#### 2단계: 토큰 주입 방식 선택

> ⚠️ **토큰은 절대 저장소에 커밋하지 마세요.**
> `frontend/.npmrc` 는 `.gitignore` 로 추적 제외되어 있고, 저장소에 커밋되는 파일은 placeholder 만 있는 `frontend/.npmrc.example` 뿐입니다.
> 실수로 푸시된 경우 즉시 해당 PAT 을 GitHub 에서 revoke 한 후 새로 발급하세요.

##### 옵션 A — `frontend/.npmrc` 파일 사용 (권장)

```bash
cd frontend
cp .npmrc.example .npmrc
# .npmrc 를 에디터로 열어 <SET_PAT_TOKEN> 부분을 방금 발급받은 ghp_... 토큰으로 교체
```

결과 파일:

```
@vmscloud:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=ghp_xxxxxxxxxxxxxxxxxxxxx
```

`pnpm install` 시 이 파일이 자동 적용됩니다.

##### 옵션 B — 환경 변수 `NPM_TOKEN`

**Windows (PowerShell)**:
```powershell
$env:NPM_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxx"
```

**macOS/Linux (Bash/Zsh)**:
```bash
export NPM_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxx"
```

개인 홈 디렉토리의 `~/.npmrc` 에 넣어도 동일하게 적용됩니다 (레포 루트 `.npmrc` 가 없을 때 fallback).

##### 옵션 C — Docker 빌드 시크릿 (CI/배포)

`deploy-custom-ui.ps1` 이 이미 `docker build --secret id=npm_token,src=<파일>` 형식으로 토큰을 주입합니다. 이 방식은 레이어 히스토리에 토큰이 남지 않아 가장 안전합니다.

### 4.2 의존성 설치

```bash
# pnpm 설치 (Windows, macOS, Linux 모두 동일)
npm install -g pnpm

# 저장소 폴더로 이동
cd custom-ui-templates/frontend

# 의존성 설치
pnpm install

# moz-ui-components 설치 확인
pnpm ls @vmscloud/moz-ui-components
```

### 4.3 환경 파일 설정

프로젝트 루트에 `.env` 파일 생성 (선택사항):

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_HOST_URL=http://localhost:8080
VITE_ENV=development
```

---

## 5. 개발 시작하기

### 5.1 독립 개발 모드 (Host 없이)

```bash
# 개발 서버 시작
pnpm dev

# 브라우저에서 접속
# http://localhost:5300
```

**특징**:
- 빠른 개발 사이클 (HMR 지원)
- Host 없이도 완전한 기능 개발 가능
- Host 데이터는 mock 데이터로 동작
- 독립적인 라우팅

### 5.2 Host와 통합 개발 (Advanced)

개발 완료 후 APS와 함께 테스트하려면:

1. **Backend API 준비**:
```bash
cd backend
pip install -e .
python -m uvicorn main:app --reload --port 8000
```

2. **Remote 앱 실행**:
```bash
pnpm dev
# http://localhost:5300
```

3. **Host 앱에서 확인**:
- APS 앱을 실행하고 `/ext/ItemMaster` 경로로 접속
- Module Federation으로 Remote 앱이 로드됨

### 5.3 프로덕션 빌드

```bash
# TypeScript 타입 검사
pnpm vue-tsc --noEmit

# 프로덕션 빌드
pnpm build

# 출력 결과
# dist/
# ├── assets/
# │   ├── remoteEntry.js (Module Federation 진입점)
# │   ├── main-xxxxx.js (메인 번들)
# │   └── *.css (스타일)
# └── index.html
```

---

## 6. 프로젝트 구조

### 디렉토리 레이아웃

```
custom-ui-templates/
├── frontend/                      # Vue 3 프런트엔드
│   ├── src/
│   │   ├── main.ts               # 개발용 진입점
│   │   ├── bootstrap.ts          # 앱 초기화 (Pinia, Vue Query)
│   │   ├── App.vue               # 개발용 Root 컴포넌트
│   │   ├── expose.ts             # Module Federation 노출 정의
│   │   │
│   │   ├── components/           # 공통 컴포넌트
│   │   │   └── DeveloperTool/    # 개발자 도구 (Host 연동 상태 확인)
│   │   │
│   │   ├── views/                # 페이지 컴포넌트
│   │   │   ├── HomeView.vue
│   │   │   └── templates/
│   │   │       ├── basic/
│   │   │       │   ├── ItemMaster.vue (CRUD 예제)
│   │   │       │   ├── HostInfo.vue (Host 데이터 표시)
│   │   │       │   └── ComponentsShowcase.vue
│   │   │       ├── chart/
│   │   │       │   └── SalesChart.vue (ECharts 예제)
│   │   │       ├── grid/
│   │   │       │   └── ProductGrid.vue (Wijmo 그리드 예제)
│   │   │       └── dm/
│   │   │           ├── DemandDistribution.vue
│   │   │           └── DemandDistributionSub.vue
│   │   │
│   │   ├── composables/          # 재사용 가능한 로직
│   │   │   ├── useHostStores.ts  # Host 스토어 접근
│   │   │   └── 기타 composables
│   │   │
│   │   ├── stores/               # Pinia 스토어 (로컬 상태)
│   │   │   └── mainStore.ts
│   │   │
│   │   ├── plugins/              # Vue 플러그인
│   │   │   └── i18n.ts           # 국제화 설정
│   │   │
│   │   ├── router/               # Vue Router (개발용)
│   │   │   └── index.ts
│   │   │
│   │   ├── types/                # TypeScript 타입 정의
│   │   │   ├── host.d.ts         # Host 관련 타입
│   │   │   └── moz-component.d.ts
│   │   │
│   │   └── assets/               # 정적 리소스
│   │       └── styles/
│   │
│   ├── public/                   # 공개 리소스
│   ├── vite.config.ts            # Vite 설정 (Module Federation)
│   ├── tsconfig.json             # TypeScript 설정
│   ├── package.json
│   └── README.md
│
├── backend/                       # FastAPI 백엔드
│   ├── src/
│   │   ├── main.py               # FastAPI 앱 진입점
│   │   ├── models/               # SQLAlchemy 모델
│   │   ├── schemas/              # Pydantic 스키마
│   │   ├── api/
│   │   │   ├── routers/          # API 라우트
│   │   │   └── deps.py
│   │   ├── services/             # 비즈니스 로직
│   │   ├── repositories/         # 데이터베이스 접근
│   │   ├── config.py             # 설정
│   │   └── db.py                 # 데이터베이스 연결
│   ├── pyproject.toml
│   ├── README.md
│   └── .env.example
│
└── docs/                          # 문서
    ├── EXTERNAL_DEVELOPER_GUIDE.md (현재 파일)
    ├── API.md
    ├── DEPLOYMENT.md
    └── TROUBLESHOOTING.md
```

### 주요 파일 설명

| 파일 | 설명 |
|------|------|
| `expose.ts` | Module Federation으로 Host에 노출할 컴포넌트 정의 |
| `useHostStores.ts` | Host의 상태(projectInfo, planCycle, menu)에 접근하는 composable |
| `bootstrap.ts` | Vue, Pinia, i18next 등 앱 초기화 |
| `ItemMaster.vue` | CRUD 화면 예제 (API 호출, 그리드 표시) |
| `HostInfo.vue` | Host 데이터 접근 예제 |
| `vite.config.ts` | Module Federation, API 프록시, 빌드 설정 |

---

## 7. 주요 개발 패턴

### 7.1 새 화면 추가

#### 1단계: Vue 컴포넌트 생성

`src/views/MyCustomView.vue`:
```vue
<template>
  <div class="my-custom-view">
    <h1>{{ t('my.custom.title') }}</h1>
    <!-- 컨텐츠 -->
  </div>
</template>

<script setup lang="ts">
import { useTranslation } from 'i18next-vue';
import { useHostProjectInfo } from '@/composables/useHostStores';

const { t } = useTranslation();
const projectInfo = useHostProjectInfo();

// 로직 작성
</script>

<style scoped lang="scss">
.my-custom-view {
  padding: 1.5rem;
  height: 100%;
  overflow: auto;
}
</style>
```

#### 2단계: expose.ts에 등록

`src/expose.ts`:
```typescript
export const viewRegistry = {
  ShowCase: () => import("./views/templates/basic/ComponentsShowcase.vue"),
  ItemMaster: () => import("./views/templates/basic/ItemMaster.vue"),
  MyCustomView: () => import("./views/MyCustomView.vue"), // 추가
} as const;

export type ViewName = keyof typeof viewRegistry;
```

#### 3단계: Host에서 접근

Host 앱의 라우팅 설정:
```typescript
// /ext/MyCustomView 경로로 접속
// RemoteLoader.vue가 자동으로 viewRegistry에서 찾아 로드
```

### 7.2 API 호출 패턴

#### useQuery (서버 상태 관리)

```typescript
import { useQuery } from '@tanstack/vue-query';
import axios from 'axios';
import { computed } from 'vue';

export function useItems() {
  const query = useQuery({
    queryKey: ['items'],
    queryFn: async () => {
      const response = await axios.get('/api/items');
      return response.data;
    },
    staleTime: 1000 * 60 * 5, // 5분
  });

  return {
    items: computed(() => query.data.value ?? []),
    isLoading: query.isPending,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
}
```

#### useMutation (데이터 변경)

```typescript
import { useMutation, useQueryClient } from '@tanstack/vue-query';
import axios from 'axios';

export function useCreateItem() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (data: CreateItemPayload) =>
      axios.post('/api/items', data),
    onSuccess: () => {
      // 캐시 무효화 (새 데이터 자동 조회)
      queryClient.invalidateQueries({ queryKey: ['items'] });
    },
    onError: (error) => {
      console.error('Item 생성 실패:', error);
    },
  });

  return {
    createItem: mutation.mutate,
    isLoading: mutation.isPending,
    isError: mutation.isError,
    error: mutation.error,
  };
}
```

### 7.3 Pinia 스토어 패턴

```typescript
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useQuery } from '@tanstack/vue-query';

export const useMyStore = defineStore('myStore', () => {
  // State
  const filters = ref({
    search: '',
    status: 'all',
  });

  const user = ref<User | null>(null);

  // Getters
  const hasFilter = computed(() => filters.value.search.length > 0);

  // Actions
  const setFilter = (key: string, value: any) => {
    filters.value[key] = value;
  };

  const loadUser = async (userId: string) => {
    // TanStack Query와 함께 사용
    const { data } = await useQuery({
      queryKey: ['user', userId],
      queryFn: () => fetch(`/api/users/${userId}`).then(r => r.json()),
    });
    user.value = data.value;
  };

  return {
    filters,
    user,
    hasFilter,
    setFilter,
    loadUser,
  };
}, {
  persist: true, // 로컬스토리지에 저장
});
```

---

## 8. moz-ui-components 활용

### 8.1 제공 컴포넌트

#### 폼 컴포넌트

```vue
<script setup lang="ts">
import {
  Button,
  Input,
  NumberInput,
  PasswordInput,
  Toggle,
  CheckBox,
  Radio,
  Select,
  MultiSelect,
  TextArea,
  TagInput,
  Slider,
} from '@vmscloud/moz-ui-components';
import { ref } from 'vue';

const name = ref('');
const email = ref('');
const age = ref(0);
const isActive = ref(true);
const role = ref('user');
const tags = ref(['tag1', 'tag2']);
</script>

<template>
  <div>
    <Input v-model="name" placeholder="이름 입력" />
    <Input v-model="email" type="email" placeholder="이메일" />
    <NumberInput v-model="age" min="0" max="100" />
    <Toggle v-model="isActive" label="활성화" />
    <Select v-model="role" :options="[
      { value: 'user', label: '사용자' },
      { value: 'admin', label: '관리자' },
    ]" />
    <TagInput v-model="tags" placeholder="태그 추가" />
    <Button @click="submit">저장</Button>
  </div>
</template>
```

#### 레이아웃 컴포넌트

```vue
<script setup lang="ts">
import { Popup, Tab, BreadCrumb } from '@vmscloud/moz-ui-components';
import { ref } from 'vue';

const activeTab = ref(0);
const isPopupOpen = ref(false);
</script>

<template>
  <div>
    <!-- 팝업 -->
    <Popup v-model="isPopupOpen" title="팝업 제목">
      <p>팝업 내용</p>
    </Popup>

    <!-- 탭 -->
    <Tab :tabs="['탭1', '탭2', '탭3']" v-model="activeTab">
      <template #content>
        <div v-if="activeTab === 0">탭 1 내용</div>
        <div v-else-if="activeTab === 1">탭 2 내용</div>
        <div v-else>탭 3 내용</div>
      </template>
    </Tab>

    <!-- 브레드크럼 -->
    <BreadCrumb :items="[
      { label: '홈', path: '/' },
      { label: '사용자', path: '/users' },
      { label: '프로필', path: '/users/profile' },
    ]" />
  </div>
</template>
```

### 8.2 유틸리티 함수

```typescript
import {
  cn,              // Tailwind 클래스 병합
  generateUUID,    // UUID 생성
  pxToRem,         // px → rem 변환
  dayjs,           // 날짜 처리
  debounce,        // 디바운스
  throttle,        // 쓰로틀
  useToast,        // 토스트 알림
  copyToClipboard, // 클립보드 복사
} from '@vmscloud/moz-ui-components';

// 예제
const id = generateUUID();           // '550e8400-e29b-41d4-a716-446655440000'
const className = cn('px-2', 'py-4'); // Tailwind 클래스 병합
const rem = pxToRem(16);             // 1rem
const date = dayjs().format('YYYY-MM-DD');

const { toast } = useToast();
toast('저장되었습니다', 'success');

// 디바운스된 검색 함수
const searchDebounced = debounce((query: string) => {
  console.log('검색:', query);
}, 300);
```

### 8.3 CSS 변수 시스템

moz-ui-components는 160개 이상의 CSS 변수를 제공하여 일관된 스타일링을 가능하게 합니다.

#### 색상 변수

```css
/* 기본 색상 */
--ui-color-accent-400: #4568e0;      /* 브랜드 주색 */
--ui-color-accent-400-hover: #3d5bc7;
--ui-color-accent-500: #3d4fc5;
--ui-color-accent-600: #333db3;

/* 배경 */
--ui-color-bg-0: #ffffff;            /* 흰색 배경 */
--ui-color-bg-1: #f5f5f5;
--ui-color-bg-2: #efefef;

/* 텍스트 */
--ui-color-text-700: #1a1a1a;        /* 진한 텍스트 */
--ui-color-text-600: #424242;
--ui-color-text-500: #666666;

/* 상태 */
--ui-color-success: #17a346;
--ui-color-warning: #ff9500;
--ui-color-error: #d32f2f;
--ui-color-info: #0277bd;
```

#### 크기 변수

```css
/* 간격 (padding, margin, gap) */
--ui-padding-4: 4px;
--ui-padding-8: 8px;
--ui-padding-12: 16px;
--ui-padding-16: 20px;

/* 둥글기 */
--ui-radius-small: 4px;
--ui-radius-medium: 8px;
--ui-radius-large: 12px;
```

#### 사용 예제

```vue
<style scoped lang="scss">
.card {
  background: var(--ui-color-bg-0);
  padding: var(--ui-padding-12);
  border-radius: var(--ui-radius-medium);
  border: 1px solid var(--ui-color-border-light);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-title {
  color: var(--ui-color-text-700);
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: var(--ui-padding-8);
}

.card-content {
  color: var(--ui-color-text-500);
  line-height: 1.5;
}

.button-primary {
  background: var(--ui-color-accent-400);
  color: white;

  &:hover {
    background: var(--ui-color-accent-400-hover);
  }
}
</style>
```

---

## 9. Host 데이터 접근

### 9.1 useHostStores 컴포저블

Host(APS)에서 주입되는 데이터에 접근하기 위한 공식 방법:

```typescript
import { useHostStores, isRunningInHost } from '@/composables/useHostStores';

export default {
  setup() {
    // Host 모드 확인
    const inHost = isRunningInHost(); // true/false

    // Host 스토어 접근
    const stores = useHostStores();

    // 각 섹션에 접근
    const { planVer, fromDate, toDate } = stores.planCycle;
    const { currentProjectID, currentProject, userInfo, isAdmin } = stores.projectInfo;
    const { items, currentMenuId, currentMenu } = stores.menu;

    return {
      planVer,
      currentProjectID,
      userInfo,
    };
  }
};
```

### 9.2 헬퍼 컴포저블

편의상 특정 데이터만 가져오는 헬퍼 제공:

```typescript
// Plan Cycle만 가져오기
import { useHostPlanCycle } from '@/composables/useHostStores';
const { planVer, fromDate, toDate } = useHostPlanCycle();

// 프로젝트 정보만 가져오기
import { useHostProjectInfo } from '@/composables/useHostStores';
const { currentProjectID, currentProject, userInfo, isAdmin } = useHostProjectInfo();

// 사용자 정보만 가져오기
import { useHostUser } from '@/composables/useHostStores';
const { userInfo, isAdmin } = useHostUser();
```

### 9.3 데이터 구조

#### PlanCycle

```typescript
interface PlanCycle {
  planVer: string;        // 계획 버전 (예: "20251103-P-TEST")
  fromDate: Dayjs;        // 계획 시작일
  toDate: Dayjs;          // 계획 종료일
}
```

#### ProjectInfo

```typescript
interface ProjectInfo {
  currentProjectID: string;  // 프로젝트 ID (UUID)
  currentProject: {
    projectID: string;
    projectNM: string;
    initMenuPath?: string;
    manualUrl?: string;
  } | null;
  userInfo: {
    id: string;
    name: string;
    email: string;
  } | null;
  isAdmin: boolean;          // 관리자 여부
}
```

#### Menu

```typescript
interface Menu {
  items: MenuItem[];         // 메뉴 아이템 배열
  currentMenuId: string;     // 현재 메뉴 ID
  currentMenu: MenuItem | null; // 현재 메뉴 정보
}

interface MenuItem {
  menuID: string;
  menuName: string;
  path: string;
  children?: MenuItem[];
}
```

### 9.4 실제 사용 예제

```vue
<template>
  <div class="host-info">
    <h2>사용자 정보</h2>
    <p>이름: {{ userInfo?.name }}</p>
    <p>이메일: {{ userInfo?.email }}</p>
    <p>관리자: {{ isAdmin ? '예' : '아니오' }}</p>

    <h2>프로젝트 정보</h2>
    <p>프로젝트 ID: {{ currentProjectID }}</p>
    <p>프로젝트명: {{ currentProject?.projectNM }}</p>

    <h2>Plan Cycle</h2>
    <p>버전: {{ planVer }}</p>
    <p>기간: {{ fromDate?.format('YYYY-MM-DD') }} ~ {{ toDate?.format('YYYY-MM-DD') }}</p>

    <!-- Host 모드가 아닌 경우 메시지 표시 -->
    <div v-if="!isHostMode" class="dev-notice">
      개발 모드에서 실행 중입니다. Host 앱에서 연동 시 실제 데이터가 표시됩니다.
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useHostStores, isRunningInHost } from '@/composables/useHostStores';

const stores = useHostStores();
const isHostMode = computed(() => isRunningInHost());

const { planVer, fromDate, toDate } = stores.planCycle;
const { currentProjectID, currentProject, userInfo, isAdmin } = stores.projectInfo;
</script>

<style scoped lang="scss">
.host-info {
  padding: 1.5rem;
}

h2 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  border-bottom: 1px solid var(--ui-color-border-light);
  padding-bottom: 0.5rem;
}

p {
  margin: 0.5rem 0;
  color: var(--ui-color-text-600);
}

.dev-notice {
  margin-top: 2rem;
  padding: 1rem;
  background: var(--ui-color-warning);
  color: white;
  border-radius: var(--ui-radius-medium);
}
</style>
```

---

## 10. API 통신

### 10.1 API 프록시 설정

개발 시 CORS 이슈를 해결하기 위해 Vite에서 API를 프록시합니다.

`vite.config.ts`:
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',  // FastAPI 서버
      changeOrigin: true,
      secure: false,
    },
  },
}
```

### 10.2 API 호출 방법

#### Axios 직접 호출

```typescript
import axios from 'axios';

// GET 요청
const fetchItems = async () => {
  try {
    const response = await axios.get('/api/items', {
      params: { page: 1, limit: 10 }
    });
    return response.data;
  } catch (error) {
    console.error('API 호출 실패:', error);
    throw error;
  }
};

// POST 요청
const createItem = async (data: ItemData) => {
  const response = await axios.post('/api/items', data);
  return response.data;
};

// PUT 요청 (수정)
const updateItem = async (id: string, data: Partial<ItemData>) => {
  const response = await axios.put(`/api/items/${id}`, data);
  return response.data;
};

// DELETE 요청
const deleteItem = async (id: string) => {
  await axios.delete(`/api/items/${id}`);
};
```

#### TanStack Query 사용 (권장)

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';

export function useItemList() {
  return useQuery({
    queryKey: ['items'],
    queryFn: async () => {
      const response = await axios.get('/api/items');
      return response.data;
    },
    staleTime: 1000 * 60 * 5, // 5분
  });
}

export function useCreateItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateItemPayload) =>
      axios.post('/api/items', data).then(r => r.data),
    onSuccess: () => {
      // 캐시 무효화
      queryClient.invalidateQueries({ queryKey: ['items'] });
    },
  });
}
```

### 10.3 API 응답 타입

#### 성공 응답

```typescript
interface ApiResponse<T> {
  code: 'success';
  message?: string;
  data: T;
  pagination?: {
    page: number;
    limit: number;
    total: number;
  };
}

// 예제
const response = await axios.get<ApiResponse<Item[]>>('/api/items');
const items = response.data.data;
```

#### 에러 응답

```typescript
interface ApiErrorResponse {
  code: 'error';
  message: string;
  errors?: Array<{
    field: string;
    message: string;
  }>;
}

// 에러 처리
try {
  await axios.post('/api/items', data);
} catch (error) {
  if (error.response?.data?.errors) {
    // 필드 레벨 에러 처리
    error.response.data.errors.forEach(err => {
      console.log(`${err.field}: ${err.message}`);
    });
  }
}
```

### 10.4 API 호출 예제 (ItemMaster)

```typescript
import { useQuery } from '@tanstack/vue-query';
import axios from 'axios';
import { ref } from 'vue';

export interface ItemMasterParams {
  projectId: string;
  planVer: string;
}

export interface ItemData {
  item_id: string;
  item_name: string;
  item_type: string;
  item_group_id: string;
  description: string;
  procurement_type: string;
  prod_type: string;
  item_spec: string;
  item_priority: number;
  create_user_id: string;
  update_datetime: string;
}

export function useItemMaster() {
  const data = ref<ItemData[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const count = ref(0);

  const loadData = async (params: ItemMasterParams) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.post<{
        data: ItemData[];
        total: number;
      }>('/api/items', params);

      data.value = response.data.data;
      count.value = response.data.total;
    } catch (err) {
      error.value = '데이터 조회 실패';
      data.value = [];
    } finally {
      loading.value = false;
    }
  };

  return {
    data: ref(data),
    loading: ref(loading),
    error: ref(error),
    count: ref(count),
    loadData,
  };
}
```

---

## 11. 상태 관리

### 11.1 Pinia를 사용한 전역 상태

```typescript
// stores/projectStore.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useProjectStore = defineStore('project', () => {
  // State
  const selectedFilters = ref({
    department: '',
    status: 'active',
  });

  const viewSettings = ref({
    columns: ['name', 'status', 'date'],
    pageSize: 20,
  });

  // Getters
  const isFiltered = computed(() =>
    selectedFilters.value.department !== ''
  );

  // Actions
  const setFilter = (key: string, value: any) => {
    selectedFilters.value[key] = value;
  };

  const resetFilters = () => {
    selectedFilters.value = {
      department: '',
      status: 'active',
    };
  };

  const updateViewSettings = (settings: Partial<typeof viewSettings.value>) => {
    viewSettings.value = { ...viewSettings.value, ...settings };
  };

  return {
    selectedFilters,
    viewSettings,
    isFiltered,
    setFilter,
    resetFilters,
    updateViewSettings,
  };
}, {
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'project_store',
        storage: localStorage,
        paths: ['viewSettings'], // viewSettings만 저장
      },
    ],
  },
});
```

### 11.2 Pinia 사용 예제

```vue
<template>
  <div class="filter-panel">
    <Select v-model="selectedFilters.department" />
    <Button @click="resetFilters">필터 초기화</Button>
    <span v-if="isFiltered">필터 적용 중</span>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useProjectStore } from '@/stores/projectStore';

const projectStore = useProjectStore();
const { selectedFilters, isFiltered } = storeToRefs(projectStore);
const { resetFilters } = projectStore;
</script>
```

### 11.2 TanStack Query를 사용한 서버 상태

```typescript
// composables/useItemMaster.ts
import { useQuery } from '@tanstack/vue-query';
import axios from 'axios';
import { ref } from 'vue';

export function useItemMaster() {
  const params = ref({ page: 1, limit: 20 });

  const query = useQuery({
    queryKey: ['items', params],
    queryFn: async () => {
      const response = await axios.get('/api/items', { params: params.value });
      return response.data;
    },
    staleTime: 1000 * 60 * 5, // 5분
    gcTime: 1000 * 60 * 10,   // 10분 (캐시 유지 시간)
  });

  return {
    items: computed(() => query.data.value?.data ?? []),
    isLoading: query.isPending,
    isError: query.isError,
    error: query.error,
    pageInfo: computed(() => query.data.value?.pagination),
    refetch: query.refetch,
    goToPage: (page: number) => {
      params.value.page = page;
      query.refetch();
    },
  };
}
```

---

## 12. 배포 및 통합

### 12.1 프로덕션 빌드

```bash
# 1단계: 타입 검사
pnpm vue-tsc --noEmit

# 2단계: 프로덕션 빌드
pnpm build

# 3단계: 빌드 결과 확인
ls -la dist/
# dist/
# ├── assets/
# │   ├── remoteEntry.js (Module Federation 진입점)
# │   ├── main-xxxxx.js
# │   └── style-xxxxx.css
# └── index.html
```

### 12.2 Docker를 사용한 배포

```dockerfile
# Dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

# Nginx 서빙
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html/ext
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 12.3 Nginx 설정

```nginx
# nginx.conf
server {
    listen 80;
    server_name _;

    location /ext {
        root /usr/share/nginx/html;
        try_files $uri /index.html;

        # Module Federation CORS 헤더
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Origin, Content-Type, Accept" always;

        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }

    # API 프록시
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 12.4 Host와 통합

#### 1단계: Remote 앱 배포

```bash
# 프로덕션 빌드
pnpm build

# Docker 이미지 빌드 및 배포
docker build -t custom-extension-app .
docker push your-registry/custom-extension-app:latest
```

#### 2단계: Host의 Module Federation 설정

Host 앱의 `vite.config.ts`에서 Remote URL 업데이트:

```typescript
federation({
  name: 'aps_host',
  remotes: {
    external_app: 'https://your-domain.com/ext/assets/remoteEntry.js',
  },
  // ...
})
```

#### 3단계: 환경 변수 설정

`.env.production`:
```env
VITE_API_BASE_URL=https://your-domain.com/api
VITE_HOST_URL=https://your-domain.com
```

### 12.5 배포 체크리스트

- [ ] 타입 검사 통과 (`pnpm vue-tsc --noEmit`)
- [ ] 프로덕션 빌드 성공 (`pnpm build`)
- [ ] `dist/assets/remoteEntry.js` 생성 확인
- [ ] CORS 헤더 설정 확인
- [ ] API 프록시 설정 확인
- [ ] 환경 변수 설정 확인
- [ ] HTTPS 활성화 (권장)
- [ ] 보안 헤더 설정 (X-Frame-Options, CSP 등)
- [ ] 성능 모니터링 설정

---

## 13. 문제 해결

### 13.1 의존성 관련 이슈

#### 문제: "@vmscloud/moz-ui-components not found"

```
원인: npm 토큰 미설정 또는 만료

해결:
1. .npmrc 파일 확인
2. 토큰 재생성 (GitHub Settings)
3. 캐시 초기화: pnpm store prune
4. 재설치: pnpm install
```

#### 문제: 버전 충돌

```
원인: vue, pinia 등 공유 라이브러리 버전 불일치

해결:
1. package.json에서 버전 확인
   - vue: ^3.4.14
   - pinia: ^2.1.7
2. Host 앱과 버전 일치하도록 수정
3. lock 파일 업데이트: pnpm install
```

### 13.2 Host 연동 이슈

#### 문제: Host 데이터가 undefined

```typescript
// 원인: Host 모드에서 실행되지 않음

// 진단
import { isRunningInHost } from '@/composables/useHostStores';
console.log('Host 모드:', isRunningInHost());

// 해결
// 1. APS 앱에서 Module Federation 설정 확인
// 2. /ext/ 경로로 접속 확인
// 3. RemoteLoader.vue에서 provide 확인
```

#### 문제: provide/inject 작동하지 않음

```
원인: 공유 라이브러리 버전 불일치로 Vue 인스턴스가 다름

해결:
1. Host와 Remote의 vue 버전 일치 확인
2. vite.config.ts에서 singleton: true 확인
3. 캐시 초기화: pnpm store prune
```

### 13.3 빌드 관련 이슈

#### 문제: Module Federation 빌드 실패

```
원인: exposes 설정 오류 또는 파일 경로 오류

해결:
1. vite.config.ts의 exposes 경로 확인
   - 상대 경로 확인 (./src/expose.ts)
2. expose.ts 파일 존재 확인
3. viewRegistry 구조 확인
```

#### 문제: remoteEntry.js 생성 안 됨

```bash
# 원인: Module Federation 플러그인 미설정

# 해결: vite.config.ts 확인
federation({
  name: 'external_app',
  filename: 'remoteEntry.js', // 필수
  exposes: {
    './expose': './src/expose.ts',
  },
  shared: { ... },
})
```

### 13.4 개발 서버 이슈

#### 문제: HMR이 작동하지 않음

```typescript
// vite.config.ts의 server 설정 확인
server: {
  hmr: {
    protocol: 'ws',
    host: 'localhost',
    port: 5300,
  },
}

// 방화벽 설정 확인 (포트 5300 개방)
```

#### 문제: API 프록시가 작동하지 않음

```
원인: 프록시 설정 오류 또는 백엔드 미실행

확인 사항:
1. Backend 서버 실행 확인
   python -m uvicorn main:app --reload --port 8000
2. vite.config.ts의 proxy 설정 확인
3. 브라우저 개발자 도구 Network 탭에서 요청 확인
```

### 13.5 런타임 에러

#### 문제: "Cannot read property 'value' of undefined"

```typescript
// 원인: useHostStores() 반환값이 undefined

// 진단 코드
const stores = useHostStores();
console.log('stores:', stores);
console.log('planCycle:', stores.planCycle);

// 해결: Host 모드 확인
if (isRunningInHost()) {
  // Host에서만 실행
} else {
  // 개발 모드에서는 기본값 설정
}
```

#### 문제: "TypeScript 타입 에러"

```bash
# 원인: TypeScript 설정 오류 또는 타입 정의 누락

# 해결
# 1. TypeScript 컴파일 확인
pnpm vue-tsc --noEmit

# 2. 타입 정의 파일 확인 (types/host.d.ts)

# 3. 타입 에러 수정
# - as any 사용 (비추천)
# - 타입 정의 추가 (권장)
```

---

## 14. 모범 사례

### 14.1 성능 최적화

#### 컴포넌트 지연 로딩

```typescript
import { defineAsyncComponent } from 'vue';

export const viewRegistry = {
  ItemMaster: () => import('./views/templates/basic/ItemMaster.vue'),
  SalesChart: defineAsyncComponent(() =>
    import('./views/templates/chart/SalesChart.vue')
  ),
} as const;
```

#### API 캐싱

```typescript
const query = useQuery({
  queryKey: ['items', params],
  queryFn: fetchItems,
  staleTime: 1000 * 60 * 5,  // 5분 동안 fresh 상태 유지
  gcTime: 1000 * 60 * 30,    // 30분 동안 캐시 유지
});
```

#### 큰 리스트 최적화

```vue
<template>
  <div class="virtual-list">
    <VirtualScroller
      :items="items"
      :item-height="50"
      class="scroller"
    >
      <template v-slot="{ item }">
        <ItemRow :item="item" />
      </template>
    </VirtualScroller>
  </div>
</template>

<script setup lang="ts">
import { VirtualScroller } from '@tanstack/vue-virtual';
</script>
```

### 14.2 코드 구조

#### Composable 분리

```typescript
// composables/useItemList.ts
export function useItemList() {
  const items = ref([]);
  const loading = ref(false);

  const loadItems = async () => {
    loading.value = true;
    items.value = await fetchItems();
    loading.value = false;
  };

  return { items, loading, loadItems };
}

// composables/useItemFilters.ts
export function useItemFilters() {
  const filters = reactive({
    search: '',
    status: 'all',
  });

  const filteredItems = computed(() => {
    // 필터링 로직
  });

  return { filters, filteredItems };
}
```

#### 컴포넌트 구성

```vue
<!-- 부모 컴포넌트 -->
<template>
  <div class="item-page">
    <ItemFilter :filters="filters" @update="updateFilters" />
    <ItemList :items="filteredItems" :loading="loading" />
  </div>
</template>

<!-- 자식 컴포넌트 -->
<ItemFilter :filters="filters" @update="updateFilters" />
<ItemList :items="filteredItems" />
```

### 14.3 에러 처리

#### 전역 에러 핸들러

```typescript
// plugins/errorHandler.ts
import { useToast } from '@vmscloud/moz-ui-components';

export function setupErrorHandler(app: App) {
  app.config.errorHandler = (err, instance, info) => {
    const { toast } = useToast();

    if (err instanceof Error) {
      toast(`오류: ${err.message}`, 'error');
      console.error('앱 에러:', err);
    }
  };
}
```

#### API 에러 처리

```typescript
try {
  const response = await axios.post('/api/items', data);
  return response.data;
} catch (error) {
  if (error.response?.status === 400) {
    // 입력 검증 에러
    throw new ValidationError(error.response.data.message);
  } else if (error.response?.status === 401) {
    // 인증 에러
    throw new AuthError('인증이 필요합니다.');
  } else if (error.response?.status === 500) {
    // 서버 에러
    throw new ServerError('서버 오류가 발생했습니다.');
  }
  throw error;
}
```

### 14.4 테스트

#### 컴포넌트 테스트

```typescript
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import ItemList from '@/views/ItemList.vue';

describe('ItemList.vue', () => {
  it('should render items', () => {
    const items = [
      { id: 1, name: 'Item 1' },
      { id: 2, name: 'Item 2' },
    ];

    const wrapper = mount(ItemList, {
      props: { items },
    });

    expect(wrapper.text()).toContain('Item 1');
    expect(wrapper.text()).toContain('Item 2');
  });

  it('should emit delete event', async () => {
    const wrapper = mount(ItemList, {
      props: { items: [{ id: 1, name: 'Item 1' }] },
    });

    await wrapper.find('.delete-btn').trigger('click');
    expect(wrapper.emitted('delete')).toBeTruthy();
  });
});
```

### 14.5 보안

#### 입력값 검증

```typescript
import { z } from 'zod';

const ItemSchema = z.object({
  name: z.string().min(1, '이름은 필수입니다'),
  email: z.string().email('유효한 이메일이 필요합니다'),
  age: z.number().min(0).max(150),
});

type Item = z.infer<typeof ItemSchema>;

const formData = { name: '', email: 'invalid', age: 200 };
const result = ItemSchema.safeParse(formData);

if (!result.success) {
  console.log(result.error.errors);
}
```

#### XSS 방지

```vue
<!-- 텍스트는 자동으로 이스케이프됨 -->
<div>{{ userInput }}</div>

<!-- HTML 렌더링이 필요한 경우만 v-html 사용 -->
<!-- ⚠️ 사용자 입력값은 절대 사용 금지 -->
<div v-html="sanitizedHTML"></div>

<!-- 대신 DOMPurify 라이브러리 사용 -->
<script setup lang="ts">
import DOMPurify from 'dompurify';

const sanitizedHTML = computed(() =>
  DOMPurify.sanitize(userGeneratedHTML.value)
);
</script>
```

#### CSRF 토큰

```typescript
// 서버에서 csrf 토큰 제공
axios.interceptors.request.use((config) => {
  const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
  if (token) {
    config.headers['X-CSRF-Token'] = token;
  }
  return config;
});
```

---

## 참고 자료

### 공식 문서
- [Vue 3 문서](https://vuejs.org)
- [Vite 문서](https://vitejs.dev)
- [Module Federation 가이드](https://webpack.js.org/concepts/module-federation/)
- [Pinia 문서](https://pinia.vuejs.org)
- [TanStack Query 문서](https://tanstack.com/query/latest)

### moz-ui-components
- 패키지: `@vmscloud/moz-ui-components`
- 버전: 1.0.17+
- 문서: [GitHub Repository]

### 추가 지원
문제 해결이나 기술 지원이 필요한 경우:
- GitHub Issues: [이슈 트래커 URL]
- 이메일: support@vmscloud.com
- 테크 지원: [지원 URL]

---

## 버전 정보

| 컴포넌트 | 버전 | 업데이트 | 설명 |
|---------|------|---------|------|
| Vue | 3.4.14 | 2025-01 | 안정 버전 |
| TypeScript | 5.3.3 | 2025-01 | 최신 타입 정의 |
| Vite | 6.3.3 | 2025-01 | 고성능 빌드 |
| Module Federation | 1.3.5 | 2024-12 | Host-Remote 통합 |
| moz-ui-components | 1.0.17 | 2025-01 | UI 라이브러리 |
| FastAPI | 0.123.5+ | 2025-01 | 백엔드 프레임워크 |

---

## 변경 이력

### v1.0.0 (2025-01-30)
- 초기 문서 작성
- 전체 개발 가이드 완성
- 예제 및 패턴 제시

---

© 2025 VMS Cloud. All rights reserved.

이 문서는 외부 개발사의 Custom Extension 개발을 위한 공식 가이드입니다.
