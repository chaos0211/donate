<template>
  <div>
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-base font-medium">{{ title }}</h3>
      <div class="text-sm text-primary cursor-pointer hover:underline" @click="$emit('viewAll')">查看全部</div>
    </div>

    <div v-if="loading" class="h-[180px] flex items-center justify-center text-info">加载中...</div>
    <div v-else>
      <div v-if="items.length === 0" class="text-info text-sm py-8 text-center">暂无数据</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-200">
              <th class="text-left py-3 px-2 font-medium text-info">排名</th>
              <th class="text-left py-3 px-2 font-medium text-info">应用名称</th>
              <th class="text-left py-3 px-2 font-medium text-info">发行商</th>
              <th v-if="order==='stable'" class="text-left py-3 px-2 font-medium text-info">平均排名</th>
              <th v-else class="text-left py-3 px-2 font-medium text-info">标准差</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in items" :key="row.app_id || idx" class="border-b border-gray-100 hover:bg-gray-50 transition-colors">
              <td class="py-3 px-2 font-medium">{{ idx + 1 }}</td>
              <td class="py-3 px-2 whitespace-nowrap overflow-hidden text-ellipsis max-w-[220px]">{{ row.app_name }}</td>
              <td class="py-3 px-2 whitespace-nowrap overflow-hidden text-ellipsis max-w-[180px] text-info">{{ row.publisher || '-' }}</td>
              <td v-if="order==='stable'" class="py-3 px-2 text-success">{{ formatNumber(row.avg_rank) }}</td>
              <td v-else class="py-3 px-2 text-danger">{{ formatNumber(row.stddev) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { getStableTop10, getVolatileTop10 } from '@/api/analytics'

interface Props {
  title: string
  order: 'stable' | 'volatile'
  days: number
  brandId: number
  country: string
  device: string
  limit?: number
  minPresence?: number
}
const props = withDefaults(defineProps<Props>(), { limit: 10 })

const loading = ref(false)
const items = ref<any[]>([])

function formatNumber(n: number | null | undefined) {
  if (n === null || n === undefined) return '-'
  const num = Number(n)
  return isNaN(num) ? '-' : num.toFixed(2)
}

async function fetchData(){
  loading.value = true
  try {
    const params = {
      days: props.days,
      brand_id: props.brandId,
      country: props.country,
      device: props.device,
      limit: props.limit,
      min_presence: props.minPresence,
    }
    const data = props.order === 'stable'
      ? await getStableTop10(params)
      : await getVolatileTop10(params)

    items.value = Array.isArray(data?.items) ? data.items : []
  } finally {
    loading.value = false
  }
}

watch(() => [props.days, props.brandId, props.country, props.device, props.limit, props.minPresence, props.order], fetchData, { immediate: true })
</script>

<style scoped>
/* 复用全局表格样式，这里不做强覆盖 */
</style>