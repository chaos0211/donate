// src/api/analytics.ts
import service from "./http";
import http from './http'

/** 大屏：最近日期的 TopN 应用（免费=1，付费=0，畅销=2） */
export const getTopApps = (params: {
  brand_id: number | string;
  country?: string;
  device?: string;
  limit?: number;
}) => service.get("/api/v1/analytics/top-apps", { params }).then(r => r.data);

/** 大屏/对比：TopN 应用在最近 N 天的排名趋势 */
export const getTopnTrend = (params: {
  days?: number;      // 默认 7
  top?: number;       // 默认 5
  brand_id?: 0|1|2;   // 默认 1
  country?: string;   // 默认 cn
  device?: string;    // 默认 iphone
}) => service.get("/api/v1/analytics/topn-trend", { params }).then(r => r.data);

/** 对比：应用搜索（模糊 app_name + 精确 app_id） */
export const searchApps = (params: {
  q: string;          // 关键词
  country?: string;
  device?: string;
  chart_date?: string;  // 可选：用于限定最近窗口
  limit?: number;
}) => service.get("/api/v1/apps/search", { params }).then(r => r.data);

/** 对比：应用详情（含基础信息 & 近 N 天趋势） */
export const getAppDetail = (appId: string, params?: {
  country?: string;
  device?: string;
  window?: number;   // 7/30/180/360
}) => service.get(`/api/v1/apps/${appId}`, { params }).then(r => r.data);

export interface VolatilityParams {
  range: number;                  // 7 | 30 | 180 | 365
  brand_id: 0|1|2;                // 免费1/付费0/畅销2（按你的后端定义来）
  country: string;                // 'cn' 等
  device: string;                 // 'iphone' / 'android'
}

export async function getVolatilityTrend(params: VolatilityParams) {
  const { data } = await http.get('/api/v1/analytics/volatility-trend', { params })
  // 期望后端返回: { labels: string[]; values: number[] }
  return data as { labels: string[]; values: number[] }
}

// 入参（随前端筛选同步）
export interface OverviewKpisParams {
  country: string;
  device: string;
  brand_id: 0 | 1 | 2;   // 0=付费, 1=免费, 2=畅销（按你的定义）
  days: number;          // 7 / 30 / 90 / 180 / 365 等
}

// 返回结构（前端四个卡片所需）
export interface OverviewKpisResp {
  new_entries: number;                     // 新进榜
  dropped_entries: number;                 // 掉榜
  top_genre: { name: string; pct: number };// 热度最高类别及占比
  volatility_index: number;                // 整体波动指数（两位小数）
}

// 统一获取 KPI（先用占位，后端就绪替换为真实接口）
export async function getOverviewKpis(params: OverviewKpisParams): Promise<OverviewKpisResp> {
  const { data } = await http.get('/api/v1/analytics/overview-kpis', { params })
  return data as OverviewKpisResp
}

export async function getStableTop10(params: {
  days: number; brand_id: number; country: string; device: string; limit?: number; min_presence?: number;
}) {
  const { data } = await http.get('/api/v1/analytics/stable-top10', { params })
  return data
}

export async function getVolatileTop10(params: {
  days: number; brand_id: number; country: string; device: string; limit?: number; min_presence?: number;
}) {
  const { data } = await http.get('/api/v1/analytics/volatile-top10', { params })
  return data
}

export async function getGenreTrend(params: {
  days:number; brand_id:number; country:string; device:string; genre:string
}) {
  const { data } = await http.get('/api/v1/analytics/genre-trend', { params })
  return data
}

export async function getGenreGrowth(params: {
  days: number;
  brand_id: number;
  country: string;
  device: string;
  genre: string;
}) {
  const { data } = await http.get('/api/v1/analytics/genre-growth', { params })
  return data
}

export async function getGenres(params: {
  days: number;
  brand_id: number;
  country: string;
  device: string;
}) {
  const { data } = await http.get('/api/v1/analytics/genres', { params });
  // 预期 { items: string[] }
  return data?.items ?? [];
}

// 特征重要性热力图
export async function getFeatureImportance(params: { days: number; brand_id: number; country: string; device: string }) {
  const { data } = await http.get("/api/v1/analytics/feature-importance", { params })
  return data
}