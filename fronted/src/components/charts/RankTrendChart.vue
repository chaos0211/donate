<template>
  <div class="rank-trend-chart" :style="{ position:'relative', minHeight: '260px', overflowX:'hidden' }">
    <div v-if="loading" class="chart-placeholder">加载中…</div>
    <div v-else-if="error" class="chart-placeholder">{{ error }}</div>
    <div v-else-if="!dates.length || !series.length" class="chart-placeholder">暂无数据</div>

    <svg v-else :width="width" :height="height" :viewBox="`0 0 ${width} ${height}`">
      <!-- Y 轴网格 & 刻度（显示具体排名数值） -->
      <g font-size="10" fill="#888">
        <g v-for="(t, ti) in yTicks" :key="'yt-'+ti">
          <line :x1="padding" :x2="width - padding" :y1="t.y" :y2="t.y" stroke="#eee" />
          <text :x="padding - 6" :y="t.y + 3" text-anchor="end">{{ t.label }}</text>
        </g>
      </g>

      <!-- X 轴刻度：最多 7 段（组件内部依据 dates 自动计算） -->
      <g font-size="10" fill="#888">
        <text v-for="(tx, i) in xTicks" :key="'xt-'+i" :x="tx.x" y="295" :text-anchor="tx.anchor">{{ tx.label }}</text>
      </g>

      <!-- 边框 -->
      <rect :x="padding" y="10" :width="width - padding*2" height="260" fill="none" stroke="#eee" />

      <!-- 各应用的平均值虚线（仅基于有数据的点） -->
      <g v-if="showAverage" v-for="(s, si) in series" :key="'avg-'+(s.app_id||si)">
        <line :x1="padding" :x2="width - padding" :y1="avgY(si)" :y2="avgY(si)"
              :stroke="seriesColor(si)" stroke-dasharray="4 4" opacity="0.5" />
      </g>

      <!-- 多条折线（跳过缺失点，连线不断） -->
      <g v-for="(s, si) in series" :key="s.app_id || si">
        <path v-for="(d, di) in buildPaths(s.points)" :key="di" :d="d"
              fill="none" :stroke="seriesColor(si)" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round" />
      </g>
    </svg>
  </div>
</template>

<script>
export default {
  name: 'RankTrendChart',
  props: {
    dates: { type: Array, default: () => [] },           // ["YYYY-MM-DD", ...]
    series: { type: Array, default: () => [] },          // [{ app_id, points: [[date, rank|null], ...] }, ...]
    loading: { type: Boolean, default: false },
    error: { type: String, default: '' },
    width: { type: Number, default: 800 },
    height: { type: Number, default: 300 },
    padding: { type: Number, default: 20 },
    showAverage: { type: Boolean, default: true },
    palette: { type: Array, default: () => ['#5470C6', '#91CC75', '#FAC858', '#EE6666', '#73C0DE', '#3BA272'] }
  },
  data() {
    return {
      xTicks: [],
      yTicks: [],
      yMin: 1,
      yMax: 10,
    }
  },
  watch: {
    dates: { immediate: true, handler() { this.computeScales() } },
    series: { immediate: true, deep: true, handler() { this.computeScales() } },
    width() { this.computeScales() },
    height() { this.computeScales() },
  },
  methods: {
    seriesColor(i) { return this.palette[i % this.palette.length] },
    computeScales() {
      // Y 轴范围（仅用有数据的排名）
      let minR = Infinity, maxR = -Infinity
      for (const s of this.series) {
        for (const [, r] of (s.points || [])) {
          if (typeof r === 'number') {
            if (r < minR) minR = r
            if (r > maxR) maxR = r
          }
        }
      }
      if (!isFinite(minR) || !isFinite(maxR)) { minR = 1; maxR = 10 }
      if (minR === maxR) maxR = minR + 1
      this.yMin = Math.max(1, Math.floor(minR))
      this.yMax = Math.ceil(maxR)

      // 5 条水平网格线
      const lines = 5
      const innerH = 260, topY = 10
      const ys = []
      for (let i = 0; i < lines; i++) {
        const t = i/(lines-1) // 0..1 自上而下
        const rank = this.yMin + (this.yMax - this.yMin) * (1 - t)
        const y = topY + t * innerH
        ys.push({ y, label: Math.round(rank) })
      }
      this.yTicks = ys

      // X 轴：最多 7 段（7天逐日；<=30 每4天；其余按等分）
      const n = this.dates.length
      this.xTicks = []
      if (!n) return
      let step
      if (n <= 7) step = 1
      else if (n <= 30) step = 4
      else step = Math.ceil(n / 7)

      const w = this.width - this.padding*2
      const dx = n>1 ? w/(n-1) : 0
      const last = n - 1

      for (let i = 0; i < n; i += step) {
        const x = this.padding + i*dx
        const raw = String(this.dates[i] || '')
        const label = raw.slice(5).replace('-', '/').replace(/^0/, '').replace('/0', '/')
        this.xTicks.push({ x, label, anchor:'middle' })
      }
      // 确保包含最后一天
      const rawEnd = String(this.dates[last] || '')
      const endLabel = rawEnd.slice(5).replace('-', '/').replace(/^0/, '').replace('/0', '/')
      if (this.xTicks[this.xTicks.length-1]?.label !== endLabel) {
        const x = this.padding + last*dx
        this.xTicks.push({ x, label: endLabel, anchor:'end' })
      } else {
        if (this.xTicks.length) {
          this.xTicks[0].anchor = 'start'
          this.xTicks[this.xTicks.length-1].anchor = 'end'
        }
      }
    },
    avgY(seriesIndex) {
      const s = this.series[seriesIndex]
      if (!s) return 0
      let sum = 0, cnt = 0
      for (const [, r] of (s.points || [])) {
        if (typeof r === 'number') { sum += r; cnt++ }
      }
      const avg = cnt ? sum / cnt : (this.yMin + this.yMax) / 2
      const innerH = 260, topY = 10
      const t = (avg - this.yMin) / (this.yMax - this.yMin)  // 0..1 自上而下
      return topY + t * innerH
    },
    buildPaths(points = []) {
      const xs = this.dates
      if (!xs || !xs.length) return []
      const w  = this.width - this.padding * 2
      const h  = 260
      const ox = this.padding, oy = 10
      // 全局最大名次（用于 y 缩放）
      let maxRank = 0
      for (const s of this.series) {
        for (const p of (s.points || [])) {
          const r = p[1]
          if (typeof r === 'number' && r > maxRank) maxRank = r
        }
      }
      if (maxRank < 10) maxRank = 10
      const dx = xs.length > 1 ? w / (xs.length - 1) : 0
      const paths = []
      let seg = ''
      let open = false
      for (let i = 0; i < xs.length; i++) {
        const r = points[i] ? points[i][1] : null
        const x = ox + i * dx
        if (r === null || r === undefined) {
          // 跳过缺失点，不中断折线
          continue
        }
        const y = oy + (r - 1) / (maxRank - 1) * h
        if (!open) { seg = `${x},${y}`; open = true } else { seg += ` L${x},${y}` }
      }
      if (seg) paths.push(`M${seg}`)
      return paths
    },
  }
}
</script>