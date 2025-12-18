/**
 * 개발용 라우터
 * Host(APS)에서 로드 시에는 사용되지 않음
 */
import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
} from "vue-router";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "Home",
    component: () => import("@/views/HomeView.vue"),
  },
  {
    path: "/host-info",
    name: "HostInfo",
    component: () => import("@/views/customs/host-info/HostInfo.vue"),
  },
  {
    path: "/item-master",
    name: "ItemMaster",
    component: () => import("@/views/templates/basic1/ItemMaster.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
