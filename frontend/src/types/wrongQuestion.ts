export interface WrongQuestionItem {
  question_id: number;
  question: string;
  question_type: string;
  options: string[];
  answer: string;
  explanation?: string | null;
  wrong_count: number;
  last_wrong_time: string;
  category_id?: number | null;
  category_name?: string | null;
}
