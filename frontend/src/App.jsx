import { useState } from 'react'
import Chat from './components/Chat'
import FileUpload from './components/FileUpload'
import SourceCitations from './components/SourceCitations'
import { useChat } from './hooks/useChat'
import { useIngestion } from './hooks/useIngestion'
import './App.css'

function App() {
  const [citations, setCitations] = useState([])
  const ingestion = useIngestion()
  const chat = useChat(setCitations)

  const handleAsk = async (query) => {
    await chat.askQuestion(query)
  }

  const error = ingestion.error || chat.error

  return (
    <main className="app-shell">
      <header className="topbar">
        <h1>NotebookLM Clone - Local RAG</h1>
        <p>Ingest docs, retrieve context, and chat with grounded citations.</p>
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
        />

        <SourceCitations citations={citations} />
      </section>
    </main>
  )
}

export default App
