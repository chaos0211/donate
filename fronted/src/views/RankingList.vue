<template>
  <div class="page">
    <h2 class="title">手机应用榜单 · 榜单列表</h2>

    <!-- 筛选区 -->
    <form class="filters" @submit.prevent="onSearch">
      <div class="row">
        <label>
          榜单日期：
          <input type="date" v-model="q.chart_date" />
        </label>


        <label>
          是否广告（is_ad）：
          <select v-model="q.is_ad">
            <option value="">全部</option>
            <option :value="true">有</option>
            <option :value="false">无</option>
          </select>
        </label>
      </div>

      <div class="row">

        <label>
          国家（country）：
          <input type="text" v-model.trim="q.country" placeholder="默认 cn" />
        </label>

        <label>
          设备（device）：
          <input type="text" v-model.trim="q.device" placeholder="默认 iphone" />
        </label>

        <label>
          榜单细分（genre）：
          <input type="text" v-model.trim="q.genre" placeholder="如: GAME_ACTION" />
        </label>
      </div>

      <div class="row actions">
        <button type="submit">查询</button>
        <button type="button" class="ghost" @click="onReset">重置</button>
      </div>
    </form>

    <!-- 表格 -->
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th @click="sort('chart_date')">榜单日期 {{ sortIcon('chart_date') }}</th>
            <th @click="sort('update_time')">数据时间 {{ sortIcon('update_time') }}</th>
            <th @click="sort('last_release_time')">最后更新时间 {{ sortIcon('last_release_time') }}</th>
            <th @click="sort('country')">国家 {{ sortIcon('country') }}</th>
            <th @click="sort('device')">设备 {{ sortIcon('device') }}</th>
            <th @click="sort('genre')">类别 {{ sortIcon('genre') }}</th>

            <th @click="sort('index')">序位 {{ sortIcon('index') }}</th>
            <th>总榜</th>
            <th>游戏/应用</th>
            <th>分类排名</th>

            <th @click="sort('app_id')">App ID {{ sortIcon('app_id') }}</th>
            <th @click="sort('app_name')">应用名 {{ sortIcon('app_name') }}</th>
            <th>图标</th>
            <th @click="sort('publisher')">发行方 {{ sortIcon('publisher') }}</th>
            <th @click="sort('rating')">评分 {{ sortIcon('rating') }}</th>
            <th @click="sort('rating_num')">评分数 {{ sortIcon('rating_num') }}</th>
            <th @click="sort('keyword_cover')">关键词指数 {{ sortIcon('keyword_cover') }}</th>
            <th @click="sort('keyword_cover_top3')">Top3关键词 {{ sortIcon('keyword_cover_top3') }}</th>
            <th @click="sort('is_ad')">广告 {{ sortIcon('is_ad') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.id || (row.app_id + '-' + (row.index ?? ''))">
            <td>{{ row.chart_date }}</td>
            <td class="muted">{{ fmtDate(row.update_time) }}</td>
            <td class="muted">{{ fmtDate(row.last_release_time) }}</td>
            <td>{{ row.country }}</td>
            <td>{{ row.device }}</td>
            <td>{{ row.genre }}</td>

            <td class="num">{{ row.index }}</td>
            <td>
              <template v-if="row._rank_a">
                <span class="num">#{{ row._rank_a.ranking ?? '—' }}</span>
              </template>
            </td>
            <td>
              <template v-if="row._rank_b">
                <span class="num">#{{ row._rank_b.ranking ?? '—' }}</span>
              </template>
            </td>
            <td>
              <template v-if="row._rank_c">
                <span class="num">#{{ row._rank_c.ranking ?? '—' }}</span>
              </template>
            </td>

            <td class="mono">{{ row.app_id }}</td>
            <td>{{ row.app_name }}</td>
            <td>
              <img v-if="row.icon_url" :src="row.icon_url" alt="" class="icon" loading="lazy" width="28" height="28"/>
            </td>
            <td>{{ row.publisher }}</td>
            <td class="num">{{ fmtScore(row.rating) }}</td>
            <td class="num">{{ fmtNum(row.rating_num) }}</td>
            <td class="num">{{ fmtNum(row.keyword_cover) }}</td>
            <td class="num">{{ fmtNum(row.keyword_cover_top3) }}</td>
            <td>
              <span :class="['tag', row.is_ad ? 'on' : 'off']">{{ row.is_ad ? '有' : '无' }}</span>
            </td>
          </tr>
          <tr v-if="!loading && rows.length === 0">
            <td colspan="19" class="empty">暂无数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="pager">
      <button :disabled="page===1 || loading" @click="goto(1)">«</button>
      <button :disabled="page===1 || loading" @click="goto(page-1)">‹</button>
      <span>第 {{ page }} / {{ totalPages }} 页</span>
      <button :disabled="page===totalPages || loading" @click="goto(page+1)">›</button>
      <button :disabled="page===totalPages || loading" @click="goto(totalPages)">»</button>

      <span class="gap"></span>
      <label>每页
        <select v-model.number="pageSize" @change="onSearch">
          <option :value="10">10</option>
          <option :value="20">20</option>
          <option :value="50">50</option>
          <option :value="100">100</option>
        </select>
        条
      </label>
    </div>
  </div>
</template>

<script>
import { fetchRankings } from '@/api/rankings'

export default {
  name: 'RankingList',
  data() {
    return {
      q: {
        chart_date: '',
        is_ad: '',
        country: '',
        device: '',
        genre: '',
      },
      sortBy: 'index',
      sortDir: 'asc', // asc | desc
      page: 1,
      pageSize: 20,
      total: 0,
      rows: [],
      loading: false,
    }
  },
  computed: {
    totalPages() {
      const n = Math.ceil(this.total / this.pageSize)
      return n || 1
    }
  },
  mounted() {
    this.onSearch()
  },
  methods: {
    async onSearch() {
      this.page = 1
      await this.load()
    },
    onReset() {
      this.q = { chart_date:'', is_ad:'', country:'', device:'', genre:'' }
      this.sortBy = 'index'
      this.sortDir = 'asc'
      this.page = 1
      this.pageSize = 20
      this.load()
    },
    sort(field) {
      if (this.sortBy === field) {
        this.sortDir = this.sortDir === 'asc' ? 'desc' : 'asc'
      } else {
        this.sortBy = field
        this.sortDir = 'asc'
      }
      this.load()
    },
    sortIcon(field) {
      if (this.sortBy !== field) return '↕'
      return this.sortDir === 'asc' ? '↑' : '↓'
    },
    // brandName and fmtPrice removed
    fmtScore(s) {
      if (s === null || s === undefined || s === '') return ''
      const v = Number(s)
      if (isNaN(v)) return s
      return v.toFixed(2)
    },
    fmtDate(d) {
      if (!d) return ''
      const s = String(d)
      return s.length > 10 ? s.slice(0,10) : s
    },
    rank(val) {
      if (!val) return null
      if (typeof val === 'string') {
        try { return JSON.parse(val) } catch(e) { return null }
      }
      if (typeof val === 'object') return val
      return null
    },
    fmtNum(n) {
      if (n === null || n === undefined || n === '') return ''
      const v = Number(n)
      return isNaN(v) ? n : v.toLocaleString()
    },
    fmtTime(t) {
      return t ? String(t).replace('T',' ').replace('Z','') : ''
    },
    async goto(p) {
      if (p < 1 || p > this.totalPages || p === this.page) return
      this.page = p
      await this.load()
    },
    _parseJSON(val) {
      if (!val) return null
      if (typeof val === 'object') return val
      if (typeof val === 'string') {
        try { return JSON.parse(val) } catch (e) { return null }
      }
      return null
    },
    _prepareRow(row) {
      // Pre-parse JSON fields once to avoid parsing on every render
      row._rank_a = this._parseJSON(row.rank_a)
      row._rank_b = this._parseJSON(row.rank_b)
      row._rank_c = this._parseJSON(row.rank_c)
      return row
    },
    async load() {
      // request id guard to ignore stale responses
      this._rid = (this._rid || 0) + 1
      const rid = this._rid
      this.loading = true
      try {
        const params = {
          ...this.q,
          is_ad: this.q.is_ad === '' ? '' : (this.q.is_ad ? 1 : 0),
          sort_by: this.sortBy,
          sort_dir: this.sortDir,
          page: this.page,
          page_size: this.pageSize,
        }
        const cleaned = Object.fromEntries(
          Object.entries(params).filter(([_, v]) => v !== '' && v !== null && v !== undefined)
        )
        const res = await fetchRankings(cleaned)
        if (rid !== this._rid) return // ignore out-of-order response
        const items = Array.isArray(res.items) ? res.items : []
        this.rows = items.map(this._prepareRow)
        this.total = Number(res.total || 0)
      } catch (e) {
        if (rid !== this._rid) return
        console.error(e)
        this.rows = []
        this.total = 0
      } finally {
        if (rid === this._rid) this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.page { padding: 16px; }
.title { font-size: 20px; font-weight: 700; margin-bottom: 12px; }
.filters { background: #fafafa; border: 1px solid #eee; border-radius: 8px; padding: 12px; margin-bottom: 12px; }
.filters .row { display: flex; flex-wrap: wrap; gap: 12px 16px; margin-bottom: 8px; }
.filters label { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.filters .price { width: 120px; }
.filters .sep { margin: 0 4px; color: #888; }
.filters .actions { justify-content: flex-end; }
.filters button { padding: 6px 12px; border-radius: 6px; border: 1px solid #ddd; background: #fff; cursor: pointer; }
.filters .ghost { background: #f6f6f6; }

.table-wrap { overflow: auto; border: 1px solid #eee; border-radius: 8px; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { padding: 8px 10px; border-bottom: 1px solid #f0f0f0; white-space: nowrap; }
th { position: sticky; top: 0; background: #fff; cursor: pointer; user-select: none; }
td.num { text-align: right; font-variant-numeric: tabular-nums; }
td.mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
td.muted { color: #888; }
.empty { text-align: center; color: #999; padding: 24px 0; }

.icon { width: 28px; height: 28px; border-radius: 6px; object-fit: cover; box-shadow: 0 0 0 1px #eee; }

.pager { display: flex; align-items: center; gap: 8px; margin-top: 12px; }
.pager button { padding: 6px 10px; border: 1px solid #ddd; background: #fff; border-radius: 6px; cursor: pointer; }
.pager button:disabled { opacity: .5; cursor: not-allowed; }
.pager .gap { flex: 1; }
 .tag { display:inline-block; padding:2px 6px; border-radius:4px; font-size:12px; }
 .tag.on { background:#e6fffb; color:#08979c; }
 .tag.off { background:#f6ffed; color:#237804; }

tbody tr { content-visibility: auto; contain-intrinsic-size: 40px; }
</style>