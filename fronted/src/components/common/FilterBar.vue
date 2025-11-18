<template>
  <div class="card p-4">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <label class="block text-sm font-medium mb-2">日期范围</label>
        <div class="relative">
          <i class="fas fa-calendar text-info absolute left-3 top-3"></i>
          <input class="block w-full pl-10 pr-8 py-2 border border-light-100 rounded-lg focus:ring-2 focus:ring-primary/30 outline-none bg-white" placeholder="最近7天"/>
          <i class="fas fa-chevron-down text-info absolute right-3 top-3"></i>
        </div>
      </div>
      <div>
        <label class="block text-sm font-medium mb-2">地区</label>
        <div class="relative">
          <i class="fas fa-map-marker-alt text-info absolute left-3 top-3"></i>
          <select class="block w-full pl-10 pr-8 py-2 border border-light-100 rounded-lg focus:ring-2 focus:ring-primary/30 outline-none bg-white appearance-none">
            <option>全国</option><option>北京</option><option>上海</option><option>广州</option><option>深圳</option>
          </select>
          <i class="fas fa-chevron-down text-info absolute right-3 top-3"></i>
        </div>
      </div>
      <div>
        <label class="block text-sm font-medium mb-2">分类</label>
        <div class="relative">
          <i class="fas fa-tags text-info absolute left-3 top-3"></i>
          <select class="block w-full pl-10 pr-8 py-2 border border-light-100 rounded-lg focus:ring-2 focus:ring-primary/30 outline-none bg-white appearance-none">
            <option>全部分类</option><option>游戏</option><option>社交</option><option>工具</option><option>娱乐</option><option>教育</option>
          </select>
          <i class="fas fa-chevron-down text-info absolute right-3 top-3"></i>
        </div>
      </div>
    </div>
    <div class="mt-4 flex justify-end gap-3">
      <button class="px-4 py-2 border border-light-100 rounded-lg hover:bg-light-100">重置</button>
      <button class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90">应用筛选</button>
    </div>
  </div>
</template>
<script setup lang="ts"></script>
