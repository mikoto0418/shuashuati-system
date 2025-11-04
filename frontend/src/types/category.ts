export interface CategoryItem {
  id: number;
  name: string;
  description?: string | null;
  parent_id?: number | null;
  question_count: number;
  created_at: string;
  updated_at: string;
}

export interface CreateCategoryPayload {
  name: string;
  description?: string | null;
  parent_id?: number | null;
}

export interface UpdateCategoryPayload {
  name?: string;
  description?: string | null;
  parent_id?: number | null;
}
