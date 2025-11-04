<template>
  <footer class="app-footer">
    <span>© {{ currentYear }} 刷刷题系统 · 提升刷题效率</span>
  </footer>
</template>

<script setup lang="ts">
const currentYear = new Date().getFullYear();
</script>

<style scoped>
.app-footer {
  padding: 16px 24px;
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 12px;
  background: var(--color-surface);
  border-top: 1px solid rgba(31, 41, 51, 0.06);
}
</style>
