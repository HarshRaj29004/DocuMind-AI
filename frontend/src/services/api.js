const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const TOKEN_KEY = 'rag_access_token'
const USER_KEY = 'rag_user'

function getAuthHeaders() {
  const token = localStorage.getItem(TOKEN_KEY)
  if (!token) {
    return {}
  }
  return { Authorization: `Bearer ${token}` }
}

function persistSession(accessToken, user) {
  localStorage.setItem(TOKEN_KEY, accessToken)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function getStoredUser() {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) {
    return null
  }

  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

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
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify({ text, source_name: sourceName }),
  })
  return parseResponse(response)
}

export async function ingestFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/ingest/file`, {
    method: 'POST',
    headers: { ...getAuthHeaders() },
    body: formData,
  })

  return parseResponse(response)
}

export async function sendChat(query, topK = 4) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify({ query, top_k: topK }),
  })
  return parseResponse(response)
}

export async function listChatWindows() {
  const response = await fetch(`${API_BASE_URL}/chat-windows`, {
    headers: { ...getAuthHeaders() },
  })
  return parseResponse(response)
}

export async function createChatWindow(title) {
  const response = await fetch(`${API_BASE_URL}/chat-windows`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify({ title }),
  })
  return parseResponse(response)
}

export async function deleteChatWindow(windowId) {
  const response = await fetch(`${API_BASE_URL}/chat-windows/${windowId}`, {
    method: 'DELETE',
    headers: { ...getAuthHeaders() },
  })
  return parseResponse(response)
}

export async function registerUser(name, email, password) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password }),
  })

  const result = await parseResponse(response)
  persistSession(result.access_token, result.user)
  return result
}

export async function loginUser(email, password) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })

  const result = await parseResponse(response)
  persistSession(result.access_token, result.user)
  return result
}

export async function getMe() {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: { ...getAuthHeaders() },
  })
  return parseResponse(response)
}
