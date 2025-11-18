<template>
  <div class="space-y-6">
    <!-- 顶部标题 + 操作按钮 -->
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <i class="fas fa-heart text-primary text-2xl" />
        <div>
          <h1 class="text-xl font-bold text-gray-700">系统管理</h1>
          <p class="text-sm text-gray-400">
            管理系统用户、角色权限、运行参数与审计日志
          </p>
        </div>
      </div>

      <div class="flex items-center space-x-3">
        <button
          class="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg flex items-center transition-all duration-300 shadow-sm hover:shadow"
        >
          <i class="fas fa-plus mr-2" />
          <span>新增用户</span>
        </button>
      </div>
    </div>



    <!-- 主内容区域：左侧导航 + 右侧不同功能块 -->
    <div class="flex flex-col lg:flex-row gap-6">
      <!-- 左侧系统管理导航 -->
      <div class="lg:w-1/5 bg-white rounded-xl shadow-card p-4 h-fit">
        <nav class="space-y-1">
          <button
            class="w-full text-left px-4 py-3 rounded-lg font-medium flex items-center transition-all duration-300"
            :class="
              currentTab === 'user'
                ? 'bg-primary-light text-primary'
                : 'hover:bg-gray-100 text-gray-700'
            "
            @click="currentTab = 'user'"
          >
            <i class="fas fa-users mr-3 w-5 text-center" />
            <span>用户管理</span>
          </button>

          <button
            class="w-full text-left px-4 py-3 rounded-lg font-medium flex items-center transition-all duration-300"
            :class="
              currentTab === 'role'
                ? 'bg-primary-light text-primary'
                : 'hover:bg-gray-100 text-gray-700'
            "
            @click="currentTab = 'role'"
          >
            <i class="fas fa-shield-alt mr-3 w-5 text-center" />
            <span>权限与角色管理</span>
          </button>

          <button
            class="w-full text-left px-4 py-3 rounded-lg font-medium flex items-center transition-all duration-300"
            :class="
              currentTab === 'settings'
                ? 'bg-primary-light text-primary'
                : 'hover:bg-gray-100 text-gray-700'
            "
            @click="currentTab = 'settings'"
          >
            <i class="fas fa-cog mr-3 w-5 text-center" />
            <span>系统参数设置</span>
          </button>

        </nav>
      </div>

      <!-- 右侧内容区 -->
      <div class="lg:w-4/5 space-y-6">
        <!-- 用户管理 -->
        <section v-if="currentTab === 'user'" class="space-y-6">
          <div class="bg-white rounded-xl shadow-card p-6">
            <div class="flex justify-between items-center mb-6">
              <h2 class="text-xl font-bold text-gray-700">用户管理</h2>
              <div class="flex space-x-2">
                <div class="relative">
                  <input
                    type="text"
                    placeholder="搜索用户名或邮箱..."
                    class="pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300 text-sm"
                  />
                  <i
                    class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-xs"
                  />
                </div>
                <select
                  class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
                >
                  <option>所有状态</option>
                  <option>启用</option>
                  <option>禁用</option>
                </select>
              </div>
            </div>

            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr class="bg-gray-50">
                    <th
                      class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      用户名
                    </th>
                    <th
                      class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      邮箱
                    </th>
                    <th
                      class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      状态
                    </th>
                    <th
                      class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      创建时间
                    </th>
                    <th
                      class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      操作
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <!-- 示例行：后端接好接口后替换为 v-for -->
                  <tr class="hover:bg-gray-50 transition-all duration-300">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <div
                          class="h-10 w-10 rounded-full bg-primary-light flex items-center justify-center text-primary font-medium"
                        >
                          AD
                        </div>
                        <div class="ml-3">
                          <div class="text-sm font-medium text-gray-700">
                            admin
                          </div>
                          <div class="text-xs text-gray-500">
                            系统管理员（示例）
                          </div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      admin@example.com
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        class="px-2 py-1 text-xs rounded-full bg-success-light text-success"
                      >
                        启用
                      </span>
                    </td>
                    <td
                      class="px-6 py-4 whitespace-nowrap text-sm text-gray-500"
                    >
                      2023-01-15
                    </td>
                    <td
                      class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
                    >
                      <button
                        class="text-primary hover:text-primary/80 mr-3 transition-colors"
                      >
                        编辑
                      </button>
                      <button
                        class="text-gray-500 hover:text-gray-700 mr-3 transition-colors"
                      >
                        详情
                      </button>
                      <button
                        class="text-danger hover:text-danger/80 transition-colors"
                      >
                        禁用
                      </button>
                    </td>
                  </tr>

                  <!-- 占位：无数据时 -->
                  <tr>
                    <td
                      colspan="5"
                      class="px-6 py-10 text-center text-sm text-gray-400"
                    >
                      用户数据将由后端接口返回，这里仅为布局占位
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- 分页占位，后端分页接入后替换 -->
            <div class="flex justify-between items-center mt-6 text-sm text-gray-500">
              <div>显示 0-0 条，共 0 条（等待后端数据）</div>
              <div class="flex space-x-1">
                <button
                  class="px-3 py-1 border border-gray-200 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled
                >
                  上一页
                </button>
                <button
                  class="px-3 py-1 border border-primary bg-primary text-white rounded"
                  disabled
                >
                  1
                </button>
                <button
                  class="px-3 py-1 border border-gray-200 rounded hover:bg-gray-50"
                  disabled
                >
                  下一页
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- 权限与角色管理 -->
        <section v-else-if="currentTab === 'role'" class="space-y-6">
          <div class="bg-white rounded-xl shadow-card p-6">
            <div class="flex justify-between items-center mb-6">
              <h2 class="text-xl font-bold text-gray-700">角色管理</h2>
              <button
                class="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg flex items-center transition-all duration-300 shadow-sm hover:shadow"
              >
                <i class="fas fa-plus mr-2" />
                <span>新增角色</span>
              </button>
            </div>

            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr class="bg-gray-50">
                    <th
                      class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      角色名称
                    </th>
                    <th
                      class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      角色说明
                    </th>
                    <th
                      class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      成员数量
                    </th>
                    <th
                      class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      创建时间
                    </th>
                    <th
                      class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      操作
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <!-- 示例数据行 -->
                  <tr class="hover:bg-gray-50 transition-all duration-300">
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-700">
                      系统管理员
                    </td>
                    <td class="px-6 py-4 text-sm text-gray-500">
                      拥有系统全部操作权限（示例）
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      1
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      2023-01-10
                    </td>
                    <td
                      class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
                    >
                      <button
                        class="text-primary hover:text-primary/80 mr-3 transition-colors"
                      >
                        编辑权限
                      </button>
                      <button
                        class="text-gray-500 hover:text-gray-700 transition-colors"
                      >
                        分配成员
                      </button>
                    </td>
                  </tr>

                  <!-- 占位无数据 -->
                  <tr>
                    <td
                      colspan="5"
                      class="px-6 py-10 text-center text-sm text-gray-400"
                    >
                      角色列表由后端提供，这里仅做结构展示
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 权限树配置区域（简化版，占位） -->
          <div class="bg-white rounded-xl shadow-card p-6">
            <h2 class="text-xl font-bold text-gray-700 mb-6">权限配置</h2>
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                选择角色
              </label>
              <select
                class="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
              >
                <option>系统管理员（示例）</option>
                <option>普通用户（示例）</option>
                <option>审计员（示例）</option>
              </select>
            </div>

            <div class="border border-gray-200 rounded-lg p-4 space-y-4">
              <!-- 这里保留几组典型权限，后端接数据时直接替换 -->
              <div class="flex items-center">
                <input
                  id="perm-all"
                  type="checkbox"
                  class="w-4 h-4 text-primary rounded focus:ring-primary/50"
                />
                <label
                  for="perm-all"
                  class="ml-2 text-sm font-medium text-gray-700"
                >
                  全选权限（示例）
                </label>
              </div>
              <div class="space-y-3">
                <div>
                  <div class="flex items-center">
                    <input
                      id="perm-user"
                      type="checkbox"
                      class="w-4 h-4 text-primary rounded focus:ring-primary/50"
                    />
                    <label
                      for="perm-user"
                      class="ml-2 text-sm font-medium text-gray-700"
                    >
                      用户管理
                    </label>
                  </div>
                  <div class="ml-6 mt-2 grid grid-cols-2 gap-2 text-sm text-gray-600">
                    <label class="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        class="w-4 h-4 text-primary rounded focus:ring-primary/50"
                      />
                      <span>查看用户</span>
                    </label>
                    <label class="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        class="w-4 h-4 text-primary rounded focus:ring-primary/50"
                      />
                      <span>添加用户</span>
                    </label>
                    <label class="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        class="w-4 h-4 text-primary rounded focus:ring-primary/50"
                      />
                      <span>编辑用户</span>
                    </label>
                    <label class="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        class="w-4 h-4 text-primary rounded focus:ring-primary/50"
                      />
                      <span>禁用 / 删除用户</span>
                    </label>
                  </div>
                </div>

                <div>
                  <div class="flex items-center">
                    <input
                      id="perm-log"
                      type="checkbox"
                      class="w-4 h-4 text-primary rounded focus:ring-primary/50"
                    />
                    <label
                      for="perm-log"
                      class="ml-2 text-sm font-medium text-gray-700"
                    >
                      日志管理
                    </label>
                  </div>
                  <div class="ml-6 mt-2 grid grid-cols-2 gap-2 text-sm text-gray-600">
                    <label class="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        class="w-4 h-4 text-primary rounded focus:ring-primary/50"
                      />
                      <span>查看操作日志</span>
                    </label>
                    <label class="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        class="w-4 h-4 text-primary rounded focus:ring-primary/50"
                      />
                      <span>导出日志</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <div class="flex justify-end space-x-3 mt-6">
              <button
                class="px-4 py-2 border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50 transition-all duration-300 text-sm"
              >
                取消
              </button>
              <button
                class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300 text-sm"
              >
                保存权限
              </button>
            </div>
          </div>
        </section>

        <!-- 系统参数设置 -->
        <section v-else-if="currentTab === 'settings'" class="space-y-6">
          <div class="bg-white rounded-xl shadow-card p-6">
            <h2 class="text-xl font-bold text-gray-700 mb-6">系统运行配置</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  系统名称
                </label>
                <input
                  type="text"
                  value="爱心捐赠管理系统"
                  class="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  区块链节点地址
                </label>
                <input
                  type="text"
                  value="http://127.0.0.1:8545"
                  class="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  数据同步周期（分钟）
                </label>
                <input
                  type="number"
                  min="1"
                  value="30"
                  class="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  系统 Logo
                </label>
                <div
                  class="mt-1 flex items-center justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg"
                >
                  <div class="space-y-1 text-center">
                    <i
                      class="fas fa-cloud-upload-alt text-gray-400 text-3xl mb-2"
                    />
                    <div class="flex text-sm text-gray-600 justify-center">
                      <label
                        for="logo-upload"
                        class="relative cursor-pointer bg-white rounded-md font-medium text-primary hover:text-primary/80"
                      >
                        <span>上传图片</span>
                        <input id="logo-upload" type="file" class="sr-only" />
                      </label>
                      <p class="pl-1">或拖放文件</p>
                    </div>
                    <p class="text-xs text-gray-500">
                      支持 PNG / JPG / GIF，最大 2MB（示例）
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-card p-6">
            <h2 class="text-xl font-bold text-gray-700 mb-6">安全配置</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  密码策略
                </label>
                <select
                  class="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
                >
                  <option>至少 6 位字符（示例）</option>
                  <option selected>至少 8 位，包含字母和数字（示例）</option>
                  <option>
                    至少 10 位，包含大小写字母、数字和特殊字符（示例）
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  会话过期时间（分钟）
                </label>
                <input
                  type="number"
                  min="5"
                  value="30"
                  class="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  登录失败锁定次数
                </label>
                <input
                  type="number"
                  min="0"
                  value="5"
                  class="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  锁定时长（分钟）
                </label>
                <input
                  type="number"
                  min="1"
                  value="15"
                  class="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
                />
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-card p-6">
            <h2 class="text-xl font-bold text-gray-700 mb-6">通知配置</h2>
            <div class="mb-4">
              <label class="flex items-center">
                <input
                  type="checkbox"
                  class="w-4 h-4 text-primary rounded focus:ring-primary/50"
                  checked
                />
                <span class="ml-2 text-sm font-medium text-gray-700">
                  启用邮件通知（示例）
                </span>
              </label>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  SMTP 服务器
                </label>
                <input
                  type="text"
                  value="smtp.example.com"
                  class="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  SMTP 端口
                </label>
                <input
                  type="number"
                  value="587"
                  class="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  发件人邮箱
                </label>
                <input
                  type="email"
                  value="notifications@example.com"
                  class="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  发件人名称
                </label>
                <input
                  type="text"
                  value="系统通知"
                  class="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
                />
              </div>
            </div>
            <div class="flex justify-end space-x-3 mt-6">
              <button
                class="px-4 py-2 border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50 transition-all duration-300 text-sm"
              >
                重置
              </button>
              <button
                class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300 text-sm"
              >
                保存配置
              </button>
            </div>
          </div>
        </section>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// 当前激活的右侧 tab
const currentTab = ref<'user' | 'role' | 'settings'>('user')
</script>