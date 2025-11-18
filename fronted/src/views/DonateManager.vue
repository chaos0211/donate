<template>
  <div class="space-y-6">
    <!-- 顶部标题 + 操作按钮 -->
    <div
      class="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0"
    >
      <div>
        <h2 class="text-[clamp(1.5rem,3vw,2rem)] font-bold text-gray-800">
          公益项目管理
        </h2>
        <p class="text-gray-500 mt-1">
          管理、查看和维护所有在链上登记的爱心公益项目
        </p>
      </div>
      <div class="flex space-x-3">
        <button
          class="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg flex items-center shadow-sm hover:shadow transition-all duration-300 text-sm"
        >
          <i class="fas fa-plus mr-2" />
          <span>新增项目</span>
        </button>
        <button
          class="bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-lg flex items-center shadow-sm hover:shadow transition-all duration-300 text-sm"
        >
          <i class="fas fa-file-import mr-2" />
          <span>批量导入</span>
        </button>
      </div>
    </div>

    <!-- 筛选查询条件区 -->
    <!-- TODO: 这里可以拆成 <ProjectFilterBar /> 组件 -->
    <div class="bg-white rounded-xl shadow-card p-5 mb-2">
      <div class="flex flex-col md:flex-row gap-4">
        <div class="flex-grow">
          <label class="block text-sm font-medium text-gray-500 mb-1">
            项目名称关键字
          </label>
          <div class="relative">
            <i
              class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
            />
            <input
              v-model="filters.keyword"
              type="text"
              placeholder="请输入项目名称关键字"
              class="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all duration-300"
            />
          </div>
        </div>

        <div class="w-full md:w-48">
          <label class="block text-sm font-medium text-gray-500 mb-1">
            项目状态
          </label>
          <select
            v-model="filters.status"
            class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all duration-300 bg-white"
          >
            <option value="">全部状态</option>
            <option value="inProgress">进行中</option>
            <option value="completed">已结束</option>
            <option value="reviewing">审核中</option>
            <option value="rejected">已驳回</option>
          </select>
        </div>

        <div class="w-full md:w-64">
          <label class="block text-sm font-medium text-gray-500 mb-1">
            所属组织
          </label>
          <select
            v-model="filters.org"
            class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all duration-300 bg-white"
          >
            <option value="">全部组织</option>
            <option value="org1">爱心公益协会</option>
            <option value="org2">阳光慈善基金会</option>
            <option value="org3">温暖救助中心</option>
            <option value="org4">希望工程办公室</option>
          </select>
        </div>

        <div class="w-full md:w-64">
          <label class="block text-sm font-medium text-gray-500 mb-1">
            创建时间
          </label>
          <div class="relative">
            <i
              class="fas fa-calendar absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
            />
            <input
              v-model="filters.dateRange"
              type="text"
              placeholder="选择时间范围（占位）"
              class="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all duration-300"
            />
          </div>
        </div>

        <div class="flex items-end space-x-3">
          <button
            class="bg-primary hover:bg-primary/90 text-white px-6 py-2 rounded-lg flex items-center shadow-sm hover:shadow transition-all duration-300 text-sm"
            @click="applyFilters"
          >
            <i class="fas fa-search mr-2" />
            <span>查询</span>
          </button>
          <button
            class="bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 px-6 py-2 rounded-lg flex items-center shadow-sm hover:shadow transition-all duration-300 text-sm"
            @click="resetFilters"
          >
            <i class="fas fa-sync-alt mr-2" />
            <span>重置</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 项目概览统计卡片区 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
      <StatsCards :value="stats.inProgress" icon="fas fa-hourglass-half" icon-bg="bg-primary-light text-primary">
        <template #title>当前进行中项目</template>
      </StatsCards>
      <StatsCards :value="stats.completed" icon="fas fa-check-circle" icon-bg="bg-success-light text-success">
        <template #title>已结束项目</template>
      </StatsCards>
      <StatsCards :value="stats.reviewing" icon="fas fa-clock-rotate-left" icon-bg="bg-warning-light text-warning">
        <template #title>审核中项目</template>
      </StatsCards>
      <StatsCards :value="stats.total" icon="fas fa-link" icon-bg="bg-gray-100 text-gray-700">
        <template #title>链上已记录项目总数</template>
      </StatsCards>
    </div>

    <!-- 项目列表表格区 -->
    <ProjectList
      :projects="filteredProjects"
      :total="filteredProjects.length"
      :page="page"
      :page-size="pageSize"
      @change-page="handlePageChange"
    />

    <!-- 弹窗区域：先不实现逻辑，只预留占位，可以拆成多个组件 -->
    <!-- TODO: <ProjectFormModal /> / <ConfirmDeleteModal /> / <SyncModal /> 等 -->
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import StatsCards from '@/components/charts/StatsCards.vue'
import ProjectList from '@/components/charts/ProjectList.vue'

type ProjectStatus = 'inProgress' | 'completed' | 'reviewing' | 'rejected'

interface Project {
  id: number
  name: string
  organization: string
  targetAmount: number
  raisedAmount: number
  status: ProjectStatus
  createdAt: string
  blockchainInfo: '已上链' | '待上链'
  blockHeight?: number | ''
}

// 模拟数据（来自 aa.html）
const projects = reactive<Project[]>([
  {
    id: 1,
    name: '乡村教育支持计划',
    organization: 'org4',
    targetAmount: 500000,
    raisedAmount: 320000,
    status: 'inProgress',
    createdAt: '2023-05-15',
    blockchainInfo: '已上链',
    blockHeight: 1258963
  },
  {
    id: 2,
    name: '贫困山区医疗援助',
    organization: 'org2',
    targetAmount: 300000,
    raisedAmount: 300000,
    status: 'completed',
    createdAt: '2023-03-22',
    blockchainInfo: '已上链',
    blockHeight: 1245632
  },
  {
    id: 3,
    name: '留守儿童关爱行动',
    organization: 'org1',
    targetAmount: 200000,
    raisedAmount: 150000,
    status: 'inProgress',
    createdAt: '2023-06-01',
    blockchainInfo: '已上链',
    blockHeight: 1260125
  },
  {
    id: 4,
    name: '残疾人就业培训',
    organization: 'org3',
    targetAmount: 150000,
    raisedAmount: 80000,
    status: 'reviewing',
    createdAt: '2023-06-18',
    blockchainInfo: '待上链',
    blockHeight: ''
  },
  {
    id: 5,
    name: '环境保护志愿者招募',
    organization: 'org2',
    targetAmount: 100000,
    raisedAmount: 100000,
    status: 'completed',
    createdAt: '2023-01-10',
    blockchainInfo: '已上链',
    blockHeight: 1230568
  }
  // 其余条目可以按需补充
])

const filters = reactive({
  keyword: '',
  status: '',
  org: '',
  dateRange: ''
})

const filteredProjects = computed(() => {
  return projects.filter((p) => {
    const nameMatch = filters.keyword
      ? p.name.toLowerCase().includes(filters.keyword.toLowerCase())
      : true
    const statusMatch = filters.status ? p.status === filters.status : true
    const orgMatch = filters.org ? p.organization === filters.org : true
    // 时间筛选先不实现，后面接 date picker 再说
    return nameMatch && statusMatch && orgMatch
  })
})

const stats = computed(() => {
  const inProgress = projects.filter((p) => p.status === 'inProgress').length
  const completed = projects.filter((p) => p.status === 'completed').length
  const reviewing = projects.filter((p) => p.status === 'reviewing').length
  const total = projects.length
  return { inProgress, completed, reviewing, total }
})

// 分页由后端控制，这里只做占位和事件转发
const page = ref(1)
const pageSize = ref(5)

const handlePageChange = (newPage: number) => {
  page.value = newPage
  // TODO: 后续接入后端接口时，在这里根据 newPage 请求新数据
}

const applyFilters = () => {
  // 这里只是触发 computed 重新计算，真实项目一般会调 API
}

const resetFilters = () => {
  filters.keyword = ''
  filters.status = ''
  filters.org = ''
  filters.dateRange = ''
}

const progressPercent = (p: Project) => {
  if (!p.targetAmount) return 0
  return Math.min(100, Math.round((p.raisedAmount / p.targetAmount) * 100))
}

const statusText = (status: ProjectStatus) => {
  const map: Record<ProjectStatus, string> = {
    inProgress: '进行中',
    completed: '已结束',
    reviewing: '审核中',
    rejected: '已驳回'
  }
  return map[status] || status
}

const statusBadgeClass = (status: ProjectStatus) => {
  const map: Record<ProjectStatus, string> = {
    inProgress: 'bg-primary-light text-primary',
    completed: 'bg-success-light text-success',
    reviewing: 'bg-warning-light text-warning',
    rejected: 'bg-danger-light text-danger'
  }
  return map[status] || 'bg-gray-100 text-gray-500'
}

const orgName = (orgCode: string) => {
  const map: Record<string, string> = {
    org1: '爱心公益协会',
    org2: '阳光慈善基金会',
    org3: '温暖救助中心',
    org4: '希望工程办公室'
  }
  return map[orgCode] || orgCode
}

const formatNumber = (num: number) => {
  return num.toLocaleString('zh-CN', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  })
}
</script>