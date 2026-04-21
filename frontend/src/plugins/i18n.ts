/**
 * i18next 플러그인 설정
 * 원본 APS의 i18n.ts와 동일한 방식으로 번역 리소스를 로드합니다.
 */
import i18next from 'i18next';
import I18NextVue from 'i18next-vue';
import type { App } from 'vue';
import ko from '@/locales/ko';

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
 * loadLanguage — 정적 JSON 기반 언어 전환 (dev 단독 실행 전용)
 */
export async function loadLanguage(lang: string) {
  const data = langResources[lang];
  if (data) {
    i18next.addResourceBundle(lang, 'translation', data, true, true);
  }
  await i18next.changeLanguage(lang);
}

/**
 * loadLanguageFromHost — APS SamLanguage API 로부터 번역 로드
 *
 * Module Federation 으로 호스트 환경에 올라갔을 때 사용.
 * 원본 APS `packages/aps/src/utils/i18n.ts` 의 loadLanguage 와 동일한 패턴.
 *
 * - host 와 리모트의 i18next 는 각각 독립 인스턴스라 서로의 resource 를 덮지 않음
 * - 원본 서버 번역(정식 text-* 키) 을 리모트의 i18next 에 그대로 주입해 이용
 * - 세션이 없으면 401 — 그 경우 정적 JSON(위 init 결과) 을 유지
 */
export async function loadLanguageFromHost(
  projectId: string,
  lang: string,
): Promise<boolean> {
  if (!projectId || !lang) return false;
  try {
    const res = await fetch(
      `/api/aps/backend/${encodeURIComponent(projectId)}/SamLanguage/${encodeURIComponent(lang)}`,
      { credentials: 'include' },
    );
    if (!res.ok) return false;
    const body = await res.json();
    const data = body?.data;
    if (!data) return false;
    if (data.sys) {
      i18next.addResourceBundle('sy', 'translation', data.sys, true, true);
    }
    if (data.lang) {
      i18next.addResourceBundle(lang, 'translation', data.lang, true, true);
    }
    if (i18next.language !== lang) {
      await i18next.changeLanguage(lang);
    }
    return true;
  } catch (e) {
    console.warn('[i18n] SamLanguage 로드 실패', e);
    return false;
  }
}

export default (app: App) => {
  app.use(I18NextVue, { i18next });
  return app;
};
