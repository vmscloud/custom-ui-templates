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
          <ExtendFlexGrid
            key="popup-grid-stable"
            style="width: 100%; height: 100%"
            :name="menuName + 're-execute-plan-pop-grid'"
            :id="menuName + 're-execute-plan-pop-grid-id'"
            :use-preset="true"
            :autoGenerateColumns="false"
            :alternatingRowStep="0"
            :itemsSource="popupDataSource"
            :initialized="onInitialized"
            :updatedView="onPopupUpdatedView"
            :emptyState="{
              isLoading: false,
            }"
            :validateKey="'none'"
            :dataKey="gridKeys"
            :setContextMenuProps="{
              useGroupColumn: false,
              useViewSelectColumn: true,
              useBulkEditColumn: {
                max_lateness_day: {
                  min: 0,
                  step: 1,
                },
                max_earliness_day: {
                  min: 0,
                  step: 1,
                },
              },
            }"
            :onInitializeRowData="
              () => {
                return { isAdded: true };
              }
            "
            :loading="false"
            :cellEditEnded="onPopupCellEditEnded"
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
            <WjFlexGridColumn
              v-for="col in propColumns"
              :key="col.binding"
              :binding="col.binding"
              :header="col.header"
              :dataType="col.dataType"
              :width="col.width"
              :align="col.align"
            ></WjFlexGridColumn>
          </ExtendFlexGrid>
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
                    <div v-show="reExecuteState.viewDemandDetail" class="sub-edited-demand-grid-wrapper">
                      <ExtendFlexGrid
                        style="width: 100%; height: 100%"
                        :name="menuName + 'sub-edited-demand-grid'"
                        :autoGenerateColumns="false"
                        :alternatingRowStep="0"
                        :itemsSource="alwaysEditedData"
                        :initialized="subEditedDemandGridInitialized"
                        :emptyState="{
                          isLoading: false,
                        }"
                        :validateKey="'none'"
                        :dataKey="gridKeys"
                        :setContextMenuProps="{
                          useGroupColumn: false,
                          useViewSelectColumn: true,
                          useBulkEditColumn: {
                            max_lateness_day: {
                              min: 0,
                              step: 1,
                            },
                            max_earliness_day: {
                              min: 0,
                              step: 1,
                            },
                          },
                        }"
                        :onInitializeRowData="
                          () => {
                            return { isAdded: true };
                          }
                        "
                        :loading="false"
                        :is-read-only="true"
                        :use-tool-box="false"
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
                        <WjFlexGridColumn
                          :width="getWidthByKey('S3')"
                          binding="demand_type"
                          :header="t('text-demand_type')"
                        />
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
                        <WjFlexGridColumn
                          :width="getWidthByKey('S2')"
                          binding="demand_group"
                          :header="t('text-demand_group')"
                        />
                        <WjFlexGridColumn
                          :width="getWidthByKey('S2')"
                          binding="final_item_buffer_id"
                          :header="t('text-final_item_buffer_id')"
                        />
                        <WjFlexGridColumn
                          :width="getWidthByKey('S1')"
                          binding="description"
                          :header="t('text-description')"
                        />
                        <WjFlexGridColumn
                          v-for="col in propColumns"
                          :key="col.binding"
                          :binding="col.binding"
                          :header="col.header"
                          :dataType="col.dataType"
                          :width="col.width"
                          :align="col.align"
                        ></WjFlexGridColumn>
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
                      </ExtendFlexGrid>
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
                                <ExtendFlexGrid
                                  :items-source="[executionFlowDataResult]"
                                  :is-read-only="true"
                                  :use-tool-box="false"
                                  :use-extend-footer="false"
                                  :use-context-menu="false"
                                  :use-sort="false"
                                  :allow-sorting="'None'"
                                  :use-filter="false"
                                  :style="{ height: '100%' }"
                                  :name="'re-execute-plan-flow-inbound'"
                                  :id="'re-execute-plan-flow-inbound-id'"
                                >
                                  <WjFlexGridColumn
                                    width="*"
                                    binding="_step"
                                    :header="t('text-execution_flow_step')"
                                  >
                                    <WjFlexGridCellTemplate v-slot="cell" cellType="Cell">
                                      <span class="wj-cell-text">{{
                                        t('text-execution_flow_inbound')
                                      }}</span>
                                      <span style="display: none">{{ cell.row.index }}</span>
                                    </WjFlexGridCellTemplate>
                                  </WjFlexGridColumn>
                                  <WjFlexGridColumn
                                    :width="160"
                                    binding="inboundID"
                                    :header="t('text-option_value')"
                                    align="center"
                                  >
                                    <WjFlexGridCellTemplate v-slot="cell" cellType="Cell">
                                      <span
                                        class="wj-cell-text"
                                        v-if="cell.item.inboundID === 'use_aps_data'"
                                        >{{ t('text-use_aps_data') }}</span
                                      >
                                      <span
                                        class="wj-cell-text"
                                        v-else-if="cell.item.inboundID === 'use_ver_data'"
                                        >{{ t('text-use_ver_data') }}</span
                                      >
                                      <span class="wj-cell-text" v-else-if="!cell.item.inboundID">
                                        <IconClose color="#dc5a5a" size="12" />
                                      </span>
                                      <span class="wj-cell-text" v-else>{{
                                        cell.item.inboundName
                                      }}</span>
                                    </WjFlexGridCellTemplate>
                                  </WjFlexGridColumn>
                                </ExtendFlexGrid>
                              </div>

                              <!-- 2) 참조 데이터 설정 (tableFilterList / tableFilterType) -->
                              <div
                                class="plan-execute-desc-grid-item-wrapper single-row-grid"
                                v-if="executionFlowDataResult.inboundID && inboundItemOptions?.tableFilterList"
                              >
                                <ExtendFlexGrid
                                  :items-source="[inboundItemOptions]"
                                  :is-read-only="true"
                                  :use-tool-box="false"
                                  :use-extend-footer="false"
                                  :use-context-menu="false"
                                  :use-sort="false"
                                  :allow-sorting="'None'"
                                  :use-filter="false"
                                  :style="{ height: '100%' }"
                                  :name="'re-execute-plan-flow-inbound-ref'"
                                  :id="'re-execute-plan-flow-inbound-ref-id'"
                                >
                                  <WjFlexGridColumn
                                    width="*"
                                    binding="tableFilterList"
                                    :header="t('text-ref_data_setting')"
                                  />
                                  <WjFlexGridColumn
                                    :width="160"
                                    binding="tableFilterType"
                                    :header="t('text-option_value')"
                                    align="center"
                                  >
                                    <WjFlexGridCellTemplate v-slot="cell" cellType="Cell">
                                      <span class="wj-cell-text">{{
                                        cell.item.tableFilterType === 'Include'
                                          ? t('text-include_table')
                                          : t('text-exclude_table')
                                      }}</span>
                                    </WjFlexGridCellTemplate>
                                  </WjFlexGridColumn>
                                </ExtendFlexGrid>
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
                                <ExtendFlexGrid
                                  class="inbound-treegrid"
                                  :items-source="inboundItemOptions.list"
                                  child-items-path="children"
                                  :format-item="onInboundDataProcessingGridFormatItem"
                                  :is-read-only="true"
                                  :use-tool-box="false"
                                  :use-extend-footer="false"
                                  :use-context-menu="false"
                                  :use-sort="false"
                                  :allow-sorting="'None'"
                                  :use-filter="false"
                                  :style="inboundTreeHeightStyle"
                                  :name="'re-execute-plan-flow-inbound-tree'"
                                  :id="'re-execute-plan-flow-inbound-tree-id'"
                                >
                                  <WjFlexGridColumn
                                    binding="menuID"
                                    :header="t('text-menu_id')"
                                    :visible="false"
                                  />
                                  <WjFlexGridColumn
                                    width="*"
                                    binding="multilingual"
                                    :header="t('text-data_processing_list')"
                                  />
                                  <WjFlexGridColumn
                                    :width="152"
                                    binding="optionValue"
                                    :header="t('text-option_value')"
                                  >
                                    <WjFlexGridCellTemplate v-slot="cell" cellType="Cell">
                                      <span class="wj-cell-text">
                                        <IconCheck
                                          v-if="cell.item.optionValue === true"
                                          color="#4568e0"
                                          size="14"
                                        />
                                        <IconClose
                                          v-if="cell.item.optionValue === false"
                                          color="#dc5a5a"
                                          size="12"
                                        />
                                      </span>
                                    </WjFlexGridCellTemplate>
                                  </WjFlexGridColumn>
                                </ExtendFlexGrid>
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
                                <ExtendFlexGrid
                                  class="inbound-treegrid"
                                  :items-source="[inboundItemOptions]"
                                  :is-read-only="true"
                                  :use-tool-box="false"
                                  :use-extend-footer="false"
                                  :use-context-menu="false"
                                  :use-sort="false"
                                  :allow-sorting="'None'"
                                  :use-filter="false"
                                  :style="{ height: '100%' }"
                                  :name="'re-execute-plan-flow-inbound-save'"
                                  :id="'re-execute-plan-flow-inbound-save-id'"
                                >
                                  <WjFlexGridColumn
                                    width="*"
                                    binding=""
                                    :header="t('text-data_storage')"
                                  >
                                    <WjFlexGridCellTemplate v-slot="cell" cellType="Cell">
                                      <span
                                        class="wj-cell-text"
                                        v-if="typeof cell.item.saveCfgValue === 'boolean'"
                                        >{{ t('desc-data_storage') }}</span
                                      >
                                    </WjFlexGridCellTemplate>
                                  </WjFlexGridColumn>
                                  <WjFlexGridColumn
                                    :width="160"
                                    binding="saveCfgValue"
                                    :header="t('text-option_value')"
                                    align="center"
                                  >
                                    <WjFlexGridCellTemplate v-slot="cell" cellType="Cell">
                                      <span class="wj-cell-text">
                                        <IconCheck
                                          v-if="cell.item.saveCfgValue"
                                          color="#4568e0"
                                          size="14"
                                        />
                                        <IconClose
                                          v-else-if="cell.item.saveCfgValue === false"
                                          color="#dc5a5a"
                                          size="12"
                                        />
                                      </span>
                                    </WjFlexGridCellTemplate>
                                  </WjFlexGridColumn>
                                </ExtendFlexGrid>
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
                                <ExtendFlexGrid
                                  :items-source="[executionFlowDataResult]"
                                  :is-read-only="true"
                                  :use-tool-box="false"
                                  :use-extend-footer="false"
                                  :use-context-menu="false"
                                  :use-sort="false"
                                  :allow-sorting="'None'"
                                  :use-filter="false"
                                  :style="{ height: '100%' }"
                                  :name="'re-execute-plan-flow-engine'"
                                  :id="'re-execute-plan-flow-engine-id'"
                                >
                                  <WjFlexGridColumn
                                    width="*"
                                    binding="_step"
                                    :header="t('text-execution_flow_step')"
                                  >
                                    <WjFlexGridCellTemplate v-slot="cell" cellType="Cell">
                                      <span class="wj-cell-text">{{ t('text-engine') }}</span>
                                      <span style="display: none">{{ cell.row.index }}</span>
                                    </WjFlexGridCellTemplate>
                                  </WjFlexGridColumn>
                                  <WjFlexGridColumn
                                    :width="160"
                                    binding="scenarioID"
                                    :header="t('text-option_value')"
                                    align="center"
                                  >
                                    <WjFlexGridCellTemplate v-slot="cell" cellType="Cell">
                                      <span class="wj-cell-text" v-if="cell.item.scenarioID">{{
                                        cell.item.scenarioName
                                      }}</span>
                                      <span class="wj-cell-text" v-else>
                                        <IconClose color="#dc5a5a" size="12" />
                                      </span>
                                    </WjFlexGridCellTemplate>
                                  </WjFlexGridColumn>
                                </ExtendFlexGrid>
                              </div>
                              <!-- 글로벌 옵션 (scenarioConfigSource) -->
                              <div
                                class="plan-execute-desc-grid-item-wrapper"
                                style="flex: 1"
                                v-if="executionFlowDataResult.scenarioID && scenarioConfigSource.length"
                              >
                                <ExtendFlexGrid
                                  :items-source="scenarioConfigSource"
                                  :is-read-only="true"
                                  :use-tool-box="false"
                                  :use-extend-footer="false"
                                  :use-context-menu="false"
                                  :use-sort="false"
                                  :allow-sorting="'None'"
                                  :use-filter="false"
                                  :allow-pinning="false"
                                  :allow-resizing="false"
                                  :format-item="engineFormatItem"
                                  :style="engineGlobalHeightStyle"
                                  :name="'re-execute-plan-flow-engine-global'"
                                  :id="'re-execute-plan-flow-engine-global-id'"
                                >
                                  <WjFlexGridColumn
                                    binding="description"
                                    :header="t('text-option')"
                                    width="*"
                                  />
                                  <WjFlexGridColumn
                                    binding="optionValue"
                                    :header="t('text-option_value')"
                                    :width="152"
                                    align="center"
                                  >
                                    <WjFlexGridCellTemplate v-slot="cell" cellType="Cell">
                                      <span
                                        class="wj-cell-text"
                                        v-if="cell.item.uiType !== 'TOGGLE'"
                                        >{{ cell.item.optionValue }}</span
                                      >
                                      <span class="wj-cell-text" v-else>
                                        <IconCheck
                                          v-if="cell.item.optionValue === 'Y'"
                                          color="#4568e0"
                                          size="14"
                                        />
                                        <IconClose
                                          v-if="cell.item.optionValue === 'N'"
                                          color="#dc5a5a"
                                          size="12"
                                        />
                                      </span>
                                    </WjFlexGridCellTemplate>
                                  </WjFlexGridColumn>
                                </ExtendFlexGrid>
                              </div>
                              <!-- 시나리오 모듈 리스트 (phaseColumns 동적) -->
                              <div
                                class="plan-execute-desc-grid-item-wrapper"
                                style="flex: 1"
                                v-if="executionFlowDataResult.scenarioID && scenarioModuleDataSource.length"
                              >
                                <ExtendFlexGrid
                                  :items-source="scenarioModuleDataSource"
                                  :initialized="onInitializedScenarioModule"
                                  :format-item="engineFormatItem"
                                  :is-read-only="true"
                                  :use-tool-box="false"
                                  :use-extend-footer="false"
                                  :use-context-menu="false"
                                  :use-sort="false"
                                  :allow-sorting="'None'"
                                  :use-filter="false"
                                  :allow-pinning="false"
                                  :style="engineModuleHeightStyle"
                                  :name="'re-execute-plan-flow-engine-modules'"
                                  :id="'re-execute-plan-flow-engine-modules-id'"
                                >
                                  <WjFlexGridColumn
                                    binding="module_id"
                                    :header="t('text-module_id')"
                                    :width="getWidthByKey('S3')"
                                  />
                                  <WjFlexGridColumn
                                    binding="description"
                                    :header="t('text-option')"
                                    width="*"
                                  />
                                  <WjFlexGridColumn
                                    v-for="col in phaseColumns"
                                    :key="`phase-${String(col.binding)}-${scenarioModuleDataSource.length}`"
                                    :binding="String(col.binding)"
                                    :header="t(col.header)"
                                    :width="152"
                                    align="center"
                                  >
                                    <WjFlexGridCellTemplate v-slot="cell" cellType="Cell">
                                      <span
                                        class="wj-cell-text"
                                        v-if="cell.item.ui_type !== 'TOGGLE'"
                                        >{{ cell.item[String(col.binding)] }}</span
                                      >
                                      <span class="wj-cell-text" v-else>
                                        <IconCheck
                                          v-if="cell.item[String(col.binding)] === 'Y'"
                                          color="#4568e0"
                                          size="14"
                                        />
                                        <IconClose
                                          v-if="cell.item[String(col.binding)] === 'N'"
                                          color="#dc5a5a"
                                          size="12"
                                        />
                                      </span>
                                    </WjFlexGridCellTemplate>
                                  </WjFlexGridColumn>
                                </ExtendFlexGrid>
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
                                <ExtendFlexGrid
                                  :items-source="[executionFlowDataResult]"
                                  :is-read-only="true"
                                  :use-tool-box="false"
                                  :use-extend-footer="false"
                                  :use-context-menu="false"
                                  :use-sort="false"
                                  :allow-sorting="'None'"
                                  :use-filter="false"
                                  :style="{ height: '100%' }"
                                  :name="'re-execute-plan-flow-outbound'"
                                  :id="'re-execute-plan-flow-outbound-id'"
                                >
                                  <WjFlexGridColumn
                                    width="*"
                                    binding="_step"
                                    :header="t('text-execution_flow_step')"
                                  >
                                    <WjFlexGridCellTemplate v-slot="cell" cellType="Cell">
                                      <span class="wj-cell-text">{{ t('text-outbound') }}</span>
                                      <span style="display: none">{{ cell.row.index }}</span>
                                    </WjFlexGridCellTemplate>
                                  </WjFlexGridColumn>
                                  <WjFlexGridColumn
                                    :width="160"
                                    binding="outboundID"
                                    :header="t('text-option_value')"
                                    align="center"
                                  >
                                    <WjFlexGridCellTemplate v-slot="cell" cellType="Cell">
                                      <span class="wj-cell-text">
                                        <IconCheck
                                          v-if="cell.item.outboundID"
                                          color="#4568e0"
                                          size="14"
                                        />
                                        <IconClose v-else color="#dc5a5a" size="12" />
                                      </span>
                                    </WjFlexGridCellTemplate>
                                  </WjFlexGridColumn>
                                </ExtendFlexGrid>
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
import { computed, nextTick, ref, toRaw, watch } from "vue";
import { useTranslation } from "i18next-vue";
import { ExtendFlexGrid, type ExtendGrid } from "@vmscloud/moz-wijmo-grid";
import { WjFlexGridCellTemplate, WjFlexGridColumn } from "@vmscloud/moz-wijmo-grid/wijmo.vue2.grid";
import { AllowMerging, type FlexGrid } from "@vmscloud/moz-wijmo-grid/wijmo.grid";
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
} from "@vmscloud/moz-ui-components";
import dayjs from "dayjs";
import {
  postReExecutePlan,
  fetchDemandSource,
  fetchDemandVerValidCheck,
  type ExecutionFlowMasterType,
  type ScenarioMasterType,
  type InboundItemType,
} from "./reExecutePlan";

// ===== Width helper (replaces @vmscloud/moz-wijmo-grid/utils getWidthByKey) =====
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
  (e: "cell-edit-ended", sender: any, event: any): void;
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
//   Wijmo FlexGrid 기본 rowHeight ≒ 28px, header padding 포함 여유 40px.
const ROW_H = 28;
const HEADER_H = 40;
const computeAutoHeight = (rowCount: number) =>
  `${HEADER_H + Math.max(1, rowCount) * ROW_H}px`;

// Inbound tree grid: Category + 확장된 Menu 자식까지 합친 총 가시 row 수.
const inboundTreeHeightStyle = computed(() => {
  const list = props.inboundItemOptions?.list ?? [];
  let count = 0;
  for (const item of list) {
    count += 1;
    if (Array.isArray(item.children)) {
      count += item.children.length;
    }
  }
  return { height: computeAutoHeight(count) };
});

// Engine global options & module 그리드: items length 기반.
const engineGlobalHeightStyle = computed(() => ({
  height: computeAutoHeight(props.scenarioConfigSource?.length ?? 0),
}));
const engineModuleHeightStyle = computed(() => ({
  height: computeAutoHeight(props.scenarioModuleDataSource?.length ?? 0),
}));

// ===== Execution Flow Summary grid helpers (원본 ExecutionFlowMasterDetailSummary 이식) =====
// Engine global/module 그리드 공통 formatItem.
//   1) description 컬럼은 raw 문자열이 i18n key일 수 있어 t() 로 번역해 치환한다.
//   2) scenarioModule 그리드에서 max_phase 를 초과한 phase_N 컬럼은 'union-null' 클래스로 음영 처리
//      (module A는 phase_2까지인데 module B가 phase_1까지인 경우, 테이블 합집합 union 이므로 B의 phase_2 셀을 빈 셀로 마킹).
//   3) option_id === 'DefaultRuleSet' + max_phase 내 phase 인데 값 없음 → 'error-mark' 로 표시.
const engineFormatItem = (_s: any, e: any) => {
  if (!e.panel || e.panel.cellType !== 1) return;
  const item = e.getRow?.()?.dataItem;
  if (!item) return;
  const col: string | undefined = e.getColumn?.()?.binding;
  if (!col) return;
  const cellSpan = e.cell.querySelector("span") ?? e.cell;

  if (col === "description") {
    const rawDesc = item[col];
    const translated = rawDesc != null ? t(String(rawDesc)) : "";
    cellSpan.textContent = translated;
  }

  const phaseMatch = col.match(/^phase_(\d+)$/);
  if (phaseMatch && item.max_phase != null) {
    const phaseN = parseInt(phaseMatch[1], 10);
    if (phaseN > item.max_phase) {
      e.cell.classList.add("union-null");
    }
    if (
      phaseN <= item.max_phase &&
      !item[col] &&
      item.option_id === "DefaultRuleSet"
    ) {
      e.cell.classList.add("error-mark");
      e.cell.classList.add("error-cell");
    }
  }
};

// Inbound tree grid 의 data cell span 색을 진하게. (원본 onInboundDataProcessingGridFormatItem)
const onInboundDataProcessingGridFormatItem = (_s: any, e: any) => {
  if (!e.panel) return;
  if (e.panel.cellType !== 1) {
    e.cell.classList.add("wj-align-center");
    return;
  }
  if (e.cell?.children) {
    for (const node of Array.from(e.cell.children) as HTMLElement[]) {
      if (node.tagName === "SPAN") node.style.color = "#28364e";
    }
  }
};

// Module 그리드 초기화 시 첫 컬럼(module_id) merge 허용. 원본과 동일한 처리.
const onInitializedScenarioModule = (flexGrid: FlexGrid) => {
  flexGrid.allowMerging = AllowMerging.All;
  if (flexGrid.columns.length > 0) {
    flexGrid.columns[0].allowMerging = true;
  }
};

// ===== Grid State =====
const grid = ref<FlexGrid | null>(null);
const extendGrid = ref<ExtendGrid>();
const gridKeys: string[] = ["demand_id"];

const subGrid = ref<FlexGrid | null>(null);
const subExtendGrid = ref<ExtendGrid>();

// ===== Grid Initialization =====
const onInitialized = (flexGrid: FlexGrid, _extendGrid: ExtendGrid) => {
  grid.value = flexGrid;
  extendGrid.value = _extendGrid;
};

const subEditedDemandGridInitialized = (flexGrid: FlexGrid, _extendGrid: ExtendGrid) => {
  subGrid.value = flexGrid;
  subExtendGrid.value = _extendGrid;

  // Sync extend grid states from main grid
  if (extendGrid.value) {
    nextTick(() => {
      setTimeout(() => {
        try {
          syncExtendGridStates(extendGrid.value, _extendGrid);
          flexGrid.invalidate();
          flexGrid.refresh();
        } catch (error) {
          console.error("[Sub grid init] State sync error:", error);
        }
      }, 50);
    });
  }
};

// ===== ExtendFlexGrid State Sync =====
const syncExtendGridStates = (sourceExtendGrid: any, targetExtendGrid: any) => {
  try {
    // originalDataMap sync
    sourceExtendGrid.originalDataMap?.forEach((value: any, key: string) => {
      if (!targetExtendGrid.originalDataMap.has(key)) {
        targetExtendGrid.originalDataMap.set(key, new Map(value));
      } else {
        const targetMap = targetExtendGrid.originalDataMap.get(key);
        value.forEach((colValue: any, colKey: string) => {
          targetMap.set(colKey, colValue);
        });
      }
    });

    // updated Set sync
    sourceExtendGrid.updated?.forEach((value: any, key: string) => {
      targetExtendGrid.updated.set(key, value);
    });

    // added Set sync
    sourceExtendGrid.added?.forEach((value: any, key: string) => {
      targetExtendGrid.added.set(key, value);
    });

    // removed Set sync
    sourceExtendGrid.removed?.forEach((value: any, key: string) => {
      targetExtendGrid.removed.set(key, value);
    });
  } catch (error) {
    console.error("[Popup] ExtendFlexGrid state sync error:", error);
  }
};

// ===== Cell Edit Handler =====
const onPopupCellEditEnded = (_sender: any, _e: any) => {
  emit("cell-edit-ended", _sender, _e);

  nextTick(() => {
    if (grid.value) {
      grid.value.invalidate();
      grid.value.refresh();
    }
  });
};

// ===== Grid View Update Handler =====
const onPopupUpdatedView = (_sender: any) => {
  if (extendGrid.value) {
    setTimeout(() => {
      try {
        if (grid.value) {
          grid.value.invalidate();
          grid.value.refresh();
        }
      } catch (error) {
        console.error("[Grid update] State restore error:", error);
      }
    }, 10);
  }
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

// showEditedData filter watcher
watch(showEditedData, () => {
  if (grid.value) {
    setTimeout(() => {
      grid.value?.invalidate();
      grid.value?.refresh();
    }, 50);
  }
});

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
          :deep(.wj-cell.union-null) {
            background-color: #f0f2f5;
          }
          :deep(.wj-cell.error-mark),
          :deep(.wj-cell.error-cell) {
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
