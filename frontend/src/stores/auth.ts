import { defineStore } from "pinia";

import { api } from "@/api/client";
import type { User } from "@/types/api";

interface AuthState {
  token: string;
  user: User | null;
  loading: boolean;
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    token: localStorage.getItem("kaoyan_token") || "",
    user: null,
    loading: false
  }),
  actions: {
    async login(username: string, password: string) {
      this.loading = true;
      try {
        const { data } = await api.post<{ access_token: string }>("/api/auth/login", {
          username,
          password
        });
        this.token = data.access_token;
        localStorage.setItem("kaoyan_token", data.access_token);
        await this.fetchMe();
      } finally {
        this.loading = false;
      }
    },
    async fetchMe() {
      const { data } = await api.get<User>("/api/auth/me");
      this.user = data;
    },
    logout() {
      this.token = "";
      this.user = null;
      localStorage.removeItem("kaoyan_token");
    }
  }
});
