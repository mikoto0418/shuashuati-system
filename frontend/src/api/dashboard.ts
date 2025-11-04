import http from './http';
import type { DashboardStats } from '@/types/dashboard';

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const { data } = await http.get<DashboardStats>('/dashboard/overview');
  return data;
}
