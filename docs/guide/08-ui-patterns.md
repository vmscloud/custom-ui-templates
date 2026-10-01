# 08. UI 패턴

자주 반복되는 화면 구성 패턴을 모아둔 챕터입니다. 각 패턴은 `@vmscloud/moz-ui-components-vue` / `@vmscloud/moz-ui-grid-vue`(`MozGrid`) 사용을 전제로 합니다.

> `moz-ui-components-vue` 의 props 타입은 `any` 라 `vue-tsc` 가 prop 오류를 잡지 못합니다. 낯선 prop 은 `node_modules/@vmscloud/moz-ui-components-core/dist/components/<컴포넌트>/*.core.d.ts` 에서 확인하세요.

## 상단 필터 바 (Controller)

거의 모든 화면이 아래 구조를 따릅니다.

```vue
<Controller
  :navigations="['상위 메뉴', '현재 페이지']"
  :show-filter-button="true"
  :actions="[
    { action: 'Search', click: onSearch, loading: isPending }
  ]"
>
  <template #beforeFilter>
    <!-- 필터바 앞쪽 뱃지·상태 표시 영역 -->
  </template>

  <template #action>
    <!-- Search 외 추가 버튼 (팝업 열기 등) -->
    <Button :text="t('text-export')" @click="onExport">
      <template #icon><IconDownload /></template>
    </Button>
  </template>

  <template #filter>
    <!-- 실제 필터 폼 컴포넌트들 -->
    <Radio v-model="summaryType" ... />
    <MultiSelect v-model="operGroups" ... />
    <Select v-model="uomType" ... />
  </template>
</Controller>
```

## 그리드 (MozGrid)

컬럼은 템플릿 태그가 아니라 `coreConfig.fields` 배열로 선언합니다. 작성 기준 예제는 `frontend/src/views/templates/grid/ProductGrid.vue`.

```vue
<MozGrid
  name="my-page-grid"
  :coreConfig="coreConfig"
  height="100%"
  :loading="isPending"
  :useToolBox="true"
  @ready="onGridReady"
/>
```

```ts
import { MozGrid } from "@vmscloud/moz-ui-grid-vue";
import type { GridChrome, MozGridCoreProps, PureSheet } from "@vmscloud/moz-ui-grid-vue";

const coreConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: ["work_order_id"],
  data: rows.value,
  fields: [
    { id: "work_order_id", header: t("text-work_order_id"), dataType: "string", width: 160 },
    { id: "qty", header: t("text-qty"), dataType: "number", width: 120,
      mask: { type: "numeric", pattern: "#,##0.00" } },
    { id: "due_date", header: t("text-due_date"), dataType: "date", width: 120, align: "center",
      mask: { type: "date", pattern: "YYYY-MM-DD" } },

    // 동적 컬럼 (백엔드에서 메타데이터 내려줄 때)
    ...propColumns.value.map((col) => ({
      id: col.binding,
      header: col.header,
      dataType: col.dataType,
      width: col.width,
      align: col.align,
    })),
  ],
}));

// 코어 그리드(PureSheet)와 래퍼(GridChrome)를 받는다. 필터·선택·변경 추적은 grid 로 다룬다.
const grid = shallowRef<PureSheet | null>(null);
const onGridReady = (g: PureSheet, _chrome: GridChrome) => { grid.value = g; };
```

### 행 키 (`keyFields`)

MozGrid 는 `keyFields` 로 행을 식별하며 **키가 중복되면 오류를 냅니다.** 서버 데이터에 고유 키가 없으면 행 순번 키를 붙여 씁니다.

```ts
const coreConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: ["_rowKey"],
  data: rows.value.map((row, idx) => ({ ...row, _rowKey: idx })),
  fields: [ /* ... */ ],
}));
```

`new-rtf-report/adapters/utils.ts` 의 `withRowKey` · `ROW_KEY` 가 같은 일을 합니다.

### 포맷 규칙

숫자/날짜 포맷은 필드의 `mask` 로 지정합니다 (`format="n0"` 같은 문자열 포맷은 쓰지 않음).


| 타입     | 권장 mask                                                  |
| ------ | -------------------------------------------------------- |
| 정수     | `{ type: "numeric", pattern: "#,##0" }`                  |
| 소수 2자리 | `{ type: "numeric", pattern: "#,##0.00" }`               |
| 퍼센트    | `{ type: "function", formatter: (v) => ... }` 로 직접 변환    |
| 날짜     | `{ type: "date", pattern: "YYYY-MM-DD" }`                |
| 날짜+시간  | `{ type: "date", pattern: "YYYY-MM-DD HH:mm:ss" }`       |
| 그 외 규칙 | `{ type: "function", formatter: formatQty }`             |


**원칙**: 소수점 반올림은 그리드에서 작업하세요. 백엔드는 raw 숫자 그대로 내려주는 것이 누적 오차를 피하는 길입니다.

## 피벗 그리드 (MozGrid pivot 모드)

같은 `MozGrid` 에 `mode: "pivot"` 을 줍니다. `fields` 대신 `rowFields`·`columnFields`·`valueFields` 를 객체로 선언합니다.

```vue
<MozGrid
  name="my-page-pivot"
  :coreConfig="pivotConfig"
  height="100%"
  :loading="isPending"
  :useToolBox="false"
  @ready="onPivotReady"
  @cell:click="onPivotCellClick"
/>
```

```ts
const pivotConfig = computed<MozGridCoreProps>(() => ({
  mode: "pivot",
  data: pivotDataSource.value,
  rowFields: [
    { field: "oper_group_id", header: t("text-oper_group_id"), dataType: "string" },
    { field: "item_group_id", header: t("text-item_group_id"), dataType: "string" },
  ],
  columnFields: [
    { field: "month", header: t("text-month"), dataType: "string" },
    { field: "week",  header: t("text-week"),  dataType: "string" },
    { field: "date",  header: t("text-date"),  dataType: "string" },
  ],
  valueFields: [
    { field: "qty", header: t("text-sum"), dataType: "number", aggregate: "sum", align: "right",
      mask: { type: "numeric", pattern: "#,##0.00" } },
  ],
  showRowGrandTotals: dataState.showRowTotals,
  showColumnGrandTotals: dataState.showColumnTotals,
  showZeros: dataState.showZeros,
}));
```

셀 스타일은 `valueFields[].cellAttributes` 로 지정합니다. 실제 예는 `pe/re-execute-plan/ReExecutePlan.vue`, `dm/DemandDistributionSub.vue`.

## 팝업 (Popup)

```vue
<Popup
  :title="t('text-setting')"
  :width="reExecutePlanPopupWidth"
  :height="reExecutePlanPopupHeight"
  v-model:visible="visibleModel"
  :onConfirm="onConfirm"
  :onCancel="onCancel"
  class="my-popup"
>
  <div class="popup-content">
    <!-- 내용 -->
  </div>
</Popup>
```

- 부모에서 `v-model:visible` 바인딩. 팝업 내부에서 `emit('update:visible', false)` 로 닫기.
- 넓은 팝업(마법사류)은 `computed` 로 `window.innerWidth * 0.6` 같이 계산.

## Step/Tab 마법사 (팝업 내부)

```vue
<div class="step-indicator-wrapper">
  <div :class="{ 'step-item-wrapper': true, 'current-step': currentStep === 1 }" @click="currentStep = 1">
    <div class="icon">
      <IconDataCheck :size="'20'" :color="currentStep === 1 ? '#4568e0' : '#6a7184'" />
    </div>
    <div class="title">{{ t('text-step-data') }}</div>
  </div>
  <div class="step-item-line"></div>
  <div :class="{ 'step-item-wrapper': true, 'current-step': currentStep === 2 }" @click="currentStep = 2">
    <div class="icon">
      <IconResultCheck :size="'20'" :color="currentStep === 2 ? '#4568e0' : '#6a7184'" />
    </div>
    <div class="title">{{ t('text-step-execute') }}</div>
  </div>
</div>

<div v-show="currentStep === 1"> ... </div>
<div v-show="currentStep === 2"> ... </div>
```

## Split Pane (상·하 또는 좌·우 분할)

```vue
<SplitPane horizontal>
  <Pane size="60%" min-size="30%">
    <MozGrid :coreConfig="pivotConfig" ... />
  </Pane>
  <Pane size="40%" min-size="30%" :hidden="isZoomed">
    <MozGrid :coreConfig="gridConfig" ... />
  </Pane>
</SplitPane>
```

- `Pane` 을 숨길 때는 **`:hidden`** 을 씁니다. `SplitPane` 은 `Pane` 에 붙인 `v-show` 를 무시합니다.

## 빈 상태 / 로딩

```vue
<MozGrid
  :coreConfig="coreConfig"
  :loading="isPending"
  :emptyState="{ useImg: false, contentMsg: t('text-no_data') }"
/>
```

- `loading` 은 로딩 오버레이를 표시합니다.
- `emptyState` 는 행이 없을 때 표시되는 placeholder 의 문구·이미지를 바꿉니다. 지정하지 않으면 기본 문구·이미지가 나옵니다.

## 필터-그리드 연동 (피벗 셀 클릭 시 하단 그리드 필터링)

```ts
const selectedDemandList = shallowRef<string[]>([]);
const isPivotCellSelected = ref(false);
const demandGrid = shallowRef<PureSheet | null>(null);  // 하단 그리드 @ready 에서 저장

// 사용자가 건 컬럼 필터와 섞이지 않도록 별도 그룹 키로 건다.
const PIVOT_SELECTION_FILTER_KEY = "pivotSelection";

const applyDemandFilter = async () => {
  const grid = demandGrid.value;
  if (!grid) return;
  const ids = selectedDemandList.value;
  await grid.setFilterGroup(
    PIVOT_SELECTION_FILTER_KEY,
    isPivotCellSelected.value && ids.length
      ? {
          type: "values",
          priority: 0,
          applied: true,
          states: [{ id: "demand_id", operator: "in", filterValue: ids, sequence: 0 }],
        }
      : null,  // null 이면 그룹 해제
  );
};

const onPivotCellClick = (payload: unknown) => {
  const row = (payload as { row?: Record<string, any> } | undefined)?.row;
  if (!row || row.__pivotType !== "data") return;  // 데이터 셀만
  // 백엔드 응답의 TOTAL row 에 있는 demandIDs 를 꺼내 selectedDemandList 에 세팅
  ...
  isPivotCellSelected.value = true;
  applyDemandFilter();
};
```

핵심: **피벗 응답에 TOTAL 행 + demandIDs 를 함께 내려주는 구조**로 설계해두면 UI 연동이 깔끔. 백엔드 SQL 설계부터 `plan_type` 등 구분 컬럼을 추가해 생각해두는 게 좋습니다.

## Controller Action 버튼 중 Search 패턴

`actions` 배열의 `click` 함수는 **async 도 가능**합니다. `loading` 에 pending ref 를 연결해두면 자동으로 로딩 스피너가 버튼에 표시됩니다.

```ts
actions: [{
  action: 'Search',
  click: async () => {
    await onLoad();
    await loadDemandSource();
  },
  loading: isPageFetching,
}]
```

## 아이콘

- `shims/moz-shared/icons/index.ts` 에서 export 되는 아이콘 사용.
- 새 아이콘이 필요하면 SVG 컴포넌트를 추가하고 index에 export.

```ts
import { IconLineEdit, IconReExecute, IconDataCheck, IconResultCheck } from "@moz-shared/icons";
```

## 스타일 / 테마

- 화면 단위 `.vue` 파일에서 `<style scoped lang="scss">` 로 제한.
- 색상 토큰을 재사용하려면 `@vmscloud/moz-ui-components-core/styles/default` 가 정의하는 `--moz-color-*` 등 CSS 변수를 참조. 공유 스타일은 `frontend/src/styles/` 같은 별도 위치에 두는 패턴도 가능.

## 권장 폴더 구성 복습

```
views/templates/pe/my-page/
├─ MyPage.vue          ← 주 화면
├─ myPage.ts           ← composable (상태+fetch)
├─ MyPagePop.vue       ← 주 팝업
├─ MyPagePopSub1.vue   ← 팝업 내부 분할 섹션
└─ components/         ← 화면 전용 작은 컴포넌트
```

다음: [09-i18n-uom-datetime](./09-i18n-uom-datetime.md) 에서 번역·UOM·날짜 처리 규칙을 정리합니다.