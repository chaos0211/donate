import type { RouteRecordRaw } from "vue-router";
import DefaultLayout from "@/layouts/DefaultLayout.vue";
import Login from "@/views/Login.vue";
import Register from "@/views/Register.vue";
import Cockpit from "@/views/Cockpit.vue";
import RankingList from "@/views/RankingList.vue";
// import RankingList from "@/views/Analytiscs.vue";

const routes: RouteRecordRaw[] = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: Login },
  { path: "/register", component: Register },
  {
    path: "/",
    component: DefaultLayout,
    children: [
      { path: "/cockpit", component: Cockpit },
      { path: "/ranking", component: RankingList },
      { path: '/DonateManager', component: () => import('@/views/DonateManager.vue'), meta: { title: '应用对比' } },
      { path: "/predict", component: () => import("@/views/Predict.vue"), meta: { title: "数据预测" } },
      { path: "/BlockchainManager", component: () => import("@/views/BlockchainManager.vue"), meta: { title: "区块链管理" } },
      { path: "/SystemManager", component: () => import("@/views/SystemManager.vue"), meta: { title: "系统管理" } },

]
  }
];
export default routes;
