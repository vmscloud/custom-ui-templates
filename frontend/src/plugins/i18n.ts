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
 * loadLanguageFromHost — systemmanagement SamLanguage API(용어관리 DB)로부터 번역 로드
 *
 * dev 단독 실행에서 정적 JSON 대신 용어관리 DB 번역을 쓰기 위한 함수다.
 * Host 에 로드된 화면은 Host 의 i18next 로 번역되므로 Host 경로에서는 호출하지 않는다.
 *
 * - vite dev 는 로그인 없이 호출할 수 있는 openapi 경로를, 배포 빌드는 게이트웨이 경로를 쓴다.
 * - 호출하는 곳은 DeveloperTool.ts 의 프로젝트 ID·언어 watcher 다.
 */
export async function loadLanguageFromHost(
  projectId: string,
  lang: string,
): Promise<boolean> {
  if (!projectId || !lang) return false;
  const base = import.meta.env.DEV
    ? '/api/openapi/common/system'
    : '/api/common/system';
  try {
    const res = await fetch(
      `${base}/${encodeURIComponent(projectId)}/SamLanguage/${encodeURIComponent(lang)}`,
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
