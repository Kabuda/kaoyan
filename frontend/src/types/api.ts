export type Subject = "politics" | "english" | "math" | "408" | string;

export interface User {
  id: number;
  username: string;
  created_at: string;
  updated_at: string;
}

export interface ExamProfile {
  id: number;
  user_id: number;
  first_politics_score: number;
  first_english_score: number;
  first_math_score: number;
  first_408_score: number;
  target_politics_score: number;
  target_english_score: number;
  target_math_score: number;
  target_408_score: number;
  target_total_score: number;
  exam_date: string | null;
  daily_target_minutes: number;
  weak_points: string;
  created_at: string;
  updated_at: string;
}

export interface StudyTask {
  id: number;
  user_id: number;
  plan_date: string;
  subject: Subject;
  module: string;
  title: string;
  task_type: string;
  estimated_minutes: number;
  actual_minutes: number;
  priority: number;
  status: "not_started" | "in_progress" | "completed" | "skipped" | "postponed" | string;
  note: string;
  created_at: string;
  updated_at: string;
}

export interface TimerSession {
  id: number;
  user_id: number;
  task_id: number;
  status: "running" | "paused" | "finished" | string;
  started_at: string;
  paused_at: string | null;
  accumulated_seconds: number;
  ended_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface StudyRecord {
  id: number;
  user_id: number;
  task_id: number | null;
  subject: Subject;
  module: string;
  task_type: string;
  title: string;
  started_at: string;
  ended_at: string;
  duration_minutes: number;
  summary: string;
  blockers: string;
  quality: string;
  is_manual: boolean;
  created_at: string;
  updated_at: string;
}

export interface TrendPoint {
  date: string;
  minutes: number;
}

export interface DistributionItem {
  name: string;
  minutes: number;
}

export interface DashboardStats {
  today_minutes: number;
  today_target_minutes: number;
  today_completion_rate: number;
  week_minutes: number;
  month_minutes: number;
  task_completion_rate: number;
  english_scheduled_today: boolean;
  math_scheduled_today: boolean;
  computer_scheduled_today: boolean;
  english_streak_days: number;
  math_week_ratio: number;
  computer_week_ratio: number;
  recent_7_days: TrendPoint[];
  subject_distribution: DistributionItem[];
}

export interface WeeklyReview {
  id: number;
  user_id: number;
  week_start: string;
  summary: string;
  biggest_problem: string;
  delay_reason: string;
  english_review: string;
  math_review: string;
  computer_review: string;
  politics_review: string;
  next_week_adjustment: string;
  created_at: string;
  updated_at: string;
}
