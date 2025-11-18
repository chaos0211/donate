<template>
  <div class="card-gradient from-cardGradientStart to-cardGradientEnd rounded-xl shadow-sm p-5 border border-gray-100 transition-all hover:shadow-md">
    <div class="flex justify-between items-start mb-3">
      <div>
        <p class="text-info text-sm">{{ subtitle }}</p>
        <h3 class="text-2xl font-bold mt-1">
          <slot name="value">
            {{ value }}
            <span v-if="valueSuffix" class="text-base font-medium ml-1">{{ valueSuffix }}</span>
          </slot>
        </h3>
      </div>
      <div class="w-10 h-10 rounded-full flex items-center justify-center" :class="iconBgClass">
        <i :class="iconClass"></i>
      </div>
    </div>

    <!-- 趋势行（可选） -->
    <div v-if="trend !== undefined" class="flex items-center">
      <span :class="trendClass" class="text-sm font-medium flex items-center">
        <i :class="trendIcon" class="mr-1"></i>
        {{ trend }}
      </span>
      <span class="text-info text-xs ml-2">vs 上一周期</span>
    </div>

    <!-- 进度条（可选，用于 Top 类目占比） -->
    <div v-if="progress !== undefined" class="w-full bg-gray-200 rounded-full h-2 mt-3">
      <div class="h-2 rounded-full" :style="{ width: progress + '%', backgroundColor: progressColor }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
const props = withDefaults(defineProps<{
  subtitle: string
  value?: string | number
  valueSuffix?: string
  iconClass?: string        // 如 'fas fa-arrow-circle-up text-primary'
  iconBgClass?: string      // 如 'bg-primary/10 text-primary'
  trend?: string            // '12.5%' / '8.3%' 等
  trendType?: 'up' | 'down' // 控制颜色与箭头
  progress?: number         // 百分比（0-100）
  progressColor?: string    // 自定义颜色，默认 '#F7BA1E'（warning）
}>(), {
  valueSuffix: '',
  iconClass: 'fas fa-chart-line text-secondary',
  iconBgClass: 'bg-secondary/10 text-secondary',
  trendType: 'up',
  progressColor: '#F7BA1E'
})

const trendClass = computed(() =>
  props.trendType === 'up' ? 'text-success' : 'text-danger'
)
const trendIcon = computed(() =>
  props.trendType === 'up' ? 'fas fa-arrow-up' : 'fas fa-arrow-down'
)
</script>

<style scoped>
.card-gradient { background: linear-gradient(135deg, var(--tw-gradient-stops)); }
</style>