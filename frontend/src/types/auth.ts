export interface ApiUser {
  id: number;
  username: string;
  email: string;
  nickname?: string | null;
  avatar_url?: string | null;
  is_active: boolean;
  created_at: string;
  is_admin: boolean;
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  nickname?: string | null;
  avatarUrl?: string | null;
  isAdmin?: boolean;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  nickname?: string | null;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: ApiUser;
}

export type UserResponse = ApiUser;
