

<template>
  <div class="bg-white rounded-xl shadow-card p-4 md:p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-semibold text-gray-800">项目列表</h3>
      <span class="text-xs text-gray-400">共 {{ total }} 个项目</span>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="bg-gray-50 text-left">
            <th class="px-6 py-4 text-sm font-semibold text-gray-700">
              项目名称
            </th>
            <th class="px-6 py-4 text-sm font-semibold text-gray-700">
              所属组织
            </th>
            <th class="px-6 py-4 text-sm font-semibold text-gray-700">
              目标金额 / 已筹金额
            </th>
            <th class="px-6 py-4 text-sm font-semibold text-gray-700">
              项目状态
            </th>
            <th class="px-6 py-4 text-sm font-semibold text-gray-700">
              创建时间
            </th>
            <th class="px-6 py-4 text-sm font-semibold text-gray-700">
              链上信息
            </th>
            <th
              class="px-6 py-4 text-sm font-semibold text-gray-700 text-right"
            >
              操作
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="project in projects"
            :key="project.id"
            class="border-b border-gray-100 hover:bg-gray-50 transition-colors"
          >
            <td class="px-6 py-4">
              <div class="flex items-center">
                <div
                  class="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center text-gray-400 mr-3 text-xs"
                >
                  图
                </div>
                <span class="font-medium">{{ project.name }}</span>
              </div>
            </td>
            <td class="px-6 py-4">
              {{ orgName(project.organization) }}
            </td>
            <td class="px-6 py-4">
              <div>
                <div class="flex justify-between text-sm mb-1">
                  <span>¥{{ formatNumber(project.raisedAmount) }}</span>
                  <span class="text-gray-500">
                    /{{ formatNumber(project.targetAmount) }}
                  </span>
                </div>
                <div class="h-1.5 rounded-full bg-gray-100 overflow-hidden">
                  <div
                    class="h-full bg-primary transition-all duration-500"
                    :style="{ width: progressPercent(project) + '%' }"
                  />
                </div>
                <div class="text-right text-xs text-gray-500 mt-1">
                  {{ progressPercent(project) }}%
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <span
                class="px-2 py-1 rounded-full text-xs font-medium"
                :class="statusBadgeClass(project.status)"
              >
                {{ statusText(project.status) }}
              </span>
            </td>
            <td class="px-6 py-4 text-gray-500">
              {{ project.createdAt }}
            </td>
            <td class="px-6 py-4">
              <div>
                <div class="text-sm">{{ project.blockchainInfo }}</div>
                <div
                  v-if="project.blockchainInfo === '已上链'"
                  class="text-xs text-gray-500"
                >
                  区块高度: {{ project.blockHeight }}
                </div>
              </div>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex items-center justify-end space-x-2 text-sm">
                <button
                  class="text-gray-500 hover:text-primary transition-colors"
                >
                  <i class="fas fa-eye" />
                </button>
                <button
                  class="text-gray-500 hover:text-primary transition-colors"
                >
                  <i class="fas fa-edit" />
                </button>
                <button
                  class="text-gray-500 hover:text-danger transition-colors"
                >
                  <i class="fas fa-trash-alt" />
                </button>
                <button
                  v-if="project.blockchainInfo === '待上链'"
                  class="text-gray-500 hover:text-primary transition-colors"
                >
                  <i class="fas fa-link" />
                </button>
              </div>
            </td>
          </tr>

          <tr v-if="!projects || !projects.length">
            <td colspan="7" class="px-6 py-12 text-center text-gray-500">
              暂无匹配项目
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页控件：参数由父组件传入，点击事件抛出给父组件处理 -->
    <div
      class="px-6 py-4 border-t border-gray-100 flex items-center justify-between text-sm text-gray-500"
    >
      <div>
        显示
        <span class="font-medium text-gray-700">
          {{ total === 0 ? 0 : start }}
        </span>
        -
        <span class="font-medium text-gray-700">
          {{ total === 0 ? 0 : end }}
        </span>
        条，共
        <span class="font-medium text-gray-700">
          {{ total }}
        </span>
        条
      </div>
      <div class="flex items-center space-x-1">
        <button
          class="w-9 h-9 flex items-center justify-center rounded-lg border border-gray-200 text-gray-400 hover:border-primary hover:text-primary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="page <= 1"
          @click="goPrev"
        >
          <i class="fas fa-angle-left" />
        </button>
        <span class="px-2">
          第
          <span class="font-medium text-gray-700">{{ page }}</span>
          / {{ pageCount }} 页
        </span>
        <button
          class="w-9 h-9 flex items-center justify-center rounded-lg border border-gray-200 text-gray-700 hover:border-primary hover:text-primary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="page >= pageCount"
          @click="goNext"
        >
          <i class="fas fa-angle-right" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

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

const props = withDefaults(
  defineProps<{
    projects: Project[]
    total: number
    page?: number
    pageSize?: number
  }>(),
  {
    projects: () => [],
    total: 0,
    page: 1,
    pageSize: 5
  }
)

const emit = defineEmits<{
  (e: 'change-page', page: number): void
}>()

const pageCount = computed(() =>
  props.total === 0 ? 1 : Math.max(1, Math.ceil(props.total / props.pageSize))
)

const page = computed(() => props.page)
const pageSize = computed(() => props.pageSize)

const start = computed(() => {
  if (props.total === 0) return 0
  return (page.value - 1) * pageSize.value + 1
})

const end = computed(() => {
  if (props.total === 0) return 0
  return Math.min(props.total, page.value * pageSize.value)
})

const goPrev = () => {
  if (page.value > 1) {
    emit('change-page', page.value - 1)
  }
}

const goNext = () => {
  if (page.value < pageCount.value) {
    emit('change-page', page.value + 1)
  }
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
  if (num === null || num === undefined) return 0
  return num.toLocaleString('zh-CN', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  })
}
</script>