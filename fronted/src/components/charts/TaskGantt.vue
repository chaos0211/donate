<template><div ref="el" class="w-full h-80"></div></template>
<script setup lang="ts">
import * as echarts from "echarts"; import { onMounted, ref } from "vue";
const el = ref<HTMLDivElement|null>(null);
onMounted(()=> {
  const chart = echarts.init(el.value!);
  const ms = (s:string)=> new Date(s).getTime();
  chart.setOption({
    tooltip:{ formatter:(p:any)=>`${p.data.name}<br/>开始: ${p.data.start}<br/>结束: ${p.data.end}` },
    grid:{ left:"10%", right:"10%", bottom:"15%" },
    xAxis:{ type:"time" }, yAxis:{ type:"category", data:["数据采集","数据清洗","数据分析","数据预测","报表生成"] },
    series:[{ type:"bar", barWidth:20, label:{ show:true, position:"inside", color:"#fff",
      formatter:(p:any)=>{ const s=new Date(p.data.value[0]).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
                           const e=new Date(p.data.value[1]).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}); return `${s} - ${e}`;}},
      data:[
        { name:"数据采集", start:"2023-06-15 08:00", end:"2023-06-15 09:30", value:[ms("2023-06-15 08:00"),ms("2023-06-15 09:30"),0], itemStyle:{ color:"#00B42A" }},
        { name:"数据清洗", start:"2023-06-15 09:30", end:"2023-06-15 10:45", value:[ms("2023-06-15 09:30"),ms("2023-06-15 10:45"),1], itemStyle:{ color:"#00B42A" }},
        { name:"数据分析", start:"2023-06-15 10:45", end:"2023-06-15 12:30", value:[ms("2023-06-15 10:45"),ms("2023-06-15 12:30"),2], itemStyle:{ color:"#00B42A" }},
        { name:"数据预测", start:"2023-06-15 12:30", end:"2023-06-15 14:15", value:[ms("2023-06-15 12:30"),ms("2023-06-15 14:15"),3], itemStyle:{ color:"#FF7D00" }},
        { name:"报表生成", start:"2023-06-15 14:15", end:"2023-06-15 15:00", value:[ms("2023-06-15 14:15"),ms("2023-06-15 15:00"),4], itemStyle:{ color:"#165DFF" }},
      ]}],
  });
  window.addEventListener("resize", ()=>chart.resize());
});
</script>
