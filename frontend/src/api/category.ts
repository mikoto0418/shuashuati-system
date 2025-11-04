import http from './http';
import type {
  CategoryItem,
  CreateCategoryPayload,
  UpdateCategoryPayload,
} from '@/types/category';

export async function fetchCategories(): Promise<CategoryItem[]> {
  const { data } = await http.get<CategoryItem[]>('/category/');
  return data;
}

export async function createCategory(
  payload: CreateCategoryPayload
): Promise<CategoryItem> {
  const { data } = await http.post<CategoryItem>('/category/', payload);
  return data;
}

export async function updateCategory(
  id: number,
  payload: UpdateCategoryPayload
): Promise<CategoryItem> {
  const { data } = await http.put<CategoryItem>(`/category/${id}`, payload);
  return data;
}

export async function deleteCategory(id: number): Promise<void> {
  await http.delete(`/category/${id}`);
}
