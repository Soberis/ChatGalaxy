import { globalIgnores } from 'eslint/config'
import { defineConfigWithVueTs, vueTsConfigs } from '@vue/eslint-config-typescript'
import pluginVue from 'eslint-plugin-vue'
import pluginVitest from '@vitest/eslint-plugin'
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting'

// To allow more languages other than `ts` in `.vue` files, uncomment the following lines:
// import { configureVueProject } from '@vue/eslint-config-typescript'
// configureVueProject({ scriptLangs: ['ts', 'tsx'] })
// More info at https://github.com/vuejs/eslint-config-typescript/#advanced-setup

export default defineConfigWithVueTs(
  {
    name: 'app/files-to-lint',
    files: ['**/*.{ts,mts,tsx,vue}'],
  },

  globalIgnores(['**/dist/**', '**/dist-ssr/**', '**/coverage/**', '**/node_modules/**']),

  pluginVue.configs['flat/essential'],
  vueTsConfigs.recommended,
  
  {
    ...pluginVitest.configs.recommended,
    files: ['src/**/__tests__/*'],
  },
  skipFormatting,
  
  // 开发阶段优化配置 - 放宽一些规则提高开发效率
  {
    rules: {
      // TypeScript 相关规则 - 开发阶段放宽
      '@typescript-eslint/no-explicit-any': 'warn', // 改为警告而不是错误
      '@typescript-eslint/no-unused-vars': ['warn', { 
        'argsIgnorePattern': '^_',
        'varsIgnorePattern': '^_',
        'caughtErrorsIgnorePattern': '^_'
      }], // 未使用变量改为警告，忽略下划线开头的变量
      '@typescript-eslint/no-non-null-assertion': 'warn', // 允许非空断言，但给出警告
      '@typescript-eslint/ban-ts-comment': 'warn', // 允许 @ts-ignore，但给出警告
      '@typescript-eslint/no-var-requires': 'off', // 允许 require 语句
      '@typescript-eslint/prefer-const': 'warn', // 优先使用 const 改为警告
      '@typescript-eslint/no-inferrable-types': 'warn', // 可推断的类型改为警告
      '@typescript-eslint/ban-types': 'warn', // 禁止的类型改为警告
      '@typescript-eslint/no-empty-function': 'warn', // 空函数改为警告
      '@typescript-eslint/no-empty-interface': 'warn', // 空接口改为警告
      
      // Vue 相关规则 - 开发阶段优化
      'vue/multi-word-component-names': 'warn', // 组件名可以是单个单词
      'vue/no-unused-components': 'warn', // 未使用的组件改为警告
      'vue/no-unused-vars': 'warn', // 未使用的变量改为警告
      'vue/require-default-prop': 'warn', // props 默认值改为警告
      'vue/require-prop-types': 'warn', // props 类型改为警告
      'vue/no-v-html': 'warn', // v-html 改为警告
      'vue/require-v-for-key': 'warn', // v-for key 改为警告
      
      // 通用规则 - 开发阶段优化
      'no-console': 'warn', // 允许 console，但给出警告
      'no-debugger': 'warn', // 允许 debugger，但给出警告
      'no-alert': 'warn', // 允许 alert，但给出警告
      'prefer-const': 'warn', // 优先使用 const 改为警告
      'no-var': 'warn', // 避免使用 var 改为警告
      'no-unused-vars': 'off', // 关闭原生规则，使用 TypeScript 版本
      'no-undef': 'warn', // 未定义变量改为警告
      'no-redeclare': 'warn', // 重复声明改为警告
      'no-unreachable': 'warn', // 不可达代码改为警告
      'no-constant-condition': 'warn', // 常量条件改为警告
      
      // 代码风格 - 开发阶段放宽
      'max-len': ['warn', { 
        'code': 120, 
        'ignoreUrls': true, 
        'ignoreStrings': true,
        'ignoreTemplateLiterals': true,
        'ignoreRegExpLiterals': true
      }], // 行长度限制放宽
      'indent': ['warn', 2], // 缩进改为警告
      'quotes': ['warn', 'single'], // 引号改为警告
      'semi': ['warn', 'never'], // 分号改为警告
      'comma-dangle': ['warn', 'never'], // 尾随逗号改为警告
      'object-curly-spacing': ['warn', 'always'], // 对象大括号间距改为警告
      'array-bracket-spacing': ['warn', 'never'], // 数组括号间距改为警告
      'space-before-function-paren': ['warn', 'always'], // 函数括号前空格改为警告
      
      // 测试相关 - 开发阶段优化
      'vitest/no-disabled-tests': 'warn', // 禁用的测试改为警告
      'vitest/no-focused-tests': 'warn', // 聚焦的测试改为警告
      'vitest/no-identical-title': 'warn', // 相同标题改为警告
      'vitest/expect-expect': 'warn', // 期望断言改为警告
      
      // 错误处理 - 开发阶段优化
      'no-empty': 'warn', // 空块改为警告
      'no-empty-pattern': 'warn', // 空模式改为警告
      'no-fallthrough': 'warn', // 缺少 break 改为警告
      'no-irregular-whitespace': 'warn', // 不规则空格改为警告
      'no-mixed-spaces-and-tabs': 'warn', // 混合空格和制表符改为警告
      'no-trailing-spaces': 'warn', // 尾随空格改为警告
      'no-multiple-empty-lines': ['warn', { 'max': 2 }], // 多个空行改为警告
      
      // 性能相关 - 开发阶段优化
      'prefer-template': 'warn', // 优先使用模板字符串改为警告
      'prefer-arrow-callback': 'warn', // 优先使用箭头函数改为警告
      'prefer-destructuring': 'warn', // 优先使用解构改为警告
      'prefer-rest-params': 'warn', // 优先使用剩余参数改为警告
      'prefer-spread': 'warn', // 优先使用展开运算符改为警告
      
      // 安全相关 - 开发阶段保持严格
      'no-eval': 'error', // 禁止 eval
      'no-implied-eval': 'error', // 禁止隐式 eval
      'no-new-func': 'error', // 禁止 new Function
      'no-script-url': 'error', // 禁止 javascript: URL
      'no-unsafe-finally': 'error', // 禁止不安全的 finally
      
      // 开发阶段特殊规则
      'no-warning-comments': 'off', // 允许 TODO 注释
      'no-restricted-syntax': 'off', // 关闭限制语法
      'no-restricted-globals': 'off', // 关闭限制全局变量
    }
  }
)
