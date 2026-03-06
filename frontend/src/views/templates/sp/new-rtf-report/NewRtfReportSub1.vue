<template>
  <ExtendFlexGrid
    :key="mainLoadParams.summary"
    :name="t(`${currentMenu.menuName}`) + '-sub1-Summary'"
    :id="`${currentMenu.menuName}-sub1-Summary-id`"
    :allowSorting="'None'"
    class="moz-readonly-grid rtf-report-sub1-grid"
    :style="{ width: parentsSummaryWidth, height: parentsSummaryHeight }"
    :itemsSource="summaryDataSource"
    :initialized="onInitialized"
    :selectionChanged="onSelectionChanged"
    :formatItem="formatItem"
    :isReadOnly="true"
    :setContextMenuProps="{
      useFlexGridSetting: true,
      useGroupColumn: false,
      useViewSelectColumn: true,
      useExportExcel: true,
      useFilter: true,
      onExportOriginalData: () =>
        downloadBigData({
          column_map: COLUMN_MAP,
          file_name: `${t(`${menuModule.currentMenu.menuName}`)}_${mainLoadParams.planVer}`,
          data_method: 'POST',
          data_parameter: JSON.stringify(mainLoadParams),
          api_key: mainApiKey,
        }),
    }"
    :use-tool-box="true"
    :isToolBoxExpanded="false"
    :loading="mainQuery.isFetching.value"
    :useSort="false"
    :use-preset="false"
  >
    <!-- v-if="mainLoadParams.summary === 'cust'" -->

    <WjFlexGridColumn
      binding="due"
      :header="groupingColumnHeader"
      aggregate="Cnt"
      :width="mainLoadParams.summary === 'due' ? 80 : 120"
      align="center"
      dataType="String"
    />
    <WjFlexGridColumn
      binding="custID"
      :header="t('text-cust_name')"
      :width="80"
      :visible="mainLoadParams.summary === 'cust'"
      align="center"
    />
    <WjFlexGridColumn
      binding="itemGroupID"
      :header="t('text-item_group')"
      :width="80"
      :visible="mainLoadParams.summary === 'itemGroup'"
      align="center"
    />
    <WjFlexGridColumn
      binding="region"
      :header="t('text-region')"
      :width="80"
      :visible="mainLoadParams.summary === 'region'"
      align="center"
    />
    <WjFlexGridColumn
      binding="demandType"
      :header="t('text-demand_type')"
      :width="80"
      :visible="mainLoadParams.summary === 'demandType'"
      align="center"
    />
    <WjFlexGridColumn binding="demandCnt" :header="t('text-demand_cnt')" aggregate="Sum" :width="80" />
    <WjFlexGridColumn
      binding="demandQty"
      :header="t('text-demand_qty')"
      dataType="Number"
      aggregate="Sum"
      :width="90"
      align="right"
      :format="projectModule.formatGrid('qty')"
    />
    <WjFlexGridColumn
      binding="rtfQty"
      :header="t('text-rtf_qty')"
      dataType="Number"
      aggregate="Sum"
      :width="90"
      align="right"
      :format="projectModule.formatGrid('qty')"
    />
    <WjFlexGridColumn
      binding="qtyUom"
      :header="t('text-qty_uom')"
      dataType="String"
      align="left"
      :width="90"
      :visible="false"
    />
    <WjFlexGridColumn
      binding="onTimeRatio"
      :header="t('text-on_time_ratio')"
      dataType="Number"
      aggregate="Avg"
      align="right"
      :width="90"
      :format="projectModule.formatGrid('ratio')"
    />
    <WjFlexGridColumn
      binding="onTimeQty"
      :header="t('text-on_time_qty')"
      dataType="Number"
      aggregate="Sum"
      align="right"
      :width="90"
      :visible="false"
      :format="projectModule.formatGrid('qty')"
    />
    <WjFlexGridColumn
      binding="lateRatio"
      :header="t('text-late_ratio')"
      dataType="Number"
      aggregate="Avg"
      align="right"
      :width="90"
      :format="projectModule.formatGrid('ratio')"
    />
    <WjFlexGridColumn
      binding="lateQty"
      :header="t('text-late_qty')"
      dataType="Number"
      aggregate="Sum"
      align="right"
      :width="90"
      :visible="false"
      :format="projectModule.formatGrid('qty')"
    />
    <WjFlexGridColumn
      binding="rtfRatio"
      :header="t('text-rtf_ratio')"
      dataType="Number"
      aggregate="Avg"
      align="right"
      :width="90"
      :format="projectModule.formatGrid('ratio')"
    />
  </ExtendFlexGrid>
</template>

<script setup lang="ts">
import { downloadBigData, useMenuStore } from './adapters/stores';
import { useProjectInfoStore } from './adapters/stores';
import { CollectionView } from '@vmscloud/moz-wijmo-grid/wijmo';
import { AllowMerging, CellRange, type FlexGrid, GroupRow } from '@vmscloud/moz-wijmo-grid/wijmo.grid';
import { WjFlexGridColumn } from '@vmscloud/moz-wijmo-grid/wijmo.vue2.grid';
import { ExtendFlexGrid, type ExtendGrid } from '@vmscloud/moz-wijmo-grid';
import { isDataCell } from '@vmscloud/moz-wijmo-grid/utils';
import { showMessage } from '@moz-shared/utils';
import { useQueryClient } from '@tanstack/vue-query';
import { useTranslation } from 'i18next-vue';
import { storeToRefs } from 'pinia';
import { computed, inject, nextTick, ref, shallowRef, toRaw, toRefs, watch } from 'vue';
import { IRtfReportQuery } from './NewRtfReport';

/**
 * props
 */
interface Props {
  parentsSummaryWidth?: string;
  parentsSummaryHeight?: string;
}
const props = defineProps<Props>();
const { parentsSummaryWidth, parentsSummaryHeight } = toRefs(props);

/**
 * DEFINE DEFAULT VARIABLE
 */
const queryClient = useQueryClient();
const projectModule = useProjectInfoStore();
const menuModule = useMenuStore();
const { currentMenu } = storeToRefs(menuModule);
const { selectedItem, mainQuery, refSub2, mainQueryKey, saveMainParams, mainLoadParams, mainApiKey } = inject(
  'useRtfReport',
) as IRtfReportQuery;
const { t } = useTranslation(); // 다국어
const summaryGrid = ref<FlexGrid>(); // Wijmo grid
const summaryExtendGrid = ref<ExtendGrid | null>(null); // Wijmo grid 확장 기능
const summaryDataSource = shallowRef<CollectionView>(new CollectionView([]));
const summaryTotalRowData = ref<any>();

/**
 * @todo 백엔드 API 스네이크 케이스로 받고 하드코딩된 로직 제거
 * 서버에서 받는 케이스가 안 맞아서 `excelModule.createColumnMapForExport(grid as FlexGrid)`으로 처리 불가능 함
 */
const COLUMN_MAP = {
  due: {
    column_name: mainLoadParams.value.aggregateType === 'MONTH' ? t('text-due_month') : t('text-due_week'),
    column_type: 'System.String',
    column_format: null,
  },
  cust_id: {
    column_name: t('text-cust_name'),
    column_type: 'System.String',
    column_format: null,
  },
  item_group_id: {
    column_name: t('text-item_group'),
    column_type: 'System.String',
    column_format: null,
  },
  region: {
    column_name: t('text-region'),
    column_type: 'System.String',
    column_format: null,
  },
  demand_type: {
    column_name: t('text-demand_type'),
    column_type: 'System.String',
    column_format: null,
  },
  demand_cnt: {
    column_name: t('text-demand_cnt'),
    column_type: 'System.Decimal',
    column_format: null,
  },
  demand_qty: {
    column_name: t('text-demand_qty'),
    column_type: 'System.Decimal',
    column_format: projectModule.formatGrid('qty'),
  },
  rtf_qty: {
    column_name: t('text-rtf_qty'),
    column_type: 'System.Decimal',
    column_format: projectModule.formatGrid('qty'),
  },
  on_time_ratio: {
    column_name: t('text-on_time_ratio'),
    column_type: 'System.Decimal',
    column_format: projectModule.formatGrid('ratio'),
  },
  on_time_qty: {
    column_name: t('text-on_time_qty'),
    column_type: 'System.Decimal',
    column_format: projectModule.formatGrid('qty'),
  },
  late_ratio: {
    column_name: t('text-late_ratio'),
    column_type: 'System.Decimal',
    column_format: projectModule.formatGrid('ratio'),
  },
  late_qty: {
    column_name: t('text-late_qty'),
    column_type: 'System.Decimal',
    column_format: projectModule.formatGrid('ratio'),
  },
  rtf_ratio: {
    column_name: t('text-rtf_ratio'),
    column_type: 'System.Decimal',
    column_format: projectModule.formatGrid('ratio'),
  },
};

const groupingColumnHeader = computed(() => {
  if (!isTempGroupColumnTitle.value) {
    if (mainLoadParams.value.summary === 'itemGroup') {
      return t('text-item_group');
    }

    if (mainLoadParams.value.summary === 'cust') {
      return t('text-customer');
    }

    if (mainLoadParams.value.summary === 'region') {
      return t('text-upper-region');
    }

    if (mainLoadParams.value.summary === 'demandType') {
      return t('text-demand_type');
    }
  }

  return mainLoadParams.value.aggregateType === 'MONTH' ? t('text-due_month') : t('text-due_week');
});
/**
 * INITIALIZE
 */
// GRID INITIALIZE
const onInitialized = (flexGrid: FlexGrid, _extendGrid: ExtendGrid) => {
  summaryGrid.value = flexGrid;
  summaryExtendGrid.value = _extendGrid;
  flexGrid.allowMerging = AllowMerging.Cells;

  const extraRow = new GroupRow();
  summaryGrid.value.columnFooters.rows.push(extraRow);
};

const isTempGroupColumnTitle = ref<boolean>(true);

const onLoad = async () => {
  isTempGroupColumnTitle.value = true;

  saveMainParams();
  const cache = queryClient.getQueryData(mainQueryKey);
  if (!cache) {
    await mainQuery.refetch();
  }

  if (mainQuery.isSuccess.value) {
    if (mainQuery.data.value?.length > 1) {
      const data = toRaw(mainQuery.data.value)
        .filter((item: any) => item.due !== '[SUB TOTAL]')
        .map((elem: any) => {
          switch (mainLoadParams.value.aggregateType) {
            case 'WEEK':
              return { ...elem, due: projectModule.convertToFormat('dateWeek', elem.due) };
            case 'MONTH':
              return { ...elem, due: projectModule.convertToFormat('dateMonth', elem.due) };
            default:
              return { ...elem };
          }
        });
      const totalRow = data.pop();

      switch (mainLoadParams.value.summary) {
        case 'due':
          summaryDataSource.value = new CollectionView(data);
          break;
        case 'cust':
          summaryDataSource.value = new CollectionView(data, {
            groupDescriptions: ['custID'],
          });
          break;
        case 'itemGroup':
          summaryDataSource.value = new CollectionView(data, {
            groupDescriptions: ['itemGroupID'],
          });
          break;
        case 'region':
          summaryDataSource.value = new CollectionView(data, {
            groupDescriptions: ['region'],
          });
          break;
        case 'demandType':
          summaryDataSource.value = new CollectionView(data, {
            groupDescriptions: ['demandType'],
          });
          break;
        default:
          break;
      }

      isTempGroupColumnTitle.value = false;

      await nextTick(() => {
        if (summaryGrid.value) {
          /**
           * RTF 현황(aps/sp/RtfReport)랑 일관적으로 접혀있는 것이 올바름
           * 펼치려면 0을 1로 변경하면 됨
           */
          summaryGrid.value.collapseGroupsToLevel(0);

          // 컬럼 visibility 설정
          const columns = summaryGrid.value.columns;

          // 모든 그룹핑 관련 컬럼을 먼저 숨김
          const custCol = columns.getColumn('custID');
          if (custCol) custCol.visible = false;

          const itemGroupCol = columns.getColumn('itemGroupID');
          if (itemGroupCol) itemGroupCol.visible = false;

          const regionCol = columns.getColumn('region');
          if (regionCol) regionCol.visible = false;

          const demandTypeCol = columns.getColumn('demandType');
          if (demandTypeCol) demandTypeCol.visible = false;
        }
      });

      summaryTotalRowData.value = totalRow;
    } else {
      summaryDataSource.value = new CollectionView([]);
    }
  } else if (mainQuery.isError.value) {
    showMessage(t('msg-toast-get_error'), false);
    summaryDataSource.value = new CollectionView([]);
  }
};

watch(summaryDataSource, (newSummaryDataSource) => {
  if (newSummaryDataSource?.items?.length) {
    nextTick(() => {
      if (summaryGrid.value) {
        summaryGrid.value.select(new CellRange(-1, -1), true);
        summaryGrid.value.select(new CellRange(0, 0, 0, 0), true);
      }

      // 그리드 초기화 (스키마 변경시 ExtendGrid 다시 초기화해줘야 text-ellipsis 적용됨)
      if (!summaryExtendGrid.value) return;
      summaryExtendGrid.value.refresh();
    });
  }
});
// endregion

/**
 * GRID EVENT
 */

const onSelectionChanged = (s: FlexGrid, e: any) => {
  const { row, col } = s.selection;
  if (row < 0 && col < 0) return;
  let dataItem;

  if (e.getRow() instanceof GroupRow) {
    const groupName = e.getRow()?.dataItem?.name;
    switch (mainLoadParams.value.summary) {
      case 'cust':
        dataItem = { due: '[SUB TOTAL]', custID: groupName };
        break;
      case 'demandType':
        dataItem = { due: '[SUB TOTAL]', demandType: groupName };
        break;
      case 'itemGroup':
        dataItem = { due: '[SUB TOTAL]', itemGroupID: groupName };
        break;
      case 'region':
        dataItem = { due: '[SUB TOTAL]', region: groupName };
        break;
      default:
        break;
    }
  } else {
    dataItem = e.getRow()?.dataItem;
  }

  if (dataItem && Object.keys(dataItem)?.length) {
    selectedItem.value = dataItem;
  }
};

/**
 * @todo 생산 유형 값을 변경하면 바로 적용되게 할 지 말지에 대해서 고민해봐야함!!!
 */
watch([selectedItem], () => {
  refSub2.value?.onLoad();
});

const calcFormula = (columnDatas: any, row: number, binding1: string, binding2: string) =>
  (columnDatas.getCellData(
    row,
    columnDatas.columns.findIndex((col: any) => col.binding === binding1),
    false,
  ) /
    columnDatas.getCellData(
      row,
      columnDatas.columns.findIndex((col: any) => col.binding === binding2),
      false,
    )) *
  100;

const formatNumber = (num: number) => {
  // 소수점 첫째 자리에서 버림
  const truncated = Number(num.toFixed(1));

  // 소수점이 0이면 정수로 변환
  if (truncated % 1 === 0) {
    return truncated.toFixed(0);
  }
  return truncated.toFixed(1);
};

/**
 * @todo 상태 관리 및 업데이트는 formatItem에서 처리하지 말고 다른 곳으로 로직 이동시키기
 */
const formatItem = (s: FlexGrid, e: any) => {
  if (e.panel.cellType === 5) {
    e.cell.classList.add('summary-footer');
    e.cell.addEventListener('mousedown', () => {
      if (summaryTotalRowData.value.due === 'Invalid Date') {
        switch (mainLoadParams.value.summary) {
          case 'cust':
            selectedItem.value = { ...toRaw(summaryTotalRowData.value), due: '[SUB TOTAL]' };
            break;
          case 'due':
            selectedItem.value = { ...toRaw(summaryTotalRowData.value), due: '[TOTAL]' };
            break;
          case 'itemGroup':
            // 여기 분기처리를 타면 아주 곤란함
            break;
          default:
            break;
        }
      } else {
        selectedItem.value = summaryTotalRowData.value;
      }
      summaryGrid.value && summaryGrid.value.select(new CellRange(-1, -1), false);
    });

    if (e.getColumn().binding === 'rtfRatio') {
      const rtfRatio = calcFormula(s.columnFooters, 0, 'rtfQty', 'demandQty');
      if (rtfRatio !== null && rtfRatio !== undefined && !Number.isNaN(rtfRatio)) {
        e.cell.innerHTML = projectModule.convertToFormat('ratio', rtfRatio);
      }
    }

    if (e.getColumn().binding === 'onTimeRatio') {
      const onTimeRatio = calcFormula(s.columnFooters, 0, 'onTimeQty', 'demandQty');
      if (onTimeRatio !== null && onTimeRatio !== undefined && !Number.isNaN(onTimeRatio)) {
        e.cell.innerHTML = projectModule.convertToFormat('ratio', onTimeRatio);
      }
    }

    if (e.getColumn().binding === 'lateRatio') {
      const lateRatio = calcFormula(s.columnFooters, 0, 'lateQty', 'demandQty');
      if (lateRatio !== null && lateRatio !== undefined && !Number.isNaN(lateRatio)) {
        e.cell.innerHTML = projectModule.convertToFormat('ratio', lateRatio);
      }
    }

    if (e.getColumn().binding === 'due') {
      e.cell.innerText = '[TOTAL]';
    }
  } else if (e.panel !== s.columnHeaders && s.rows[e.row] instanceof GroupRow) {
    const row = s.rows[e.row];
    if (row instanceof GroupRow && !row.isCollapsed) {
      e.cell.classList.add('rtf-report-group-separator');
    }

    // 현재 셀의 컬럼에 대해 visible = true인 컬럼 인덱스를 구합니다.
    const visibleColumns = e.panel.columns.filter((column: any) => column.visible);
    const visibleColumnIndex = visibleColumns.indexOf(e.panel.columns[e.col]);

    if (visibleColumnIndex === 0) {
      const btn = e.cell.childNodes[0];
      const spanEl = document.createElement('span');
      spanEl.style.width = '90%';
      spanEl.textContent = s.rows[e.row]?.dataItem?.name;
      spanEl.classList.add('wj-cell-text');
      e.cell.innerHTML = '';
      e.cell.append(btn);
      e.cell.append(spanEl);
    } else {
      const spanEl = document.createElement('span');
      spanEl.classList.add('wj-cell-text');
      spanEl.innerText = e.cell.innerText;
      e.cell.innerHTML = '';
      e.cell.append(spanEl);
    }

    if (e.getColumn().binding === 'rtfRatio') {
      const rtfRatio = calcFormula(s, e.row, 'rtfQty', 'demandQty');
      e.cell.innerHTML = `${formatNumber(rtfRatio) || '0'}%`;
    }

    if (e.getColumn().binding === 'onTimeRatio') {
      const onTimeRatio = calcFormula(s, e.row, 'onTimeQty', 'demandQty');
      e.cell.innerHTML = `${formatNumber(onTimeRatio) || '0'}%`;
    }

    if (e.getColumn().binding === 'lateRatio') {
      const lateRatio = calcFormula(s, e.row, 'lateQty', 'demandQty');
      e.cell.innerHTML = `${formatNumber(lateRatio) || '0'}%`;
    }
  } else if (isDataCell(s, e)) {
    e.cell.classList.add('rtf-report-child-row');
  }

  if (s.rows[e.row + 1] instanceof GroupRow) {
    e.cell.classList.add('rtf-report-separator');
  }

  if (!isDataCell(s, e)) return;

  const item = e.getRow()?.dataItem;
  const col = e.getColumn().binding;
  const cell = e.cell.querySelector('span') != null ? e.cell.querySelector('span') : e.cell;

  switch (col) {
    case 'demandQty':
    case 'onTimeQty':
    case 'shortQty':
    case 'rtfQty':
      if (typeof item[col] === 'number') cell.textContent = item[col].toLocaleString();
      break;
    case 'onTimeRatio':
      if (typeof item[col] === 'number') cell.textContent = `${item[col].toLocaleString()}%`;
      break;
    case 'rtfRatio':
      if (typeof item[col] === 'number') cell.textContent = `${item[col].toLocaleString()}%`;
      break;
    case 'lateRatio':
      if (typeof item[col] === 'number') cell.textContent = `${item[col].toLocaleString()}%`;
      break;
    default:
      break;
  }
};

defineExpose({ onLoad });
</script>
<style lang="scss">
.rtf-report-sub1-grid {
  .wj-group {
    // background-color: #d6def8 !important;
    font-weight: 500;
  }

  .wj-flexgrid .wj-cell .wj-btn.wj-btn-glyph {
    width: 20px;
    height: 12px;
  }

  .wj-glyph-right,
  .wj-glyph-down-right {
    color: #8998b5 !important;
  }
}

.summary-footer {
  // border-top: 1px solid #6a7184 !important;
  border-right: 1px solid #c1c1d8 !important;
  border-bottom: 1px solid #c1c1d8;
  background-color: #d6def8 !important;
  font-weight: 500;
  &:focus {
    color: #4568e0;
    &::after {
      content: '';
      border: 2px solid #4568e0;
      width: 100%;
      height: 100%;
      left: 0;
      top: 0;
      position: absolute;
      border-radius: 1px;
    }
  }
}

.rtf-report-separator {
  border-bottom: 1px solid #6a7184 !important;
}

.rtf-report-group-separator {
  box-shadow: 0px -1px 0px 0px #6a7184;
  // background-color: #d6def8 !important;
}

.rtf-report-child-row {
  // background-color: #ecf1ff !important;
}
</style>
