import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth, useModal } from '../store'
import { api } from '../api'
import { MODELS } from '../constants'

function SidebarUserPanel() {
  const { username, logout } = useAuth()
  const { open } = useModal()
  const navigate = useNavigate()
  const [confirming, setConfirming] = useState(false)

  function handleLogout() {
    logout()
    navigate('/app')
  }

  function handleSwitchUser() {
    setConfirming(true)
  }

  function confirmSwitch() {
    setConfirming(false)
    logout()
    open('login')
  }

  return (
    <div className="sidebar-user-panel">
      <div className="sup-avatar">{(username || '?')[0].toUpperCase()}</div>
      <div className="sup-info">
        {confirming ? (
          <div style={{ fontSize: 12, color: 'var(--ink)' }}>
            <div style={{ marginBottom: 6, fontWeight: 600 }}>确认切换账户？</div>
            <div style={{ display: 'flex', gap: 6 }}>
              <button
                className="sup-btn"
                onClick={confirmSwitch}
                style={{ color: '#dc2626', fontWeight: 700 }}
              >确认</button>
              <button
                className="sup-btn"
                onClick={() => setConfirming(false)}
              >取消</button>
            </div>
          </div>
        ) : (
          <>
            <div className="sup-name">{username}</div>
            <div className="sup-actions">
              <button className="sup-btn" onClick={() => navigate('/')} title="返回主页">🏠</button>
              <button className="sup-btn" onClick={handleSwitchUser} title="切换用户">🔄</button>
              <button className="sup-btn sup-btn-logout" onClick={handleLogout} title="退出登录">退出</button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function renderMd(text) {
  if (!text || text === '[SKIPPED] 本次分析未启用此维度') {
    return <span style={{ color: 'var(--muted)', fontSize: 13 }}>本次未启用此维度分析</span>
  }
  return text.split('\n').map((line, i) => {
    if (line.startsWith('### ')) return <h4 key={i} style={{ margin: '12px 0 4px', fontSize: 14, fontWeight: 700, color: 'var(--ink)' }}>{line.slice(4)}</h4>
    if (line.startsWith('## ')) return <h3 key={i} style={{ margin: '14px 0 6px', fontSize: 15, fontWeight: 700, color: 'var(--ink)' }}>{line.slice(3)}</h3>
    if (line.startsWith('# ')) return <h2 key={i} style={{ margin: '16px 0 8px', fontSize: 16, fontWeight: 800, color: 'var(--ink)' }}>{line.slice(2)}</h2>
    if (line.trim() === '') return <br key={i} />
    const parts = line.split(/(\*\*[^*]+\*\*)/)
    return (
      <p key={i} style={{ margin: '3px 0', fontSize: 13.5, lineHeight: 1.75, color: 'var(--slate)' }}>
        {parts.map((part, j) =>
          part.startsWith('**') && part.endsWith('**')
            ? <strong key={j} style={{ color: 'var(--ink)', fontWeight: 600 }}>{part.slice(2, -2)}</strong>
            : part
        )}
      </p>
    )
  })
}

function AnalyzeCard({ data }) {
  const [tab, setTab] = useState('decision')

  const isObj = typeof data === 'object' && data !== null
  const sections = isObj ? {
    decision: data.decision || '',
    technical: data.technical_report || '',
    fundamental: data.fundamental_report || '',
    sentiment: data.sentiment_report || '',
    researcher: data.researcher_analysis || data.bull_argument || '',
  } : { decision: String(data) }

  const stockCode = isObj ? (data.stock_code || '') : ''
  const stockName = isObj ? (data.stock_name || '') : ''
  const decisionText = sections.decision
  const isBuy = decisionText.includes('买入')
  const isSell = decisionText.includes('卖出') || decisionText.includes('减仓')

  const tabs = [
    { key: 'decision', label: '📋 综合结论' },
    { key: 'technical', label: '📈 技术面' },
    { key: 'fundamental', label: '📊 基本面' },
    { key: 'sentiment', label: '📰 情绪面' },
    { key: 'researcher', label: '⚖️ 多空辩论' },
  ]

  return (
    <div className="analyze-card" style={{ width: '100%', maxWidth: '100%' }}>
      <div className="analyze-card-header">
        <div className="analyze-card-stock">📊 投研报告</div>
        {(stockName || stockCode) && (
          <div className="analyze-card-code">{stockName} {stockCode}</div>
        )}
        <span className={`analyze-decision-badge ${isBuy ? 'badge-buy' : isSell ? 'badge-sell' : 'badge-hold'}`} style={{ marginLeft: 'auto' }}>
          {isBuy ? '🔴 买入' : isSell ? '🟢 减仓' : '🟡 观望'}
        </span>
      </div>

      <div style={{ display: 'flex', gap: 4, padding: '8px 16px 0', flexWrap: 'wrap', borderBottom: '1px solid var(--border)' }}>
        {tabs.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            style={{
              padding: '5px 12px', fontSize: 12, fontWeight: 600, border: 'none', cursor: 'pointer',
              borderRadius: '6px 6px 0 0', marginBottom: -1,
              background: tab === t.key ? 'var(--bg)' : 'transparent',
              color: tab === t.key ? 'var(--purple)' : 'var(--muted)',
              borderBottom: tab === t.key ? '2px solid var(--purple)' : '2px solid transparent',
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div style={{ padding: '16px 20px', minHeight: 200, maxHeight: 480, overflowY: 'auto' }}>
        {renderMd(sections[tab])}
      </div>
    </div>
  )
}

function ChatBubble({ msg }) {
  if (msg.role === 'user') {
    return (
      <div className="chat-bubble-wrap user">
        <div className="chat-bubble user">
          {msg.attachments?.length > 0 && (
            <div className="bubble-attachments">
              {msg.attachments.map((f, i) => (
                <div key={i} className="bubble-attach-chip">📎 {f}</div>
              ))}
            </div>
          )}
          {msg.content}
        </div>
      </div>
    )
  }
  if (msg.type === 'analyze') {
    return (
      <div className="chat-bubble-wrap assistant">
        <AnalyzeCard data={msg.content} />
      </div>
    )
  }
  return (
    <div className="chat-bubble-wrap assistant">
      <div className={`chat-bubble assistant${msg.thinking ? ' thinking' : ''}`}>
        {typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)}
      </div>
    </div>
  )
}

function AuthGate() {
  const openModal = useModal(s => s.open)
  return (
    <div className="auth-gate">
      <p style={{ fontSize: 18, fontWeight: 700, color: 'var(--ink)' }}>请先登录后使用 Alpha AI</p>
      <p>投研对话、历史记录保存等功能需要登录账号</p>
      <button className="btn-start" style={{ marginTop: 8 }} onClick={() => openModal('login')}>立即登录</button>
    </div>
  )
}

let convIdCounter = Date.now()

export default function Chat() {
  const { token, username } = useAuth()
  const [conversations, setConversations] = useState([])
  const [currentConvId, setCurrentConvId] = useState(null)
  const [messages, setMessages] = useState([])
  const [mode, setMode] = useState('chat')
  const [input, setInput] = useState('')
  const [stockCode, setStockCode] = useState('')
  const [stockName, setStockName] = useState('')
  const [model, setModel] = useState(MODELS[1].value)
  const [loading, setLoading] = useState(false)
  const [attachments, setAttachments] = useState([])
  const messagesEndRef = useRef()
  const inputRef = useRef()
  const fileInputRef = useRef()

  useEffect(() => {
    if (token && username) {
      api.getConversations(username)
        .then(data => setConversations(Array.isArray(data) ? data : []))
        .catch(() => {})
    }
  }, [token, username])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  function newConversation() {
    setCurrentConvId(null)
    setMessages([])
    setInput('')
    setStockCode('')
    setAttachments([])
  }

  function loadConversation(conv) {
    setCurrentConvId(conv.id || conv.conv_id)
    setMessages(conv.messages || [])
  }

  async function deleteConversation(e, conv) {
    e.stopPropagation()
    const id = conv.id || conv.conv_id
    try {
      await api.deleteConversation(id)
      setConversations(prev => prev.filter(c => (c.id || c.conv_id) !== id))
      if (currentConvId === id) newConversation()
    } catch (err) {
      alert(err.message)
    }
  }

  async function saveConversation(msgs) {
    if (!username || msgs.length < 2) return
    const title = msgs.find(m => m.role === 'user')?.content?.slice(0, 30) || '新对话'
    try {
      const saved = await api.saveConversation({ username, title, messages: msgs, conv_id: currentConvId || undefined })
      const id = saved?.conv_id || saved?.id || currentConvId || `local-${++convIdCounter}`
      setCurrentConvId(id)
      setConversations(prev => {
        const exists = prev.find(c => (c.id || c.conv_id) === id)
        if (exists) return prev.map(c => (c.id || c.conv_id) === id ? { ...c, messages: msgs, title } : c)
        return [{ id, conv_id: id, title, messages: msgs }, ...prev]
      })
    } catch { /* save failed silently */ }
  }

  function handleFileChange(e) {
    const files = Array.from(e.target.files)
    setAttachments(prev => [...prev, ...files.map(f => f.name)])
    e.target.value = ''
  }

  function removeAttachment(i) {
    setAttachments(prev => prev.filter((_, j) => j !== i))
  }

  async function send() {
    if (loading) return
    const content = mode === 'chat' ? input.trim() : stockCode.trim()
    if (!content) return

    const userMsg = {
      role: 'user',
      content: mode === 'chat' ? content : `📊 分析股票: ${content}${stockName ? ` (${stockName})` : ''}`,
      type: mode,
      attachments: attachments.length > 0 ? [...attachments] : undefined,
    }
    const newMsgs = [...messages, userMsg]
    setMessages(newMsgs)
    setInput('')
    setAttachments([])
    setLoading(true)

    try {
      let assistantMsg
      if (mode === 'chat') {
        const d = await api.chat(content, model)
        // intent=2 时后端返回完整分析对象，按投研报告渲染
        if (d.intent === 2 && d.decision !== undefined) {
          assistantMsg = { role: 'assistant', content: d, type: 'analyze' }
        } else {
          const reply = d.content || d.reply || d.response || (typeof d === 'string' ? d : JSON.stringify(d))
          assistantMsg = { role: 'assistant', content: reply, type: 'chat' }
        }
      } else {
        const d = await api.analyze(content, model)
        // analyze 接口直接返回结构化对象
        assistantMsg = { role: 'assistant', content: d, type: 'analyze' }
      }
      const finalMsgs = [...newMsgs, assistantMsg]
      setMessages(finalMsgs)
      saveConversation(finalMsgs)
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: `错误：${err.message}`, type: 'chat' }])
    } finally {
      setLoading(false)
    }
  }

  function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  if (!token) return (
    <div className="func-page">
      <AuthGate />
    </div>
  )

  return (
    <div className="chat-layout">
      {/* Sidebar */}
      <div className="chat-sidebar">
        <div className="sidebar-header">
          <span className="sidebar-title">对话历史</span>
          <button className="btn-new-conv" onClick={newConversation}>+ 新对话</button>
        </div>
        <div className="conv-list">
          {conversations.length === 0 ? (
            <div style={{ padding: '20px 12px', fontSize: 13, color: 'var(--muted)' }}>暂无历史对话</div>
          ) : conversations.map(conv => {
            const id = conv.id || conv.conv_id
            return (
              <div
                key={id}
                className={`conv-item${currentConvId === id ? ' active' : ''}`}
                onClick={() => loadConversation(conv)}
              >
                <span className="conv-title">{conv.title || '未命名对话'}</span>
                <button className="btn-del-conv" onClick={e => deleteConversation(e, conv)}>✕</button>
              </div>
            )
          })}
        </div>
        <SidebarUserPanel />
      </div>

      {/* Main */}
      <div className="chat-main">
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div style={{ margin: 'auto', textAlign: 'center', color: 'var(--muted)', padding: '60px 20px' }}>
              <div style={{ fontSize: 48, marginBottom: 16 }}>🤖</div>
              <p style={{ fontSize: 16, fontWeight: 700, color: 'var(--ink)', marginBottom: 8 }}>Alpha AI 投研助手</p>
              <p style={{ fontSize: 14, lineHeight: 1.7 }}>
                普通对话模式：直接输入问题<br />
                投研分析模式：输入股票代码，AI 多视角深度分析
              </p>
            </div>
          ) : (
            messages.map((msg, i) => <ChatBubble key={i} msg={msg} />)
          )}
          {loading && (
            <div className="chat-bubble-wrap assistant">
              <div className="chat-bubble assistant thinking">
                <span className="inline-spinner" />
                AI 思考中…
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="chat-input-area">
          {/* Mode tabs */}
          <div className="chat-mode-tabs">
            <button className={`chat-mode-tab${mode === 'chat' ? ' active' : ''}`} onClick={() => setMode('chat')}>
              💬 普通对话
            </button>
            <button className={`chat-mode-tab${mode === 'analyze' ? ' active' : ''}`} onClick={() => setMode('analyze')}>
              📊 投研分析
            </button>
          </div>

          {/* Card input */}
          <div className="chat-input-card">
            {mode === 'chat' ? (
              <textarea
                ref={inputRef}
                className="chat-card-textarea"
                placeholder="输入问题，Shift+Enter 换行，Enter 发送…"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={onKeyDown}
                rows={2}
              />
            ) : (
              <div className="analyze-input-row">
                <input
                  className="chat-card-input"
                  placeholder="股票代码（如 600150）"
                  value={stockCode}
                  onChange={e => setStockCode(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && send()}
                />
                <input
                  className="chat-card-input"
                  placeholder="股票名称（可选，如 中国船舶）"
                  value={stockName}
                  onChange={e => setStockName(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && send()}
                  style={{ flex: 1.5 }}
                />
              </div>
            )}

            {attachments.length > 0 && (
              <div className="attachment-previews">
                {attachments.map((name, i) => (
                  <div key={i} className="attachment-chip">
                    <span>📎 {name}</span>
                    <button onClick={() => removeAttachment(i)}>✕</button>
                  </div>
                ))}
              </div>
            )}

            <div className="chat-toolbar">
              <div className="toolbar-left">
                <input
                  type="file"
                  ref={fileInputRef}
                  style={{ display: 'none' }}
                  onChange={handleFileChange}
                  multiple
                  accept="image/*,.pdf,.txt,.csv,.xlsx"
                />
                <button
                  className="toolbar-icon-btn"
                  onClick={() => fileInputRef.current?.click()}
                  title="添加附件"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                    <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                </button>
              </div>

              <div className="toolbar-right">
                <select
                  className="toolbar-model-select"
                  value={model}
                  onChange={e => setModel(e.target.value)}
                >
                  {MODELS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
                </select>

                <span className="toolbar-hint">
                  {mode === 'analyze' ? '约需 30-60s' : '直接对话 AI 助手'}
                </span>

                <button className="toolbar-icon-btn" title="语音输入（即将开放）">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                    <rect x="9" y="2" width="6" height="11" rx="3" />
                    <path d="M5 10a7 7 0 0014 0" />
                    <line x1="12" y1="19" x2="12" y2="22" />
                    <line x1="9" y1="22" x2="15" y2="22" />
                  </svg>
                </button>

                <button className="toolbar-icon-btn" title="音频模式（即将开放）">
                  <svg width="16" height="12" viewBox="0 0 24 16" fill="currentColor">
                    <rect x="0" y="5" width="3" height="6" rx="1.5" />
                    <rect x="5" y="2" width="3" height="12" rx="1.5" />
                    <rect x="10" y="0" width="3" height="16" rx="1.5" />
                    <rect x="15" y="3" width="3" height="10" rx="1.5" />
                    <rect x="20" y="6" width="3" height="4" rx="1.5" />
                  </svg>
                </button>

                <button className="btn-send-arrow" onClick={send} disabled={loading}>
                  {loading ? (
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="spin-icon">
                      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" strokeLinecap="round"/>
                    </svg>
                  ) : (
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
