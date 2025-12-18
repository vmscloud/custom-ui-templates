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
    path: "/custom-menu-1",
    name: "CustomMenu1",
    component: () => import("@/views/customs/host-info/HostInfo.vue"),
  },
  {
    path: "/item-master",
    name: "ItemMaster",
    component: () => import("@/views/templates/basic1/ItemMaster.vue"),
  },
  {
    path: "/item-master-wijmo",
    name: "ItemMasterWijmo",
    component: () => import("@/views/templates/basic2/ItemMasterWijmo.vue"),
    meta: {
      navis: ["text-item_master", "text-wijmo_grid"],
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
