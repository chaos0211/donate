

<template>
  <div class="inline-flex rounded-full overflow-hidden bg-gray-100">
    <button
      v-for="v in resolvedOptions"
      :key="v"
      class="px-4 py-2 text-sm"
      :class="modelValue === v ? activeBtn : normalBtn"
      @click="onPick(v)"
    >
      {{ renderLabel(v) }}
    </button>
  </div>
</template>

<script setup lang="ts">
/**
 * DateRangePills
 * 可复用的日期范围按钮组（7/30/90 天）。
 * - 保持与原筛选框相同的样式：
 *   wrapper:  inline-flex rounded-full overflow-hidden bg-gray-100
 *   button:   px-4 py-2 text-sm  + (active/normal 切换类)
 * - 支持 v-model（数字：7/30/90），可通过 props.options 自定义候选
 * - 可通过 props.suffix 设置标签后缀（默认 “天”）
 */

import { computed } from 'vue'

const props = withDefaults(defineProps<{
  modelValue: number
  options?: number[]
  suffix?: string
  labels?: Record<number, string>
}>(), {
  options: () => [7, 30, 90],
  suffix: '天',
  labels: () => ({})
})

const emit = defineEmits<{
  (e: 'update:modelValue', v: number): void
}>()

// 与原样式一致的激活/常态类
const activeBtn = 'bg-white text-gray-900'
const normalBtn = 'text-gray-500 hover:text-gray-700'

const resolvedOptions = computed(() => props.options?.slice() ?? [7, 30, 90])

function onPick(v: number) {
  if (v !== props.modelValue) emit('update:modelValue', v)
}

function renderLabel(v: number) {
  // 优先使用自定义 labels，其次用 `${v}天` 形式
  return props.labels?.[v] ?? `${v}${props.suffix}`
}
</script>