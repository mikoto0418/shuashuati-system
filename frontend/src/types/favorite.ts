export interface FavoriteItem {
  question_id: number;
  question: string;
  question_type: string;
  options: string[];
  answer: string;
  explanation?: string | null;
  created_at: string;
  category_id?: number | null;
  category_name?: string | null;
}
