/**
 * Host(APS)에서 주입된 스토어에 접근하는 컴포저블
 *
 * RemoteLoader.vue에서 provide('hostData', hostData)로 주입된 데이터를 inject합니다.
 * 컴포넌트 방식에서는 같은 Vue 인스턴스를 공유하므로 provide/inject가 정상 작동합니다.
 */
import { inject, computed, type ComputedRef } from "vue";
import type { HostStores } from "@/types/host.d";

// RemoteLoader.vue에서 provide하는 키
export const HOST_DATA_KEY = "hostData";

// 레거시 호환을 위한 키 (기존 코드에서 사용 시)
export const HOST_STORES_KEY = "aps:hostStores";

/**
 * Host에서 provide된 hostData 타입
 * RemoteLoader.vue의 hostData computed 구조와 일치
 */
interface HostData {
  projectInfo: {
    currentProjectID: string;
    currentProject: {
      projectID: string;
      projectNM: string;
      initMenuPath?: string;
      manualUrl?: string;
    } | null;
    userInfo: {
      id: string;
      name: string;
      email: string;
    } | null;
    isAdmin: boolean;
  };
  planCycle: {
    planVer: string;
    fromDate: any; // Dayjs
    toDate: any; // Dayjs
  };
  menu: {
    items: any[];
    currentMenuId: string;
    currentMenu: any | null;
  };
}

/**
 * Host 스토어 접근 컴포저블
 * Host(APS)에서 로드된 경우 주입된 hostData를 HostStores 형태로 변환하여 반환
 */
export function useHostStores(): HostStores {
  // RemoteLoader.vue에서 provide한 hostData inject
  const hostData = inject<ComputedRef<HostData>>(HOST_DATA_KEY);
  const computedHostData =  {
      planCycle: {
        planVer: computed(() => hostData?.value?.planCycle?.planVer ?? ""),
        fromDate: computed(() => hostData?.value?.planCycle?.fromDate ?? null),
        toDate: computed(() => hostData?.value?.planCycle?.toDate ?? null),
      },
      projectInfo: {
        currentProjectID: computed(
            () => hostData?.value?.projectInfo?.currentProjectID ?? ""
        ),
        currentProject: computed(
            () => hostData?.value?.projectInfo?.currentProject ?? null
        ),
        userInfo: computed(() => hostData?.value?.projectInfo?.userInfo ?? null),
        isAdmin: computed(() => hostData?.value?.projectInfo?.isAdmin ?? false),
      },
      menu: {
        items: computed(() => hostData?.value?.menu?.items ?? []),
        currentMenuId: computed(
            () => hostData?.value?.menu?.currentMenuId ?? ""
        ),
        currentMenu: computed(() => hostData?.value?.menu?.currentMenu ?? null),
      },
    } as HostStores;

  return computedHostData
}

/**
 * Host 데이터 직접 접근 (원본 형태)
 * provide된 hostData를 그대로 반환
 */
export function useHostData(): ComputedRef<HostData | null> {
  const hostData = inject<ComputedRef<HostData> | null>(HOST_DATA_KEY, null);
  return hostData ?? computed(() => null);
}

/**
 * PlanCycle 정보만 가져오는 헬퍼
 */
export function useHostPlanCycle() {
  const stores = useHostStores();
  return stores.planCycle;
}

/**
 * 프로젝트 정보만 가져오는 헬퍼
 */
export function useHostProjectInfo() {
  const stores = useHostStores();
  return stores.projectInfo;
}

/**
 * 사용자 정보만 가져오는 헬퍼
 */
export function useHostUser() {
  const stores = useHostStores();
  return {
    userInfo: stores.projectInfo.userInfo,
    isAdmin: stores.projectInfo.isAdmin,
  };
}

/**
 * Host 환경에서 실행 중인지 확인
 */
export function isRunningInHost(): boolean {
  return (
    typeof window !== "undefined" && window.__POWERED_BY_APS_HOST__ === true
  );
}
