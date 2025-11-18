<template>
  <div class="bg-white rounded-xl shadow-card p-6 card-hover">
    <div class="flex items-start justify-between">
      <div>
        <!-- 标题：在页面里用 <template #title> 写死，这里只是展示 -->
        <p class="text-gray-500 text-sm font-medium">
          <slot name="title"></slot>
        </p>

        <!-- 值：由父组件传入，空/null/'' 时显示 0 -->
        <h3 class="text-2xl font-bold mt-1">
          {{ displayValue }}
        </h3>

        <!-- 趋势文字：可选，由父组件传入 -->
        <p
          v-if="trendText"
          :class="trendUp ? 'text-success' : 'text-danger'"
          class="text-sm mt-2 flex items-center"
        >
          <i :class="[trendUp ? 'fas fa-arrow-up' : 'fas fa-arrow-down', 'mr-1']"></i>
          <span>{{ trendText }}</span>
        </p>
      </div>

      <!-- 右侧图标 -->
      <div
        class="w-12 h-12 rounded-full flex items-center justify-center"
        :class="iconBg"
      >
        <i :class="[icon, 'text-xl']"></i>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    value?: number | string | null
    trendText?: string
    trendUp?: boolean
    icon?: string
    iconBg?: string
  }>(),
  {
    value: 0,
    trendText: '',
    trendUp: true,
    icon: 'fas fa-circle',
    iconBg: 'bg-gray-100 text-gray-500'
  }
)

// 值为空时显示 0
const displayValue = computed(() => {
  if (props.value === null || props.value === undefined || props.value === '') {
    return 0
  }
  return props.value
})

const trendText = computed(() => props.trendText)
const trendUp = computed(() => props.trendUp)
const icon = computed(() => props.icon)
const iconBg = computed(() => props.iconBg)
</script>