import { useState } from 'react'
import AuthPanel from './components/AuthPanel'
import Chat from './components/Chat'
import FileUpload from './components/FileUpload'
import SourceCitations from './components/SourceCitations'
import { useAuth } from './hooks/useAuth'
import { useChat } from './hooks/useChat'
import { useIngestion } from './hooks/useIngestion'
import './App.css'

function App() {
  const [citations, setCitations] = useState([])
  const auth = useAuth()
  const ingestion = useIngestion()
  const chat = useChat(setCitations)

  const handleAsk = async (query) => {
    await chat.askQuestion(query)
  }

  const error = auth.error || ingestion.error || chat.error

  if (!auth.user) {
    return (
      <main className="app-shell">
        <header className="topbar">
          <h1>DocuMind-AI</h1>
          <p>Sign in to keep each user's document index isolated.</p>
        </header>

        <AuthPanel
          onLogin={auth.login}
          onRegister={auth.register}
          loading={auth.loading}
          error={auth.error}
        />
      </main>
    )
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <h1>DocuMind-AI</h1>
        <p>Ingest docs, retrieve context, and chat with grounded citations.</p>
        <div className="user-row">
          <span>Signed in as {auth.user.name || auth.user.email}</span>
          <button className="secondary" onClick={auth.logout}>Logout</button>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      {ingestion.status && (
        <div className="status-banner">
          {ingestion.status.message} Added: {ingestion.status.chunks_added} | Total:{' '}
          {ingestion.status.total_chunks}
        </div>
      )}

      <section className="grid-layout">
        <FileUpload
          onIngestFile={ingestion.ingestFileContent}
          onIngestText={ingestion.ingestTextContent}
          loading={ingestion.loading}
        />

        <Chat
          messages={chat.messages}
          loading={chat.loading}
          onAsk={handleAsk}
          sessions={chat.sessions}
          activeSessionId={chat.activeSessionId}
          onSwitchSession={chat.switchChatSession}
          onCreateSession={chat.createChatSession}
        />

        <SourceCitations citations={citations} />
      </section>
    </main>
  )
}

export default App
