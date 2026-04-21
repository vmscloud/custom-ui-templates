# 04. 프론트엔드 가이드

## 진입점 파일 4개

| 파일 | 역할 |
|------|------|
| `src/main.ts` | **dev 단독 실행** 전용. `bootstrap()` 호출로 Vue 앱 마운트 |
| `src/bootstrap.ts` | Vue 생성·i18n·router·host inject 세팅 공용 로직 |
| `src/expose.ts` | **Module Federation** 에서 외부에 노출하는 viewRegistry |
| `src/router/index.ts` | dev 라우트 (`/ext/<path>` → Vue 컴포넌트) |

`expose.ts` 예:

```ts
export const viewRegistry = {
  MyPage: () => withHostInit(
    import("@/views/templates/pe/my-page/MyPage.vue"),
  ),
  // ...
};
```

- `withHostInit`: Host 주입값 준비 + `setProjectIdResolver()` 를 수행한 뒤 실제 Vue 컴포넌트를 반환하는 래퍼.
- Host 앱에서는 `viewRegistry["MyPage"]()` 를 호출해 비동기로 컴포넌트를 받아 자체 router 에 꽂습니다.

## 폴더 관례

```
src/views/templates/
├── basic/    ← 교육용 미니 예제
├── chart/    ← 차트 위주 화면
├── grid/     ← 그리드 위주 화면
├── dm/       ← 수요 관리 (Demand Management)
├── pe/       ← 계획 수립 (Planning Execution)
└── sp/       ← 스케줄링/리포트 (SP)
```

**한 페이지 = 한 폴더** 원칙.

```
pe/my-page/
├── MyPage.vue          ← 최상위 화면
├── MyPagePop.vue       ← (필요시) 팝업
└── myPage.ts           ← composable / fetch / 상태
```

화면이 단순해 `.vue` 내부 `<script setup>` 만으로도 충분하다면 composable 파일은 생략해도 됩니다. 화면이 조금이라도 복잡해지면 상태와 API 호출을 `myPage.ts` 로 빼는 것이 관리에 유리.

## 공용 유틸 빠른 둘러보기

### `api/client.ts`

```ts
import { api, getProjectId } from "@/api/client";

api.get<ResType>(
  `/api/custom/backend/${getProjectId()}/my-page/summary`,
);
api.post<ResType>(
  `/api/custom/backend/${getProjectId()}/my-page/main`,
  params,
);
```

- `api` 는 axios 인스턴스.
- `getProjectId()` 는 **Host 주입** 또는 **dev DeveloperTool** 이 세팅한 리졸버 결과를 반환.
- 개별 화면에서 별도 axios 인스턴스를 만들지 말고 이 `api` 만 사용.

### `composables/useHostStores.ts`

Host 가 `provide('hostData', ...)` 로 내려준 ref를 추상화한 훅들.

```ts
import {
  useHostData,        // 전체 ref
  useHostPlanCycle,   // { planVer, fromDate, toDate }
  useHostProjectInfo, // projectInfo ref
  useHostUser,        // { userInfo, isAdmin }
  useHostNavigation,  // { openLinkNewTab }
  isRunningInHost,    // window.__POWERED_BY_APS_HOST__ 체크
} from "@/composables/useHostStores";
```

**규칙**: `hostData` 는 시간차를 두고 채워집니다. Ref<string>이 `""` → 실제값으로 바뀌는 순간을 반드시 의식해 API 가드(`if (!planVer) return;`)를 넣으세요.

### `composables/useQtyUomQuery.ts`

수량 단위(UOM) 선호값 관리.

```ts
const { uomType, qtyUOMSource } = useQtyUomQuery(
  ["DEFAULT", "CONVERSION"],
  "DEFAULT",
  { menuID: "myPageUomType" },
);
```

- URL 쿼리(`?qtyUOM=...`) > localStorage > defaultValue 우선순위로 초기화.
- i18n 번역값 `text-default_uom`, `text-conversion_uom` 을 그대로 `displayValue` 에 매핑.
- 새 화면에서 UOM Select 를 쓸 때 이 훅을 재사용하면 Host URL 파라미터 자동 연동됩니다.

### `shims/moz-shared/icons`

UI에 쓰이는 공용 아이콘 SVG 컴포넌트 모음. 새 아이콘이 필요하면 `IconLineEdit.vue` 등을 참고해 같은 형식으로 추가하고 `index.ts` 에 export.

```ts
import { IconLineEdit, IconReExecute, IconDataCheck } from "@moz-shared/icons";
```

## API 호출 패턴

### 커스텀 백엔드 (권장)

```ts
// myPage.ts
import { api, getProjectId } from "@/api/client";

const BASE_URL = () => `/api/custom/backend/${getProjectId()}/my-page`;

export const fetchMain = (params: MyPageParams) =>
  api.post<MyPageResponse>(`${BASE_URL()}/main`, params);

export const fetchOptions = () =>
  api.get<{ data: Option[] }>(`${BASE_URL()}/options`);
```

### APS 표준 API (세션 필요)

```ts
export const fetchScenarioList = () =>
  api.get<any>(`/api/aps/backend/${getProjectId()}/PlmScenarioMaster`);
```

특수한 프록시 엔드포인트(`/api/custom/backend/<pid>/.../proxy/<route>`) 가 필요한 경우, `aps_proxy.py` 의 라우트 맵에 route 를 등록한 뒤 사용합니다.

## 상태 관리 규칙

이 저장소는 **Pinia 대신** Vue 기본 `ref/computed` + composable 패턴을 씁니다.

- 화면 전역 상태: `views/.../myPage.ts` 의 `useMyPage()` composable 안에 ref.
- Host 공유 상태: `useHostStores` 의 inject.
- 진짜 다중 화면 공유가 필요하면 `src/stores/` 아래에 얇게 추가하거나, Host 가 제공하는 값을 그대로 활용.

## 폼/필터 컴포넌트

`@vmscloud/moz-ui-components` 가 `Input`, `Select`, `MultiSelect`, `Radio`, `DateInput`, `TimePicker`, `NumberInput`, `Toggle`, `Controller`, `Popup`, `SplitPane`, `Pane`, `Button` 등을 제공합니다. 화면 상단 필터 영역은 `Controller` 래퍼를 쓰는 것이 공통 관례.

```vue
<Controller
  :navigations="['Menu', 'My Page']"
  :show-filter-button="true"
  :actions="[{ action: 'Search', click: onSearch, loading: isLoading }]"
>
  <template #filter>
    <Radio v-model="summaryType" :label="t('text-summary_type')" ... />
    <MultiSelect v-model="custParam" :items-source="custSource" ... />
    <Select v-model="uomType" :items-source="qtyUOMSource" display-prop="displayValue" />
  </template>
</Controller>
```

팝업은 `Popup` + `v-model:visible`. `width` 등은 props 로 조정. 자세한 패턴은 [08-ui-patterns](./08-ui-patterns.md).

## 그리드 (Wijmo)

- 일반 그리드: `@vmscloud/moz-wijmo-grid` 의 `ExtendFlexGrid`.
- 피벗 그리드: `ExtendPivotGrid`.
- 컬럼 정의: `WjFlexGridColumn`.
- 숫자 표시 포맷: `dataType="Number" format="n2"`.

**중요**: 숫자는 백엔드에서 raw `double`/`number`로 내려받고, 표시 단에서 `format="n2"` 같은 지시로 반올림하세요. 중간에 반올림이 섞이면 누적 오차로 값이 밀립니다.

## i18n

```ts
import { useTranslation } from "i18next-vue";
const { t } = useTranslation();
t("text-my_page_title");
```

`<template>` 에서는 `{{ t('text-my_page_title') }}`. 문자열 리터럴을 직접 박지 마세요. 키가 없으면 `src/lang/*.json` 네 개 파일 모두에 추가합니다. [09-i18n-uom-datetime](./09-i18n-uom-datetime.md) 참조.

## Dayjs 규칙

`DateInput`, `TimePicker` 는 `Dayjs` 객체를 v-model 로 받습니다. composable 에서 상태를 만들 때:

```ts
import dayjs, { type Dayjs } from "dayjs";

const state = ref<{ startDate: Dayjs }>({ startDate: dayjs() });
// 템플릿에서 state.value.startDate.format("YYYY-MM-DD") 사용 가능
```

`Date` 를 섞어 쓰면 `.format`, `.add` 호출 시 런타임 에러. 새 화면을 만들 때 처음부터 Dayjs로 통일.

## 체크리스트

새 프론트 화면마다 확인:

- [ ] `src/api/client.ts` 의 `api` + `getProjectId()` 로 HTTP 호출했는가
- [ ] host 값은 `useHostPlanCycle` 등으로 참조했는가
- [ ] `planVer` 등 host 주입값이 비어있는 동안 API 호출이 나가지 않도록 가드했는가
- [ ] UOM Select 가 있다면 `useQtyUomQuery` 로 만들었는가
- [ ] 숫자/날짜 컬럼의 포맷을 Wijmo 컬럼 속성에 맡겼는가
- [ ] i18n 키를 `t()` 로만 사용했는가 (4개 언어에 모두 추가했는가)
- [ ] `expose.ts` · `router/index.ts` 등록했는가
- [ ] `Dayjs` 와 `Date` 가 섞여 있지 않은가
