import http from './http';

export async function cleanupUploads(retentionHours = 6): Promise<string> {
  const { data } = await http.post<{ message: string }>(
    '/admin/uploads/cleanup',
    undefined,
    { params: { retention_hours: retentionHours } }
  );
  return data.message;
}
