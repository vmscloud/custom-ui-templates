/**
 * Host(APS)에서 주입된 스토어에 접근하는 컴포저블
 */
import { inject, ref, computed, shallowRef, onMounted } from "vue";
import type { HostStores } from "@/types/host.d";

// 문자열 키 사용 (Module Federation 환경에서 Symbol은 번들 간 공유 불가)
export const HOST_STORES_KEY = "aps:hostStores";

// 독립 실행 모드용 스토어 캐시 (지연 로드)
let standaloneStoreCache: any = null;

/**
 * 독립 실행 모드용 스토어를 지연 로드
 */
async function loadStandaloneStore() {
  if (standaloneStoreCache) return standaloneStoreCache;

  try {
    const module = await import("@/stores/mainStore");
    standaloneStoreCache = module.useProjectInfoStore();
    return standaloneStoreCache;
  } catch (error) {
    console.warn(
      "[External App] Failed to load local projectInfoStore:",
      error
    );
    return null;
  }
}

/**
 * Host 스토어 접근 컴포저블
 * Host(APS)에서 로드된 경우 주입된 스토어 반환
 * 독립 실행 시 자체 스토어 사용
 */
export function useHostStores(): HostStores {
  const injected = inject(HOST_STORES_KEY, null);

  // Host에서 주입된 경우 (APS에서 로드됨)
  if (injected) {
    return injected;
  }

  // 독립 실행: 자체 스토어 사용
  console.warn(
    "[External App] Host stores not found. Using local stores for standalone mode."
  );

  // 독립 실행 모드에서 스토어를 비동기로 로드
  const projectInfoStore = shallowRef<any>(null);

  // 컴포넌트 마운트 시 스토어 로드
  onMounted(async () => {
    projectInfoStore.value = await loadStandaloneStore();
  });

  return {
    planCycle: {
      // PlanCycle은 독립 실행 시 사용 불가 (APS 전용)
      planVer: ref(""),
      fromDate: ref(null),
      toDate: ref(null),
    },
    projectInfo: {
      currentProjectID: computed(
        () => projectInfoStore.value?.currentProjectID ?? ""
      ),
      currentProject: computed(
        () => projectInfoStore.value?.currentProject ?? null
      ),
      userInfo: computed(() => projectInfoStore.value?.userInfo ?? null),
      isAdmin: computed(() => projectInfoStore.value?.isAdmin ?? false),
    },
    menu: {
      // Menu는 독립 실행 시 사용 불가 (APS 전용)
      items: ref([]),
      currentMenuId: ref(""),
      currentMenu: ref(null),
    },
  };
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
