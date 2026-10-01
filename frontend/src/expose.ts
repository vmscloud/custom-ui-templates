/**
 * Module Federation으로 노출할 컴포넌트 정의
 * Host(APS)에서 이 파일을 통해 컴포넌트를 동적으로 import
 *
 * 주의: static export를 사용하면 모든 컴포넌트가 한꺼번에 로드되므로
 * 동적 import를 사용하는 viewRegistry만 제공합니다.
 */

// Module Federation으로 로드될 때 필요한 스타일
import "@vmscloud/moz-ui-components-core/styles/default";
import "@vmscloud/moz-ui-grid-wrapper/style.css";
import "@vmscloud/moz-ui-grid-vue/style.css";
import "@vmscloud/moz-ui-chart-vue/style.css";
import "@/styles/moz-overrides.css";

import { defineComponent, h, inject, type Component } from "vue";
import { setProjectIdResolver } from "@/api/client";
import { HOST_DATA_KEY } from "@/composables/useHostStores";

/**
 * Host 환경에서 projectId resolver 설정
 *
 * 번역은 따로 로드하지 않는다. Host 안에 마운트된 화면의 useTranslation()·$t 는
 * Host 앱에 등록된 i18next(용어관리 DB 번역)를 쓰기 때문이다.
 * 리모트 코드에서 `import i18next from "i18next"` 로 직접 번역하면
 * Host 와 분리된 리모트 사본을 쓰게 되어 번역이 늦게 반영되므로 금지한다.
 *
 * 주의: `async setup()` 은 host 가 <Suspense> 경계를 제공하지 않는 한
 * 마운트 자체가 막혀 화면이 비어버린다. 따라서 setup 은 **동기**로 유지한다.
 */
function withHostInit(loader: () => Promise<{ default: Component }>) {
  return () =>
    loader().then((mod) => ({
      ...mod,
      default: defineComponent({
        setup(_, { attrs, slots }) {
          const hostData = inject<any>(HOST_DATA_KEY, null);

          if (hostData) {
            setProjectIdResolver(
              () => hostData.value?.projectInfo?.currentProjectID ?? "",
            );
          }

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
  ProductionByProcess: withHostInit(() => import("./views/templates/chart/ProductionByProcess.vue")),
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
  /**
   * 이 뷰가 Host(APS)의 planCycle 정보(planVer/planCycleID/fromDate/toDate)를
   * 필요로 하는지 선언한다. Host(RemoteLoader)가 이 플래그를 읽어 hostData.planCycle
   * 주입 범위를 결정할 수 있다 — true 인 뷰에만 planCycleID 등 전체를 제공.
   * (false 인 데모/마스터성 화면은 planCycle 불필요.)
   */
  usePlanCycle: boolean;
}

/** 뷰 메타데이터 레지스트리 */
export const viewMeta: Record<ViewName, ViewMeta> = {
  ShowCase: { name: "ShowCase", defaultMenuName: "컴포넌트 쇼케이스", usePlanCycle: false },
  ItemMaster: { name: "ItemMaster", defaultMenuName: "ItemMaster", usePlanCycle: false },
  HostInfo: { name: "HostInfo", defaultMenuName: "호스트 정보", usePlanCycle: true },
  SalesChart: { name: "SalesChart", defaultMenuName: "매출 차트", usePlanCycle: false },
  ProductionByProcess: { name: "ProductionByProcess", defaultMenuName: "공정별 생산량", usePlanCycle: true },
  ProductGrid: { name: "ProductGrid", defaultMenuName: "제품 그리드", usePlanCycle: false },
  DemandDistribution: { name: "DemandDistribution", defaultMenuName: "수요 배분", usePlanCycle: false },
  RtfReport: { name: "RtfReport", defaultMenuName: "RTF 리포트", usePlanCycle: true },
  PlanDashboard: { name: "PlanDashboard", defaultMenuName: "계획 대시보드", usePlanCycle: true },
  OnTimeRescheduledPlanResult: { name: "OnTimeRescheduledPlanResult", defaultMenuName: "재수립계획 RTF 현황", usePlanCycle: true },
  LoadFactorByOperGroup: { name: "LoadFactorByOperGroup", defaultMenuName: "공정그룹별 부하율", usePlanCycle: true },
  ReExecutePlan: { name: "ReExecutePlan", defaultMenuName: "계획 재실행", usePlanCycle: true },
  NewRtfReport: { name: "NewRtfReport", defaultMenuName: "RTF 리포트 (이수페타시스)", usePlanCycle: true },
};

/** 전체 뷰 메타데이터 목록 반환 */
export function getViewMeta(): ViewMeta[] {
  return Object.values(viewMeta);
}
