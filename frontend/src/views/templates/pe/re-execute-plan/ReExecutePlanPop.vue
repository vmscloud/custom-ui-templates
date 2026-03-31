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
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="4" width="14" height="12" rx="2" :stroke="currentStep === 1 ? '#4568e0' : '#6a7184'" stroke-width="1.5" fill="none"/>
              <line x1="7" y1="8" x2="13" y2="8" :stroke="currentStep === 1 ? '#4568e0' : '#6a7184'" stroke-width="1.5"/>
              <line x1="7" y1="12" x2="11" y2="12" :stroke="currentStep === 1 ? '#4568e0' : '#6a7184'" stroke-width="1.5"/>
            </svg>
          </div>
          <div class="title">{{ t('text-demand_info_edit_check') }}</div>
        </div>
        <div class="step-item-line"></div>
        <div :class="{ 'step-item-wrapper': true, 'current-step': currentStep === 2 }" @click="currentStep = 2">
          <div class="icon">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="10" cy="10" r="7" :stroke="currentStep === 2 ? '#4568e0' : '#6a7184'" stroke-width="1.5" fill="none"/>
              <polyline points="7,10 9.5,12.5 13.5,7.5" :stroke="currentStep === 2 ? '#4568e0' : '#6a7184'" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
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
                  <!-- Simplified ExecutionFlowMasterDetailSummary replacement -->
                  <div
                    v-show="reExecuteState.viewScenarioDetail"
                    class="execution-flow-summary-placeholder"
                  >
                    <div class="flow-summary-card">
                      <div class="flow-summary-title">{{ t('text-execution_flow_detail') }}</div>
                      <div class="flow-summary-row" v-if="!isAdvancedOption">
                        <span class="flow-label">{{ t('text-execution_flow') }}:</span>
                        <span class="flow-value">{{ selectedExecutionFlowName || t('text-not_selected') }}</span>
                      </div>
                      <template v-else>
                        <div class="flow-summary-row">
                          <span class="flow-label">{{ t('text-inbound_scenario') }}:</span>
                          <span class="flow-value">{{ selectedInboundName || t('text-use_aps_data') }}</span>
                        </div>
                        <div class="flow-summary-row">
                          <span class="flow-label">{{ t('text-engine_scenario') }}:</span>
                          <span class="flow-value">{{ selectedScenarioName || t('text-no_execution') }}</span>
                        </div>
                        <div class="flow-summary-row">
                          <span class="flow-label">{{ t('text-outbound') }}:</span>
                          <span class="flow-value">{{ reExecuteState.outboundScenarioID ? t('text-enabled') : t('text-disabled') }}</span>
                        </div>
                      </template>
                    </div>
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
                :disabled="isDuplicated"
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
import { WjFlexGridColumn } from "@vmscloud/moz-wijmo-grid/wijmo.vue2.grid";
import { type FlexGrid } from "@vmscloud/moz-wijmo-grid/wijmo.grid";
import {
  Button,
  DateInput,
  Input,
  NumberInput,
  Popup,
  Select,
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

const reExecuteState = ref<ReExecuteStateType>({
  planCycleID: props.planCycleId || "",
  startDate: dayjs(),
  planStartTime: props.factoryStartTime || "06:00",
  period: 7,
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

.execution-flow-summary-placeholder {
  .flow-summary-card {
    border: 1px solid #bac6d4;
    border-radius: 6px;
    background-color: #f8f8fd;
    padding: 18px 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    min-height: 100px;

    .flow-summary-title {
      font-size: 14px;
      font-weight: 500;
      color: #28364e;
      margin-bottom: 4px;
    }

    .flow-summary-row {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;

      .flow-label {
        color: #6a7184;
        font-weight: 400;
      }

      .flow-value {
        color: #28364e;
        font-weight: 500;
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
