import { defineStore } from 'pinia';

export type ThemeMode = 'light' | 'dark';

const STORAGE_KEY = 'shuashuati-theme';

function applyTheme(theme: ThemeMode) {
  document.documentElement.dataset.theme = theme;
}

function resolveInitialTheme(): ThemeMode {
  const stored = localStorage.getItem(STORAGE_KEY) as ThemeMode | null;
  if (stored === 'light' || stored === 'dark') {
    return stored;
  }
  if (window.matchMedia?.('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  return 'light';
}

export const useThemeStore = defineStore('theme', {
  state: () => ({
    theme: 'light' as ThemeMode,
    initialized: false,
  }),
  actions: {
    initialize() {
      if (this.initialized) return;
      this.theme = resolveInitialTheme();
      applyTheme(this.theme);
      this.initialized = true;
    },
    setTheme(theme: ThemeMode) {
      this.theme = theme;
      applyTheme(theme);
      localStorage.setItem(STORAGE_KEY, theme);
    },
    toggleTheme() {
      this.setTheme(this.theme === 'dark' ? 'light' : 'dark');
    },
  },
});
