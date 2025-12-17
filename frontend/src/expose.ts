/**
 * Module Federation으로 노출할 컴포넌트 정의
 * Host(APS)에서 이 파일을 통해 컴포넌트를 동적으로 import
 */

// 뷰 컴포넌트들을 export
export { default as CustomMenu1 } from './views/CustomMenu1/CustomMenu1.vue';
export { default as CustomMenu2 } from './views/CustomMenu2/CustomMenu2.vue';

// 뷰 목록 (Host에서 동적 라우팅에 사용)
export const viewRegistry = {
  CustomMenu1: () => import('./views/CustomMenu1/CustomMenu1.vue'),
  CustomMenu2: () => import('./views/CustomMenu2/CustomMenu2.vue'),
} as const;

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

