<script setup lang="ts">
import {
  BarChart3,
  BookOpenCheck,
  CalendarCheck2,
  ClipboardList,
  Clock3,
  Gauge,
  LogOut,
  Settings,
  Target
} from "lucide-vue-next";
import { computed, onMounted } from "vue";
import { RouterLink, useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";
import { useStudyStore } from "@/stores/study";

const auth = useAuthStore();
const study = useStudyStore();
const router = useRouter();

onMounted(() => {
  if (!study.profile && auth.token) {
    study.bootstrap().catch(() => undefined);
  }
});

const navItems = [
  { path: "/", label: "仪表盘", icon: Gauge },
  { path: "/plans", label: "今日计划", icon: CalendarCheck2 },
  { path: "/timer", label: "学习计时", icon: Clock3 },
  { path: "/records", label: "学习记录", icon: ClipboardList },
  { path: "/review", label: "复盘", icon: BarChart3 },
  { path: "/settings", label: "设置", icon: Settings }
];

const firstScores = computed(() => {
  const profile = study.profile;
  return [
    ["政治", profile?.first_politics_score ?? 64],
    ["英语", profile?.first_english_score ?? 46],
    ["数学", profile?.first_math_score ?? 74],
    ["408", profile?.first_408_score ?? 83],
    ["总分", totalFirstScore.value]
  ];
});

const totalFirstScore = computed(() => {
  const profile = study.profile;
  return (
    (profile?.first_politics_score ?? 64) +
    (profile?.first_english_score ?? 46) +
    (profile?.first_math_score ?? 74) +
    (profile?.first_408_score ?? 83)
  );
});

const targetTotal = computed(() => study.profile?.target_total_score ?? 330);

const logout = () => {
  auth.logout();
  router.push("/login");
};
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand-block">
        <div class="brand-title">11408 考研</div>
        <div class="brand-subtitle">二战上岸计划</div>
      </div>

      <nav class="side-nav" aria-label="主导航">
        <RouterLink v-for="item in navItems" :key="item.path" :to="item.path" class="nav-item">
          <component :is="item.icon" :size="20" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <section class="score-panel">
        <div class="score-panel-title">
          <BookOpenCheck :size="17" />
          首次成绩
        </div>
        <div v-for="[label, value] in firstScores" :key="label" class="score-row">
          <span>{{ label }}</span>
          <strong>{{ value }}</strong>
        </div>
      </section>
    </aside>

    <main class="main-surface">
      <header class="top-strip">
        <div class="strip-cell">
          <span>距离 2026 考研</span>
          <strong class="green-text">210 天</strong>
          <small>2026-12-26 考试</small>
        </div>
        <div class="strip-cell">
          <span>目标总分</span>
          <strong>{{ targetTotal }}</strong>
          <small>当前 {{ totalFirstScore }} / {{ targetTotal }}</small>
        </div>
        <div class="strip-cell wide">
          <span>关键目标</span>
          <div class="goal-line">
            <Target :size="16" />
            <strong>数学 {{ study.profile?.target_math_score ?? 110 }}</strong>
            <span>当前 {{ study.profile?.first_math_score ?? 74 }}</span>
          </div>
          <div class="progress-line"><i :style="{ width: '67%' }"></i></div>
        </div>
        <div class="strip-cell wide">
          <span>408</span>
          <div class="goal-line">
            <strong>{{ study.profile?.target_408_score ?? 100 }}</strong>
            <span>当前 {{ study.profile?.first_408_score ?? 83 }}</span>
          </div>
          <div class="progress-line amber"><i :style="{ width: '83%' }"></i></div>
        </div>
        <div class="strip-cell">
          <span>今日已学</span>
          <strong>{{ ((study.stats?.today_minutes ?? 0) / 60).toFixed(1) }} 小时</strong>
          <small>目标 {{ ((study.stats?.today_target_minutes ?? 405) / 60).toFixed(1) }} 小时</small>
        </div>
        <button class="icon-text-button" type="button" @click="logout">
          <LogOut :size="18" />
          退出
        </button>
      </header>

      <slot />
    </main>
  </div>
</template>
