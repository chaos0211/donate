
import http from './http'

export type MetaFields = 'country' | 'device' | 'brand' | 'is_ad' | 'chart_date' | 'app_genre'

export interface MetaOptionsResponse {
  country?: string[]
  device?: string[]
  brand?: string[]
  is_ad?: number[] | boolean[]
  chart_date?: { min: string; max: string } | null
  app_genre?: string[]
}

export interface AppSearchItem {
  app_id: string
  app_name: string
  icon_url?: string
  publisher?: string
}

export interface AppSearchResponse {
  items: AppSearchItem[]
}

/**
 * 获取筛选下拉数据
 * @param fields 需要的字段列表（不传则服务端返回全部可选项）
 */
export async function fetchMetaOptions(fields?: MetaFields[]) {
  const params: Record<string, any> = {}
  if (fields && fields.length) params.fields = fields.join(',')
  const { data } = await http.get<MetaOptionsResponse>('/api/v1/meta/options', { params })
  return data
}

export interface SearchAppsParams {
  q: string
  limit?: number
  country?: string
  device?: string
  brand?: string // free/paid/grossing
  window?: number // 最近N天，与 date_from/date_to 互斥
  date_from?: string
  date_to?: string
}

/**
 * 应用搜索（按 app_id 精确、按 app_name 模糊；支持国家/设备/brand/时间窗口过滤）
 */
export async function searchApps(params: SearchAppsParams) {
  const qp: Record<string, any> = {}
  for (const k of ['q','limit','country','device','brand','window','date_from','date_to'] as const) {
    const v = (params as any)[k]
    if (v !== undefined && v !== null && v !== '') qp[k] = v
  }
  const { data } = await http.get<AppSearchResponse>('/api/v1/apps/search', { params: qp })
  return data
}

export default {
  fetchMetaOptions,
  searchApps,
}
