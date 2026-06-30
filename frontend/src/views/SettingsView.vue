<script setup lang="ts">
import { Save } from "lucide-vue-next";
import { onMounted, reactive, watch } from "vue";

import AppShell from "@/components/AppShell.vue";
import { useStudyStore } from "@/stores/study";

const study = useStudyStore();
const form = reactive({
  first_politics_score: 64,
  first_english_score: 46,
  first_math_score: 74,
  first_408_score: 83,
  target_politics_score: 65,
  target_english_score: 55,
  target_math_score: 110,
  target_408_score: 100,
  target_total_score: 330,
  exam_date: "",
  daily_target_minutes: 405,
  weak_points: "英语不断档，数学主攻，408 稳步提分"
});

onMounted(() => study.bootstrap());

watch(
  () => study.profile,
  (profile) => {
    if (!profile) return;
    Object.assign(form, {
      first_politics_score: profile.first_politics_score,
      first_english_score: profile.first_english_score,
      first_math_score: profile.first_math_score,
      first_408_score: profile.first_408_score,
      target_politics_score: profile.target_politics_score,
      target_english_score: profile.target_english_score,
      target_math_score: profile.target_math_score,
      target_408_score: profile.target_408_score,
      target_total_score: profile.target_total_score,
      exam_date: profile.exam_date || "",
      daily_target_minutes: profile.daily_target_minutes,
      weak_points: profile.weak_points
    });
  },
  { immediate: true }
);

const submit = () =>
  study.updateProfile({
    ...form,
    exam_date: form.exam_date || null
  });
</script>

<template>
  <AppShell>
    <section class="panel settings-panel">
      <div class="panel-heading">
        <div>
          <h2>设置</h2>
          <span>维护一战基线、二战目标和每日学习节奏</span>
        </div>
        <Save :size="18" />
      </div>
      <form class="settings-form" @submit.prevent="submit">
        <fieldset>
          <legend>一战成绩</legend>
          <label><span>政治</span><input v-model.number="form.first_politics_score" type="number" /></label>
          <label><span>英语</span><input v-model.number="form.first_english_score" type="number" /></label>
          <label><span>数学</span><input v-model.number="form.first_math_score" type="number" /></label>
          <label><span>408</span><input v-model.number="form.first_408_score" type="number" /></label>
        </fieldset>
        <fieldset>
          <legend>二战目标</legend>
          <label><span>政治</span><input v-model.number="form.target_politics_score" type="number" /></label>
          <label><span>英语</span><input v-model.number="form.target_english_score" type="number" /></label>
          <label><span>数学</span><input v-model.number="form.target_math_score" type="number" /></label>
          <label><span>408</span><input v-model.number="form.target_408_score" type="number" /></label>
          <label><span>总分</span><input v-model.number="form.target_total_score" type="number" /></label>
        </fieldset>
        <fieldset>
          <legend>学习节奏</legend>
          <label><span>考试日期</span><input v-model="form.exam_date" type="date" /></label>
          <label><span>每日目标分钟</span><input v-model.number="form.daily_target_minutes" type="number" /></label>
          <label class="wide-field"><span>弱点策略</span><textarea v-model="form.weak_points" rows="4" /></label>
        </fieldset>
        <button class="primary-button" type="submit">保存设置</button>
      </form>
    </section>
  </AppShell>
</template>
