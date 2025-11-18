<template><div ref="el" class="w-full h-80"></div></template>
<script setup lang="ts">
import * as echarts from "echarts"; import { onMounted, ref } from "vue";
const el = ref<HTMLDivElement|null>(null);
onMounted(()=> {
  const chart = echarts.init(el.value!);
  chart.setOption({
    tooltip:{ trigger:"item" },
    legend:{ orient:"vertical", left:"left" },
    series:[{ name:"分类占比", type:"pie", radius:["40%","70%"], itemStyle:{ borderRadius:10, borderColor:"#fff", borderWidth:2 },
      label:{ show:false, position:"center" }, emphasis:{ label:{ show:true, fontSize:16, fontWeight:"bold" }}, labelLine:{ show:false },
      data:[{value:325,name:"游戏"},{value:244,name:"社交"},{value:188,name:"工具"},{value:155,name:"娱乐"},{value:102,name:"教育"},{value:85,name:"其他"}]}],
  });
  window.addEventListener("resize", ()=>chart.resize());
});
</script>
