/**
 * 애플리케이션 부트스트랩
 * Module Federation의 비동기 로딩을 위한 분리
 */
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
import { VueQueryPlugin } from '@tanstack/vue-query';
import { createSharedStoresPlugin } from '@vmscloud/moz-component';
import App from './App.vue';
import router from './router';
import { useProjectInfoStore } from './stores/mainStore';
import i18nPlugin from './plugins/i18n';

// Wijmo 스타일 임포트
import '@grapecity/wijmo.styles/wijmo.css';

// moz-component 스타일 임포트
import '@vmscloud/moz-component/style.css';

// Pinia 설정
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

const app = createApp(App);

app.use(pinia);
app.use(VueQueryPlugin);
app.use(router);

// i18next 플러그인 (moz-component에서 useTranslation 사용)
i18nPlugin(app);

// 스토어 공유 플러그인 적용 (독립 실행 시에만 사용)
// APS에서 로드될 때는 Host의 스토어가 inject됨
app.use(
  createSharedStoresPlugin({
    projectInfo: () => useProjectInfoStore(),
  }),
);

app.mount('#app');
