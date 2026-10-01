/**
 * 애플리케이션 부트스트랩
 * Module Federation의 비동기 로딩을 위한 분리
 */

// CSS 레이어 순서 선언 (reset < moz). 어떤 스타일보다 먼저 import 해야 한다.
import "./styles/layer-order.css";

// ECharts 초기화 (가장 먼저 실행되어야 함)
// 단독 개발 환경에서 CanvasRenderer가 등록되지 않는 문제 해결
import { use } from "@vmscloud/moz-ui-chart-vue/echarts/core";
import { CanvasRenderer } from "@vmscloud/moz-ui-chart-vue/echarts/renderers";
import { BarChart, LineChart, PieChart, ScatterChart } from "@vmscloud/moz-ui-chart-vue/echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DatasetComponent,
  DataZoomComponent,
  TitleComponent,
} from "@vmscloud/moz-ui-chart-vue/echarts/components";

use([
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DatasetComponent,
  DataZoomComponent,
  TitleComponent,
]);

import { createApp } from "vue";
import { createPinia } from "pinia";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";
import { QueryCache, QueryClient, VueQueryPlugin } from "@tanstack/vue-query";
import App from "./App.vue";
import router from "./router";
import i18nPlugin from "./plugins/i18n";

// 2. moz-ui 컴포넌트·그리드·차트 스타일 (그리드 본체 .ps-* 는 grid-wrapper 스타일에만 있음)
import "@vmscloud/moz-ui-components-core/styles/default";
import "@vmscloud/moz-ui-grid-wrapper/style.css";
import "@vmscloud/moz-ui-grid-vue/style.css";
import "@vmscloud/moz-ui-chart-vue/style.css";
import "./styles/moz-overrides.css";

// 커스텀 디렉티브 스타일
import "./directives/tooltip/_index.scss";

// 커스텀 디렉티브
import { tooltipDirective, loadingDirective } from "./directives";

// Pinia 설정
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (_error, query) => {
      queryClient.removeQueries(query);
    },
  }),
  defaultOptions: {
    queries: {
      refetchOnMount: false,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
      enabled: false,
      retry: 2,
    },
  },
});

const app = createApp(App);

app.use(pinia);
app.use(VueQueryPlugin, { queryClient });
app.use(router);
i18nPlugin(app);

// 커스텀 디렉티브 등록
app.directive("tooltip", tooltipDirective);
app.directive("loading", loadingDirective);

app.mount("#app");
