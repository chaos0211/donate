<template>
  <div class="bg-gray-50 font-inter text-gray-800 min-h-screen">
    <!-- 页面容器 -->
    <div class="container mx-auto px-4 py-6 max-w-7xl">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-[clamp(1.5rem,3vw,2.5rem)] font-bold text-gray-800 mb-2">
          应用榜单数据分析
        </h1>
        <p class="text-gray-500">预测应用在榜单中的未来表现趋势与排名变化</p>
      </div>

      <!-- 筛选区（已拆分为可复用组件） -->
      <FilterBox
        v-model:dateRange="state.dateRange"
        v-model:country="state.country"
        v-model:device="state.device"
        v-model:chartType="state.chartType"
        v-model:category="state.category"
        v-model:selectedApps="state.selectedApps"
      />

      <!-- 模型管理与上传 -->
      <div class="bg-white rounded-xl shadow-sm p-5 mb-8 transition-all duration-300 hover:shadow-md">
        <div class="flex flex-wrap items-center gap-4">
          <!-- 选择模型类型 -->
          <div>
            <label class="block text-sm text-gray-500 mb-1">模型类型</label>
            <select v-model="state.modelType" class="border rounded px-3 py-2 text-sm">
              <option value="lstm">LSTM</option>
              <option>随机森林</option>
            </select>
          </div>

          <!-- 选择本地可用模型文件 -->
          <div class="min-w-[280px]">
            <label class="block text-sm text-gray-500 mb-1">本地模型文件（.pt）</label>
            <select v-model="state.selectedModel" class="border rounded px-3 py-2 text-sm w-full">
              <option v-if="modelFiles.length===0" disabled value="">无</option>
              <option v-for="m in modelFiles" :key="m" :value="m">{{ m }}</option>
            </select>
          </div>

          <!-- 上传模型文件（.pt） -->
          <div>
            <label class="block text-sm text-gray-500 mb-1">上传模型（.pt）</label>
            <input ref="fileInputRef" type="file" accept=".pt" @change="onUploadModel($event)" class="hidden" />
            <button @click="() => fileInputRef?.click()" class="px-3 py-2 text-sm rounded bg-gray-100 hover:bg-gray-200">选择文件</button>
            <div class="text-sm inline-block ml-3 align-middle" :class="uploadedFileName ? 'text-gray-700' : 'text-gray-400'">
              {{ uploadedFileName ? uploadedFileName : '未选择任何文件' }}
            </div>
            <p v-if="uploadMsg" class="text-xs mt-1" :class="uploadOk ? 'text-green-600' : 'text-red-600'">{{ uploadMsg }}</p>
          </div>

          <!-- 刷新列表按钮 -->
          <div class="mt-6">
            <button @click="() => refreshModelFiles(true)" class="px-3 py-2 text-sm rounded bg-gray-100 hover:bg-gray-200">刷新模型列表</button>
          </div>
        </div>
      </div>

      <!-- 核心预测结果区：趋势 + TopN -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- 预测趋势图 -->
        <div class="lg-col-span-2 bg-white rounded-xl shadow-sm p-5 transition-all duration-300 hover:shadow-md">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-lg font-semibold text-gray-800">
              预测趋势图
              <span class="text-sm font-normal text-gray-500 ml-2">（未来{{ state.dateRange }}天）</span>
            </h2>
            <div class="flex space-x-2">
              <button class="p-2 rounded hover:bg-gray-100 text-gray-600 transition-colors" @click="downloadTrend">
                <i class="fas fa-download"></i>
              </button>
              <button class="p-2 rounded hover:bg-gray-100 text-gray-600 transition-colors" @click="fullscreenTrend">
                <i class="fas fa-expand"></i>
              </button>
            </div>
          </div>
          <div ref="trendRef" class="w-full h-[400px] bg-gray-50 rounded-lg p-2"></div>
        </div>

        <!-- 预测Top10榜单 -->
        <div class="bg-white rounded-xl shadow-sm p-5 transition-all duration-300 hover:shadow-md card-hover">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-lg font-semibold text-gray-800">
              预测Top10榜单
              <span v-if="topNBrand" class="text-sm font-normal text-gray-500 ml-2">（{{ topNBrand }}榜）</span>
            </h2>
            <div class="flex items-center space-x-3">
              <DateRangePills v-model="topNRange" />
            </div>
          </div>
          <div class="overflow-x-auto rounded-lg border border-gray-100">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider rounded-tl-lg w-16">排名</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">应用信息</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">发行商</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider rounded-tr-lg">排名变化</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr
                  v-for="item in topNRows"
                  :key="item.rank"
                  class="hover:bg-gray-50 transition-colors"
                >
                  <td class="px-3 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div
                        class="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-full"
                        :class="item.rank<=3 ? 'bg-primary text-white font-bold' : 'bg-gray-100 text-gray-600'"
                      >
                        {{ item.rank }}
                      </div>
                    </div>
                  </td>
                  <td class="px-3 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="flex-shrink-0 h-10 w-10">
                        <img :src="item.icon" :alt="item.appName" class="h-10 w-10 rounded object-cover" />
                      </div>
                      <div class="ml-3">
                        <div class="text-sm font-medium text-gray-900" :title="item.appName">{{ truncate4(item.appName) }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-3 py-4 whitespace-nowrap text-sm text-gray-500" :title="item.publisher">
                      {{ truncate4(item.publisher) }}
                  </td>
                  <td class="px-3 py-4 whitespace-nowrap">
                    <div
                      class="text-sm flex items-center"
                      :class="item.change>0 ? 'text-success' : item.change<0 ? 'text-danger' : 'text-gray-500'"
                    >
                      <i :class="item.change>0 ? 'fas fa-arrow-up mr-1' : item.change<0 ? 'fas fa-arrow-down mr-1' : 'fas fa-minus mr-1'"></i>
                      {{ Math.abs(item.change) }} ({{ item.changePercent }}%)
                    </div>
                  </td>
                </tr>
                <tr v-if="!topNRows.length">
                  <td colspan="4" class="px-4 py-6 text-center text-gray-400">暂无数据</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 模型评估区域（与原 HTML 一致的 4 卡 + 历史准确率趋势） -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <!-- MAE -->
          <div class="bg-white rounded-xl shadow-sm p-5 transition-all duration-300 hover:shadow-md card-hover">
            <div class="flex items-start">
              <div class="flex-shrink-0 bg-blue-50 p-3 rounded-lg">
                <i class="fas fa-crosshairs text-primary text-xl"></i>
              </div>
              <div class="ml-4">
                <h3 class="text-sm font-medium text-gray-500">平均绝对误差 (MAE)</h3>
                <p class="mt-1 text-2xl font-semibold text-gray-900">{{ kpi.mae }}</p>
                <p class="mt-1 text-xs text-success flex items-center">
                  <i class="fas fa-arrow-down mr-1"></i>较上期降低12.3%
                </p>
              </div>
            </div>
          </div>
          <!-- RMSE -->
          <div class="bg-white rounded-xl shadow-sm p-5 transition-all duration-300 hover:shadow-md card-hover">
            <div class="flex items-start">
              <div class="flex-shrink-0 bg-purple-50 p-3 rounded-lg">
                <i class="fas fa-square-root-alt text-purple-600 text-xl"></i>
              </div>
              <div class="ml-4">
                <h3 class="text-sm font-medium text-gray-500">均方根误差 (RMSE)</h3>
                <p class="mt-1 text-2xl font-semibold text-gray-900">{{ kpi.rmse }}</p>
                <p class="mt-1 text-xs text-success flex items-center">
                  <i class="fas fa-arrow-down mr-1"></i>较上期降低8.7%
                </p>
              </div>
            </div>
          </div>
          <!-- 置信区间 -->
          <div class="bg-white rounded-xl shadow-sm p-5 transition-all duration-300 hover:shadow-md card-hover">
            <div class="flex items-start">
              <div class="flex-shrink-0 bg-green-50 p-3 rounded-lg">
                <i class="fas fa-check-circle text-green-600 text-xl"></i>
              </div>
              <div class="ml-4">
                <h3 class="text-sm font-medium text-gray-500">95%置信区间</h3>
                <p class="mt-1 text-2xl font-semibold text-gray-900">±{{ kpi.ci }}排名</p>
                <p class="mt-1 text-xs text-gray-500">覆盖95%的预测结果</p>
              </div>
            </div>
          </div>
          <!-- 准确率 -->
          <div class="bg-white rounded-xl shadow-sm p-5 transition-all duration-300 hover:shadow-md card-hover">
            <div class="flex items-start">
              <div class="flex-shrink-0 bg-amber-50 p-3 rounded-lg">
                <i class="fas fa-chart-pie text-amber-600 text-xl"></i>
              </div>
              <div class="ml-4">
                <h3 class="text-sm font-medium text-gray-500">预测准确率</h3>
                <p class="mt-1 text-2xl font-semibold text-gray-900">
                  {{ kpi.acc }}<span class="text-lg">%</span>
                </p>
                <p class="mt-1 text-xs text-success flex items-center">
                  <i class="fas fa-arrow-up mr-1"></i>较上期提升2.1%
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- 历史预测准确率趋势 -->
        <div class="bg-white rounded-xl shadow-sm p-5 transition-all duration-300 hover:shadow-md card-hover">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-lg font-semibold text-gray-800">历史预测准确率趋势</h2>
            <div class="flex space-x-2">
              <button class="p-2 rounded hover:bg-gray-100 text-gray-600 transition-colors" @click="downloadAccuracy">
                <i class="fas fa-download"></i>
              </button>
            </div>
          </div>
          <div ref="accuracyRef" class="w-full h-[300px] bg-gray-50 rounded-lg p-2"></div>
        </div>
      </div>
    </div>

    <!-- 加载遮罩 -->
    <div
      id="loading-overlay"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      :class="state.isLoading ? '' : 'hidden'"
    >
      <div class="bg-white rounded-lg p-8 max-w-md w-full mx-4">
        <div class="flex flex-col items-center">
          <div class="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
          <h3 class="text-lg font-medium text-gray-800 mb-2">数据处理中</h3>
          <p class="text-gray-500 text-center">{{ loadingMessage }}</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
// 说明：本 SFC 严格保留了原 HTML 的样式与布局（Tailwind 类名未变），逻辑基于原生脚本等价迁移。
// 后续你可把 mock 数据替换为真实后端接口。

import * as echarts from 'echarts'
import { onMounted, onBeforeUnmount, reactive, ref, watch, computed } from 'vue'
import FilterBox from "@/components/charts/filter_box.vue";
import DateRangePills from '@/components/common/DateRangePills.vue'


// lodash.debounce 可替换为下方简单实现
function debounce<T extends (...args:any[])=>any>(fn:T, wait=400){
  let timer:ReturnType<typeof setTimeout>|null=null
  return function(this:unknown, ...args:Parameters<T>){
    if(timer) clearTimeout(timer)
    timer = setTimeout(()=>fn.apply(this,args), wait)
  }
}

function truncate4(s: string){
  if(!s) return ''
  const chars = Array.from(s)
  const head = chars.slice(0, 4).join('')
  return chars.length > 4 ? head + '…' : head
}

function formatMD(d: Date){
  return `${d.getMonth()+1}/${d.getDate()}`
}
function addDays(base: Date, n: number){
  const d = new Date(base)
  d.setDate(d.getDate()+n)
  return d
}

function fmtDate(d: Date){
  const m = String(d.getMonth()+1).padStart(2,'0')
  const day = String(d.getDate()).padStart(2,'0')
  return `${d.getFullYear()}-${m}-${day}`
}

// ——— 状态 ———
const state = reactive({
  dateRange: 7 as 7|30|90,
  country: '' as string,
  device: 'iphone' as 'iphone'|'ipad'|'android',
  chartType: 'free' as 'free'|'paid'|'grossing',
  category: 'all' as string,
  selectedApps: [] as string[],
  isLoading: false,
  modelType: 'lstm' as 'lstm',
  selectedModel: '' as string,
})

const modelFiles = ref<string[]>([])
const uploadMsg = ref('')
const uploadOk = ref(false)
const fileInputRef = ref<HTMLInputElement|null>(null)
const uploadedFileName = ref('')
const topNDate = ref<string>('') // 空表示后端默认(最新+1天)
const topNRange = ref<7|30|90>(7)
// ——— 后端 API 辅助 ———
const API_BASE = 'http://127.0.0.1:8000' // 开发环境直连后端端口，生产可改为 '' 并使用反向代理

async function listModels(algo: 'lstm'): Promise<string[]> {
  try{
    const resp = await fetch(`${API_BASE}/api/v1/predict/models?algo=${algo}`)
    if(!resp.ok) throw new Error(await resp.text())
    const data = await resp.json()
    // 只使用后端返回的 trained 目录文件
    const files = (data && data.groups && Array.isArray(data.groups.trained))
      ? data.groups.trained
      : (Array.isArray(data.files) ? data.files : [])
    return files
  }catch(e){
    console.warn('listModels failed', e)
    return []
  }
}

async function uploadModel(algo: 'lstm', file: File){
  const fd = new FormData()
  fd.append('file', file)
  try{
    const resp = await fetch(`${API_BASE}/api/v1/predict/models/upload?algo=${algo}`, { method:'POST', body: fd })
    if(!resp.ok){
      const t = await resp.text(); throw new Error(t)
    }
    return await resp.json()
  }catch(e){
    throw e
  }
}

async function postForecast(appId: string, country: string, device: string, brand: string, lookback: number, horizon: number, modelName?: string){
  const body:any = { app_id: appId, country, device, brand, lookback, horizon }
  // 模型来源与文件名：优先上传模型
  const sel = getSelectedModel()
  body.model_source = sel.source
  if (sel.name) body.model_name = sel.name
  // 细分类（rank_c.genre）：当筛选为具体分类时传入，"all" 则省略让后端自动推断
  const genre = state.category && state.category !== 'all' ? state.category : undefined
  if (genre) body.genre = genre

  const resp = await fetch(`${API_BASE}/api/v1/predict/forecast_global`, {
    method:'POST', headers:{ 'Content-Type':'application/json' }, body: JSON.stringify(body)
  })
  if(!resp.ok) throw new Error(await resp.text())
  return await resp.json() as { predictions: number[] }
}

// TopN预测API
async function fetchTopNPredict(modelName: string, n=10, lookback=30, horizon=1, modelSource: 'upload'|'trained'='trained', target?: string){
  const url = new URL(`${API_BASE}/api/v1/predict/topn/predict`)
  url.searchParams.set('model_name', modelName)
  url.searchParams.set('model_source', modelSource)
  url.searchParams.set('n', String(n))
  url.searchParams.set('lookback', String(lookback))
  url.searchParams.set('horizon', String(horizon))
  if (target) url.searchParams.set('target', target)
  const resp = await fetch(url.toString())
  if(!resp.ok) throw new Error(await resp.text())
  return await resp.json() as { items: Array<{rank:number, app_id:string, app_name:string, publisher:string, icon_url:string, change:number|null, change_percent:number|null}> }
}

function getSelectedModel(){
  // 有上传文件则优先，来源为 upload；否则来源为 trained，并使用下拉选择的文件
  if (uploadedFileName.value){
    return { source: 'upload' as const, name: uploadedFileName.value }
  }
  if (state.selectedModel){
    return { source: 'trained' as const, name: state.selectedModel }
  }
  return { source: 'trained' as const, name: '' }
}

// ——— 模型上传与管理相关 UI 逻辑 ———
async function refreshModelFiles(reset = false){
  // 仅当用户点击“刷新模型列表”按钮时重置上传文件名
  if (reset) uploadedFileName.value = ''
  modelFiles.value = await listModels(state.modelType)
  if(modelFiles.value.length === 0){
    state.selectedModel = ''
    return
  }
  if(!state.selectedModel || !modelFiles.value.includes(state.selectedModel)){
    state.selectedModel = modelFiles.value[0]
  }
}

async function onUploadModel(ev: Event){
  const input = ev.target as HTMLInputElement
  const file = input?.files?.[0]
  if(!file){ return }
  uploadMsg.value = '正在上传...'; uploadOk.value = false
  try{
    const res:any = await uploadModel(state.modelType, file)
    const saved = res?.saved_as || file.name
    uploadedFileName.value = saved        // 用文件名替代“未选择任何文件”
    uploadMsg.value = ''                  // 不再显示“上传成功”提示
    uploadOk.value = true
    await refreshModelFiles(false)        // 刷新列表但不清空上传文件名
    // 业务规则：上传成功仅在按钮下方显示文件名，不加入下拉框
  }catch(e:any){
    uploadMsg.value = '上传失败：' + (e?.message || e)
    uploadOk.value = false
  }finally{
    // 清空 input，便于连续上传同名文件
    if(fileInputRef.value) fileInputRef.value.value = ''
  }
}
// 榜单类型映射（显示值 -> 后端参数）
const rankGroupMap = {
  free: 'rank_a',
  paid: 'rank_b',
  grossing: 'rank_c'
}

// 统一过滤参数对象（组合所有筛选项）
const filters = computed(() => {
  const group = rankGroupMap[state.chartType] ?? state.chartType
  return {
    dateRange: state.dateRange,
    country: state.country,
    device: state.device,
    rankGroup: group,
    genre: state.category || null,  // 总是把选择的分类传给后端；后端按 rankGroup 到 rank_a/rank_b/rank_c 的 JSON 里取 $.genre 进行过滤
    category: state.category,
    chartType: state.chartType
  }
})

const loadingMessage = ref('加载中...')

// ——— 模拟数据（保留原始逻辑） ———
const COLORS = ['#165DFF','#722ED1','#F53F3F','#FF7D00','#0FC6C2','#86909C','#00B42A','#F7BA1E','#8E44AD','#3498DB']

// 趋势图 mock
function generateMockTrendData(appIds: string[], days=7){
  const data:any[] = []
  const today = new Date()
  const dates:string[] = []
  for(let i=0;i<days;i++){
    const d = new Date(today)
    d.setDate(today.getDate()+i+1)
    dates.push(d.toLocaleDateString('zh-CN',{month:'numeric', day:'numeric'}))
  }
  appIds.forEach((id, idx)=>{
    const baseRank = Math.floor(Math.random()*50)+1
    const ranks:number[] = []
    for(let i=0;i<days;i++){
      const fluct = Math.floor(Math.random()*10)-5
      let rank = baseRank + fluct + (i * (Math.random()>0.5?1:-1) * Math.random()*3)
      rank = Math.max(1, Math.round(rank))
      ranks.push(rank)
    }
    data.push({
      name: id,
      appId: id,
      type: 'line',
      data: ranks,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { width:2, color: COLORS[idx%COLORS.length] },
      itemStyle: { color: COLORS[idx%COLORS.length] },
      emphasis: { focus:'series' },
      markPoint: { data: [{type:'max', name:'最高排名'},{type:'min', name:'最低排名'}] }
    })
  })
  return { dates, series:data }
}

function generateMockTopNData(days=7, appIds: string[] = []){
  // 说明：
  // - 用当前已选择的应用 ID 或自动生成占位应用名称来构建 TopN 列表。
  const baseList = (appIds && appIds.length > 0)
    ? [...appIds]
    : Array.from({ length: 10 }, (_v, i) => `App ${i + 1}`)

  const topN:any[] = []
  baseList.slice(0, 10).forEach((id, idx) => {
    const rank = idx + 1
    const prevRank = Math.max(1, rank + Math.floor(Math.random() * 10) - 5)
    const change = prevRank - rank
    const changePercent = Math.round(Math.abs(change) / prevRank * 100)

    topN.push({
      rank,
      appName: String(id),
      publisher: '',
      appId: String(id),
      icon: '',
      prevRank,
      change,
      changePercent
    })
  })
  return topN
}

// 历史准确率 mock
function generateMockAccuracyData(){
  const months = ['1月','2月','3月','4月','5月','6月']
  const acc = months.map(()=> 75 + Math.random()*15)
  return { months, accuracy: acc.map(a=> Math.round(a*10)/10) }
}


// ——— 图表实例 ———
const trendRef = ref<HTMLDivElement|null>(null)
const accuracyRef = ref<HTMLDivElement|null>(null)
let trendChart: echarts.ECharts | null = null
let accuracyChart: echarts.ECharts | null = null

// KPI 演示数据
const kpi = reactive({ mae:'3.78', rmse:'5.24', ci:'4.6', acc:'89.3' })

// TopN 表
const topNRows = ref<any[]>([])
const topNBrand = ref<string>('')

// ——— 动作 ———
function setDateRange(d:7|30|90){ state.dateRange = d }

function onReset(){
  state.selectedApps = []
  // 重置筛选
  state.dateRange = 7
  state.device = 'iphone'
  state.chartType = 'free'
  state.category = 'all'
  state.country = ''
  // 主动刷新
  reloadAll()
}

function onAnalyze(){
  if (!state.selectedApps.length) {
    alert('请至少选择一个应用进行分析'); return
  }
  // 分析时可刷新
  showLoading('正在分析数据并生成预测结果...')
  setTimeout(()=>{
    reloadAll()
    hideLoading()
  }, 600)
}

function downloadTrend(){ if(trendChart) trendChart.dispatchAction({type:'takeGlobalCursor'}) }
function fullscreenTrend(){ if(trendChart) trendChart.resize() }
function downloadTopN(){ /* 可扩展导出 */ }
function downloadAccuracy(){ if(accuracyChart) accuracyChart.resize() }

function showLoading(msg='加载中...'){ state.isLoading = true; loadingMessage.value = msg }
function hideLoading(){ state.isLoading = false }

// ——— 渲染图表 ———
function renderTrendChart(){
  if (!trendChart || !trendRef.value) return
  if (state.selectedApps.length===0){
    trendChart.setOption({
      title:{ text:'请选择应用进行分析', left:'center', top:'center', textStyle:{ color:'#9CA3AF', fontSize:16 }},
      tooltip:{ trigger:'axis', axisPointer:{ type:'cross' } },
      grid:{ left:'3%', right:'4%', bottom:'3%', containLabel:true },
      xAxis:{ type:'category', data:[] },
      yAxis:{ type:'value', inverse:true, min:1, axisLabel:{ formatter:'{value}' } },
      series:[]
    }, true)
    return
  }
  // 数据已由 loadTrend 设置
  if (!trendChartOptionCache) return
  trendChart.setOption(trendChartOptionCache, true)
}

function renderTopNTable(){
  // 数据已由 loadTopN 设置
  // topNRows.value 已被赋值
}

function renderAccuracyChart(){
  if (!accuracyChart) return
  const { months, accuracy } = generateMockAccuracyData()
  const option: echarts.EChartsOption = {
    tooltip:{ trigger:'axis', axisPointer:{ type:'shadow' }, formatter:'{b}: {c}%' },
    grid:{ left:'3%', right:'4%', bottom:'3%', containLabel:true },
    xAxis:{ type:'category', data:months, axisLine:{ lineStyle:{ color:'#E5E7EB' } }, splitLine:{ show:false } },
    yAxis:{ type:'value', min:70, max:95, axisLabel:{ formatter:'{value}%' }, axisLine:{ show:false }, splitLine:{ lineStyle:{ color:'#F3F4F6' } } },
    series:[{
      name:'预测准确率', type:'line', data:accuracy, smooth:true, symbol:'circle', symbolSize:8,
      lineStyle:{ width:3, color:'#165DFF' }, itemStyle:{ color:'#165DFF', borderColor:'#fff', borderWidth:2 },
      areaStyle:{ color: new (echarts as any).graphic.LinearGradient(0,0,0,1,[{offset:0, color:'rgba(22, 93, 255, 0.3)'},{offset:1, color:'rgba(22, 93, 255, 0)'}]) },
      markLine:{ data:[{ type:'average', name:'平均值', lineStyle:{ color:'#FF7D00' } }], label:{ formatter:'平均值: {c}%' } }
    }]
  }
  accuracyChart.setOption(option, true)
}

// ——— 数据加载与防抖监听 ———
let trendChartOptionCache: echarts.EChartsOption | null = null

async function loadTrend(params: any, appIds: string[]) {
  const horizon = params.dateRange || 7
  const lookback = 30
  if(!appIds || appIds.length===0){
    trendChartOptionCache = null
    renderTrendChart()
    return
  }
  try{
    // 生成未来日期轴
    const dates:string[] = []
    const start = addDays(new Date(), 1)
    for(let i=0;i<horizon;i++){
      dates.push(formatMD(addDays(start, i)))
    }
    // 对每个 app 调用后端预测
    const series: any[] = []
    for(let i=0;i<appIds.length;i++){
      const appId = appIds[i]
      // 使用统一的模型来源与名称
      const sel = getSelectedModel()
      const res = await postForecast(appId, state.country, state.device, state.chartType, lookback, horizon, sel.name)
      const ranks = (res?.predictions || []).map(v=>Math.max(1, Math.round(v)))
      series.push({
        name: appId,
        appId,
        type: 'line',
        data: ranks,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width:2, color: COLORS[i%COLORS.length] },
        itemStyle: { color: COLORS[i%COLORS.length] },
        emphasis: { focus:'series' },
        markPoint: { data: [{type:'max', name:'最高排名'},{type:'min', name:'最低排名'}] }
      })
    }
    const maxRank = Math.max(...series.flatMap((s:any)=>s.data)) + 10
    trendChartOptionCache = {
      tooltip:{
        trigger:'axis',
        axisPointer:{ type:'cross', label:{ backgroundColor:'#6a7985' }},
        formatter(params:any){
          let res = `${params[0].name}<br/>`
          params.forEach((it:any)=>{
            res += `<span style="display:inline-block;margin-right:5px;width:10px;height:10px;border-radius:50%;background-color:${it.color};"></span>`
            res += `${it.seriesName}: 第${it.data}名<br/>`
          })
          return res
        }
      },
      legend:{ data: series.map((s:any)=>s.name), top:0, left:'center', orient:'horizontal', backgroundColor:'transparent', textStyle:{ fontSize:12 }},
      grid:{ left:'3%', right:'4%', bottom:'10%', top:'15%', containLabel:true },
      xAxis:{ type:'category', data:dates, axisLabel:{ interval:0, rotate:30, fontSize:12 }, axisLine:{ lineStyle:{ color:'#E5E7EB' } }, splitLine:{ show:false }},
      yAxis:{ type:'value', inverse:true, min:1, max:maxRank, axisLabel:{ formatter:'{value}' }, axisLine:{ show:false }, splitLine:{ lineStyle:{ color:'#F3F4F6' } } },
      series,
      dataZoom:[{ type:'slider', show:true, xAxisIndex:0, bottom:0, start:0, end:100, height:8, handleSize:'100%', backgroundColor:'#F3F4F6', fillerColor:'#CBD5E1', borderColor:'transparent' }]
    }
    renderTrendChart()
  }catch(e){
    console.warn('loadTrend fallback to mock due to error:', e)
    const { dates, series } = generateMockTrendData(appIds, horizon)
    const maxRank = Math.max(...series.flatMap((s:any)=>s.data)) + 10
    trendChartOptionCache = { /* 与原实现一致 */
      tooltip:{ trigger:'axis', axisPointer:{ type:'cross', label:{ backgroundColor:'#6a7985' }}, formatter(params:any){ let res = `${params[0].name}<br/>`; params.forEach((it:any)=>{ res += `<span style=\"display:inline-block;margin-right:5px;width:10px;height:10px;border-radius:50%;background-color:${it.color};\"></span>`; res += `${it.seriesName}: 第${it.data}名<br/>`; }); return res; } },
      legend:{ data: series.map((s:any)=>s.name), top:0, left:'center', orient:'horizontal', backgroundColor:'transparent', textStyle:{ fontSize:12 }},
      grid:{ left:'3%', right:'4%', bottom:'10%', top:'15%', containLabel:true },
      xAxis:{ type:'category', data:dates, axisLabel:{ interval:0, rotate:30, fontSize:12 }, axisLine:{ lineStyle:{ color:'#E5E7EB' } }, splitLine:{ show:false }},
      yAxis:{ type:'value', inverse:true, min:1, max:maxRank, axisLabel:{ formatter:'{value}' }, axisLine:{ show:false }, splitLine:{ lineStyle:{ color:'#F3F4F6' } } },
      series,
      dataZoom:[{ type:'slider', show:true, xAxisIndex:0, bottom:0, start:0, end:100, height:8, handleSize:'100%', backgroundColor:'#F3F4F6', fillerColor:'#CBD5E1', borderColor:'transparent' }]
    }
    renderTrendChart()
  }
}

async function loadTopN(){
  const sel = getSelectedModel()
  if(!sel.name){
    topNRows.value = []
    topNBrand.value = ''
    return
  }
  try{
    const data = await fetchTopNPredict(sel.name, 10, 30, topNRange.value, sel.source, topNDate.value || undefined)
    topNBrand.value = (data as any).brand || ''
    const items = Array.isArray((data as any).items) ? (data as any).items : []
    topNRows.value = items.map(it=>({
      rank: it.rank,
      appId: it.app_id,
      appName: it.app_name,
      publisher: it.publisher,
      icon: it.icon_url,
      change: it.change ?? 0,
      changePercent: it.change_percent ?? 0,
    }))
  }catch(err){
    console.warn('loadTopN failed, fallback to mock', err)
    topNRows.value = generateMockTopNData(state.dateRange, state.selectedApps)
    topNBrand.value = ''
  }
}

// 趋势刷新
const reloadTrend = debounce(async ()=>{
  if (state.device !== 'iphone' || !modelFiles.value.length){
    trendChartOptionCache = null
    renderTrendChart()
    return
  }
  showLoading('加载趋势预测...')
  await loadTrend(filters.value, state.selectedApps)
  hideLoading()
}, 300)

// 总刷新逻辑：防抖调用
const reloadAll = debounce(async ()=>{
  await reloadTrend()
  await loadTopN()
}, 400)

// 监听 filters 变化，仅刷新趋势
watch(filters, reloadTrend, { deep: true })
// 选择应用，刷新趋势和TopN
watch(() => state.selectedApps, reloadAll, { deep: true })

// 监听模型类型变化，自动刷新文件列表及趋势图
watch(() => state.modelType, async () => {
  await refreshModelFiles()
  if(!modelFiles.value.length){
    trendChartOptionCache = null
    renderTrendChart()
    return
  }
  if(state.selectedApps.length){
    reloadAll()
  }
})
// 监听模型选择、上传文件变化，仅刷新TopN
watch(() => state.selectedModel, () => { loadTopN() })
watch(uploadedFileName, () => { loadTopN() })
watch(topNDate, () => { loadTopN() })
watch(topNRange, () => { loadTopN() })

// ——— 生命周期 ———
onMounted(async ()=>{
  // init charts
  trendChart = echarts.init(trendRef.value as HTMLDivElement)
  accuracyChart = echarts.init(accuracyRef.value as HTMLDivElement)
  window.addEventListener('resize', onResize)

  // TopN 日期默认值（为空表示后端默认(最新+1天)。若要默认今天可改为： fmtDate(new Date()) ）
  topNDate.value = ''

  // 初始渲染
  showLoading('初始化数据加载中...')
  setTimeout(()=>{
    renderAccuracyChart()
    hideLoading()
  }, 500)
  await refreshModelFiles()
  await loadTopN()
  if(modelFiles.value.length && state.selectedApps.length){
    await reloadAll()
  }
})

onBeforeUnmount(()=>{
  window.removeEventListener('resize', onResize)
  trendChart?.dispose()
  accuracyChart?.dispose()
  trendChart = null
  accuracyChart = null
})

function onResize(){
  trendChart?.resize()
  accuracyChart?.resize()
}
</script>

<style scoped>
/* 保留原页面的视觉风格，Tailwind 类已写在模板中，这里无需额外样式 */
:deep(.card-hover){ transition: all .3s ease; }
:deep(.card-hover:hover){ transform: translateY(-4px); box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04); }

/* tailwind 扩展色名在你的项目里应已配置（primary 等）；如未配置，可在全局 tailwind.config.js 中加入。 */
</style>
function onTopNDateChange(){
  loadTopN()
}