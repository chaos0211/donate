<template>
  <div :style="{ width: '100%', height: `${height}px` }" ref="el"></div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  labels: string[]          // x 轴日期
  values: number[]          // y 轴波动率(%)
  height?: number           // 可选高度，默认 400
}>()

const el = ref<HTMLDivElement|null>(null)
let chart: echarts.ECharts | null = null

function render() {
  if (!el.value) return
  if (!chart) chart = echarts.init(el.value)
  const option: echarts.EChartsOption = {
    tooltip:{ trigger:'axis', backgroundColor:'rgba(255,255,255,0.9)', borderColor:'#EBEEF5', borderWidth:1, padding:10,
      textStyle:{color:'#303133'}, formatter:(p:any)=>`${p[0].name}<br/>波动指数: ${p[0].value}%` },
    grid:{ left:'3%', right:'4%', bottom:'3%', containLabel:true },
    xAxis:{ type:'category', data: props.labels, axisLine:{ lineStyle:{ color:'#E4E7ED'}},
      axisLabel:{ color:'#909399', fontSize:10, interval: Math.floor(props.labels.length/10) } },
    yAxis:{ type:'value', axisLine:{show:false}, axisLabel:{ color:'#909399', formatter:'{value}%' },
      splitLine:{ lineStyle:{ color:'#F2F3F5'}},
      min: props.values.length ? Math.min(...props.values)*0.9 : 0,
      max: props.values.length ? Math.max(...props.values)*1.1 : 100 },
    series:[{
      type:'line', data: props.values, smooth:true,
      lineStyle:{ color:'#165DFF', width:2 },
      symbol:'circle', symbolSize:4,
      itemStyle:{ color:'#165DFF', borderWidth:2, borderColor:'#fff' },
      areaStyle:{ color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(22,93,255,0.2)'},{offset:1,color:'rgba(22,93,255,0)'}]) }
    }]
  }
  chart.setOption(option)
  chart.resize()
}

watch(() => [props.labels, props.values], render, { deep: true })
onMounted(() => { render(); window.addEventListener('resize', onResize) })
onBeforeUnmount(() => { window.removeEventListener('resize', onResize); chart?.dispose(); chart = null })
function onResize(){ chart?.resize() }
</script>