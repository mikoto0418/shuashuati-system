<template>
  <div class="page dashboard-page">
    <section class="page-hero neo-card">
      <div class="page-hero__content">
        <h1 class="page-hero__title">刷刷题仪表盘</h1>
        <p class="page-hero__subtitle">
          总览练习进度、错题积累与收藏，随时调整学习节奏。
        </p>
        <div class="page-hero__actions">
          <n-button type="primary" size="large" @click="goToPractice" :loading="loading">
            开始练习
          </n-button>
          <n-button tertiary size="large" @click="goToWrongBook" :loading="loading">
            打开错题本
          </n-button>
        </div>
      </div>
      <div class="page-hero__metrics">
        <div class="metric-stack">
          <div class="metric-pill">
            <span class="metric-pill__value">{{ todayCompleted }}</span>
            <span class="metric-pill__label">今日完成</span>
          </div>
          <div class="metric-pill">
            <span class="metric-pill__value">{{ todayAccuracyDisplay }}</span>
            <span class="metric-pill__label">今日正确率</span>
          </div>
          <div class="metric-pill">
            <span class="metric-pill__value">{{ pendingWrongQuestions }}</span>
            <span class="metric-pill__label">待复习错题</span>
          </div>
        </div>
      </div>
    </section>

    <section class="metric-section">
      <div class="metric-stack">
        <div class="metric-pill neo-card">
          <span class="metric-pill__value">{{ totalPracticeQuestions }}</span>
          <span class="metric-pill__label">累计练习题目</span>
        </div>
        <div class="metric-pill neo-card">
          <span class="metric-pill__value">{{ totalFavorites }}</span>
          <span class="metric-pill__label">收藏题目</span>
        </div>
        <div class="metric-pill neo-card">
          <span class="metric-pill__value">{{ aiParseCount }}</span>
          <span class="metric-pill__label">AI 解析次数</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { NButton, useMessage } from 'naive-ui';

import { fetchDashboardStats } from '@/api/dashboard';
import type { DashboardStats } from '@/types/dashboard';

const router = useRouter();
const message = useMessage();

const loading = ref(false);
const stats = ref<DashboardStats | null>(null);

const todayCompleted = computed(() => stats.value?.today_completed ?? 0);
const todayAccuracyDisplay = computed(() => {
  const value = stats.value?.today_accuracy ?? 0;
  return `${Math.round(value * 1000) / 10}%`;
});
const pendingWrongQuestions = computed(
  () => stats.value?.pending_wrong_questions ?? 0
);
const totalPracticeQuestions = computed(
  () => stats.value?.total_practice_questions ?? 0
);
const totalFavorites = computed(() => stats.value?.total_favorites ?? 0);
const aiParseCount = computed(() => stats.value?.ai_parse_count ?? 0);

const loadDashboardStats = async () => {
  loading.value = true;
  try {
    stats.value = await fetchDashboardStats();
  } catch (error) {
    console.error(error);
    message.error('仪表盘数据加载失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

const goToPractice = () => {
  router.push({ name: 'PracticeCenter' });
};

const goToWrongBook = () => {
  router.push({ name: 'PracticeWrongBook' });
};

onMounted(() => {
  loadDashboardStats();
});
</script>

<style scoped>
.dashboard-page {
  gap: 32px;
}

.metric-section .metric-pill {
  background: var(--color-surface);
  box-shadow: var(--shadow-medium);
}

html[data-theme='dark'] .metric-section .metric-pill {
  background: rgba(26, 34, 51, 0.92);
  border: 1px solid rgba(148, 163, 184, 0.12);
}
</style>
