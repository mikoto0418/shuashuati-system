import http from './http';
import type {
  PracticeAnswerRequest,
  PracticeAnswerResponse,
  PracticeFinishResponse,
  PracticeHistoryItem,
  PracticeHistoryQuery,
  PracticeMode,
  PracticePreviewResponse,
  PracticeResultResponse,
  PracticeStartRequest,
  PracticeStartResponse
} from '@/types/practice';
import type { PaginatedResponse } from '@/types/question';

export async function previewPractice(
  payload: PracticeStartRequest
): Promise<PracticePreviewResponse> {
  const { data } = await http.post<PracticePreviewResponse>('/practice/preview', {
    category_ids: payload.category_ids ?? [],
    question_types: payload.question_types ?? [],
    mode: payload.mode
  });
  return data;
}

export async function startPractice(
  payload: PracticeStartRequest
): Promise<PracticeStartResponse> {
  const { data } = await http.post<PracticeStartResponse>('/practice/start', {
    category_ids: payload.category_ids ?? [],
    question_types: payload.question_types ?? [],
    mode: payload.mode,
    question_ids: payload.question_ids ?? undefined
  });
  return data;
}

export async function submitPracticeAnswer(
  sessionId: number,
  payload: PracticeAnswerRequest
): Promise<PracticeAnswerResponse> {
  const { data } = await http.post<PracticeAnswerResponse>(
    `/practice/${sessionId}/answer`,
    payload
  );
  return data;
}

export async function finishPractice(
  sessionId: number
): Promise<PracticeFinishResponse> {
  const { data } = await http.post<PracticeFinishResponse>(
    `/practice/${sessionId}/finish`
  );
  return data;
}

export const practiceModeOptions: Array<{ label: string; value: PracticeMode }> = [
  { label: '顺序练习', value: 'sequential' },
  { label: '随机练习', value: 'random' },
  { label: '错题练习', value: 'wrong' },
  { label: '收藏练习', value: 'favorite' }
];

export async function getPracticeResult(
  sessionId: number
): Promise<PracticeResultResponse> {
  const { data } = await http.get<PracticeResultResponse>(
    `/practice/${sessionId}/result`
  );
  return data;
}

export async function listPracticeHistory(
  params: PracticeHistoryQuery = {}
): Promise<PaginatedResponse<PracticeHistoryItem>> {
  const query = new URLSearchParams();
  if (params.page) query.set('page', String(params.page));
  if (params.page_size) query.set('page_size', String(params.page_size));
  if (params.mode) query.set('mode', params.mode);

  const queryString = query.toString();
  const url = queryString
    ? `/practice/history?${queryString}`
    : '/practice/history';
  const { data } = await http.get<PaginatedResponse<PracticeHistoryItem>>(url);
  return data;
}
