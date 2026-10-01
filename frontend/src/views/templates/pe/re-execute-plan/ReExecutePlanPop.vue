<template>
  <Popup
    class="re-execute-plan-pop"
    :title="t('text-re_plan_excute')"
    v-model:visible="visibleModel"
    preset="no-footer"
    :width="reExecutePlanPopupWidth"
    :height="reExecutePlanPopupHeight"
    :maxWidth="reExecutePlanPopupWidth"
    :maxHeight="reExecutePlanPopupHeight"
    :resizeable="true"
    :closeOnOutsideClick="false"
    :use-v-show="true"
    :on-before-close="
      () => {
        if (alwaysEditedData?.length > 0 && !isClickCancel && !isClickConfirm) {
          showCheckClose = true;
          isClickCancel = false;
          isClickConfirm = false;
          return false;
        } else {
          isClickCancel = false;
          isClickConfirm = false;
          return true;
        }
      }
    "
  >
    <div class="popup-container">
      <!-- Step Indicator -->
      <div class="step-indicator-wrapper">
        <div :class="{ 'step-item-wrapper': true, 'current-step': currentStep === 1 }" @click="currentStep = 1">
          <div class="icon">
            <IconDataCheck
              :size="'20'"
              class="icon-data-check"
              :color="currentStep === 1 ? '#4568e0' : '#6a7184'"
            />
          </div>
          <div class="title">{{ t('text-demand_info_edit_check') }}</div>
        </div>
        <div class="step-item-line"></div>
        <div :class="{ 'step-item-wrapper': true, 'current-step': currentStep === 2 }" @click="currentStep = 2">
          <div class="icon">
            <IconResultCheck
              :size="'20'"
              class="icon-result-check"
              :color="currentStep === 2 ? '#4568e0' : '#6a7184'"
            />
          </div>
          <div class="title">{{ t('text-engine_re_execute') }}</div>
        </div>
      </div>

      <!-- Option Bar -->
      <div class="option-wrapper">
        <div class="option-breadcrumbs">
          <div class="parent-menu-name">{{ parentMenuName }}</div>
          <div>
            <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor"><path d="M4.5 2L8.5 6L4.5 10" stroke="currentColor" stroke-width="1.5" fill="none"/></svg>
          </div>
          <div class="accent-color">{{ menuName }}</div>
        </div>
        <div class="option-wrapper-content">
          <div v-show="currentStep === 1" class="demand-ver-text">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><circle cx="6" cy="6" r="5" stroke="#4568e0" stroke-width="1.2" fill="none"/><line x1="6" y1="4" x2="6" y2="6.5" stroke="#4568e0" stroke-width="1.2"/><circle cx="6" cy="8.2" r="0.6" fill="#4568e0"/></svg>
            <div class="demand-ver-text-content">
              {{ `${t('text-demand_ver_info')}: ${demandVer || '-'}` }}
            </div>
          </div>
          <Toggle v-show="currentStep === 1" :label="t('text-view_edit_data')" v-model="showEditedData" />
          <div v-show="currentStep === 1" class="splitter"></div>
          <Button :style="{ padding: '12px' }" v-show="currentStep === 1" @click="currentStep = 2">
            <span class="icon-arrow">&rarr;</span>
            <span class="button-text">{{ t('text-next') }}</span>
          </Button>
          <Button :style="{ padding: '12px' }" v-show="currentStep === 2" @click="currentStep = 1">
            <span class="icon-arrow">&larr;</span>
            <span class="button-text">{{ t('text-prev') }}</span>
          </Button>
        </div>
      </div>

      <!-- Content Wrapper -->
      <div class="content-wrapper">
        <!-- ========== STEP 1: Data Check Grid ========== -->
        <div v-show="currentStep === 1" class="re-execute-popup-grid-wrapper">
          <MozGrid
            :name="menuName + 're-execute-plan-pop-grid'"
            :coreConfig="popupGridConfig"
            height="100%"
            :loading="false"
            :useRowGroupSettings="false"
            :contextMenuConfig="{
              useViewSelectColumn: true,
              useBulkEditColumn: true,
            }"
            @ready="onPopupGridReady"
          />
        </div>

        <!-- ========== STEP 2: Engine Re-Execute Settings ========== -->
        <div v-show="currentStep === 2" class="re-execute-option-setting detail-setting-wrapper">
          <div class="setting-option-container">
            <!-- Description Card -->
            <div class="setting-option-item">
              <div class="option-title desc-title">
                {{ t('text-set_re_execute') }}
              </div>
              <div class="setting-desc">
                {{ t('desc-re_execute_plan_summary') }}
              </div>
            </div>

            <!-- Plan Default Info Card -->
            <div class="setting-option-item">
              <div class="option-title">
                {{ t('text-plan_default_info') }}
              </div>
              <div class="sub-content-wrapper">
                <!-- Plan Cycle -->
                <div class="sub-content-item">
                  <div class="sub-content-title-desc">
                    <div class="sub-title">
                      {{ t('text-plan_cycle') }}
                    </div>
                  </div>
                  <div class="sub-content">
                    <div class="sub-content-desc">
                      {{ t('desc-plancycle_setting') }}
                    </div>
                    <div class="sub-content-input-wrapper">
                      <Input v-model="reExecuteState.planCycleID" :disabled="true" :width="396" />
                    </div>
                  </div>
                </div>

                <!-- Plan Start Date / Period -->
                <div class="sub-content-item">
                  <div class="sub-content-title-desc">
                    <div class="sub-title">
                      {{ t('text-plan_start_date_period') }}
                    </div>
                  </div>
                  <div class="sub-content">
                    <div class="sub-content-desc">
                      <div class="margin-bottom-10">
                        {{ t('desc-re_execute_set_total_date') }}
                      </div>
                      <div>
                        {{ planDateRangeText }}
                      </div>
                    </div>
                    <div class="sub-content-input-wrapper">
                      <DateInput v-model="reExecuteState.startDate" :width="122" />
                      <TimePicker v-model="reExecuteState.planStartTime" :width="'85px'" />
                      <span class="sub-content-text">{{ t('text-from') }}</span>
                      <NumberInput v-model="reExecuteState.period" :min="1" :step="1" />
                      <span class="sub-content-text">{{ t('text-during_date') }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Edited Demand Info Card -->
            <div class="setting-option-item">
              <div class="option-title">
                {{ t('text-edited_demand_info_setting') }}
              </div>
              <div class="sub-content-wrapper">
                <!-- Demand Version Name -->
                <div class="sub-content-item">
                  <div class="sub-content-title-desc">
                    <div class="sub-title">
                      {{ t('text-demand_ver_name') }}
                    </div>
                  </div>
                  <div class="sub-content valid-wrapper">
                    <div class="sub-content-desc">
                      <div class="sub-content-desc-detail">
                        <div class="margin-bottom-10">{{ t('desc-input_edited_demand_ver') }}</div>
                        <div>{{ `${t('desc-auto_naming_if_empty')} (${t('desc-example')}: ${autoDemandVer})` }}</div>
                      </div>
                    </div>
                    <Input
                      :width="696"
                      v-model="reExecuteState.demandVer"
                      :disabled="false"
                      :placeholder="autoDemandVer"
                      :rules="[{
                        validator: async (value: string) => {
                          if (!value) return true;
                          try {
                            const res = await fetchDemandVerValidCheck({ demand_ver: value });
                            if (res?.data?.length > 0) return '이미 존재하는 수요 버전입니다.';
                            return true;
                          } catch { return true; }
                        }
                      }]"
                    />
                  </div>
                </div>

                <!-- Demand Version Description -->
                <div class="sub-content-item">
                  <div class="sub-content-title-desc">
                    <div class="sub-title">
                      {{ t('text-demand_ver_desc_placeholder') }}
                    </div>
                  </div>
                  <div class="sub-content textarea-wrapper">
                    <div class="sub-content-desc">
                      {{ t('desc-put_edidted_demand_ver_simple_desc') }}
                    </div>
                    <div class="sub-content-input-wrapper">
                      <TextArea
                        v-model="reExecuteState.demandDesc"
                        :disabled="false"
                        :width="396"
                        :height="68"
                        :placeholder="t('desc-example_demand_ver_desc')"
                      />
                    </div>
                  </div>
                </div>

                <!-- Edit Summary -->
                <div class="sub-content-item">
                  <div class="sub-content-title-desc">
                    <div class="sub-title">
                      {{ t('text-mainly_changed_things_summary') }}
                    </div>
                    <div class="sub-content sub-desc style-grid">
                      <div class="sub-desc-detail">
                        <span class="sub-desc-detail-label">{{ t('text-edited_row_data_prefix') }}</span>
                        <span class="sub-desc-detail-value">{{ `${alwaysEditedData.length}${t('text-case')}` }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Edited Demand Detail Toggle -->
                <div class="sub-content-item">
                  <div class="sub-content-title-desc toggle-wrapper">
                    <div class="sub-title style-flex style-flex-end">
                      <div>
                        <div>{{ t('text-open-demand-info-detail-view') }}</div>
                      </div>
                      <div class="sub-title-detail-toggle-wrapper">
                        <div class="sub-title-detail">{{ t('desc-edited_demand_info_detail_list') }}</div>
                        <Toggle v-model="reExecuteState.viewDemandDetail" />
                      </div>
                    </div>
                    <!-- 숨겨진 채로 그리드를 만들면 크기가 0 으로 잡히므로 펼칠 때 만든다. -->
                    <div v-if="reExecuteState.viewDemandDetail" class="sub-edited-demand-grid-wrapper">
                      <MozGrid
                        :name="menuName + 'sub-edited-demand-grid'"
                        :coreConfig="subEditedGridConfig"
                        height="100%"
                        :loading="false"
                        :useToolBox="false"
                        :useRowGroupSettings="false"
                        :contextMenuConfig="{ useViewSelectColumn: true }"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Data & Execution Setting Card -->
            <div class="setting-option-item">
              <div class="option-title">
                {{ t('text-data_and_execution_setting') }}
              </div>
              <div class="sub-content-wrapper">
                <!-- Demand Version (read-only) -->
                <div class="sub-content-item">
                  <div class="sub-content-title-desc">
                    <div class="sub-title">
                      {{ t('text-demand_ver') }}
                    </div>
                  </div>
                  <div class="sub-content valid-wrapper">
                    <div class="sub-content-desc">
                      {{ t('desc-example_reflect_current_demand_ver') }}
                    </div>
                    <Input
                      :width="696"
                      v-model="reExecuteState.demandVer"
                      :disabled="true"
                      :placeholder="autoDemandVer"
                    />
                  </div>
                </div>

                <!-- Execution Flow Setting -->
                <div class="sub-content-item" style="gap: 16px">
                  <div class="sub-content-title-desc">
                    <div class="sub-title">
                      {{ t('text-execution_flow_setting') }}
                    </div>
                    <div class="sub-desc">
                      {{ t('text-replan_execution_flow_desc') }}
                      <div class="sub-desc-toggle">
                        <Toggle v-model="isAdvancedOption" :label="t('text-advanced_option')" />
                      </div>
                    </div>
                  </div>

                  <!-- Simple mode: Execution Flow Select -->
                  <div class="sub-content" v-if="!isAdvancedOption">
                    <div class="sub-content-desc">{{ t('msg-replan_execution_flow') }}</div>
                    <Select
                      :itemsSource="executionFlowSource"
                      keyProp="execution_flow_id"
                      displayProp="execution_flow_name"
                      :width="'396px'"
                      v-model="reExecuteState.executionFlowID"
                      :placeholder="!executionFlowSource.length ? `(${t('msg-no_execution_flow')})` : ''"
                    />
                  </div>

                  <!-- Advanced mode: Individual Scenario Selects -->
                  <div class="sub-content" v-else>
                    <div class="sub-content-flex">
                      <Select
                        v-model="reExecuteState.inboundScenarioID"
                        :itemsSource="inboundSource"
                        keyProp="inboundScenarioID"
                        displayProp="inboundScenarioName"
                        :width="'233px'"
                        :label="t('text-inbound_scenario')"
                      />
                      <Select
                        :label="t('text-engine_scenario')"
                        v-model="reExecuteState.scenarioID"
                        :itemsSource="scenarioList"
                        keyProp="scenarioID"
                        displayProp="scenarioName"
                        :class="'select-wrapper'"
                        :width="'233px'"
                      />
                      <div class="moz-switch-wrapper">
                        <Toggle v-model="outboundScenarioIDForToggle" :label="t('text-outbound')" />
                      </div>
                    </div>
                  </div>
                </div>

                <!-- View Execution Flow Detail -->
                <div class="sub-content-item" style="gap: 14px">
                  <div class="sub-content-title-desc">
                    <div class="sub-title">
                      {{ t('text-view_selected_execution_flow_detail') }}
                    </div>
                    <div class="sub-desc">
                      {{ t('desc-view_selected_execution_flow_detail') }}
                      <div class="sub-desc-toggle">
                        <Toggle v-model="reExecuteState.viewScenarioDetail" />
                      </div>
                    </div>
                  </div>
                  <!-- 원본 ExecutionFlowMasterDetailSummary: 인바운드 / 엔진 / 아웃바운드 탭 구조.
                       운영 동작과 동일하게 토글과 무관하게 항상 노출한다 (토글은 legacy UI). -->
                  <div class="execution-flow-summary-placeholder">
                    <Tab
                      style="flex: 1; overflow: hidden"
                      v-model="flowSummaryTab"
                      :itemSource="[
                        { id: 'inbound', text: t('text-execution_flow_inbound') },
                        { id: 'engine', text: t('text-engine') },
                        { id: 'outbound', text: t('text-outbound') },
                      ]"
                    >
                      <!-- ===== Inbound 탭 ===== -->
                      <template #inbound>
                        <div class="plan-execute-inner-wrapper">
                          <span
                            :class="{
                              'plan-execute-desc-text': true,
                              'flow-master-summary-desc-empty': !executionFlowDataResult.inboundDesc,
                            }"
                            v-if="
                              executionFlowDataResult.inboundID &&
                              executionFlowDataResult.inboundID !== 'use_aps_data' &&
                              executionFlowDataResult.inboundID !== 'use_ver_data'
                            "
                          >
                            {{
                              executionFlowDataResult.inboundDesc ||
                              `(${t('desc-inbound_scenario_no_description')})`
                            }}
                          </span>
                          <div class="plan-execute-desc-grid-outer-wrapper">
                            <div class="plan-execute-desc-grid-wrapper">
                              <!-- 1) 실행 플로우 단계 + 선택된 inbound scenarioName -->
                              <div
                                class="plan-execute-desc-grid-item-wrapper single-row-grid"
                                :style="executionFlowDataResult.inboundID ? {} : { flex: 1 }"
                              >
                                <MozGrid
                                  v-bind="INFO_GRID_UI"
                                  :coreConfig="inboundStepGridConfig"
                                  :name="'re-execute-plan-flow-inbound'"
                                >
                                  <CellTemplate field="_step">
                                    <span class="cell-text">{{ t('text-execution_flow_inbound') }}</span>
                                  </CellTemplate>
                                  <CellTemplate field="inboundID" #default="{ rowData }">
                                    <span class="cell-text" v-if="rowData.inboundID === 'use_aps_data'">{{
                                      t('text-use_aps_data')
                                    }}</span>
                                    <span class="cell-text" v-else-if="rowData.inboundID === 'use_ver_data'">{{
                                      t('text-use_ver_data')
                                    }}</span>
                                    <span class="cell-text" v-else-if="!rowData.inboundID">
                                      <IconClose color="#dc5a5a" size="12" />
                                    </span>
                                    <span class="cell-text" v-else>{{ rowData.inboundName }}</span>
                                  </CellTemplate>
                                </MozGrid>
                              </div>

                              <!-- 2) 참조 데이터 설정 (tableFilterList / tableFilterType) -->
                              <div
                                class="plan-execute-desc-grid-item-wrapper single-row-grid"
                                v-if="executionFlowDataResult.inboundID && inboundItemOptions?.tableFilterList"
                              >
                                <MozGrid
                                  v-bind="INFO_GRID_UI"
                                  :coreConfig="inboundRefGridConfig"
                                  :name="'re-execute-plan-flow-inbound-ref'"
                                >
                                  <CellTemplate field="tableFilterType" #default="{ rowData }">
                                    <span class="cell-text">{{
                                      rowData.tableFilterType === 'Include'
                                        ? t('text-include_table')
                                        : t('text-exclude_table')
                                    }}</span>
                                  </CellTemplate>
                                </MozGrid>
                              </div>

                              <!-- 3) Inbound config tree (OPER RES PROP VALUE / CALENDAR / SYSTEM 등) -->
                              <div
                                class="plan-execute-desc-grid-item-wrapper inbound-treegrid-wrapper"
                                style="flex: 1"
                                v-if="
                                  executionFlowDataResult.inboundID &&
                                  executionFlowDataResult.inboundID !== 'use_aps_data' &&
                                  executionFlowDataResult.inboundID !== 'use_ver_data' &&
                                  inboundItemOptions?.list?.length
                                "
                              >
                                <MozGrid
                                  class="inbound-treegrid"
                                  v-bind="INFO_GRID_UI"
                                  :coreConfig="inboundTreeGridConfig"
                                  :height="inboundTreeHeight"
                                  :name="'re-execute-plan-flow-inbound-tree'"
                                >
                                  <CellTemplate field="optionValue" #default="{ rowData }">
                                    <span class="cell-text">
                                      <IconCheck v-if="rowData.optionValue === true" color="#4568e0" size="14" />
                                      <IconClose v-if="rowData.optionValue === false" color="#dc5a5a" size="12" />
                                    </span>
                                  </CellTemplate>
                                </MozGrid>
                              </div>

                              <!-- 4) 데이터 저장 여부 -->
                              <div
                                class="plan-execute-desc-grid-item-wrapper single-row-grid"
                                v-if="
                                  executionFlowDataResult.inboundID &&
                                  executionFlowDataResult.inboundID !== 'use_aps_data' &&
                                  executionFlowDataResult.inboundID !== 'use_ver_data' &&
                                  typeof inboundItemOptions?.saveCfgValue === 'boolean'
                                "
                              >
                                <MozGrid
                                  class="inbound-treegrid"
                                  v-bind="INFO_GRID_UI"
                                  :coreConfig="inboundSaveGridConfig"
                                  :name="'re-execute-plan-flow-inbound-save'"
                                >
                                  <CellTemplate field="_storage" #default="{ rowData }">
                                    <span class="cell-text" v-if="typeof rowData.saveCfgValue === 'boolean'">{{
                                      t('desc-data_storage')
                                    }}</span>
                                  </CellTemplate>
                                  <CellTemplate field="saveCfgValue" #default="{ rowData }">
                                    <span class="cell-text">
                                      <IconCheck v-if="rowData.saveCfgValue" color="#4568e0" size="14" />
                                      <IconClose v-else-if="rowData.saveCfgValue === false" color="#dc5a5a" size="12" />
                                    </span>
                                  </CellTemplate>
                                </MozGrid>
                              </div>
                            </div>
                          </div>
                        </div>
                      </template>

                      <!-- ===== Engine 탭 ===== -->
                      <template #engine>
                        <div class="plan-execute-inner-wrapper">
                          <span
                            :class="{
                              'plan-execute-desc-text': true,
                              'flow-master-summary-desc-empty': !executionFlowDataResult.scenarioDesc,
                            }"
                          >
                            {{
                              executionFlowDataResult.scenarioDesc ||
                              `(${t('desc-engine_scenario_no_description')})`
                            }}
                          </span>
                          <div class="plan-execute-desc-grid-outer-wrapper">
                            <div class="plan-execute-desc-grid-wrapper">
                              <!-- 엔진 기본 정보 -->
                              <div
                                class="plan-execute-desc-grid-item-wrapper single-row-grid"
                                :style="executionFlowDataResult.scenarioID ? {} : { flex: 1 }"
                              >
                                <MozGrid
                                  v-bind="INFO_GRID_UI"
                                  :coreConfig="engineStepGridConfig"
                                  :name="'re-execute-plan-flow-engine'"
                                >
                                  <CellTemplate field="_step">
                                    <span class="cell-text">{{ t('text-engine') }}</span>
                                  </CellTemplate>
                                  <CellTemplate field="scenarioID" #default="{ rowData }">
                                    <span class="cell-text" v-if="rowData.scenarioID">{{ rowData.scenarioName }}</span>
                                    <span class="cell-text" v-else>
                                      <IconClose color="#dc5a5a" size="12" />
                                    </span>
                                  </CellTemplate>
                                </MozGrid>
                              </div>
                              <!-- 글로벌 옵션 (scenarioConfigSource) -->
                              <div
                                class="plan-execute-desc-grid-item-wrapper"
                                style="flex: 1"
                                v-if="executionFlowDataResult.scenarioID && scenarioConfigSource.length"
                              >
                                <MozGrid
                                  v-bind="INFO_GRID_UI"
                                  :coreConfig="engineGlobalGridConfig"
                                  :height="engineGlobalHeight"
                                  :name="'re-execute-plan-flow-engine-global'"
                                >
                                  <CellTemplate field="optionValue" #default="{ rowData }">
                                    <span class="cell-text" v-if="rowData.uiType !== 'TOGGLE'">{{
                                      rowData.optionValue
                                    }}</span>
                                    <span class="cell-text" v-else>
                                      <IconCheck v-if="rowData.optionValue === 'Y'" color="#4568e0" size="14" />
                                      <IconClose v-if="rowData.optionValue === 'N'" color="#dc5a5a" size="12" />
                                    </span>
                                  </CellTemplate>
                                </MozGrid>
                              </div>
                              <!-- 시나리오 모듈 리스트 (phaseColumns 동적) -->
                              <div
                                class="plan-execute-desc-grid-item-wrapper"
                                style="flex: 1"
                                v-if="executionFlowDataResult.scenarioID && scenarioModuleDataSource.length"
                              >
                                <MozGrid
                                  v-bind="INFO_GRID_UI"
                                  :coreConfig="engineModuleGridConfig"
                                  :height="engineModuleHeight"
                                  :name="'re-execute-plan-flow-engine-modules'"
                                  @ready="onScenarioModuleReady"
                                >
                                  <CellTemplate
                                    v-for="col in phaseColumns"
                                    :key="`phase-${String(col.binding)}-${scenarioModuleDataSource.length}`"
                                    :field="String(col.binding)"
                                    #default="{ rowData }"
                                  >
                                    <span class="cell-text" v-if="rowData.ui_type !== 'TOGGLE'">{{
                                      rowData[String(col.binding)]
                                    }}</span>
                                    <span class="cell-text" v-else>
                                      <IconCheck
                                        v-if="rowData[String(col.binding)] === 'Y'"
                                        color="#4568e0"
                                        size="14"
                                      />
                                      <IconClose
                                        v-if="rowData[String(col.binding)] === 'N'"
                                        color="#dc5a5a"
                                        size="12"
                                      />
                                    </span>
                                  </CellTemplate>
                                </MozGrid>
                              </div>
                            </div>
                          </div>
                        </div>
                      </template>

                      <!-- ===== Outbound 탭 ===== -->
                      <template #outbound>
                        <div class="plan-execute-inner-wrapper">
                          <div class="plan-execute-desc-grid-outer-wrapper">
                            <div class="plan-execute-desc-grid-wrapper">
                              <div class="plan-execute-desc-grid-item-wrapper single-row-grid">
                                <MozGrid
                                  v-bind="INFO_GRID_UI"
                                  :coreConfig="outboundStepGridConfig"
                                  :name="'re-execute-plan-flow-outbound'"
                                >
                                  <CellTemplate field="_step">
                                    <span class="cell-text">{{ t('text-outbound') }}</span>
                                  </CellTemplate>
                                  <CellTemplate field="outboundID" #default="{ rowData }">
                                    <span class="cell-text">
                                      <IconCheck v-if="rowData.outboundID" color="#4568e0" size="14" />
                                      <IconClose v-else color="#dc5a5a" size="12" />
                                    </span>
                                  </CellTemplate>
                                </MozGrid>
                              </div>
                            </div>
                          </div>
                        </div>
                      </template>
                    </Tab>
                  </div>
                </div>

                <!-- Plan Description -->
                <div class="sub-content-item">
                  <div class="sub-content-title-desc">
                    <div class="sub-title">
                      {{ t('text-plan_desc_placeholder') }}
                    </div>
                  </div>
                  <div class="sub-content textarea-wrapper">
                    <div class="sub-content-desc">
                      {{ t('desc-put_desc_for_identify_plan') }}
                    </div>
                    <TextArea
                      v-model="reExecuteState.planDesc"
                      :disabled="false"
                      :height="68"
                      :width="696"
                      :placeholder="t('desc-sample_first_week_regular_plan')"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Execute / Cancel Buttons -->
            <div class="execute-button-wrapper">
              <Button
                :text="t('text-Cancel')"
                :width="80"
                @click="
                  () => {
                    isClickCancel = true;
                    if (alwaysEditedData?.length > 0) {
                      checkCloseBefore();
                    } else {
                      closePopup();
                    }
                  }
                "
                :type="'outline'"
              />
              <Button
                :text="t('text-plan_excute')"
                class="execute-button"
                :disabled="isDuplicated || isExecuting"
                :loading="isExecuting"
                @click="
                  () => {
                    onClickConfirm();
                  }
                "
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </Popup>

  <!-- Confirm Close Dialog -->
  <Popup
    :title="t('text-warning')"
    :dialogMessage="t('desc-confirm_cancel_re_execute_plan')"
    preset="confirm"
    :width="420"
    :dialogIcon="'warning'"
    :onConfirm="
      () => {
        closePopup();
      }
    "
    v-model:visible="showCheckClose"
    :onCancel="
      () => {
        showCheckClose = false;
      }
    "
  >
  </Popup>
</template>

<script setup lang="ts">
import { computed, ref, shallowRef, toRaw, watch } from "vue";
import { useTranslation } from "i18next-vue";
import { CellTemplate, MozGrid } from "@vmscloud/moz-ui-grid-vue";
import type { FieldDef, GridChrome, MozGridCoreProps, PureSheet } from "@vmscloud/moz-ui-grid-vue";
import { IconCheck, IconClose, IconDataCheck, IconResultCheck } from "@moz-shared/icons";
import {
  Button,
  DateInput,
  Input,
  NumberInput,
  Popup,
  Select,
  Tab,
  TextArea,
  TimePicker,
  Toggle,
} from "@vmscloud/moz-ui-components-vue";
import dayjs from "dayjs";
import {
  buildDemandFields,
  postReExecutePlan,
  fetchDemandSource,
  fetchDemandVerValidCheck,
  type ExecutionFlowMasterType,
  type ScenarioMasterType,
  type InboundItemType,
} from "./reExecutePlan";

// ===== Width helper (원본 getWidthByKey 대체) =====
const WIDTH_MAP: Record<string, number> = {
  S1: 80, S2: 100, S3: 120,
  D1: 130, D2: 110, D3: 100,
  DF: 120, N2: 90, F3: 120,
};
const getWidthByKey = (key: string) => WIDTH_MAP[key] ?? 100;

// ===== Local type aliases =====
export type ExecutionFlowType = ExecutionFlowMasterType;
export type ScenarioType = ScenarioMasterType;
export type DemandDataRow = Record<string, any>;
export interface ReExecuteStateType {
  planCycleID: string;
  startDate: any;
  planStartTime: string;
  period: number | string;
  demandVer: string;
  demandDesc: string;
  planDesc: string;
  executionFlowID: string;
  inboundScenarioID: string | null;
  scenarioID: string | null;
  outboundScenarioID: string | null;
  viewDemandDetail: boolean;
  viewScenarioDetail: boolean;
  editSummary: {
    dueDateCnt: number;
    delayCnt: number;
    shorteningCnt: number;
    maxDueDateCnt: number;
    demandPriorityCnt: number;
  };
  [key: string]: any;
}

const { t } = useTranslation();

// ===== Props =====
interface Props {
  visible: boolean;
  // Menu info (replaces store dependencies)
  parentMenuName?: string;
  menuName?: string;
  // Plan cycle info
  planVer?: string;
  planStartDate?: string;
  demandVer?: string;
  factoryStartTime?: string;
  planCycleId?: string;
  // User info
  userId?: string;
  userEmail?: string;
  // Project info
  tenantNM?: string;
  projectNM?: string;
  tenantID?: string;
  // Data sources
  popupDataSource: any[];
  demandSource: any[];
  alwaysEditedData: any[];
  // demand_id → 메인 그리드에서 수정된 필드 목록 (수정 데이터 상세 그리드 강조용)
  editedDemandFields?: Record<string, string[]>;
  propColumns?: any[];
  // Execution flow & scenario sources
  executionFlowSource?: ExecutionFlowType[];
  scenarioList?: ScenarioType[];
  inboundSource?: InboundItemType[];
  // 시나리오 모듈 상세 (원본 ExecutionFlowMasterDetailSummary의 하단 그리드)
  scenarioModuleDataSource?: any[];
  scenarioConfigSource?: any[];
  phaseColumns?: { binding: string | number; header: string; width: string | number }[];
  // inbound 탭 전용 (PlmInboundScenarioMaster/Config 응답 → 트리/데이터 저장 그리드)
  inboundItemOptions?: {
    list?: any[];
    tableFilterList?: any[];
    tableFilterType?: string;
    saveCfgValue?: boolean;
    [key: string]: any;
  };
  // Initial state
  initialReExecuteState?: Partial<ReExecuteStateType>;
}

const props = withDefaults(defineProps<Props>(), {
  parentMenuName: "",
  menuName: "",
  planVer: "",
  planStartDate: "",
  demandVer: "",
  factoryStartTime: "06:00",
  planCycleId: "",
  userId: "",
  userEmail: "",
  tenantNM: "",
  projectNM: "",
  tenantID: "",
  editedDemandFields: () => ({}),
  propColumns: () => [],
  executionFlowSource: () => [],
  scenarioList: () => [],
  inboundSource: () => [],
  scenarioModuleDataSource: () => [],
  scenarioConfigSource: () => [],
  phaseColumns: () => [],
  inboundItemOptions: () => ({}),
});

const emit = defineEmits<{
  (e: "update:visible", value: boolean): void;
  (e: "close"): void;
  (e: "executed", param: any): void;
  // 팝업 그리드에서 값이 바뀐 수요 행(현재 값 전체). 수정을 되돌린 행은 원래 값으로 보낸다.
  (e: "demand-edited", rows: Record<string, any>[]): void;
  (e: "data-refreshed"): void;
}>();

// ===== Visible Model =====
const visibleModel = computed({
  get: () => props.visible,
  set: (v: boolean) => emit("update:visible", v),
});

// ===== Reactive State =====
const currentStep = ref(1);
const showEditedData = ref(false);
const showCheckClose = ref(false);
const isClickCancel = ref(false);
const isClickConfirm = ref(false);
const isDuplicated = ref(false);
const isAdvancedOption = ref(false);
// 확정 버튼 클릭 → postReExecutePlan 요청이 진행중인 동안 true. moz Button 의
// :loading 에 연결되어 스피너 + disabled 처리된다.
const isExecuting = ref(false);

// composable(useReExecutePlanQuery)과 동일한 초기값 규칙:
//   startDate   = dayjs() (오늘)
//   period      = 오늘~월말까지 남은 일수 (inclusive)
//   planStartTime = props.factoryStartTime 없으면 현재 시각
// 원본은 단일 reExecuteState를 공유하지만 포팅본은 팝업이 로컬 ref라, 최소한 초기값이
// composable과 어긋나지 않도록 맞춘다.
const _initNow = dayjs();
const _initPeriod = (() => {
  const today = _initNow.toDate();
  const end = new Date(today.getFullYear(), today.getMonth() + 1, 0);
  return (
    Math.ceil((end.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)) + 1
  );
})();

const reExecuteState = ref<ReExecuteStateType>({
  planCycleID: props.planCycleId || "",
  startDate: _initNow,
  planStartTime: props.factoryStartTime || _initNow.format("HH:mm"),
  period: _initPeriod,
  demandVer: "",
  demandDesc: "",
  planDesc: "",
  executionFlowID: "",
  inboundScenarioID: null,
  scenarioID: null,
  outboundScenarioID: null,
  viewDemandDetail: false,
  viewScenarioDetail: false,
  editSummary: {
    dueDateCnt: 0,
    delayCnt: 0,
    shorteningCnt: 0,
    maxDueDateCnt: 0,
    demandPriorityCnt: 0,
  },
});

// Apply initial state from props
if (props.initialReExecuteState) {
  Object.assign(reExecuteState.value, props.initialReExecuteState);
}

// ===== Computed =====
const reExecutePlanPopupWidth = computed(() => Math.floor(window.innerWidth * 0.6));
const reExecutePlanPopupHeight = computed(() => Math.floor(window.innerHeight * 0.8));

const autoDemandVer = computed(() => {
  const now = dayjs();
  return `DV_${now.format("YYYYMMDD_HHmmss")}`;
});

const planDateRangeText = computed(() => {
  const start = reExecuteState.value.startDate;
  if (!start || !start.format) return "";
  const end = start.add(Number(reExecuteState.value.period) - 1, "day");
  return `( ${start.format("YYYY-MM-DD")} ~ ${end.format("YYYY-MM-DD")} )`;
});

const outboundScenarioIDForToggle = computed({
  get() {
    return !!reExecuteState.value.outboundScenarioID;
  },
  set(value: boolean) {
    reExecuteState.value.outboundScenarioID = value ? "useOutbound" : null;
  },
});

const flowOptions = computed(() => {
  if (isAdvancedOption.value) {
    return {
      inboundScenario: reExecuteState.value.inboundScenarioID,
      inboundScenarioID: reExecuteState.value.inboundScenarioID,
      scenarioID: reExecuteState.value.scenarioID,
      outboundScenarioID: reExecuteState.value.outboundScenarioID,
      executionFlowID: null,
    };
  }
  return {
    executionFlowID: reExecuteState.value.executionFlowID,
    inboundScenario: null,
    inboundScenarioID: null,
    scenarioID: null,
    outboundScenarioID: null,
  };
});

// Computed names for the execution flow summary
const selectedExecutionFlowName = computed(() => {
  const flowId = reExecuteState.value.executionFlowID;
  if (!flowId) return "";
  const found = props.executionFlowSource.find((f) => f.execution_flow_id === flowId);
  return found?.execution_flow_name || flowId;
});

const selectedInboundName = computed(() => {
  const id = reExecuteState.value.inboundScenarioID;
  if (!id) return "";
  const found = props.inboundSource.find((s) => s.inboundScenarioID === id);
  return found?.inboundScenarioName || id;
});

const selectedScenarioName = computed(() => {
  const id = reExecuteState.value.scenarioID;
  if (!id) return "";
  const found = props.scenarioList.find((s) => s.scenarioID === id);
  return found?.scenarioName || id;
});

// ===== Execution Flow Detail Tab =====
const flowSummaryTab = ref<string>("inbound");

// 원본 ExecutionFlowMasterDetailSummary 의 executionFlowDataResult 와 동일한 평탄화 구조.
// 팝업에서는 선택된 Flow 기준으로 { inboundID, inboundName, inboundDesc, scenarioID, scenarioName,
// scenarioDesc, outboundID } 를 단일 객체로 만들어 하단 그리드 3개에 공급한다.
const executionFlowDataResult = computed(() => {
  if (isAdvancedOption.value) {
    const inboundId = reExecuteState.value.inboundScenarioID ?? "";
    const scenarioId = reExecuteState.value.scenarioID ?? "";
    const outboundId = reExecuteState.value.outboundScenarioID ?? "";
    const inbound = props.inboundSource.find((s) => s.inboundScenarioID === inboundId);
    const scenario = props.scenarioList.find((s) => s.scenarioID === scenarioId);
    return {
      inboundID: inboundId,
      inboundName: inbound?.inboundScenarioName ?? inboundId,
      inboundDesc: (inbound as any)?.inboundScenarioDesc ?? "",
      scenarioID: scenarioId,
      scenarioName: scenario?.scenarioName ?? scenarioId,
      scenarioDesc: (scenario as any)?.scenarioDesc ?? "",
      outboundID: outboundId,
    };
  }
  const flowId = reExecuteState.value.executionFlowID;
  const flow = props.executionFlowSource.find((f) => f.execution_flow_id === flowId) as any;
  const inboundId = flow?.inbound_scenario_id ?? flow?.inboundScenarioID ?? "";
  // 원본 ExecutionFlowMasterType 에서 엔진 시나리오 필드는 engine_scenario_id.
  //   과거 scenario_id 로 찾고 있어서 scenarioID 가 항상 비어 엔진/아웃바운드 탭이 비어보였다.
  const scenarioId =
    flow?.engine_scenario_id ??
    flow?.scenario_id ??
    flow?.engineScenarioID ??
    flow?.scenarioID ??
    "";
  const outboundId = flow?.outbound_scenario_id ?? flow?.outboundScenarioID ?? "";
  const inbound = props.inboundSource.find((s) => s.inboundScenarioID === inboundId);
  const scenario = props.scenarioList.find((s) => s.scenarioID === scenarioId);
  return {
    inboundID: inboundId,
    inboundName:
      inbound?.inboundScenarioName ??
      flow?.inbound_scenario_name ??
      flow?.inboundScenarioName ??
      inboundId,
    inboundDesc:
      (inbound as any)?.inboundScenarioDesc ??
      flow?.inbound_scenario_desc ??
      flow?.inboundScenarioDesc ??
      "",
    scenarioID: scenarioId,
    scenarioName:
      scenario?.scenarioName ?? flow?.scenario_name ?? flow?.scenarioName ?? scenarioId,
    scenarioDesc:
      (scenario as any)?.scenarioDesc ?? flow?.scenario_desc ?? flow?.scenarioDesc ?? "",
    outboundID: outboundId,
  };
});

// 각 multi-row 그리드 높이 계산: 헤더 1 + 데이터 행 수만큼 확장.
//   그리드 내부에 scroll 이 생기지 않도록 전체 행을 다 펼친 높이를 준다.
//   행 높이 ≒ 28px, header padding 포함 여유 40px.
const ROW_H = 28;
const HEADER_H = 40;
const computeAutoHeight = (rowCount: number) =>
  `${HEADER_H + Math.max(1, rowCount) * ROW_H}px`;

// Inbound tree grid: Category + 확장된 Menu 자식까지 합친 총 가시 row 수.
const inboundTreeHeight = computed(() => {
  const list = props.inboundItemOptions?.list ?? [];
  let count = 0;
  for (const item of list) {
    count += 1;
    if (Array.isArray(item.children)) {
      count += item.children.length;
    }
  }
  return computeAutoHeight(count);
});

// Engine global options & module 그리드: items length 기반.
const engineGlobalHeight = computed(() =>
  computeAutoHeight(props.scenarioConfigSource?.length ?? 0),
);
const engineModuleHeight = computed(() =>
  computeAutoHeight(props.scenarioModuleDataSource?.length ?? 0),
);

// ===== Execution Flow Summary grid helpers (원본 ExecutionFlowMasterDetailSummary 이식) =====
// 읽기 전용 요약 그리드 공통 UI: 툴박스·푸터·컨텍스트 메뉴·정렬 없음.
const INFO_GRID_UI = {
  height: "100%",
  loading: false,
  useToolBox: false,
  useToolBoxSetting: false,
  useExtendFooter: false,
  useContextMenu: false,
  useSort: false,
};

// 요약 데이터에는 행 식별 필드가 없어 순번 키를 붙인다.
const withRowKey = (rows: any[]) => rows.map((row, index) => ({ ...row, _rowKey: index }));

const infoGridConfig = (
  data: any[],
  fields: FieldDef[],
  extra: Partial<MozGridCoreProps> = {},
): MozGridCoreProps => ({
  mode: "flat",
  keyFields: ["_rowKey"],
  data: withRowKey(data),
  fields: fields.map((field) => ({ sortable: false, showFilterIcon: false, ...field })),
  ...extra,
});

// 실행 플로우 단계 컬럼(_step)은 데이터 없이 템플릿으로 단계명을 그린다.
const stepField = (): FieldDef => ({
  id: "_step",
  header: t("text-execution_flow_step"),
  dataType: "string",
  flex: 1,
});
const optionValueField = (id: string, width = 160): FieldDef => ({
  id,
  header: t("text-option_value"),
  dataType: "string",
  width,
  align: "center",
});

const inboundStepGridConfig = computed(() =>
  infoGridConfig([executionFlowDataResult.value], [stepField(), optionValueField("inboundID")]),
);

const inboundRefGridConfig = computed(() =>
  infoGridConfig(
    [props.inboundItemOptions],
    [
      {
        id: "tableFilterList",
        header: t("text-ref_data_setting"),
        dataType: "string",
        flex: 1,
        mask: {
          type: "function",
          formatter: (value: unknown) =>
            Array.isArray(value) ? value.join(",") : String(value ?? ""),
        },
      },
      optionValueField("tableFilterType"),
    ],
  ),
);

// Inbound tree grid: Category 아래 Menu 자식을 부모 키로 펼친 평탄 데이터.
const inboundTreeRows = computed(() => {
  const rows: any[] = [];
  (props.inboundItemOptions?.list ?? []).forEach((item: any, index: number) => {
    const { children, ...parent } = item;
    const parentKey = String(index);
    rows.push({ ...parent, _treeKey: parentKey, _parentKey: null });
    (Array.isArray(children) ? children : []).forEach((child: any, childIndex: number) => {
      rows.push({ ...child, _treeKey: `${parentKey}-${childIndex}`, _parentKey: parentKey });
    });
  });
  return rows;
});

// 원본 onInboundDataProcessingGridFormatItem: 헤더 가운데 정렬, 데이터 셀 글자색 진하게.
const INBOUND_TREE_HEADER = { style: "justify-content: center; text-align: center" };
const INBOUND_TREE_CELL = { style: "color: #28364e" };

const inboundTreeGridConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: ["_treeKey"],
  data: inboundTreeRows.value,
  treeConfig: {
    idField: "_treeKey",
    parentField: "_parentKey",
    treeColumn: "multilingual",
    defaultExpandLevel: Infinity,
  },
  fields: [
    { id: "menuID", header: t("text-menu_id"), dataType: "string", hidden: true },
    {
      id: "multilingual",
      header: t("text-data_processing_list"),
      dataType: "string",
      flex: 1,
      headerAttributes: INBOUND_TREE_HEADER,
      cellAttributes: INBOUND_TREE_CELL,
    },
    {
      ...optionValueField("optionValue", 152),
      align: undefined,
      headerAttributes: INBOUND_TREE_HEADER,
      cellAttributes: INBOUND_TREE_CELL,
    },
  ].map((field): FieldDef => ({ sortable: false, showFilterIcon: false, ...field }) as FieldDef),
}));

const inboundSaveGridConfig = computed(() =>
  infoGridConfig(
    [props.inboundItemOptions],
    [
      { id: "_storage", header: t("text-data_storage"), dataType: "string", flex: 1 },
      optionValueField("saveCfgValue"),
    ],
  ),
);

const engineStepGridConfig = computed(() =>
  infoGridConfig([executionFlowDataResult.value], [stepField(), optionValueField("scenarioID")]),
);

const outboundStepGridConfig = computed(() =>
  infoGridConfig([executionFlowDataResult.value], [stepField(), optionValueField("outboundID")]),
);

// description 은 raw 문자열이 i18n key일 수 있어 t() 로 번역해 표시한다.
const descriptionField = (): FieldDef => ({
  id: "description",
  header: t("text-option"),
  dataType: "string",
  flex: 1,
  mask: {
    type: "function",
    formatter: (value: unknown) => (value != null ? t(String(value)) : ""),
  },
});

// scenarioModule 그리드 phase_N 셀 표시.
//   1) max_phase 를 초과한 phase_N 컬럼은 'union-null' 클래스로 음영 처리
//      (module A는 phase_2까지인데 module B가 phase_1까지인 경우, 테이블 합집합 union 이므로 B의 phase_2 셀을 빈 셀로 마킹).
//   2) option_id === 'DefaultRuleSet' + max_phase 내 phase 인데 값 없음 → 'error-mark' 로 표시.
const phaseCellAttributes = ({ rowData, columnId }: { rowData: Record<string, any>; columnId: string }) => {
  const phaseMatch = columnId.match(/^phase_(\d+)$/);
  if (!phaseMatch || rowData.max_phase == null) return undefined;
  const phaseN = parseInt(phaseMatch[1], 10);
  if (phaseN > rowData.max_phase) {
    return { class: "union-null" };
  }
  if (!rowData[columnId] && rowData.option_id === "DefaultRuleSet") {
    return { class: "error-mark error-cell" };
  }
  return undefined;
};

const engineGlobalGridConfig = computed(() =>
  infoGridConfig(
    props.scenarioConfigSource ?? [],
    [descriptionField(), optionValueField("optionValue", 152)],
    { resizableColumns: false },
  ),
);

const engineModuleGridConfig = computed(() =>
  infoGridConfig(props.scenarioModuleDataSource ?? [], [
    { id: "module_id", header: t("text-module_id"), dataType: "string", width: getWidthByKey("S3") },
    descriptionField(),
    ...props.phaseColumns.map(
      (col): FieldDef => ({
        ...optionValueField(String(col.binding), 152),
        header: t(col.header),
        cellAttributes: phaseCellAttributes,
      }),
    ),
  ]),
);

// Module 그리드는 첫 컬럼(module_id)의 같은 값을 병합한다. 원본과 동일한 처리.
const onScenarioModuleReady = (grid: PureSheet) => {
  grid.setMergeConfig({ type: "content", columns: ["module_id"] });
};

// ===== Demand Grid =====
// 팝업이 열릴 때의 수요 목록(메인 그리드 수정값 반영)으로 고정한다.
//   팝업에서 고친 값은 메인 그리드로 넘어가 다시 이 목록에 반영되는데, 그때마다 다시 로드하면
//   팝업 그리드의 변경 표시와 스크롤이 초기화되므로 열린 동안에는 다시 읽지 않는다.
const popupGridData = shallowRef<any[]>(props.popupDataSource);
const popupGridRows = computed(
  () => new Map<string, any>(popupGridData.value.map((row) => [String(row?.demand_id), row])),
);

const popupGridConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: ["demand_id"],
  editable: true,
  data: popupGridData.value,
  fields: buildDemandFields(t, props.propColumns, "popup"),
}));

// 수정 데이터 상세 그리드: 메인 그리드에서 수정된 셀을 강조한다.
const subEditedGridConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: ["demand_id"],
  data: props.alwaysEditedData,
  fields: [
    ...buildDemandFields(t, props.propColumns, "popup").map(
      (field): FieldDef => ({
        ...field,
        cellAttributes: ({ rowData, columnId }: { rowData: Record<string, any>; columnId: string }) =>
          props.editedDemandFields[String(rowData?.demand_id)]?.includes(columnId)
            ? { class: "edited-cell" }
            : undefined,
      }),
    ),
    { id: "legacy_data_version", header: t("text-legacy_data_version"), dataType: "string", width: getWidthByKey("S2"), readonly: true, hidden: true },
    { id: "interfaced_from", header: t("text-interfaced_from"), dataType: "string", width: getWidthByKey("S2"), readonly: true, hidden: true },
  ],
}));

const popupGrid = shallowRef<PureSheet | null>(null);
// 팝업에서 한 번이라도 수정된 행. 수정을 되돌리면 원래 값을 메인 그리드에 다시 보낸다.
const touchedDemandIds = new Set<string>();

const onPopupChanges = () => {
  const grid = popupGrid.value;
  if (!grid) return;

  const rows: Record<string, any>[] = [];
  const modifiedIds = new Set<string>();
  grid.changes.getAll().modified.forEach((row: { rowId: unknown; currentData: Record<string, any> }) => {
    const id = String(row.rowId);
    modifiedIds.add(id);
    touchedDemandIds.add(id);
    rows.push(row.currentData);
  });
  touchedDemandIds.forEach((id) => {
    if (modifiedIds.has(id)) return;
    const original = popupGridRows.value.get(id);
    if (original) rows.push(original);
    touchedDemandIds.delete(id);
  });

  if (rows.length) {
    emit("demand-edited", rows);
  }
};

// '수정 데이터 보기' — 수정된 수요(demand_id)만 남긴다. 사용자가 건 컬럼 필터와 별도 그룹이다.
const EDITED_FILTER_KEY = "editedOnly";
const NO_EDITED_DEMAND = "__no_edited_demand__";

const applyEditedFilter = async () => {
  const grid = popupGrid.value;
  if (!grid) return;

  const editedIDs = props.alwaysEditedData.map((row) => row?.demand_id);
  await grid.setFilterGroup(
    EDITED_FILTER_KEY,
    showEditedData.value
      ? {
          type: "values",
          priority: 0,
          applied: true,
          states: [
            {
              id: "demand_id",
              operator: "in",
              filterValue: editedIDs.length ? editedIDs : [NO_EDITED_DEMAND],
              sequence: 0,
            },
          ],
        }
      : null,
  );
};

const onPopupGridReady = (grid: PureSheet, chrome: GridChrome) => {
  popupGrid.value = grid;
  chrome.on("changes:changed", onPopupChanges);
  applyEditedFilter();
};

// ===== Close =====
const closePopup = () => {
  currentStep.value = 1;
  isClickCancel.value = false;
  isClickConfirm.value = false;
  showCheckClose.value = false;
  emit("update:visible", false);
  emit("close");
};

// ===== Confirm Close Check =====
const checkCloseBefore = async (): Promise<boolean> => {
  if (props.alwaysEditedData.length > 0) {
    showCheckClose.value = true;
    return false;
  }
  closePopup();
  return true;
};

// ===== Execute Confirm =====
const onClickConfirm = async () => {
  // Validation
  if (isAdvancedOption.value) {
    if (!flowOptions.value.inboundScenarioID && !flowOptions.value.scenarioID) {
      alert(t("msg-popup-execution_flow_info"));
      return false;
    }
  } else {
    if (!flowOptions.value.executionFlowID) {
      alert(t("msg-popup_no_execution_flow"));
      return false;
    }
  }

  const param = {
    query: {
      planVer: props.planVer,
      planStartDate: reExecuteState.value.startDate?.format("YYYY-MM-DD"),
      planStartTime: `${reExecuteState.value.planStartTime}:00`,
      planPeriod: Number(reExecuteState.value.period),
      demandDesc: reExecuteState.value.demandDesc,
      description: reExecuteState.value.planDesc,
      createUser: props.userEmail,
      planCycleID: props.planCycleId,
      curDemandVer: "",
      planStatus: "",
      schedDatetime: dayjs().toISOString(),
      executionType: "SingleRun",
      frozenDesc: "",
      demandVer: !reExecuteState.value.demandVer ? autoDemandVer.value : reExecuteState.value.demandVer,
      planType: "Manual",
      useReservationExecution: false,
      reservationTime: "15:00",
      reservationDate: dayjs().toISOString(),
      testPlanYN: "N",
      tenantNM: props.tenantNM,
      projectNM: props.projectNM,
      tenantID: props.tenantID,
      ...flowOptions.value,
    },
    mdmDemands: Array.isArray(props.demandSource) ? [...toRaw(props.demandSource)] : [],
  };

  console.log("[ReExecutePlanPop] Execute params:", param);

  isExecuting.value = true;
  try {
    await postReExecutePlan(param);
    emit("executed", param);

    // Refresh demand source
    if (props.planVer) {
      await fetchDemandSource({ plan_ver: props.planVer, schema_name: "Demand" });
      emit("data-refreshed");
    }

    isClickConfirm.value = true;
    currentStep.value = 1;
    closePopup();
  } catch (error) {
    console.error("[ReExecutePlanPop] Execute error:", error);
  } finally {
    isExecuting.value = false;
  }

  return true;
};

// ===== Watchers =====

// showEditedData filter watcher — 켜진 동안 수정 건이 바뀌면 필터도 다시 건다.
watch([showEditedData, () => props.alwaysEditedData], applyEditedFilter);

// Popup open watcher
watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      currentStep.value = 1;
      reExecuteState.value.planCycleID = props.planCycleId || "";

      if (!props.planStartDate) {
        reExecuteState.value.planStartTime = props.factoryStartTime || "06:00";
      } else {
        reExecuteState.value.planStartTime = dayjs(props.planStartDate).format("HH:mm");
      }
    }
  }
);

// Demand ver duplication check
watch(
  () => reExecuteState.value.demandVer,
  async (newVal) => {
    if (!newVal || !newVal.length) {
      isDuplicated.value = false;
      return;
    }
    try {
      const res = await fetchDemandVerValidCheck({ demand_ver: newVal });
      isDuplicated.value = !!(res.data && (res.data as any[]).length > 0);
    } catch {
      isDuplicated.value = false;
    }
  }
);
</script>

<style lang="scss" scoped>
.re-execute-plan-pop {
  .popup-container {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;

    .step-indicator-wrapper {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: 80px;
      background-color: #eef2fa;

      .step-item-line {
        width: 30px;
        border-top: 2px dotted #8998b5;
      }

      .step-item-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 40px;
        border-radius: 99px;
        cursor: pointer;
        color: #6a7184;
        font-size: 14px;
        font-weight: 400;
        background: white;
        gap: 8px;
        padding: 0px 20px 0px 5px;

        .icon {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 30px;
          height: 30px;
          background-color: #eef2fa;
          border-radius: 99px;
        }

        .title {
          display: flex;
          align-items: center;
          justify-content: center;
        }

        &.current-step {
          background: #5f7de5;
          color: white;

          .icon {
            background-color: white;
          }
        }
      }
    }

    .option-wrapper {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      padding: 16px 16px;

      .splitter {
        width: 1px;
        height: 14px;
        background-color: #bac6d4;
      }

      .option-wrapper-content {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        width: 100%;
        height: 100%;
        gap: 15px;
      }

      .option-breadcrumbs {
        display: flex;
        width: 100%;
        gap: 4px;
        color: #6a7184;
        font-size: 16px;
        font-weight: 500;

        .accent-color {
          color: #4568e0;
        }
      }
    }

    .content-wrapper {
      width: 100%;
      height: 100%;
      padding: 0px 16px 16px 16px;
      overflow: auto;
      display: flex;
      align-items: center;
      justify-content: center;

      .re-execute-popup-grid-wrapper {
        width: 100%;
        height: 100%;
      }

      .re-execute-option-setting {
        width: 1020px;
        height: 100%;

        .setting-option-container {
          display: flex;
          flex-direction: column;
          width: 100%;
          min-height: 100%;
          gap: 24px;
          padding: 0px 0px 24px 0px;
          margin-top: 8px;

          .setting-option-item {
            display: flex;
            flex-direction: column;
            width: 100%;
            flex: 0 0 auto;
            background-color: white;
            padding: 40px 40px 40px 40px;
            border-radius: 10px;
            border: 1px solid #bac6d4;
            background: #fff;

            .option-title {
              font-size: 16px;
              font-weight: 500;
              margin-bottom: 24px;
              color: #28364e;

              &.desc-title {
                margin-bottom: 16px;
              }
            }

            .setting-desc {
              font-size: 12px;
              color: #434c60;
            }

            .sub-content-wrapper {
              width: 100%;
              flex: 1;
              display: flex;
              flex-direction: column;
              gap: 20px;

              .sub-content-item {
                display: flex;
                flex-direction: column;
                gap: 10px;

                .sub-content-title-desc {
                  width: 100%;
                  display: flex;
                  flex-direction: column;
                  gap: 14px;

                  &.toggle-wrapper {
                    gap: 6px;
                  }

                  .sub-title {
                    font-size: 14px;
                    font-weight: 500;
                    color: #565f6e;

                    &.style-flex {
                      display: flex;
                      align-items: center;
                      gap: 10px;
                      width: 100%;

                      &.style-flex-end {
                        flex-direction: column;
                        gap: 6px;
                        align-items: flex-start;

                        .sub-title-detail-toggle-wrapper {
                          width: 100%;
                          display: flex;
                          align-items: center;
                          justify-content: space-between;

                          .sub-title-detail {
                            font-size: 12px;
                            font-weight: 400;
                            color: #6a7184;
                          }
                        }
                      }
                    }
                  }

                  .style-grid {
                    width: 100%;
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 10px;
                  }

                  .sub-desc {
                    font-size: 12px;
                    font-weight: 400;
                    color: #6a7184;
                    position: relative;

                    .sub-desc-toggle {
                      position: absolute;
                      top: -8px;
                      right: 0;
                    }

                    .sub-desc-detail {
                      display: flex;
                      align-items: center;
                      gap: 5px;

                      .sub-desc-detail-label {
                        font-size: 12px;
                        font-weight: 400;
                        color: #6a7184;
                      }
                      .sub-desc-detail-value {
                        font-size: 12px;
                        font-weight: 500;
                        color: #6a7184;
                      }
                    }
                  }
                }

                .sub-content {
                  width: 100%;
                  border: 1px solid #bac6d4;
                  display: flex;
                  align-items: center;
                  justify-content: space-between;
                  padding: 16px 16px;
                  border-radius: 6px;
                  background-color: #f8f8fd;

                  &.valid-wrapper {
                    padding: 20px 16px;
                  }

                  &.textarea-wrapper {
                    padding: 12px 16px 16px;
                  }

                  .sub-content-desc {
                    font-size: 12px;
                    font-weight: 400;
                    color: #434c60;
                    width: 100%;

                    .margin-bottom-10 {
                      margin-bottom: 4px;
                    }
                  }

                  .sub-content-input-wrapper {
                    width: 100%;
                    display: flex;
                    gap: 8px;
                    align-items: center;
                    color: #434c60;
                    font-size: 12px;
                    justify-content: flex-end;
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}

.sub-edited-demand-grid-wrapper {
  width: 100%;
  height: 200px;

  // 메인 그리드에서 수정된 셀
  :deep(.ps-cell.edited-cell) {
    background-color: var(--ps-dirty-modified-cell-bg);
  }
}

.execute-button-wrapper {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
  margin-top: -4px;
}

.icon-arrow {
  margin-right: 6px;
}

.demand-ver-text {
  height: 24px;
  padding: 5px 10px;
  border-radius: 99px;
  border: 1px solid #cad4e5;
  background: #f5f7fc;
  color: #434c60;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-right: -5px;

  .demand-ver-text-content {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.sub-content-flex {
  display: flex;
  gap: 6px;
  align-items: center;

  .moz-switch-wrapper {
    margin-top: 20px;
  }
}

// 원본 ExecutionFlowMasterDetailSummary SCSS 그대로.
//   그리드들은 세로로 stack (flex-direction: column), outer-wrapper 에 overflow: auto
//   로 담고, 각 item 은 height: fit-content 로 내용만큼 세로 차지.
.execution-flow-summary-placeholder {
  width: 100%;
  min-height: 400px;
  display: flex;
  flex-direction: column;

  .plan-execute-inner-wrapper {
    height: 100%;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 12px 0 0 0;

    .plan-execute-desc-text {
      color: #6a7184;
      font-size: 13px;
      font-weight: 500;
      word-break: keep-all;

      &.flow-master-summary-desc-empty {
        color: #8998b5;
        font-style: italic;
      }
    }

    .plan-execute-desc-grid-outer-wrapper {
      height: 100%;
      overflow: auto;
      flex: 1;
      display: grid;

      .plan-execute-desc-grid-wrapper {
        min-height: 100%;
        display: flex;
        flex-direction: column;
        gap: 11px;
        overflow: hidden;

        .plan-execute-desc-grid-item-wrapper {
          display: flex;
          flex-direction: column;
          overflow: hidden;
          height: fit-content;
          min-height: 120px;

          // 한 행짜리 그리드 (실행 플로우 단계 / 참조 데이터 / 데이터 저장 / 아웃바운드 step).
          //   header(~28px) + row(~32px) + border 여유 ≒ 72px.
          &.single-row-grid {
            min-height: 0;
            height: 72px;
          }

          // 원본 ExecutionFlowMasterDetailSummary 와 동일.
          :deep(.ps-cell.union-null) {
            background-color: #f0f2f5;
          }
          :deep(.ps-cell.error-mark),
          :deep(.ps-cell.error-cell) {
            background-color: #fdecec;
          }
        }
      }
    }
  }
}
</style>

<style lang="scss">
.moz-popup-container.re-execute-plan-pop {
  .moz-popup {
    .moz-popup-body {
      padding: 0px !important;
    }
  }
}

.moz-button.moz-default-button.execute-button {
  padding: 0px 14px;
}
</style>
