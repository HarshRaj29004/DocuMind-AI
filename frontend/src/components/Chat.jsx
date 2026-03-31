import { useState } from 'react'

function Chat({ messages, loading, onAsk }) {
  const [query, setQuery] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!query.trim()) {
      return
    }
    const current = query
    setQuery('')
    await onAsk(current)
  }

  return (
    <section className="panel">
      <h2>Chat</h2>
      <div className="chat-window">
        {messages.map((message, index) => (
          <article
            key={`${message.role}-${index}`}
            className={`bubble bubble-${message.role}`}
          >
            <p>{message.content}</p>
          </article>
        ))}
      </div>

      <form className="chat-input" onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Ask a grounded question..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !query.trim()}>
          {loading ? 'Thinking...' : 'Send'}
        </button>
      </form>
    </section>
  )
}

export default Chat
