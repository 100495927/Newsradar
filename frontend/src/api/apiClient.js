const TOKEN_KEY = 'nr_token'

export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem(TOKEN_KEY)
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }
  return fetch(path, { ...options, headers })
}

// ---------------------------------------------------------------------------
// Stats — basado en GET /api/v1/stats del contrato (api_ag_comentado.py)
//
// El backend almacena métricas con la siguiente convención de nombres:
//   sources_count             → nº total de fuentes de información
//   news_count                → nº total de noticias procesadas
//   alerts_count              → nº total de alertas
//   rss_channels_count        → nº total de canales RSS
//   news_cat_<code>           → noticias de la categoría IPTC <code>
//   timeline_<YYYY-MM-DD>     → noticias procesadas en esa fecha
//   cloud_<code>_<palabra>    → frecuencia de <palabra> en categoría <code>
//
// Se usa el objeto Stats de id más alto (el más reciente).
// ---------------------------------------------------------------------------

let _statsPromise = null
let _statsCacheTs = 0
const CACHE_TTL_MS = 30_000

function _fetchStats() {
  const now = Date.now()
  if (_statsPromise && now - _statsCacheTs < CACHE_TTL_MS) return _statsPromise
  _statsCacheTs = now
  _statsPromise = apiFetch('/api/v1/stats')
    .then((r) => {
      if (!r.ok) throw new Error('Error al obtener estadísticas')
      return r.json()
    })
    .catch((err) => {
      _statsPromise = null
      throw err
    })
  return _statsPromise
}

async function _latestStats() {
  const list = await _fetchStats()
  if (!list || list.length === 0) return []
  const latest = list.reduce((a, b) => (a.id > b.id ? a : b))
  return latest.metrics ?? []
}

function _metricsMap(metrics) {
  const map = new Map()
  for (const m of metrics) map.set(m.name, m.value)
  return map
}

export async function getGlobalStats() {
  const metrics = await _latestStats()
  const map = _metricsMap(metrics)

  const n_noticias = map.get('news_count') ?? 0
  const n_fuentes = map.get('sources_count') ?? 0
  const n_alertas = map.get('alerts_count') ?? 0
  const n_canales_rss = map.get('rss_channels_count') ?? 0

  const noticias_por_categoria = []
  for (const [name, value] of map) {
    if (name.startsWith('news_cat_')) {
      noticias_por_categoria.push({ id: name.replace('news_cat_', ''), total: value })
    }
  }
  noticias_por_categoria.sort((a, b) => b.total - a.total)

  return { n_noticias, n_fuentes, n_alertas, n_canales_rss, noticias_por_categoria }
}

export async function getTimeline() {
  const metrics = await _latestStats()
  const entries = []
  for (const m of metrics) {
    if (m.name.startsWith('timeline_')) {
      entries.push({ fecha: m.name.replace('timeline_', ''), total: m.value })
    }
  }
  entries.sort((a, b) => a.fecha.localeCompare(b.fecha))
  return entries
}

export async function getWordCloud(categoryCode) {
  const metrics = await _latestStats()
  const prefix = `cloud_${categoryCode}_`
  const words = []
  for (const m of metrics) {
    if (m.name.startsWith(prefix)) {
      words.push({ word: m.name.replace(prefix, ''), value: m.value })
    }
  }
  words.sort((a, b) => b.value - a.value)
  return words
}
