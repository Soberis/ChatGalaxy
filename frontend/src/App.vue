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

  html,
  body {
    height: 100%;
    font-family:
      'Inter',
      -apple-system,
      BlinkMacSystemFont,
      'Segoe UI',
      Roboto,
      sans-serif;
    background-color: #f5f7fa;
  }

  #app {
    height: 100%;
    width: 100%;
  }

  /* Element Plus 主题色覆盖 */
  :root {
    --el-color-primary: #1677ff;
    --el-color-primary-light-3: #5b9bff;
    --el-color-primary-light-5: #8bb8ff;
    --el-color-primary-light-7: #bbd5ff;
    --el-color-primary-light-8: #d6e4ff;
    --el-color-primary-light-9: #ecf5ff;
    --el-color-primary-dark-2: #0958d9;
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
  @media (max-width: 640px) {
    html {
      font-size: 14px;
    }
  }

  @media (min-width: 641px) and (max-width: 1024px) {
    html {
      font-size: 15px;
    }
  }

  @media (min-width: 1025px) {
    html {
      font-size: 16px;
    }
  }

  /* 文字截断工具类 */
  .line-clamp-2 {
    overflow: hidden;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
  }

  .line-clamp-3 {
    overflow: hidden;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;
  }

  /* 移动端触摸优化 */
  @media (max-width: 768px) {
    .el-button {
      min-height: 44px;
    }

    .el-input__wrapper {
      min-height: 44px;
    }

    .el-dropdown-menu__item {
      min-height: 44px;
      display: flex;
      align-items: center;
    }
  }

  /* 平滑滚动 */
  html {
    scroll-behavior: smooth;
  }

  /* 提高对比度 */
  .text-gray-500 {
    color: #6b7280;
  }

  .text-gray-600 {
    color: #4b5563;
  }

  .text-gray-700 {
    color: #374151;
  }
</style>
