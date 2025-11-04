import http from './http';
import type {
  AuthTokenResponse,
  LoginPayload,
  RegisterPayload,
  UserResponse
} from '@/types/auth';

export async function register(payload: RegisterPayload): Promise<UserResponse> {
  const { data } = await http.post<UserResponse>('/auth/register', payload);
  return data;
}

export async function login(payload: LoginPayload): Promise<AuthTokenResponse> {
  const formData = new URLSearchParams();
  formData.append('username', payload.username);
  formData.append('password', payload.password);

  const { data } = await http.post<AuthTokenResponse>('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
  return data;
}

export async function getCurrentUser(): Promise<UserResponse> {
  const { data } = await http.get<UserResponse>('/auth/me');
  return data;
}
