const BASE = '/api/v1'

function headers() {
  return { 'Content-Type': 'application/json' }
}

function withToken(body) {
  const token = localStorage.getItem('token')
  return token ? { ...body, token } : body
}

async function post(path, body) {
  const r = await fetch(BASE + path, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify(body),
  })
  const text = await r.text()
  let d = {}
  try { d = JSON.parse(text) } catch { d = { detail: text || `请求失败 (${r.status})` } }
  if (!r.ok) throw new Error(d.detail || `请求失败 (${r.status})`)
  return d
}

async function get(path) {
  const r = await fetch(BASE + path)
  const text = await r.text()
  let d = {}
  try { d = JSON.parse(text) } catch { d = { detail: text || `请求失败 (${r.status})` } }
  if (!r.ok) throw new Error(d.detail || `请求失败 (${r.status})`)
  return d
}

async function del(path) {
  const r = await fetch(BASE + path, { method: 'DELETE', headers: headers() })
  if (!r.ok) {
    const d = await r.json().catch(() => ({}))
    throw new Error(d.detail || `请求失败 (${r.status})`)
  }
  return true
}

export const api = {
  login: (username, password) => post('/auth/login', { username, password }),
  register: (username, password) => post('/auth/register', { username, password }),
  verify: (token) => post('/auth/verify', { token }),
  googleToken: (email, name, google_id) => post('/auth/google/token', { email, name, google_id }),

  chat: (message, model) => post('/chat', withToken({ message, model })),
  analyze: (stock_code, model) => post('/analyze', withToken({ stock_code, model })),

  backtest: (params) => post('/backtest', withToken(params)),
  getStrategies: () => get('/backtest/strategies'),
  getSectors: () => get('/backtest/sectors'),
  filterSector: (params) => post('/backtest/filter', withToken(params)),

  scanToday: (params) => post('/scan/today', withToken(params)),

  alphaSingle: (stock_code, stock_name) =>
    post('/alpha/single', withToken({ stock_code, stock_name })),

  getConversations: (username) => get(`/conversations/${username}`),
  saveConversation: (data) => post('/conversations/save', withToken(data)),
  deleteConversation: (conv_id) => del(`/conversations/${conv_id}`),
}
