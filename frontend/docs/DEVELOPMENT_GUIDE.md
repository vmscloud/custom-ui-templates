# 커스텀 확장앱 개발 가이드

이 문서는 커스텀 확장앱을 개발하기 위한 상세 가이드입니다.

## 개발 환경 설정

### 사전 요구사항

- Node.js 18+
- pnpm 8+
- GitHub Personal Access Token (`read:packages` 권한)

### 초기 설정

1. **NPM_TOKEN 환경변수 설정**

   ```bash
   # Windows (PowerShell)
   $env:NPM_TOKEN="your_github_token_here"

   # macOS/Linux
   export NPM_TOKEN="your_github_token_here"
   ```

2. **의존성 설치**

   ```bash
   pnpm install
   ```

3. **개발 서버 시작**

   ```bash
   pnpm dev
   ```

## 개발 워크플로우

### 독립 개발 모드

일상적인 개발은 `pnpm dev`로 진행합니다:

```bash
pnpm dev
# http://localhost:5300 에서 확인
```

**특징**:
- HMR(Hot Module Replacement) 지원
- 빌드 없이 즉시 변경사항 반영
- APS 없이 독립적으로 개발 가능
- Host 데이터는 빈 값으로 동작 (정상)

### APS 통합 테스트

통합 테스트가 필요한 경우:

```bash
pnpm build
pnpm preview
```

APS 측에서 통합 테스트 환경을 제공받아야 합니다.

## 컴포넌트 개발

### 새 뷰 컴포넌트 생성

1. **파일 생성**

   ```
   src/views/customs/
   └── MyFeature/
       └── MyFeature.vue
   ```

2. **컴포넌트 작성**

   ```vue
   <template>
     <div class="my-feature">
       <h1>My Feature</h1>
       
       <!-- Host 데이터 사용 -->
       <div class="info">
         <p>프로젝트: {{ currentProject?.projectNM ?? '-' }}</p>
         <p>사용자: {{ userInfo?.name ?? '-' }}</p>
         <p>Plan Version: {{ planVer ?? '-' }}</p>
       </div>
       
       <!-- 비즈니스 로직 -->
       <div class="content">
         <!-- 커스텀 콘텐츠 -->
       </div>
     </div>
   </template>

   <script setup lang="ts">
   import { ref, onMounted } from 'vue';
   import { useHostStores } from '@/composables/useHostStores';

   // Host 스토어 접근
   const hostStores = useHostStores();
   const { planVer, fromDate, toDate } = hostStores.planCycle;
   const { currentProject, userInfo, isAdmin } = hostStores.projectInfo;

   // 컴포넌트 로직
   const data = ref([]);

   onMounted(async () => {
     // 초기화 로직
   });
   </script>

   <style scoped lang="scss">
   .my-feature {
     padding: 1.5rem;
     height: 100%;
     overflow: auto;

     h1 {
       font-size: 1.75rem;
       margin-bottom: 1rem;
     }

     .info {
       background: #f9fafb;
       padding: 1rem;
       border-radius: 0.5rem;
       margin-bottom: 1.5rem;
     }
   }
   </style>
   ```

3. **viewRegistry에 등록**

   ```typescript
   // src/expose.ts
   export const viewRegistry = {
     // 기존 뷰들...
     MyFeature: () => import('./views/customs/MyFeature/MyFeature.vue'),
   } as const;
   ```

## Host 데이터 사용

### useHostStores 컴포저블

Host(APS)에서 제공하는 데이터에 접근합니다.

```typescript
import { useHostStores } from '@/composables/useHostStores';

const hostStores = useHostStores();

// 구조 분해 할당으로 사용
const { planVer, fromDate, toDate } = hostStores.planCycle;
const { currentProjectID, currentProject, userInfo, isAdmin } = hostStores.projectInfo;
const { items, currentMenuId, currentMenu } = hostStores.menu;
```

### 사용 가능한 데이터

#### planCycle

| 필드 | 타입 | 설명 |
|------|------|------|
| `planVer` | `Ref<string>` | Plan Version |
| `fromDate` | `Ref<Dayjs \| null>` | 시작 날짜 |
| `toDate` | `Ref<Dayjs \| null>` | 종료 날짜 |

#### projectInfo

| 필드 | 타입 | 설명 |
|------|------|------|
| `currentProjectID` | `ComputedRef<string>` | 현재 프로젝트 ID |
| `currentProject` | `ComputedRef<Project \| null>` | 현재 프로젝트 정보 |
| `userInfo` | `ComputedRef<UserInfo \| null>` | 사용자 정보 |
| `isAdmin` | `ComputedRef<boolean>` | 관리자 여부 |

#### menu

| 필드 | 타입 | 설명 |
|------|------|------|
| `items` | `ComputedRef<MenuItem[]>` | 메뉴 목록 |
| `currentMenuId` | `ComputedRef<string>` | 현재 메뉴 ID |
| `currentMenu` | `ComputedRef<MenuItem \| null>` | 현재 메뉴 정보 |

### 헬퍼 함수

특정 데이터만 필요한 경우 헬퍼 함수를 사용합니다:

```typescript
import {
  useHostPlanCycle,
  useHostProjectInfo,
  useHostUser,
  isRunningInHost,
} from '@/composables/useHostStores';

// PlanCycle만 필요한 경우
const { planVer } = useHostPlanCycle();

// 사용자 정보만 필요한 경우
const { userInfo, isAdmin } = useHostUser();

// Host 환경 확인
if (isRunningInHost()) {
  console.log('APS에서 실행 중');
}
```

## API 호출

### 기본 설정

API 호출 시 APS의 프록시를 통해 백엔드에 접근합니다.

```typescript
// api/client.ts
const API_BASE = '/api';

export async function fetchItems(projectId: string) {
  const response = await fetch(`${API_BASE}/items?projectId=${projectId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch items');
  }
  return response.json();
}
```

### Vue Query 사용

```typescript
import { useQuery } from '@tanstack/vue-query';
import { useHostStores } from '@/composables/useHostStores';

const hostStores = useHostStores();
const { currentProjectID } = hostStores.projectInfo;

const { data, isLoading, error } = useQuery({
  queryKey: ['items', currentProjectID],
  queryFn: () => fetchItems(currentProjectID.value),
  enabled: computed(() => !!currentProjectID.value),
});
```

## 스타일링

### Scoped CSS

스타일 충돌을 방지하기 위해 항상 scoped CSS를 사용합니다:

```vue
<style scoped lang="scss">
.my-component {
  // 스타일
}
</style>
```

### CSS 변수 사용

APS의 테마와 일관성을 위해 CSS 변수를 활용합니다:

```scss
.my-component {
  color: var(--color-text-primary, #1f2937);
  background: var(--color-bg-secondary, #f9fafb);
  border: 1px solid var(--color-border, #e5e7eb);
}
```

### 공통 CSS 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `--color-text-primary` | `#1f2937` | 주요 텍스트 색상 |
| `--color-text-secondary` | `#6b7280` | 보조 텍스트 색상 |
| `--color-bg-primary` | `#ffffff` | 주요 배경 색상 |
| `--color-bg-secondary` | `#f9fafb` | 보조 배경 색상 |
| `--color-border` | `#e5e7eb` | 테두리 색상 |
| `--color-primary` | `#3b82f6` | 주요 강조 색상 |

## 빌드 및 테스트

### 빌드

```bash
pnpm build
```

빌드 결과물:
- `dist/assets/remoteEntry.js` - Module Federation 엔트리
- `dist/assets/__federation_expose_*.js` - 노출된 컴포넌트

### Preview 모드

```bash
pnpm preview
# http://localhost:5300 에서 빌드된 앱 확인
```

### 타입 체크

```bash
pnpm type-check
```

### 린트

```bash
pnpm lint
pnpm lint:fix  # 자동 수정
```

## 베스트 프랙티스

### 1. Host 데이터는 읽기 전용

```typescript
// 좋은 예
const { currentProject } = hostStores.projectInfo;
console.log(currentProject.value?.projectNM);

// 나쁜 예 - Host 데이터 수정 금지
// currentProject.value = { ... }; // ❌
```

### 2. 반응형 데이터 활용

```typescript
// Host 데이터는 reactive하므로 watch/computed 사용 가능
watch(planVer, (newVer) => {
  console.log('Plan Version 변경:', newVer);
  // 필요한 로직 실행
});

const formattedDate = computed(() => {
  return fromDate.value?.format('YYYY-MM-DD') ?? '-';
});
```

### 3. 에러 처리

```typescript
async function loadData() {
  try {
    const data = await fetchItems(currentProjectID.value);
    items.value = data;
  } catch (error) {
    console.error('데이터 로드 실패:', error);
    // 사용자에게 에러 표시
  }
}
```

### 4. 로딩 상태 관리

```typescript
const loading = ref(false);

async function handleAction() {
  loading.value = true;
  try {
    await performAction();
  } finally {
    loading.value = false;
  }
}
```

## 제한사항

### moz-component 사용 불가

현재 `@vmscloud/moz-component`는 커스텀 확장앱에서 사용할 수 없습니다.

**이유**: APS와 커스텀 확장앱 간의 패키지 충돌 문제

**대안**:
- 순수 Vue 컴포넌트로 UI 구현
- 외부 UI 라이브러리 사용 (단, 번들 크기 고려)
- 향후 커스텀 확장앱 전용 컴포넌트 라이브러리 제공 예정

### 전역 상태 공유 금지

커스텀 확장앱은 Host의 상태를 직접 수정할 수 없습니다.

```typescript
// ❌ 금지: Host 스토어 직접 수정
// hostStores.planCycle.planVer.value = 'new-version';

// ✅ 허용: 읽기만 가능
const ver = hostStores.planCycle.planVer.value;
```

## 문제 해결

### Host 데이터가 빈 값

**증상**: `useHostStores()`에서 모든 값이 빈 문자열/null

**원인**: 독립 개발 모드에서는 Host 데이터가 없음 (정상 동작)

**해결**: APS 통합 환경에서 테스트

### 컴포넌트가 로드되지 않음

**증상**: APS에서 `뷰 'MyFeature'를 찾을 수 없습니다` 오류

**해결**:
1. `expose.ts`의 `viewRegistry`에 등록 확인
2. 재빌드 후 preview 서버 재시작
3. URL의 뷰 이름 확인 (대소문자 구분)

### 스타일이 적용되지 않음

**해결**:
1. `<style scoped>` 사용 확인
2. CSS 변수가 정의되어 있는지 확인
3. 브라우저 개발자 도구에서 스타일 확인

### API 호출 실패

**해결**:
1. APS 프록시 설정 확인 (`/api` → 백엔드)
2. 네트워크 탭에서 요청 확인
3. CORS 설정 확인

