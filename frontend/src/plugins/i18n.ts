/**
 * i18next 플러그인 설정
 * 원본 APS의 i18n.ts와 동일한 방식으로 번역 리소스를 로드합니다.
 */
import i18next from 'i18next';
import I18NextVue from 'i18next-vue';
import type { App } from 'vue';

import koData from '@/lang/ko.json';
import enData from '@/lang/en.json';
import zhData from '@/lang/zh.json';
import jpData from '@/lang/jp.json';

// 언어 코드 → 리소스 매핑
const langResources: Record<string, Record<string, string>> = {
  ko: koData,
  en: enData,
  zh: zhData,
  jp: jpData,
};

// 기본 초기화 (APS와 동일한 방식)
i18next.init({
  fallbackLng: 'ko',
  lng: 'ko',
  resources: {
    ko: { translation: koData },
    en: { translation: enData },
    zh: { translation: zhData },
    jp: { translation: jpData },
  },
  interpolation: {
    escapeValue: false,
  },
});

/**
 * loadLanguage — 언어 전환
 * 원본 APS: SamLanguage API에서 동적으로 로드
 * 여기서는 정적 JSON에서 로드
 */
export async function loadLanguage(lang: string) {
  const data = langResources[lang];
  if (data) {
    i18next.addResourceBundle(lang, 'translation', data, true, true);
  }
  await i18next.changeLanguage(lang);
}

export default (app: App) => {
  app.use(I18NextVue, { i18next });
  return app;
};
