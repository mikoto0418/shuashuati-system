import http from './http';
import type {
  FileImportRequest,
  FileImportResult,
  FilePreviewResponse,
} from '@/types/file';

export async function uploadPreview(
  file: File,
  mode: 'basic' | 'ai' | 'mixed'
): Promise<FilePreviewResponse> {
  const formData = new FormData();
  formData.append('upload_file', file);
  formData.append('mode', mode);

  const { data } = await http.post<FilePreviewResponse>(
    '/file/upload/preview',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return data;
}

export async function confirmImport(
  payload: FileImportRequest
): Promise<FileImportResult> {
  const { data } = await http.post<FileImportResult>(
    '/file/upload/confirm',
    payload
  );
  return data;
}
