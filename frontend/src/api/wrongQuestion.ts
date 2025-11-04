import http from './http';
import type { WrongQuestionItem } from '@/types/wrongQuestion';

export async function fetchWrongQuestions(): Promise<WrongQuestionItem[]> {
  const { data } = await http.get<WrongQuestionItem[]>('/wrong-question/');
  return data;
}

export async function removeWrongQuestion(questionId: number): Promise<void> {
  await http.delete(`/wrong-question/${questionId}`);
}
