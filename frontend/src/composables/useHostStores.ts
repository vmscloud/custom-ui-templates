/**
 * Host(APS)에서 주입된 데이터에 접근하는 컴포저블
 *
 * Host(APS): RemoteLoader.vue에서 provide('hostData', computed({...}))
 * Dev: DeveloperToolCore.vue에서 provide('hostData', settingsValue)
 */
import { computed, inject, type Ref } from "vue";

// ── Injection Key ──
export const HOST_DATA_KEY = "hostData";

/**
 * Host에서 provide한 원본 데이터 ref 접근
 */
export function useHostData(): Ref<any> {
  const hostData = inject<Ref<any>>(HOST_DATA_KEY);
  if (!hostData) {
    throw new Error(
      "[useHostData] hostData not provided. " +
        "Ensure RemoteLoader or DeveloperTool provides data via provide('hostData', {...})."
    );
  }
  return hostData;
}

/**
 * Host 데이터 구조 접근 (기존 호환 인터페이스)
 * planCycle, projectInfo, menu, dateFormat을 computed ref로 반환
 */
export function useHostStores() {
  const hostData = useHostData();
  return {
    planCycle: computed(() => hostData.value?.planCycle ?? {}),
    projectInfo: computed(() => hostData.value?.projectInfo ?? {}),
    menu: computed(() => hostData.value?.menu ?? {}),
    dateFormat: computed(() => hostData.value?.dateFormat ?? "YYYY-MM-DD"),
  };
}

// ── Convenience Helpers ──

export function useHostPlanCycle() {
  const hostData = useHostData();
  return {
    planVer: computed(() => hostData.value?.planCycle?.planVer ?? ""),
    fromDate: computed(() => hostData.value?.planCycle?.fromDate ?? ""),
    toDate: computed(() => hostData.value?.planCycle?.toDate ?? ""),
  };
}

export function useHostProjectInfo() {
  const hostData = useHostData();
  return computed(() => hostData.value?.projectInfo ?? {});
}

export function useHostUser() {
  const hostData = useHostData();
  return {
    userInfo: computed(() => hostData.value?.projectInfo?.userInfo),
    isAdmin: computed(() => hostData.value?.projectInfo?.isAdmin ?? false),
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

/**
 * Host 네비게이션 기능
 * Host(APS)에서 provide('hostNavigation', { openLinkNewTab }) 로 주입된 함수 사용
 */
interface HostNavigation {
  openLinkNewTab: (route: { path: string; query?: Record<string, string> }, forceOpen?: boolean) => void;
}

export function useHostNavigation(): HostNavigation {
  const navigation = inject<HostNavigation | null>("hostNavigation", null);

  const fallbackOpenLinkNewTab = (route: { path: string; query?: Record<string, string> }) => {
    // standalone 모드: 단순 window.open
    const queryStr = route.query
      ? "?" + Object.entries(route.query).map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`).join("&")
      : "";
    window.open(route.path + queryStr, "_blank");
  };

  return {
    openLinkNewTab: navigation?.openLinkNewTab ?? fallbackOpenLinkNewTab,
  };
}
