import type { PracticeMode } from './practice';

export type AnswerDisplayMode = 'immediate' | 'summary';

export type AIProvider =
  | 'openai'
  | 'azure'
  | 'qianfan'
  | 'dashscope'
  | 'siliconflow'
  | 'custom';

export interface UserSettingsResponse {
  id: number;
  user_id: number;
  ai_provider: string;
  ai_model: string;
  practice_mode: PracticeMode;
  answer_display_mode: AnswerDisplayMode;
  has_api_key: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserPreferencesPayload {
  practice_mode?: PracticeMode | null;
  answer_display_mode?: AnswerDisplayMode | null;
}

export interface UserAISettingsPayload {
  ai_provider?: string | null;
  ai_model?: string | null;
  api_key?: string | null;
}

export interface AIModelListRequest {
  provider: string;
  api_key?: string | null;
}

export interface AIModelListResponse {
  models: string[];
}

export interface UserProfilePayload {
  nickname?: string | null;
  avatar_url?: string | null;
}

export interface UserPasswordPayload {
  old_password: string;
  new_password: string;
}

export const answerDisplayOptions: Array<{ label: string; value: AnswerDisplayMode }> = [
  { label: '提交后即时显示', value: 'immediate' },
  { label: '练习结束统一查看', value: 'summary' }
];

export const aiProviderOptions: Array<{ label: string; value: AIProvider }> = [
  { label: 'OpenAI', value: 'openai' },
  { label: 'Azure OpenAI', value: 'azure' },
  { label: '阿里通义（DashScope）', value: 'dashscope' },
  { label: '百度千帆', value: 'qianfan' },
  { label: '硅基流动（SiliconFlow）', value: 'siliconflow' },
  { label: '其他自定义', value: 'custom' }
];
