/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

// Module Federation 타입
declare module 'external_app/*' {
  const component: any;
  export default component;
}

// 전역 Window 확장
declare global {
  interface Window {
    __POWERED_BY_APS_HOST__?: boolean;
  }
}

export {};

