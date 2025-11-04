import http from './http';
import type {
  PaginatedResponse,
  QuestionCreatePayload,
  QuestionDetail,
  QuestionImageUploadResult,
  QuestionListItem,
  QuestionUpdatePayload,
} from '@/types/question';

interface QuestionListParams {
  page?: number;
  page_size?: number;
  keyword?: string;
  category_id?: number;
}

export async function fetchQuestions(
  params: QuestionListParams
): Promise<PaginatedResponse<QuestionListItem>> {
  const { data } = await http.get<PaginatedResponse<QuestionListItem>>(
    '/question/',
    { params }
  );
  return data;
}

export async function fetchQuestionDetail(
  id: number
): Promise<QuestionDetail> {
  const { data } = await http.get<QuestionDetail>(`/question/${id}`);
  return data;
}

export async function createQuestion(
  payload: QuestionCreatePayload
): Promise<QuestionDetail> {
  const { data } = await http.post<QuestionDetail>('/question/', payload);
  return data;
}

export async function updateQuestion(
  id: number,
  payload: QuestionUpdatePayload
): Promise<QuestionDetail> {
  const { data } = await http.put<QuestionDetail>(`/question/${id}`, payload);
  return data;
}

export async function deleteQuestion(id: number): Promise<void> {
  await http.delete(`/question/${id}`);
}

export async function deleteQuestionsBatch(ids: number[]): Promise<void> {
  await http.request({
    method: 'DELETE',
    url: '/question/batch',
    data: { ids }
  });
}

export async function uploadQuestionImage(
  file: File,
  questionId?: number
): Promise<QuestionImageUploadResult> {
  const formData = new FormData();
  formData.append('upload_file', file);
  if (typeof questionId === 'number') {
    formData.append('question_id', String(questionId));
  }
  const { data } = await http.post<QuestionImageUploadResult>(
    '/question/image',
    formData
  );
  return data;
}
