import { createRouter, createWebHistory } from "vue-router";

import { useAuthStore } from "@/stores/auth";
import DashboardView from "@/views/DashboardView.vue";
import LoginView from "@/views/LoginView.vue";
import PlansView from "@/views/PlansView.vue";
import RecordsView from "@/views/RecordsView.vue";
import ReviewView from "@/views/ReviewView.vue";
import SettingsView from "@/views/SettingsView.vue";
import TimerView from "@/views/TimerView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", component: LoginView, meta: { public: true } },
    { path: "/", component: DashboardView },
    { path: "/plans", component: PlansView },
    { path: "/timer", component: TimerView },
    { path: "/records", component: RecordsView },
    { path: "/review", component: ReviewView },
    { path: "/settings", component: SettingsView }
  ]
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (!auth.token && !to.meta.public) {
    return "/login";
  }
  if (auth.token && !auth.user) {
    await auth.fetchMe().catch(() => auth.logout());
  }
  if (to.path === "/login" && auth.token) {
    return "/";
  }
  return true;
});

export default router;
