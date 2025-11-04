<template>
  <div class="page">
    <n-page-header title="错题本" />
    <n-card>
      <n-data-table
        :loading="loading"
        :columns="columns"
        :data="wrongQuestions"
        :row-key="rowKey"
        :expanded-row-keys="expandedRowKeys"
        @update:expanded-row-keys="updateExpanded"
      />
      <n-empty
        v-if="!loading && wrongQuestions.length === 0"
        description="当前没有错题，继续保持！"
      />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue';
import {
  DataTableColumn,
  NButton,
  NCard,
  NDataTable,
  NEmpty,
  NPageHeader,
  NSpace,
  useDialog,
  useMessage
} from 'naive-ui';
import { useRouter } from 'vue-router';
import { fetchWrongQuestions, removeWrongQuestion } from '@/api/wrongQuestion';
import type { WrongQuestionItem } from '@/types/wrongQuestion';

const message = useMessage();
const dialog = useDialog();
const router = useRouter();

const wrongQuestions = ref<WrongQuestionItem[]>([]);
const loading = ref(false);
const expandedRowKeys = ref<number[]>([]);

const columns: DataTableColumn<WrongQuestionItem>[] = [
  {
    type: 'expand',
    renderExpand(row) {
      return h('div', { class: 'expand-content' }, [
        h('div', { class: 'expand-title' }, '题目详情'),
        h('p', row.question),
        row.options.length
          ? h(
              'ul',
              { class: 'options' },
              row.options.map((opt) => h('li', opt))
            )
          : null,
        row.explanation
          ? h('p', { class: 'explanation' }, `解析：${row.explanation}`)
          : null
      ]);
    }
  },
  {
    title: '题目',
    key: 'question',
    ellipsis: { tooltip: true }
  },
  {
    title: '分类',
    key: 'category_name',
    render(row) {
      return row.category_name ?? '未分类';
    }
  },
  {
    title: '错题次数',
    key: 'wrong_count',
    width: 120
  },
  {
    title: '最近错误时间',
    key: 'last_wrong_time',
    width: 200
  },
  {
    title: '操作',
    key: 'actions',
    width: 220,
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
                onClick: () => handleRepractice()
              },
              { default: () => '错题再练' }
            ),
            h(
              NButton,
              {
                size: 'small',
                type: 'error',
                quaternary: true,
                onClick: () => confirmRemove(row.question_id)
              },
              { default: () => '移除' }
            )
          ]
        }
      );
    }
  }
];

const rowKey = (row: WrongQuestionItem) => row.question_id;

function updateExpanded(keys: Array<string | number>) {
  expandedRowKeys.value = keys.map((key) => Number(key));
}

async function loadData() {
  loading.value = true;
  try {
    wrongQuestions.value = await fetchWrongQuestions();
  } catch (error) {
    console.error(error);
    message.error('加载错题失败，请稍后重试。');
  } finally {
    loading.value = false;
  }
}

function handleRepractice() {
  router.push({ name: 'PracticeCenter', query: { mode: 'wrong' } });
}

function confirmRemove(questionId: number) {
  dialog.warning({
    title: '确认移除此错题？',
    content: '移除后将不再出现在错题本中。',
    positiveText: '移除',
    negativeText: '取消',
    onPositiveClick: () => remove(questionId)
  });
}

async function remove(questionId: number) {
  try {
    await removeWrongQuestion(questionId);
    message.success('已移除错题');
    await loadData();
  } catch (error) {
    console.error(error);
    message.error('移除失败，请稍后重试。');
  }
}

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.expand-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-right: 48px;
}

.expand-title {
  font-weight: 600;
  color: #1f2933;
}

.options {
  margin: 0;
  padding-left: 20px;
  color: #52606d;
}

.explanation {
  color: #52606d;
}
</style>
