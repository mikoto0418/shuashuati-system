<template>
  <div class="auth-page">
    <n-card class="auth-card" title="注册刷刷题系统">
      <n-form ref="formRef" :model="form" :rules="rules">
        <n-form-item path="username" label="用户名">
          <n-input
            v-model:value="form.username"
            placeholder="请输入用户名"
            :disabled="loading"
            @keyup.enter="handleRegister"
          />
        </n-form-item>
        <n-form-item path="email" label="邮箱">
          <n-input
            v-model:value="form.email"
            placeholder="请输入邮箱"
            type="text"
            :disabled="loading"
            @keyup.enter="handleRegister"
          />
        </n-form-item>
        <n-form-item path="password" label="密码">
          <n-input
            v-model:value="form.password"
            placeholder="请输入密码"
            type="password"
            show-password-on="click"
            :disabled="loading"
            @keyup.enter="handleRegister"
          />
        </n-form-item>
        <n-space vertical size="large">
          <n-button type="primary" block :loading="loading" @click="handleRegister">
            注册
          </n-button>
          <n-button quaternary block :disabled="loading" @click="goLogin">
            已有账号？前往登录
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
import { useRouter } from 'vue-router';
import { isAxiosError } from 'axios';
import { useAuthStore } from '@/stores/auth';

interface RegisterForm {
  username: string;
  email: string;
  password: string;
}

const router = useRouter();
const message = useMessage();
const authStore = useAuthStore();

const formRef = ref<FormInst | null>(null);
const loading = ref(false);

const form = reactive<RegisterForm>({
  username: '',
  email: '',
  password: ''
});

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: ['input', 'blur'] },
    {
      min: 3,
      max: 50,
      message: '用户名长度需在 3-50 个字符之间',
      trigger: ['input', 'blur']
    }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: ['input', 'blur'] },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: ['input', 'blur'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: ['input', 'blur'] },
    {
      min: 8,
      max: 50,
      message: '密码长度需在 8-50 个字符之间',
      trigger: ['input', 'blur']
    }
  ]
};

const resolveErrorMessage = (error: unknown): string => {
  if (isAxiosError<{ detail?: string }>(error)) {
    return error.response?.data?.detail ?? '注册失败，请稍后重试';
  }
  return error instanceof Error ? error.message : '注册失败，请稍后重试';
};

const handleRegister = async () => {
  if (!formRef.value || loading.value) return;
  try {
    await formRef.value.validate();
  } catch {
    return;
  }

  loading.value = true;
  try {
    await authStore.register({
      username: form.username.trim(),
      email: form.email.trim(),
      password: form.password
    });
    message.success('注册成功，请登录');
    router.push({
      name: 'Login',
      query: { username: form.username }
    });
  } catch (error) {
    message.error(resolveErrorMessage(error));
  } finally {
    loading.value = false;
  }
};

const goLogin = () => {
  router.push({ name: 'Login' });
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
  width: 400px;
  box-shadow: 0 10px 40px rgba(15, 23, 42, 0.12);
  border-radius: 16px;
}
</style>
