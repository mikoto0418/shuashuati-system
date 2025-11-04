<template>
  <div class="auth-page">
    <n-card class="auth-card" title="登录刷刷题系统">
      <n-form ref="formRef" :model="form" :rules="rules">
        <n-form-item path="username" label="用户名或邮箱">
          <n-input
            v-model:value="form.username"
            placeholder="请输入用户名或邮箱"
            autofocus
            :disabled="loading"
            @keyup.enter="handleLogin"
          />
        </n-form-item>
        <n-form-item path="password" label="密码">
          <n-input
            v-model:value="form.password"
            placeholder="请输入密码"
            type="password"
            show-password-on="click"
            :disabled="loading"
            @keyup.enter="handleLogin"
          />
        </n-form-item>
        <n-space vertical size="large">
          <n-button type="primary" block :loading="loading" @click="handleLogin">
            登录
          </n-button>
          <n-button quaternary block :disabled="loading" @click="goRegister">
            立即注册
          </n-button>
        </n-space>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import {
  FormInst,
  FormRules,
  NButton,
  NCard,
  NForm,
  NFormItem,
  NInput,
  NSpace,
  useMessage
} from 'naive-ui';
import { useRoute, useRouter } from 'vue-router';
import { isAxiosError } from 'axios';
import { useAuthStore } from '@/stores/auth';

interface LoginForm {
  username: string;
  password: string;
}

const router = useRouter();
const route = useRoute();
const message = useMessage();
const authStore = useAuthStore();

const formRef = ref<FormInst | null>(null);
const loading = ref(false);

const form = reactive<LoginForm>({
  username: '',
  password: ''
});

if (typeof route.query.username === 'string') {
  form.username = route.query.username;
}

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: ['input', 'blur'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: ['input', 'blur'] }
  ]
};

const resolveErrorMessage = (error: unknown): string => {
  if (isAxiosError<{ detail?: string }>(error)) {
    return error.response?.data?.detail ?? '登录失败，请稍后重试';
  }
  return error instanceof Error ? error.message : '登录失败，请稍后重试';
};

const handleLogin = async () => {
  if (!formRef.value || loading.value) return;
  try {
    await formRef.value.validate();
  } catch {
    return;
  }

  loading.value = true;
  try {
    await authStore.login({
      username: form.username.trim(),
      password: form.password
    });
    message.success('登录成功');
    const redirect = (route.query.redirect as string) ?? '/';
    router.replace(redirect);
  } catch (error) {
    message.error(resolveErrorMessage(error));
  } finally {
    loading.value = false;
  }
};

const goRegister = () => {
  router.push({ name: 'Register', query: route.query });
};
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #e0f2f1 0%, #f1f5f9 100%);
}

.auth-card {
  width: 360px;
  box-shadow: 0 10px 40px rgba(15, 23, 42, 0.12);
  border-radius: 16px;
}
</style>
