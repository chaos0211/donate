<template>
  <div class="space-y-6">
    <!-- 顶部标题 + 操作按钮 -->
    <div
      class="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0"
    >
      <div>
        <h2 class="text-[clamp(1.5rem,3vw,2rem)] font-bold text-gray-800">
          区块链管理
        </h2>
        <p class="text-gray-500 mt-1">
          监控爱心捐赠系统的链上运行状态，查看区块、节点与链配置信息
        </p>
      </div>
      <div class="flex space-x-3">
        <button
          class="bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-lg flex items-center shadow-sm hover:shadow transition-all duration-300 text-sm"
        >
          <i class="fas fa-sync-alt mr-2" />
          <span>刷新状态</span>
        </button>
        <button
          class="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg flex items-center shadow-sm hover:shadow transition-all duration-300 text-sm"
        >
          <i class="fas fa-bolt mr-2" />
          <span>同步区块</span>
        </button>
      </div>
    </div>

    <!-- 区块链统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatsCards
        :value="chainStats.height"
        trend-text="示例数据"
        :trend-up="true"
        icon="fas fa-layer-group"
        icon-bg="bg-primary-light text-primary"
      >
        <template #title>当前区块高度</template>
      </StatsCards>

      <StatsCards
        :value="chainStats.txCount"
        trend-text="示例数据"
        :trend-up="true"
        icon="fas fa-receipt"
        icon-bg="bg-secondary-light text-secondary"
      >
        <template #title>链上捐赠笔数</template>
      </StatsCards>

      <StatsCards
        :value="chainStats.nodeOnline"
        trend-text="示例数据"
        :trend-up="true"
        icon="fas fa-server"
        icon-bg="bg-success-light text-success"
      >
        <template #title>在线节点数</template>
      </StatsCards>

      <StatsCards
        :value="chainStats.syncStatus"
        trend-text=""
        :trend-up="true"
        icon="fas fa-heartbeat"
        icon-bg="bg-info-light text-info"
      >
        <template #title>同步状态</template>
      </StatsCards>
    </div>

    <!-- 主体：左侧项目列表 + 右侧链详情 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 左侧：已上链项目列表（管理员视角） -->
      <div class="lg:col-span-2 space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="font-semibold text-gray-800">项目链上记录</h3>
          <span class="text-xs text-gray-400">
            仅展示已上链 / 待上链的公益项目
          </span>
        </div>

        <ProjectList
          :projects="projects"
          :total="projects.length"
          :page="page"
          :page-size="pageSize"
          user-role="admin"
          @change-page="handlePageChange"
        />
      </div>

      <!-- 右侧：区块详情 + 节点状态 + 链配置 -->
      <div class="lg:col-span-1 space-y-4">
        <!-- 区块详情 -->
        <div class="bg-white rounded-xl shadow-card p-4 md:p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-gray-800">区块详情</h3>
            <span class="text-xs text-gray-400">
              当前展示为整体链状态
            </span>
          </div>

          <div class="space-y-2 text-sm text-gray-700">
            <div class="flex justify-between">
              <span class="text-gray-500">最新区块高度</span>
              <span class="font-medium">
                {{ chainStats.height || 0 }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">最近出块时间</span>
              <span class="font-medium">
                <!-- TODO: 后端传递最近出块时间 -->
                暂无数据
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">最近区块哈希</span>
              <span class="font-mono text-xs text-gray-600 truncate max-w-[160px]">
                <!-- TODO: 后端传递区块哈希 -->
                无
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">当前交易池大小</span>
              <span class="font-medium">
                <!-- TODO: 后端传递 tx pool 大小 -->
                0
              </span>
            </div>
          </div>
        </div>

        <!-- 节点状态 -->
        <div class="bg-white rounded-xl shadow-card p-4 md:p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-gray-800">节点状态</h3>
            <span class="text-xs text-gray-400">
              后续由后端返回真实节点列表
            </span>
          </div>

          <ul class="space-y-2 text-sm">
            <li
              class="flex items-center justify-between px-3 py-2 rounded-lg bg-gray-50"
            >
              <div>
                <p class="font-medium text-gray-800">
                  节点列表占位
                </p>
                <p class="text-xs text-gray-500">
                  等后端返回节点信息后再填充
                </p>
              </div>
              <span
                class="px-2 py-1 rounded-full text-xs bg-gray-200 text-gray-600"
              >
                未连接
              </span>
            </li>
          </ul>
        </div>

        <!-- 链配置信息 -->
        <div class="bg-white rounded-xl shadow-card p-4 md:p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-gray-800">链配置信息</h3>
          </div>

          <div class="space-y-2 text-sm text-gray-700">
            <div class="flex justify-between">
              <span class="text-gray-500">网络类型</span>
              <span class="font-medium">
                私有链（本地内网）
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">共识机制</span>
              <span class="font-medium">
                <!-- TODO: 后端传具体名称，如 PoA / Raft / PBFT -->
                待配置
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">数据持久化策略</span>
              <span class="font-medium">
                区块 + MySQL 双存储
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">区块生成间隔</span>
              <span class="font-medium">
                <!-- TODO: 由后端传递，单位秒 -->
                待配置
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">当前网络 ID</span>
              <span class="font-mono text-xs text-gray-700">
                <!-- TODO: 后端传递 chainId / networkId -->
                未设置
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import StatsCards from '@/components/charts/StatsCards.vue'
import ProjectList from '@/components/charts/ProjectList.vue'

// TODO: 接入后端接口时，用真实接口替换下面这些占位数据

// 已上链 / 待上链项目列表（现在先给空数组，后端接入后再填）
const projects = ref<any[]>([])

// 分页占位（后端控制页码时，这里只负责把事件传出去）
const page = ref(1)
const pageSize = ref(5)

const handlePageChange = (newPage: number) => {
  page.value = newPage
  // TODO: 接入后端后，在这里根据 newPage 请求区块链相关项目数据
}

// 区块链整体统计信息（先给 0/空值，后端接入后再赋值）
const chainStats = computed(() => ({
  height: 0,        // 当前区块高度
  txCount: 0,       // 链上捐赠交易笔数
  nodeOnline: 0,    // 在线节点数
  syncStatus: '未同步' // 同步状态展示字符串
}))
</script>