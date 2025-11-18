<template>
  <!-- 固定一个可见高度，避免高度为 0 导致看不到图 -->
  <div ref="el" class="w-full" style="height:360px"></div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { getGenreGrowth } from '@/api/analytics'

interface Props {
  days: number
  brandId: number
  country: string
  device: string
  genre?: string       // 'all' 或中文类目
  visible?: boolean    // 父级 v-show 控制时传入
}
const props = defineProps<Props>()

const el = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

const genreParam = computed(() => (props.genre && props.genre !== 'all') ? props.genre : 'all')

async function fetchAndRender () {
  await nextTick()
  if (!el.value) return

  if (!chart) {
    // 容器有宽高后再 init
    if (el.value.clientWidth === 0 || el.value.clientHeight === 0) return
    chart = echarts.init(el.value)
  }

  // --- 拉后端数据（兼容两种返回形态） ---
  const resp = await getGenreGrowth({
    days: props.days,
    brand_id: props.brandId,
    country: props.country,
    device: props.device,
    genre: genreParam.value
  })
  const items = Array.isArray(resp) ? resp : (resp?.items ?? [])

  const categories = items.map((d: any) => d.genre ?? '')
  const values = items.map((d: any) => Number(d.growth ?? 0))

  const option: echarts.EChartsOption = {
    grid: { left: '6%', right: '4%', top: 20, bottom: 30, containLabel: true },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: categories, axisLabel: { color: '#909399' } },
    yAxis: { type: 'value', axisLabel: { color: '#909399', formatter: '{value}%' } },
    series: [{
      type: 'bar',
      data: values,
      barWidth: '50%',
      itemStyle: { borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: 'top', formatter: ({ value }: any) => `${value}%` }
    }]
  }

  chart.clear()
  chart.setOption(option)
}

function resize () {
  if (chart) chart.resize()
}

watch(
  () => [props.days, props.brandId, props.country, props.device, props.genre, props.visible],
  async () => {
    await fetchAndRender()
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  if (chart) { chart.dispose(); chart = null }
  if (typeof window !== 'undefined') window.removeEventListener('resize', resize)
})

if (typeof window !== 'undefined') window.addEventListener('resize', resize)
</script>