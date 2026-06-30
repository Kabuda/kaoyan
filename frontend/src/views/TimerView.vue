<script setup lang="ts">
import { ImagePlus, Pause, Play, Sparkles, Square, X } from "lucide-vue-next";
import { computed, onMounted, onUnmounted, ref } from "vue";

import AppShell from "@/components/AppShell.vue";
import { useStudyStore } from "@/stores/study";

const study = useStudyStore();
const now = ref(Date.now());
const summary = ref("");
const selectedFiles = ref<File[]>([]);
const analysisLoading = ref(false);
const finishError = ref("");
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

const onFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement;
  selectedFiles.value = Array.from(input.files || []);
};

const removeFile = (index: number) => {
  selectedFiles.value = selectedFiles.value.filter((_, currentIndex) => currentIndex !== index);
};

const finishWithImages = async () => {
  finishError.value = "";
  analysisLoading.value = true;
  try {
    if (selectedFiles.value.length) {
      await study.finishTimerWithImages(summary.value || "完成一次专注学习。", selectedFiles.value);
    } else {
      await study.finishTimer(summary.value || "完成一次专注学习。");
      study.latestImageAnalyses = [];
    }
    selectedFiles.value = [];
    summary.value = "";
  } catch {
    finishError.value = "结束计时失败，请检查图片格式或稍后重试。";
  } finally {
    analysisLoading.value = false;
  }
};
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
          <button class="primary-pill" :disabled="!study.timer || analysisLoading" @click="finishWithImages">
            <Square :size="16" />
            {{ selectedFiles.length ? "结束并分析" : "结束并记录" }}
          </button>
        </div>
        <label class="note-box">
          <span>结束记录</span>
          <textarea v-model="summary" rows="5" placeholder="这次解决了什么？卡在哪里？下一次从哪里继续？" />
        </label>
        <div class="upload-box">
          <label class="upload-control">
            <ImagePlus :size="18" />
            上传完成题目图片
            <input type="file" accept="image/png,image/jpeg,image/webp" multiple @change="onFileChange" />
          </label>
          <div v-if="selectedFiles.length" class="file-list">
            <div v-for="(file, index) in selectedFiles" :key="file.name + index">
              <span>{{ file.name }}</span>
              <button type="button" class="icon-button" @click="removeFile(index)">
                <X :size="15" />
              </button>
            </div>
          </div>
          <p v-if="finishError" class="form-error">{{ finishError }}</p>
        </div>
        <div v-if="study.latestImageAnalyses.length" class="analysis-list">
          <div class="panel-heading compact-heading">
            <div>
              <h2>Doubao 分析</h2>
              <span>本次题目图片分析结果</span>
            </div>
            <Sparkles :size="18" />
          </div>
          <article v-for="image in study.latestImageAnalyses" :key="image.id" class="analysis-card">
            <div>
              <strong>{{ image.original_filename }}</strong>
              <span class="tag" :class="image.analysis_status === 'completed' ? 'tag-english' : 'tag-computer'">
                {{ image.analysis_status === "completed" ? "已分析" : image.analysis_status === "skipped" ? "待配置" : "失败" }}
              </span>
            </div>
            <p>{{ image.analysis_text }}</p>
            <small v-if="image.suggestions">建议：{{ image.suggestions }}</small>
          </article>
        </div>
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
