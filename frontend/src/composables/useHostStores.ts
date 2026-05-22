/**
 * Host(APS)에서 주입된 데이터에 접근하는 컴포저블
 *
 * Host(APS): RemoteLoader.vue에서 provide('hostData', computed({...}))
 * Dev: DeveloperToolCore.vue에서 provide('hostData', settingsValue)
 */
import { computed, inject, type ComputedRef, type Ref } from "vue";
import { useTranslation } from "i18next-vue";

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

// ── Menu / Breadcrumb ──

/** Host(APS) menu item 형태 (@moz-shared IMenu 의 부분집합). */
interface HostMenuItem {
  menuID?: string;
  menuName?: string;
  categoryID?: string;
  parentMenuName?: string;
}

/**
 * Host 가 제공한 menu(currentMenu + items)로부터 breadcrumb 경로명을 도출한다.
 * currentMenu 의 menuName 을 leaf 로 두고 categoryID 를 따라 상위 카테고리명을
 * 앞에 붙여 [상위…, 현재] 순서로 만든다(원본 getNavis 와 동일 순서). items 로
 * 상위를 찾지 못하면 parentMenuName 을 1단계 fallback 으로 사용한다.
 * 제공 메뉴가 없으면 undefined → 호출측에서 하드코딩 fallback 사용.
 */
function resolveHostNavigations(menu: any): string[] | undefined {
  const current: HostMenuItem | null | undefined = menu?.currentMenu;
  if (!current || !current.menuName) return undefined;

  const items: HostMenuItem[] = Array.isArray(menu?.items) ? menu.items : [];
  const names: string[] = [current.menuName];

  let categoryId = current.categoryID;
  let guard = 0;
  while (categoryId && guard++ < 16) {
    const parent = items.find((m) => m.menuID === categoryId);
    if (!parent || !parent.menuName) break;
    names.unshift(parent.menuName);
    categoryId = parent.categoryID;
  }
  // items 로 상위를 못 찾았지만 parentMenuName 이 있으면 1단계만 보강.
  if (names.length === 1 && current.parentMenuName) {
    names.unshift(current.parentMenuName);
  }
  return names;
}

/**
 * Controller breadcrumb 용 navigations 를 반환한다.
 * 우선순위:
 *   1) Host 가 prebuilt 한 `menu.navis` (원본 getNavis 결과, child-first 배열)
 *      → 원본 Controller 와 동일하게 reverse + t() 적용해 [상위…, 현재] 로 표시.
 *   2) `menu.currentMenu` + `menu.items` 로 직접 [상위…, 현재] 구성(각 항목 t() 적용).
 *   3) 화면 하드코딩 fallback.
 *   4) undefined(미표시).
 *
 * Host 환경(RemoteLoader)에서는 프로젝트 메뉴 관리/다국어로 변경된 실제 메뉴명을,
 * standalone/dev 등 menu 미제공 환경에서는 화면이 넘긴 하드코딩 값을 쓴다.
 *
 * 메뉴명이 i18n 키(예: "menu-SupplyPlan")일 수 있어 Host 유래 값에는 t() 를 적용한다
 * (키가 아니면 i18next 가 입력을 그대로 반환하므로 안전). 하드코딩 fallback 은 화면이
 * 이미 t() 로 만들어 넘기므로 추가 변환하지 않는다.
 *
 * @param fallback 화면별 하드코딩 navigations (다국어 t() 반응성을 위해 getter 권장)
 */
export function useHostNavigations(
  fallback: () => string[],
): ComputedRef<string[] | undefined> {
  // 비-호스트(standalone) 환경에서도 throw 하지 않도록 default null 로 inject.
  const hostData = inject<Ref<any> | null>(HOST_DATA_KEY, null);
  const { t } = useTranslation();
  return computed(() => {
    const menu = hostData?.value?.menu;

    const navis = menu?.navis;
    if (Array.isArray(navis) && navis.length) {
      return [...navis].reverse().map((title: string) => t(title));
    }

    const fromMenu = resolveHostNavigations(menu);
    if (fromMenu && fromMenu.length) return fromMenu.map((n) => t(n));

    const fb = fallback() ?? [];
    return fb.length ? fb : undefined;
  });
}

// ── Convenience Helpers ──

export function useHostPlanCycle() {
  const hostData = useHostData();
  return {
    planVer: computed(() => hostData.value?.planCycle?.planVer ?? ""),
    planCycleID: computed(() => hostData.value?.planCycle?.planCycleID ?? ""),
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
