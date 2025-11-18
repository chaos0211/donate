<template>
  <div class="card p-4">
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-semibold">{{ title }}</h3>
      <div class="flex items-center gap-2"><slot name="tools"/></div>
    </div>
    <slot />
  </div>
</template>
<script setup lang="ts">defineProps<{ title:string }>()</script>
