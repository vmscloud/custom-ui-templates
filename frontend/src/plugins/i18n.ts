/**
 * i18next 플러그인 설정
 * moz-component 내부에서 useTranslation을 사용하기 위한 최소 설정
 */
import i18next from 'i18next';
import I18NextVue from 'i18next-vue';
import type { App } from 'vue';
import ko from '@/locales/ko';

// 기본 초기화 (APS와 동일한 방식)
i18next.init({
  fallbackLng: 'ko',
  lng: 'ko',
  resources: {
    ko: { translation: ko },
    en: { translation: {} },
  },
  interpolation: {
    escapeValue: false,
  },
});

// 빈 번역 리소스 로드 함수 (standalone 모드용)
export async function loadLanguage(lang: string) {
  // standalone 모드에서는 번역 리소스가 없으므로 언어만 변경
  await i18next.changeLanguage(lang);
}

export default (app: App) => {
  app.use(I18NextVue, { i18next });
  return app;
};
