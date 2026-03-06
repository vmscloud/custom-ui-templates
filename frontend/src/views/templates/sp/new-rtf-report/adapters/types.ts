/**
 * Type 어댑터 레이어
 *
 * 원본 APS의 sp.types, PlanDashboard 등 타입/함수를 대체합니다.
 */
import { ref, type Ref } from "vue";

// ── sp.types ──

export interface IPlanByProdDetailSource {
  itemID: string;
  bufferSeq: number;
  bufferID: string;
  operGroupID: string;
  operID: string;
  siteID: string;
  itemType: string;
  wipQty: number;
  pegQty: number;
  usedTotalQty: number;
  outPlanQty: number;
  planDate: string;
  planMonth: string;
}

export interface IPlanByProdMasterSource {
  demandID: string;
  demandItemID: string;
  dueDate: string;
  demandQty: number;
  planQty: number;
  shortQty: number;
  lateQty: number;
  planDate: string;
  planMonth: string;
  [key: string]: any;
}

// ── usePlanDashboardSubQuery (Widget 캐시 무효화) ──

export function usePlanDashboardSubQuery(_planVer: Ref<string>) {
  return {
    async invalidateAllCache() {
      // no-op in MF — Widget 캐시는 Host의 Dashboard에서 관리
    },
  };
}
