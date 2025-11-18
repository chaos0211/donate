<template>
  <div class="bg-white rounded-xl shadow-sm p-5 mb-8 border border-light-200">
    <!-- 行 1：时间范围 / 国家 / 设备 / 榜单类型 / 榜单分类 -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4 items-center">
      <!-- 时间范围 -->
      <div>
        <label class="block text-sm text-gray-500 mb-1">日期范围</label>
        <DateRangePills v-model="dateRangeModel" @update:modelValue="onChangeDate" />
      </div>

      <!-- 国家/地区 -->
      <div>
        <label class="block text-sm text-gray-500 mb-1">国家/地区</label>
        <select v-model="countryModel" @change="$emit('update:country', countryModel)"
                class="w-full px-3 py-2 rounded-lg border border-light-200 focus:outline-none">
          <option v-for="c in countries" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>

      <!-- 设备（按钮组） -->
      <div>
        <label class="block text-sm text-gray-500 mb-1">设备</label>
        <div class="inline-flex rounded-full overflow-hidden bg-gray-100">
          <button
            class="px-4 py-2 text-sm"
            :disabled="!devices.includes('iphone')"
            :class="[(deviceModel === 'iphone' ? activeBtn : normalBtn), (!devices.includes('iphone') ? 'opacity-50 cursor-not-allowed' : '')]"
            @click="updateDevice('iphone')"
          >iPhone</button>
          <button
            class="px-4 py-2 text-sm"
            :disabled="!devices.includes('ipad')"
            :class="[(deviceModel === 'ipad' ? activeBtn : normalBtn), (!devices.includes('ipad') ? 'opacity-50 cursor-not-allowed' : '')]"
            @click="updateDevice('ipad')"
          >iPad</button>
          <button
            class="px-4 py-2 text-sm"
            :disabled="!devices.includes('android')"
            :class="[(deviceModel === 'android' ? activeBtn : normalBtn), (!devices.includes('android') ? 'opacity-50 cursor-not-allowed' : '')]"
            @click="updateDevice('android')"
          >Android</button>
        </div>
      </div>

      <!-- 榜单类型（brand） -->
      <div>
        <label class="block text-sm text-gray-500 mb-1">榜单类型</label>
        <div class="inline-flex rounded-full overflow-hidden bg-gray-100">
          <button class="px-4 py-2 text-sm" :class="chartTypeModel === 'free' ? activeBtn : normalBtn" @click="$emit('update:chartType', 'free')">免费</button>
          <button class="px-4 py-2 text-sm" :class="chartTypeModel === 'paid' ? activeBtn : normalBtn" @click="$emit('update:chartType', 'paid')">付费</button>
          <button class="px-4 py-2 text-sm" :class="chartTypeModel === 'grossing' ? activeBtn : normalBtn" @click="$emit('update:chartType', 'grossing')">畅销</button>
        </div>
      </div>

      <!-- 榜单分类（应用类别） -->
      <div>
        <label class="block text-sm text-gray-500 mb-1">榜单分类</label>
        <div class="relative">
          <select v-model="categoryModel" @change="$emit('update:category', categoryModel)"
                  class="w-full appearance-none px-3 py-2 rounded-lg border border-light-200 focus:outline-none">
            <option v-for="g in genres" :key="g" :value="g">{{ g }}</option>
          </select>
          <div class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
            <i class="fas fa-chevron-down text-xs"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- 行 2：应用搜索 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-center mt-4">
      <!-- 应用搜索 -->
      <div>
        <label class="block text-sm text-gray-500 mb-1">应用搜索（最多添加 3 个）</label>
        <div class="flex gap-2">
          <input v-model.trim="keyword" @keyup.enter="doSearch"
                 placeholder="输入应用名或 app_id"
                 class="flex-1 px-3 py-2 rounded-lg border border-light-200 focus:outline-none"/>
          <button class="px-3 py-2 text-sm rounded-lg border bg-white hover:bg-light-100" @click="doSearch">搜索</button>
          <button v-if="showClear" class="px-3 py-2 text-sm rounded-lg border bg-white hover:bg-light-100" @click="clearSearch">清空</button>
        </div>
        <!-- 搜索结果 -->
        <div v-if="results.length" class="mt-2 border border-light-200 rounded-lg overflow-hidden">
          <div v-for="(r, idx) in shownResults" :key="r.app_id+idx"
               class="flex items-center justify-between px-3 py-2 hover:bg-light-50">
            <div class="flex items-center gap-2 overflow-hidden">
              <img :src="r.icon_url" class="w-6 h-6 rounded" alt=""/>
              <div class="truncate">
                <div class="text-sm truncate">{{ r.app_name }}</div>
                <div class="text-xs text-gray-500 truncate">{{ r.publisher }}</div>
              </div>
            </div>
            <button class="px-2 py-1 text-xs rounded border hover:bg-light-100"
                    :disabled="selectedAppsModel.length>=3 || selectedAppsModel.includes(r.app_id)"
                    @click="addApp(r.app_id)">添加</button>
          </div>
          <div v-if="results.length>5 && !expanded" class="text-center py-2">
            <button class="text-xs text-primary-600" @click="expanded=true">更多</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 已选应用 -->
    <div v-if="selectedAppsModel.length" class="mt-4">
      <div class="text-sm text-gray-500 mb-1">已选应用（{{ selectedAppsModel.length }}/3）</div>
      <div class="flex flex-wrap gap-2">
        <div v-for="aid in selectedAppsModel" :key="aid" class="flex items-center gap-2 px-2 py-1 rounded-full bg-light-100 text-sm">
          <span class="truncate max-w-[160px]">{{ aid }}</span>
          <button class="text-xs text-red-500" @click="removeApp(aid)">×</button>
        </div>
      </div>
    </div>

    <!-- 操作区 -->
    <div class="flex justify-end gap-2 mt-6">
      <button class="px-4 py-2 text-sm rounded-lg border bg-white hover:bg-light-100" @click="onReset">重置</button>
      <button class="px-4 py-2 text-sm rounded-lg bg-primary-600 text-white hover:bg-primary-700" @click="$emit('submit')">开始预测分析</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import DateRangePills from '@/components/common/DateRangePills.vue'
import { onMounted, ref, watch, computed } from 'vue'
import http from '@/api/http'

const props = defineProps<{
  dateRange: number
  country: string
  device: string
  chartType: string
  category: string
  selectedApps: string[]
}>()

const emit = defineEmits<{
  (e:'update:dateRange', v:number):void
  (e:'update:country', v:string):void
  (e:'update:device', v:string):void
  (e:'update:chartType', v:string):void
  (e:'update:category', v:string):void
  (e:'update:selectedApps', v:string[]):void
  (e:'submit'):void
  (e:'reset'):void
}>()

// 本地 model （双向绑定至父组件）
const dateRangeModel = ref(props.dateRange)
const countryModel = ref(props.country)
const deviceModel = ref(props.device)
const chartTypeModel = ref(props.chartType)
const categoryModel = ref(props.category)
const selectedAppsModel = ref<string[]>([...(props.selectedApps||[])])

watch(() => props.dateRange, v => dateRangeModel.value = v)
watch(() => props.country, v => countryModel.value = v)
watch(() => props.device, v => deviceModel.value = v)
watch(() => props.chartType, v => chartTypeModel.value = v)
watch(() => props.category, v => categoryModel.value = v)
watch(() => props.selectedApps, v => selectedAppsModel.value = [...(v||[])])

// 选项数据
const countries = ref<string[]>([])
const devices = ref<string[]>([])
const brands = ref<string[]>([])
const genres = ref<string[]>([])

// 搜索
const keyword = ref('')
const results = ref<Array<{app_id:string; app_name:string; icon_url?:string; publisher?:string}>>([])
const expanded = ref(false)
const showClear = computed(() => !!keyword.value || results.value.length>0)
const shownResults = computed(() => expanded.value ? results.value.slice(0,10) : results.value.slice(0,5))

const activeBtn = 'bg-blue-600 text-white hover:bg-blue-700'
const normalBtn = 'bg-gray-100 text-gray-700 hover:bg-gray-200'

function updateDevice(v:string){
  deviceModel.value = v
  emit('update:device', v)
}

function onChangeDate(v:number){
  dateRangeModel.value = v
  emit('update:dateRange', v)
}

function addApp(appId:string){
  if(selectedAppsModel.value.includes(appId)) return
  if(selectedAppsModel.value.length>=3) return
  const next = [...selectedAppsModel.value, appId]
  selectedAppsModel.value = next
  emit('update:selectedApps', next)
}
function removeApp(appId:string){
  const next = selectedAppsModel.value.filter(x=>x!==appId)
  selectedAppsModel.value = next
  emit('update:selectedApps', next)
}

async function doSearch(){
  const q = keyword.value.trim()
  if(!q) return
  try{
    const params:any = { q, limit: 10, window: dateRangeModel.value||30 }
    if(countryModel.value) params.country = countryModel.value
    if(deviceModel.value) params.device = deviceModel.value
    if(chartTypeModel.value) params.brand = chartTypeModel.value
    if (categoryModel.value && categoryModel.value !== '所有分类') params.genre = categoryModel.value
    const { data } = await http.get('/api/v1/apps/search', { params })
    results.value = Array.isArray(data?.items) ? data.items : []
  }catch(err){
    console.error('search failed', err)
    results.value = []
  }
}

function clearSearch(){
  keyword.value = ''
  results.value = []
  expanded.value = false
}

async function loadOptions(){
  try{
    // country/device/brand
    const { data } = await http.get('/api/v1/meta/options', { params: { fields: 'country,device,brand' } })
    countries.value = Array.isArray(data?.country) ? data.country : []
    devices.value = Array.isArray(data?.device) ? data.device : []
    brands.value = Array.isArray(data?.brand) ? data.brand : []

    if (!countries.value.length) countries.value = ['cn', 'us']
    if (!devices.value.length) devices.value = ['iphone']
    if (!brands.value.length)  brands.value  = ['free', 'paid', 'grossing']

    // genres：直接从 app_ratings 表的 rank_c 字段中获取
    // const r2 = await http.get('/api/v1/meta/options', { params: { fields: 'app_genre' } })
    // const g = r2.data?.app_genre
    // const list = Array.isArray(g) ? g.slice() : []
    // if (!list.includes('所有分类')) list.unshift('所有分类')
    // genres.value = list
    const r2 = await http.get('/api/v1/meta/options', { params: { fields: 'app_genre', window: dateRangeModel.value || 30 } })
    const list = Array.isArray(r2.data?.app_genre) ? r2.data.app_genre.slice() : []
    if (!list.includes('所有分类')) list.unshift('所有分类')
    genres.value = list

    if (!categoryModel.value && genres.value.length) {
      categoryModel.value = genres.value[0]
      emit('update:category', categoryModel.value)
    }

    // 初始化默认值（若父组件未传则取首项）
    if(!countryModel.value && countries.value.length) {
      countryModel.value = countries.value[0]; emit('update:country', countryModel.value)
    }
    if(!deviceModel.value && devices.value.length) {
      deviceModel.value = devices.value[0]; emit('update:device', deviceModel.value)
    }
    if (!chartTypeModel.value) {
      chartTypeModel.value = brands.value.includes('free') ? 'free'
                            : (brands.value[0] || 'free')
      emit('update:chartType', chartTypeModel.value)
    }
  }catch(err){
    console.error('load meta/options failed', err)
  }
}

function onReset(){
  // 清空本地
  selectedAppsModel.value = []
  keyword.value = ''
  results.value = []
  expanded.value = false
  // 通知父组件
  emit('update:selectedApps', [])
  emit('reset')
}

onMounted(()=>{
  loadOptions()
})
</script>

<style scoped>
/* 可按需覆盖 */
</style>