export interface QuestionListItem {
  id: number;
  question: string;
  question_type: string;
  answer: string;
  category_id?: number | null;
  category_name?: string | null;
  practice_count: number;
  correct_count: number;
  correct_rate: number;
  has_image: boolean;
  created_at: string;
}

export interface QuestionDetail {
  id: number;
  user_id: number;
  question: string;
  question_type: string;
  options?: string[] | null;
  answer: string;
  explanation?: string | null;
  tags?: string[] | null;
  image_url?: string | null;
  category_id?: number | null;
  category_name?: string | null;
  source_file?: string | null;
  practice_count: number;
  correct_count: number;
  correct_rate: number;
  created_at: string;
  updated_at: string;
}

export interface QuestionCreatePayload {
  question: string;
  question_type: string;
  options?: string[] | null;
  answer: string;
  explanation?: string | null;
  tags?: string[] | null;
  category_id?: number | null;
  image_url?: string | null;
}

export interface QuestionUpdatePayload {
  question?: string;
  question_type?: string;
  options?: string[] | null;
  answer?: string;
  explanation?: string | null;
  tags?: string[] | null;
  category_id?: number | null;
  image_url?: string | null;
}

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  page_size: number;
  items: T[];
}

export interface QuestionImageUploadResult {
  image_url: string;
  relative_path: string;
  question_id?: number | null;
}
