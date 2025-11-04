<template>
  <div class="page">
    <n-page-header title="题库文件解析">
      <template #extra>
        <n-space>
          <n-button tertiary :disabled="loading" @click="resetAll">重置</n-button>
          <n-button
            v-if="isAdmin"
            tertiary
            type="error"
            :loading="cleaning"
            @click="handleCleanupUploads"
          >
            清理上传缓存
          </n-button>
        </n-space>
      </template>
    </n-page-header>

    <n-space vertical size="large">
      <n-card title="Upload Source" class="upload-card">
        <n-space vertical size="large">
          <n-space align="center" wrap>
            <input
              ref="fileInputRef"
              type="file"
              accept=".txt,.doc,.docx,.pdf"
              @change="handleFileChange"
            />
            <n-button type="primary" :loading="loading" @click="handleUpload">
              提交解析任务
            </n-button>
            <span class="upload-hint">
              支持 txt / doc / docx / pdf，单个文件不超过 {{ maxSizeText }}
            </span>
          </n-space>
          <n-radio-group v-model:value="parseMode" size="medium">
            <n-space align="center" wrap>
              <n-radio-button value="basic">规则解析</n-radio-button>
              <n-radio-button value="ai">AI 解析</n-radio-button>
              <n-radio-button value="mixed">混合模式</n-radio-button>
              <span class="mode-hint">
                混合模式会先尝试规则解析，必要时自动调用 AI。
              </span>
            </n-space>
          </n-radio-group>
        </n-space>
      </n-card>

      <n-card v-if="taskStatus" title="解析任务进度" class="task-card">
        <n-space vertical size="medium">
          <div class="task-header">
            <span class="task-name">{{ taskStatus.original_name }}</span>
            <n-tag size="small" :type="statusTagType(taskStatus.status)">
              {{ statusLabel(taskStatus.status) }}
            </n-tag>
          </div>
          <n-progress type="line" :percentage="progressPercent" indicator-placement="outside" />
          <div class="task-meta">
            <span>模式：{{ modeLabel(taskStatus.mode) }}</span>
            <span>更新时间：{{ formatTime(taskStatus.updated_at) }}</span>
            <span v-if="taskStats">
              段数：{{ taskStats.processed_segments ?? taskStats.initial_segments ?? '-' }}，细分：{{ taskStats.auto_split_segments ?? 0 }}，题目：{{ taskStats.parsed_questions ?? '-' }}
            </span>
          </div>
          <div v-if="taskStatus.events?.length" class="event-log">
            <div
              v-for="(event, index) in taskStatus.events"
              :key="index"
              class="event-line"
            >
              {{ describeEvent(event) }}
            </div>
          </div>
          <n-alert
            v-if="taskStatus.error"
            type="error"
            show-icon
            :closable="false"
          >
            {{ taskStatus.error }}
          </n-alert>
          <n-alert
            v-if="taskStatus.warnings?.length"
            type="warning"
            show-icon
            :closable="false"
          >
            <n-space vertical size="small">
              <span v-for="(warning, index) in taskStatus.warnings" :key="index">
                {{ warning }}
              </span>
            </n-space>
          </n-alert>
        </n-space>
      </n-card>

      <n-card v-if="taskHistory.length" title="最近任务" class="task-card">
        <n-space vertical size="small">
          <div v-for="item in taskHistory" :key="item.id" class="history-item">
            <div class="history-header">
              <span class="history-name">{{ item.original_name }}</span>
              <n-tag size="small" :type="statusTagType(item.status)">
                {{ statusLabel(item.status) }}
              </n-tag>
            </div>
            <div class="history-meta">
              <span>模式：{{ modeLabel(item.mode) }}</span>
              <span>更新时间：{{ formatTime(item.updated_at) }}</span>
            </div>
          </div>
        </n-space>
      </n-card>

      <n-card v-if="preview" title="解析结果">
        <n-space vertical size="large">
          <n-alert type="info" show-icon>
            <n-space vertical size="small">
              <span>当前模式：{{ modeLabel(preview.mode) }}</span>
              <span>实际调用 AI：{{ preview.used_ai ? '是' : '否' }}</span>
            </n-space>
          </n-alert>
          <n-alert
            v-if="preview.warnings?.length"
            type="warning"
            show-icon
            :closable="false"
          >
            <n-space vertical size="small">
              <span v-for="(warning, index) in preview.warnings" :key="index">
                {{ warning }}
              </span>
            </n-space>
          </n-alert>
          <n-alert
            v-if="showAutoImportNotice && preview.import_summary"
            type="success"
            show-icon
            :closable="false"
          >
            <n-space vertical size="small">
              <span>
                自动导入完成：分类「{{ preview.import_summary.category_name }}」
                成功 {{ preview.import_summary.success }} 题
                <template v-if="preview.import_summary.failed">
                  ，失败 {{ preview.import_summary.failed }} 题
                </template>
              </span>
              <span v-if="preview.import_summary.created_category">
                已为本次导入新建分类。
              </span>
              <span class="muted">
                如需调整题目，可在题库管理中编辑；当前导入按钮已禁用以避免重复导入。
              </span>
            </n-space>
          </n-alert>
          <n-space align="center">
            <n-input-number
              v-model:value="categoryId"
              :min="1"
              placeholder="分类 ID（可选）"
            />
            <n-button
              type="success"
              :disabled="selectedKeys.length === 0 || preview.auto_imported"
              :loading="confirming"
              @click="handleConfirm"
            >
              导入选中题目
            </n-button>
            <span class="summary-text">
              已解析 {{ preview.questions.length }} 题，当前选中 {{ selectedKeys.length }} 题
            </span>
          </n-space>

          <n-data-table
            :columns="columns"
            :data="preview.questions"
            :row-key="rowKey"
            checkable
            :checked-row-keys="selectedKeys"
            @update:checked-row-keys="updateSelectedKeys"
          />
        </n-space>
      </n-card>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { computed, h, onBeforeUnmount, onMounted, ref } from 'vue';
import {
  NAlert,
  NButton,
  NCard,
  NDataTable,
  NInputNumber,
  NPageHeader,
  NProgress,
  NRadioButton,
  NRadioGroup,
  NSpace,
  NTag,
  useMessage,
  type DataTableColumn
} from 'naive-ui';
import { confirmImport } from '@/api/file';
import { cleanupUploads } from '@/api/admin';
import {
  createParseTask,
  getParseTaskResult,
  getParseTaskStatus,
  listParseTasks
} from '@/api/parseTask';
import type {
  FilePreviewResponse,
  ParsedQuestion,
  ParseTaskStatus,
  ParseTaskEvent
} from '@/types/file';
import { useAuthStore } from '@/stores/auth';
import { questionTypeLabel } from '@/utils/question';

const authStore = useAuthStore();
const fileInputRef = ref<HTMLInputElement | null>(null);
const selectedFile = ref<File | null>(null);
const preview = ref<FilePreviewResponse | null>(null);
const selectedKeys = ref<number[]>([]);
const categoryId = ref<number | null>(null);
const parseMode = ref<'basic' | 'ai' | 'mixed'>('basic');
const taskStatus = ref<ParseTaskStatus | null>(null);
const taskHistory = ref<ParseTaskStatus[]>([]);
const activeTaskId = ref<number | null>(null);
const pollingTimer = ref<number | null>(null);
const historyTimer = ref<number | null>(null);

const loading = ref(false);
const confirming = ref(false);
const cleaning = ref(false);
const message = useMessage();

const maxSizeText = computed(() => {
  const size =
    Number.parseInt(import.meta.env.VITE_MAX_FILE_SIZE ?? '', 10) ||
    50 * 1024 * 1024;
  return `${(size / (1024 * 1024)).toFixed(0)} MB`;
});

const progressPercent = computed(() =>
  taskStatus.value ? Math.round(taskStatus.value.progress * 100) : 0
);
const isAdmin = computed(() => !!authStore.user?.isAdmin);
const showAutoImportNotice = computed(
  () => preview.value?.auto_imported ?? false
);
const taskStats = computed(() => taskStatus.value?.stats ?? null);

const columns: DataTableColumn<ParsedQuestion>[] = [
  {
    type: 'selection'
  },
  {
    title: '#',
    key: 'index',
    width: 70
  },
  {
    title: 'Question',
    key: 'question',
    ellipsis: {
      tooltip: true
    }
  },
  {
    title: '题型',
    key: 'question_type',
    width: 120,
    render: (row) => questionTypeLabel(row.question_type)
  },
  {
    title: 'Options',
    key: 'options',
    render(row) {
      if (!row.options || row.options.length === 0) {
        return h('span', { class: 'muted' }, '--');
      }
      return row.options.map((opt) => `${opt.key}. ${opt.content}`).join(' | ');
    }
  },
  {
    title: '标签',
    key: 'tags',
    width: 160,
    render(row) {
      if (!row.tags || row.tags.length === 0) {
        return h('span', { class: 'muted' }, '--');
      }
      return row.tags.join('、');
    }
  },
  {
    title: 'Answer',
    key: 'answer',
    width: 120,
    ellipsis: {
      tooltip: true
    }
  }
];

const rowKey = (row: ParsedQuestion) => Number(row.index);

const handleFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement;
  selectedFile.value = input.files?.[0] ?? null;
};

const handleUpload = async () => {
  if (!selectedFile.value) {
    message.warning('请先选择文件');
    return;
  }

  loading.value = true;
  try {
    const response = await createParseTask(selectedFile.value, parseMode.value);
    message.success('解析任务已创建，正在后台处理');
    preview.value = null;
    selectedKeys.value = [];
    activeTaskId.value = response.task_id;
    const nowIso = new Date().toISOString();
    const initialStatus: ParseTaskStatus = {
      id: response.task_id,
      status: 'pending',
      progress: 0,
      mode: parseMode.value,
      original_name: response.original_name,
      file_path: response.file_path,
      warnings: [],
      events: [],
      stats: null,
      created_at: nowIso,
      updated_at: nowIso
    };
    taskStatus.value = initialStatus;
    startPolling(response.task_id);
    await refreshTaskHistory();
  } catch (error: any) {
    console.error(error);
    const detail = error?.response?.data?.detail;
    message.error(detail ?? '任务创建失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

const updateSelectedKeys = (keys: Array<string | number>) => {
  selectedKeys.value = keys.map((key) => Number(key));
};

const handleConfirm = async () => {
  if (!preview.value) return;
  if (preview.value.auto_imported) {
    message.info('本次任务已自动写入题库，如需调整请前往题目管理页面。');
    return;
  }
  const selected = preview.value.questions.filter((item) =>
    selectedKeys.value.includes(Number(item.index))
  );
  if (selected.length === 0) {
    message.warning('请至少选择一道题目');
    return;
  }

  confirming.value = true;
  try {
    const payload = {
      file_path: preview.value.file_path,
      category_id: categoryId.value ?? undefined,
      questions: selected
    };
    const result = await confirmImport(payload);
    if (result.success_count > 0) {
      message.success(`成功导入 ${result.success_count} 道题目${result.failed_count ? `，失败 ${result.failed_count} 道` : ''}`);
    } else {
      message.error('没有成功导入题目，请检查提示。');
    }
    if (result.errors?.length) {
      result.errors.forEach((err) => message.warning(err));
    }
  } catch (error: any) {
    console.error(error);
    const detail = error?.response?.data?.detail;
    message.error(detail ?? '导入失败');
  } finally {
    confirming.value = false;
  }
};

const resetAll = () => {
  selectedFile.value = null;
  preview.value = null;
  selectedKeys.value = [];
  categoryId.value = null;
  taskStatus.value = null;
  activeTaskId.value = null;
  stopPolling();
  if (fileInputRef.value) {
    fileInputRef.value.value = '';
  }
};

function modeLabel(mode: 'basic' | 'ai' | 'mixed') {
  switch (mode) {
    case 'ai':
      return 'AI 解析';
    case 'mixed':
      return '混合模式';
    default:
      return '规则解析';
  }
}

function statusLabel(status: string) {
  switch (status) {
    case 'pending':
      return '排队中';
    case 'running':
      return '解析中';
    case 'success':
      return '已完成';
    case 'failed':
      return '失败';
    default:
      return status;
  }
}

function statusTagType(status: string) {
  switch (status) {
    case 'pending':
      return 'warning';
    case 'running':
      return 'info';
    case 'success':
      return 'success';
    case 'failed':
      return 'error';
    default:
      return 'default';
  }
}

function describeEvent(event: ParseTaskEvent) {
  const parts: string[] = [];
  if (event.segment != null) {
    parts.push(`段 ${event.segment}`);
  }
  if (event.message) {
    parts.push(event.message);
  }
  if (event.elapsed != null) {
    parts.push(`耗时 ${event.elapsed}s`);
  }
  if (event.timestamp) {
    parts.push(`@ ${formatTime(event.timestamp)}`);
  }
  return parts.join(' · ');
}

function combineWarnings(a?: string[], b?: string[]) {
  const merged = [...(a ?? []), ...(b ?? [])];
  return Array.from(new Set(merged));
}

function stopPolling() {
  if (pollingTimer.value !== null) {
    window.clearInterval(pollingTimer.value);
    pollingTimer.value = null;
  }
}

function stopHistoryPolling() {
  if (historyTimer.value !== null) {
    window.clearInterval(historyTimer.value);
    historyTimer.value = null;
  }
}

async function fetchTaskStatus(taskId: number) {
  try {
    const status = await getParseTaskStatus(taskId);
    taskStatus.value = status;
    if (status.status === 'success') {
      await handleTaskSuccess(status);
      stopPolling();
      await refreshTaskHistory();
    } else if (status.status === 'failed') {
      stopPolling();
      message.error(status.error ?? '解析任务失败，请查看提示');
      preview.value = null;
      await refreshTaskHistory();
    }
  } catch (error) {
    console.error(error);
    message.error('获取任务状态失败');
  }
}

async function handleCleanupUploads() {
  if (cleaning.value) return;
  cleaning.value = true;
  try {
    const msg = await cleanupUploads();
    message.success(msg);
    await refreshTaskHistory();
  } catch (error) {
    console.error(error);
    message.error('清理缓存失败');
  } finally {
    cleaning.value = false;
  }
}

async function handleTaskSuccess(status: ParseTaskStatus) {
  try {
    const result = await getParseTaskResult(status.id);
    const warnings = combineWarnings(status.warnings, result.warnings);
    preview.value = {
      file_path: result.file_path,
      original_name: result.original_name,
      text: '',
      questions: result.questions,
      mode: status.mode,
      used_ai: result.used_ai,
      warnings,
      stats: result.stats ?? null,
      events: result.events,
      auto_imported: result.auto_imported,
      import_summary: result.import_summary ?? null
    };
    selectedKeys.value = result.questions.map((item, index) =>
      Number.isFinite(item.index) ? Number(item.index) : index + 1
    );
    if (warnings.length) {
      warnings.forEach((warning) => message.warning(warning));
    }
    message.success(`已解析 ${result.questions.length} 道题目`);
    if (result.auto_imported && result.import_summary) {
      message.success(
        `已自动导入 ${result.import_summary.success} 道题目至分类「${result.import_summary.category_name}」`
      );
    }
  } catch (error) {
    console.error(error);
    message.error('获取解析结果失败');
  }
}

function startPolling(taskId: number) {
  stopPolling();
  fetchTaskStatus(taskId);
  pollingTimer.value = window.setInterval(() => fetchTaskStatus(taskId), 2000);
}

async function refreshTaskHistory() {
  try {
    const { tasks } = await listParseTasks();
    taskHistory.value = tasks.slice(0, 5);
  } catch (error) {
    console.error(error);
  }
}

function startHistoryPolling() {
  stopHistoryPolling();
  refreshTaskHistory();
  historyTimer.value = window.setInterval(() => {
    refreshTaskHistory();
  }, 5000);
}

function formatTime(iso: string) {
  if (!iso) return '--';
  return new Date(iso).toLocaleString();
}

onMounted(() => {
  startHistoryPolling();
});

onBeforeUnmount(() => {
  stopPolling();
  stopHistoryPolling();
});
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.upload-card {
  max-width: 720px;
}

.upload-hint {
  font-size: 12px;
  color: #7b8794;
}

.mode-hint {
  font-size: 12px;
  color: #7b8794;
}

.summary-text {
  font-size: 14px;
  color: #52606d;
}

.task-card {
  border-radius: var(--radius-medium);
  box-shadow: var(--shadow-small);
}

.task-header,
.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.task-name,
.history-name {
  font-weight: 600;
  color: #1f2933;
}

.task-meta,
.history-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #7b8794;
}

.history-item {
  padding: 8px 0;
  border-bottom: 1px solid rgba(82, 96, 109, 0.12);
}

.history-item:last-child {
  border-bottom: none;
}

.muted {
  color: #9aa5b1;
}
</style>
