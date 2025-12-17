/**
 * 개발용 라우터
 * Host(APS)에서 로드 시에는 사용되지 않음
 */
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
  },
  {
    path: '/custom-menu-1',
    name: 'CustomMenu1',
    component: () => import('@/views/CustomMenu1/CustomMenu1.vue'),
  },
  {
    path: '/custom-menu-2',
    name: 'CustomMenu2',
    component: () => import('@/views/CustomMenu2/CustomMenu2.vue'),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

