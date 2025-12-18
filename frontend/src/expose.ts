/**
 * Module Federation으로 노출할 컴포넌트 정의
 * Host(APS)에서 이 파일을 통해 컴포넌트를 동적으로 import
 *
 * 주의: static export를 사용하면 모든 컴포넌트가 한꺼번에 로드되므로
 * 동적 import를 사용하는 viewRegistry만 제공합니다.
 */

// 뷰 목록 (Host에서 동적 라우팅에 사용)
// 동적 import를 사용하여 필요한 컴포넌트만 로드
// 현재: moz-component 미사용 화면만 등록
// 향후: 커스텀 확장앱 전용 moz-component 분리 후 ItemMasterWijmo 추가 예정
export const viewRegistry = {
  ItemMaster: () => import("./views/templates/basic1/ItemMaster.vue"),
  HostInfo: () => import("./views/customs/host-info/HostInfo.vue"),
  // ItemMasterWijmo: () => import("./views/templates/basic2/ItemMasterWijmo.vue"), // moz-component 사용 - 향후 활성화
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
