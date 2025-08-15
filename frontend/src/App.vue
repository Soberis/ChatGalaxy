<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <RouterView />
  </div>
</template>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #f5f7fa;
}

#app {
  height: 100%;
  width: 100%;
}

/* Element Plus 主题色覆盖 */
:root {
  --el-color-primary: #1677FF;
  --el-color-primary-light-3: #5B9BFF;
  --el-color-primary-light-5: #8BB8FF;
  --el-color-primary-light-7: #BBD5FF;
  --el-color-primary-light-8: #D6E4FF;
  --el-color-primary-light-9: #ECF5FF;
  --el-color-primary-dark-2: #0958D9;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式字体大小 */
@media (max-width: 768px) {
  html {
    font-size: 14px;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  html {
    font-size: 15px;
  }
}

@media (min-width: 1025px) {
  html {
    font-size: 16px;
  }
}
</style>
