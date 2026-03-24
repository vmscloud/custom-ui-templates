/**
 * 개발용 라우터
 * Host(APS)에서 로드 시에는 사용되지 않음
 */
import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
} from "vue-router";

export const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "Home",
    component: () => import("@/views/HomeView.vue"),
  },
  {
    path: "/host-info",
    name: "HostInfo",
    component: () => import("@/views/templates/basic/HostInfo.vue"),
  },
  {
    path: "/item-master",
    name: "ItemMaster",
    component: () => import("@/views/templates/basic/ItemMaster.vue"),
  },
  {
    path: "/sales-chart",
    name: "SalesChart",
    component: () => import("@/views/templates/chart/SalesChart.vue"),
  },
  {
    path: "/product-grid",
    name: "ProductGrid",
    component: () => import("@/views/templates/grid/ProductGrid.vue"),
  },
  {
    path: "/components-showcase",
    name: "ShowCase",
    component: () => import("@/views/templates/basic/ComponentsShowcase.vue"),
  },
  {
    path: "/demand-distribution",
    name: "DemandDistribution",
    component: () => import("@/views/templates/dm/DemandDistribution.vue"),
  },
  {
    path: "/rtf-report",
    name: "RtfReport",
    component: () => import("@/views/templates/sp/rtf-report/RtfReport.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
