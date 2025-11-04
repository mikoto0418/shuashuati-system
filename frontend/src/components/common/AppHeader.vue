<template>
  <n-layout-header bordered class="app-header">
    <div class="app-header__left">
      <n-space align="center" size="small">
        <n-button quaternary circle @click="toggleSidebar">
          <template #icon>
            <n-icon size="18">
              <MenuOutline />
            </n-icon>
          </template>
        </n-button>
        <h1 class="app-title">刷刷题系统</h1>
      </n-space>
    </div>
    <div class="app-header__right">
      <n-space align="center" size="large">
        <n-button quaternary circle @click="toggleTheme">
          <template #icon>
            <n-icon size="18">
              <component :is="themeIcon" />
            </n-icon>
          </template>
        </n-button>
        <template v-if="isAuthenticated">
          <n-space align="center" size="small">
            <n-avatar round size="medium">
              {{ avatarInitial }}
            </n-avatar>
            <div class="user-meta">
              <span class="welcome-text">欢迎，{{ displayName }}</span>
              <span v-if="userEmail" class="user-email">{{ userEmail }}</span>
            </div>
          </n-space>
          <n-button tertiary size="small" :loading="logoutLoading" @click="handleLogout">
            退出登录
          </n-button>
        </template>
        <template v-else>
          <span class="welcome-text">欢迎访问刷刷题系统</span>
        </template>
      </n-space>
    </div>
  </n-layout-header>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { MenuOutline, MoonOutline, SunnyOutline } from '@vicons/ionicons5';
import { useMessage } from 'naive-ui';
import { useAuthStore } from '@/stores/auth';
import { useThemeStore } from '@/stores/theme';

const emit = defineEmits<{
  (event: 'toggle-sidebar'): void;
}>();

const authStore = useAuthStore();
const themeStore = useThemeStore();
const message = useMessage();
const logoutLoading = ref(false);

const isAuthenticated = computed(() => Boolean(authStore.token));
const displayName = computed(
  () => authStore.user?.nickname ?? authStore.user?.username ?? '访客'
);
const userEmail = computed(() => authStore.user?.email ?? '');
const avatarInitial = computed(() => displayName.value.slice(0, 1).toUpperCase());
const isDark = computed(() => themeStore.theme === 'dark');
const themeIcon = computed(() => (isDark.value ? SunnyOutline : MoonOutline));

const toggleSidebar = () => {
  emit('toggle-sidebar');
};

const toggleTheme = () => {
  themeStore.toggleTheme();
};

const handleLogout = async () => {
  if (logoutLoading.value) return;
  logoutLoading.value = true;
  try {
    await authStore.logout();
    message.success('已退出登录');
  } finally {
    logoutLoading.value = false;
  }
};
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: var(--color-surface);
  backdrop-filter: blur(12px);
  box-shadow: var(--shadow-header);
  border-bottom: 1px solid rgba(31, 41, 51, 0.06);
}

.app-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  letter-spacing: 0.02em;
}

.welcome-text {
  font-size: 14px;
  color: var(--color-text-primary);
}

.user-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-email {
  font-size: 12px;
  color: var(--color-text-secondary);
}
</style>
