<script setup lang="ts">
import { Plus } from "lucide-vue-next";
import { computed, onMounted, reactive } from "vue";

import AppShell from "@/components/AppShell.vue";
import { useStudyStore } from "@/stores/study";

const study = useStudyStore();
const now = new Date();
const start = new Date(now.getTime() - 60 * 60 * 1000);

const form = reactive({
  subject: "math",
  module: "advanced_math",
  task_type: "manual",
  title: "手动补录：错题复盘",
  started_at: start.toISOString().slice(0, 16),
  ended_at: now.toISOString().slice(0, 16),
  duration_minutes: 60,
  summary: "",
  blockers: "",
  quality: "medium"
});

onMounted(() => study.bootstrap());

const totalHours = computed(() => (study.records.reduce((sum, record) => sum + record.duration_minutes, 0) / 60).toFixed(1));

const submit = async () => {
  await study.createRecord({
    ...form,
    started_at: new Date(form.started_at).toISOString(),
    ended_at: new Date(form.ended_at).toISOString()
  });
};
</script>

<template>
  <AppShell>
    <div class="page-grid two-column">
      <section class="panel">
        <div class="panel-heading">
          <div>
            <h2>学习记录</h2>
            <span>已沉淀 {{ totalHours }} 小时</span>
          </div>
        </div>
        <div class="record-list">
          <article v-for="record in study.records" :key="record.id" class="record-row">
            <div>
              <span class="tag" :class="`tag-${record.subject === '408' ? 'computer' : record.subject}`">{{ record.subject }}</span>
              <strong>{{ record.title }}</strong>
              <small>{{ record.started_at.slice(0, 16).replace("T", " ") }} · {{ record.duration_minutes }} 分钟</small>
            </div>
            <p>{{ record.summary || "暂无总结" }}</p>
          </article>
          <div v-if="!study.records.length" class="empty-state">完成计时或手动补录后，记录会出现在这里。</div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-heading">
          <div>
            <h2>手动补录</h2>
            <span>适合线下刷题、自习室复盘后补记</span>
          </div>
          <Plus :size="18" />
        </div>
        <form class="form-grid" @submit.prevent="submit">
          <label>
            <span>科目</span>
            <select v-model="form.subject">
              <option value="math">数学</option>
              <option value="408">408</option>
              <option value="english">英语</option>
              <option value="politics">政治</option>
            </select>
          </label>
          <label>
            <span>模块</span>
            <input v-model="form.module" />
          </label>
          <label class="full-span">
            <span>标题</span>
            <input v-model="form.title" />
          </label>
          <label>
            <span>开始</span>
            <input v-model="form.started_at" type="datetime-local" />
          </label>
          <label>
            <span>结束</span>
            <input v-model="form.ended_at" type="datetime-local" />
          </label>
          <label>
            <span>分钟</span>
            <input v-model.number="form.duration_minutes" type="number" min="1" max="1440" />
          </label>
          <label>
            <span>质量</span>
            <select v-model="form.quality">
              <option value="high">高</option>
              <option value="medium">中</option>
              <option value="low">低</option>
            </select>
          </label>
          <label class="full-span">
            <span>总结</span>
            <textarea v-model="form.summary" rows="4" />
          </label>
          <button class="primary-button full-span" type="submit">保存记录</button>
        </form>
      </section>
    </div>
  </AppShell>
</template>
