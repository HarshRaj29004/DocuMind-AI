import { useState } from 'react'
import { ingestFile, ingestText } from '../services/api'

export function useIngestion() {
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)

  const ingestTextContent = async (text, sourceName) => {
    setLoading(true)
    setError(null)
    try {
      const result = await ingestText(text, sourceName)
      setStatus(result)
      return result
    } catch (err) {
      setError(err.message || 'Failed to ingest text')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const ingestFileContent = async (file) => {
    setLoading(true)
    setError(null)
    try {
      const result = await ingestFile(file)
      setStatus(result)
      return result
    } catch (err) {
      setError(err.message || 'Failed to ingest file')
      throw err
    } finally {
      setLoading(false)
    }
  }

  return {
    loading,
    status,
    error,
    ingestTextContent,
    ingestFileContent,
  }
}
