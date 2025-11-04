<template>
  <div class="page category-page">
    <section class="page-hero neo-card">
      <div class="page-hero__content">
        <h1 class="page-hero__title">分类管理</h1>
        <p class="page-hero__subtitle">
          维护题目分类，构建清晰的知识结构，方便查询与练习。
        </p>
        <div class="page-hero__actions">
          <n-button type="primary" size="large" @click="openCreateModal">
            新增分类
          </n-button>
          <n-button tertiary size="large" @click="fetchData">刷新列表</n-button>
        </div>
      </div>
      <div class="page-hero__metrics">
        <div class="metric-stack">
          <div class="metric-pill">
            <span class="metric-pill__value">{{ categoryCount }}</span>
            <span class="metric-pill__label">分类总数</span>
          </div>
        </div>
      </div>
    </section>

    <section class="section-card neo-card">
      <div class="section-heading">
        <div>
          <h3 class="section-heading__title">分类列表</h3>
          <p class="section-heading__subtitle">
            支持编辑、删除与维护分类说明
          </p>
        </div>
      </div>
      <n-data-table
        :loading="loading"
        :columns="columns"
        :data="categories"
        :row-key="rowKey"
      />
    </section>

    <n-modal v-model:show="showModal" preset="card" :title="modalTitle">
      <n-form ref="formRef" :model="form" :rules="rules" label-placement="top">
        <n-form-item label="名称" path="name">
          <n-input v-model:value="form.name" placeholder="请输入分类名称" />
        </n-form-item>
        <n-form-item label="描述" path="description">
          <n-input
            v-model:value="form.description"
            type="textarea"
            placeholder="可选，填写分类说明"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" :loading="saving" @click="handleSubmit">
            保存
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { computed, h, onMounted, reactive, ref } from 'vue';
import {
  DataTableColumn,
  FormInst,
  FormRules,
  NButton,
  NDataTable,
  NForm,
  NFormItem,
  NInput,
  NModal,
  NSpace,
  useDialog,
  useMessage,
} from 'naive-ui';
import {
  createCategory,
  deleteCategory,
  fetchCategories,
  updateCategory,
} from '@/api/category';
import type { CategoryItem, CreateCategoryPayload } from '@/types/category';

const message = useMessage();
const dialog = useDialog();

const categories = ref<CategoryItem[]>([]);
const loading = ref(false);
const saving = ref(false);
const showModal = ref(false);
const editingId = ref<number | null>(null);
const formRef = ref<FormInst | null>(null);
const modalTitle = computed(() =>
  editingId.value ? '编辑分类' : '新增分类'
);

const categoryCount = computed(() => categories.value.length);

const form = reactive<CreateCategoryPayload>({
  name: '',
  description: ''
});

const rules: FormRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: ['input'] }]
};

const columns: DataTableColumn<CategoryItem>[] = [
  {
    title: '名称',
    key: 'name'
  },
  {
    title: '描述',
    key: 'description'
  },
  {
    title: '题目数量',
    key: 'question_count',
    width: 120
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
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
                onClick: () => openEditModal(row)
              },
              { default: () => '编辑' }
            ),
            h(
              NButton,
              {
                size: 'small',
                type: 'error',
                quaternary: true,
                onClick: () => handleDelete(row.id)
              },
              { default: () => '删除' }
            )
          ]
        }
      );
    }
  }
];

const rowKey = (row: CategoryItem) => row.id;

const loadData = async () => {
  loading.value = true;
  try {
    categories.value = await fetchCategories();
  } catch (error) {
    console.error(error);
    message.error('加载分类失败');
  } finally {
    loading.value = false;
  }
};

const fetchData = () => loadData();

const resetForm = () => {
  form.name = '';
  form.description = '';
};

const openCreateModal = () => {
  editingId.value = null;
  resetForm();
  showModal.value = true;
};

const openEditModal = (item: CategoryItem) => {
  editingId.value = item.id;
  form.name = item.name;
  form.description = item.description ?? '';
  showModal.value = true;
};

const handleSubmit = async () => {
  if (!formRef.value) return;
  try {
    await formRef.value.validate();
  } catch {
    return;
  }

  saving.value = true;
  try {
    if (editingId.value) {
      await updateCategory(editingId.value, form);
      message.success('分类更新成功');
    } else {
      await createCategory(form);
      message.success('分类创建成功');
    }
    showModal.value = false;
    await loadData();
  } catch (error) {
    console.error(error);
    message.error('保存失败，请稍后重试');
  } finally {
    saving.value = false;
  }
};

const handleDelete = (id: number) => {
  dialog.warning({
    title: '确认删除？',
    content: '删除分类后，该分类下题目将转为未分类，确定继续？',
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteCategory(id);
        message.success('删除成功');
        await loadData();
      } catch (error) {
        console.error(error);
        message.error('删除失败，请稍后重试');
      }
    }
  });
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
