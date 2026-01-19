<template>
  <ContextMenu ref="settingsRef" :itemSource="[{template:'contents[padding]', hover:false}]" :fixPosition="{
    useTeleport: true,
    top: '100%',
    left: '95px'
  }">
    <template #contents[padding]>
      <div class="dev-tool-setting">
        <div class="dev-tool-setting-box">
          <Input v-model="settingsValueClone.projectInfo.currentProjectID" :label="'프로젝트 ID'" :required="true" />
          <Input v-model="settingsValueClone.projectInfo.currentProject.projectNM" :label="'프로젝트 이름'" />
        </div>
        <div class="dev-tool-setting-box">
          <Input v-model="settingsValueClone.projectInfo.userInfo.id" :label="'유저 ID'" :required="true" />
          <Input v-model="settingsValueClone.projectInfo.userInfo.email" :label="'유저 이메일'" :required="true" />
          <Input v-model="settingsValueClone.projectInfo.userInfo.name" :label="'유저 이름'" />
        </div>
        <div class="dev-tool-setting-box">
          <Toggle :label="'관리자 여부'" v-model="settingsValueClone.projectInfo.isAdmin"></Toggle>
        </div>
        <div class="dev-tool-setting-footer">
          <Button @click="onClickReset">초기화</Button>
          <Button @click="onClickSave" :disabled="!isDiff">저장</Button>
        </div>

      </div>

    </template>
  </ContextMenu>
</template>

<script setup lang="ts">
import {computed, inject, ref, watch} from "vue";
import {HOST_DATA_KEY} from "@/composables/useHostStores.ts";
import {Button, ContextMenu, Input, Toggle} from "@vmscloud/moz-ui-components";
import { DeveloperToolType } from "./DeveloperTool.ts";

const settingsRef = defineModel<any>({required: true})

const developerTool = inject('developerTool') as DeveloperToolType;
const { settingsValue } = developerTool;
const settingsValueClone = ref(JSON.parse(JSON.stringify(settingsValue.value)));
const isDiff = computed(() => {
  return JSON.stringify(settingsValue.value) !== JSON.stringify(settingsValueClone.value);
})

const onClickReset = () => {
  window.localStorage.removeItem(HOST_DATA_KEY + '_dev');
  window.location.reload();
}

const onClickSave = () => {
  settingsValue.value = JSON.parse(JSON.stringify(settingsValueClone.value));
}

watch(() => ([settingsValue.value, settingsRef.value?.state]), () => {
  settingsValueClone.value = JSON.parse(JSON.stringify(settingsValue.value));
}, {deep: true})
</script>

<style lang="scss" scoped>
.dev-tool-setting {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px;
  width: 330px;

  .dev-tool-setting-box {
    border: 1px solid #bac6d4;
    background-color: #f8f8fd;
    border-radius: 5px;
    padding: 12px;

    display: flex;
    flex-direction: column;
  }
  .dev-tool-setting-footer {
    display: flex;
    width: 100%;
    justify-content: flex-end;
    gap: 8px;
  }
}
</style>