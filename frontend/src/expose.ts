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

/**
 * Host 환경에서 자동으로 projectId resolver를 설정하는 래퍼
 * Module Federation으로 로드될 때 각 뷰가 hostData에 접근할 수 있도록 함
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
  ProductGrid: withHostInit(() => import("./views/templates/grid/ProductGrid.vue")),
  DemandDistribution: withHostInit(() => import("./views/templates/dm/DemandDistribution.vue")),
  RtfReport: withHostInit(() => import("./views/templates/sp/RtfReport.vue")),
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
