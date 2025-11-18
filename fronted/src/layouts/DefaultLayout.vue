<template>
  <div class="h-screen flex flex-col" @click="onRootClick">
    <header class="bg-white h-16 border-b border-light-100 px-4 md:px-6 flex items-center justify-between shadow-sm">
      <div class="flex items-center">
        <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center mr-2">
          <i class="fas fa-chart-line text-primary"></i>
        </div>
        <h1 class="text-lg font-semibold hidden md:block">智慧捐赠平台</h1>
      </div>
      <div class="hidden md:flex">
        <div class="relative">
          <i class="fas fa-search text-info absolute left-3 top-3"></i>
          <input class="pl-10 pr-4 py-2 rounded-lg bg-light-100 border-0 outline-none text-sm w-64" placeholder="全局搜索..." />
        </div>
      </div>
      <div class="flex items-center gap-3 relative">
        <button class="p-2 rounded-lg hover:bg-light-100 relative">
          <i class="fas fa-bell"></i>
          <span class="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full"></span>
        </button>
        <button class="flex items-center focus:outline-none" @click.stop="toggleUserMenu" aria-label="User menu">
          <img class="w-8 h-8 rounded-full border" src="https://design.gemcoder.com/staticResource/echoAiSystemImages/b4836a22bb7346e0969480410c37b5b5.png" />
        </button>
        <div v-if="showUserMenu" class="absolute right-0 top-10 mt-2 w-44 bg-white border border-light-100 rounded-lg shadow-dropdown z-50">
          <div class="px-3 py-2 text-sm text-info border-b border-light-100">{{ currentUserLabel }}</div>
          <button type="button" class="w-full text-left px-3 py-2 text-sm hover:bg-light-100" @click.stop="goProfile">个人信息（功能待添加）</button>
          <button type="button" class="w-full text-left px-3 py-2 text-sm text-danger hover:bg-danger/5" @click.stop="logout">退出登录</button>
        </div>
      </div>
    </header>

    <div class="flex flex-1 overflow-hidden">
      <aside class="w-64 bg-white border-r border-light-100 flex-shrink-0 hidden md:flex flex-col">
        <nav class="flex-1 overflow-y-auto p-4">
          <ul class="space-y-1">
            <li>
              <RouterLink to="/cockpit" class="flex items-center px-3 py-2 text-sm font-medium rounded-lg">
                <i class="fas fa-tachometer-alt w-5 h-5 mr-3"></i> 首页总览
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/DonateManager" class="flex items-center px-3 py-2 text-sm font-medium rounded-lg">
                <i class="fas fa-folder-open w-5 h-5 mr-3"></i> 公益项目管理
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/blank" class="flex items-center px-3 py-2 text-sm font-medium rounded-lg">
                <i class="fas fa-hand-holding-heart w-5 h-5 mr-3"></i> 项目参与
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/BlockchainManager" class="flex items-center px-3 py-2 text-sm font-medium rounded-lg">
                <i class="fas fa-link w-5 h-5 mr-3"></i> 区块链管理
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/SystemManager" class="flex items-center px-3 py-2 text-sm font-medium rounded-lg">
                <i class="fas fa-cog w-5 h-5 mr-3"></i> 系统管理
              </RouterLink>
            </li>
          </ul>
        </nav>
        <div class="p-4 border-t border-light-100">
          <div class="bg-light-100 rounded-lg p-3 text-xs">
            <i class="fas fa-info-circle text-primary mr-2"></i>
            <div class="inline-block align-top">
              <div>系统版本: v1.0.0</div>
              <div class="text-info mt-1">上次更新: 2023-06-15</div>
            </div>
          </div>
        </div>
      </aside>

      <main class="flex-1 overflow-y-auto bg-light-200 p-4 md:p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const showUserMenu = ref(false)
const currentUserLabel = (localStorage.getItem('session_user') || '未登录')

function toggleUserMenu() {
  showUserMenu.value = !showUserMenu.value
}
function onRootClick() {
  if (showUserMenu.value) showUserMenu.value = false
}
function goProfile() {
  showUserMenu.value = false
  alert('个人信息功能待添加')
}
function logout() {
  localStorage.removeItem('session_user')
  showUserMenu.value = false
  router.push('/login')
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') showUserMenu.value = false
}
onMounted(() => document.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => document.removeEventListener('keydown', onKeydown))
</script>
<style>
.router-link-exact-active {
  @apply bg-primary/10 text-primary;
}
/* Windowed fullscreen (triggered by BigScreen.vue adding class on <html>) */
html.edge-full-active .h-screen > header { display: none !important; }
html.edge-full-active .h-screen > .flex > aside { display: none !important; }
html.edge-full-active .h-screen > .flex > main { width: 100% !important; }
</style>
