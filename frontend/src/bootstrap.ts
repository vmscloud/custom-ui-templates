/**
 * 애플리케이션 부트스트랩
 * Module Federation의 비동기 로딩을 위한 분리
 */

// ECharts 초기화 (가장 먼저 실행되어야 함)
// 단독 개발 환경에서 CanvasRenderer가 등록되지 않는 문제 해결
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { BarChart, LineChart, PieChart, ScatterChart } from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DatasetComponent,
  DataZoomComponent,
  TitleComponent,
} from "echarts/components";

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
import { VueQueryPlugin } from "@tanstack/vue-query";
import App from "./App.vue";
import router from "./router";
import i18nPlugin from "./plugins/i18n";

// 2. moz-ui-components 스타일 (Wijmo Grid 커스터마이징 포함, 마지막에 덮어쓰기)
import "@vmscloud/moz-ui-components/style.css";

// Pinia 설정
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

const app = createApp(App);

app.use(pinia);
app.use(VueQueryPlugin);
app.use(router);

// i18next 플러그인 (moz-component에서 useTranslation 사용)
i18nPlugin(app);

app.mount("#app");
