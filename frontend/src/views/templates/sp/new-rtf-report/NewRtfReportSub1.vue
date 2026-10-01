<template>
  <MozGrid
    :key="mainLoadParams.summary"
    :id="`${currentMenu.menuName}-sub1-Summary-id`"
    class="moz-readonly-grid rtf-report-sub1-grid"
    :style="{ width: parentsSummaryWidth, height: parentsSummaryHeight }"
    :coreConfig="coreConfig"
    :contextMenuConfig="{
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
    :loading="mainQuery.isFetching.value"
    :useSort="false"
    @ready="onReady"
    @cell:click="onCellClick"
  />
</template>

<script setup lang="ts">
import { downloadBigData, useMenuStore } from './adapters/stores';
import { useProjectInfoStore } from './adapters/stores';
import { MozGrid } from '@vmscloud/moz-ui-grid-vue';
import type { FieldDef, GridChrome, MozGridCoreProps, PureSheet } from '@vmscloud/moz-ui-grid-vue';
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
const summaryGrid = shallowRef<PureSheet>(); // 코어 그리드
/** 그리드 행 — 그룹 요약이면 그룹 행(부모) 아래에 데이터 행(자식)을 둔 트리 구조 */
const summaryDataSource = shallowRef<SummaryRow[]>([]);
const summaryTotalRowData = ref<any>();

type SummaryRowKind = 'group' | 'data' | 'total';
type SummaryRow = Record<string, any> & { _rowKey: string; _parentKey: string | null; _kind: SummaryRowKind };

// 요약 기준별 그룹 컬럼
const GROUP_BINDING: Record<string, string | undefined> = {
  cust: 'custID',
  itemGroup: 'itemGroupID',
  region: 'region',
  demandType: 'demandType',
};
const SUM_BINDINGS = ['demandCnt', 'demandQty', 'rtfQty', 'onTimeQty', 'lateQty'];

/**
 * @todo 백엔드 API 스네이크 케이스로 받고 하드코딩된 로직 제거
 * 서버에서 받는 케이스가 안 맞아서 `createColumnMapForExport(coreConfig.fields)`로 처리 불가능 함
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
 * 비율 = 분자 합 / 분모 합 * 100 (소수점 첫째 자리)
 */
const calcRatio = (numerator: number, denominator: number) => {
  if (!denominator) return 0;
  return Number(((numerator / denominator) * 100).toFixed(1));
};

/**
 * 합계 컬럼을 더하고 비율 컬럼을 합계로 다시 계산한다 (그룹 행·전체 합계 행 공용)
 */
const summarize = (rows: any[]) => {
  const result: Record<string, number> = {};
  SUM_BINDINGS.forEach((binding) => {
    result[binding] = rows.reduce((acc, row) => acc + (Number(row[binding]) || 0), 0);
  });
  result.rtfRatio = calcRatio(result.rtfQty, result.demandQty);
  result.onTimeRatio = calcRatio(result.onTimeQty, result.demandQty);
  result.lateRatio = calcRatio(result.lateQty, result.demandQty);
  return result;
};

const buildSummaryRows = (data: any[]): SummaryRow[] => {
  const groupBinding = GROUP_BINDING[mainLoadParams.value.summary];
  const rows: SummaryRow[] = [];

  if (!groupBinding) {
    data.forEach((elem, idx) => rows.push({ ...elem, _rowKey: `data-${idx}`, _parentKey: null, _kind: 'data' }));
  } else {
    const groups = new Map<string, any[]>();
    data.forEach((elem) => {
      const groupName = elem[groupBinding];
      if (!groups.has(groupName)) groups.set(groupName, []);
      groups.get(groupName)!.push(elem);
    });

    let dataIdx = 0;
    groups.forEach((children, groupName) => {
      const groupKey = `group-${groupName}`;
      rows.push({
        ...summarize(children),
        due: groupName,
        [groupBinding]: groupName,
        _rowKey: groupKey,
        _parentKey: null,
        _kind: 'group',
      });
      children.forEach((elem) => {
        rows.push({ ...elem, _rowKey: `data-${dataIdx++}`, _parentKey: groupKey, _kind: 'data' });
      });
    });
  }

  // 전체 합계 행 (옛 그리드의 컬럼 푸터)
  rows.push({ ...summarize(data), due: '[TOTAL]', _rowKey: 'total', _parentKey: null, _kind: 'total' });
  return rows;
};

const isTempGroupColumnTitle = ref<boolean>(true);

const ratioMask = {
  type: 'function' as const,
  formatter: (value: unknown) => (typeof value === 'number' ? `${value.toLocaleString()}%` : String(value ?? '')),
};

const rowClass = ({ row: rowData }: { row: any }) => {
  switch (rowData?._kind) {
    case 'group':
      return { class: 'rtf-report-group-separator' };
    case 'total':
      return { class: 'summary-footer' };
    default:
      return { class: 'rtf-report-child-row' };
  }
};

const coreConfig = computed<MozGridCoreProps>(() => {
  const isGrouped = !!GROUP_BINDING[mainLoadParams.value.summary];
  const qtyMask = projectModule.maskGrid('qty');
  const numberField = (id: string, header: string, extra: Partial<FieldDef> = {}): FieldDef => ({
    id,
    header,
    dataType: 'number',
    width: 90,
    align: 'right',
    sortable: false,
    cellAttributes: rowClass,
    ...extra,
  });
  const textField = (id: string, header: string): FieldDef => ({
    id,
    header,
    dataType: 'string',
    width: 80,
    align: 'center',
    hidden: true,
    sortable: false,
    cellAttributes: rowClass,
  });

  return {
    mode: 'flat',
    keyFields: ['_rowKey'],
    data: summaryDataSource.value,
    treeConfig: isGrouped
      ? {
          idField: '_rowKey',
          parentField: '_parentKey',
          treeColumn: 'due',
          /**
           * RTF 현황(aps/sp/RtfReport)랑 일관적으로 접혀있는 것이 올바름
           * 펼치려면 0을 1로 변경하면 됨
           */
          defaultExpandLevel: 0,
        }
      : undefined,
    fields: [
      {
        id: 'due',
        header: groupingColumnHeader.value,
        dataType: 'string',
        width: mainLoadParams.value.summary === 'due' ? 80 : 120,
        align: 'center',
        sortable: false,
        cellAttributes: rowClass,
      },
      // 그룹핑 관련 컬럼은 그룹 행 이름으로 대신 보여주므로 숨긴다
      textField('custID', t('text-cust_name')),
      textField('itemGroupID', t('text-item_group')),
      textField('region', t('text-region')),
      textField('demandType', t('text-demand_type')),
      numberField('demandCnt', t('text-demand_cnt'), { width: 80 }),
      numberField('demandQty', t('text-demand_qty'), { mask: qtyMask }),
      numberField('rtfQty', t('text-rtf_qty'), { mask: qtyMask }),
      { ...textField('qtyUom', t('text-qty_uom')), width: 90, align: 'left' },
      numberField('onTimeRatio', t('text-on_time_ratio'), { mask: ratioMask }),
      numberField('onTimeQty', t('text-on_time_qty'), { mask: qtyMask, hidden: true }),
      numberField('lateRatio', t('text-late_ratio'), { mask: ratioMask }),
      numberField('lateQty', t('text-late_qty'), { mask: qtyMask, hidden: true }),
      numberField('rtfRatio', t('text-rtf_ratio'), { mask: ratioMask }),
    ],
  };
});

/**
 * INITIALIZE
 */
// GRID INITIALIZE
const onReady = (grid: PureSheet, _chrome: GridChrome) => {
  summaryGrid.value = grid;
};

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

      summaryDataSource.value = buildSummaryRows(data);

      isTempGroupColumnTitle.value = false;

      summaryTotalRowData.value = totalRow;
    } else {
      summaryDataSource.value = [];
    }
  } else if (mainQuery.isError.value) {
    showMessage(t('msg-toast-get_error'), false);
    summaryDataSource.value = [];
  }
};

watch(summaryDataSource, (newSummaryDataSource) => {
  if (newSummaryDataSource?.length) {
    nextTick(() => {
      // 첫 행을 선택한다 (옛 그리드의 select(0, 0) 과 같은 동작)
      summaryGrid.value?.cells.selectCellsByViewIndices([{ viewIndex: 0, columnId: 'due' }]);
      selectRow(newSummaryDataSource[0]);
    });
  }
});
// endregion

/**
 * GRID EVENT
 */

const selectTotalRow = () => {
  if (summaryTotalRowData.value?.due === 'Invalid Date') {
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
};

const selectRow = (row?: SummaryRow) => {
  if (!row) return;
  const { _rowKey, _parentKey, _kind, ...item } = row;
  let dataItem: any;

  switch (_kind) {
    case 'total':
      selectTotalRow();
      return;
    case 'group': {
      const groupBinding = GROUP_BINDING[mainLoadParams.value.summary];
      if (groupBinding) dataItem = { due: '[SUB TOTAL]', [groupBinding]: item[groupBinding] };
      break;
    }
    default:
      dataItem = item;
      break;
  }

  if (dataItem && Object.keys(dataItem)?.length) {
    selectedItem.value = dataItem;
  }
};

const onCellClick = (payload: any) => {
  selectRow(payload?.row);
};

/**
 * @todo 생산 유형 값을 변경하면 바로 적용되게 할 지 말지에 대해서 고민해봐야함!!!
 */
watch([selectedItem], () => {
  refSub2.value?.onLoad();
});

defineExpose({ onLoad });
</script>
<style lang="scss">
.rtf-report-sub1-grid {
  .ps-cell.rtf-report-group-separator {
    font-weight: 500;
    box-shadow: 0px -1px 0px 0px #6a7184;
  }

  .ps-cell.summary-footer {
    border-top: 1px solid #6a7184;
    border-right: 1px solid #c1c1d8;
    border-bottom: 1px solid #c1c1d8;
    background-color: #d6def8;
    font-weight: 500;
  }
}

.rtf-report-child-row {
  // background-color: #ecf1ff !important;
}
</style>
