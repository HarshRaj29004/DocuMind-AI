import { useState } from 'react'

function FileUpload({ onIngestFile, onIngestText, loading }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [textInput, setTextInput] = useState('')
  const [sourceName, setSourceName] = useState('manual-input')

  const handleFileSubmit = async (event) => {
    event.preventDefault()
    if (!selectedFile) {
      return
    }
    await onIngestFile(selectedFile)
    setSelectedFile(null)
    event.target.reset()
  }

  const handleTextSubmit = async (event) => {
    event.preventDefault()
    if (!textInput.trim()) {
      return
    }
    await onIngestText(textInput, sourceName)
    setTextInput('')
  }

  return (
    <section className="panel">
      <h2>Ingestion</h2>

      <form className="stack" onSubmit={handleFileSubmit}>
        <label htmlFor="file-input">Upload text file</label>
        <input
          id="file-input"
          type="file"
          accept=".txt,.md,.csv,.json"
          onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !selectedFile}>
          {loading ? 'Uploading...' : 'Ingest File'}
        </button>
      </form>

      <form className="stack" onSubmit={handleTextSubmit}>
        <label htmlFor="source-name">Source name</label>
        <input
          id="source-name"
          value={sourceName}
          onChange={(event) => setSourceName(event.target.value)}
          disabled={loading}
        />
        <label htmlFor="text-input">Or paste text</label>
        <textarea
          id="text-input"
          value={textInput}
          onChange={(event) => setTextInput(event.target.value)}
          rows={8}
          placeholder="Paste article, docs, notes..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !textInput.trim()}>
          {loading ? 'Indexing...' : 'Ingest Text'}
        </button>
      </form>
    </section>
  )
}

export default FileUpload
