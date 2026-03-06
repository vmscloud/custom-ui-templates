<template>
  <header class="dev-header">
    <div class="dev-header-left">
      <img class="dev-logo" src="../../../public/logo_mozart_cloud.svg" alt="logo">
      <div class="dev-menu">
        <p>메뉴</p>
        <div class="dev-menu-safe-zone"/>
        <div class="dev-menu-list">
          <div class="dev-menu-list-item" @click="routeToMenu(menu.path)" v-for="menu in menus">
            {{menu.name}}
          </div>
        </div>
      </div>
    </div>

    <div class="dev-header-right">
      <TreeSelect
          v-model="settingsValue.planCycle.planVer"
          :itemsSource="formattedPlanItems"
          :treeProps="{
              keyProp: 'plan_ver',
              displayProp: 'plan_ver',
              categoryLv1ID: 'plan_cycle_id',
              description: 'plan_status',
            }"
          :useMultiSelect="false"
          :placeholder="`플랜 버전 선택`"
          :tree-levels="2"
          :width="250"
      >
        <template #list-item="{ item, highlightText }">
          <div class="dev-plan-ver-item">
            <IconDecide
                v-if="item.description == 'FROZEN'"
                class="dev-plan-ver-item-badge moz-frozen-icon"
                color="var(--color-badge-800)"
            />
            <IconCircleDot
                v-else-if="item.description == 'DONE'"
                class="dev-plan-ver-item-badge moz-frozen-icon"
            />
            <IconCircleDot
                v-else-if="item.description == 'WARNING'"
                class="dev-plan-ver-item-badge moz-frozen-icon"
                color="#fa9e23"
            />
            <IconCircleX
                v-else-if="item.description == 'INBOUNDTIMEOUT' || item.description == 'ENGINETIMEOUT'"
                class="dev-plan-ver-item-badge moz-frozen-icon"
                color="var(--color-plan-status-600)"
                :size="'12'"
            />
            <IconCircleX
                :size="'12'"
                v-else
                class="chatbot-tag-plan-ver-item-badge moz-frozen-icon"
                color="var(--color-system-200)"
            />
            <div>
                  <span v-for="({ part, highlight }, index) in highlightText" :key="index" :class="{ highlight }">{{
                      part
                    }}</span>
            </div>
          </div>
        </template>
      </TreeSelect>
      <div class="dev-header-setting">

        <Button @click="settingsRef.open()">
          설정
        </Button>
        <DeveloperToolSetting v-model="settingsRef"/>
      </div>

    </div>
  </header>
  <aside class="dev-aside">
  </aside>
  <slot>
  </slot>
</template>

<script setup lang="ts">
// Host에서 로드되었는지 확인 (개발 모드 구분)
import {computed, onMounted, provide, ref} from "vue";
import {routes} from "@/router";
import {getAvailableViews} from "@/expose.ts";
import {RouteRecordRaw, useRouter} from "vue-router";
import DeveloperToolSetting from "@/components/DeveloperTool/DeveloperToolSetting.vue";
import {Button, TreeSelect} from "@vmscloud/moz-ui-components";
import {HOST_DATA_KEY} from "@/composables/useHostStores.ts";
import { setProjectIdResolver } from "@/api/client";
import { useDeveloperTool } from "./DeveloperTool.ts";
import IconDecide from "@/components/DeveloperTool/assets/IconDecide.vue";
import IconCircleDot from "@/components/DeveloperTool/assets/IconCircleDot.vue";
import IconCircleX from "@/components/DeveloperTool/assets/IconCircleX.vue";

const HEADER_SIZE = '55px'
const ASIDE_SIZE = '54px'

const developerTool = useDeveloperTool();
provide('developerTool', developerTool);

const { settingsValue, planCycleSource } = developerTool;
const router = useRouter();
const settingsRef = ref()
const formattedPlanItems = computed(() => planCycleSource.value.filter((item) => item.plan_ver));




const menus = ref<RouteRecordRaw[]>([])

const routeToMenu = (url: string) => {
  router.push(url)
}

onMounted(() => {
  const availableMenus = getAvailableViews() as string[]
  menus.value = routes.filter(route => {
    return availableMenus.includes(route.name as string)
  })
})

provide(HOST_DATA_KEY, settingsValue)
setProjectIdResolver(() => settingsValue.value?.projectInfo?.currentProjectID ?? "")
</script>

<style lang="scss">
//#dev-tool {
//  width: 100%;
//  height: 100%;
//  display: grid;
//  position: fixed;
//  top: 0;
//  left: 0;
//  grid-template-rows: v-bind('HEADER_SIZE') auto;
//  z-index: 0;
//}

.dev-header {
  position: absolute;
  background: #fff;
  border-bottom: 1px solid #bbc6d9;
  width: 100%;
  height: v-bind('HEADER_SIZE');
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 1;

  .dev-header-left {
    display: flex;
    align-items: center;
    .dev-logo {
      margin: 0 21px;
      width: 158px;
    }

    .dev-menu {
      position: relative;
      cursor: pointer;
      background-color: rgba(69, 104, 224, 0.16);
      color: #4568e0;
      height: 40px;
      padding: 0 0.875rem;
      border-radius: 0.25rem;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      justify-content: center;


      .dev-menu-safe-zone {
        position: absolute;
        width: 100%;
        height: calc(100% + 16px);
        top: 0;
        left: 0;
      }

      .dev-menu-list {
        transition-duration: 0.2s;
        transition-property: top, opacity;
        transition-timing-function: cubic-bezier(0.5, 0.25, 0, 1);
        position: absolute;
        opacity: 0;
        pointer-events: none;
        top: calc(100% + 8px);
        left: 0;
        border-radius: 0.5rem;
        border: 1px solid #bac6d4;
        background-color: #fff;
        padding: 0.375rem 0;
        min-width: 200px;
        box-shadow: 0px 10px 20px 0px rgba(81, 102, 110, .07);

        .dev-menu-list-item {
          padding: 0 1rem;
          color: #434c60;
          cursor: pointer;
          font-size: 0.813rem;
          height: 30px;
          display: flex;
          align-items: center;

          &:hover {
            background-color: #EEF1FC;
          }

        }
      }
      &:hover {
        .dev-menu-list {
          opacity: 1;
          top: calc(100% + 16px);
          pointer-events: auto;
        }
      }
    }
  }

  .dev-header-right {
    display: flex;
    align-items: center;

    .dev-header-setting {
      position: ab;
      height: 40px;
      padding: 0 0.875rem;

      display: flex;
      align-items: center;
      justify-content: center;
    }
  }

}

.dev-aside {
  position: absolute;
  width: v-bind('ASIDE_SIZE');
  height: calc(100% - v-bind('HEADER_SIZE'));
  top: v-bind('HEADER_SIZE');
  background: #191727;
}

.dev-aside + * {
  position: absolute;
  top: v-bind('HEADER_SIZE');
  left: v-bind('ASIDE_SIZE');
  overflow: hidden;
  width: calc(100% - v-bind('ASIDE_SIZE')) !important;
  height: calc(100% - v-bind('HEADER_SIZE')) !important;
  z-index: 0;
}

.dev-plan-ver-item {
  display: flex;
  align-items: center;
  gap: 6px;

  & .dev-plan-ver-item-badge {
    min-width: 12px;
    min-height: 12px;
  }
}
</style>