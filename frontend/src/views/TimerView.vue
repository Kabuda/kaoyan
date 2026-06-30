<script setup lang="ts">
import { Pause, Play, Square } from "lucide-vue-next";
import { computed, onMounted, onUnmounted, ref } from "vue";

import AppShell from "@/components/AppShell.vue";
import { useStudyStore } from "@/stores/study";

const study = useStudyStore();
const now = ref(Date.now());
const summary = ref("");
let ticker: number | undefined;

onMounted(async () => {
  await study.bootstrap();
  ticker = window.setInterval(() => (now.value = Date.now()), 1000);
});
onUnmounted(() => {
  if (ticker) window.clearInterval(ticker);
});

const elapsed = computed(() => {
  const timer = study.timer;
  if (!timer) return 0;
  const live = timer.status === "running" ? Math.floor((now.value - new Date(timer.started_at).getTime()) / 1000) : 0;
  return timer.accumulated_seconds + Math.max(0, live);
});

const timerText = computed(() => {
  const h = String(Math.floor(elapsed.value / 3600)).padStart(2, "0");
  const m = String(Math.floor((elapsed.value % 3600) / 60)).padStart(2, "0");
  const s = String(elapsed.value % 60).padStart(2, "0");
  return `${h}:${m}:${s}`;
});
</script>

<template>
  <AppShell>
    <div class="page-grid two-column">
      <section class="panel timer-focus-panel">
        <div class="panel-heading">
          <div>
            <h2>学习计时</h2>
            <span>服务端保存状态，刷新页面也不丢</span>
          </div>
        </div>
        <div class="timer-ring oversized" :style="{ '--timer-progress': `${Math.min(100, (elapsed / 7200) * 100)}%` }">
          <div>
            <span>{{ study.timer?.status === "paused" ? "休息中" : study.timer ? "专注中" : "等待任务" }}</span>
            <strong>{{ timerText }}</strong>
            <small>建议单次 90-120 分钟</small>
          </div>
        </div>
        <div class="timer-actions center">
          <button v-if="study.timer?.status === 'running'" class="secondary-round" @click="study.pauseTimer()">
            <Pause :size="20" />
            暂停
          </button>
          <button v-else-if="study.timer?.status === 'paused'" class="secondary-round" @click="study.resumeTimer()">
            <Play :size="20" />
            继续
          </button>
          <button class="primary-pill" :disabled="!study.timer" @click="study.finishTimer(summary || '完成一次专注学习。')">
            <Square :size="16" />
            结束并记录
          </button>
        </div>
        <label class="note-box">
          <span>结束记录</span>
          <textarea v-model="summary" rows="5" placeholder="这次解决了什么？卡在哪里？下一次从哪里继续？" />
        </label>
      </section>

      <section class="panel">
        <div class="panel-heading">
          <div>
            <h2>选择任务</h2>
            <span>同一时间只允许一个运行中计时</span>
          </div>
        </div>
        <div class="task-list spacious">
          <div v-for="task in study.tasks.filter((item) => item.status !== 'completed')" :key="task.id" class="task-row">
            <span class="tag" :class="`tag-${task.subject === '408' ? 'computer' : task.subject}`">{{ task.subject }}</span>
            <strong>{{ task.title }}</strong>
            <span class="task-minutes">{{ task.estimated_minutes }} 分钟</span>
            <button class="primary-icon" :disabled="Boolean(study.timer)" @click="study.startTimer(task.id)">
              <Play :size="16" />
            </button>
          </div>
          <div v-if="!study.tasks.length" class="empty-state">先到今日计划生成任务，再开始计时。</div>
        </div>
      </section>
    </div>
  </AppShell>
</template>
