/**
 * Module Federation으로 노출할 컴포넌트 정의
 * Host(APS)에서 이 파일을 통해 컴포넌트를 동적으로 import
 *
 * 주의: static export를 사용하면 모든 컴포넌트가 한꺼번에 로드되므로
 * 동적 import를 사용하는 viewRegistry만 제공합니다.
 */

// Module Federation으로 로드될 때 필요한 스타일
import "@vmscloud/moz-ui-components/style.css";
import "@vmscloud/moz-wijmo-grid/style.css";
import "@vmscloud/moz-ui-chart/style.css";

import { defineComponent, h, inject, type Component } from "vue";
import { setProjectIdResolver } from "@/api/client";
import { HOST_DATA_KEY } from "@/composables/useHostStores";
import { loadLanguageFromHost } from "@/plugins/i18n";

/**
 * 원본 APS `packages/aps/src/utils/i18n.ts` 의 loadLanguage 와 동일하게
 * `SamLanguage/<lang>` API 를 호출해 i18next 에 번역 번들을 주입한다.
 *
 * - Module Federation 으로 로드된 리모트에서 bootstrap.ts 가 실행되지 않아
 *   리모트 i18next 에 번역이 비어있던 문제를 원본과 동일한 방식으로 해결.
 * - 리모트 i18next 인스턴스가 host 와 독립이든 공유든, SamLanguage 응답을
 *   자기 인스턴스에 addResourceBundle 하므로 host 번역을 덮어쓰지 않는다.
 * - 세션이 없는 dev 단독 실행에서는 호출이 401 로 실패하고 fallback 없이
 *   정적 JSON(plugins/i18n.ts 의 초기 init) 을 유지.
 */
let _i18nHostInitPromise: Promise<void> | null = null;

function ensureRemoteI18n(hostData: any): Promise<void> {
  if (_i18nHostInitPromise) return _i18nHostInitPromise;
  _i18nHostInitPromise = (async () => {
    const lang =
      hostData?.value?.projectInfo?.userInfo?.language ||
      hostData?.value?.projectInfo?.language ||
      (typeof navigator !== "undefined"
        ? navigator.language?.split("-")[0]
        : "") ||
      "ko";
    const projectId = hostData?.value?.projectInfo?.currentProjectID ?? "";
    await loadLanguageFromHost(projectId, lang);
  })();
  return _i18nHostInitPromise;
}

/**
 * Host 환경에서 projectId resolver 설정 + SamLanguage 번역 로드
 */
function withHostInit(loader: () => Promise<{ default: Component }>) {
  return () =>
    loader().then((mod) => ({
      ...mod,
      default: defineComponent({
        async setup(_, { attrs, slots }) {
          const hostData = inject<any>(HOST_DATA_KEY, null);

          if (hostData) {
            setProjectIdResolver(
              () => hostData.value?.projectInfo?.currentProjectID ?? "",
            );
          }

          await ensureRemoteI18n(hostData);

          return () => h(mod.default, attrs, slots);
        },
      }),
    }));
}

// 뷰 목록 (Host에서 동적 라우팅에 사용)
// 동적 import를 사용하여 필요한 컴포넌트만 로드
// withHostInit으로 래핑하여 Host 환경에서 projectId resolver 자동 설정
export const viewRegistry = {
  ShowCase: withHostInit(() => import("./views/templates/basic/ComponentsShowcase.vue")),
  ItemMaster: withHostInit(() => import("./views/templates/basic/ItemMaster.vue")),
  HostInfo: withHostInit(() => import("./views/templates/basic/HostInfo.vue")),
  SalesChart: withHostInit(() => import("./views/templates/chart/SalesChart.vue")),
  ProductGrid: withHostInit(() => import("./views/templates/grid/ProductGrid.vue")),
  DemandDistribution: withHostInit(() => import("./views/templates/dm/DemandDistribution.vue")),
  RtfReport: withHostInit(() => import("./views/templates/sp/rtf-report/RtfReport.vue")),
  PlanDashboard: withHostInit(() => import("./views/templates/sp/plan-dashboard/PlanDashboard.vue")),
  OnTimeRescheduledPlanResult: withHostInit(() => import("./views/templates/sp/ontime-rescheduled-plan-result/OnTimeRescheduledPlanResult.vue")),
  LoadFactorByOperGroup: withHostInit(() => import("./views/templates/sp/load-factor-by-oper-group/LoadFactorByOperGroup.vue")),
  ReExecutePlan: withHostInit(() => import("./views/templates/pe/re-execute-plan/ReExecutePlan.vue")),
  NewRtfReport: withHostInit(() => import("./views/templates/sp/new-rtf-report/NewRtfReport.vue")),
};

export type ViewName = keyof typeof viewRegistry;

/**
 * 뷰 이름으로 컴포넌트 가져오기
 */
export function getView(name: ViewName) {
  return viewRegistry[name];
}

/**
 * 사용 가능한 뷰 목록
 */
export function getAvailableViews(): ViewName[] {
  return Object.keys(viewRegistry) as ViewName[];
}

/** 뷰 메타데이터 (메뉴 등록 시 사용) */
export interface ViewMeta {
  /** 뷰 이름 (viewRegistry 키와 동일) */
  name: string;
  /** Admin에서 보여줄 기본 메뉴명 */
  defaultMenuName: string;
}

/** 뷰 메타데이터 레지스트리 */
export const viewMeta: Record<ViewName, ViewMeta> = {
  ShowCase: { name: "ShowCase", defaultMenuName: "컴포넌트 쇼케이스" },
  ItemMaster: { name: "ItemMaster", defaultMenuName: "ItemMaster" },
  HostInfo: { name: "HostInfo", defaultMenuName: "호스트 정보" },
  SalesChart: { name: "SalesChart", defaultMenuName: "매출 차트" },
  ProductGrid: { name: "ProductGrid", defaultMenuName: "제품 그리드" },
  DemandDistribution: { name: "DemandDistribution", defaultMenuName: "수요 배분" },
  RtfReport: { name: "RtfReport", defaultMenuName: "RTF 리포트" },
  PlanDashboard: { name: "PlanDashboard", defaultMenuName: "계획 대시보드" },
  OnTimeRescheduledPlanResult: { name: "OnTimeRescheduledPlanResult", defaultMenuName: "재수립계획 RTF 현황" },
  LoadFactorByOperGroup: { name: "LoadFactorByOperGroup", defaultMenuName: "공정그룹별 부하율" },
  ReExecutePlan: { name: "ReExecutePlan", defaultMenuName: "계획 재실행" },
  NewRtfReport: { name: "NewRtfReport", defaultMenuName: "RTF 리포트 (이수페타시스)" },
};

/** 전체 뷰 메타데이터 목록 반환 */
export function getViewMeta(): ViewMeta[] {
  return Object.values(viewMeta);
}
