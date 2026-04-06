/**
 * Host(APS)에서 inject되는 타입 정의
 */

/**
 * Host에서 provide('hostData', {...})로 주입되는 데이터 구조
 */
export interface HostData {
  projectInfo: {
    currentProjectID: string;
    currentProject?: any;
    userInfo?: any;
    isAdmin?: boolean;
  };
  planCycle: {
    planVer: string;
    fromDate: any;
    toDate: any;
  };
  menu: {
    items?: any[];
    currentMenuId?: string;
    currentMenu?: any;
  };
  dateFormat?: string;
}

export interface MenuItem {
  menuID: string;
  menuName: string;
  path: string;
  children?: MenuItem[];
}

// 전역 타입 확장
declare global {
  interface Window {
    __POWERED_BY_APS_HOST__?: boolean;
  }
}
