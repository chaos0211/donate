<template>
  <div class="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-base font-medium">{{ title }}</h3>
      <div class="text-sm text-info">按日统计</div>
    </div>
    <div class="relative w-full" style="height:360px">
      <!-- 图表容器始终存在，防止 ref 不可用导致不发起请求 -->
      <div ref="el" class="absolute inset-0 w-full h-full"></div>
      <!-- 覆盖层：加载中/暂无数据 -->
      <div v-if="loading" class="absolute inset-0 flex items-center justify-center text-info bg-white/30">加载中...</div>
      <div v-else-if="!hasData" class="absolute inset-0 flex items-center justify-center text-gray-400 bg-white/30">暂无数据</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getGenreTrend } from '@/api/analytics'

interface Props {
  title?: string
  days: number
  brandId: number
  country: string
  device: string
  genre: string  // 中文或 'all'
  visible?: boolean
}
const props = withDefaults(defineProps<Props>(), { title: '类别热度趋势' })

const el = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
const loading = ref(false)
const hasData = ref(false)

let retryTimer: number | any = null

async function ensureInitAndResize(){
  await nextTick()
  if(!el.value) return
  if(!chart){
    chart = echarts.init(el.value)
  }
  chart.resize()
}

async function fetchAndRender(){
  if (loading.value) return
  loading.value = true
  try {
    await nextTick()
    // 确保容器已挂载
    if (!el.value) {
      await nextTick()
    }
    // 初始化并自适应
    await ensureInitAndResize()

    // 如果容器尺寸仍为 0，稍后重试（先释放 loading，避免死循环）
    if (!el.value || el.value.clientWidth === 0 || el.value.clientHeight === 0) {
      loading.value = false
      clearTimeout(retryTimer)
      retryTimer = setTimeout(fetchAndRender, 200)
      return
    }

    const dataResp = await getGenreTrend({
      days: props.days,
      brand_id: props.brandId,
      country: props.country,
      device: props.device,
      genre: props.genre,
    })

    const labels = dataResp?.labels ?? []
    const appCount = dataResp?.app_count ?? []
    const avgRank  = dataResp?.avg_rank  ?? []

    hasData.value = Array.isArray(labels) && labels.length > 0 && (
      (Array.isArray(appCount) && appCount.some(v => v != null)) ||
      (Array.isArray(avgRank) && avgRank.some(v => v != null))
    )

    const maxAvg = Array.isArray(avgRank) && avgRank.length ? Math.max(...avgRank) : 0
    const isRatingScale = maxAvg > 0 && maxAvg <= 5.5

    if (!chart) chart = echarts.init(el.value as HTMLDivElement)
    if (!hasData.value) {
      chart.clear()
      return
    }

    const option: echarts.EChartsOption = {
      tooltip:{
        trigger:'axis',
        backgroundColor:'rgba(255,255,255,0.9)',
        borderColor:'#EBEEF5', borderWidth:1, padding:10,
        textStyle:{color:'#303133'},
        valueFormatter: (v:any)=>{
          if(v == null) return ''
          return typeof v === 'number' ? (isRatingScale ? v.toFixed(2) : v) : v
        }
      },
      legend:{ data:['应用数量','平均排名'], textStyle:{ color:'#606266' }, top:0 },
      grid:{ left:'3%', right:'4%', bottom:'3%', containLabel:true, top:'15%' },
      xAxis:{ type:'category', data:labels, axisLine:{ lineStyle:{ color:'#E4E7ED'}}, axisLabel:{ color:'#909399', fontSize:10, interval: Math.floor((labels.length||1)/10) } },
      yAxis:[
        { type:'value', name:'应用数量', nameTextStyle:{ color:'#165DFF'}, axisLine:{show:false}, axisLabel:{ color:'#909399'}, splitLine:{ lineStyle:{ color:'#F2F3F5'}} },
        {
          type:'value',
          name: '平均排名',
          nameTextStyle:{ color:'#F53F3F'},
          axisLine:{show:false},
          axisLabel:{ color:'#909399' },
          splitLine:{ show:false },
          // 评分固定 0~5；排名默认 1~100（或按数据上限+一个余量）
          min: isRatingScale ? 0 : 1,
          max: isRatingScale ? 5 : Math.max(100, Math.ceil(maxAvg/10)*10),
          inverse: isRatingScale ? false : true
        }
      ],
      series:[
        { name:'应用数量', type:'line', data:appCount, smooth:true, lineStyle:{ color:'#165DFF', width:2 }, symbol:'circle', symbolSize:4, itemStyle:{ color:'#165DFF', borderWidth:2, borderColor:'#fff' }, areaStyle:{ color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(22,93,255,0.2)'},{offset:1,color:'rgba(22,93,255,0)'}]) } },
        { name:'平均排名', type:'line', data:avgRank,  smooth:true, yAxisIndex:1, lineStyle:{ color:'#F53F3F', width:2 }, symbol:'circle', symbolSize:4, itemStyle:{ color:'#F53F3F', borderWidth:2, borderColor:'#fff' }, areaStyle:{ color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(245,63,63,0.2)'},{offset:1,color:'rgba(245,63,63,0)'}]) } }
      ]
    }
    chart.clear()
    chart.setOption(option)
    await nextTick()
    chart.resize()
  } finally {
    loading.value = false
  }
}

function handleResize(){ ensureInitAndResize() }

watch(
  () => [props.days, props.brandId, props.country, props.device, props.genre, props.visible],
  () => { fetchAndRender() },
  { immediate: true }
)

onMounted(()=>{ window.addEventListener('resize', handleResize) })
onBeforeUnmount(()=>{ window.removeEventListener('resize', handleResize); chart?.dispose(); chart=null })
</script>