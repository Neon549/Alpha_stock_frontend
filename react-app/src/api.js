const BASE = '/api/v1'

function headers() {
  return { 'Content-Type': 'application/json' }
}

function withToken(body) {
  const token = sessionStorage.getItem('token')
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

async function uploadDocument(file, sessionId) {
  const form = new FormData()
  form.append('file', file)
  form.append('session_id', sessionId)
  const r = await fetch(BASE + '/upload/document', { method: 'POST', body: form })
  const text = await r.text()
  let d = {}
  try { d = JSON.parse(text) } catch { d = { detail: text || `请求失败 (${r.status})` } }
  if (!r.ok) throw new Error(d.detail || `上传失败 (${r.status})`)
  return d
}

export const api = {
  login: (username, password) => post('/auth/login', { username, password }),
  register: (username, password, email) => post('/auth/register', { username, password, email: email || '' }),
  verify: (token) => post('/auth/verify', { token }),
  googleToken: (email, name, google_id) => post('/auth/google/token', { email, name, google_id }),
  forgotPassword: (email) => post('/auth/forgot-password', { email }),
  resetPassword: (token, new_password) => post('/auth/reset-password', { token, new_password }),

  chat: (message, model, session_id) => post('/chat', withToken({ message, model, session_id })),
  analyze: (stock_code, model, session_id) => post('/analyze', withToken({ stock_code, model, session_id })),
  uploadDocument,
  cleanupDocumentSession: (sessionId) => del(`/upload/session/${encodeURIComponent(sessionId)}`),
  cleanupDocument: (sessionId, documentId) => del(`/upload/session/${encodeURIComponent(sessionId)}/document/${encodeURIComponent(documentId)}`),

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
