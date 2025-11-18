<template><div ref="el" class="w-full h-80"></div></template>
<script setup lang="ts">
import * as echarts from "echarts"; import { onMounted, ref } from "vue";
const el = ref<HTMLDivElement|null>(null);
onMounted(async ()=>{
  const chart = echarts.init(el.value!);
  const geo = await fetch("/china.json").then(r=>r.json());
  echarts.registerMap("china", geo as any);
  chart.setOption({
    tooltip:{ trigger:"item" },
    visualMap:{ min:0, max:200, left:"left", bottom:0, text:["高","低"], calculable:true },
    series:[{ name:"应用数量", type:"map", map:"china", roam:false, label:{ show:true },
      data:[
        {name:"北京",value:150},{name:"天津",value:80},{name:"上海",value:180},{name:"重庆",value:90},
        {name:"河北",value:70},{name:"河南",value:65},{name:"云南",value:50},{name:"辽宁",value:60},
        {name:"黑龙江",value:45},{name:"湖南",value:75},{name:"安徽",value:60},{name:"山东",value:90},
        {name:"新疆",value:40},{name:"江苏",value:120},{name:"浙江",value:130},{name:"江西",value:55},
        {name:"湖北",value:85},{name:"广西",value:50},{name:"甘肃",value:40},{name:"山西",value:50},
        {name:"内蒙古",value:35},{name:"陕西",value:70},{name:"吉林",value:45},{name:"福建",value:95},
        {name:"贵州",value:45},{name:"广东",value:170},{name:"青海",value:30},{name:"西藏",value:25},
        {name:"四川",value:100},{name:"宁夏",value:35},{name:"海南",value:40},{name:"台湾",value:50},
        {name:"香港",value:60},{name:"澳门",value:30}
      ]}],
  });
  window.addEventListener("resize", ()=>chart.resize());
});
</script>
