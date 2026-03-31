import { useState } from 'react'
import { sendChat } from '../services/api'

export function useChat(onSourcesUpdate) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Upload documents or paste text, then ask a question to run retrieval.',
      sources: [],
    },
  ])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const askQuestion = async (query) => {
    const userMessage = { role: 'user', content: query, sources: [] }
    setMessages((prev) => [...prev, userMessage])
    setLoading(true)
    setError(null)

    try {
      const result = await sendChat(query)
      const assistantMessage = {
        role: 'assistant',
        content: result.answer,
        sources: result.citations || [],
      }
      setMessages((prev) => [...prev, assistantMessage])
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
    messages,
    loading,
    error,
    askQuestion,
  }
}
