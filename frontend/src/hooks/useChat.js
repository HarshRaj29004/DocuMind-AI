import { useState } from 'react'
import { sendChat } from '../services/api'

const INITIAL_ASSISTANT_MESSAGE = {
  role: 'assistant',
  content: 'Upload documents or paste text, then ask a question to run retrieval.',
  sources: [],
}

function createSession(index) {
  return {
    id: `chat-${Date.now()}-${index}`,
    title: `Chat ${index}`,
    messages: [{ ...INITIAL_ASSISTANT_MESSAGE }],
  }
}

function getLatestSources(messages) {
  for (let i = messages.length - 1; i >= 0; i -= 1) {
    if (messages[i].role === 'assistant') {
      return messages[i].sources || []
    }
  }
  return []
}

export function useChat(onSourcesUpdate) {
  const [sessions, setSessions] = useState([createSession(1)])
  const [activeSessionId, setActiveSessionId] = useState(sessions[0].id)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const activeSession = sessions.find((session) => session.id === activeSessionId) || sessions[0]

  const createChatSession = () => {
    setError(null)
    const nextIndex = sessions.length + 1
    const nextSession = createSession(nextIndex)
    setSessions((prev) => [...prev, nextSession])
    setActiveSessionId(nextSession.id)
    if (onSourcesUpdate) {
      onSourcesUpdate([])
    }
  }

  const switchChatSession = (sessionId) => {
    setActiveSessionId(sessionId)
    setError(null)
    const nextSession = sessions.find((session) => session.id === sessionId)
    if (nextSession && onSourcesUpdate) {
      onSourcesUpdate(getLatestSources(nextSession.messages))
    }
  }

  const askQuestion = async (query) => {
    const userMessage = { role: 'user', content: query, sources: [] }
    setSessions((prev) =>
      prev.map((session) =>
        session.id === activeSessionId
          ? { ...session, messages: [...session.messages, userMessage] }
          : session
      )
    )
    setLoading(true)
    setError(null)

    try {
      const result = await sendChat(query)
      const assistantMessage = {
        role: 'assistant',
        content: result.answer,
        sources: result.citations || [],
      }
      setSessions((prev) =>
        prev.map((session) =>
          session.id === activeSessionId
            ? { ...session, messages: [...session.messages, assistantMessage] }
            : session
        )
      )
      if (onSourcesUpdate) {
        onSourcesUpdate(result.citations || [])
      }
      return result
    } catch (err) {
      setError(err.message || 'Failed to send message')
      throw err
    } finally {
      setLoading(false)
    }
  }

  return {
    sessions,
    activeSessionId,
    activeSession,
    messages: activeSession ? activeSession.messages : [],
    loading,
    error,
    askQuestion,
    createChatSession,
    switchChatSession,
  }
}
