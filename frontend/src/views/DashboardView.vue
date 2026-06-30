<script setup lang="ts">
import {
  Check,
  Clock3,
  Pause,
  Play,
  Plus,
  RefreshCw,
  RotateCcw,
  Square,
  TimerReset
} from "lucide-vue-next";
import { computed, onMounted, onUnmounted, ref } from "vue";

import AppShell from "@/components/AppShell.vue";
import { todayISO, useStudyStore } from "@/stores/study";
import type { StudyTask } from "@/types/api";

const study = useStudyStore();
const now = ref(Date.now());
const finishSummary = ref("复习了定积分应用，整理了常见题型和卡点。");

let ticker: number | undefined;

onMounted(async () => {
  await study.bootstrap();
  ticker = window.setInterval(() => {
    now.value = Date.now();
  }, 1000);
});

onUnmounted(() => {
  if (ticker) window.clearInterval(ticker);
});

const subjectLabel: Record<string, string> = {
  politics: "政治",
  english: "英语",
  math: "数学",
  "408": "408"
};

const subjectClass = (subject: string) => `tag tag-${subject === "408" ? "computer" : subject}`;
const labelOf = (subject: string) => subjectLabel[subject] || subject;

const planMinutes = computed(() => study.plannedMinutes || study.profile?.daily_target_minutes || 405);
const actualMinutes = computed(() => study.stats?.today_minutes || study.actualTaskMinutes);
const completionPercent = computed(() => {
  if (!planMinutes.value) return 0;
  return Math.min(100, Math.round((actualMinutes.value / planMinutes.value) * 100));
});

const timerSeconds = computed(() => {
  const timer = study.timer;
  if (!timer) return 0;
  const base = timer.accumulated_seconds;
  if (timer.status !== "running") return base;
  return base + Math.max(0, Math.floor((now.value - new Date(timer.started_at).getTime()) / 1000));
});

const timerText = computed(() => {
  const seconds = timerSeconds.value;
  const h = String(Math.floor(seconds / 3600)).padStart(2, "0");
  const m = String(Math.floor((seconds % 3600) / 60)).padStart(2, "0");
  const s = String(seconds % 60).padStart(2, "0");
  return `${h}:${m}:${s}`;
});

const activeTask = computed(() => study.currentTask || study.tasks.find((task) => task.status !== "completed") || null);
const weeklyHours = computed(() => ((study.stats?.week_minutes ?? 0) / 60).toFixed(1));
const dailyTrend = computed(() => study.stats?.recent_7_days || []);
const maxTrend = computed(() => Math.max(360, ...dailyTrend.value.map((point) => point.minutes)));

const targetGapRows = computed(() => {
  const profile = study.profile;
  const firstTotal =
    (profile?.first_politics_score ?? 64) +
    (profile?.first_english_score ?? 46) +
    (profile?.first_math_score ?? 74) +
    (profile?.first_408_score ?? 83);
  return [
    ["政治", profile?.first_politics_score ?? 64, profile?.target_politics_score ?? 65],
    ["英语", profile?.first_english_score ?? 46, profile?.target_english_score ?? 55],
    ["数学", profile?.first_math_score ?? 74, profile?.target_math_score ?? 110],
    ["408", profile?.first_408_score ?? 83, profile?.target_408_score ?? 100],
    ["总分", firstTotal, profile?.target_total_score ?? 330]
  ];
});

const start = async (task: StudyTask) => {
  await study.startTimer(task.id);
};
</script>

<template>
  <AppShell>
    <div class="dashboard-grid">
      <section class="panel plan-panel">
        <div class="panel-heading">
          <div>
            <h2>今日计划</h2>
            <span>{{ todayISO() }} · 计划 {{ (planMinutes / 60).toFixed(1) }} 小时</span>
          </div>
          <button class="ghost-button" type="button" @click="study.generateDailyTemplate()">
            <Plus :size="17" />
            生成计划
          </button>
        </div>
        <div class="plan-progress">
          <span>已完成 {{ (actualMinutes / 60).toFixed(1) }} 小时</span>
          <strong>完成度 {{ completionPercent }}%</strong>
          <div class="progress-line large"><i :style="{ width: `${completionPercent}%` }"></i></div>
        </div>
        <div class="task-list">
          <div v-for="task in study.tasks" :key="task.id" class="task-row">
            <button class="check-button" :class="{ done: task.status === 'completed' }" @click="study.completeTask(task.id)">
              <Check v-if="task.status === 'completed'" :size="16" />
            </button>
            <span class="time-range">{{ task.actual_minutes ? "已学" : "计划" }}</span>
            <span :class="subjectClass(task.subject)">{{ labelOf(task.subject) }}</span>
            <strong>{{ task.title }}</strong>
            <span class="task-minutes">{{ task.estimated_minutes }} 分钟</span>
            <button class="icon-button" type="button" @click="start(task)" :disabled="Boolean(study.timer)">
              <Play :size="16" />
            </button>
          </div>
          <div v-if="!study.tasks.length" class="empty-state">
            今天还没有计划，先生成一套英语不断档、数学主攻、408 稳步提分的任务。
          </div>
        </div>
      </section>

      <section class="panel timer-panel">
        <div class="panel-heading">
          <div>
            <h2>学习计时</h2>
            <span>{{ study.timer?.status === "paused" ? "休息中" : "专注模式" }}</span>
          </div>
          <TimerReset :size="22" />
        </div>
        <div class="timer-ring" :style="{ '--timer-progress': `${Math.min(100, (timerSeconds / 7200) * 100)}%` }">
          <div>
            <span>{{ study.timer ? "专注中" : "等待开始" }}</span>
            <strong>{{ timerText }}</strong>
            <small>目标 120 分钟</small>
          </div>
        </div>
        <div class="current-task">
          <span>当前任务</span>
          <strong>{{ activeTask?.title || "选择一个计划任务开始" }}</strong>
          <small v-if="activeTask">
            {{ labelOf(activeTask.subject) }} · {{ activeTask.estimated_minutes }} 分钟
          </small>
        </div>
        <div class="timer-actions">
          <button v-if="study.timer?.status === 'running'" class="secondary-round" @click="study.pauseTimer()">
            <Pause :size="20" />
            暂停
          </button>
          <button v-else-if="study.timer?.status === 'paused'" class="secondary-round" @click="study.resumeTimer()">
            <Play :size="20" />
            继续
          </button>
          <button v-else class="secondary-round" :disabled="!activeTask" @click="activeTask && start(activeTask)">
            <Play :size="20" />
            开始
          </button>
          <button class="primary-pill" :disabled="!study.timer" @click="study.finishTimer(finishSummary)">
            <Square :size="16" />
            结束并记录
          </button>
          <button class="icon-button large-icon" @click="study.loadTimer()">
            <RotateCcw :size="19" />
          </button>
        </div>
        <label class="note-box">
          <span>学习记录（本次）</span>
          <textarea v-model="finishSummary" rows="4" maxlength="200" />
        </label>
      </section>

      <section class="panel trend-panel">
        <div class="panel-heading">
          <div>
            <h2>7 天学习趋势</h2>
            <span>单位：小时</span>
          </div>
          <div class="segmented"><button>今日</button><button class="active">本周</button></div>
        </div>
        <div class="bar-chart">
          <div v-for="point in dailyTrend" :key="point.date" class="bar-column">
            <span>{{ (point.minutes / 60).toFixed(1) }}</span>
            <i :style="{ height: `${Math.max(10, (point.minutes / maxTrend) * 170)}px` }"></i>
            <small>{{ point.date.slice(5) }}</small>
          </div>
        </div>
        <div class="target-gap">
          <div class="subheading">
            <h3>目标差距</h3>
            <span>更新于今日</span>
          </div>
          <div class="gap-table">
            <div class="gap-head"><span>科目</span><span>首战</span><span>目标</span><span>差距</span></div>
            <div v-for="[name, first, target] in targetGapRows" :key="name" class="gap-row">
              <span>{{ name }}</span>
              <span>{{ first }}</span>
              <strong>{{ target }}</strong>
              <em>{{ Number(first) - Number(target) }}</em>
            </div>
          </div>
        </div>
      </section>

      <section class="panel distribution-panel">
        <div class="panel-heading">
          <div>
            <h2>今日专注分布</h2>
            <span>按学科拆分</span>
          </div>
          <RefreshCw :size="18" />
        </div>
        <div class="distribution-content">
          <div
            class="donut"
            :style="{
              background: `conic-gradient(#ef4444 0 34%, #2563eb 34% 68%, #f59e0b 68% 88%, #93c5fd 88% 100%)`
            }"
          ></div>
          <div class="legend-list">
            <div v-for="item in study.stats?.subject_distribution || []" :key="item.name">
              <span :class="subjectClass(item.name)">{{ labelOf(item.name) }}</span>
              <strong>{{ (item.minutes / 60).toFixed(1) }} 小时</strong>
            </div>
            <div v-if="!(study.stats?.subject_distribution || []).length">暂无记录，完成一次计时后这里会自动更新。</div>
          </div>
          <div class="today-total">
            <span>今日总计</span>
            <strong>{{ (actualMinutes / 60).toFixed(1) }} 小时</strong>
          </div>
        </div>
      </section>

      <section class="panel review-panel">
        <div class="panel-heading">
          <div>
            <h2>本周复盘</h2>
            <span>节奏、完成率、正确率</span>
          </div>
          <Clock3 :size="18" />
        </div>
        <div class="review-metrics">
          <div><span>本周学习时长</span><strong>{{ weeklyHours }} 小时</strong><small>日均 {{ ((Number(weeklyHours) || 0) / 7).toFixed(1) }} 小时</small></div>
          <div><span>完成任务</span><strong>{{ study.completedTasks.length }} / {{ study.tasks.length || 1 }}</strong><small>完成率 {{ Math.round((study.stats?.task_completion_rate ?? 0) * 100) }}%</small></div>
          <div><span>英语不断档</span><strong>{{ study.stats?.english_streak_days ?? 0 }} 天</strong><small>风险科目</small></div>
          <div><span>408 占比</span><strong>{{ Math.round((study.stats?.computer_week_ratio ?? 0) * 100) }}%</strong><small>稳步提分</small></div>
        </div>
      </section>
    </div>
  </AppShell>
</template>
