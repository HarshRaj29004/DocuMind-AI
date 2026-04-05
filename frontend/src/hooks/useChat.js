import { useEffect, useState } from 'react'
import {
  createChatWindow,
  deleteChatWindow,
  listChatWindows,
  sendChat,
} from '../services/api'

const INITIAL_ASSISTANT_MESSAGE = {
  role: 'assistant',
  content: 'Upload documents or paste text, then ask a question to run retrieval.',
  sources: [],
}

function createSession(index) {
  return {
    id: index,
    title: `Chat ${index}`,
    messages: [{ ...INITIAL_ASSISTANT_MESSAGE }],
  }
}

function mapWindowToSession(window, fallbackIndex) {
  return {
    id: Number(window.id),
    title: window.title || `Chat ${fallbackIndex}`,
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

export function useChat(onSourcesUpdate, isEnabled = true) {
  const [sessions, setSessions] = useState([createSession(1)])
  const [activeSessionId, setActiveSessionId] = useState(sessions[0].id)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!isEnabled) {
      return
    }

    const initializeChatWindows = async () => {
      try {
        const payload = await listChatWindows()
        let nextSessions = (payload.chat_windows || []).map((window, index) =>
          mapWindowToSession(window, index + 1)
        )

        if (!nextSessions.length) {
          const created = await createChatWindow('Chat 1')
          nextSessions = [mapWindowToSession(created, 1)]
        }

        setSessions(nextSessions)
        setActiveSessionId(nextSessions[0].id)
        if (onSourcesUpdate) {
          onSourcesUpdate([])
        }
      } catch (err) {
        setError(err.message || 'Failed to load chat windows')
      }
    }

    initializeChatWindows()
  }, [isEnabled, onSourcesUpdate])

  const activeSession = sessions.find((session) => session.id === activeSessionId) || sessions[0]

  const createChatSession = async () => {
    setError(null)
    try {
      const nextIndex = sessions.length + 1
      const created = await createChatWindow(`Chat ${nextIndex}`)
      const nextSession = mapWindowToSession(created, nextIndex)
      setSessions((prev) => [...prev, nextSession])
      setActiveSessionId(nextSession.id)
      if (onSourcesUpdate) {
        onSourcesUpdate([])
      }
    } catch (err) {
      setError(err.message || 'Failed to create chat window')
      throw err
    }
  }

  const switchChatSession = (sessionId) => {
    const normalizedId = Number(sessionId)
    setActiveSessionId(normalizedId)
    setError(null)
    const nextSession = sessions.find((session) => session.id === normalizedId)
    if (nextSession && onSourcesUpdate) {
      onSourcesUpdate(getLatestSources(nextSession.messages))
    }
  }

  const deleteChatSession = async (sessionId) => {
    setError(null)
    if (sessions.length <= 1) {
      return
    }

    try {
      await deleteChatWindow(sessionId)
      setSessions((prev) => {
        const removedIndex = prev.findIndex((session) => session.id === sessionId)
        if (removedIndex === -1) {
          return prev
        }

        const nextSessions = prev.filter((session) => session.id !== sessionId)
        if (activeSessionId === sessionId) {
          const fallback = nextSessions[Math.max(0, removedIndex - 1)] || nextSessions[0]
          setActiveSessionId(fallback.id)
          if (onSourcesUpdate) {
            onSourcesUpdate(getLatestSources(fallback.messages))
          }
        }
        return nextSessions
      })
    } catch (err) {
      setError(err.message || 'Failed to delete chat window')
      throw err
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
    deleteChatSession,
  }
}
