import { defineStore } from "pinia";

import { api } from "@/api/client";
import type {
  DashboardStats,
  ExamProfile,
  StudyRecord,
  StudyTask,
  TimerSession,
  WeeklyReview
} from "@/types/api";

interface StudyState {
  profile: ExamProfile | null;
  stats: DashboardStats | null;
  tasks: StudyTask[];
  timer: TimerSession | null;
  records: StudyRecord[];
  reviews: WeeklyReview[];
  loading: boolean;
}

export const todayISO = () => new Date().toISOString().slice(0, 10);

export const useStudyStore = defineStore("study", {
  state: (): StudyState => ({
    profile: null,
    stats: null,
    tasks: [],
    timer: null,
    records: [],
    reviews: [],
    loading: false
  }),
  getters: {
    currentTask: (state) => state.tasks.find((task) => task.id === state.timer?.task_id) || null,
    completedTasks: (state) => state.tasks.filter((task) => task.status === "completed"),
    plannedMinutes: (state) => state.tasks.reduce((sum, task) => sum + task.estimated_minutes, 0),
    actualTaskMinutes: (state) => state.tasks.reduce((sum, task) => sum + task.actual_minutes, 0)
  },
  actions: {
    async bootstrap(date = todayISO()) {
      this.loading = true;
      try {
        await Promise.all([
          this.loadProfile(),
          this.loadStats(),
          this.loadTasks(date),
          this.loadTimer(),
          this.loadRecords(),
          this.loadReviews()
        ]);
      } finally {
        this.loading = false;
      }
    },
    async loadProfile() {
      const { data } = await api.get<ExamProfile>("/api/profile");
      this.profile = data;
    },
    async updateProfile(payload: Partial<ExamProfile>) {
      const { data } = await api.put<ExamProfile>("/api/profile", payload);
      this.profile = data;
      await this.loadStats();
    },
    async loadStats() {
      const { data } = await api.get<DashboardStats>("/api/stats/dashboard");
      this.stats = data;
    },
    async loadTasks(date = todayISO()) {
      const { data } = await api.get<StudyTask[]>("/api/tasks", { params: { date } });
      this.tasks = data;
    },
    async createTask(payload: Partial<StudyTask>) {
      await api.post("/api/tasks", payload);
      await this.loadTasks(payload.plan_date || todayISO());
      await this.loadStats();
    },
    async updateTask(id: number, payload: Partial<StudyTask>) {
      await api.put(`/api/tasks/${id}`, payload);
      await this.loadTasks(payload.plan_date || todayISO());
      await this.loadStats();
    },
    async completeTask(id: number) {
      await api.post(`/api/tasks/${id}/complete`);
      await this.loadTasks();
      await this.loadStats();
    },
    async skipTask(id: number) {
      await api.post(`/api/tasks/${id}/skip`);
      await this.loadTasks();
      await this.loadStats();
    },
    async generateDailyTemplate(date = todayISO()) {
      await api.post("/api/tasks/generate-daily-template", { plan_date: date });
      await this.loadTasks(date);
      await this.loadStats();
    },
    async loadTimer() {
      const { data } = await api.get<TimerSession | null>("/api/timer/current");
      this.timer = data;
    },
    async startTimer(taskId: number) {
      const { data } = await api.post<TimerSession>("/api/timer/start", { task_id: taskId });
      this.timer = data;
      await this.loadTasks();
    },
    async pauseTimer() {
      const { data } = await api.post<TimerSession>("/api/timer/pause");
      this.timer = data;
    },
    async resumeTimer() {
      const { data } = await api.post<TimerSession>("/api/timer/resume");
      this.timer = data;
    },
    async finishTimer(summary: string, blockers = "", quality = "medium") {
      await api.post("/api/timer/finish", { summary, blockers, quality });
      this.timer = null;
      await Promise.all([this.loadTasks(), this.loadStats(), this.loadRecords()]);
    },
    async loadRecords() {
      const { data } = await api.get<StudyRecord[]>("/api/records");
      this.records = data;
    },
    async createRecord(payload: Partial<StudyRecord>) {
      await api.post("/api/records", payload);
      await Promise.all([this.loadRecords(), this.loadStats()]);
    },
    async loadReviews() {
      const { data } = await api.get<WeeklyReview[]>("/api/reviews/weekly");
      this.reviews = data;
    },
    async createReview(payload: Partial<WeeklyReview>) {
      await api.post("/api/reviews/weekly", payload);
      await this.loadReviews();
    }
  }
});
