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
// Stats — basado en GET /api/v1/stats del contrato oficial
//
// El backend almacena métricas con la siguiente convención de nombres:
//   sources_count             → nº total de fuentes de información
//   news_count                → nº total de noticias procesadas
//   alerts_count              → nº total de alertas
//   rss_channels_count        → nº total de canales RSS
//   news_cat_<code>           → noticias de la categoría IPTC <code> (ej. news_cat_01000000)
//   timeline_<YYYY-MM-DD>     → noticias procesadas en esa fecha (ej. timeline_2026-04-01)
//   cloud_<code>_<palabra>    → frecuencia de <palabra> en categoría <code>
//
// Se usa el objeto Stats de id más alto (el más reciente).
// ---------------------------------------------------------------------------

// Cache de la llamada a /api/v1/stats para no repetirla dentro del mismo ciclo de render
let _statsPromise = null
let _statsCacheTs = 0
const CACHE_TTL_MS = 30_000 // 30 s

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
      _statsPromise = null // permitir reintento en error
      throw err
    })
  return _statsPromise
}

// Devuelve el objeto Stats más reciente (el de id más alto)
async function _latestStats() {
  const list = await _fetchStats()
  if (!list || list.length === 0) return []
  const latest = list.reduce((a, b) => (a.id > b.id ? a : b))
  return latest.metrics ?? []
}

// Convierte la lista de métricas en un Map { name -> value }
function _metricsMap(metrics) {
  const map = new Map()
  for (const m of metrics) map.set(m.name, m.value)
  return map
}

// ---------------------------------------------------------------------------
// API pública — misma firma que antes para no tocar las páginas
// ---------------------------------------------------------------------------

export async function getGlobalStats() {
  const metrics = await _latestStats()
  const map = _metricsMap(metrics)

  // Contadores globales
  const n_noticias = map.get('news_count') ?? 0
  const n_fuentes = map.get('sources_count') ?? 0
  const n_alertas = map.get('alerts_count') ?? 0
  const n_canales_rss = map.get('rss_channels_count') ?? 0

  // Noticias por categoría: buscar todas las métricas con prefijo "news_cat_"
  const noticias_por_categoria = []
  for (const [name, value] of map) {
    if (name.startsWith('news_cat_')) {
      const id = name.replace('news_cat_', '')
      noticias_por_categoria.push({ id, total: value })
    }
  }
  noticias_por_categoria.sort((a, b) => b.total - a.total)

  return { n_noticias, n_fuentes, n_alertas, n_canales_rss, noticias_por_categoria }
}

export async function getTimeline() {
  const metrics = await _latestStats()

  // Buscar métricas con prefijo "timeline_"
  const entries = []
  for (const m of metrics) {
    if (m.name.startsWith('timeline_')) {
      const fecha = m.name.replace('timeline_', '')
      entries.push({ fecha, total: m.value })
    }
  }

  // Ordenar cronológicamente
  entries.sort((a, b) => a.fecha.localeCompare(b.fecha))
  return entries
}

export async function getWordCloud(categoryCode) {
  const metrics = await _latestStats()
  const prefix = `cloud_${categoryCode}_`

  const words = []
  for (const m of metrics) {
    if (m.name.startsWith(prefix)) {
      const word = m.name.replace(prefix, '')
      words.push({ word, value: m.value })
    }
  }

  words.sort((a, b) => b.value - a.value)
  return words
}
