import http from './http';
import type {
  ParseTaskCreateResponse,
  ParseTaskListResponse,
  ParseTaskResult,
  ParseTaskStatus
} from '@/types/file';

export async function createParseTask(
  file: File,
  mode: 'basic' | 'ai' | 'mixed'
): Promise<ParseTaskCreateResponse> {
  const formData = new FormData();
  formData.append('upload_file', file);
  formData.append('mode', mode);

  const { data } = await http.post<ParseTaskCreateResponse>('/parse-task', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  return data;
}

export async function getParseTaskStatus(taskId: number): Promise<ParseTaskStatus> {
  const { data } = await http.get<ParseTaskStatus>(`/parse-task/${taskId}`);
  return data;
}

export async function getParseTaskResult(taskId: number): Promise<ParseTaskResult> {
  const { data } = await http.get<ParseTaskResult>(`/parse-task/${taskId}/result`);
  return data;
}

export async function listParseTasks(): Promise<ParseTaskListResponse> {
  const { data } = await http.get<ParseTaskListResponse>('/parse-task');
  return data;
}
