export type PracticeMode = 'sequential' | 'random' | 'wrong' | 'favorite';

export interface PracticeStartRequest {
  category_ids?: number[];
  question_types?: string[];
  mode: PracticeMode;
  question_ids?: number[];
}

export interface PracticeQuestion {
  id: number;
  question: string;
  question_type: string;
  options: string[];
  image_url?: string | null;
}

export interface PracticeStartResponse {
  session_id: number;
  total_count: number;
  mode: PracticeMode;
  start_time: string;
  questions: PracticeQuestion[];
}

export interface PracticePreviewResponse {
  total_count: number;
  questions: PracticeQuestion[];
}

export interface PracticeAnswerRequest {
  question_id: number;
  user_answer?: string | null;
}

export interface PracticeAnswerResponse {
  question_id: number;
  user_answer?: string | null;
  correct_answer?: string | null;
  is_correct?: boolean | null;
  explanation?: string | null;
}

export interface PracticeFinishResponse {
  session_id: number;
  total_count: number;
  correct_count: number;
  correct_rate: number;
  duration_seconds: number;
  end_time: string;
}

export interface PracticeAnswerRecord {
  question_id: number;
  question: string;
  question_type: string;
  user_answer: string;
  correct_answer?: string | null;
  is_correct?: boolean | null;
  explanation?: string | null;
}

export interface PracticeAnswerDetail {
  question_id: number;
  question: string;
  question_type: string;
  options?: string[] | null;
  user_answer?: string | null;
  correct_answer: string;
  is_correct: boolean;
  explanation?: string | null;
}

export interface PracticeResultResponse {
  session_id: number;
  mode: PracticeMode;
  total_count: number;
  correct_count: number;
  correct_rate: number;
  duration_seconds: number;
  start_time: string;
  end_time: string;
  answers: PracticeAnswerDetail[];
}

export interface PracticeHistoryItem {
  session_id: number;
  mode: PracticeMode;
  total_count: number;
  correct_count: number;
  correct_rate: number;
  duration_seconds?: number | null;
  start_time: string;
  end_time?: string | null;
}

export interface PracticeHistoryQuery {
  page?: number;
  page_size?: number;
  mode?: PracticeMode;
}
