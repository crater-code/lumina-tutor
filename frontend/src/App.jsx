import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [healthStatus, setHealthStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [messages, setMessages] = useState([])
  const [query, setQuery] = useState('')
  const [chatting, setChatting] = useState(false)

  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(data => {
        setHealthStatus(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to connect to backend:', err)
        setLoading(false)
      })
  }, [])

  const handleChat = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    const userMessage = { role: 'user', text: query }
    setMessages(prev => [...prev, userMessage])
    setQuery('')
    setChatting(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, language: 'en' })
      })
      const data = await res.json()
      
      const botMessage = { 
        role: 'bot', 
        text: data.response,
        isRefusal: data.is_refusal
      }
      setMessages(prev => [...prev, botMessage])
    } catch (err) {
      setMessages(prev => [...prev, { role: 'error', text: 'Chat failed: ' + err.message }])
    } finally {
      setChatting(false)
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Book-Bounded Tutoring Chatbot</h1>
        <p>Ask questions about the book</p>
        
        {loading ? (
          <p>Connecting...</p>
        ) : !healthStatus ? (
          <p className="error">✗ Unable to connect to backend</p>
        ) : (
          <div className="main-content">
            <div className="chat-section">
              <div className="messages">
                {messages.length === 0 && (
                  <div className="welcome-message">
                    <p>Welcome! Ask me anything about the book.</p>
                    <p className="hint">Try: "Who is the author?" or "What is this book about?"</p>
                  </div>
                )}
                {messages.map((msg, i) => (
                  <div key={i} className={`message ${msg.role}`}>
                    <strong>{msg.role === 'user' ? 'You' : msg.role === 'bot' ? 'Tutor' : 'System'}:</strong>
                    <p>{msg.text}</p>
                  </div>
                ))}
              </div>

              <form onSubmit={handleChat} className="chat-input">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask a question about the book..."
                  disabled={chatting}
                />
                <button type="submit" disabled={chatting || !query.trim()}>
                  {chatting ? 'Thinking...' : 'Send'}
                </button>
              </form>
            </div>
          </div>
        )}
      </header>
    </div>
  )
}

export default App
