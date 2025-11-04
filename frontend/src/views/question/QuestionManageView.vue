<template>
  <div class="page question-manage-page">
    <section class="page-hero neo-card">
      <div class="page-hero__content">
        <h1 class="page-hero__title">题目管理</h1>
        <p class="page-hero__subtitle">
          按分类与关键字快速定位题目，支持批量管理与详情查看。
        </p>
        <div class="page-hero__actions">
          <n-button type="primary" size="large" @click="goToCreate">
            新增题目
          </n-button>
          <n-button tertiary size="large" @click="handleSearch">
            刷新列表
          </n-button>
        </div>
      </div>
      <div class="page-hero__metrics">
        <div class="metric-stack">
          <div class="metric-pill">
            <span class="metric-pill__value">{{ pagination.total }}</span>
            <span class="metric-pill__label">题目总数</span>
          </div>
          <div class="metric-pill">
            <span class="metric-pill__value">{{ selectedRowKeys.length }}</span>
            <span class="metric-pill__label">已选题目</span>
          </div>
        </div>
      </div>
    </section>

    <section class="filter-card neo-card">
      <div class="section-heading">
        <div>
          <h3 class="section-heading__title">筛选条件</h3>
          <p class="section-heading__subtitle">
            支持关键字与分类筛选，按下回车即可搜索。
          </p>
        </div>
      </div>
      <n-form :model="filters" label-placement="left" class="filter-form">
        <div class="filter-grid">
          <n-form-item label="关键字">
            <n-input
              v-model:value="filters.keyword"
              placeholder="题干、解析关键字"
              @keyup.enter="handleSearch"
            />
          </n-form-item>
          <n-form-item label="分类">
            <n-select
              v-model:value="filters.category_id"
              :options="categoryOptions"
              clearable
              placeholder="全部分类"
            />
          </n-form-item>
          <div class="filter-actions">
            <n-button type="primary" :loading="loading" @click="handleSearch">
              查询
            </n-button>
            <n-button secondary @click="resetFilters">重置</n-button>
          </div>
        </div>
      </n-form>
    </section>

    <section class="section-card neo-card data-card">
      <div class="section-heading">
        <div>
          <h3 class="section-heading__title">题目列表</h3>
          <p class="section-heading__subtitle">批量删除、查看详情或编辑题目</p>
        </div>
        <n-button
          type="error"
          quaternary
          :disabled="selectedRowKeys.length === 0"
          :loading="batchDeleting"
          @click="handleBatchDelete"
        >
          删除选中
        </n-button>
      </div>

      <template v-if="isTableEmpty">
        <n-empty description="暂无题目，请先导入或创建。" />
      </template>
      <template v-else>
        <n-data-table
          :loading="loading"
          :columns="columns"
          :data="tableData"
          :row-key="rowKey"
          checkable
          :checked-row-keys="selectedRowKeys"
          @update:checked-row-keys="updateCheckedKeys"
        />
        <n-pagination
          :page="pagination.page"
          :page-size="pagination.pageSize"
          :item-count="pagination.total"
          show-size-picker
          :page-sizes="[10, 20, 50]"
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
        />
      </template>
    </section>

    <n-modal
      v-model:show="showDetailModal"
      preset="card"
      title="题目详情"
      style="width: 680px"
    >
      <n-descriptions v-if="currentDetail" :column="1">
        <n-descriptions-item label="题目">
          {{ currentDetail.question }}
        </n-descriptions-item>
        <n-descriptions-item label="答案">
          {{ currentDetail.answer }}
        </n-descriptions-item>
        <n-descriptions-item label="题型">
          {{ questionTypeLabel(currentDetail.question_type) }}
        </n-descriptions-item>
        <n-descriptions-item label="分类">
          {{ currentDetail.category_name ?? '未分类' }}
        </n-descriptions-item>
        <n-descriptions-item label="解析">
          {{ currentDetail.explanation || '—' }}
        </n-descriptions-item>
        <n-descriptions-item label="选项">
          <n-space vertical>
            <span v-for="option in currentDetail.options || []" :key="option">
              {{ option }}
            </span>
            <span v-if="!currentDetail.options?.length">无选项</span>
          </n-space>
        </n-descriptions-item>
      </n-descriptions>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { computed, h, onMounted, reactive, ref } from 'vue';
import {
  NButton,
  NDataTable,
  NDescriptions,
  NDescriptionsItem,
  NEmpty,
  NForm,
  NFormItem,
  NInput,
  NModal,
  NPagination,
  NSelect,
  NSpace,
  useDialog,
  useMessage,
  type DataTableColumn,
  type SelectOption,
} from 'naive-ui';
import { fetchCategories } from '@/api/category';
import {
  deleteQuestion,
  deleteQuestionsBatch,
  fetchQuestionDetail,
  fetchQuestions,
} from '@/api/question';
import type { CategoryItem } from '@/types/category';
import type {
  QuestionDetail,
  QuestionListItem,
} from '@/types/question';
import { useRouter } from 'vue-router';
import { questionTypeLabel } from '@/utils/question';

const message = useMessage();
const dialog = useDialog();
const router = useRouter();

const filters = reactive({
  keyword: '',
  category_id: null as number | null,
});

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
});

const categories = ref<CategoryItem[]>([]);
const categoryOptions = ref<SelectOption[]>([]);
const tableData = ref<QuestionListItem[]>([]);
const selectedRowKeys = ref<number[]>([]);
const loading = ref(false);
const batchDeleting = ref(false);

const isTableEmpty = computed(
  () => !loading.value && tableData.value.length === 0
);

const showDetailModal = ref(false);
const currentDetail = ref<QuestionDetail | null>(null);

const goToCreate = () => {
  router.push({ name: 'QuestionCreate' });
};

const goToEdit = (id: number) => {
  router.push({ name: 'QuestionEdit', params: { id } });
};

const columns: DataTableColumn<QuestionListItem>[] = [
  { type: 'selection' },
  {
    title: '题目',
    key: 'question',
    ellipsis: { tooltip: true },
  },
  {
    title: '题型',
    key: 'question_type',
    width: 120,
    render: (row) => questionTypeLabel(row.question_type),
  },
  {
    title: '答案',
    key: 'answer',
    width: 160,
    ellipsis: { tooltip: true },
  },
  {
    title: '分类',
    key: 'category_name',
    render(row) {
      return row.category_name ?? '未分类';
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 260,
    render(row) {
      return h(
        NSpace,
        { size: 'small' },
        {
          default: () => [
            h(
              NButton,
              {
                size: 'small',
                type: 'primary',
                quaternary: true,
                onClick: () => openDetail(row.id),
              },
              { default: () => '详情' }
            ),
            h(
              NButton,
              {
                size: 'small',
                type: 'warning',
                quaternary: true,
                onClick: () => goToEdit(row.id),
              },
              { default: () => '编辑' }
            ),
            h(
              NButton,
              {
                size: 'small',
                type: 'error',
                quaternary: true,
                onClick: () => confirmDelete(row.id),
              },
              { default: () => '删除' }
            ),
          ],
        }
      );
    },
  },
];

const rowKey = (row: QuestionListItem) => row.id;

const loadCategories = async () => {
  try {
    categories.value = await fetchCategories();
    categoryOptions.value = categories.value.map((item) => ({
      label: item.name,
      value: item.id,
    }));
  } catch (error) {
    console.error(error);
    message.error('加载分类失败');
  }
};

const loadQuestions = async () => {
  loading.value = true;
  try {
    const result = await fetchQuestions({
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: filters.keyword || undefined,
      category_id: filters.category_id ?? undefined,
    });
    tableData.value = result.items;
    pagination.total = result.total;
  } catch (error) {
    console.error(error);
    message.error('加载题目失败');
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  pagination.page = 1;
  loadQuestions();
};

const resetFilters = () => {
  filters.keyword = '';
  filters.category_id = null;
  handleSearch();
};

const handlePageChange = (page: number) => {
  pagination.page = page;
  loadQuestions();
};

const handlePageSizeChange = (pageSize: number) => {
  pagination.pageSize = pageSize;
  pagination.page = 1;
  loadQuestions();
};

const updateCheckedKeys = (keys: Array<string | number>) => {
  selectedRowKeys.value = keys.map((key) => Number(key));
};

const confirmDelete = (id: number) => {
  dialog.warning({
    title: '确认删除此题目？',
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteQuestion(id);
        message.success('删除成功');
        loadQuestions();
      } catch (error) {
        console.error(error);
        message.error('删除失败');
      }
    },
  });
};

const handleBatchDelete = () => {
  dialog.warning({
    title: '确认删除选中题目？',
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      batchDeleting.value = true;
      try {
        await deleteQuestionsBatch(selectedRowKeys.value);
        message.success('批量删除成功');
        selectedRowKeys.value = [];
        await loadQuestions();
      } catch (error) {
        console.error(error);
        message.error('批量删除失败');
      } finally {
        batchDeleting.value = false;
      }
    },
  });
};

const openDetail = async (id: number) => {
  try {
    currentDetail.value = await fetchQuestionDetail(id);
    showDetailModal.value = true;
  } catch (error) {
    console.error(error);
    message.error('加载详情失败');
  }
};

onMounted(() => {
  loadCategories();
  loadQuestions();
});
</script>

<style scoped>
.question-manage-page {
  gap: 32px;
}

.filter-form {
  display: flex;
  flex-direction: column;
}

.filter-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

.filter-actions {
  display: flex;
  gap: 12px;
}

.options-list {
  display: grid;
  gap: 6px;
}
</style>
