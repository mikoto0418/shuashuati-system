import http from './http';
import type { FavoriteItem } from '@/types/favorite';

export async function fetchFavorites(): Promise<FavoriteItem[]> {
  const { data } = await http.get<FavoriteItem[]>('/favorite/');
  return data;
}

export async function addFavorite(questionId: number): Promise<void> {
  await http.post('/favorite/', { question_id: questionId });
}

export async function removeFavorite(questionId: number): Promise<void> {
  await http.delete(`/favorite/${questionId}`);
}
