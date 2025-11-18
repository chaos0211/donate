<template>
  <div class="w-full">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-base font-medium">特征重要性热力图</h3>
      <div class="text-sm text-info">对预测模型的影响权重</div>
    </div>

    <div v-if="loading" class="chart-container flex items-center justify-center text-info">加载中...</div>
    <div v-else-if="!hasData" class="chart-container flex items-center justify-center text-info">暂无数据</div>
    <div v-else ref="chartEl" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { getFeatureImportance } from '@/api/analytics'

const props = defineProps<{
  days: number
  brandId: number
  country: string
  device: string
}>()

const chartEl = ref<HTMLDivElement|null>(null)
let chart: echarts.ECharts | null = null

const loading = ref(false)
const hasData = ref(false)
let features: string[] = []
let scores: number[] = []

async function fetchData() {
  loading.value = true
  hasData.value = false
  try {
    const data = await getFeatureImportance({
      days: props.days,
      brand_id: props.brandId,
      country: props.country,
      device: props.device
    })
    features = Array.isArray(data?.features) ? data.features : []
    scores   = Array.isArray(data?.scores)   ? data.scores   : []
    hasData.value = features.length > 0 && scores.length > 0
  } finally {
    loading.value = false
  }
}

function render() {
  if (!chartEl.value) return
  const existed = echarts.getInstanceByDom(chartEl.value)
  chart = existed || echarts.init(chartEl.value)

  const seriesData = features.map((f, i) => [0, i, Number(scores[i] ?? 0)])

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255,255,255,0.9)',
      borderColor: '#EBEEF5',
      borderWidth: 1,
      padding: 10,
      textStyle: { color: '#303133' },
      formatter: (p: any) => `${features[p.data[1]]}<br/>重要性权重: ${p.data[2]}`
    },
    grid: { left: '12%', right: '4%', bottom: '12%', containLabel: true },
    xAxis: { type: 'category', data: ['重要性权重'], axisLine: { show: false }, axisLabel: { show: false }, splitLine: { show: false } },
    yAxis: { type: 'category', data: features, axisLine: { show: false }, axisLabel: { color: '#909399' }, splitLine: { show: false } },
    visualMap: { min: 0, max: 1, calculable: true, orient: 'horizontal', left: 'center', bottom: 0, textStyle: { color: '#909399' }, inRange: { color: ['#E0F2FF', '#165DFF'] } },
    series: [
      {
        name: '特征重要性',
        type: 'heatmap',
        data: seriesData,
        label: { show: true, color: '#303133', formatter: (p: any) => p.data[2] },
        itemStyle: { borderRadius: 4 }
      }
    ]
  }

  chart.clear()
  chart.setOption(option)
  chart.resize()
}

async function refresh() {
  await fetchData()
  if (hasData.value) render()
}

function handleResize() { chart?.resize() }

watch(() => [props.days, props.brandId, props.country, props.device], () => {
  refresh()
}, { immediate: true, deep: false })

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.chart-container { width: 100%; height: 300px; }
@media (min-width: 768px){ .chart-container { height: 350px; } }
@media (min-width: 1024px){ .chart-container { height: 400px; } }
</style>