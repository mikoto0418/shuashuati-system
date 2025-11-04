<template>
  <div class="page">
    <n-page-header title="系统设置" />

    <n-grid :cols="1" :y-gap="24" class="settings-grid">
      <n-gi>
        <n-card title="练习偏好" :loading="loadingSettings">
          <n-form
            ref="preferenceFormRef"
            label-placement="top"
            :model="preferenceForm"
            :rules="preferenceRules"
          >
            <n-grid :cols="2" :x-gap="24">
              <n-gi>
                <n-form-item label="练习模式" path="practice_mode">
                  <n-select
                    v-model:value="preferenceForm.practice_mode"
                    :options="practiceModeOptions"
                    placeholder="请选择默认练习模式"
                  />
                </n-form-item>
              </n-gi>
              <n-gi>
                <n-form-item label="答案显示方式" path="answer_display_mode">
                  <n-select
                    v-model:value="preferenceForm.answer_display_mode"
                    :options="answerDisplayOptions"
                    placeholder="请选择答案显示方式"
                  />
                </n-form-item>
              </n-gi>
            </n-grid>

            <n-space justify="end">
              <n-button type="primary" :loading="savingPreferences" @click="handleSavePreferences">
                保存练习偏好
              </n-button>
            </n-space>
          </n-form>
        </n-card>
      </n-gi>

      <n-gi>
        <n-card title="AI 配置" :loading="loadingSettings">
          <n-form
            ref="aiFormRef"
            label-placement="top"
            :model="aiForm"
            :rules="aiRules"
          >
            <n-grid :cols="2" :x-gap="24">
              <n-gi>
                <n-form-item label="服务提供商" path="ai_provider">
                  <n-select
                    v-model:value="aiForm.ai_provider"
                    :options="aiProviderOptions"
                    placeholder="请选择提供商"
                  />
                </n-form-item>
              </n-gi>
              <n-gi>
                <n-form-item label="模型名称" path="ai_model">
                  <n-space align="center" wrap>
                    <n-select
                      v-model:value="aiForm.ai_model"
                      :options="modelSelectOptions"
                      :loading="fetchingModels"
                      :disabled="!canFetchModels"
                      filterable
                      clearable
                      :allow-create="true"
                      placeholder="例如：gpt-4.1, qwen-plus"
                      style="min-width: 220px;"
                    />
                    <n-button
                      tertiary
                      type="primary"
                      :loading="fetchingModels"
                      :disabled="!canFetchModels"
                      @click="handleFetchModels"
                    >
                      获取模型列表
                    </n-button>
                  </n-space>
                  <template #feedback>
                    <n-text depth="3">
                      若未列出模型，可直接输入自定义名称。
                    </n-text>
                  </template>
                </n-form-item>
              </n-gi>
            </n-grid>

            <n-form-item label="API Key" path="api_key_input">
              <n-input
                v-model:value="aiForm.api_key_input"
                type="password"
                show-password-on="click"
                placeholder="输入新 Key 将覆盖已有配置"
              />
              <template #feedback>
                <n-space align="center">
                  <n-text depth="3">
                    {{ hasApiKey ? '已配置密钥，输入新值可覆盖。' : '当前未配置密钥。' }}
                  </n-text>
                  <n-button
                    v-if="hasApiKey"
                    text
                    type="warning"
                    @click="handleClearApiKey"
                    :loading="clearingApiKey"
                  >
                    清除密钥
                  </n-button>
                </n-space>
              </template>
            </n-form-item>

            <n-space justify="end">
              <n-button type="primary" :loading="savingAI" @click="handleSaveAI">
                保存 AI 配置
              </n-button>
            </n-space>
          </n-form>
        </n-card>
      </n-gi>

      <n-gi>
        <n-card title="个人资料">
          <n-form
            ref="profileFormRef"
            label-placement="top"
            :model="profileForm"
            :rules="profileRules"
          >
            <n-grid :cols="2" :x-gap="24">
              <n-gi>
                <n-form-item label="昵称" path="nickname">
                  <n-input
                    v-model:value="profileForm.nickname"
                    placeholder="请输入昵称"
                  />
                </n-form-item>
              </n-gi>
              <n-gi>
                <n-form-item label="头像地址" path="avatar_url">
                  <n-input
                    v-model:value="profileForm.avatar_url"
                    placeholder="可填写图片链接"
                  />
                </n-form-item>
              </n-gi>
            </n-grid>

            <n-space justify="end">
              <n-button type="primary" :loading="savingProfile" @click="handleSaveProfile">
                更新资料
              </n-button>
            </n-space>
          </n-form>
        </n-card>
      </n-gi>

      <n-gi>
        <n-card title="修改密码">
          <n-form
            ref="passwordFormRef"
            label-placement="top"
            :model="passwordForm"
            :rules="passwordRules"
          >
            <n-grid :cols="2" :x-gap="24">
              <n-gi>
                <n-form-item label="原密码" path="old_password">
                  <n-input
                    v-model:value="passwordForm.old_password"
                    type="password"
                    show-password-on="click"
                    placeholder="请输入当前密码"
                  />
                </n-form-item>
              </n-gi>
              <n-gi>
                <n-form-item label="新密码" path="new_password">
                  <n-input
                    v-model:value="passwordForm.new_password"
                    type="password"
                    show-password-on="click"
                    placeholder="至少 8 个字符"
                  />
                </n-form-item>
              </n-gi>
            </n-grid>

            <n-form-item label="确认新密码" path="confirm_password">
              <n-input
                v-model:value="passwordForm.confirm_password"
                type="password"
                show-password-on="click"
                placeholder="请再次输入新密码"
              />
            </n-form-item>

            <n-space justify="end">
              <n-button type="primary" :loading="changingPassword" @click="handleChangePassword">
                修改密码
              </n-button>
            </n-space>
          </n-form>
        </n-card>
      </n-gi>
    </n-grid>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch, onMounted } from 'vue';
import {
  NButton,
  NCard,
  NForm,
  NFormItem,
  NGrid,
  NGi,
  NInput,
  NPageHeader,
  NSelect,
  NSpace,
  NText,
  type FormInst,
  type FormRules,
  useMessage
} from 'naive-ui';
import { useAuthStore } from '@/stores/auth';
import {
  changeUserPassword,
  fetchAIModels,
  fetchUserSettings,
  updateUserAISettings,
  updateUserPreferences,
  updateUserProfile
} from '@/api/user';
import { answerDisplayOptions, aiProviderOptions } from '@/types/user';
import { practiceModeOptions } from '@/api/practice';
import type {
  UserAISettingsPayload,
  UserPasswordPayload,
  UserPreferencesPayload,
  UserProfilePayload,
  UserSettingsResponse
} from '@/types/user';

interface AIFormState {
  ai_provider: string;
  ai_model: string;
  api_key_input: string;
}

interface PasswordFormState extends UserPasswordPayload {
  confirm_password: string;
}

const message = useMessage();
const authStore = useAuthStore();

const loadingSettings = ref(false);
const savingPreferences = ref(false);
const savingAI = ref(false);
const clearingApiKey = ref(false);
const savingProfile = ref(false);
const changingPassword = ref(false);

const preferenceFormRef = ref<FormInst | null>(null);
const aiFormRef = ref<FormInst | null>(null);
const profileFormRef = ref<FormInst | null>(null);
const passwordFormRef = ref<FormInst | null>(null);

const preferenceForm = reactive<UserPreferencesPayload>({
  practice_mode: 'random',
  answer_display_mode: 'immediate'
});

const aiForm = reactive<AIFormState>({
  ai_provider: 'openai',
  ai_model: 'gpt-3.5-turbo',
  api_key_input: ''
});
const hasApiKey = ref(false);
const modelOptions = ref<string[]>([]);
const fetchingModels = ref(false);

const profileForm = reactive<UserProfilePayload>({
  nickname: '',
  avatar_url: ''
});

const passwordForm = reactive<PasswordFormState>({
  old_password: '',
  new_password: '',
  confirm_password: ''
});

const preferenceRules: FormRules = {
  practice_mode: [{ required: true, message: '请选择练习模式', trigger: ['change'] }],
  answer_display_mode: [{ required: true, message: '请选择答案显示方式', trigger: ['change'] }]
};

const aiRules: FormRules = {
  ai_provider: [{ required: true, message: '请选择服务提供商', trigger: ['change'] }],
  ai_model: [{ required: true, message: '请输入模型名称', trigger: ['input', 'blur'] }]
};

const modelSelectOptions = computed(() =>
  Array.from(
    new Set([
      ...modelOptions.value,
      aiForm.ai_model ? aiForm.ai_model : ''
    ].filter(Boolean))
  ).map((item) => ({ label: item, value: item }))
);

const canFetchModels = computed(
  () =>
    aiForm.ai_provider !== 'custom' &&
    aiForm.ai_provider !== 'mock' &&
    Boolean(aiForm.api_key_input.trim() || hasApiKey.value)
);

const profileRules: FormRules = {
  nickname: [{ required: true, message: '昵称不能为空', trigger: ['input', 'blur'] }]
};

const passwordRules: FormRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: ['blur', 'input'] }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: ['blur', 'input'] },
    {
      validator: (_rule, value: string) => {
        if (!value || value.length >= 8) return true;
        return new Error('新密码至少 8 个字符');
      },
      trigger: ['blur', 'input']
    }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: ['blur', 'input'] },
    {
      validator: (_rule, value: string) => {
        if (value === passwordForm.new_password) return true;
        return new Error('两次输入的密码不一致');
      },
      trigger: ['blur', 'input']
    }
  ]
};

watch(
  () => aiForm.ai_provider,
  () => {
    modelOptions.value = [];
    if (aiForm.ai_provider === 'openai') {
      aiForm.ai_model = aiForm.ai_model || 'gpt-3.5-turbo';
    } else if (aiForm.ai_provider === 'siliconflow') {
      aiForm.ai_model = aiForm.ai_model || 'Qwen/Qwen2-72B-Instruct (32K)';
    }
  }
);

function hydrateProfile() {
  const user = authStore.user;
  profileForm.nickname = user?.nickname ?? '';
  profileForm.avatar_url = user?.avatarUrl ?? '';
}

async function loadSettings() {
  loadingSettings.value = true;
  try {
    const data: UserSettingsResponse = await fetchUserSettings();
    preferenceForm.practice_mode = data.practice_mode ?? 'random';
    preferenceForm.answer_display_mode = data.answer_display_mode ?? 'immediate';
    aiForm.ai_provider = data.ai_provider ?? 'openai';
    aiForm.ai_model = data.ai_model ?? 'gpt-3.5-turbo';
    aiForm.api_key_input = '';
    hasApiKey.value = data.has_api_key;
    modelOptions.value = [];
  } catch (error) {
    console.error(error);
    message.error('加载设置失败，请稍后重试');
  } finally {
    loadingSettings.value = false;
  }
}

async function handleSavePreferences() {
  if (preferenceFormRef.value) {
    try {
      await preferenceFormRef.value.validate();
    } catch {
      return;
    }
  }
  savingPreferences.value = true;
  try {
    const updated = await updateUserPreferences({
      practice_mode: preferenceForm.practice_mode,
      answer_display_mode: preferenceForm.answer_display_mode
    });
    preferenceForm.practice_mode = updated.practice_mode;
    preferenceForm.answer_display_mode = updated.answer_display_mode;
    message.success('练习偏好已保存');
  } catch (error) {
    console.error(error);
    message.error('保存失败，请稍后重试');
  } finally {
    savingPreferences.value = false;
  }
}

async function handleSaveAI() {
  if (aiFormRef.value) {
    try {
      await aiFormRef.value.validate();
    } catch {
      return;
    }
  }

  const payload: UserAISettingsPayload = {
    ai_provider: aiForm.ai_provider,
    ai_model: aiForm.ai_model
  };
  if (aiForm.api_key_input.trim()) {
    payload.api_key = aiForm.api_key_input.trim();
  }

  savingAI.value = true;
  try {
    const updated = await updateUserAISettings(payload);
    aiForm.ai_provider = updated.ai_provider;
    aiForm.ai_model = updated.ai_model;
    aiForm.api_key_input = '';
    hasApiKey.value = updated.has_api_key;
    modelOptions.value = [];
    message.success('AI 配置已保存');
  } catch (error) {
    console.error(error);
    message.error('保存失败，请稍后重试');
  } finally {
    savingAI.value = false;
  }
}

async function handleFetchModels() {
  if (!canFetchModels.value) {
    message.warning('当前服务商不支持自动获取模型，请手动填写。');
    return;
  }
  fetchingModels.value = true;
  try {
    if (!aiForm.api_key_input.trim() && hasApiKey.value) {
      message.info('使用已保存的 API Key 获取模型列表');
    }
    const result = await fetchAIModels({
      provider: aiForm.ai_provider,
      api_key: aiForm.api_key_input.trim() || undefined
    });
    modelOptions.value = result.models ?? [];
    if (!result.models?.length) {
      message.warning('未获取到模型列表，可手动输入模型名称。');
    } else {
      if (!result.models.includes(aiForm.ai_model)) {
        aiForm.ai_model = result.models[0];
      }
      message.success(`已获取 ${result.models.length} 个模型`);
    }
  } catch (error: any) {
    console.error(error);
    const detail = error?.response?.data?.detail;
    message.error(detail ?? '获取模型失败，请检查 Key 是否有效');
  } finally {
    fetchingModels.value = false;
  }
}

async function handleClearApiKey() {
  clearingApiKey.value = true;
  try {
    const updated = await updateUserAISettings({ api_key: '' });
    hasApiKey.value = updated.has_api_key;
    aiForm.api_key_input = '';
    modelOptions.value = [];
    message.success('已清除 API Key');
  } catch (error) {
    console.error(error);
    message.error('清除失败，请稍后重试');
  } finally {
    clearingApiKey.value = false;
  }
}

async function handleSaveProfile() {
  if (profileFormRef.value) {
    try {
      await profileFormRef.value.validate();
    } catch {
      return;
    }
  }
  savingProfile.value = true;
  try {
    await updateUserProfile({
      nickname: profileForm.nickname,
      avatar_url: profileForm.avatar_url
    });
    await authStore.fetchCurrentUser();
    hydrateProfile();
    message.success('个人资料已更新');
  } catch (error) {
    console.error(error);
    message.error('更新失败，请稍后重试');
  } finally {
    savingProfile.value = false;
  }
}

async function handleChangePassword() {
  if (passwordFormRef.value) {
    try {
      await passwordFormRef.value.validate();
    } catch {
      return;
    }
  }
  changingPassword.value = true;
  try {
    await changeUserPassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    });
    message.success('密码修改成功，下次登录请使用新密码');
    passwordForm.old_password = '';
    passwordForm.new_password = '';
    passwordForm.confirm_password = '';
  } catch (error) {
    console.error(error);
    message.error('修改失败，请确认原密码是否正确');
  } finally {
    changingPassword.value = false;
  }
}

onMounted(async () => {
  if (!authStore.user) {
    try {
      await authStore.fetchCurrentUser();
    } catch (error) {
      console.error(error);
    }
  }
  hydrateProfile();
  await loadSettings();
});
</script>

<style scoped>
.settings-grid :deep(.n-card) {
  border-radius: var(--radius-large);
  box-shadow: var(--shadow-medium);
}

.settings-grid :deep(.n-form) {
  gap: 16px;
}
</style>
