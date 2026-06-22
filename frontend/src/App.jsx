import { useState, useRef, useEffect, useCallback } from 'react'
import './index.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const QUICK_QUESTIONS = [
  '📍 Onde fica o MCJB?',
  '⏰ Qual o horário de atendimento?',
  '💳 Como me associar?',
  '💻 O que é o Ecowork?',
  '📞 Quais são os contatos?',
  '💰 Qual a chave PIX?',
]

function TypingIndicator() {
  return (
    <div className="message-row">
      <div className="avatar bot">🌿</div>
      <div className="bubble bot typing-indicator">
        <span className="typing-dot" />
        <span className="typing-dot" />
        <span className="typing-dot" />
      </div>
    </div>
  )
}

function MessageBubble({ msg }) {
  return (
    <div className={`message-row ${msg.role}`}>
      <div className={`avatar ${msg.role}`}>
        {msg.role === 'bot' ? '🌿' : '👤'}
      </div>
      <div className={`bubble ${msg.role}`}>
        {msg.content}
      </div>
    </div>
  )
}

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = useCallback(async (text) => {
    const trimmed = text.trim()
    if (!trimmed || loading) return

    setError(null)
    const userMsg = { role: 'user', content: trimmed }
    const history = [...messages, userMsg]
    setMessages(history)
    setInput('')
    setLoading(true)

    // reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: history.map(m => ({
            role: m.role === 'bot' ? 'assistant' : 'user',
            content: m.content,
          })),
        }),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || `Erro ${res.status}`)
      }

      const data = await res.json()
      setMessages(prev => [...prev, { role: 'bot', content: data.reply }])
    } catch (err) {
      setError(`Não foi possível conectar ao servidor. (${err.message})`)
      // remove user message on error
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setLoading(false)
    }
  }, [messages, loading])

  const handleSubmit = (e) => {
    e.preventDefault()
    sendMessage(input)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  const handleTextareaChange = (e) => {
    setInput(e.target.value)
    // auto-grow
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 150) + 'px'
  }

  const isEmpty = messages.length === 0

  return (
    <div className="app-layout">
      {/* ── Header ── */}
      <header className="header">
        <div className="header-logo" aria-hidden="true">🌿</div>
        <div className="header-info">
          <h1 className="header-title">Assistente MCJB</h1>
          <p className="header-subtitle">Movimento Comunitário do Jardim Botânico</p>
        </div>
        <div className="status-dot" title="Online">Online</div>
      </header>

      {/* ── Messages ── */}
      <main className="messages-container" id="messages-container" role="log" aria-live="polite">
        {isEmpty ? (
          <div className="welcome-wrapper">
            <div className="welcome-icon" aria-hidden="true">🌱</div>
            <h2 className="welcome-title">Olá! Como posso ajudar?</h2>
            <p className="welcome-subtitle">
              Sou a assistente virtual do MCJB. Estou aqui para responder suas dúvidas
              sobre o Movimento Comunitário do Jardim Botânico.
            </p>
            <div className="quick-questions" role="group" aria-label="Perguntas rápidas">
              {QUICK_QUESTIONS.map((q) => (
                <button
                  key={q}
                  className="quick-btn"
                  onClick={() => sendMessage(q.replace(/^.{2}/, '').trim())}
                  disabled={loading}
                  aria-label={`Perguntar: ${q}`}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, i) => (
              <MessageBubble key={i} msg={msg} />
            ))}
            {loading && <TypingIndicator />}
          </>
        )}
        <div ref={bottomRef} aria-hidden="true" />
      </main>

      {/* ── Error Banner ── */}
      {error && <div className="error-banner" role="alert">⚠️ {error}</div>}

      {/* ── Input Area ── */}
      <footer className="input-area">
        <form className="input-form" onSubmit={handleSubmit} noValidate>
          <div className="input-wrapper">
            <textarea
              ref={textareaRef}
              id="chat-input"
              className="input-field"
              value={input}
              onChange={handleTextareaChange}
              onKeyDown={handleKeyDown}
              placeholder="Digite sua mensagem... (Enter para enviar)"
              rows={1}
              disabled={loading}
              aria-label="Campo de mensagem"
              autoComplete="off"
            />
          </div>
          <button
            type="submit"
            id="send-button"
            className="send-btn"
            disabled={!input.trim() || loading}
            aria-label="Enviar mensagem"
            title="Enviar (Enter)"
          >
            {loading ? '⏳' : '➤'}
          </button>
        </form>
        <p className="input-footer">
          Assistente de IA · Informações baseadas na base de conhecimentos do MCJB
        </p>
      </footer>
    </div>
  )
}
