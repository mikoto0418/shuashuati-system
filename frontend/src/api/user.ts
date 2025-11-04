import http from './http';
import type { ApiUser } from '@/types/auth';
import type {
  AIModelListRequest,
  AIModelListResponse,
  UserAISettingsPayload,
  UserPasswordPayload,
  UserPreferencesPayload,
  UserProfilePayload,
  UserSettingsResponse
} from '@/types/user';

interface MessageResponse {
  message: string;
}

export async function fetchUserSettings(): Promise<UserSettingsResponse> {
  const { data } = await http.get<UserSettingsResponse>('/user/settings');
  return data;
}

export async function updateUserPreferences(
  payload: UserPreferencesPayload
): Promise<UserSettingsResponse> {
  const { data } = await http.put<UserSettingsResponse>('/user/settings', payload);
  return data;
}

export async function updateUserAISettings(
  payload: UserAISettingsPayload
): Promise<UserSettingsResponse> {
  const { data } = await http.put<UserSettingsResponse>('/user/settings/ai', payload);
  return data;
}

export async function fetchAIModels(
  payload: AIModelListRequest
): Promise<AIModelListResponse> {
  const { data } = await http.post<AIModelListResponse>(
    '/user/settings/models',
    payload
  );
  return data;
}

export async function updateUserProfile(
  payload: UserProfilePayload
): Promise<ApiUser> {
  const { data } = await http.put<ApiUser>('/user/profile', payload);
  return data;
}

export async function changeUserPassword(
  payload: UserPasswordPayload
): Promise<MessageResponse> {
  const { data } = await http.put<MessageResponse>('/user/password', payload);
  return data;
}
