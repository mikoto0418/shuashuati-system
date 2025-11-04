<template>
  <div class="practice-page">
    <template v-if="!sessionState && !summary">
      <section class="hero-section neo-card gradient-hero">
        <div class="hero-content">
          <div class="hero-top">
            <span class="floating-tag">
              <span class="tag-icon">{{ currentModeMeta.icon }}</span>
              <span>{{ currentModeMeta.label }}</span>
            </span>
            <h1 class="hero-title">智能练习中心</h1>
            <p class="hero-subtitle">{{ heroSubtitle }}</p>
          </div>
          <div class="hero-metrics">
            <div v-for="metric in heroMetrics" :key="metric.label" class="metric-card">
              <span class="metric-value">{{ metric.value }}</span>
              <span class="metric-label">{{ metric.label }}</span>
            </div>
          </div>
          <div class="hero-actions">
            <n-button strong type="primary" size="large" :loading="starting" @click="openPreview">
              快速开始
            </n-button>
            <span class="hero-hint">系统将依据当前配置生成最佳题单</span>
          </div>
        </div>
        <div class="hero-insights">
          <div v-for="chip in insightChips" :key="chip.title" class="hero-chip">
            <span class="chip-icon">{{ chip.icon }}</span>
            <div class="chip-text">
              <div class="chip-title">{{ chip.title }}</div>
              <div class="chip-description">{{ chip.description }}</div>
            </div>
          </div>
        </div>
      </section>

      <section class="dashboard-grid">
        <div class="mode-selector neo-card">
          <div class="section-heading">
            <h3>练习模式</h3>
            <span>挑选适合你的刷题节奏</span>
          </div>
          <div class="mode-gallery">
            <button
              v-for="card in modeGallery"
              :key="card.value"
              type="button"
              class="mode-card"
              :class="{ active: configForm.mode === card.value }"
              :style="{ background: card.gradient }"
              @click="selectMode(card.value)"
            >
              <div class="mode-icon">{{ card.icon }}</div>
              <div class="mode-title">{{ card.label }}</div>
              <div class="mode-description">{{ card.description }}</div>
              <span class="mode-cta">{{ configForm.mode === card.value ? '当前模式' : '选择模式' }}</span>
            </button>
          </div>
        </div>

        <div class="config-card neo-card">
          <div class="section-heading">
            <h3>练习配置</h3>
            <span>多维度筛选，打造个性题单</span>
          </div>
          <template v-if="initialLoading">
            <n-skeleton text :repeat="5" />
          </template>
          <template v-else>
            <n-form label-placement="top" :model="configForm" :disabled="starting">
              <div class="config-grid">
                <n-form-item label="练习分类">
                  <n-select
                    v-model:value="configForm.category_ids"
                    multiple
                    clearable
                    filterable
                    :loading="categoryLoading"
                    :options="categoryOptions"
                    placeholder="可选择多个分类，不选则使用全部题库"
                  />
                  <div class="selection-hint">{{ selectedCategoryNames }}</div>
                </n-form-item>
                <n-form-item label="题型筛选">
                  <n-select
                    v-model:value="configForm.question_types"
                    multiple
                    clearable
                    :options="questionTypeOptions"
                    placeholder="默认包含所有题型"
                  />
                  <div class="selection-hint">{{ selectedQuestionTypeNames }}</div>
                </n-form-item>
              </div>
              <div class="config-footer">
                <span class="config-tip">支持多选分类与题型组合筛选</span>
                <n-button type="primary" size="large" :loading="starting" @click="openPreview">
                  生成题单
                </n-button>
              </div>
            </n-form>
          </template>
        </div>
      </section>
    </template>

    <template v-else-if="sessionState && currentQuestion">
      <div class="session-area">
        <div class="session-header">
          <div class="floating-tag">
            <span>{{ currentModeMeta.icon }}</span>
            <span>{{ currentModeMeta.label }}</span>
          </div>
          <div class="session-progress">
            <span class="progress-label">题目进度</span>
            <span class="progress-value">{{ sessionState.currentIndex + 1 }} / {{ sessionState.totalCount }}</span>
          </div>
        </div>

        <n-card class="neo-card session-card">
          <div class="question-head">
            <h2 class="question-title">{{ currentQuestion.question }}</h2>
            <span class="question-type-chip">{{ questionTypeLabel(currentQuestion.question_type) }}</span>
          </div>

          <div v-if="currentQuestionImageUrl" class="question-image">
            <img :src="currentQuestionImageUrl" alt="question image" />
          </div>

          <div class="answer-area">
            <n-radio-group
              v-if="isSingleChoice"
              v-model:value="singleAnswer"
              class="option-group option-group--single"
            >
              <n-radio
                v-for="option in parsedOptions"
                :key="option.key"
                :value="option.key"
                class="option-tile"
              >
                <template v-if="isBooleanQuestion">
                  <span class="option-label">{{ option.label }}</span>
                </template>
                <template v-else>
                  <span class="option-key">{{ option.key }}</span>
                  <span class="option-label">{{ option.label }}</span>
                </template>
              </n-radio>
            </n-radio-group>

            <n-checkbox-group
              v-else-if="isMultipleChoice"
              v-model:value="multipleAnswer"
              class="option-group option-group--multiple"
            >
              <n-checkbox
                v-for="option in parsedOptions"
                :key="option.key"
                :value="option.key"
                class="option-tile"
              >
                <template v-if="isBooleanQuestion">
                  <span class="option-label">{{ option.label }}</span>
                </template>
                <template v-else>
                  <span class="option-key">{{ option.key }}</span>
                  <span class="option-label">{{ option.label }}</span>
                </template>
              </n-checkbox>
            </n-checkbox-group>

            <template v-else>
              <n-input
                v-model:value="textAnswer"
                type="textarea"
                :rows="currentQuestion.question_type === 'short_answer' ? 5 : 3"
                placeholder="请输入答案"
              />
            </template>
          </div>

          <n-alert
            v-if="feedback"
            :type="feedback.is_correct ? 'success' : 'warning'"
            closable
            class="answer-feedback"
            @close="feedback = null"
          >
            <template #header>
              {{ feedback.is_correct ? '回答正确' : '回答结果' }}
            </template>
            <div>
              你的答案：{{
                formatAnswerDisplay(
                  feedbackQuestionType,
                  feedback?.user_answer ?? displayUserAnswer
                )
              }}
            </div>
            <div v-if="feedback?.correct_answer">
              正确答案：{{
                formatAnswerDisplay(feedbackQuestionType, feedback.correct_answer)
              }}
            </div>
            <div v-if="feedback.explanation">解析：{{ feedback.explanation }}</div>
          </n-alert>

          <div class="session-actions">
            <n-button quaternary @click="goToPrevious" :disabled="!hasPreviousQuestion">
              上一题
            </n-button>
            <n-button tertiary :disabled="awaitingNext" @click="resetAnswers">
              重置作答
            </n-button>
            <n-button strong secondary :loading="submitting" :disabled="awaitingNext" @click="handleSubmitAnswer">
              提交答案
            </n-button>
            <n-button
              v-if="awaitingNext"
              type="primary"
              :loading="finishing"
              @click="goToNext"
            >
              {{ isLastQuestion ? '查看结果' : '下一题' }}
            </n-button>
          </div>
        </n-card>
      </div>
    </template>

    <template v-else>
      <div class="summary-area">
        <section class="summary-hero neo-card">
          <div class="summary-head">
            <div>
              <h2>练习完成</h2>
              <p class="summary-subtitle">保持节奏，持续巩固你的知识体系。</p>
            </div>
            <n-button strong secondary :loading="restartLoading" :disabled="!wrongAnswers.length" @click="handleWrongPractice">
              错题再练
            </n-button>
          </div>
          <div class="summary-metrics">
            <div class="metric-card" v-for="metric in summaryMetrics" :key="metric.label">
              <span class="metric-value">{{ metric.value }}</span>
              <span class="metric-label">{{ metric.label }}</span>
            </div>
          </div>
        </section>

        <section class="summary-details neo-card">
          <div class="summary-actions">
            <n-button quaternary @click="goToWrongBook">查看错题本</n-button>
            <n-button @click="resetAll">重新配置练习</n-button>
          </div>
          <template v-if="hasHistory">
            <n-data-table
              :columns="historyColumns"
              :data="answerHistory"
              :row-key="row => row.question_id"
              :row-props="rowProps"
            />
          </template>
          <n-empty v-else description="暂无作答记录，可从练习配置重新开始。" />
        </section>
      </div>
    </template>


    <n-modal
      v-model:show="previewVisible"
      preset="card"
      title="本次练习题目"
      style="width: 840px"
      :mask-closable="false"
    >
      <template v-if="previewLoading">
        <n-skeleton text :repeat="6" />
      </template>
      <template v-else>
        <n-alert v-if="previewError" type="warning" show-icon>
          {{ previewError }}
        </n-alert>
        <template v-else>
          <n-space justify="space-between" align="center" class="preview-toolbar">
            <n-checkbox
              :checked="
                previewSelectedCount > 0 &&
                previewSelectedCount === previewQuestions.length
              "
              @update:checked="toggleSelectAll"
            >
              全选
            </n-checkbox>
            <span class="muted">
              已选择 {{ previewSelectedCount }} / {{ previewQuestions.length }}
            </span>
          </n-space>
          <n-table size="small" :single-line="false">
            <thead>
              <tr>
                <th style="width: 64px">选择</th>
                <th style="width: 64px">序号</th>
                <th>题目</th>
                <th style="width: 120px">题型</th>
                <th style="width: 160px">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in previewQuestions" :key="item.id">
                <td>
                  <n-checkbox v-model:checked="item.selected" />
                </td>
                <td>{{ index + 1 }}</td>
                <td class="preview-question-text">{{ item.question }}</td>
                <td>{{ questionTypeLabel(item.question_type) }}</td>
                <td>
                  <n-space size="small">
                    <n-button
                      size="tiny"
                      tertiary
                      @click="movePreview(index, -1)"
                      :disabled="index === 0"
                    >
                      上移
                    </n-button>
                    <n-button
                      size="tiny"
                      tertiary
                      @click="movePreview(index, 1)"
                      :disabled="index === previewQuestions.length - 1"
                    >
                      下移
                    </n-button>
                  </n-space>
                </td>
              </tr>
              <tr v-if="!previewQuestions.length">
                <td colspan="5">
                  <n-empty description="暂无题目，请调整筛选条件后重试。" />
                </td>
              </tr>
            </tbody>
          </n-table>
        </template>
      </template>
      <template #footer>
        <n-space justify="end">
          <n-button @click="previewVisible = false">取消</n-button>
          <n-button
            type="primary"
            :loading="starting"
            :disabled="!previewSelectedCount"
            @click="confirmPreview"
          >
            开始练习
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import {
  NAlert,
  NButton,
  NCard,
  NCheckbox,
  NCheckboxGroup,
  NDataTable,
  NEmpty,
  NForm,
  NFormItem,
  NInput,
  NModal,
  NRadio,
  NRadioGroup,
  NSelect,
  NSkeleton,
  NSpace,
  NTable,
  useMessage,
  type DataTableColumn
} from 'naive-ui';
import { useRoute, useRouter } from 'vue-router';
import { fetchCategories } from '@/api/category';
import {
  finishPractice,
  getPracticeResult,
  practiceModeOptions,
  previewPractice,
  startPractice,
  submitPracticeAnswer
} from '@/api/practice';
import type {
  PracticeAnswerDetail,
  PracticeAnswerResponse,
  PracticeMode,
  PracticeQuestion,
  PracticeResultResponse,
  PracticeStartResponse
} from '@/types/practice';
import type { CategoryItem } from '@/types/category';
import { useAuthStore } from '@/stores/auth';
import {
  QUESTION_TYPE_OPTIONS,
  questionTypeLabel
} from '@/utils/question';
import { resolveStaticUrl } from '@/utils/url';

interface PracticeSessionState {
  sessionId: number;
  totalCount: number;
  mode: PracticeMode;
  questions: PracticeQuestion[];
  currentIndex: number;
}

interface ParsedOption {
  key: string;
  label: string;
}

interface PreviewQuestion extends PracticeQuestion {
  selected: boolean;
}

type PracticeFeedback = (PracticeAnswerResponse & { question_type?: string | null }) | null;

const BOOLEAN_OPTIONS: ParsedOption[] = [
  { key: 'true', label: '正确' },
  { key: 'false', label: '错误' },
];

function normalizeBooleanValue(value: string | null | undefined): 'true' | 'false' | null {
  if (value === null || value === undefined) return null;
  const normalized = value.toString().trim().toLowerCase();
  if (['true', '1', 't', 'yes', 'y', 'correct', '正确', '对', '是'].includes(normalized)) {
    return 'true';
  }
  if (['false', '0', 'f', 'no', 'n', 'incorrect', '错误', '错', '否'].includes(normalized)) {
    return 'false';
  }
  return null;
}

function formatAnswerDisplay(questionType: string, value: string | null | undefined): string {
  if (questionType === 'true_false') {
    const normalized = normalizeBooleanValue(value);
    if (normalized === 'true') return '正确';
    if (normalized === 'false') return '错误';
    return value ?? '';
  }
  return value ?? '';
}

const message = useMessage();
const router = useRouter();
const route = useRoute();
const autoStarted = ref(false);

const categories = ref<CategoryItem[]>([]);
const categoryLoading = ref(false);
const initialLoading = ref(true);

const previewVisible = ref(false);
const previewLoading = ref(false);
const previewQuestions = ref<PreviewQuestion[]>([]);
const previewError = ref<string | null>(null);

const configForm = reactive({
  mode: practiceModeOptions[0].value as PracticeMode,
  category_ids: [] as number[],
  question_types: [] as string[]
});

const questionTypeOptions = QUESTION_TYPE_OPTIONS;

const categoryOptions = computed(() =>
  categories.value.map((item) => ({ label: item.name, value: item.id }))
);

const categoryLookup = computed(() => new Map(categories.value.map((item) => [item.id, item.name])));
const questionTypeLookup = new Map(QUESTION_TYPE_OPTIONS.map((item) => [item.value, item.label]));

const selectedCategoryNames = computed(() => {
  if (!configForm.category_ids.length) return '全部分类';
  const names = configForm.category_ids
    .map((id) => categoryLookup.value.get(id))
    .filter((name): name is string => Boolean(name));
  return names.length ? names.join('、') : '全部分类';
});

const selectedQuestionTypeNames = computed(() => {
  if (!configForm.question_types.length) return '全部题型';
  const names = configForm.question_types
    .map((type) => questionTypeLookup.get(type) ?? type)
    .filter((name): name is string => Boolean(name));
  return names.length ? names.join('、') : '全部题型';
});

const authStore = useAuthStore();
const displayName = computed(
  () => authStore.user?.nickname || authStore.user?.username || '同学'
);
const heroSubtitle = computed(
  () => `你好，${displayName.value}！定制你的高效刷题旅程。`
);

const modeMetaMap: Record<
  PracticeMode,
  { icon: string; label: string; description: string; gradient: string }
> = {
  sequential: {
    icon: '📚',
    label: '顺序练习',
    description: '按章节逐步推进，适合系统性复习。',
    gradient: 'linear-gradient(135deg, #d3f8ff 0%, #b4ecff 50%, #d8dcff 100%)'
  },
  random: {
    icon: '🎲',
    label: '随机练习',
    description: '智能抽题保持敏感度，检测综合实力。',
    gradient: 'linear-gradient(135deg, #cffafe 0%, #a5f3fc 45%, #d9f99d 100%)'
  },
  wrong: {
    icon: '🧠',
    label: '错题专练',
    description: '聚焦薄弱点，快速补齐短板。',
    gradient: 'linear-gradient(135deg, #fde68a 0%, #fbcfe8 60%, #f9a8d4 100%)'
  },
  favorite: {
    icon: '⭐',
    label: '收藏加固',
    description: '重温重点题，保持长期记忆。',
    gradient: 'linear-gradient(135deg, #e9d5ff 0%, #c4b5fd 50%, #fbcfe8 100%)'
  }
};

const modeGallery = computed(() =>
  practiceModeOptions.map((item) => ({
    value: item.value,
    label: modeMetaMap[item.value].label,
    icon: modeMetaMap[item.value].icon,
    description: modeMetaMap[item.value].description,
    gradient: modeMetaMap[item.value].gradient
  }))
);

const currentModeMeta = computed(() => modeMetaMap[configForm.mode]);

const selectMode = (value: PracticeMode | string) => {
  configForm.mode = value as PracticeMode;
};

const starting = ref(false);
const submitting = ref(false);
const finishing = ref(false);
const awaitingNext = ref(false);
const restartLoading = ref(false);

const sessionState = ref<PracticeSessionState | null>(null);
const summary = ref<PracticeResultResponse | null>(null);
const answerHistory = ref<PracticeAnswerDetail[]>([]);
const feedback = ref<PracticeFeedback>(null);

const singleAnswer = ref<string | null>(null);
const multipleAnswer = ref<string[]>([]);
const textAnswer = ref('');

const currentQuestion = computed(() =>
  sessionState.value?.questions[sessionState.value.currentIndex] ?? null
);
const currentQuestionImageUrl = computed(() =>
  resolveStaticUrl(currentQuestion.value?.image_url ?? null)
);
const parsedOptions = computed<ParsedOption[]>(() => {
  if (!currentQuestion.value) return [];
  if (currentQuestion.value.question_type === 'true_false') {
    return BOOLEAN_OPTIONS;
  }
  return (currentQuestion.value.options ?? []).map(parseOption);
});
const isSingleChoice = computed(
  () =>
    !!currentQuestion.value &&
    ['single_choice', 'true_false'].includes(currentQuestion.value.question_type) &&
    parsedOptions.value.length > 0
);
const isMultipleChoice = computed(
  () =>
    !!currentQuestion.value &&
    currentQuestion.value.question_type === 'multiple_choice' &&
    parsedOptions.value.length > 0
);
const isBooleanQuestion = computed(
  () => currentQuestion.value?.question_type === 'true_false'
);
const isLastQuestion = computed(() =>
  sessionState.value
    ? sessionState.value.currentIndex === sessionState.value.totalCount - 1
    : false
);

const displayUserAnswer = computed(() => {
  if (!currentQuestion.value) return '';
  if (isMultipleChoice.value) {
    return multipleAnswer.value.join(',');
  }
  if (isSingleChoice.value) {
    if (isBooleanQuestion.value) {
      return formatAnswerDisplay('true_false', singleAnswer.value);
    }
    return singleAnswer.value ?? '';
  }
  return textAnswer.value;
});

const historyColumns: DataTableColumn<PracticeAnswerDetail>[] = [
  { title: '题目', key: 'question', ellipsis: { tooltip: true } },
  {
    title: '题型',
    key: 'question_type',
    width: 120,
    render: (row) => questionTypeLabel(row.question_type)
  },
  {
    title: '我的答案',
    key: 'user_answer',
    width: 160,
    render: (row) => formatAnswerDisplay(row.question_type, row.user_answer)
  },
  {
    title: '正确答案',
    key: 'correct_answer',
    width: 160,
    render: (row) => formatAnswerDisplay(row.question_type, row.correct_answer)
  },
  {
    title: '结果',
    key: 'is_correct',
    width: 100,
    render(row) {
      if (row.is_correct === undefined || row.is_correct === null) {
        return '—';
      }
      return row.is_correct ? '正确' : '错误';
    }
  },
  { title: '解析', key: 'explanation', ellipsis: { tooltip: true } }
];

const wrongAnswers = computed(() =>
  answerHistory.value.filter((item) => item.is_correct === false)
);
const hasHistory = computed(() => answerHistory.value.length > 0);

const heroMetrics = computed(() => [
  {
    label: '题库分类',
    value: String(categoryOptions.value.length || 0)
  },
  {
    label: '题型覆盖',
    value: configForm.question_types.length
      ? `${configForm.question_types.length} 类`
      : `${QUESTION_TYPE_OPTIONS.length} 类`
  },
  {
    label: '错题积累',
    value: String(wrongAnswers.value.length)
  }
]);

const summaryMetrics = computed(() => {
  const stats = summary.value;
  if (!stats) {
    return [];
  }
  return [
    { label: '答对题数', value: String(stats.correct_count) },
    { label: '题目总数', value: String(stats.total_count) },
    { label: '正确率', value: formatPercent(stats.correct_rate) },
    { label: '耗时(秒)', value: String(stats.duration_seconds) },
    { label: '错题数量', value: String(wrongAnswers.value.length) }
  ];
});

const insightChips = computed(() => [
  {
    icon: currentModeMeta.value.icon,
    title: currentModeMeta.value.label,
    description: currentModeMeta.value.description
  },
  {
    icon: '🗂',
    title: selectedCategoryNames.value,
    description: '按分类筛选题目，定向巩固知识点。'
  },
  {
    icon: '🎯',
    title: selectedQuestionTypeNames.value,
    description: '题型灵活组合，匹配不同答题节奏。'
  }
]);

const hasPreviousQuestion = computed(() => {
  const state = sessionState.value;
  return !!state && state.currentIndex > 0;
});

const feedbackQuestionType = computed(() => {
  return feedback.value?.question_type ?? currentQuestion.value?.question_type ?? '';
});

const previewSelectedCount = computed(() =>
  previewQuestions.value.filter((item) => item.selected).length
);

const rowProps = (row: PracticeAnswerDetail) => ({
  class: row.is_correct === false ? 'row-wrong' : undefined
});

function parseOption(option: string): ParsedOption {
  const match = option.match(/^([A-Za-z])(?:[\.|\)|．|、]\s?)/u);
  const key = (match ? match[1] : option).toUpperCase();
  const label = match ? option.slice(match[0].length).trim() : option;
  return { key, label: label || option };
}

function resetAnswers() {
  singleAnswer.value = null;
  multipleAnswer.value = [];
  textAnswer.value = '';
  feedback.value = null;
  awaitingNext.value = false;
}

function setCurrentQuestionState() {
  if (!sessionState.value) {
    resetAnswers();
    return;
  }
  const question = sessionState.value.questions[sessionState.value.currentIndex];
  if (!question) {
    resetAnswers();
    return;
  }
  const record = answerHistory.value.find(
    (item) => item.question_id === question.id
  );
  if (!record) {
    resetAnswers();
    return;
  }

  resetAnswers();

  if (question.question_type === 'multiple_choice') {
    multipleAnswer.value = (record.user_answer ?? '')
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean);
  } else if (question.question_type === 'true_false') {
    singleAnswer.value = normalizeBooleanValue(record.user_answer) ?? null;
  } else if (question.question_type === 'single_choice') {
    singleAnswer.value = record.user_answer ?? null;
  } else {
    textAnswer.value = record.user_answer ?? '';
  }

  const normalizedRecordUser =
    question.question_type === 'true_false'
      ? normalizeBooleanValue(record.user_answer) ?? record.user_answer ?? ''
      : record.user_answer ?? '';
  const normalizedRecordCorrect =
    question.question_type === 'true_false'
      ? normalizeBooleanValue(record.correct_answer) ?? record.correct_answer ?? ''
      : record.correct_answer ?? '';

  feedback.value = {
    question_id: record.question_id,
    question_type: question.question_type,
    user_answer: normalizedRecordUser,
    correct_answer: normalizedRecordCorrect,
    is_correct: record.is_correct ?? null,
    explanation: record.explanation ?? null
  };
  awaitingNext.value = true;
}

async function loadCategories() {
  categoryLoading.value = true;
  try {
    categories.value = await fetchCategories();
  } catch (error) {
    console.error(error);
    message.warning('分类列表加载失败，可稍后重试。');
  } finally {
    categoryLoading.value = false;
    initialLoading.value = false;
  }
}

async function startSession(questionIds?: number[]): Promise<boolean> {
  starting.value = true;
  try {
    const payload = {
      mode: configForm.mode,
      category_ids: [...configForm.category_ids],
      question_types: [...configForm.question_types],
      question_ids: questionIds ?? undefined
    };
    const response: PracticeStartResponse = await startPractice(payload);
    if (!response.questions.length) {
      message.warning('未获取到题目，请调整筛选条件后重试。');
      return false;
    }
    sessionState.value = {
      sessionId: response.session_id,
      totalCount: response.total_count,
      mode: response.mode,
      questions: response.questions,
      currentIndex: 0
    };
    summary.value = null;
    answerHistory.value = [];
    setCurrentQuestionState();
    message.success(`开始练习，共 ${response.total_count} 题`);
    return true;
  } catch (error: any) {
    console.error(error);
    const detail = error?.response?.data?.detail;
    message.error(detail ?? '无法开始练习，请稍后重试。');
    return false;
  } finally {
    starting.value = false;
  }
}

function validateAnswer(question: PracticeQuestion): string | null {
  if (isSingleChoice.value) {
    if (!singleAnswer.value) {
      message.warning('请选择一个答案');
      return null;
    }
    return singleAnswer.value;
  }
  if (isMultipleChoice.value) {
    if (!multipleAnswer.value.length) {
      message.warning('请至少选择一个答案');
      return null;
    }
    return multipleAnswer.value.map((item) => item.trim().toUpperCase()).join(',');
  }
  if (!textAnswer.value.trim()) {
    message.warning('请输入答案');
    return null;
  }
  return textAnswer.value.trim();
}

async function handleSubmitAnswer() {
  if (!sessionState.value || !currentQuestion.value) return;
  const userAnswer = validateAnswer(currentQuestion.value);
  if (userAnswer === null) return;

  submitting.value = true;
  try {
    const response = await submitPracticeAnswer(sessionState.value.sessionId, {
      question_id: currentQuestion.value.id,
      user_answer: userAnswer
    });
    const questionType = currentQuestion.value.question_type;
    const normalizedUser =
      questionType === 'true_false'
        ? normalizeBooleanValue(userAnswer) ?? userAnswer ?? ''
        : userAnswer ?? '';
    const normalizedCorrect =
      questionType === 'true_false'
        ? normalizeBooleanValue(response.correct_answer) ??
          response.correct_answer ??
          ''
        : response.correct_answer ?? '';
    feedback.value = {
      ...response,
      question_type: questionType,
      user_answer: normalizedUser,
      correct_answer: normalizedCorrect
    };
    answerHistory.value.push({
      question_id: currentQuestion.value.id,
      question: currentQuestion.value.question,
      question_type: questionType,
      options: currentQuestion.value.options ?? [],
      user_answer: normalizedUser,
      correct_answer: normalizedCorrect,
      is_correct: Boolean(response.is_correct),
      explanation: response.explanation ?? null
    });
    awaitingNext.value = true;
    if (isLastQuestion.value) {
      message.info('最后一题已提交，可查看结果。');
    }
  } catch (error: any) {
    console.error(error);
    const detail = error?.response?.data?.detail;
    message.error(detail ?? '提交答案失败，请稍后重试。');
  } finally {
    submitting.value = false;
  }
}

async function goToNext() {
  if (!sessionState.value) return;
  if (isLastQuestion.value) {
    await handleFinish();
    return;
  }
  sessionState.value.currentIndex += 1;
  setCurrentQuestionState();
}

async function handleFinish() {
  if (!sessionState.value) return;
  finishing.value = true;
  try {
    const sessionId = sessionState.value.sessionId;
    await finishPractice(sessionId);
    const result = await getPracticeResult(sessionId);
    summary.value = result;
    answerHistory.value = result.answers;
    sessionState.value = null;
    message.success('练习完成');
  } catch (error: any) {
    console.error(error);
    const detail = error?.response?.data?.detail;
    message.error(detail ?? '获取练习结果失败，请稍后重试。');
    sessionState.value = null;
  } finally {
    finishing.value = false;
    awaitingNext.value = false;
  }
}

function resetPreviewState() {
  previewQuestions.value = [];
  previewError.value = null;
}

async function openPreview() {
  previewVisible.value = true;
  previewLoading.value = true;
  resetPreviewState();
  try {
    const response = await previewPractice({
      mode: configForm.mode,
      category_ids: [...configForm.category_ids],
      question_types: [...configForm.question_types]
    });
    if (!response.questions.length) {
      previewError.value = '暂无符合条件的题目，可调整筛选条件后重试。';
      return;
    }
    previewQuestions.value = response.questions.map((item) => ({
      ...item,
      selected: true
    }));
  } catch (error: any) {
    console.error(error);
    const detail = error?.response?.data?.detail;
    previewError.value = detail ?? '获取题目列表失败，请稍后重试。';
  } finally {
    previewLoading.value = false;
  }
}

function toggleSelectAll(value: boolean) {
  previewQuestions.value = previewQuestions.value.map((item) => ({
    ...item,
    selected: value
  }));
}

function movePreview(index: number, offset: number) {
  const target = index + offset;
  if (target < 0 || target >= previewQuestions.value.length) return;
  const list = [...previewQuestions.value];
  const [item] = list.splice(index, 1);
  list.splice(target, 0, item);
  previewQuestions.value = list;
}

async function confirmPreview() {
  const selected = previewQuestions.value.filter((item) => item.selected);
  if (!selected.length) {
    message.warning('请至少保留一道题目。');
    return;
  }
  const success = await startSession(selected.map((item) => item.id));
  if (success) {
    previewVisible.value = false;
    resetPreviewState();
  }
}

function goToPrevious() {
  if (!sessionState.value) return;
  if (sessionState.value.currentIndex === 0) return;
  sessionState.value.currentIndex -= 1;
  setCurrentQuestionState();
}

async function handleWrongPractice() {
  if (!wrongAnswers.value.length) {
    message.info('当前没有可供错题再练的题目。');
    return;
  }
  restartLoading.value = true;
  try {
    configForm.mode = 'wrong';
    configForm.category_ids = [];
    configForm.question_types = [];
    await startSession();
  } finally {
    restartLoading.value = false;
  }
}

function resetAll() {
  sessionState.value = null;
  summary.value = null;
  answerHistory.value = [];
  resetAnswers();
  previewVisible.value = false;
  resetPreviewState();
}

function formatPercent(num: number) {
  return `${(num * 100).toFixed(1)}%`;
}

function goToWrongBook() {
  router.push({ name: 'PracticeWrongBook' });
}

async function maybeAutoStart() {
  if (autoStarted.value) return;
  const mode = route.query.mode;
  if (mode === 'wrong') {
    autoStarted.value = true;
    configForm.mode = 'wrong';
    configForm.category_ids = [];
    configForm.question_types = [];
    await startSession();
    router.replace({ name: 'PracticeCenter' });
  }
}

onMounted(async () => {
  await loadCategories();
  await maybeAutoStart();
});

watch(
  () => route.query.mode,
  () => {
    autoStarted.value = false;
    maybeAutoStart();
  }
);

watch(previewVisible, (visible) => {
  if (!visible) {
    resetPreviewState();
  }
});
</script>

<style scoped>
.practice-page {
  display: flex;
  flex-direction: column;
  gap: 32px;
  padding-bottom: 48px;
}

.gradient-hero {
  background: var(--gradient-primary);
  color: var(--color-text-primary);
}

.hero-section {
  display: flex;
  flex-wrap: wrap;
  gap: 32px;
  padding: 40px;
  position: relative;
  overflow: hidden;
}

.hero-content {
  flex: 1 1 320px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-top {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hero-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0;
}

.hero-subtitle {
  margin: 0;
  font-size: 16px;
  color: rgba(31, 41, 51, 0.85);
}

.hero-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.metric-card {
  min-width: 120px;
  padding: 16px 20px;
  border-radius: var(--radius-medium);
  background: rgba(255, 255, 255, 0.82);
  box-shadow: var(--shadow-medium);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric-value {
  font-size: 24px;
  font-weight: 600;
}

.metric-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

html[data-theme='dark'] .metric-card {
  background: rgba(26, 34, 51, 0.92);
  box-shadow: var(--shadow-medium);
  border: 1px solid rgba(148, 163, 184, 0.12);
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.hero-hint {
  font-size: 13px;
  color: rgba(31, 41, 51, 0.72);
}

.hero-insights {
  flex: 0 1 280px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hero-chip {
  display: flex;
  gap: 12px;
  padding: 16px 18px;
  border-radius: var(--radius-medium);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: var(--shadow-medium);
  border: 1px solid rgba(15, 23, 42, 0.08);
}

.chip-icon {
  font-size: 20px;
  color: var(--color-focus);
}

.chip-title {
  font-weight: 600;
}

.chip-description {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.dashboard-grid {
  display: grid;
  gap: 24px;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}

.neo-card {
  padding: 28px !important;
}

.section-heading {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 20px;
}

.section-heading h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.section-heading span {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.mode-gallery {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.mode-card {
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: var(--radius-large);
  padding: 20px;
  text-align: left;
  cursor: pointer;
  color: var(--color-text-primary);
  background: rgba(255, 255, 255, 0.96);
  box-shadow: var(--shadow-medium);
  transition: box-shadow 0.25s ease, border-color 0.25s ease;
}

.mode-card:hover {
  box-shadow: var(--shadow-card);
}

.mode-card.active {
  box-shadow: var(--shadow-card);
  border: 1px solid rgba(15, 23, 42, 0.12);
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.08) 0%, rgba(255, 255, 255, 0.95) 100%);
}

.mode-icon {
  font-size: 28px;
}

.mode-title {
  font-size: 18px;
  font-weight: 600;
  margin: 12px 0 8px;
}

.mode-description {
  font-size: 13px;
  color: rgba(31, 41, 51, 0.75);
  line-height: 1.6;
}

.mode-cta {
  display: inline-flex;
  margin-top: 16px;
  font-size: 12px;
  padding: 6px 12px;
  border-radius: var(--radius-pill);
  background: rgba(15, 23, 42, 0.08);
  color: var(--color-text-primary);
}

html[data-theme='dark'] .mode-card {
  border: 1px solid rgba(148, 163, 184, 0.14);
  background: rgba(26, 34, 51, 0.92);
}

html[data-theme='dark'] .mode-card.active {
  border: 1px solid rgba(56, 211, 159, 0.32);
  background: linear-gradient(135deg, rgba(56, 211, 159, 0.15) 0%, rgba(15, 23, 42, 0.92) 100%);
}

html[data-theme='dark'] .mode-cta {
  background: rgba(56, 211, 159, 0.18);
  color: #c6ffe6;
}

.config-grid {
  display: grid;
  gap: 20px;
}

.selection-hint {
  margin-top: 8px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.config-footer {
  margin-top: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.config-tip {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.session-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-progress {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.progress-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.progress-value {
  font-size: 20px;
  font-weight: 600;
}

.session-card {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.question-head {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.question-title {
  flex: 1;
  margin: 0;
  font-size: 22px;
  line-height: 1.5;
}

.question-type-chip {
  padding: 6px 12px;
  border-radius: var(--radius-pill);
  background: rgba(24, 160, 88, 0.12);
  color: var(--color-focus);
  font-size: 12px;
  font-weight: 600;
}

.question-image img {
  max-width: 100%;
  border-radius: var(--radius-medium);
  box-shadow: var(--shadow-medium);
}

.answer-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.option-group {
  display: grid;
  gap: 12px;
}

.option-group--multiple {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

:deep(.option-tile) {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border-radius: var(--radius-medium);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: var(--shadow-medium);
  border: 1px solid rgba(15, 23, 42, 0.08);
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}

:deep(.option-tile:hover) {
  box-shadow: var(--shadow-card);
}

:deep(.option-tile.n-radio--checked),
:deep(.option-tile.n-checkbox--checked) {
  border-color: var(--color-focus);
  box-shadow: var(--shadow-card);
  background: rgba(255, 255, 255, 0.95);
}

:deep(.option-tile .n-radio__label),
:deep(.option-tile .n-checkbox__label) {
  display: flex;
  align-items: center;
  gap: 12px;
}

html[data-theme='dark'] :deep(.option-tile) {
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(26, 34, 51, 0.92);
  box-shadow: var(--shadow-medium);
}

html[data-theme='dark'] :deep(.option-tile.n-radio--checked),
html[data-theme='dark'] :deep(.option-tile.n-checkbox--checked) {
  border-color: rgba(56, 211, 159, 0.45);
  background: linear-gradient(135deg, rgba(56, 211, 159, 0.2) 0%, rgba(15, 23, 42, 0.92) 100%);
}

.option-key {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--color-focus);
  color: #fff;
  font-weight: 600;
}

.option-label {
  font-size: 14px;
  text-align: left;
}

.answer-feedback {
  margin-top: 12px;
}

.session-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.summary-area {
  display: grid;
  gap: 24px;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}

.summary-hero {
  background: var(--gradient-warm) !important;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.summary-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.summary-head h2 {
  margin: 0;
  font-size: 24px;
}

.summary-subtitle {
  margin: 4px 0 0;
  font-size: 14px;
  color: rgba(31, 41, 51, 0.75);
}

.summary-metrics {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
}

html[data-theme='dark'] .summary-hero {
  background: linear-gradient(135deg, rgba(56, 211, 159, 0.15) 0%, rgba(17, 24, 39, 0.9) 100%) !important;
}

.summary-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.summary-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.preview-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.preview-footer {
  width: 100%;
}

.preview-selection-summary {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.preview-question-text {
  max-height: 3.2em;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.muted {
  color: var(--color-text-secondary);
  font-size: 12px;
}

:deep(.row-wrong) {
  background-color: rgba(248, 113, 113, 0.12);
}

@media (max-width: 768px) {
  .hero-section {
    padding: 28px;
  }

  .hero-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .session-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>


