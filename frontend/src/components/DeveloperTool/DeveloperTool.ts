import { HOST_DATA_KEY } from '@/composables/useHostStores.ts';
import { useMutation } from '@tanstack/vue-query';
import { onMounted, Ref, ref, watch } from 'vue';

export const useDeveloperTool = () => {
  const settingsValue = ref({
    "projectInfo": {
      "currentProjectID": "",
      "currentProject": {
        "projectID": "",
        "projectNM": "",
        "initMenuPath": "",
        "manualUrl": ""
      },
      "userInfo": {
        "id": "",
        "name": "",
        "email": ""
      },
      "isAdmin": true,
    },
    "planCycle": {
      "planVer": "",
      "fromDate": "",
      "toDate": ""
    },
    "menu": {
      "items": [],
          "currentMenuId": "",
          "currentMenu": null
    }
  })

  const planCycleSource: Ref<any[]> = ref([]);

  const lastCallParam = ref<{
    take: number;
    skip: number;
    planCycleID?: string;
    exact: boolean;
    planVer: string;
    isDone: boolean;
  } | null>(null);

  // 최신 PlanCycle 정보 GET
  const getPlanCycleSource = useMutation({
    mutationFn: async () => {
      const response = await fetch(`/api/custom/backend/${settingsValue.value.projectInfo.currentProjectID}/planCycleSource`, {
        method: "POST",
      });
      return response.json();  // 여기서 파싱
    },
    onSuccess: (response) => {
      if (response.data.length) {
        planCycleSource.value = response.data
      } else {
        planCycleSource.value = []
      }
      settingsValue.value.planCycle.planVer = "";
      settingsValue.value.planCycle.fromDate = "";
      settingsValue.value.planCycle.toDate = "";
    },
    onError: () => {
    },
  });
  watch(() => settingsValue.value.projectInfo.currentProjectID, () => {
    if (settingsValue.value.projectInfo.currentProjectID) {
      getPlanCycleSource.mutateAsync();
    }
  }, {immediate: true})

  watch([settingsValue], () => {
    window.localStorage.setItem(HOST_DATA_KEY + '_dev', JSON.stringify(settingsValue.value));
  }, {deep: true})
  
  onMounted(() => {
    const loadString = window.localStorage.getItem(HOST_DATA_KEY + '_dev')
    if (loadString) {
      settingsValue.value = JSON.parse(loadString);
    }
  })

  watch(() => settingsValue.value.projectInfo.currentProjectID, (newVal) => {
    settingsValue.value.projectInfo.currentProject.projectID = newVal;
  }, {immediate: true})

  watch(() => settingsValue.value.planCycle.planVer, (newVal) => {
    const currentPlan = planCycleSource.value.find((p) => p.plan_ver === newVal);
    if (!currentPlan) return
    settingsValue.value.planCycle.fromDate = currentPlan.plan_start_date
    settingsValue.value.planCycle.toDate = currentPlan.plan_end_date
  }, {immediate: true})

  return {
    settingsValue,
    planCycleSource,
    lastCallParam,
    getPlanCycleSource,
  };
};

export type DeveloperToolType = ReturnType<typeof useDeveloperTool>;