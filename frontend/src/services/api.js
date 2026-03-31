const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function parseResponse(response) {
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`
    try {
      const body = await response.json()
      message = body.detail || message
    } catch {
      // Ignore JSON parsing failures for non-JSON error responses.
    }
    throw new Error(message)
  }

  return response.json()
}

export async function ingestText(text, sourceName = 'manual-input') {
  const response = await fetch(`${API_BASE_URL}/ingest/text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, source_name: sourceName }),
  })
  return parseResponse(response)
}

export async function ingestFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/ingest/file`, {
    method: 'POST',
    body: formData,
  })

  return parseResponse(response)
}

export async function sendChat(query, topK = 4) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k: topK }),
  })
  return parseResponse(response)
}
