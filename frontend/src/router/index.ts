import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import MainLayout from '@/components/common/MainLayout.vue';
import { useAuthStore } from '@/stores/auth';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'DashboardHome',
        component: () => import('@/views/dashboard/DashboardHome.vue')
      },
      {
        path: 'questions',
        redirect: { name: 'QuestionManage' }
      },
      {
        path: 'questions/manage',
        name: 'QuestionManage',
        component: () => import('@/views/question/QuestionManageView.vue')
      },
      {
        path: 'questions/categories',
        name: 'CategoryManage',
        component: () => import('@/views/question/CategoryManageView.vue')
      },
      {
        path: 'questions/import',
        name: 'QuestionImport',
        component: () => import('@/views/question/QuestionImportView.vue')
      },
      {
        path: 'questions/new',
        name: 'QuestionCreate',
        component: () => import('@/views/question/QuestionEditorView.vue')
      },
      {
        path: 'questions/:id/edit',
        name: 'QuestionEdit',
        component: () => import('@/views/question/QuestionEditorView.vue')
      },
      {
        path: 'practice',
        name: 'PracticeCenter',
        component: () => import('@/views/practice/PracticeCenterView.vue')
      },
      {
        path: 'practice/wrong-book',
        name: 'PracticeWrongBook',
        component: () => import('@/views/practice/WrongBookView.vue')
      },
      {
        path: 'settings',
        name: 'SettingsHome',
        component: () => import('@/views/settings/SettingsHome.vue')
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach(async (to) => {
  const authStore = useAuthStore();
  if (!authStore.isInitialized) {
    await authStore.initialize();
  }

  const isAuthenticated = Boolean(authStore.token);
  if (to.meta.requiresAuth && !isAuthenticated) {
    return {
      name: 'Login',
      query: { redirect: to.fullPath }
    };
  }

  if (to.meta.guestOnly && isAuthenticated) {
    return { name: 'DashboardHome' };
  }

  return true;
});

export default router;
