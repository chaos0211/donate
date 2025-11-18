<template><div ref="el" class="w-full h-80"></div></template>
<script setup lang="ts">
import * as echarts from "echarts"; import { onMounted, ref } from "vue";
const el = ref<HTMLDivElement|null>(null);
onMounted(()=> {
  const chart = echarts.init(el.value!);
  chart.setOption({
    tooltip:{ trigger:"axis", axisPointer:{ type:"cross", label:{ backgroundColor:"#6a7985" }}},
    legend:{ data:["手机应用市场","微信","抖音","支付宝","淘宝"], top:0 },
    grid:{ left:"3%", right:"4%", bottom:"3%", containLabel:true },
    xAxis:[{ type:"category", boundaryGap:false, data:["6/10","6/11","6/12","6/13","6/14","6/15","6/16"]}],
    yAxis:[{ type:"value", max:20, inverse:true }],
    series:[
      { name:"手机应用市场", type:"line", stack:"Total", areaStyle:{}, data:[1,1,1,1,1,1,1] },
      { name:"微信", type:"line", stack:"Total", areaStyle:{}, data:[2,2,3,2,2,2,2] },
      { name:"抖音", type:"line", stack:"Total", areaStyle:{}, data:[3,3,2,3,3,3,3] },
      { name:"支付宝", type:"line", stack:"Total", areaStyle:{}, data:[4,4,4,4,5,4,4] },
      { name:"淘宝", type:"line", stack:"Total", areaStyle:{}, data:[5,5,5,5,4,5,5] },
    ],
  });
  window.addEventListener("resize", ()=>chart.resize());
});
</script>
