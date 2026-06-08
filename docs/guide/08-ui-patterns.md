# 08. UI 패턴

자주 반복되는 화면 구성 패턴을 모아둔 챕터입니다. 각 패턴은 `@vmscloud/moz-ui-components` / `@vmscloud/moz-wijmo-grid` 사용을 전제로 합니다.

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

## 그리드 (ExtendFlexGrid)

```vue
<ExtendFlexGrid
  style="width: 100%; height: 100%"
  :id="'my-page-grid-id'"
  :name="'my-page-grid'"
  :use-preset="true"
  :auto-generate-columns="false"
  :items-source="rows"
  :is-read-only="true"
  :loading="isPending"
  :empty-state="{ isLoading: isPending }"
  :use-tool-box="true"
  :is-tool-box-expanded="false"
>
  <WjFlexGridColumn binding="work_order_id"
                    :header="t('text-work_order_id')" :width="160" :is-required="true" />
  <WjFlexGridColumn binding="qty" :header="t('text-qty')" :width="120"
                    dataType="Number" format="n2" align="right" />
  <WjFlexGridColumn binding="due_date" :header="t('text-due_date')" :width="120"
                    dataType="Date" format="yyyy-MM-dd" align="center" />

  <!-- 동적 컬럼 (백엔드에서 메타데이터 내려줄 때) -->
  <WjFlexGridColumn
    v-for="col in propColumns"
    :key="col.binding"
    :binding="col.binding"
    :header="col.header"
    :dataType="col.dataType"
    :width="col.width"
    :align="col.align"
  />
</ExtendFlexGrid>
```

### 포맷 규칙


| 타입     | 권장 format             |
| ------ | --------------------- |
| 정수     | `n0`                  |
| 소수 2자리 | `n2`                  |
| 퍼센트    | `p2` (곱해서 100)        |
| 날짜     | `yyyy-MM-dd`          |
| 날짜+시간  | `yyyy-MM-dd HH:mm:ss` |


**원칙**: 소수점 반올림은 그리드에서 작업하세요. 백엔드는 raw 숫자 그대로 내려주는 것이 누적 오차를 피하는 길입니다.

## 피벗 그리드 (ExtendPivotGrid)

```vue
<ExtendPivotGrid
  :name="'my-page-pivot'"
  :id="'my-page-pivot-id'"
  :items-source="pivotDataSource"
  :engine-option="{
    fields,
    rowFields,
    columnFields,
    valueFields,
    showRowTotals: dataState.showRowTotals,
    showColumnTotals: dataState.showColumnTotals,
    showZeros: dataState.showZeros,
    totalsBeforeData: dataState.totalsBeforeData,
  }"
  :formatItem="pivotFormatItem"
  :loading="isPending"
  :empty-state="{ isLoading: isPending }"
  :use-pivot-chart="false"
  :use-tool-box="false"
/>
```

필드 정의:

```ts
const fields = computed(() => ([
  { binding: "oper_group_id", header: t("text-oper_group_id"), dataType: DataType.String, align: "left" },
  { binding: "item_group_id", header: t("text-item_group_id"), dataType: DataType.String, align: "left" },
  { binding: "date",          header: t("text-date"),          dataType: DataType.String, align: "left" },
  { binding: "qty",           header: t("text-sum"),           dataType: DataType.Number, align: "right", format: "n2" },
]));

const rowFields    = computed(() => [t("text-oper_group_id"), t("text-item_group_id")]);
const columnFields = ref([t("text-month"), t("text-week"), t("text-date")]);
const valueFields  = ref([t("text-sum")]);
```

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
    <ExtendPivotGrid ... />
  </Pane>
  <Pane size="40%" min-size="30%">
    <ExtendFlexGrid ... />
  </Pane>
</SplitPane>
```

## 빈 상태 / 로딩

```vue
<ExtendFlexGrid
  :items-source="rows"
  :loading="isPending"
  :empty-state="{ isLoading: isPending }"
/>
```

- `empty-state` 는 행이 없을 때 표시되는 placeholder를 관리합니다.
- 로딩 중에는 `isLoading: true` 로 스피너 상태.

## 필터-그리드 연동 (피벗 셀 클릭 시 하단 그리드 필터링)

```ts
const selectedDemandList = shallowRef<string[]>([]);
const isPivotCellSelected = ref(false);

const applyDemandFilter = () => {
  const cv = grid.value.collectionView;
  if (!isPivotCellSelected.value || !selectedDemandList.value.length) {
    cv.filter = null;
  } else {
    cv.filter = (item: any) => selectedDemandList.value.includes(item.demand_id);
  }
  cv.refresh();
};

const onPivotCellClick = (e: MouseEvent) => {
  const hit = pivot.value.hitTest(e);
  if (hit.cellType === 1) {  // 1 = data cell
    // 백엔드 응답의 TOTAL row 에 있는 demandIDs 를 꺼내 selectedDemandList 에 세팅
    ...
    isPivotCellSelected.value = true;
    applyDemandFilter();
  }
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
- 색상 토큰을 재사용하려면 `@vmscloud/moz-ui-components` 의 SCSS 변수/믹스인이 있는 경우 참조. 공유 스타일은 `frontend/src/styles/` 같은 별도 위치에 두는 패턴도 가능.

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