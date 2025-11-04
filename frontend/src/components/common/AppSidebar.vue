<template>
  <n-layout-sider
    bordered
    collapse-mode="width"
    :collapsed-width="64"
    :width="220"
    :native-scrollbar="false"
    :collapsed="collapsed"
    class="app-sidebar"
  >
    <div class="logo">刷刷题</div>
    <n-menu
      :options="menuOptions"
      :value="activeKey"
      :default-expanded-keys="defaultExpandedKeys"
      @update:value="handleSelect"
    />
  </n-layout-sider>
</template>

<script setup lang="ts">
import { computed, h, ref, toRefs, type Component } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { NIcon } from 'naive-ui';
import type { MenuOption } from 'naive-ui';
import {
  HomeOutline,
  DocumentOutline,
  CloudUploadOutline,
  BarbellOutline,
  SettingsOutline
} from '@vicons/ionicons5';

interface Props {
  collapsed: boolean;
}

const props = defineProps<Props>();
const { collapsed } = toRefs(props);

const router = useRouter();
const route = useRoute();
const defaultExpandedKeys = ref<string[]>(['question-menu', 'practice']);

const renderIcon = (icon: Component) => () =>
  h(NIcon, null, {
    default: () => h(icon)
  });

const menuOptions: MenuOption[] = [
  {
    label: '仪表盘',
    key: 'dashboard',
    icon: renderIcon(HomeOutline)
  },
  {
    label: '题目管理',
    key: 'question-menu',
    icon: renderIcon(DocumentOutline),
    children: [
      {
        label: '题库维护',
        key: 'question-manage'
      },
      {
        label: '分类管理',
        key: 'category-manage'
      },
      {
        label: '题目导入',
        key: 'question-import'
      }
    ]
  },
  {
    label: '练习中心',
    key: 'practice',
    icon: renderIcon(BarbellOutline),
    children: [
      {
        label: '自定义练习',
        key: 'practice-center'
      },
      {
        label: '错题本',
        key: 'practice-wrong-book'
      }
    ]
  },
  {
    label: '系统设置',
    key: 'settings',
    icon: renderIcon(SettingsOutline)
  }
];

const activeKey = computed(() => {
  switch (route.name) {
    case 'QuestionManage':
      return 'question-manage';
    case 'CategoryManage':
      return 'category-manage';
    case 'QuestionImport':
      return 'question-import';
    case 'PracticeCenter':
      return 'practice-center';
    case 'PracticeWrongBook':
      return 'practice-wrong-book';
    case 'SettingsHome':
      return 'settings';
    default:
      return 'dashboard';
  }
});

const handleSelect = (key: string) => {
  switch (key) {
    case 'dashboard':
      router.push({ name: 'DashboardHome' });
      break;
    case 'question-manage':
      router.push({ name: 'QuestionManage' });
      break;
    case 'category-manage':
      router.push({ name: 'CategoryManage' });
      break;
    case 'question-import':
      router.push({ name: 'QuestionImport' });
      break;
    case 'practice-center':
      router.push({ name: 'PracticeCenter' });
      break;
    case 'practice-wrong-book':
      router.push({ name: 'PracticeWrongBook' });
      break;
    case 'settings':
      router.push({ name: 'SettingsHome' });
      break;
    default:
      break;
  }
};
</script>

<style scoped>
.app-sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
  border-right: 1px solid rgba(31, 41, 51, 0.06);
  box-shadow: rgba(15, 23, 42, 0.04) 4px 0 12px;
}

.logo {
  padding: 24px 16px;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-focus);
  letter-spacing: 0.04em;
}
</style>
