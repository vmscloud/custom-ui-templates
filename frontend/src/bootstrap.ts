/**
 * 애플리케이션 부트스트랩
 * Module Federation의 비동기 로딩을 위한 분리
 */
import { createApp } from "vue";
import { createPinia } from "pinia";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";
import { VueQueryPlugin } from "@tanstack/vue-query";
import App from "./App.vue";
import router from "./router";
import i18nPlugin from "./plugins/i18n";

// 1. 로컬 테마/CSS 변수 (moz-component 스타일보다 먼저 로드)
import "./styles/index.scss";

// 2. moz-ui-components 스타일 (Tailwind CSS 포함)
import "@vmscloud/moz-ui-components/style.css";

// Wijmo 한국어 문화 설정
import "@grapecity/wijmo.cultures/wijmo.culture.ko";

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
