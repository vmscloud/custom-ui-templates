/**
 * Host(APS)에서 inject되는 타입 정의
 */
import type { Ref, ComputedRef } from 'vue';

// Host에서 주입되는 스토어 인터페이스
export interface HostStores {
  // PlanCycle 스토어
  planCycle: {
    planVer: Ref<string>;
    fromDate: Ref<any>; // Dayjs
    toDate: Ref<any>; // Dayjs
  };

  // ProjectInfo 스토어
  projectInfo: {
    currentProjectID: ComputedRef<string>;
    currentProject: Ref<{
      projectID: string;
      projectNM: string;
      initMenuPath?: string;
      manualUrl?: string;
    } | null>;
    userInfo: Ref<{
      id: string;
      name: string;
      email: string;
    } | null>;
    isAdmin: ComputedRef<boolean>;
  };

  // Menu 스토어
  menu: {
    items: Ref<MenuItem[]>;
    currentMenuId: Ref<string>;
    currentMenu: Ref<MenuItem | null>;
  };
}

export interface MenuItem {
  menuID: string;
  menuName: string;
  path: string;
  children?: MenuItem[];
}

// Host에서 주입되는 injection keys
export const HOST_STORES_KEY = Symbol('hostStores') as InjectionKey<HostStores>;

// 전역 타입 확장
declare global {
  interface Window {
    __POWERED_BY_APS_HOST__?: boolean;
  }
}

