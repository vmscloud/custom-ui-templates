/**
 * Utility 어댑터 레이어
 *
 * 원본 APS의 @/utils/hook, @/utils/i18n, QueryParamsUrl 등을 대체합니다.
 */
import { computed, ref, type Ref, type UnwrapRef, watch } from "vue";
import { apiCall } from "./stores";

// ── useLoaderParams ──

/**
 * useLoaderParams — 원본 APS의 useLoaderParams 복사
 */
export const useLoaderParams = <T extends Record<string, any>>(paramsCB: () => [string, T]) => {
  const loadParams = ref<T>(paramsCB()[1]);

  const queryKey = computed(paramsCB);

  /**
   * onLoad 호출하고 캐시 접근 전에 호출 필요
   */
  const saveParams = () => {
    /** @todo UnwrapRef<T> 단언하지 않는 방법 찾기 */
    loadParams.value = paramsCB()[1] as UnwrapRef<T>;
  };

  return { loadParams, queryKey, saveParams };
};

// ── useProp ──

/**
 * useProp — 사용자 정의 속성 컬럼을 로드합니다.
 * 원본 APS에서는 서버에서 동적 prop 컬럼 정보를 가져옵니다.
 */
export function useProp(planVer: Ref<string>, _menuId: string) {
  const propColumns = ref<{ binding: string; header: string }[]>([]);
  const propColumnsModule = {
    parseFlex(elem: any) {
      // prop_json이 있는 경우 동적 컬럼 데이터를 elem에 매핑
      if (elem?.prop_json) {
        try {
          const props =
            typeof elem.prop_json === "string"
              ? JSON.parse(elem.prop_json)
              : elem.prop_json;
          Object.keys(props).forEach((key) => {
            elem[key] = props[key];
          });
        } catch {
          // ignore
        }
      }
    },
    parseExcel(columnMap: any) {
      return columnMap;
    },
  };

  async function onLoadHeader() {
    if (!planVer.value) return;
    try {
      const res: any = await apiCall({
        url: "RarPlanByRes/GetProps",
        param: { planVer: planVer.value },
        method: "POST",
      });
      if (res?.data && typeof res.data === "object" && !Array.isArray(res.data)) {
        // 단일 item의 prop 키들을 컬럼으로 변환
        const knownKeys = new Set([
          "item_id", "item_type", "item_name", "item_group", "description",
          "item_priority", "procurement_type", "prod_type", "item_size",
          "item_spec", "descending",
        ]);
        propColumns.value = Object.keys(res.data)
          .filter((k) => !knownKeys.has(k))
          .map((k) => ({ binding: k, header: k }));
      }
    } catch {
      propColumns.value = [];
    }
  }

  return { onLoadHeader, propColumns, propColumnsModule };
}

// ── useSearchParam ──

/**
 * useSearchParam — URL 쿼리 파라미터 동기화 (no-op in MF context)
 */
export function useSearchParam(_options: {
  model: Ref<any>;
  id: string;
  defaultValue: () => any;
  type: string;
}) {
  // MF 환경에서는 URL 파라미터 동기화를 하지 않음
}

// ── convertToInternationalization ──

/**
 * convertToInternationalization — enum 값을 i18n 키로 변환
 */
export function convertToInternationalization(
  value: string,
  prefix: string,
  specialKeys: string[]
) {
  if (!value) return "";
  // specialKeys에 포함된 경우 변환
  if (specialKeys.includes(value)) {
    return value
      .replace(/([A-Z])/g, " $1")
      .trim()
      .replace(/^./, (s) => s.toUpperCase());
  }
  return value;
}

// ── openLinkNewTab ──

/**
 * openLinkNewTab — MF 환경에서 새 탭으로 링크 열기
 * 원본 APS의 @/utils/common.openLinkNewTab 대체
 */
export function openLinkNewTab(routeInfo: {
  path: string;
  query?: Record<string, string>;
}) {
  const queryStr = routeInfo.query
    ? "?" + new URLSearchParams(routeInfo.query).toString()
    : "";
  window.open(routeInfo.path + queryStr, "_blank");
}
