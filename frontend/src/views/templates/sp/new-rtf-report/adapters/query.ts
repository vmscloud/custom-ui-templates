/**
 * Query 어댑터 레이어
 *
 * 원본 APS의 @/api/query 모듈을 custom-ui-templates 환경에 맞게 매핑합니다.
 * 각 필터 쿼리 훅은 apiCall을 통해 커스텀 백엔드를 호출합니다.
 */
import { ref, type Ref, watch } from "vue";
import { useTranslation } from "i18next-vue";
import { apiCall } from "./stores";

// ── Types ──

export type AggregateType = "WEEK" | "MONTH";
export type QtyUOMType = "DEFAULT" | "CONVERSION";
export type SummaryType =
  | "itemGroup"
  | "cust"
  | "region"
  | "demandType"
  | "due";

// ── useCustInRtfQuery ──

export function useCustInRtfQuery(planVer: Ref<string>) {
  const custParam = ref<string[]>([]);
  const custSource = ref<any[]>([]);

  watch(
    planVer,
    async (ver) => {
      if (!ver) return;
      try {
        const res: any = await apiCall({
          url: "ComCustInRtf",
          param: { planVer: ver },
          method: "POST",
        });
        if (res?.data) {
          custSource.value = res.data;
          custParam.value = res.data.map((c: any) => c.cust_id);
        }
      } catch {
        custSource.value = [];
        custParam.value = [];
      }
    },
    { immediate: true }
  );

  return { custParam, custSource };
}

// ── useItemGroupInRtfQuery ──

export function useItemGroupInRtfQuery(planVer: Ref<string>) {
  const itemGroup = ref<string[]>([]);
  const itemGroupSource = ref<any[]>([]);

  watch(
    planVer,
    async (ver) => {
      if (!ver) return;
      try {
        const res: any = await apiCall({
          url: "ComItemGroupInRtf",
          param: { planVer: ver },
          method: "POST",
        });
        if (res?.data) {
          itemGroupSource.value = res.data;
          itemGroup.value = res.data.map((g: any) => g.item_group);
        }
      } catch {
        itemGroupSource.value = [];
        itemGroup.value = [];
      }
    },
    { immediate: true }
  );

  return { itemGroup, itemGroupSource };
}

// ── useGetRegionsQuery ──

export function useGetRegionsQuery(planVer: Ref<string>) {
  const region = ref<string[]>([]);
  const regionSource = ref<any[]>([]);

  watch(
    planVer,
    async (ver) => {
      if (!ver) return;
      try {
        const res: any = await apiCall({
          url: "RarRtfReport/GetRegions",
          param: { planVer: ver },
          method: "POST",
        });
        if (res?.data) {
          regionSource.value = res.data;
          region.value = res.data.map((r: any) => r.value);
        }
      } catch {
        regionSource.value = [];
        region.value = [];
      }
    },
    { immediate: true }
  );

  return { region, regionSource };
}

// ── useGetDemandTypesQuery ──

export function useGetDemandTypesQuery(planVer: Ref<string>) {
  const demandType = ref<string[]>([]);
  const demandTypeSource = ref<any[]>([]);

  watch(
    planVer,
    async (ver) => {
      if (!ver) return;
      try {
        const res: any = await apiCall({
          url: "RarRtfReport/GetDemandTypes",
          param: { planVer: ver },
          method: "POST",
        });
        if (res?.data) {
          demandTypeSource.value = res.data;
          demandType.value = res.data.map((d: any) => d.value);
        }
      } catch {
        demandTypeSource.value = [];
        demandType.value = [];
      }
    },
    { immediate: true }
  );

  return { demandType, demandTypeSource };
}

// ── useQtyUomQuery ──

export function useQtyUomQuery(
  types: QtyUOMType[],
  defaultValue: QtyUOMType,
  _options?: { menuID?: string }
) {
  const uomType = ref<QtyUOMType>(defaultValue);
  const qtyUOMSource = ref(
    types.map((t) => ({
      value: t,
      displayValue: t === "DEFAULT" ? "Default" : "Conversion",
    }))
  );

  return { uomType, qtyUOMSource };
}

// ── useAggTypeQuery ──

export function useAggTypeQuery(
  planVer: Ref<string>,
  types: AggregateType[],
  options?: { defaultValue?: AggregateType }
) {
  const aggType = ref<AggregateType>(options?.defaultValue ?? "MONTH");
  const isAggFetching = ref(false);
  const aggTypeSource = ref(
    types.map((t) => ({
      value: t,
      label: t === "MONTH" ? "Monthly" : "Weekly",
    }))
  );

  return { aggType, aggTypeSource, isAggFetching };
}

// ── useSummaryQuery ──

export function useSummaryQuery(
  types: SummaryType[],
  defaultValue: SummaryType
) {
  const { t } = useTranslationFallback();

  const summaryType = ref<SummaryType>(defaultValue);
  const summarySource = ref(
    types.map((type) => {
      const labelMap: Record<SummaryType, string> = {
        itemGroup: t("text-upper-item_group"),
        cust: t("text-upper-customer"),
        region: t("text-upper-region"),
        demandType: t("text-upper-demand_type"),
        due: t("text-due"),
      };
      return { value: type, label: labelMap[type] || type };
    })
  );

  return { summaryType, summarySource };
}

// ── useTranslation wrapper ──
function useTranslationFallback() {
  try {
    return useTranslation();
  } catch {
    return { t: (key: string) => key };
  }
}
