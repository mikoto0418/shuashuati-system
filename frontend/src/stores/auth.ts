import { defineStore } from 'pinia';
import {
  login as loginApi,
  register as registerApi,
  getCurrentUser
} from '@/api/auth';
import type {
  AuthTokenResponse,
  LoginPayload,
  RegisterPayload,
  UserProfile,
  ApiUser
} from '@/types/auth';

interface AuthState {
  token: string | null;
  user: UserProfile | null;
  isInitialized: boolean;
}

interface PersistedState {
  token: string | null;
  user: UserProfile | null;
}

const STORAGE_KEY = 'shuashuati-auth';

function mapUser(apiUser: ApiUser): UserProfile {
  return {
    id: apiUser.id,
    username: apiUser.username,
    email: apiUser.email,
    nickname: apiUser.nickname ?? undefined,
    avatarUrl: apiUser.avatar_url ?? undefined,
    isAdmin: apiUser.is_admin ?? false
  };
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: null,
    user: null,
    isInitialized: false
  }),
  actions: {
    setToken(token: string | null) {
      this.token = token;
      this.persist();
    },
    setUser(user: UserProfile | null) {
      this.user = user;
      this.persist();
    },
    persist() {
      const state: PersistedState = {
        token: this.token,
        user: this.user
      };
      if (state.token) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      } else {
        localStorage.removeItem(STORAGE_KEY);
      }
    },
    loadFromStorage(): PersistedState | null {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      try {
        const parsed = JSON.parse(raw) as PersistedState;
        return parsed;
      } catch {
        return null;
      }
    },
    async initialize(): Promise<void> {
      if (this.isInitialized) {
        return;
      }

      const persisted = this.loadFromStorage();
      if (persisted?.token) {
        this.token = persisted.token;
        this.user = persisted.user ?? null;
        try {
          await this.fetchCurrentUser();
        } catch {
          await this.logout({ redirect: false });
        }
      } else {
        this.token = null;
        this.user = null;
      }

      this.isInitialized = true;
    },
    async login(payload: LoginPayload): Promise<UserProfile> {
      const response: AuthTokenResponse = await loginApi(payload);
      const profile = mapUser(response.user);
      this.setToken(response.access_token);
      this.setUser(profile);
      return profile;
    },
    async register(payload: RegisterPayload): Promise<UserProfile> {
      const response = await registerApi(payload);
      return mapUser(response);
    },
    async fetchCurrentUser(): Promise<UserProfile> {
      const response = await getCurrentUser();
      const profile = mapUser(response);
      this.setUser(profile);
      return profile;
    },
    async logout(options?: { redirect?: boolean }) {
      this.token = null;
      this.user = null;
      this.persist();
      if (!this.isInitialized) {
        this.isInitialized = true;
      }

      if (options?.redirect === false) {
        return;
      }

      const { default: router } = await import('@/router');
      const currentRoute = router.currentRoute.value;
      if (currentRoute.name !== 'Login') {
        router.push({
          name: 'Login',
          query:
            currentRoute.meta.requiresAuth && currentRoute.fullPath
              ? { redirect: currentRoute.fullPath }
              : undefined
        });
      }
    }
  }
});
