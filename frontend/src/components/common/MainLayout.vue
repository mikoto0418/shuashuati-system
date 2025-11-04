<template>
  <n-layout has-sider class="main-layout">
    <AppSidebar :collapsed="isSidebarCollapsed" />
    <n-layout>
      <AppHeader @toggle-sidebar="toggleSidebar" />
      <n-layout-content class="layout-content">
        <RouterView />
      </n-layout-content>
      <AppFooter />
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import AppHeader from './AppHeader.vue';
import AppSidebar from './AppSidebar.vue';
import AppFooter from './AppFooter.vue';

const isSidebarCollapsed = ref(false);

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
};
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  background: var(--color-surface-subtle);
}

.layout-content {
  padding: 24px;
  background: var(--color-surface-subtle);
}
</style>
