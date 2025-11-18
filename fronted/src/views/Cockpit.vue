<template>
  <div class="space-y-6">
    <!-- 页面标题与操作按钮 -->
    <div
      class="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0"
    >
      <div>
        <h2 class="text-[clamp(1.5rem,3vw,2rem)] font-bold text-gray-800">
          首页总览
        </h2>
        <p class="text-gray-500 mt-1">查看平台捐赠概况和区块链状态</p>
      </div>
      <div class="flex space-x-3">
        <button class="btn-secondary text-sm flex items-center">
          <i class="fas fa-download mr-2"></i>
          <span>导出报告</span>
        </button>
        <button class="btn-primary text-sm flex items-center">
          <i class="fas fa-plus mr-2"></i>
          <span>发起捐赠</span>
        </button>
      </div>
    </div>

    <!-- 统计卡片区 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatsCards
        :value="totalAmount"
        trend-text="12.5% 较上月"
        :trend-up="true"
        icon="fas fa-wallet"
        icon-bg="bg-primary-light text-primary"
      >
        <template #title>累计捐赠总额</template>
      </StatsCards>

      <StatsCards
        :value="todayAmount"
        trend-text="8.2% 较昨日"
        :trend-up="true"
        icon="fas fa-calendar-day"
        icon-bg="bg-secondary-light text-secondary"
      >
        <template #title>今日捐赠金额</template>
      </StatsCards>

      <StatsCards
        :value="activeProjects"
        trend-text="2 较上周"
        :trend-up="false"
        icon="fas fa-project-diagram"
        icon-bg="bg-warning-light text-warning"
      >
        <template #title>进行中的公益项目</template>
      </StatsCards>

      <StatsCards
        :value="blockHeight"
        trend-text="同步中"
        :trend-up="true"
        icon="fas fa-link"
        icon-bg="bg-info-light text-info"
      >
        <template #title>区块链区块高度</template>
      </StatsCards>
    </div>

    <!-- 图表区 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 捐赠金额趋势图 -->
      <div class="bg-white rounded-xl shadow-card p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="font-semibold text-gray-800">捐赠金额趋势</h3>
          <div class="flex space-x-2">
            <button class="text-xs px-3 py-1 rounded-full bg-primary text-white">
              周
            </button>
            <button
              class="text-xs px-3 py-1 rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200"
            >
              月
            </button>
            <button
              class="text-xs px-3 py-1 rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200"
            >
              年
            </button>
          </div>
        </div>

        <TrendChart />
      </div>

      <!-- 捐赠分布饼图 -->
      <div class="bg-white rounded-xl shadow-card p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="font-semibold text-gray-800">捐赠分布</h3>
          <div class="flex space-x-2">
            <button class="text-xs px-3 py-1 rounded-full bg-primary text-white">
              项目
            </button>
            <button
              class="text-xs px-3 py-1 rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200"
            >
              组织
            </button>
          </div>
        </div>

  <CategoryPie />
</div>
    </div>

    <!-- 双列表区：最新捐赠记录 & 最新区块 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 最新捐赠记录 -->
      <div class="bg-white rounded-xl shadow-card p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="font-semibold text-gray-800">最新捐赠记录</h3>
          <a href="javascript:void(0);" class="text-primary text-sm hover:underline">
            查看全部
          </a>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  时间
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  项目名称
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  捐赠人
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  金额
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  区块哈希
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr class="hover:bg-gray-50 transition-colors duration-150">
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                  2023-06-15 14:32
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                  山区教育支持计划
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                  匿名捐赠者
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm font-medium text-success">
                  ¥5,000
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                  0x7f3d2a...
                </td>
              </tr>
              <tr class="hover:bg-gray-50 transition-colors duration-150">
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                  2023-06-15 13:45
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                  留守儿童关爱
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                  李华
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm font-medium text-success">
                  ¥1,000
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                  0x9e2c5b...
                </td>
              </tr>
              <tr class="hover:bg-gray-50 transition-colors duration-150">
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                  2023-06-15 11:20
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                  乡村医疗建设
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                  匿名捐赠者
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm font-medium text-success">
                  ¥2,500
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                  0x3a7f1d...
                </td>
              </tr>
              <tr class="hover:bg-gray-50 transition-colors duration-150">
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                  2023-06-15 10:05
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                  环保植树计划
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                  王芳
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm font-medium text-success">
                  ¥300
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                  0x8b4e6c...
                </td>
              </tr>
              <tr class="hover:bg-gray-50 transition-colors duration-150">
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                  2023-06-15 09:18
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                  山区教育支持计划
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                  张伟
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm font-medium text-success">
                  ¥1,200
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                  0x5d1f3e...
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 最新区块 -->
      <div class="bg-white rounded-xl shadow-card p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="font-semibold text-gray-800">最新区块</h3>
          <a href="javascript:void(0);" class="text-primary text-sm hover:underline">
            查看全部
          </a>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  区块高度
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  时间
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  哈希
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  捐赠笔数
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr class="hover:bg-gray-50 transition-colors duration-150">
                <td class="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                  12,584
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                  2023-06-15 14:32
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                  0x7f3d2a8b...
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                  3
                </td>
              </tr>
              <tr class="hover:bg-gray-50 transition-colors duration-150">
                <td class="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                  12,583
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                  2023-06-15 13:45
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                  0x9e2c5b7d...
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                  1
                </td>
              </tr>
              <tr class="hover:bg-gray-50 transition-colors duration-150">
                <td class="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                  12,582
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                  2023-06-15 11:20
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                  0x3a7f1d9c...
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                  2
                </td>
              </tr>
              <tr class="hover:bg-gray-50 transition-colors duration-150">
                <td class="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                  12,581
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                  2023-06-15 10:05
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                  0x8b4e6c3d...
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                  1
                </td>
              </tr>
              <tr class="hover:bg-gray-50 transition-colors duration-150">
                <td class="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                  12,580
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                  2023-06-15 09:18
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                  0x5d1f3e7a...
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                  4
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import TrendChart from '@/components/charts/DonationTrendSimple.vue'
import CategoryPie from '@/components/charts/CategoryPie.vue'
import StatsCards from '@/components/charts/StatsCards.vue'

// 这四个值以后由后端接口赋值，现在为 null，会在组件里显示为 0
const totalAmount = ref<number | null>(null)
const todayAmount = ref<number | null>(null)
const activeProjects = ref<number | null>(null)
const blockHeight = ref<number | null>(null)
</script>
