<template>
  <ExtendFlexGrid
    :name="t(`${currentMenu.menuName}-sub2-summary`)"
    :id="`${currentMenu.menuName}-sub2-summary-id`"
    class="moz-readonly-grid rtf-report-sub2"
    style="width: var(--parents-main-width); height: 100%"
    :emptyState="{
      isLoading: !load.loading,
    }"
    :itemsSource="detailDataSource"
    :initialized="onInitialized"
    :selectionChanged="onSelectionChanged"
    :formatItem="formatItem"
    :isReadOnly="true"
    :allowSorting="'None'"
    :setContextMenuProps="{
      useFlexGridSetting: true,
      useFilter: true,
      useExportExcel: true,
      customMenu: [
        {
          align: 0,
          header: t(`text-view-item-additional-prop`),
          cmd: 'oponView',
          clicked: (res: any) => {
            if (!open) {
              modalOpen(selectedCellPosition.left, selectedCellPosition.top + selectedCellPosition.height + 5);
            }
          },
          active: (res: any) => {
            if (res?.hitTest.cellType === 2) {
              return false;
            }
            return true;
          },
        },
        {
          align: 0,
          header: t('text-open-demand-info-detail-view'),
          cmd: 'openDemandInfo',
          clicked: (res: any) => {
            if (!demandOpen) {
              demandModalOpen(selectedCellPosition.left, selectedCellPosition.top + selectedCellPosition.height + 5);
            }
          },
          active: (res: any) => {
            if (res?.hitTest.cellType === 2) {
              return false;
            }
            return true;
          },
        },
        { align: 0, header: '-' },
      ],
      onExportOriginalData: () =>
        downloadBigData({
          /**
           * @todo 백엔드 API 스네이크 케이스로 받고 변환처리하는 로직 제거
           * 서버에서 받는 케이스가 안 맞아서 `excelModule.createColumnMapForExport(grid as FlexGrid)`으로 처리 불가능 함
           */
          column_map: camelToSnake(
            propColumnsModule.parseExcel(excelModule.createColumnMapForExport(grid as FlexGrid)),
          ),
          file_name: `${t(`${menuModule.currentMenu.menuName}`)}_${detailLoadParams.planVer}`,
          data_method: 'POST',
          data_parameter: JSON.stringify(detailLoadParams),
          api_key: detailApiKey,
        }),
    }"
    :onInitializeRowData="
      () => {
        return { isAdded: true };
      }
    "
    :use-tool-box="true"
    :isToolBoxExpanded="false"
    ref="gridRef"
    :loading="detailQuery.isFetching.value || mainQuery.isFetching.value"
    :use-preset="true"
  >
    <ExtendGridContextOpenNewTab
      :route="
        (item: any) => {
          return {
            path: `/sp/ProdPlanByOper`,
            query: {
              planCycle: mainLoadParams.planCycleID,
              planVer: mainLoadParams.planVer,
              fromDate: fromDate?.format('YYYY-MM-DD') ?? '',
              toDate: toDate?.format('YYYY-MM-DD') ?? '',
              [`buffer[A]`]: 'All',
              [`itemGroup[+]`]: `${[item?.itemGroupID]}`,
              [`item[+]`]: `${[item?.itemID]}`,
            },
          };
        }
      "
      :disabled="
        (item: any) => {
          return !(item?.itemID || item?.itemGroup);
        }
      "
      :label="t('text-context-open_prod_plan_by_oper')"
    />
    <ExtendGridContextOpenNewTab
      :route="
        (item: any) => {
          return {
            path: `/dm/Demand`,
            query: {
              planCycle: mainLoadParams.planCycleID,
              planVer: mainLoadParams.planVer,
              [`item[+]`]: `${[item?.itemID]}`,
              [`demandVer[+]`]: `${[demandVer]}`,
            },
          };
        }
      "
      :disabled="
        (item: any) => {
          return !item?.itemID;
        }
      "
      :label="t('text-context-open_demand')"
    />
    <ExtendGridContextOpenNewTab
      :route="
        (item: any) => {
          return {
            path: `/sp/BomMapPlanView`,
            query: {
              planCycle: mainLoadParams.planCycleID,
              planVer: mainLoadParams.planVer,
              demandItemID: item?.itemID,
              demandID: item?.demandID,
            },
          };
        }
      "
      :disabled="
        (item: any) => {
          return !(item?.demandItemID || item?.itemID || item?.demandID);
        }
      "
      :label="t('text-context-open_bom_map_plan_view')"
    />
    <ExtendGridContextOpenNewTab
      :route="
        (item: any) => {
          return {
            path: `/sp/FgsStockInPlan`,
            query: {
              planCycle: mainLoadParams.planCycleID,
              planVer: mainLoadParams.planVer,
              fromDate: fromDate?.format('YYYY-MM-DD') ?? '',
              toDate: toDate?.format('YYYY-MM-DD') ?? '',
              [`item[+]`]: item?.itemID,
              [`itemGroup[+]`]: `${[item?.itemGroupID]}`,
            },
          };
        }
      "
      :disabled="
        (item: any) => {
          return !(item?.demandItemID || item?.itemID || item?.demandID);
        }
      "
      :label="t('text-context-open_fgs_prod_plan')"
    />
    <WjFlexGridColumn binding="demandID" :header="t('text-demand_id')" :width="80" align="left" />
    <WjFlexGridColumn binding="custID" :header="t('text-cust_name')" :width="80" />
    <WjFlexGridColumn
      :width="getWidthByKey('N2')"
      binding="onTimeRatio"
      :header="t('text-on_time_ratio')"
      dataType="Number"
      align="right"
      :format="projectModule.formatGrid('ratio')"
    />
    <WjFlexGridColumn
      :width="getWidthByKey('N2')"
      binding="lateRatio"
      :header="t('text-late_ratio')"
      dataType="Number"
      align="right"
      :format="projectModule.formatGrid('ratio')"
    />
    <WjFlexGridColumn
      :width="getWidthByKey('N2')"
      binding="rtfRatio"
      :header="t('text-rtf_ratio')"
      dataType="Number"
      align="right"
      :format="projectModule.formatGrid('ratio')"
    />
    <WjFlexGridColumn binding="showDetailCol" :header="t('text-simple_short_reason')" :width="getWidthByKey('N2')" />
    <WjFlexGridColumn binding="itemGroupID" :header="t('text-item_group')" dataType="String" />
    <WjFlexGridColumn binding="itemID" :header="t('text-item_id')" dataType="String" />
    <WjFlexGridColumn binding="itemName" :header="t('text-item_name')" dataType="String" />
    <WjFlexGridColumn binding="dueWeek" :header="t('text-due_week')" dataType="String" align="center" />
    <WjFlexGridColumn :width="getWidthByKey('S2')" binding="dueDate" :header="t('text-due_date')" dataType="String" />
    <WjFlexGridColumn
      :width="getWidthByKey('N2')"
      binding="demandQty"
      :header="t('text-demand_qty')"
      dataType="Number"
      align="right"
      :format="projectModule.formatGrid('qty')"
    />
    <WjFlexGridColumn
      :width="getWidthByKey('N2')"
      binding="onTimeQty"
      :header="t('text-on_time_qty')"
      dataType="Number"
      :format="projectModule.formatGrid('qty')"
      align="right"
    />
    <WjFlexGridColumn
      :width="getWidthByKey('N2')"
      binding="lateQty"
      :header="t('text-late_qty')"
      dataType="Number"
      :format="projectModule.formatGrid('qty')"
      align="right"
    />
    <WjFlexGridColumn
      :width="getWidthByKey('N2')"
      binding="rtfQty"
      :header="t('text-rtf_qty')"
      dataType="Number"
      :format="projectModule.formatGrid('qty')"
      align="right"
    />
    <WjFlexGridColumn
      :width="getWidthByKey('N2')"
      binding="shortQty"
      :header="t('text-short_qty')"
      dataType="Number"
      :format="projectModule.formatGrid('qty')"
      align="right"
    />
    <WjFlexGridColumn
      binding="qtyUom"
      :header="t('text-qty_uom')"
      dataType="String"
      align="left"
      :width="90"
      :visible="false"
    />
    <WjFlexGridColumn binding="demand_type" :header="t('text-demand_type')" dataType="String" :visible="false" />
    <WjFlexGridColumn binding="item_type" :header="t('text-item_type')" dataType="String" :visible="false" />
    <WjFlexGridColumn binding="prod_type" :header="t('text-prod_type')" dataType="String" :visible="false" />
    <WjFlexGridColumn binding="item_size_type" :header="t('text-item_size_type')" dataType="String" :visible="false" />
    <WjFlexGridColumn binding="item_spec" :header="t('text-item_spec')" dataType="String" :visible="false" />

    <WjFlexGridColumn
      v-for="(col, idx) in propColumns"
      :binding="col.binding"
      :header="propHeaders[idx]"
      dataType="String"
      :width="120"
      align="left"
      :visible="false"
    ></WjFlexGridColumn>
  </ExtendFlexGrid>

  <PlanByProdPop
    :showDetail="localState.showDetail"
    :planCycleID="mainLoadParams.planCycleID"
    :planVer="mainLoadParams.planVer"
    :data="{
      demandItemIDs: [localState.selectedItem?.itemID],
      customers: [localState.selectedItem?.custID],
      demandIDs: [localState.selectedItem?.demandID],
      demandQty: localState.selectedItem?.demandQty,
    }"
    :close="() => (localState.showDetail = false)"
    :auto-focus-props="{
      targetDemandID: localState.selectedItem?.demandID,
    }"
  />
  <Popup
    :width="popupWidth"
    :height="popupHeight"
    v-model:visible="popup"
    :title="t('text-short-reason-detail-view')"
    :onCancel="
      () => {
        popup = false;
      }
    "
    preset="close"
    :maxWidth="popupWidth"
    :maxHeight="popupHeight"
    :resizeable="true"
    :style="{
      minWidth: '650px',
      minHeight: '400px',
    }"
    :useVShow="false"
  >
    <div ref="container" class="bom-map-popup-container" v-loading="bomNetworkQuery.isFetching.value">
      <SplitPane horizontal style="max-width: 100%">
        <Pane size="70%" max-size="90%">
          <BomMapInterface
            v-if="!bomNetworkQuery.isFetching.value && bomNetworkInfos?.length"
            :bomNetworkInfos="bomNetworkInfos"
            :demandInfos="demandInfos"
            :shortLogs="shortLogs"
            :initKey="demandInfos?.item_id"
            :planCycleData="{
              planVer: mainLoadParams.planVer,
              planCycleID,
              fromDate: fromDate?.format('YYYY-MM-DD') ?? '',
              toDate: toDate?.format('YYYY-MM-DD') ?? '',
              projectID,
              demandID: demandID,
            }"
            :userID="userID"
          />
          <div v-else class="grid-empty">
            <EmptyState v-if="!bomNetworkQuery.isLoading.value" :is-read-only="true" />
          </div>
        </Pane>
        <Pane size="30%" max-size="90%">
          <div v-if="!bomNetworkQuery.isFetching.value && bomNetworkInfos?.length" class="grid-sort-reason">
            <ExtendFlexGrid
              :height="'100%'"
              class="moz-readonly-grid"
              :id="`${currentMenu.menuName}-sub2-short-info-modal-id`"
              :name="t(`${currentMenu.menuName}`) + '-sub2-short-info-modal'"
              :use-preset="true"
              :itemsSource="shortDataSource"
              :initialized="onInitialized"
              :formatItem="formatItem"
              :isReadOnly="true"
              :allowSorting="'None'"
              :setContextMenuProps="{
                useFlexGridSetting: false,
                useGroupColumn: false,
                useViewSelectColumn: true,
                useExportExcel: true,
                useFilter: false,
                onExportOriginalData: () =>
                  downloadBigData({
                    column_map: COLUMN_MAP,
                    file_name: `${t(`${menuModule.currentMenu.menuName}`)}_${shortLoadParams.planVer}`,
                    data_method: 'POST',
                    data_parameter: JSON.stringify(shortLoadParams),
                    api_key: shortApiKey,
                  }),
              }"
              :use-tool-box="false"
              :empty-state="{
                isLoading: shortQuery.isFetching.value,
                contentMsg: '',
              }"
              :loading="shortQuery.isFetching.value"
            >
              <WjFlexGridColumn
                :width="getWidthByKey('S3')"
                binding="shortType"
                :header="t('text-short_type')"
                align="center"
              />
              <WjFlexGridColumn
                :width="getWidthByKey('S2')"
                binding="shortCategory"
                :header="t('text-short_category')"
              />
              <WjFlexGridColumn :width="getWidthByKey('DF')" binding="shortReason" :header="t('text-short_reason')">
                <WjFlexGridCellTemplate cellType="Cell" v-slot="cell">
                  <span
                    class="wj-cell-text"
                    v-tooltip="{
                      text: t(`desc-${cell?.item?.shortType}-${cell?.item?.shortCategory}-${cell?.item?.shortReason}`),
                    }"
                    >{{
                      convertToInternationalization(cell?.item?.shortReason, 'short', [
                        'LackOfResourceCapacity',
                        'LateReleaseLot',
                        'InvalidBuffer',
                        'InvalidCustomer',
                        'InvalidItem',
                        'InvalidSite',
                      ])
                    }}</span
                  >
                </WjFlexGridCellTemplate>
              </WjFlexGridColumn>
              <WjFlexGridColumn
                :width="getWidthByKey('N2')"
                binding="shortQty"
                :header="t('text-short_qty')"
                dataType="Number"
                :format="projectModule.formatGrid('qty')"
                align="right"
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
                :width="getWidthByKey('S1')"
                binding="shortDetailInfo"
                :header="t('text-short_detail_info')"
              />
              <WjFlexGridColumn :width="getWidthByKey('S1')" binding="isbID" :header="t('text-isb_id')" />
              <WjFlexGridColumn :width="getWidthByKey('S1')" binding="bomID" :header="t('text-bom_id')" />
              <WjFlexGridColumn :width="getWidthByKey('S1')" binding="routingID" :header="t('text-routing_id')" />
              <WjFlexGridColumn :width="getWidthByKey('DF')" binding="operID" :header="t('text-oper_id')" />
              <WjFlexGridColumn :width="getWidthByKey('DF')" binding="resID" :header="t('text-res_id')" />
            </ExtendFlexGrid>
          </div>
        </Pane>
      </SplitPane>
    </div>
  </Popup>
  <InfoModal key="main-info-modal">
    <!-- 제목 슬롯 -->
    <template #title>
      <span>{{ itemInfoHeaderText }}</span>
    </template>
    <!-- 컨텐츠 슬롯 -->
    <template #content>
      <div class="info-modal-content-wrapper">
        <ExtendFlexGrid
          height="100%"
          :id="`${t(currentMenu.menuName)}-item-info-modal-id`"
          :name="`${t(currentMenu.menuName)}-item-info-modal-name`"
          :autoGenerateColumns="false"
          :alternatingRowStep="0"
          :itemsSource="selectedItemInfo"
          :initialized="onItemInfoInitialized"
          :isReadOnly="true"
          :emptyState="{
            isLoading: itemDetailQuery.isFetching.value,
            contentMsg: '',
          }"
          :use-tool-box="true"
          :loading="itemDetailQuery.isFetching.value"
          :use-sort="true"
          :use-preset="true"
          :setContextMenuProps="{
            useGroupColumn: false,
            useViewSelectColumn: true,
            useBulkEditColumn: false,
            useExportExcel: false,
            useExportImport: currentMenu?.isWrite,
          }"
        >
          <WjFlexGridColumn :width="150" binding="item_id" :header="t('text-item_id')" :isRequired="true" />
          <WjFlexGridColumn :width="getWidthByKey('S3')" binding="item_type" :header="t('text-item_type')" />
          <WjFlexGridColumn :width="150" binding="item_name" :header="t('text-item_name')" />
          <WjFlexGridColumn :width="getWidthByKey('S2')" binding="item_group" :header="t('text-item_group')" />
          <WjFlexGridColumn :width="getWidthByKey('S1')" binding="description" :header="t('text-description')" />
          <WjFlexGridColumn
            :width="getWidthByKey('N2')"
            binding="item_priority"
            :header="t('text-item_priority')"
            dataType="Number"
            align="right"
          />
          <WjFlexGridColumn
            :width="getWidthByKey('S3')"
            binding="procurement_type"
            :header="t('text-procurement_type')"
          />
          <WjFlexGridColumn :width="getWidthByKey('S3')" binding="prod_type" :header="t('text-prod_type')" />
          <WjFlexGridColumn :width="getWidthByKey('S3')" binding="item_size" :header="t('text-item_size')" />
          <WjFlexGridColumn :width="getWidthByKey('S3')" binding="item_spec" :header="t('text-item_spec')" />
          <WjFlexGridColumn
            v-for="col in selectedItemColumnHeaders"
            :width="150"
            :binding="`${col}`"
            :header="t(col)"
            :cssClass="'master-prop-col'"
          />
        </ExtendFlexGrid>
      </div>
    </template>
  </InfoModal>

  <!-- 두 번째 InfoModal (수요 정보용) -->
  <InfoModal key="demand-info-modal" storeKey="useDemandInfoModal">
    <template #title>
      <span>{{ '수요 정보 상세 보기' }}</span>
    </template>
    <template #content>
      <div class="demand-modal-content-wrapper">
        <ExtendFlexGrid
          height="100%"
          :id="`${t(currentMenu.menuName)}-demand-info-modal-id`"
          :name="`${t(currentMenu.menuName)}-demand-info-modal`"
          :use-preset="true"
          :autoGenerateColumns="false"
          :alternatingRowStep="0"
          :itemsSource="demandInfoSource"
          :initialized="onDemandInfoInitialized"
          :emptyState="{
            isLoading: false,
          }"
          :isReadOnly="true"
          :validateKey="'none'"
          :setContextMenuProps="{
            useGroupColumn: false,
            useViewSelectColumn: false,
            useBulkEditColumn: false,
            useExportExcel: false,
            useExportImport: false,
          }"
          :loading="false"
        >
          <WjFlexGridColumn
            :width="getWidthByKey('S2')"
            binding="demand_id"
            :header="t('text-demand_id')"
            :isRequired="true"
          />
          <WjFlexGridColumn
            :width="getWidthByKey('DF')"
            binding="item_id"
            :header="t('text-item_id')"
            :isRequired="true"
          />
          <WjFlexGridColumn
            :width="getWidthByKey('S2')"
            binding="site_id"
            :header="t('text-site_id')"
            :isRequired="true"
          />
          <WjFlexGridColumn
            :width="getWidthByKey('S2')"
            binding="buffer_id"
            :header="t('text-buffer_id')"
            :isRequired="true"
          />
          <WjFlexGridColumn
            :width="getWidthByKey('D2')"
            binding="due_date"
            :header="t('text-due_date')"
            dataType="Date"
            format="yyyy-MM-dd"
            align="center"
            :isRequired="true"
          />
          <WjFlexGridColumn
            :width="getWidthByKey('D1')"
            binding="due_datetime"
            :header="t('text-due_datetime')"
            dataType="Date"
            format="yyyy-MM-dd HH:mm:ss"
            align="center"
          />
          <!-- mask="99:99:99" -->
          <WjFlexGridColumn
            :width="getWidthByKey('N2')"
            binding="demand_qty"
            :header="t('text-demand_qty')"
            dataType="Number"
            align="right"
          />
          <WjFlexGridColumn
            :width="getWidthByKey('N2')"
            binding="demand_priority"
            :header="t('text-demand_priority')"
            dataType="Number"
            align="right"
          />
          <WjFlexGridColumn :width="getWidthByKey('S2')" binding="cust_id" :header="t('text-cust_id')" />
          <WjFlexGridColumn :width="getWidthByKey('S3')" binding="demand_type" :header="t('text-demand_type')" />
          <WjFlexGridColumn
            :width="getWidthByKey('N2')"
            binding="max_lateness_day"
            :header="t('text-max_lateness_day')"
            dataType="Number"
            align="right"
          />
          <WjFlexGridColumn
            :width="getWidthByKey('N2')"
            binding="max_earliness_day"
            :header="t('text-max_earliness_day')"
            dataType="Number"
            align="right"
          />
          <WjFlexGridColumn :width="getWidthByKey('S2')" binding="demand_group" :header="t('text-demand_group')" />
          <WjFlexGridColumn
            :width="getWidthByKey('S2')"
            binding="final_item_buffer_id"
            :header="t('text-final_item_buffer_id')"
          />
          <WjFlexGridColumn :width="getWidthByKey('S1')" binding="description" :header="t('text-description')" />
          <!-- <WjFlexGridColumn
            v-for="col in propColumns"
            :binding="col.binding"
            :header="col.header"
            :dataType="col.dataType"
            :width="col.width"
            :align="col.align"
          ></WjFlexGridColumn> -->
          <WjFlexGridColumn
            :width="getWidthByKey('S2')"
            binding="legacy_data_version"
            :header="t('text-legacy_data_version')"
            :isReadOnly="true"
            :visible="false"
          />
          <WjFlexGridColumn
            :width="getWidthByKey('S2')"
            binding="interfaced_from"
            :header="t('text-interfaced_from')"
            :isReadOnly="true"
            :visible="false"
          />

          <WjFlexGridColumn
            :width="getWidthByKey('D1')"
            binding="create_datetime"
            :header="t('text-create_datetime')"
            dataType="Date"
            format="yyyy-MM-dd HH:mm:ss"
            align="center"
            :isReadOnly="true"
          />
          <WjFlexGridColumn
            :width="getWidthByKey('S2')"
            binding="create_user_id"
            :header="t('text-create_user_id')"
            :isReadOnly="true"
          />
          <WjFlexGridColumn
            :width="getWidthByKey('D1')"
            binding="update_datetime"
            :header="t('text-update_datetime')"
            dataType="Date"
            format="yyyy-MM-dd HH:mm:ss"
            align="center"
            :isReadOnly="true"
          />
          <WjFlexGridColumn
            :width="getWidthByKey('S2')"
            binding="update_user_id"
            :header="t('text-update_user_id')"
            :isReadOnly="true"
          />
        </ExtendFlexGrid>
        <!-- 수요 정보용 그리드나 다른 컨텐츠 -->
      </div>
    </template>
  </InfoModal>
</template>
<script setup lang="ts">
import ExtendGridContextOpenNewTab from './components/ExtendGridContextOpenNewTab.vue';
import { useInfoModalStore } from './components/InfoModal';
import InfoModal from './components/InfoModal.vue';
import { downloadBigData, useMenuStore, usePlanCycleStore } from './adapters/stores';
import { useLoadStore, useProjectInfoStore } from './adapters/stores';
import { convertToInternationalization } from './adapters/utils';
import BomMapInterface from './components/bom-map/BomMapInterface.vue';
import { FlexGrid, FormatItemEventArgs, GroupRow } from '@vmscloud/moz-wijmo-grid/wijmo.grid';
import { WjFlexGridCellTemplate, WjFlexGridColumn } from '@vmscloud/moz-wijmo-grid/wijmo.vue2.grid';
import { EmptyState, Pane, Popup, SplitPane } from '@vmscloud/moz-ui-components';
import { ExtendFlexGrid, type ExtendGrid } from '@vmscloud/moz-wijmo-grid';
import { useExcelStore } from '@vmscloud/moz-wijmo-grid/store';
import { getWidthByKey, isDataCell } from '@vmscloud/moz-wijmo-grid/utils';
import { camelToSnake, showMessage } from '@moz-shared/utils';
import { useQueryClient } from '@tanstack/vue-query';
import { debounce } from 'es-toolkit';
import { useTranslation } from 'i18next-vue';
import { storeToRefs } from 'pinia';
import {
  computed,
  defineAsyncComponent,
  inject,
  nextTick,
  onBeforeUnmount,
  onMounted,
  provide,
  reactive,
  ref,
  shallowRef,
  toRaw,
  toRefs,
  watch,
  watchEffect,
} from 'vue';
import { IRtfReportQuery } from './NewRtfReport';

const PlanByProdPop = defineAsyncComponent(() => import('./components/PlanByProdPop.vue'));

/**
 * props
 */
interface Props {
  parentsMainWidth?: string;
  parentsMainHeight?: string;
}

const props = withDefaults(defineProps<Props>(), {});
const { parentsMainWidth, parentsMainHeight } = toRefs(props);
const planCycleStore = usePlanCycleStore();
const { demandVer, fromDate, toDate, planCycleID, planVer } = storeToRefs(planCycleStore as any);

/**
 * DEFINE DEFAULT VARIABLE
 */
const queryClient = useQueryClient();
const menuModule = useMenuStore();
const { currentMenu } = storeToRefs(menuModule);
const projectModule = useProjectInfoStore();
const { currentProjectID: projectID } = storeToRefs(projectModule);
const projectInfoStore = useProjectInfoStore();
const userID = computed(() => projectInfoStore.userInfo?.id || '');
const excelModule = useExcelStore();
const load = useLoadStore();
const useInfoModal = useInfoModalStore();
const useDemandInfoModal = useInfoModalStore();
provide('useInfoModal', useInfoModal);
provide('useDemandInfoModal', useDemandInfoModal);
const { modalOpen, open } = useInfoModal;
const { modalOpen: demandModalOpen, open: demandOpen } = useDemandInfoModal;

const {
  itemDetailQuery,
  detailItemId,
  demandID,
  detailQuery,
  detailQueryKey,
  refSub3,
  saveDetailParams,
  mainLoadParams,
  detailApiKey,
  detailLoadParams,
  onLoadHeader,
  propColumnsModule,
  propColumns,
  showBomMapView: popup,
  bomNetworkQuery,
  shortQuery,
  shortLoadParams,
  shortApiKey,
  mainQuery,
  openItemInfo,
  demandDetailQuery,
  openDemandInfo,
} = inject('useRtfReport') as IRtfReportQuery;

const { t } = useTranslation(); // 다국어

// 브라우저 크기 변화 감지용 반응형 변수
const windowWidth = ref(window.innerWidth);
const windowHeight = ref(window.innerHeight);

// 브라우저 크기 90%의 px 단위 숫자 반환
const popupWidth = computed(() => Math.floor(windowWidth.value * 0.8));
const popupHeight = computed(() => Math.floor(windowHeight.value * 0.9));

// window resize 이벤트 처리
const updateWindowWidth = () => {
  windowWidth.value = window.innerWidth;
  windowHeight.value = window.innerHeight;
};

onMounted(() => {
  window.addEventListener('resize', updateWindowWidth);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateWindowWidth);
});

const grid = ref<FlexGrid | null>(null); // Wijmo grid
const extendGrid = ref<ExtendGrid | null>(null); // Wijmo grid
const gridRef = ref();
const localState: {
  showDetail: boolean;
  selectedItem: any;
} = reactive({
  showDetail: false,
  selectedItem: null,
});
const detailDataSource = shallowRef<any[]>([]);
const selectedCellPosition = ref<any>();

/**
 * INITIALIZE
 */
onMounted(() => {
  resetSize();
});

// GRID INITIALIZE
const onInitialized = (flexGrid: FlexGrid, _extendGrid: ExtendGrid) => {
  grid.value = flexGrid;
  extendGrid.value = _extendGrid;

  grid.value.loadedRows.addHandler(async () => {
    await nextTick(() => {
      if (grid.value) {
        grid.value.collapseGroupsToLevel(0);
      }
    });
  });
};

const onSelectionChanged = debounce((s: FlexGrid, e: any) => {
  const { row, col } = s.selection;

  if (row < 0 || col < 0) {
    demandID.value = '';
  } else {
    const dataItem = e.getRow().dataItem;
    demandID.value = dataItem.demandID;
    detailItemId.value = dataItem.itemID;

    // 선택된 셀의 DOM 요소와 위치 정보 얻기
    const cellElement = s.getCellBoundingRect(row, col);
    if (cellElement) {
      selectedCellPosition.value = cellElement;
    }
  }

  refSub3.value?.onLoad();
}, 300);

const onItemInfoInitialized = (_s: FlexGrid, _e: any) => {};

const onDemandInfoInitialized = (_s: FlexGrid, _e: any) => {};

/**
 * @description 하나의 tick 사이클에서 처리되어야 함. 전체 목록을 기록하는 과정이 있어야 prop 컬럼들에 대해서 채번이 가능해짐.
 * 갱신에 반응함. 그래서 고정된 문자열 배열로 처리해야 함.
 */
const propHeaders = computed(() => {
  if (!grid.value) return [];

  const result: string[] = [
    t('text-demand_id'),
    t('text-cust_name'),
    t('text-on_time_ratio'),
    t('text-late_ratio'),
    t('text-rtf_ratio'),
    t('text-item_group'),
    t('text-item_id'),
    t('text-item_name'),
    t('text-due_week'),
    t('text-due_date'),
    t('text-demand_qty'),
    t('text-on_time_qty'),
    t('text-late_qty'),
    t('text-rtf_qty'),
    t('text-short_qty'),
    t('text-qty_uom'),
    t('text-demand_type'),
    t('text-item_type'),
    t('text-prod_type'),
    t('text-item_size_type'),
    t('text-item_spec'),
  ];

  // const columns = [
  //   t('text-demand_id'),
  //   t('text-cust_name'),
  //   t('text-on_time_ratio'),
  //   t('text-late_ratio'),
  //   t('text-rtf_ratio'),
  //   t('text-item_group'),
  //   t('text-item_id'),
  //   t('text-item_name'),
  //   t('text-due_week'),
  //   t('text-due_date'),
  //   t('text-demand_qty'),
  //   t('text-on_time_qty'),
  //   t('text-late_qty'),
  //   t('text-rtf_qty'),
  //   t('text-short_qty'),
  //   t('text-qty_uom'),
  //   t('text-demand_type'),
  //   t('text-item_type'),
  //   t('text-prod_type'),
  //   t('text-item_size_type'),
  //   t('text-item_spec'),
  // ];

  // propColumns의 binding 목록 (prop 컬럼 식별용)
  const propBindings = new Set(propColumns.value.map((col) => col.binding));

  // prop 컬럼이 아닌 일반 컬럼의 header만 수집 (갱신 시 기존 prop 컬럼 제외)
  const existingHeaders = grid.value?.columns
    .filter((col) => !propBindings.has(col.binding ?? ''))
    .map((col) => col.header)
    .filter(Boolean) as string[];

  propColumns.value.forEach((prop) => {
    // 정규식 특수문자 이스케이프
    const escapedHeader = prop.header.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    // 정확히 일치하거나 "헤더명 숫자" 형식만 매칭 (^시작, $끝으로 부분 매칭 방지)
    const exactPattern = new RegExp(`^${escapedHeader}(\\s\\d+)?$`);

    /**
     * 그리드의 컬럼 header(prop 제외)와 앞으로 붙일 배열(result) 전체를 확인하고 채번을 한다.
     */
    const duplicatedHeaders = existingHeaders.concat(result).filter((header) => exactPattern.test(header));

    if (!duplicatedHeaders.length) {
      result.push(prop.header);
      return;
    }
    result.push(`${prop.header} ${duplicatedHeaders.length + 1}`);
  });
  return result;
});

const formatItem = (s: FlexGrid, e: FormatItemEventArgs) => {
  if (!isDataCell(s, e)) return;
  if (e.getRow() instanceof GroupRow) return;

  const item = e.getRow()?.dataItem;
  const col = e.getColumn().binding as
    | 'demandID'
    | 'custID'
    | 'onTimeRatio'
    | 'lateRatio'
    | 'rtfRatio'
    | 'itemGroupID'
    | 'itemID'
    | 'itemName'
    | 'itemName'
    | 'dueWeek'
    | 'dueDate'
    | 'demandQty'
    | 'onTimeQty'
    | 'lateQty'
    | 'rtfQty'
    | 'shortQty'
    | 'showDetailCol';
  const cell = e.cell.querySelector('span') != null ? e.cell.querySelector('span') : e.cell;
  if (!cell) return;

  switch (col) {
    case 'rtfQty':
    case 'demandQty':
    case 'onTimeQty':
    case 'shortQty':
    case 'lateQty':
      cell.textContent = item[col].toLocaleString();
      break;

    case 'rtfRatio':
    case 'onTimeRatio':
    case 'lateRatio':
      cell.textContent = `${item[col]}%`;
      break;
    case 'showDetailCol':
      cell.textContent = `${'상세 보기'}`;
      cell.style.cursor = 'pointer';
      cell.style.color = '#4568e0';
      cell.style.textDecoration = 'underline';
      cell.addEventListener('click', () => {
        popup.value = true;
      });
      break;
    default:
      break;
  }

  // short이 그리드 표시 우선순위에 더 중요해서 다음과 같이 분기처리함
  if (item.rtfRatio < 100) {
    e.cell.classList.add('ratio-short');
  }
  if (item.rtfRatio === 100 && item.lateRatio > 0) {
    e.cell.classList.add('ratio-late');
  }

  switch (col) {
    // case "SHORT_QTY":
    //   if (item.RTF_RATIO < 100) {
    //     const cell = e.cell.querySelector("span") != null ? e.cell.querySelector("span") : e.cell;
    //     cell.textContent = "0";
    //   }
    //   break;
    case 'rtfRatio':
      if (item.rtfRatio < 100) {
        e.cell.classList.add('ratio-short-font');
      }
      break;
    default:
      break;
  }

  // if (col === 'lateQty' && e.cell.innerText === '-0') {
  //   e.cell.innerText = '0';
  // }
};

const onloadDetail = async () => {
  saveDetailParams();
  const cache = queryClient.getQueryData(detailQueryKey);
  if (!cache) {
    await detailQuery.refetch();
  }

  if (detailQuery.isSuccess.value) {
    if (detailQuery.data.value?.length) {
      detailDataSource.value = toRaw(detailQuery.data.value).map((elem: any) => {
        propColumnsModule.parseFlex(elem);
        const [date, rangeStart, rangeEnd] = elem.dueDate.split(' ');
        return {
          ...elem,
          dueWeek: projectModule.convertToFormat('dateWeek', elem.dueWeek),
          dueDate: `${projectModule.convertToFormat('date', date)} ${rangeStart} ${rangeEnd}`,
        };
      });
      demandID.value = detailDataSource.value[0].demandID;
      refSub3.value?.onLoad();
    } else {
      detailDataSource.value = [];
    }
  } else if (detailQuery.isError.value) {
    showMessage(t('msg-toast-get_error'), false);
    detailDataSource.value = [];
  }
};

// region GET DATA
const onLoad = debounce(async () => {
  await onLoadHeader();
  await onloadDetail();
}, 100);

const resetDetailDataSource = () => {
  detailDataSource.value = [];
  demandID.value = '';
};

const bomNetworkInfos = shallowRef<any[]>([]);
const demandInfos = ref<any>({});
const shortLogs = shallowRef<any[]>([]);

watchEffect(
  () => {
    if (bomNetworkQuery.isSuccess.value) {
      if (bomNetworkQuery.data.value?.bomNetworkInfos?.length) {
        const rawData = toRaw(bomNetworkQuery.data.value);
        bomNetworkInfos.value = rawData.bomNetworkInfos;
        demandInfos.value = rawData.demandInfos;
        shortLogs.value = rawData.shortLogs;
      } else {
        bomNetworkInfos.value = [];
        demandInfos.value = {};
        shortLogs.value = [];
      }
    } else if (bomNetworkQuery.isError.value) {
      showMessage(t('msg-toast-get_error'), false);
      bomNetworkInfos.value = [];
      demandInfos.value = {};
      shortLogs.value = [];
    }
  },
  {
    flush: 'post',
  },
);

const shortDataSource = shallowRef<any[]>([]);

// short 그리드 데이터
watchEffect(
  () => {
    if (shortQuery.isSuccess.value) {
      if (shortQuery.data.value) {
        shortDataSource.value = toRaw(shortQuery.data.value);
      } else {
        shortDataSource.value = [];
      }
    } else if (bomNetworkQuery.isError.value) {
      showMessage(t('msg-toast-get_error'), false);
    }
  },
  {
    flush: 'post',
  },
);

const INFO_COLUMN_KEYS = [
  'item_id',
  'item_type',
  'item_name',
  'item_group',
  'description',
  'item_priority',
  'procurement_type',
  'prod_type',
  'item_size',
  'item_spec',
  'descending',
];

const selectedItemColumnHeaders = ref<string[]>([]);
const selectedItemInfo = shallowRef<any[]>([]);

watchEffect(
  () => {
    if (planVer.value && itemDetailQuery.isSuccess.value) {
      if (itemDetailQuery.data.value) {
        selectedItemColumnHeaders.value = Object.keys(itemDetailQuery.data.value).filter((item: any) => {
          if (!INFO_COLUMN_KEYS.includes(item)) {
            return true;
          }
          return false;
        });

        nextTick(() => {
          selectedItemInfo.value = [toRaw(itemDetailQuery.data.value)];
        });
      } else {
        selectedItemColumnHeaders.value = [];
        selectedItemInfo.value = [];
      }
    } else if (itemDetailQuery.isError.value) {
      selectedItemColumnHeaders.value = [];
      selectedItemInfo.value = [];
    }
  },
  {
    flush: 'post',
  },
);

const demandInfoSource = shallowRef<any[]>([]);

watchEffect(
  () => {
    if (planVer.value && demandDetailQuery.isSuccess.value) {
      if (demandDetailQuery.data.value) {
        nextTick(() => {
          demandInfoSource.value = toRaw(demandDetailQuery.data.value);
        });
      } else {
        demandInfoSource.value = [];
      }
    } else if (itemDetailQuery.isError.value) {
      demandInfoSource.value = [];
    }
  },
  {
    flush: 'post',
  },
);

/**
 * @todo 백엔드 API 스네이크 케이스로 받고 하드코딩된 로직 제거
 * 서버에서 받는 케이스가 안 맞아서 `excelModule.createColumnMapForExport(grid as FlexGrid)`으로 처리 불가능 함
 */
const COLUMN_MAP = {
  short_type: {
    column_name: t('text-short_type'),
    column_type: 'System.String',
    column_format: null,
  },
  short_category: {
    column_name: t('text-short_category'),
    column_type: 'System.String',
    column_format: null,
  },
  short_reason: {
    column_name: t('text-short_reason'),
    column_type: 'System.String',
    column_format: null,
  },
  short_qty: {
    column_name: t('text-short_qty'),
    column_type: 'System.Decimal',
    column_format: projectModule.formatGrid('qty'),
  },
  short_detail_info: {
    column_name: t('text-short_detail_info'),
    column_type: 'System.String',
    column_format: null,
  },
  isb_id: {
    column_name: t('text-isb_id'),
    column_type: 'System.String',
    column_format: null,
  },
  bom_id: {
    column_name: t('text-bom_id'),
    column_type: 'System.String',
    column_format: null,
  },
  routing_id: {
    column_name: t('text-routing_id'),
    column_type: 'System.String',
    column_format: null,
  },
  oper_id: {
    column_name: t('text-oper_id'),
    column_type: 'System.String',
    column_format: null,
  },
  res_id: {
    column_name: t('text-res_id'),
    column_type: 'System.String',
    column_format: null,
  },
};

// endregion

watch([parentsMainWidth, parentsMainHeight], () => {
  resetSize();
});

watch(open, () => {
  openItemInfo.value = open.value;
});

watch(demandOpen, () => {
  openDemandInfo.value = demandOpen.value;
});

const resetSize = () => {
  const el = document.querySelector('.rtf-report-sub2') as HTMLElement;
  if (!el) return;

  el?.style?.setProperty('--parents-main-width', `${parentsMainWidth?.value}`);
  el?.style?.setProperty('--parents-main-height', `${parentsMainHeight?.value}`);
};

const itemInfoHeaderText = computed(() => `제품 정보 보기`);

defineExpose({ onLoad, resetDetailDataSource });
</script>
<style lang="scss">
.moz-readonly-grid.rtf-report-sub2.wj-flexgrid .wj-cells .wj-row {
  &:nth-child(n) {
    .wj-cell.ratio-short {
      // 흰 배경일때 ratio-short 일때
      background-color: #f6d5d5 !important;

      // 그 상태에서 clicked 했을때
      &.aleatorik-clicked-state {
        background-color: #eae0ec !important;
      }
    }

    .wj-cell.ratio-late {
      // 흰 배경일때 ratio-late 일때
      background-color: #fde6c8 !important;

      // 그 상태에서 clicked 했을때
      &.aleatorik-clicked-state {
        background-color: #eae0ec !important;
      }
    }
  }

  &:nth-child(2n) {
    .wj-cell.ratio-short {
      // 파란 배경에서 ratio-short 일때
      background-color: #f1d0d4 !important;

      &.aleatorik-clicked-state {
        background-color: #e5daea !important;
      }
    }

    .wj-cell.ratio-late {
      // 파란 배경에서 ratio-late 일때
      background-color: #f8e1c7 !important;

      &.aleatorik-clicked-state {
        background-color: #e5daea !important;
      }
    }
  }

  .wj-cell.ratio-short:not(.wj-header) {
    &.wj-state-multi-selected,
    &.wj-state-active {
      background-color: #d4cde8 !important;
    }
  }

  &:hover {
    .wj-cell.ratio-short:not(.wj-header) {
      background-color: #d4cde8 !important;
    }
  }

  .wj-cell.ratio-late:not(.wj-header) {
    &.wj-state-multi-selected,
    &.wj-state-active {
      background-color: #d4cde8 !important;
    }
  }

  &:hover {
    .wj-cell.ratio-late:not(.wj-header) {
      background-color: #d4cde8 !important;
    }
  }

  .ratio-short-font span {
    color: #dc5a5a !important;
  }
}

.cs-link {
  color: #4568e0;
  text-decoration: underline;
  cursor: pointer;
}

.bom-map-popup-container {
  height: 100%;
  width: 100%;

  .bom-map-outer-wrapper {
    border: 1px solid #bbc6d9;
    border-bottom: none;

    &:before {
      border: none !important;
    }
  }

  .grid-sort-reason {
    height: 100%;
  }
}

.info-modal-content-wrapper {
  height: 100%;
}

.demand-modal-content-wrapper {
  height: 100%;
}
</style>
