<script setup lang="ts">
import { LockKeyhole, UserRound } from "lucide-vue-next";
import { ref } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();
const username = ref("admin");
const password = ref("change-me-now");
const error = ref("");

const submit = async () => {
  error.value = "";
  try {
    await auth.login(username.value, password.value);
    await router.push("/");
  } catch {
    error.value = "账号或密码不正确";
  }
};
</script>

<template>
  <main class="login-page">
    <section class="login-card">
      <div>
        <div class="login-kicker">私人备考系统</div>
        <h1>11408 考研驾驶舱</h1>
        <p>每日规划、学习计时、记录沉淀和二战目标差距，统一放在一个安静的工作台里。</p>
      </div>

      <form class="login-form" @submit.prevent="submit">
        <label>
          <span>用户名</span>
          <div class="input-wrap">
            <UserRound :size="18" />
            <input v-model="username" autocomplete="username" />
          </div>
        </label>
        <label>
          <span>密码</span>
          <div class="input-wrap">
            <LockKeyhole :size="18" />
            <input v-model="password" type="password" autocomplete="current-password" />
          </div>
        </label>
        <p v-if="error" class="form-error">{{ error }}</p>
        <button class="primary-button" type="submit" :disabled="auth.loading">
          {{ auth.loading ? "登录中" : "进入仪表盘" }}
        </button>
      </form>
    </section>
  </main>
</template>
