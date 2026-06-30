<script setup lang="ts">
import { Save } from "lucide-vue-next";
import { onMounted, reactive } from "vue";

import AppShell from "@/components/AppShell.vue";
import { useStudyStore } from "@/stores/study";

const study = useStudyStore();
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
