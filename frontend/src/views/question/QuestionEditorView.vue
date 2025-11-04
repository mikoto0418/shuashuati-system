<template>
  <div class="page question-editor-page">
    <section class="page-hero neo-card">
      <div class="page-hero__content">
        <h1 class="page-hero__title">{{ pageTitle }}</h1>
        <p class="page-hero__subtitle">
          支持单选、多选、判断等题型，填写题干、选项、解析与标签信息。
        </p>
        <div class="page-hero__actions">
          <n-button quaternary size="large" @click="goBack">返回列表</n-button>
          <n-button type="primary" size="large" :loading="saving" @click="handleSubmit">
            保存题目
          </n-button>
        </div>
      </div>
      <div class="page-hero__metrics">
        <div class="metric-stack">
          <div class="metric-pill">
            <span class="metric-pill__value">{{ questionTypeLabel(form.question_type) }}</span>
            <span class="metric-pill__label">当前题型</span>
          </div>
          <div class="metric-pill">
            <span class="metric-pill__value">{{ categories.length }}</span>
            <span class="metric-pill__label">可用分类</span>
          </div>
        </div>
      </div>
    </section>

    <section class="section-card neo-card">
      <n-form
        ref="formRef"
        label-placement="top"
        :model="form"
        :rules="rules"
        size="large"
        class="editor-form"
      >
        <n-grid :cols="2" :x-gap="24">
          <n-gi>
            <n-form-item label="题目" path="question">
              <n-input
                v-model:value="form.question"
                type="textarea"
                rows="5"
                placeholder="请输入题干，可贴入多行内容"
              />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="答案" path="answer">
              <template v-if="isJudgement">
                <n-radio-group v-model:value="form.answer" size="large">
                  <n-radio value="true">正确</n-radio>
                  <n-radio value="false">错误</n-radio>
                </n-radio-group>
              </template>
              <template v-else>
                <n-input v-model:value="form.answer" placeholder="请输入答案" />
              </template>
            </n-form-item>
          </n-gi>
        </n-grid>

        <n-grid :cols="3" :x-gap="24">
          <n-gi>
            <n-form-item label="题型" path="question_type">
              <n-select
                v-model:value="form.question_type"
                :options="questionTypeSelectOptions"
              />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="分类" path="category_id">
              <n-select
                v-model:value="form.category_id"
                :options="categoryOptions"
                :loading="categoryLoading"
                clearable
                filterable
                placeholder="请选择分类"
              />
              <template #feedback v-if="!hasCategories">
                <n-text depth="3">暂无分类，可前往分类管理创建。</n-text>
              </template>
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="标签（逗号分隔）" path="tags">
              <n-input
                v-model:value="tagInput"
                placeholder="例如：数据结构,选择"
              />
            </n-form-item>
          </n-gi>
        </n-grid>

        <n-form-item label="解析" path="explanation">
          <n-input
            v-model:value="form.explanation"
            type="textarea"
            rows="4"
            placeholder="可填写题目解析，便于后续复盘"
          />
        </n-form-item>

        <n-form-item label="题目图片">
          <div class="image-upload-block">
            <div v-if="previewImageUrl" class="image-preview">
              <img :src="previewImageUrl" alt="question preview" />
              <div class="image-actions">
                <n-button tertiary size="small" @click="handleRemoveImage">
                  移除图片
                </n-button>
              </div>
            </div>
            <n-upload
              accept="image/*"
              :show-file-list="false"
              :max="1"
              :disabled="uploadingImage"
              :custom-request="handleImageUpload"
            >
              <n-button type="primary" quaternary :loading="uploadingImage">
                {{ previewImageUrl ? '重新上传图片' : '上传图片' }}
              </n-button>
            </n-upload>
            <n-text depth="3" class="image-tip">
              支持 PNG/JPG/BMP，大小不超过 5MB。
            </n-text>
          </div>
        </n-form-item>

        <n-form-item
          v-if="shouldShowOptions"
          label="选项"
          path="options"
          class="options-form-item"
        >
          <n-space vertical size="medium">
            <n-space
              v-for="(option, index) in form.options"
              :key="index"
              align="center"
              class="option-row"
            >
              <span class="option-label">{{ String.fromCharCode(65 + index) }}</span>
              <n-input
                v-model:value="form.options[index]"
                :placeholder="`选项 ${String.fromCharCode(65 + index)}`"
              />
              <n-button tertiary type="error" size="small" @click="removeOption(index)">
                删除
              </n-button>
            </n-space>
            <n-button dashed type="primary" @click="addOption">
              新增选项
            </n-button>
          </n-space>
        </n-form-item>
      </n-form>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import {
  NButton,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  NGrid,
  NGi,
  NSpace,
  NText,
  NRadio,
  NRadioGroup,
  NUpload,
  type UploadCustomRequestOptions,
  useMessage,
} from 'naive-ui';
import { useRouter, useRoute } from 'vue-router';
import { fetchCategories } from '@/api/category';
import {
  createQuestion,
  fetchQuestionDetail,
  updateQuestion,
  uploadQuestionImage,
} from '@/api/question';
import type { CategoryItem } from '@/types/category';
import type { QuestionDetail } from '@/types/question';
import { QUESTION_TYPE_OPTIONS, questionTypeLabel } from '@/utils/question';
import { resolveStaticUrl } from '@/utils/url';

const message = useMessage();
const router = useRouter();
const route = useRoute();

const editingId = ref<number | null>(route.params.id ? Number(route.params.id) : null);
const formRef = ref();
const categoryLoading = ref(false);
const categories = ref<CategoryItem[]>([]);
const saving = ref(false);

const form = reactive({
  question: '',
  answer: '',
  question_type: QUESTION_TYPE_OPTIONS[0].value,
  category_id: null as number | null,
  explanation: '',
  options: [] as string[],
  tags: [] as string[],
  image_url: null as string | null,
});

const tagInput = ref('');
const uploadingImage = ref(false);

const rules = {
  question: [{ required: true, message: '请输入题干' }],
  answer: [{ required: true, message: '请输入答案' }],
  question_type: [{ required: true, message: '请选择题型' }],
};

const questionTypeSelectOptions = QUESTION_TYPE_OPTIONS;
const isJudgement = computed(() => form.question_type === 'true_false');
const isMultipleChoice = computed(() => form.question_type === 'multiple_choice');
const isSingleChoiceType = computed(() => form.question_type === 'single_choice');

watch(
  () => form.question_type,
  (type, prev) => {
    if (type === 'true_false') {
      form.options = [];
      form.answer = normalizeBooleanAnswerValue(form.answer) ?? 'true';
    } else {
      if (prev === 'true_false') {
        form.answer = '';
      }
      if (type === 'multiple_choice' || type === 'single_choice') {
        if (!form.options.length) {
          form.options = ['', '', '', ''];
        }
      } else {
        form.options = [];
      }
    }
  },
  { immediate: true }
);

const pageTitle = computed(() =>
  editingId.value ? '编辑题目' : '新增题目'
);

const categoryOptions = computed(() =>
  categories.value.map((item) => ({
    label: item.name,
    value: item.id,
  }))
);

const hasCategories = computed(() => categoryOptions.value.length > 0);

const shouldShowOptions = computed(() =>
  isSingleChoiceType.value || isMultipleChoice.value
);

const previewImageUrl = computed(() => resolveStaticUrl(form.image_url));

const addOption = () => {
  form.options = [...form.options, ''];
};

const removeOption = (index: number) => {
  form.options = form.options.filter((_, i) => i !== index);
};

function normalizeBooleanAnswerValue(value: string | null | undefined): 'true' | 'false' | null {
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

const normalizeTags = () => {
  form.tags =
    tagInput.value
      ?.split(',')
      .map((tag) => tag.trim())
      .filter(Boolean) ?? [];
};

const syncTagInput = () => {
  tagInput.value = (form.tags ?? []).join(',');
};

const ensureCategoryValidity = () => {
  if (
    form.category_id !== null &&
    !categories.value.some((item) => item.id === form.category_id)
  ) {
    form.category_id = null;
  }
};

const loadCategories = async () => {
  categoryLoading.value = true;
  try {
    categories.value = await fetchCategories();
  } catch (error) {
    console.error(error);
    message.warning('分类列表加载失败，可稍后重试或先创建分类。');
  } finally {
    categoryLoading.value = false;
    ensureCategoryValidity();
  }
};

const loadDetail = async () => {
  if (!editingId.value) {
    addOption();
    return;
  }
  try {
    const detail: QuestionDetail = await fetchQuestionDetail(editingId.value);
    form.question = detail.question;
    form.answer = detail.answer;
   form.question_type = detail.question_type;
   form.explanation = detail.explanation ?? '';
   form.options = detail.options ?? [];
   form.tags = detail.tags ?? [];
   form.category_id = detail.category_id ?? null;
    form.image_url = detail.image_url ?? null;
    syncTagInput();
    ensureCategoryValidity();
  } catch (error) {
    console.error(error);
    message.error('加载题目详情失败');
  }
};

const handleSubmit = async () => {
  if (!formRef.value) return;
  try {
    await formRef.value.validate();
  } catch {
    return;
  }

  normalizeTags();

  saving.value = true;
  try {
    if (editingId.value) {
      await updateQuestion(editingId.value, form);
      message.success('题目更新成功');
    } else {
      await createQuestion(form);
      message.success('题目创建成功');
    }
    goBack();
  } catch (error) {
    console.error(error);
    message.error('保存失败，请稍后重试');
  } finally {
    saving.value = false;
  }
};

const goBack = () => {
  router.push({ name: 'QuestionManage' });
};

const initializeOptions = () => {
  if (!form.options.length) {
    form.options = ['', '', '', ''];
  }
};

const handleImageUpload = async (
  options: UploadCustomRequestOptions
): Promise<void> => {
  const { file, onFinish, onError } = options;
  if (!file || !file.file) {
    onError?.();
    return;
  }
  uploadingImage.value = true;
  try {
    const result = await uploadQuestionImage(
      file.file as File,
      editingId.value ?? undefined
    );
    form.image_url = result.image_url;
    onFinish?.();
    message.success(editingId.value ? '图片已更新' : '图片上传成功');
  } catch (error) {
    console.error(error);
    onError?.();
    message.error('图片上传失败，请稍后重试');
  } finally {
    uploadingImage.value = false;
  }
};

const handleRemoveImage = async (): Promise<void> => {
  if (editingId.value) {
    try {
      await updateQuestion(editingId.value, { image_url: null });
      message.success('已移除图片');
    } catch (error) {
      console.error(error);
      message.error('移除图片失败，请稍后重试');
      return;
    }
  }
  form.image_url = null;
};

onMounted(async () => {
  await loadCategories();
  await loadDetail();
  initializeOptions();
});
</script>

<style scoped>
.question-editor-page {
  gap: 32px;
}

.editor-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filter-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

.option-row {
  display: grid;
  grid-template-columns: 32px 1fr auto;
  gap: 12px;
  align-items: center;
}

.option-label {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--color-focus);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.options-form-item {
  margin-bottom: 0;
}

.image-upload-block {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-start;
}

.image-preview {
  position: relative;
  max-width: 320px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--card-shadow);
}

.image-preview img {
  display: block;
  width: 100%;
  height: auto;
}

.image-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 8px;
}

.image-tip {
  font-size: 12px;
}
</style>
