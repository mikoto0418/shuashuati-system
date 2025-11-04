import { createApp } from 'vue';
import naive from 'naive-ui';
import App from './App.vue';
import router from './router';
import pinia from './stores';
import './assets/styles/global.css';
import { useAuthStore } from '@/stores/auth';
import { useThemeStore } from '@/stores/theme';

async function bootstrap() {
  const app = createApp(App);

  app.use(pinia);
  app.use(router);
  app.use(naive);

  const authStore = useAuthStore();
  const themeStore = useThemeStore();
  themeStore.initialize();
  await authStore.initialize();

  await router.isReady();
  app.mount('#app');
}

bootstrap();
