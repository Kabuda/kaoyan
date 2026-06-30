<script setup lang="ts">
import { Check, Play, Plus, SkipForward } from "lucide-vue-next";
import { onMounted, reactive } from "vue";

import AppShell from "@/components/AppShell.vue";
import { todayISO, useStudyStore } from "@/stores/study";

const study = useStudyStore();

const form = reactive({
  plan_date: todayISO(),
  subject: "math",
  module: "advanced_math",
  title: "高数：定积分应用专项",
  task_type: "practice",
  estimated_minutes: 120,
  priority: 1,
  note: ""
});

const subjectOptions = [
  ["math", "数学"],
  ["408", "408"],
  ["english", "英语"],
  ["politics", "政治"]
];

onMounted(() => study.bootstrap());

const submit = async () => {
  await study.createTask({ ...form });
  form.title = "";
  form.note = "";
};
</script>

<template>
  <AppShell>
    <div class="page-grid two-column">
      <section class="panel">
        <div class="panel-heading">
          <div>
            <h2>今日计划</h2>
            <span>按科目、模块和时长拆成可执行任务</span>
          </div>
          <button class="ghost-button" @click="study.generateDailyTemplate(form.plan_date)">
            <Plus :size="17" />
            一键生成
          </button>
        </div>

        <div class="task-list spacious">
          <div v-for="task in study.tasks" :key="task.id" class="task-row">
            <button class="check-button" :class="{ done: task.status === 'completed' }" @click="study.completeTask(task.id)">
              <Check v-if="task.status === 'completed'" :size="16" />
            </button>
            <span class="tag" :class="`tag-${task.subject === '408' ? 'computer' : task.subject}`">
              {{ task.subject === "english" ? "英语" : task.subject === "math" ? "数学" : task.subject === "politics" ? "政治" : "408" }}
            </span>
            <strong>{{ task.title }}</strong>
            <span class="task-minutes">{{ task.estimated_minutes }} 分钟</span>
            <button class="icon-button" @click="study.startTimer(task.id)" :disabled="Boolean(study.timer) || task.status === 'completed'">
              <Play :size="16" />
            </button>
            <button class="icon-button" @click="study.skipTask(task.id)">
              <SkipForward :size="16" />
            </button>
          </div>
          <div v-if="!study.tasks.length" class="empty-state">还没有任务，先生成一套今日计划。</div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-heading">
          <div>
            <h2>添加任务</h2>
            <span>围绕数学主攻、英语不断档、408 稳步提分</span>
          </div>
        </div>
        <form class="form-grid" @submit.prevent="submit">
          <label>
            <span>日期</span>
            <input v-model="form.plan_date" type="date" @change="study.loadTasks(form.plan_date)" />
          </label>
          <label>
            <span>科目</span>
            <select v-model="form.subject">
              <option v-for="[value, label] in subjectOptions" :key="value" :value="value">{{ label }}</option>
            </select>
          </label>
          <label>
            <span>模块</span>
            <input v-model="form.module" />
          </label>
          <label>
            <span>预计分钟</span>
            <input v-model.number="form.estimated_minutes" type="number" min="0" max="1440" />
          </label>
          <label class="full-span">
            <span>任务标题</span>
            <input v-model="form.title" placeholder="例如：线代特征值与特征向量" />
          </label>
          <label class="full-span">
            <span>备注</span>
            <textarea v-model="form.note" rows="4" placeholder="材料、题号、复盘点" />
          </label>
          <button class="primary-button full-span" type="submit">保存任务</button>
        </form>
      </section>
    </div>
  </AppShell>
</template>
