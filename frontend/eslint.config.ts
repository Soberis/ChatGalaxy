import pluginVue from 'eslint-plugin-vue'
import pluginVitest from '@vitest/eslint-plugin'
import { defineConfigWithVueTs } from '@vue/eslint-config-typescript'
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting'

export default defineConfigWithVueTs(
  {
    name: 'app/files-to-lint',
    files: ['**/*.{ts,mts,tsx,vue}'],
  },

  // 全局忽略
  {
    ignores: ['**/dist/**', '**/dist-ssr/**', '**/coverage/**', '**/node_modules/**']
  },

  // Vue 基础配置
  ...pluginVue.configs['flat/essential'],
  
  // 测试文件配置
  {
    ...pluginVitest.configs.recommended,
    files: ['src/**/__tests__/*'],
  },
  
  // 跳过格式化
  skipFormatting,
  
  // 开发阶段优化配置
  {
    rules: {
      // TypeScript 相关规则 - 开发阶段放宽
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': ['warn', { 
        'argsIgnorePattern': '^_',
        'varsIgnorePattern': '^_',
        'caughtErrorsIgnorePattern': '^_'
      }],
      '@typescript-eslint/ban-ts-comment': 'warn',
      '@typescript-eslint/no-var-requires': 'off',
      '@typescript-eslint/no-inferrable-types': 'warn',
      '@typescript-eslint/ban-types': 'warn',
      
      // Vue 相关规则 - 开发阶段优化
      'vue/multi-word-component-names': 'warn',
      'vue/no-unused-components': 'warn',
      'vue/no-unused-vars': 'warn',
      
      // 通用规则 - 开发阶段优化
      'no-console': 'warn',
      'no-debugger': 'warn',
      'prefer-const': 'warn',
      'no-var': 'warn',
      'no-unused-vars': 'off', // 使用 TypeScript 版本
      
      // 代码风格 - 开发阶段放宽
      'max-len': ['warn', { 
        'code': 120, 
        'ignoreUrls': true, 
        'ignoreStrings': true
      }],
      
      // 安全相关 - 保持严格
      'no-eval': 'error',
      'no-implied-eval': 'error',
    }
  }
)
