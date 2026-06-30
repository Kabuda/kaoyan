<script setup lang="ts">
import { CalendarDays, Save, Sparkles } from "lucide-vue-next";
import { computed, onMounted, reactive, ref } from "vue";

import AppShell from "@/components/AppShell.vue";
import { todayISO, useStudyStore } from "@/stores/study";

const study = useStudyStore();
const dailyDate = ref(todayISO());
const dailyLoading = ref(false);
const monday = new Date();
monday.setDate(monday.getDate() - ((monday.getDay() + 6) % 7));

const form = reactive({
  week_start: monday.toISOString().slice(0, 10),
  summary: "",
  biggest_problem: "",
  delay_reason: "",
  english_review: "",
  math_review: "",
  computer_review: "",
  politics_review: "",
  next_week_adjustment: ""
});

onMounted(() => study.bootstrap());

const currentDailyReview = computed(() => study.dailyReviews.find((review) => review.review_date === dailyDate.value));

const generateDaily = async () => {
  dailyLoading.value = true;
  try {
    await study.generateDailyReview(dailyDate.value);
  } finally {
    dailyLoading.value = false;
  }
};

const submit = async () => {
  await study.createReview({ ...form });
  form.summary = "";
  form.biggest_problem = "";
  form.delay_reason = "";
  form.next_week_adjustment = "";
};
</script>

<template>
  <AppShell>
    <div class="page-grid two-column">
      <section class="panel">
        <div class="panel-heading">
          <div>
            <h2>本周复盘</h2>
            <span>把分数目标翻译成下一周动作</span>
          </div>
        </div>
        <div class="daily-review-box">
          <div class="subheading">
            <h3>今日复盘</h3>
            <span>{{ currentDailyReview?.model_status === "completed" ? "Doubao 生成" : "本地总结/待配置模型" }}</span>
          </div>
          <div class="daily-review-controls">
            <label>
              <CalendarDays :size="17" />
              <input v-model="dailyDate" type="date" @change="study.loadDailyReviews(dailyDate)" />
            </label>
            <button class="primary-pill" type="button" :disabled="dailyLoading" @click="generateDaily">
              <Sparkles :size="16" />
              {{ dailyLoading ? "生成中" : "生成今日总结" }}
            </button>
          </div>
          <div v-if="currentDailyReview" class="daily-review-result">
            <strong>{{ currentDailyReview.summary }}</strong>
            <p><b>完成内容：</b>{{ currentDailyReview.completed_content }}</p>
            <p><b>薄弱点：</b>{{ currentDailyReview.weak_points }}</p>
            <p><b>明日建议：</b>{{ currentDailyReview.next_actions }}</p>
          </div>
          <div v-else class="empty-state compact-empty">今天还没有生成复盘。完成计时或补录记录后，可以在这里汇总。</div>
        </div>
        <div class="review-metrics stacked">
          <div><span>本周学习</span><strong>{{ ((study.stats?.week_minutes ?? 0) / 60).toFixed(1) }} 小时</strong><small>月累计 {{ ((study.stats?.month_minutes ?? 0) / 60).toFixed(1) }} 小时</small></div>
          <div><span>数学投入</span><strong>{{ Math.round((study.stats?.math_week_ratio ?? 0) * 100) }}%</strong><small>目标主攻</small></div>
          <div><span>408 投入</span><strong>{{ Math.round((study.stats?.computer_week_ratio ?? 0) * 100) }}%</strong><small>稳步提分</small></div>
          <div><span>英语连续</span><strong>{{ study.stats?.english_streak_days ?? 0 }} 天</strong><small>不断档</small></div>
        </div>
        <div class="record-list">
          <article v-for="review in study.reviews" :key="review.id" class="record-row">
            <div>
              <strong>{{ review.week_start }} 周复盘</strong>
              <small>{{ review.biggest_problem || "暂无最大问题" }}</small>
            </div>
            <p>{{ review.summary || "暂无总结" }}</p>
          </article>
          <div v-if="!study.reviews.length" class="empty-state">写下第一条周复盘，后面就能看到策略变化。</div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-heading">
          <div>
            <h2>填写复盘</h2>
            <span>只记录能影响下周安排的内容</span>
          </div>
          <Save :size="18" />
        </div>
        <form class="form-grid" @submit.prevent="submit">
          <label class="full-span">
            <span>周开始日期</span>
            <input v-model="form.week_start" type="date" />
          </label>
          <label class="full-span">
            <span>本周总结</span>
            <textarea v-model="form.summary" rows="3" />
          </label>
          <label class="full-span">
            <span>最大问题</span>
            <textarea v-model="form.biggest_problem" rows="3" />
          </label>
          <label class="full-span">
            <span>拖延原因</span>
            <textarea v-model="form.delay_reason" rows="3" />
          </label>
          <label class="full-span">
            <span>下周调整</span>
            <textarea v-model="form.next_week_adjustment" rows="4" />
          </label>
          <button class="primary-button full-span" type="submit">保存周复盘</button>
        </form>
      </section>
    </div>
  </AppShell>
</template>
