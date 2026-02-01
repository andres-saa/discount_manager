const BASE = 'https://discounts.salchimonster.com'

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = path.startsWith('http') ? path : `${BASE}${path}`
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail))
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

export const api = {
  sites: {
    list: () => request<Array<Record<string, unknown>>>('/sites'),
    get: (id: number) => request<Record<string, unknown>>(`/sites/${id}`),
  },
  menus: {
    get: (siteId: number) => request<Record<string, unknown>>(`/menus/site/${siteId}`),
    categories: (siteIds: number[] | null) => {
      const params = siteIds?.length ? `?site_ids=${siteIds.join(',')}` : ''
      return request<Array<{ id: string; name: string }>>(`/menus/categories${params}`)
    },
    products: (params: { site_ids: number[] | null; q?: string; limit?: number; offset?: number; ids?: string[] }) => {
      const sp = new URLSearchParams()
      if (params.site_ids?.length) sp.set('site_ids', params.site_ids.join(','))
      if (params.q) sp.set('q', params.q)
      if (params.limit != null) sp.set('limit', String(params.limit))
      if (params.offset != null) sp.set('offset', String(params.offset))
      if (params.ids?.length) sp.set('ids', params.ids.join(','))
      const query = sp.toString()
      return request<{ items: Array<{ id: string; name: string; category_id: string }>; total: number }>(`/menus/products${query ? `?${query}` : ''}`)
    },
  },
  folders: {
    list: () => request<Array<Record<string, unknown>>>('/folders'),
    get: (id: string) => request<Record<string, unknown>>(`/folders/${id}`),
    create: (body: Record<string, unknown>) => request<Record<string, unknown>>('/folders', { method: 'POST', body: JSON.stringify(body) }),
    update: (id: string, body: Record<string, unknown>) => request<Record<string, unknown>>(`/folders/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
    delete: (id: string, cascade = true) => request<void>(`/folders/${id}?cascade=${cascade}`, { method: 'DELETE' }),
  },
  discounts: {
    list: () => request<Array<Record<string, unknown>>>('/discounts'),
    get: (id: string) => request<Record<string, unknown>>(`/discounts/${id}`),
    create: (body: Record<string, unknown>) => request<Record<string, unknown>>('/discounts', { method: 'POST', body: JSON.stringify(body) }),
    update: (id: string, body: Record<string, unknown>) => request<Record<string, unknown>>(`/discounts/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
    delete: (id: string) => request<void>(`/discounts/${id}`, { method: 'DELETE' }),
  },
  cuponeras: {
    list: () => request<Array<Record<string, unknown>>>('/cuponeras'),
    get: (id: string) => request<Record<string, unknown>>(`/cuponeras/${id}`),
    create: (body: Record<string, unknown>) => request<Record<string, unknown>>('/cuponeras', { method: 'POST', body: JSON.stringify(body) }),
    update: (id: string, body: Record<string, unknown>) => request<Record<string, unknown>>(`/cuponeras/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
    delete: (id: string) => request<void>(`/cuponeras/${id}`, { method: 'DELETE' }),
  },
  cuponeraUsers: {
    list: (cuponeraId: string) => request<Array<Record<string, unknown>>>(`/cuponeras/${cuponeraId}/users`),
    get: (cuponeraId: string, userId: string) =>
      request<Record<string, unknown>>(`/cuponeras/${cuponeraId}/users/${userId}`),
    create: (cuponeraId: string, body: Record<string, unknown>) =>
      request<Record<string, unknown>>(`/cuponeras/${cuponeraId}/users`, { method: 'POST', body: JSON.stringify(body) }),
    update: (cuponeraId: string, userId: string, body: Record<string, unknown>) =>
      request<Record<string, unknown>>(`/cuponeras/${cuponeraId}/users/${userId}`, { method: 'PATCH', body: JSON.stringify(body) }),
    delete: (cuponeraId: string, userId: string) =>
      request<void>(`/cuponeras/${cuponeraId}/users/${userId}`, { method: 'DELETE' }),
  },
  redeem: (code: string, date?: string, recordUse = false) => {
    const params = new URLSearchParams({ code })
    if (date) params.set('date', date)
    if (recordUse) params.set('record_use', 'true')
    return request<{
      success: boolean
      message: string
      cuponera_name?: string
      discounts: Array<{ discount_id: string; discount: Record<string, unknown> }>
      uses_remaining_today?: number
      user?: { name: string; phone: string; email: string; address?: string }
    }>(`/redeem?${params}`)
  },
}
